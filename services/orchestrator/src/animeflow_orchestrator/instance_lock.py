"""Prevent two local workers from recovering jobs in the same data directory."""

import os
from pathlib import Path
from typing import BinaryIO


class InstanceLock:
    def __init__(self, directory: Path):
        self.path = directory / ".worker.lock"
        self._file: BinaryIO | None = None

    def acquire(self) -> None:
        handle = self.path.open("a+b")
        try:
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            handle.close()
            raise RuntimeError("Another AnimeFlow worker is using this data directory.") from exc
        self._file = handle

    def release(self) -> None:
        if self._file is None:
            return
        try:
            self._file.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
        finally:
            self._file.close()
            self._file = None
