import copy
import hashlib
import time

from animeflow_api.app import create_app
from animeflow_contracts.validation import schema_issues
from fastapi.testclient import TestClient

TOKEN = "local-test-token-" + "x" * 32
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def test_api_project_and_real_background_job(tmp_path, project):
    app = create_app(data_dir=tmp_path, api_token=TOKEN)
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json()["status"] == "ok"
        assert client.get("/api/v1/projects").status_code == 401
        created = client.post("/api/v1/projects", json={"project": project}, headers=HEADERS)
        assert created.status_code == 201
        assert created.json()["revision"] == 1
        project_id = project["project_id"]
        assert (
            client.post("/api/v1/projects", json={"project": project}, headers=HEADERS).status_code
            == 409
        )

        changed = copy.deepcopy(project)
        changed["title"] = "Một cảnh mới"
        update_url = f"/api/v1/projects/{project_id}"
        updated = client.put(
            update_url, json={"project": changed, "expected_revision": 1}, headers=HEADERS
        )
        assert updated.status_code == 200
        assert updated.json()["revision"] == 2
        assert (
            client.put(
                update_url, json={"project": changed, "expected_revision": 1}, headers=HEADERS
            ).status_code
            == 409
        )
        assert client.get(update_url, headers=HEADERS).json()["project"]["title"] == "Một cảnh mới"

        response = client.post(
            f"{update_url}/jobs",
            json={"operation": "project.validate", "expected_revision": 2},
            headers=HEADERS,
        )
        assert response.status_code == 202
        job_id = response.json()["job_id"]
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            job = client.get(f"/api/v1/jobs/{job_id}", headers=HEADERS).json()
            if job["state"] in ("succeeded", "failed", "cancelled"):
                break
            time.sleep(0.02)
        assert job["state"] == "succeeded", job
        assert not schema_issues("job", job)
        assert job["result"]["duration_samples"] == 240240
        assert job["result"]["valid"] is True
        assert (
            len(client.get("/api/v1/catalog/repos", headers=HEADERS).json()["repositories"]) >= 200
        )


def test_api_rejects_invalid_project_and_unimplemented_job(tmp_path, project):
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    with TestClient(app) as client:
        invalid = copy.deepcopy(project)
        invalid["canvas"]["fps"]["denominator"] = 0
        result = client.post("/api/v1/projects", json={"project": invalid}, headers=HEADERS)
        assert result.status_code == 422
        assert result.json()["detail"]["code"] == "invalid_project"
        client.post("/api/v1/projects", json={"project": project}, headers=HEADERS)
        result = client.post(
            f"/api/v1/projects/{project['project_id']}/jobs",
            json={"operation": "render.frames", "expected_revision": 1},
            headers=HEADERS,
        )
        assert result.status_code == 422


def test_asset_upload_is_hashed_revisioned_and_checked(tmp_path, project):
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    with TestClient(app) as client:
        client.post("/api/v1/projects", json={"project": project}, headers=HEADERS)
        project_id = project["project_id"]
        content = b"example audio bytes"
        result = client.post(
            f"/api/v1/projects/{project_id}/assets",
            files={"file": ("voice.wav", content, "audio/wav")},
            data={"kind": "audio", "expected_revision": "1"},
            headers=HEADERS,
        )
        assert result.status_code == 201, result.text
        assert result.json()["revision"] == 2
        asset = result.json()["asset"]
        assert asset["sha256"] == hashlib.sha256(content).hexdigest()
        file_url = f"/api/v1/projects/{project_id}/assets/{asset['asset_id']}"
        assert client.get(file_url, headers=HEADERS).content == content
        assert client.get(file_url).status_code == 401
        assert (
            client.post(
                f"/api/v1/projects/{project_id}/assets",
                files={"file": ("second.wav", b"other", "audio/wav")},
                data={"kind": "audio", "expected_revision": "1"},
                headers=HEADERS,
            ).status_code
            == 409
        )
        assert client.post(f"/api/v1/projects/{project_id}/validate", headers=HEADERS).json()[
            "valid"
        ]
        (tmp_path / "projects" / project_id / asset["path"]).unlink()
        validation = client.post(f"/api/v1/projects/{project_id}/validate", headers=HEADERS).json()
        assert not validation["valid"]
        assert validation["issues"][0]["code"] == "missing_asset_file"


def test_upload_limit_removes_incomplete_file(tmp_path, project, monkeypatch):
    monkeypatch.setenv("ANIMEFLOW_MAX_UPLOAD_BYTES", "4")
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    with TestClient(app) as client:
        client.post("/api/v1/projects", json={"project": project}, headers=HEADERS)
        response = client.post(
            f"/api/v1/projects/{project['project_id']}/assets",
            files={"file": ("big.bin", b"12345", "application/octet-stream")},
            data={"kind": "other", "expected_revision": "1"},
            headers=HEADERS,
        )
        assert response.status_code == 413
        assets = tmp_path / "projects" / project["project_id"] / "assets"
        assert list(assets.iterdir()) == []
