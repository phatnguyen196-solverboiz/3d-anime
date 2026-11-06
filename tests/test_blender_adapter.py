import copy
import hashlib
import json
import struct
import time
import zlib
from pathlib import Path

import pytest
from animeflow_api.app import create_app
from animeflow_blender import RenderError, render_shot, validate_scene
from animeflow_blender.runner import _png_dimensions, validate_render_request
from animeflow_contracts.validation import schema_issues
from animeflow_orchestrator.storage import Storage
from animeflow_project.validation import validate_project
from fastapi.testclient import TestClient

TOKEN = "local-test-token-" + "x" * 32
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
SHOT_ID = "2673bbee-bcbc-4591-8bc6-795fc5463c17"


@pytest.fixture
def blender_project():
    path = Path(__file__).resolve().parents[1] / "fixtures/blender-primitive-project/project.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _png(width, height):
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    pixels = b"".join(b"\0" + b"\x33\x66\x99" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(pixels))
        + chunk(b"IEND", b"")
    )


def test_png_validation_rejects_truncation(tmp_path):
    path = tmp_path / "incomplete.png"
    path.write_bytes(_png(2, 2)[:-12])
    with pytest.raises(RenderError, match="Truncated PNG"):
        _png_dimensions(path)


def test_blender_scene_validation_and_range(blender_project):
    assert validate_project(blender_project) == []
    shot, scene, end = validate_render_request(blender_project, SHOT_ID, 2, 5)
    assert shot["duration_frames"] == 24
    assert end == 5
    invalid = copy.deepcopy(scene)
    invalid["objects"][1]["name"] = "floor"
    invalid["objects"][1]["keyframes"][1]["frame"] = 24
    issues = validate_scene(invalid, 24)
    assert {issue["path"] for issue in issues} == {
        "/objects/1/name",
        "/objects/1/keyframes/1/frame",
    }
    with pytest.raises(RenderError, match="inside the shot"):
        validate_render_request(blender_project, SHOT_ID, 23, 25)


def test_render_manifest_verifies_pngs_and_hashes(tmp_path, blender_project, monkeypatch):
    monkeypatch.setenv("ANIMEFLOW_BLENDER_BIN", "fake-blender")
    monkeypatch.setattr("animeflow_blender.runner.shutil.which", lambda _: "fake-blender")

    class FakeBlender:
        returncode = 0

        def __init__(self, argv, **_kwargs):
            assert argv[1:7] == [
                "--background",
                "--factory-startup",
                "--offline-mode",
                "--python-exit-code",
                "1",
                "--python",
            ]
            request = json.loads(Path(argv[-1]).read_text(encoding="utf-8"))
            folder = Path(request["frames_dir"])
            for index in range(request["frame_start"], request["frame_end_exclusive"]):
                (folder / f"frame_{index:06d}.png").write_bytes(_png(320, 180))
            Path(request["result_path"]).write_text(
                json.dumps({"blender_version": "test-double", "rendered_frames": 3}),
                encoding="utf-8",
            )

        def poll(self):
            return 0

    monkeypatch.setattr("animeflow_blender.runner.subprocess.Popen", FakeBlender)
    store = Storage(tmp_path)
    store.create_project(blender_project)
    job = store.enqueue(
        blender_project["project_id"],
        1,
        "render.shot.blender",
        {"shot_id": SHOT_ID, "frame_start": 2, "frame_end_exclusive": 5},
    )
    store.claim_next()
    manifest = render_shot(blender_project, SHOT_ID, job["job_id"], tmp_path, 2, 5)
    store.finish_job(job["job_id"], result=manifest)
    assert manifest["frame_start"] == 2
    assert manifest["frame_end_exclusive"] == 5
    assert [frame["index"] for frame in manifest["frames"]] == [2, 3, 4]
    assert not schema_issues("render-result", manifest)
    path = tmp_path / manifest["frames"][0]["path"]
    assert manifest["frames"][0]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    with TestClient(app) as client:
        response = client.get(f"/api/v1/jobs/{job['job_id']}/frames/2", headers=HEADERS)
        assert response.status_code == 200
        assert response.content == path.read_bytes()


def test_missing_blender_fails_job_with_specific_error(tmp_path, blender_project, monkeypatch):
    monkeypatch.setenv("ANIMEFLOW_BLENDER_BIN", "definitely-absent-blender")
    app = create_app(data_dir=tmp_path, api_token=TOKEN)
    with TestClient(app) as client:
        assert client.get("/api/v1/adapters/blender", headers=HEADERS).json()["status"] == (
            "missing_binary"
        )
        created = client.post(
            "/api/v1/projects", json={"project": blender_project}, headers=HEADERS
        )
        assert created.status_code == 201, created.text
        response = client.post(
            f"/api/v1/projects/{blender_project['project_id']}/jobs",
            json={
                "operation": "render.shot.blender",
                "expected_revision": 1,
                "shot_id": SHOT_ID,
                "frame_start": 0,
                "frame_end_exclusive": 2,
            },
            headers=HEADERS,
        )
        assert response.status_code == 202, response.text
        job_id = response.json()["job_id"]
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            job = client.get(f"/api/v1/jobs/{job_id}", headers=HEADERS).json()
            if job["state"] in ("failed", "succeeded", "cancelled"):
                break
            time.sleep(0.02)
        assert job["state"] == "failed"
        assert job["error"]["code"] == "blender_missing"
        assert not schema_issues("job", job)
        assert client.get(f"/api/v1/jobs/{job_id}/frames/0", headers=HEADERS).status_code == 404
