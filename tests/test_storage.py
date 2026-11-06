import copy
from concurrent.futures import ThreadPoolExecutor

import pytest
from animeflow_orchestrator.instance_lock import InstanceLock
from animeflow_orchestrator.storage import Conflict, Storage


def test_revision_conflict_is_atomic(tmp_path, project):
    store = Storage(tmp_path)
    store.create_project(project)

    def update(title):
        updated = copy.deepcopy(project)
        updated["title"] = title
        try:
            return store.update_project(project["project_id"], 1, updated)["revision"]
        except Conflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(update, ["First", "Second"]))
    assert sorted(map(str, results)) == ["2", "conflict"]
    assert store.get_project(project["project_id"])["revision"] == 2


def test_job_keeps_original_snapshot_after_project_update(tmp_path, project):
    store = Storage(tmp_path)
    store.create_project(project)
    job = store.enqueue(project["project_id"], 1, "project.validate")
    changed = copy.deepcopy(project)
    changed["title"] = "New title"
    store.update_project(project["project_id"], 1, changed)
    claimed, snapshot = store.claim_next()
    assert claimed["job_id"] == job["job_id"]
    assert claimed["project_revision"] == 1
    assert snapshot["title"] == project["title"]
    store.finish_job(job["job_id"], result={"valid": True})
    assert store.get_job(job["job_id"])["state"] == "succeeded"


def test_cancellation_and_crash_recovery(tmp_path, project):
    store = Storage(tmp_path)
    store.create_project(project)
    queued = store.enqueue(project["project_id"], 1, "project.validate")
    assert store.cancel_job(queued["job_id"])["state"] == "cancelled"
    running = store.enqueue(project["project_id"], 1, "project.validate")
    store.claim_next()
    assert store.cancel_job(running["job_id"])["state"] == "cancel_requested"
    store.finish_job(running["job_id"], result={"valid": True})
    assert store.get_job(running["job_id"])["state"] == "cancelled"
    interrupted = store.enqueue(project["project_id"], 1, "project.validate")
    store.claim_next()
    Storage(tmp_path).recover_interrupted_jobs()
    assert store.get_job(interrupted["job_id"])["state"] == "queued"
    events = store.events_after(project["project_id"], 0)
    assert [event["event_id"] for event in events] == sorted(event["event_id"] for event in events)
    assert any(event["payload"].get("recovered") for event in events)


def test_single_worker_lock(tmp_path):
    first, second = InstanceLock(tmp_path), InstanceLock(tmp_path)
    first.acquire()
    try:
        with pytest.raises(RuntimeError, match="Another AnimeFlow worker"):
            second.acquire()
    finally:
        first.release()
    second.acquire()
    second.release()
