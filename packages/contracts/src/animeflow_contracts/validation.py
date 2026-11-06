"""Load and validate the published contract schemas."""

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

SCHEMAS = frozenset(
    {
        "project",
        "job",
        "artifact",
        "adapter-manifest",
        "render-result",
        "story-edit",
        "editorial-report",
        "story-edit-result",
    }
)


@lru_cache
def get_schema(name: str) -> dict[str, Any]:
    if name not in SCHEMAS:
        raise ValueError(f"Unknown schema: {name}")
    resource = files("animeflow_contracts").joinpath("schemas", f"{name}.schema.json")
    schema = json.loads(resource.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


@lru_cache
def _registry() -> Registry:
    # Resolve published local contracts without fetching animeflow.local URLs.
    return Registry().with_resources(
        (get_schema(name)["$id"], Resource.from_contents(get_schema(name)))
        for name in sorted(SCHEMAS)
    )


def schema_issues(name: str, instance: Any) -> list[dict[str, str]]:
    validator = Draft202012Validator(
        get_schema(name), format_checker=FormatChecker(), registry=_registry()
    )
    errors = sorted(
        validator.iter_errors(instance), key=lambda error: str(list(error.absolute_path))
    )
    return [
        {
            "path": "/"
            + "/".join(
                str(part).replace("~", "~0").replace("/", "~1") for part in error.absolute_path
            ),
            "code": f"schema.{error.validator}",
            "message": error.message,
        }
        for error in errors
    ]
