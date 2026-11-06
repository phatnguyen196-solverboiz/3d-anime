import json
from pathlib import Path

import pytest


@pytest.fixture
def project():
    path = Path(__file__).resolve().parents[1] / "fixtures" / "tiny-project" / "project.json"
    return json.loads(path.read_text(encoding="utf-8"))
