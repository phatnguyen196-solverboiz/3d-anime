import copy
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import pytest
from animeflow_api.app import create_app
from animeflow_contracts.validation import schema_issues
from animeflow_project.editorial import StoryEditError, editorial_report, plan_story_edit
from animeflow_project.timebase import frames_to_samples
from fastapi.testclient import TestClient

TOKEN = "editorial-test-token-" + "x" * 32
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def uid(name):
    return str(uuid5(NAMESPACE_URL, name))


@pytest.fixture
def story(project):
    scene = project["sequences"][0]["scenes"][0]
    scene["shots"].append(
        {
            "shot_id": uid("reaction"),
            "title": "Reaction",
            "duration_frames": 48,
            "events": [],
            "extensions": {"example.story": {"purpose": "reaction"}},
        }
    )
    project["sequences"][0]["scenes"].append(
        {
            "scene_id": uid("next-scene"),
            "title": "Next scene",
            "shots": [
                {
                    "shot_id": uid("next-shot"),
                    "title": "Next shot",
                    "duration_frames": 24,
                    "events": [],
                }
            ],
        }
    )
    return project


def request(*operations):
    return {"expected_revision": 1, "operations": list(operations)}


def attach_audio(story):
    asset_id = uid("audio")
    story["assets"].append(
        {
            "asset_id": asset_id,
            "kind": "audio",
            "uri": f"asset://{asset_id}",
            "path": "assets/voice.wav",
            "sha256": "a" * 64,
        }
    )
    story["voice_lines"][0]["audio_asset_id"] = asset_id


def test_story_fixture_and_edit_are_usable_examples():
    directory = Path(__file__).parents[1] / "fixtures/story-edit-project"
    project = json.loads((directory / "project.json").read_text(encoding="utf-8"))
    edit = json.loads((directory / "edit.json").read_text(encoding="utf-8"))
    assert editorial_report(project, 1)["duration_frames"] == 264
    plan = plan_story_edit(project, edit)
    assert plan["report"]["duration_frames"] == 240
    assert plan["report"]["duration_samples"] == 480480
    assert not schema_issues("editorial-report", plan["report"])


def test_absolute_sample_boundaries_telescope_without_rounding_drift(story):
    story["voice_lines"] = []
    story["canvas"]["fps"] = {"numerator": 30000, "denominator": 1001}
    story["canvas"]["audio_sample_rate"] = 44100
    for sequence in story["sequences"]:
        for scene in sequence["scenes"]:
            for shot in scene["shots"]:
                shot["duration_frames"] = 1
                shot["events"] = []
    report = editorial_report(story, 7)
    assert not schema_issues("editorial-report", report)
    assert report["duration_samples"] == 4414
    assert sum(shot["duration_samples"] for shot in report["shots"]) == 4414
    assert report["shots"][0]["end_sample_exclusive"] == report["shots"][1]["start_sample"]


def test_reorder_preserves_ids_local_cues_extensions_and_source_snapshot(story):
    original = copy.deepcopy(story)
    scene = story["sequences"][0]["scenes"][0]
    order = [shot["shot_id"] for shot in reversed(scene["shots"])]
    plan = plan_story_edit(
        story,
        request(
            {
                "op": "reorder_shots",
                "scene_id": scene["scene_id"],
                "shot_ids": order,
            }
        ),
    )
    assert story == original
    assert plan["project"]["voice_lines"] == story["voice_lines"]
    moved = plan["report"]["shots"][1]
    assert moved["start_frame"] == 48
    assert moved["events"][0]["local_frame"] == 12
    assert moved["events"][0]["frame"] == 60
    assert plan["report"]["voice_lines"][0]["start_frame"] == 72
    assert plan["impact"]["render_review_shot_ids"] == []
    assert (
        plan["project"]["sequences"][0]["scenes"][0]["shots"][0]["extensions"]
        == (scene["shots"][1]["extensions"])
    )


@pytest.mark.parametrize("order", [[], [uid("reaction")], [uid("reaction"), uid("next-shot")]])
def test_reorder_cannot_drop_or_import_shots(story, order):
    scene = story["sequences"][0]["scenes"][0]
    with pytest.raises(StoryEditError) as error:
        plan_story_edit(
            story,
            request(
                {
                    "op": "reorder_shots",
                    "scene_id": scene["scene_id"],
                    "shot_ids": order,
                }
            ),
        )
    assert error.value.issues[0]["code"] == "invalid_shot_order"


@pytest.mark.parametrize(
    "duration,code", [(12, "event_out_of_shot"), (59, "voice_line_out_of_shot")]
)
def test_resize_rejects_lost_cues_and_dialogue(story, duration, code):
    original = copy.deepcopy(story)
    shot_id = story["voice_lines"][0]["shot_id"]
    with pytest.raises(StoryEditError) as error:
        plan_story_edit(
            story,
            request(
                {
                    "op": "set_shot_duration",
                    "shot_id": shot_id,
                    "duration_frames": duration,
                }
            ),
        )
    assert code in {issue["code"] for issue in error.value.issues}
    assert story == original


def test_valid_resize_ripples_global_positions_without_retiming_local_audio(story):
    line = story["voice_lines"][0]
    plan = plan_story_edit(
        story,
        request(
            {
                "op": "set_shot_duration",
                "shot_id": line["shot_id"],
                "duration_frames": 60,
            }
        ),
    )
    assert plan["project"]["voice_lines"][0] == line
    assert plan["report"]["duration_frames"] == 132
    assert [shot["start_frame"] for shot in plan["report"]["shots"]] == [0, 60, 108]
    assert plan["report"]["duration_samples"] == frames_to_samples(132, 24000, 1001, 48000)
    assert plan["impact"]["resized_shot_ids"] == [line["shot_id"]]


def test_spoken_text_change_requires_explicit_audio_detach_and_retains_asset(story):
    attach_audio(story)
    operation = {
        "op": "set_voice_text",
        "voice_line_id": story["voice_lines"][0]["voice_line_id"],
        "text": "Chúng ta bắt đầu nhé!",
    }
    with pytest.raises(StoryEditError) as error:
        plan_story_edit(story, request(operation))
    assert error.value.issues[0]["code"] == "linked_audio_requires_detach"
    operation["audio_policy"] = "detach"
    plan = plan_story_edit(story, request(operation))
    assert "audio_asset_id" not in plan["project"]["voice_lines"][0]
    assert plan["project"]["assets"] == story["assets"]
    assert "audio_asset_id" in story["voice_lines"][0]
    assert "alignment" in plan["impact"]["rebuild_candidates"]


def test_failed_batch_is_atomic_and_noop_does_not_invalidate(story):
    original = copy.deepcopy(story)
    text_op = {
        "op": "set_voice_text",
        "voice_line_id": story["voice_lines"][0]["voice_line_id"],
        "text": "Câu đã sửa",
    }
    with pytest.raises(StoryEditError):
        plan_story_edit(
            story,
            request(
                text_op,
                {"op": "set_shot_duration", "shot_id": uid("missing"), "duration_frames": 10},
            ),
        )
    assert story == original
    noop = plan_story_edit(story, request({**text_op, "text": story["voice_lines"][0]["text"]}))
    assert noop["changed"] is False
    assert noop["impact"]["rebuild_candidates"] == []


def test_same_speaker_overlap_is_advisory_and_reports_missing_audio(story):
    line = copy.deepcopy(story["voice_lines"][0])
    line["voice_line_id"] = uid("overlapping-line")
    line["start_frame"] = 30
    story["voice_lines"].append(line)
    report = editorial_report(story, 1)
    assert [warning["code"] for warning in report["warnings"]].count("same_speaker_overlap") == 1
    assert [warning["code"] for warning in report["warnings"]].count("voice_audio_unlinked") == 2


def test_api_preview_apply_conflicts_auth_and_noop(tmp_path, story):
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    with TestClient(app) as client:
        project_url = f"/api/v1/projects/{story['project_id']}"
        url = project_url + "/story-edits"
        client.post("/api/v1/projects", json={"project": story}, headers=HEADERS)
        edit = request(
            {
                "op": "set_voice_text",
                "voice_line_id": story["voice_lines"][0]["voice_line_id"],
                "text": "Hẹn gặp lại!",
            }
        )
        assert client.post(url + "/preview", json=edit).status_code == 401
        preview = client.post(url + "/preview", json=edit, headers=HEADERS)
        assert preview.status_code == 200, preview.text
        assert not schema_issues("story-edit-result", preview.json())
        assert client.get(project_url, headers=HEADERS).json()["project"] == story
        result = client.post(url, json=edit, headers=HEADERS)
        assert result.status_code == 200, result.text
        assert result.json()["revision"] == 2
        assert not schema_issues("story-edit-result", result.json())
        assert client.post(url, json=edit, headers=HEADERS).status_code == 409
        assert client.post(url + "/preview", json=edit, headers=HEADERS).status_code == 409
        edit["expected_revision"] = 2
        noop = client.post(url, json=edit, headers=HEADERS).json()
        assert noop["changed"] is False and noop["revision"] == 2
        report = client.get(project_url + "/editorial", headers=HEADERS).json()
        assert report["project_revision"] == 2
        assert not schema_issues("editorial-report", report)
        assert client.post(url, json={"operations": []}, headers=HEADERS).status_code == 422


def test_api_concurrent_edit_cannot_overwrite_newer_revision(tmp_path, story, monkeypatch):
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    storage = app.state.storage
    storage.create_project(story)
    original_update = storage.update_project

    def another_writer_wins(project_id, revision, candidate):
        changed = copy.deepcopy(story)
        changed["title"] = "Concurrent writer"
        original_update(project_id, revision, changed)
        return original_update(project_id, revision, candidate)

    monkeypatch.setattr(storage, "update_project", another_writer_wins)
    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/projects/{story['project_id']}/story-edits",
            headers=HEADERS,
            json=request(
                {
                    "op": "set_voice_text",
                    "voice_line_id": story["voice_lines"][0]["voice_line_id"],
                    "text": "Must not win",
                }
            ),
        )
    assert response.status_code == 409
    stored = storage.get_project(story["project_id"])
    assert stored["project"]["title"] == "Concurrent writer"
    assert stored["project"]["voice_lines"] == story["voice_lines"]


def test_api_resize_checks_blender_keyframes_before_commit(tmp_path):
    path = Path(__file__).parents[1] / "fixtures/blender-primitive-project/project.json"
    project = json.loads(path.read_text(encoding="utf-8"))
    shot = project["sequences"][0]["scenes"][0]["shots"][0]
    app = create_app(data_dir=tmp_path, api_token=TOKEN, start_worker=False)
    app.state.storage.create_project(project)
    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/projects/{project['project_id']}/story-edits",
            headers=HEADERS,
            json=request(
                {"op": "set_shot_duration", "shot_id": shot["shot_id"], "duration_frames": 1}
            ),
        )
    assert response.status_code == 422
    assert any(
        issue["code"] == "invalid_blender_scene" for issue in response.json()["detail"]["issues"]
    )
    assert all(
        "/extensions/animeflow.blender.scene.v1/" in issue["path"]
        for issue in response.json()["detail"]["issues"]
    )
    assert app.state.storage.get_project(project["project_id"])["revision"] == 1
