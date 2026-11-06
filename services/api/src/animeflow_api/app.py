"""Local-first API. The bearer token must be supplied by the launcher or developer."""

import asyncio
import hashlib
import hmac
import json
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from animeflow_blender import RenderError
from animeflow_blender.runner import (
    EXTENSION_KEY,
    blender_executable,
    validate_render_request,
    validate_scene,
)
from animeflow_catalog import load_catalog
from animeflow_contracts.validation import schema_issues
from animeflow_orchestrator.storage import Conflict, NotFound, Storage
from animeflow_orchestrator.worker import Worker
from animeflow_project.editorial import StoryEditError, editorial_report, plan_story_edit
from animeflow_project.summary import summarize_project
from animeflow_project.validation import validate_project
from fastapi import (
    Depends,
    FastAPI,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field


class CreateProject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project: dict[str, Any]


class UpdateProject(CreateProject):
    expected_revision: int = Field(ge=1)


class CreateJob(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal["project.validate", "render.shot.blender"]
    expected_revision: int = Field(ge=1)
    shot_id: UUID | None = None
    frame_start: int = Field(default=0, ge=0)
    frame_end_exclusive: int | None = Field(default=None, ge=1)


def create_app(
    data_dir: str | Path | None = None,
    api_token: str | None = None,
    start_worker: bool = True,
) -> FastAPI:
    token = api_token or os.environ.get("ANIMEFLOW_API_TOKEN", "")
    if len(token) < 32 or not token.isascii():
        raise RuntimeError("Set ANIMEFLOW_API_TOKEN to an ASCII secret of at least 32 characters.")
    directory = Path(data_dir or os.environ.get("ANIMEFLOW_DATA_DIR", ".animeflow-data"))
    storage = Storage(directory)
    worker = Worker(storage)
    max_upload_bytes = int(os.environ.get("ANIMEFLOW_MAX_UPLOAD_BYTES", str(100 * 1024 * 1024)))
    if max_upload_bytes <= 0:
        raise RuntimeError("ANIMEFLOW_MAX_UPLOAD_BYTES must be positive.")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if start_worker:
            worker.start()
        try:
            yield
        finally:
            if start_worker:
                worker.stop()

    app = FastAPI(title="AnimeFlow Local API", version="0.1.0", lifespan=lifespan)
    app.state.storage = storage
    app.state.worker = worker

    origins = os.environ.get(
        "ANIMEFLOW_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Last-Event-ID"],
    )

    def require_auth(authorization: str | None = Header(default=None)) -> None:
        expected = f"Bearer {token}"
        if (
            authorization is None
            or not authorization.isascii()
            or not hmac.compare_digest(authorization, expected)
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    @app.exception_handler(NotFound)
    async def not_found_handler(request: Request, exc: NotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404, content={"detail": {"code": "not_found", "message": str(exc)}}
        )

    @app.exception_handler(Conflict)
    async def conflict_handler(request: Request, exc: Conflict) -> JSONResponse:
        return JSONResponse(
            status_code=409, content={"detail": {"code": "conflict", "message": str(exc)}}
        )

    @app.exception_handler(StoryEditError)
    async def story_edit_error_handler(request: Request, exc: StoryEditError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": {"code": "invalid_story_edit", "issues": exc.issues}},
        )

    def assert_valid(project: dict[str, Any]) -> None:
        try:
            json.dumps(project, allow_nan=False)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=422,
                detail={"code": "invalid_json", "message": "Project must be valid JSON."},
            ) from None
        issues = validate_project(project)
        if issues:
            raise HTTPException(
                status_code=422, detail={"code": "invalid_project", "issues": issues}
            )

    def project_root(project_id: str) -> Path:
        projects_root = (storage.directory / "projects").resolve()
        root = (projects_root / project_id).resolve()
        if not projects_root.is_relative_to(storage.directory) or not root.is_relative_to(
            projects_root
        ):
            raise Conflict("Project storage must remain inside the data directory.")
        return root

    @app.get("/api/v1/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "project_schema_version": "1.0.0"}

    @app.get("/api/v1/adapters/blender", dependencies=[Depends(require_auth)], tags=["adapters"])
    def blender_health() -> dict[str, Any]:
        return {
            "id": "animeflow.blender.primitives",
            "status": "binary_detected" if blender_executable() else "missing_binary",
            "probe": "executable_path_only",
            "scene_extension": "animeflow.blender.scene.v1",
            "capabilities": ["render.frames", "physics.rigid_body"],
        }

    @app.get("/api/v1/catalog/repos", dependencies=[Depends(require_auth)], tags=["catalog"])
    def catalog() -> dict[str, Any]:
        return load_catalog()

    @app.get("/api/v1/projects", dependencies=[Depends(require_auth)], tags=["projects"])
    def list_projects() -> dict[str, Any]:
        return {"projects": storage.list_projects()}

    @app.post(
        "/api/v1/projects", dependencies=[Depends(require_auth)], status_code=201, tags=["projects"]
    )
    def create_project(body: CreateProject) -> dict[str, Any]:
        assert_valid(body.project)
        return storage.create_project(body.project)

    @app.get(
        "/api/v1/projects/{project_id}", dependencies=[Depends(require_auth)], tags=["projects"]
    )
    def get_project(project_id: UUID) -> dict[str, Any]:
        return storage.get_project(str(project_id))

    @app.put(
        "/api/v1/projects/{project_id}", dependencies=[Depends(require_auth)], tags=["projects"]
    )
    def update_project(project_id: UUID, body: UpdateProject) -> dict[str, Any]:
        assert_valid(body.project)
        if body.project["project_id"] != str(project_id):
            raise HTTPException(status_code=422, detail={"code": "project_id_mismatch"})
        return storage.update_project(str(project_id), body.expected_revision, body.project)

    @app.get(
        "/api/v1/projects/{project_id}/editorial",
        dependencies=[Depends(require_auth)],
        tags=["editorial"],
    )
    def get_editorial(project_id: UUID) -> dict[str, Any]:
        current = storage.get_project(str(project_id))
        return editorial_report(current["project"], current["revision"])

    def edit_story(project_id: UUID, body: dict[str, Any], mode: str) -> dict[str, Any]:
        issues = schema_issues("story-edit", body)
        if issues:
            raise StoryEditError(issues)
        current = storage.get_project(str(project_id))
        base_revision = body["expected_revision"]
        if current["revision"] != base_revision:
            raise Conflict(
                f"Expected revision {base_revision}; current revision is {current['revision']}."
            )
        plan = plan_story_edit(current["project"], body)
        # Adapter-specific timing also needs review when the shot's length changes.
        resized = set(plan["impact"]["resized_shot_ids"])
        for seq_index, sequence in enumerate(plan["project"]["sequences"]):
            for scene_index, scene in enumerate(sequence["scenes"]):
                for shot_index, shot in enumerate(scene["shots"]):
                    extension = shot.get("extensions", {}).get(EXTENSION_KEY)
                    if shot["shot_id"] in resized and extension is not None:
                        issues = validate_scene(extension, shot["duration_frames"])
                        if issues:
                            prefix = (
                                f"/sequences/{seq_index}/scenes/{scene_index}/shots/{shot_index}"
                                f"/extensions/{EXTENSION_KEY}"
                            )
                            raise StoryEditError(
                                [
                                    {
                                        "path": prefix + issue["path"],
                                        "code": "invalid_blender_scene",
                                        "message": issue["message"],
                                    }
                                    for issue in issues
                                ]
                            )
        revision = base_revision
        if mode == "apply" and plan["changed"]:
            # Storage performs the compare-and-swap inside a write transaction.
            storage.update_project(str(project_id), base_revision, plan["project"])
            revision += 1
        plan["report"]["project_revision"] = revision
        return {"mode": mode, "base_revision": base_revision, "revision": revision, **plan}

    @app.post(
        "/api/v1/projects/{project_id}/story-edits/preview",
        dependencies=[Depends(require_auth)],
        tags=["editorial"],
    )
    def preview_story_edit(project_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        return edit_story(project_id, body, "preview")

    @app.post(
        "/api/v1/projects/{project_id}/story-edits",
        dependencies=[Depends(require_auth)],
        tags=["editorial"],
    )
    def apply_story_edit(project_id: UUID, body: dict[str, Any]) -> dict[str, Any]:
        return edit_story(project_id, body, "apply")

    @app.post(
        "/api/v1/projects/{project_id}/assets",
        dependencies=[Depends(require_auth)],
        status_code=201,
        tags=["assets"],
    )
    def import_asset(
        project_id: UUID,
        file: UploadFile,
        expected_revision: Annotated[int, Form(ge=1)],
        kind: Annotated[Literal["image", "video", "audio", "model", "other"], Form()],
    ) -> dict[str, Any]:
        key = str(project_id)
        current = storage.get_project(key)
        if current["revision"] != expected_revision:
            raise Conflict(
                f"Expected revision {expected_revision}; current revision is {current['revision']}."
            )
        root = project_root(key)
        assets_dir = (root / "assets").resolve()
        if not assets_dir.is_relative_to(root):
            raise Conflict("Asset storage must remain inside the project directory.")
        assets_dir.mkdir(parents=True, exist_ok=True)
        asset_id = str(uuid4())
        supplied_name = PurePosixPath((file.filename or "upload").replace("\\", "/")).name
        supplied_name = "".join(c for c in supplied_name if ord(c) >= 32)[:255] or "upload"
        suffix = Path(supplied_name).suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
            suffix = ".bin"
        destination = assets_dir / f"{asset_id}{suffix}"
        digest = hashlib.sha256()
        total = 0
        committed = False
        created = False
        try:
            with destination.open("xb") as output:
                created = True
                while chunk := file.file.read(1024 * 1024):
                    total += len(chunk)
                    if total > max_upload_bytes:
                        raise HTTPException(status_code=413, detail={"code": "asset_too_large"})
                    digest.update(chunk)
                    output.write(chunk)
            asset = {
                "asset_id": asset_id,
                "kind": kind,
                "uri": f"asset://{asset_id}",
                "path": f"assets/{asset_id}{suffix}",
                "sha256": digest.hexdigest(),
                "source_name": supplied_name,
            }
            if file.content_type and len(file.content_type) <= 128:
                asset["media_type"] = file.content_type
            updated = storage.attach_asset(key, expected_revision, asset)
            committed = True
            return {"asset": asset, "revision": updated["revision"]}
        finally:
            file.file.close()
            if created and not committed:
                destination.unlink(missing_ok=True)

    @app.get(
        "/api/v1/projects/{project_id}/assets/{asset_id}",
        dependencies=[Depends(require_auth)],
        tags=["assets"],
    )
    def get_asset(project_id: UUID, asset_id: UUID) -> FileResponse:
        key = str(project_id)
        project = storage.get_project(key)["project"]
        asset = next(
            (item for item in project["assets"] if item["asset_id"] == str(asset_id)), None
        )
        if asset is None:
            raise NotFound("Asset not found.")
        root = project_root(key)
        path = (root / asset["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise NotFound("Asset file not found.")
        return FileResponse(path, media_type=asset.get("media_type"))

    @app.post(
        "/api/v1/projects/{project_id}/validate",
        dependencies=[Depends(require_auth)],
        tags=["projects"],
    )
    def validate_saved_project(project_id: UUID) -> dict[str, Any]:
        saved = storage.get_project(str(project_id))
        return {
            "revision": saved["revision"],
            **summarize_project(saved["project"], storage.directory),
        }

    @app.post(
        "/api/v1/projects/{project_id}/jobs",
        dependencies=[Depends(require_auth)],
        status_code=202,
        tags=["jobs"],
    )
    def create_job(project_id: UUID, body: CreateJob) -> dict[str, Any]:
        params = None
        if body.operation == "render.shot.blender":
            if body.shot_id is None:
                raise HTTPException(status_code=422, detail={"code": "shot_id_required"})
            saved = storage.get_project(str(project_id))
            if saved["revision"] != body.expected_revision:
                raise Conflict("Project revision changed before render submission.")
            try:
                validate_render_request(
                    saved["project"],
                    str(body.shot_id),
                    body.frame_start,
                    body.frame_end_exclusive,
                )
            except RenderError as exc:
                raise HTTPException(
                    status_code=422, detail={"code": exc.code, "message": str(exc)}
                ) from exc
            params = {
                "shot_id": str(body.shot_id),
                "frame_start": body.frame_start,
                "frame_end_exclusive": body.frame_end_exclusive,
            }
        elif (
            body.shot_id is not None
            or body.frame_start != 0
            or body.frame_end_exclusive is not None
        ):
            raise HTTPException(status_code=422, detail={"code": "unexpected_render_fields"})
        job = storage.enqueue(str(project_id), body.expected_revision, body.operation, params)
        worker.notify()
        return job

    @app.get("/api/v1/jobs/{job_id}", dependencies=[Depends(require_auth)], tags=["jobs"])
    def get_job(job_id: UUID) -> dict[str, Any]:
        return storage.get_job(str(job_id))

    @app.get(
        "/api/v1/jobs/{job_id}/frames/{frame_index}",
        dependencies=[Depends(require_auth)],
        tags=["jobs"],
    )
    def get_rendered_frame(job_id: UUID, frame_index: int) -> FileResponse:
        job = storage.get_job(str(job_id))
        if job["state"] != "succeeded" or job["operation"] != "render.shot.blender":
            raise NotFound("Rendered frame is not available.")
        frame = next(
            (item for item in job["result"]["frames"] if item["index"] == frame_index), None
        )
        if frame is None:
            raise NotFound("Rendered frame not found.")
        path = (storage.directory / frame["path"]).resolve()
        if not path.is_relative_to(storage.directory) or not path.is_file():
            raise NotFound("Rendered frame file not found.")
        return FileResponse(path, media_type="image/png")

    @app.post("/api/v1/jobs/{job_id}/cancel", dependencies=[Depends(require_auth)], tags=["jobs"])
    def cancel_job(job_id: UUID) -> dict[str, Any]:
        return storage.cancel_job(str(job_id))

    @app.get(
        "/api/v1/projects/{project_id}/events",
        dependencies=[Depends(require_auth)],
        tags=["events"],
    )
    async def events(
        project_id: UUID,
        request: Request,
        after_id: int = Query(default=0, ge=0),
        last_event_id: int | None = Header(default=None, ge=0, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        project_key = str(project_id)
        storage.get_project(project_key)
        cursor = max(after_id, last_event_id or 0)

        async def stream():
            nonlocal cursor
            idle_ticks = 0
            yield ": connected\n\n"
            while not await request.is_disconnected():
                batch = storage.events_after(project_key, cursor)
                for event in batch:
                    cursor = event["event_id"]
                    data = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
                    yield f"id: {cursor}\nevent: {event['type']}\ndata: {data}\n\n"
                idle_ticks = 0 if batch else idle_ticks + 1
                if idle_ticks >= 30:
                    yield ": heartbeat\n\n"
                    idle_ticks = 0
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
        )

    return app
