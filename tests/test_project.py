import copy

import pytest
from animeflow_contracts.validation import get_schema, schema_issues
from animeflow_project.summary import summarize_project
from animeflow_project.timebase import frames_to_samples
from animeflow_project.validation import validate_project


def test_schemas_and_sample_project_are_valid(project):
    for name in ("project", "job", "artifact", "adapter-manifest"):
        assert get_schema(name)["$schema"].endswith("2020-12/schema")
    assert validate_project(project) == []
    assert summarize_project(project)["duration_samples"] == 240240


@pytest.mark.parametrize(
    ("change", "expected_code"),
    [
        (lambda p: p["canvas"]["fps"].update(denominator=0), "schema.minimum"),
        (lambda p: p["voice_lines"][0].update(start_frame=119), "voice_line_out_of_shot"),
        (
            lambda p: p["voice_lines"][0].update(
                character_id="99999999-9999-4999-8999-999999999999"
            ),
            "missing_character",
        ),
        (
            lambda p: p["sequences"][0]["scenes"][0]["shots"][0]["events"][0].update(frame=120),
            "event_out_of_shot",
        ),
        (lambda p: p["characters"].append(copy.deepcopy(p["characters"][0])), "duplicate_id"),
    ],
)
def test_invalid_project_is_rejected(project, change, expected_code):
    change(project)
    assert expected_code in {issue["code"] for issue in validate_project(project)}


def test_asset_path_and_uri_must_remain_safe(project):
    project["assets"].append(
        {
            "asset_id": "f9bd1630-1aa9-43e1-93a1-28885a829da3",
            "kind": "audio",
            "uri": "asset://f9bd1630-1aa9-43e1-93a1-28885a829da3",
            "path": "assets/../../secret.wav",
            "sha256": "0" * 64,
        }
    )
    assert "unsafe_asset_path" in {issue["code"] for issue in validate_project(project)}
    project["assets"][0]["path"] = "assets/voice.wav"
    project["assets"][0]["uri"] = "asset://a9bd1630-1aa9-43e1-93a1-28885a829da3"
    assert "asset_uri_mismatch" in {issue["code"] for issue in validate_project(project)}


def test_timebase_uses_absolute_integer_positions():
    assert frames_to_samples(24, 24, 1, 48000) == 48000
    assert frames_to_samples(24000, 24000, 1001, 48000) == 48048000
    assert frames_to_samples(1, 2, 1, 1) == 1
    with pytest.raises(ValueError):
        frames_to_samples(-1, 24, 1, 48000)
    assert schema_issues("job", {})  # job contract rejects missing fields
