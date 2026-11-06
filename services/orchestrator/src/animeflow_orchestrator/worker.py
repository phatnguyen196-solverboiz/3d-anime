"""Single local worker for durable, snapshot-based jobs."""

import logging
from threading import Event, Thread

from animeflow_blender import RenderError, render_shot
from animeflow_contracts.validation import schema_issues
from animeflow_project.summary import summarize_project

from animeflow_orchestrator.instance_lock import InstanceLock
from animeflow_orchestrator.storage import Storage

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, storage: Storage):
        self.storage = storage
        self._stop = Event()
        self._wake = Event()
        self._thread: Thread | None = None
        self._lock = InstanceLock(storage.directory)

    def start(self) -> None:
        self._lock.acquire()
        try:
            self.storage.recover_interrupted_jobs()
            self._thread = Thread(target=self._run, name="animeflow-worker", daemon=True)
            self._thread.start()
        except BaseException:
            self._lock.release()
            raise

    def notify(self) -> None:
        self._wake.set()

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                logger.error("Worker did not stop; retaining its instance lock.")
                return
        self._lock.release()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                claimed = self.storage.claim_next()
                if claimed is None:
                    self._wake.wait(timeout=0.5)
                    self._wake.clear()
                    continue
                job, snapshot = claimed
                try:
                    if job["operation"] == "project.validate":
                        result = summarize_project(snapshot, self.storage.directory)
                    elif job["operation"] == "render.shot.blender":
                        params = snapshot["params"]
                        result = render_shot(
                            snapshot["project"],
                            params["shot_id"],
                            job["job_id"],
                            self.storage.directory,
                            frame_start=params["frame_start"],
                            frame_end_exclusive=params["frame_end_exclusive"],
                            should_cancel=lambda job_id=job["job_id"]: (
                                self._stop.is_set()
                                or self.storage.get_job(job_id)["state"] == "cancel_requested"
                            ),
                        )
                        if schema_issues("render-result", result):
                            raise RenderError(
                                "invalid_result", "Renderer output violated RenderResult schema."
                            )
                    else:
                        raise ValueError("Unsupported operation.")
                    self.storage.finish_job(job["job_id"], result=result)
                except RenderError as exc:
                    if self._stop.is_set() and exc.code == "render_cancelled":
                        return  # Startup recovery requeues the interrupted snapshot.
                    logger.warning("Job %s: %s: %s", job["job_id"], exc.code, exc)
                    self.storage.finish_job(
                        job["job_id"], error={"code": exc.code, "message": str(exc)}
                    )
                except Exception:
                    logger.exception("Job %s failed", job["job_id"])
                    self.storage.finish_job(
                        job["job_id"],
                        error={
                            "code": "job_failed",
                            "message": "The worker could not complete this job.",
                        },
                    )
            except Exception:
                logger.exception("Worker loop failed; retrying.")
                self._stop.wait(timeout=1)
