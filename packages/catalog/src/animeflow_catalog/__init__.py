"""Research catalog; entries indicate research, not working integrations."""

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any


@lru_cache
def load_catalog() -> dict[str, Any]:
    resource = files("animeflow_catalog").joinpath("data", "repos.json")
    return json.loads(resource.read_text(encoding="utf-8"))
