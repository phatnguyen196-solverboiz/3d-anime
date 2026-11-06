"""Run Blender in a separate process and verify every rendered frame."""

import hashlib
import json
import os
import shutil
import struct
import subprocess
import time
import zlib
from collections.abc import Callable
from importlib.resources import files
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from jsonschema import Draft202012Validator

EXTENSION_KEY = "animeflow.blender.scene.v1"
ADAPTER_ID = "animeflow.blender.primitives"
ADAPTER_VERSION = "0.1.0"


class RenderError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def blender_executable() -> str | None:
    configured = os.environ.get("ANIMEFLOW_BLENDER_BIN", "").strip()
    if configured:
        return shutil.which(configured)
    return shutil.which("blender")


def find_shot(project: dict[str, Any], shot_id: str) -> dict[str, Any]:
    for sequence in project["sequences"]:
        for scene in sequence["scenes"]:
            for shot in scene["shots"]:
                if shot["shot_id"] == shot_id:
                    return shot
    raise RenderError("shot_not_found", "Shot does not exist in this project revision.")


def validate_scene(scene: Any, duration_frames: int) -> list[dict[str, str]]:
    schema = json.loads(files("animeflow_blender").joinpath("scene.schema.json").read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(scene), key=lambda e: str(e.path))
    issues = [
        {"path": "/" + "/".join(map(str, error.path)), "message": error.message} for error in errors
    ]
    if errors:
        return issues
    if scene["camera"]["location"] == scene["camera"]["target"]:
        issues.append(
            {"path": "/camera/target", "message": "Camera target must differ from location."}
        )
    names: set[str] = set()
    for index, obj in enumerate(scene["objects"]):
        if obj["name"] in names:
            issues.append(
                {"path": f"/objects/{index}/name", "message": "Object names must be unique."}
            )
        names.add(obj["name"])
        keyframes = obj.get("keyframes", [])
        seen_frames: set[int] = set()
        for key_index, key in enumerate(keyframes):
            frame = key["frame"]
            if frame >= duration_frames or frame in seen_frames:
                issues.append(
                    {
                        "path": f"/objects/{index}/keyframes/{key_index}/frame",
                        "message": "Keyframes must be unique and inside the shot.",
                    }
                )
            seen_frames.add(frame)
        if keyframes and obj.get("rigid_body", {}).get("type") == "active":
            issues.append(
                {
                    "path": f"/objects/{index}/keyframes",
                    "message": "Active rigid bodies cannot also have transform keyframes in v1.",
                }
            )
    return issues


def validate_render_request(
    project: dict[str, Any],
    shot_id: str,
    frame_start: int = 0,
    frame_end_exclusive: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any], int]:
    shot = find_shot(project, shot_id)
    duration = shot["duration_frames"]
    end = duration if frame_end_exclusive is None else frame_end_exclusive
    if project["canvas"]["fps"]["numerator"] > 32767:
        raise RenderError("fps_unsupported", "Blender FPS numerator must be at most 32767.")
    if frame_start < 0 or end <= frame_start or end > duration:
        raise RenderError(
            "invalid_frame_range", "Render range must be inside the shot and nonempty."
        )
    limit = int(os.environ.get("ANIMEFLOW_MAX_RENDER_FRAMES", "1000"))
    if limit <= 0 or end - frame_start > limit:
        raise RenderError(
            "render_limit", f"Render range exceeds the configured {limit} frame limit."
        )
    scene = shot.get("extensions", {}).get(EXTENSION_KEY)
    if scene is None:
        raise RenderError("scene_missing", f"Shot needs extensions['{EXTENSION_KEY}'].")
    issues = validate_scene(scene, duration)
    if issues:
        raise RenderError("invalid_scene", json.dumps(issues, ensure_ascii=False))
    return shot, scene, end


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as file:
        if file.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RenderError("invalid_frame", f"Invalid PNG signature: {path.name}")
        dimensions = None
        saw_image_data = False
        while True:
            header = file.read(8)
            if len(header) != 8:
                raise RenderError("invalid_frame", f"Truncated PNG: {path.name}")
            length, kind = struct.unpack(">I4s", header)
            if length > 512 * 1024 * 1024:
                raise RenderError("invalid_frame", f"Oversized PNG chunk: {path.name}")
            if dimensions is None and (kind != b"IHDR" or length != 13):
                raise RenderError("invalid_frame", f"Missing PNG header: {path.name}")
            crc = zlib.crc32(kind)
            remaining = length
            ihdr = b""
            while remaining:
                block = file.read(min(remaining, 1024 * 1024))
                if not block:
                    raise RenderError("invalid_frame", f"Truncated PNG chunk: {path.name}")
                crc = zlib.crc32(block, crc)
                if kind == b"IHDR":
                    ihdr += block
                remaining -= len(block)
            stored_crc = file.read(4)
            if len(stored_crc) != 4 or struct.unpack(">I", stored_crc)[0] != crc:
                raise RenderError("invalid_frame", f"PNG checksum failed: {path.name}")
            if kind == b"IHDR":
                if dimensions is not None:
                    raise RenderError("invalid_frame", f"Duplicate PNG header: {path.name}")
                dimensions = struct.unpack(">II", ihdr[:8])
            elif kind == b"IDAT":
                saw_image_data = True
            elif kind == b"IEND":
                if length or not saw_image_data or file.read(1):
                    raise RenderError("invalid_frame", f"Incomplete PNG: {path.name}")
                return dimensions


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def render_shot(
    project: dict[str, Any],
    shot_id: str,
    job_id: str,
    data_dir: Path,
    frame_start: int = 0,
    frame_end_exclusive: int | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Render a project snapshot. Every output path is relative to data_dir."""
    shot, scene, end = validate_render_request(project, shot_id, frame_start, frame_end_exclusive)
    executable = blender_executable()
    if executable is None:
        raise RenderError("blender_missing", "Set ANIMEFLOW_BLENDER_BIN to a Blender executable.")
    # IDs are validated before they become filesystem components.
    UUID(job_id)
    UUID(shot_id)
    root = data_dir.resolve()
    relative_dir = Path("renders") / job_id / str(uuid4())
    run_dir = (root / relative_dir).resolve()
    if not run_dir.is_relative_to(root):
        raise RenderError("unsafe_path", "Render output escaped the data directory.")
    frames_dir = run_dir / "frames"
    frames_dir.mkdir(parents=True)
    canvas = project["canvas"]
    request = {
        "shot_id": shot["shot_id"],
        "frame_start": frame_start,
        "frame_end_exclusive": end,
        "shot_duration_frames": shot["duration_frames"],
        "fps": canvas["fps"],
        "width": canvas["width"],
        "height": canvas["height"],
        "scene": scene,
        "frames_dir": str(frames_dir),
        "result_path": str(run_dir / "blender-result.json"),
    }
    source_bytes = json.dumps(
        request | {"frames_dir": "", "result_path": ""},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    request_path = run_dir / "request.json"
    request_path.write_text(
        json.dumps(request, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    script = files("animeflow_blender").joinpath("blender_scene.py")
    command = [
        executable,
        "--background",
        "--factory-startup",
        "--offline-mode",
        "--python-exit-code",
        "1",
        "--python",
        str(script),
        "--",
        str(request_path),
    ]
    log_path = run_dir / "blender.log"
    timeout = int(os.environ.get("ANIMEFLOW_RENDER_TIMEOUT_SECONDS", "3600"))
    if timeout <= 0:
        raise RenderError("invalid_timeout", "Render timeout must be positive.")
    with log_path.open("wb") as log:
        try:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        except OSError as exc:
            raise RenderError("blender_start_failed", str(exc)) from exc
        deadline = time.monotonic() + timeout
        while process.poll() is None:
            if should_cancel and should_cancel():
                _stop_process(process)
                raise RenderError("render_cancelled", "Render was cancelled.")
            if time.monotonic() >= deadline:
                _stop_process(process)
                raise RenderError("render_timeout", f"Blender exceeded {timeout} seconds.")
            time.sleep(0.2)
    if process.returncode:
        tail = log_path.read_bytes()[-4000:].decode("utf-8", errors="replace")
        raise RenderError("blender_failed", f"Blender exited {process.returncode}: {tail}")
    result_path = run_dir / "blender-result.json"
    if not result_path.is_file():
        raise RenderError("result_missing", "Blender did not write its result metadata.")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("rendered_frames") != end - frame_start:
        raise RenderError("frame_count_mismatch", "Blender reported an unexpected frame count.")
    frame_records = []
    for index in range(frame_start, end):
        path = frames_dir / f"frame_{index:06d}.png"
        if not path.is_file():
            raise RenderError("frame_missing", f"Frame {index} is missing.")
        dimensions = _png_dimensions(path)
        if dimensions != (canvas["width"], canvas["height"]):
            raise RenderError("frame_dimensions", f"Frame {index} has dimensions {dimensions}.")
        frame_records.append(
            {
                "index": index,
                "path": (relative_dir / "frames" / path.name).as_posix(),
                "sha256": _sha256(path),
                "width": dimensions[0],
                "height": dimensions[1],
            }
        )
    if len(list(frames_dir.glob("*.png"))) != len(frame_records):
        raise RenderError("extra_frames", "Blender wrote unexpected PNG files.")
    manifest = {
        "adapter_id": ADAPTER_ID,
        "adapter_version": ADAPTER_VERSION,
        "backend_version": str(result.get("blender_version", "unknown")),
        "project_id": project["project_id"],
        "shot_id": shot_id,
        "job_id": job_id,
        "frame_start": frame_start,
        "frame_end_exclusive": end,
        "fps": canvas["fps"],
        "width": canvas["width"],
        "height": canvas["height"],
        "source_sha256": source_hash,
        "seed": scene.get("seed", 0),
        "frames": frame_records,
        "warnings": [],
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest
