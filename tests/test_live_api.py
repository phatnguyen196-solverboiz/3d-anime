"""Exercise real HTTP and SSE rather than only an in-process client."""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

TOKEN = "live-integration-token-" + "x" * 32


def test_live_server_streams_resumable_events(tmp_path, project):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    environment = os.environ.copy()
    environment.update(ANIMEFLOW_API_TOKEN=TOKEN, ANIMEFLOW_DATA_DIR=str(tmp_path))
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "animeflow_api.app:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "error",
        ],
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        deadline = time.monotonic() + 10
        while True:
            try:
                with opener.open(base + "/api/v1/health", timeout=1) as response:
                    assert json.load(response)["status"] == "ok"
                break
            except (OSError, urllib.error.URLError):
                assert process.poll() is None, "API process exited before becoming healthy"
                assert time.monotonic() < deadline, "API did not become healthy"
                time.sleep(0.05)
        headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        create = urllib.request.Request(
            base + "/api/v1/projects",
            data=json.dumps({"project": project}).encode(),
            headers=headers,
            method="POST",
        )
        with opener.open(create, timeout=3) as response:
            assert response.status == 201
        project_id = project["project_id"]
        job = urllib.request.Request(
            base + f"/api/v1/projects/{project_id}/jobs",
            data=json.dumps({"operation": "project.validate", "expected_revision": 1}).encode(),
            headers=headers,
            method="POST",
        )
        with opener.open(job, timeout=3) as response:
            assert response.status == 202
        stream = urllib.request.Request(
            base + f"/api/v1/projects/{project_id}/events",
            headers={"Authorization": f"Bearer {TOKEN}", "Last-Event-ID": "1"},
        )
        with opener.open(stream, timeout=3) as response:
            assert response.readline() == b": connected\n"
            assert response.readline() == b"\n"
            assert response.readline().startswith(b"id: 2")
            assert response.readline() == b"event: job.queued\n"
    finally:
        process.terminate()
        process.wait(timeout=5)
