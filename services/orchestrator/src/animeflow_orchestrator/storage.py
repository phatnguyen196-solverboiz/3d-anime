"""SQLite persistence for local projects, immutable job inputs, and events."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from animeflow_project.validation import validate_project


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


def now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def encode(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


class Storage:
    """Each operation opens its own connection; write transactions are serialized by SQLite."""

    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.database = self.directory / "animeflow.sqlite3"
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > 1:
                raise RuntimeError(
                    f"Database version {version} is newer than this application supports."
                )
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    spec_json TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(project_id),
                    project_revision INTEGER NOT NULL,
                    operation TEXT NOT NULL,
                    state TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    result_json TEXT,
                    error_json TEXT
                );
                CREATE INDEX IF NOT EXISTS jobs_state_created ON jobs(state, created_at);
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES projects(project_id),
                    type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS events_project_id ON events(project_id, event_id);
                PRAGMA user_version=1;
                """
            )

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.database, timeout=15, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
            except BaseException:
                db.rollback()
                raise
            else:
                db.commit()

    @staticmethod
    def _event(db: sqlite3.Connection, project_id: str, kind: str, payload: dict) -> None:
        db.execute(
            "INSERT INTO events(project_id, type, payload_json, created_at) VALUES (?, ?, ?, ?)",
            (project_id, kind, encode(payload), now()),
        )

    @staticmethod
    def _project(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "project": json.loads(row["spec_json"]),
            "revision": row["revision"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    @staticmethod
    def _job(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "job_id": row["job_id"],
            "project_id": row["project_id"],
            "project_revision": row["project_revision"],
            "operation": row["operation"],
            "state": row["state"],
            "created_at": row["created_at"],
            "started_at": row["started_at"],
            "finished_at": row["finished_at"],
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "error": json.loads(row["error_json"]) if row["error_json"] else None,
        }

    def create_project(self, project: dict[str, Any]) -> dict[str, Any]:
        project_id = project["project_id"]
        timestamp = now()
        with self.transaction() as db:
            if db.execute("SELECT 1 FROM projects WHERE project_id=?", (project_id,)).fetchone():
                raise Conflict("Project ID already exists.")
            db.execute(
                "INSERT INTO projects VALUES (?, ?, 1, ?, ?)",
                (project_id, encode(project), timestamp, timestamp),
            )
            self._event(db, project_id, "project.created", {"revision": 1})
        return self.get_project(project_id)

    def list_projects(self) -> list[dict[str, Any]]:
        with self.connection() as db:
            rows = db.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC, project_id"
            ).fetchall()
        return [
            {
                "project_id": row["project_id"],
                "title": json.loads(row["spec_json"])["title"],
                "revision": row["revision"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def get_project(self, project_id: str) -> dict[str, Any]:
        with self.connection() as db:
            row = db.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
        if row is None:
            raise NotFound("Project not found.")
        return self._project(row)

    def update_project(
        self, project_id: str, expected_revision: int, project: dict
    ) -> dict[str, Any]:
        with self.transaction() as db:
            row = db.execute(
                "SELECT revision FROM projects WHERE project_id=?", (project_id,)
            ).fetchone()
            if row is None:
                raise NotFound("Project not found.")
            if row["revision"] != expected_revision:
                raise Conflict(
                    f"Expected revision {expected_revision}; current revision is {row['revision']}."
                )
            revision = expected_revision + 1
            db.execute(
                "UPDATE projects SET spec_json=?, revision=?, updated_at=? WHERE project_id=?",
                (encode(project), revision, now(), project_id),
            )
            self._event(db, project_id, "project.updated", {"revision": revision})
        return self.get_project(project_id)

    def attach_asset(self, project_id: str, expected_revision: int, asset: dict) -> dict[str, Any]:
        with self.transaction() as db:
            row = db.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
            if row is None:
                raise NotFound("Project not found.")
            if row["revision"] != expected_revision:
                raise Conflict(
                    f"Expected revision {expected_revision}; current revision is {row['revision']}."
                )
            project = json.loads(row["spec_json"])
            project["assets"].append(asset)
            if validate_project(project):
                raise ValueError("Generated asset metadata did not satisfy the project contract.")
            revision = expected_revision + 1
            db.execute(
                "UPDATE projects SET spec_json=?, revision=?, updated_at=? WHERE project_id=?",
                (encode(project), revision, now(), project_id),
            )
            self._event(
                db,
                project_id,
                "asset.imported",
                {"revision": revision, "asset_id": asset["asset_id"]},
            )
        return self.get_project(project_id)

    def enqueue(
        self,
        project_id: str,
        expected_revision: int,
        operation: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        job_id = str(uuid4())
        timestamp = now()
        with self.transaction() as db:
            row = db.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
            if row is None:
                raise NotFound("Project not found.")
            if row["revision"] != expected_revision:
                raise Conflict(
                    f"Expected revision {expected_revision}; current revision is {row['revision']}."
                )
            snapshot = (
                encode({"project": json.loads(row["spec_json"]), "params": params})
                if params is not None
                else row["spec_json"]
            )
            db.execute(
                """INSERT INTO jobs(
                       job_id, project_id, project_revision, operation, state,
                       input_json, created_at)
                   VALUES (?, ?, ?, ?, 'queued', ?, ?)""",
                (job_id, project_id, row["revision"], operation, snapshot, timestamp),
            )
            self._event(
                db, project_id, "job.queued", {"job_id": job_id, "revision": row["revision"]}
            )
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self.connection() as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise NotFound("Job not found.")
        return self._job(row)

    def claim_next(self) -> tuple[dict[str, Any], dict[str, Any]] | None:
        with self.transaction() as db:
            row = db.execute(
                "SELECT * FROM jobs WHERE state='queued' ORDER BY created_at, job_id LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            db.execute(
                "UPDATE jobs SET state='running', started_at=? WHERE job_id=?",
                (now(), row["job_id"]),
            )
            self._event(db, row["project_id"], "job.running", {"job_id": row["job_id"]})
            updated = db.execute("SELECT * FROM jobs WHERE job_id=?", (row["job_id"],)).fetchone()
            return self._job(updated), json.loads(row["input_json"])

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        with self.transaction() as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None:
                raise NotFound("Job not found.")
            if row["state"] == "queued":
                db.execute(
                    "UPDATE jobs SET state='cancelled', finished_at=? WHERE job_id=?",
                    (now(), job_id),
                )
                self._event(db, row["project_id"], "job.cancelled", {"job_id": job_id})
            elif row["state"] == "running":
                db.execute("UPDATE jobs SET state='cancel_requested' WHERE job_id=?", (job_id,))
                self._event(db, row["project_id"], "job.cancel_requested", {"job_id": job_id})
        return self.get_job(job_id)

    def finish_job(
        self, job_id: str, result: dict | None = None, error: dict | None = None
    ) -> None:
        with self.transaction() as db:
            row = db.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
            if row is None:
                raise NotFound("Job not found.")
            if row["state"] not in ("running", "cancel_requested"):
                raise Conflict("Only a running job can finish.")
            state = (
                "cancelled"
                if row["state"] == "cancel_requested"
                else ("failed" if error else "succeeded")
            )
            db.execute(
                "UPDATE jobs SET state=?, finished_at=?, result_json=?, error_json=? "
                "WHERE job_id=?",
                (
                    state,
                    now(),
                    encode(result) if state == "succeeded" else None,
                    encode(error) if state == "failed" else None,
                    job_id,
                ),
            )
            self._event(db, row["project_id"], f"job.{state}", {"job_id": job_id})

    def recover_interrupted_jobs(self) -> None:
        """Only call when starting the single local worker after a process restart."""
        with self.transaction() as db:
            rows = db.execute(
                "SELECT * FROM jobs WHERE state IN ('running', 'cancel_requested')"
            ).fetchall()
            for row in rows:
                state = "queued" if row["state"] == "running" else "cancelled"
                db.execute(
                    "UPDATE jobs SET state=?, started_at=NULL, finished_at=? WHERE job_id=?",
                    (state, now() if state == "cancelled" else None, row["job_id"]),
                )
                self._event(
                    db,
                    row["project_id"],
                    f"job.{state}",
                    {"job_id": row["job_id"], "recovered": True},
                )

    def events_after(self, project_id: str, cursor: int, limit: int = 100) -> list[dict[str, Any]]:
        with self.connection() as db:
            rows = db.execute(
                """SELECT * FROM events WHERE project_id=? AND event_id>?
                   ORDER BY event_id LIMIT ?""",
                (project_id, cursor, limit),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "type": row["type"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
