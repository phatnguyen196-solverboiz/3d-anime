"""A cut-only editorial projection and non-destructive story edit planning."""

from copy import deepcopy
from typing import Any
from uuid import UUID

from animeflow_contracts.validation import schema_issues

from animeflow_project.timebase import frames_to_samples
from animeflow_project.validation import validate_project


class StoryEditError(ValueError):
    def __init__(self, issues: list[dict[str, str]]):
        super().__init__("Story edit could not be applied.")
        self.issues = issues


def editorial_report(project: dict[str, Any], revision: int) -> dict[str, Any]:
    """Project shot-local cues onto a sequential, half-open global timeline.

    Samples are rounded at absolute boundaries, so adjacent ranges telescope
    even when the FPS/sample-rate combination has fractional samples per frame.
    This describes intended timing, not rendered media or measured audio.
    """
    issues = validate_project(project)
    if issues:
        raise StoryEditError(issues)
    canvas = project["canvas"]
    fps = canvas["fps"]

    def sample(frame: int) -> int:
        return frames_to_samples(
            frame, fps["numerator"], fps["denominator"], canvas["audio_sample_rate"]
        )

    def timing(start: int, end: int) -> dict[str, int]:
        start_sample, end_sample = sample(start), sample(end)
        return {
            "start_frame": start,
            "end_frame_exclusive": end,
            "duration_frames": end - start,
            "start_sample": start_sample,
            "end_sample_exclusive": end_sample,
            "duration_samples": end_sample - start_sample,
        }

    warnings: list[dict[str, str]] = []
    by_shot: dict[str, list[dict[str, Any]]] = {}
    for line in project["voice_lines"]:
        by_shot.setdefault(line["shot_id"], []).append(line)
    shots: list[dict[str, Any]] = []
    voice_lines: list[dict[str, Any]] = []
    offset = 0
    for sequence in project["sequences"]:
        for scene in sequence["scenes"]:
            if not scene["shots"]:
                warnings.append({"code": "empty_scene", "entity_id": scene["scene_id"]})
            for shot in scene["shots"]:
                end = offset + shot["duration_frames"]
                lines = sorted(
                    by_shot.get(shot["shot_id"], []),
                    key=lambda line: (line["start_frame"], line["voice_line_id"]),
                )
                shots.append(
                    {
                        "shot_id": shot["shot_id"],
                        "scene_id": scene["scene_id"],
                        "sequence_id": sequence["sequence_id"],
                        "title": shot["title"],
                        "description": shot.get("description", ""),
                        **timing(offset, end),
                        "voice_line_ids": [line["voice_line_id"] for line in lines],
                        "events": [
                            {
                                "event_id": event["event_id"],
                                "type": event["type"],
                                "local_frame": event["frame"],
                                "frame": offset + event["frame"],
                            }
                            for event in shot["events"]
                        ],
                    }
                )
                for line in lines:
                    start = offset + line["start_frame"]
                    voice_lines.append(
                        {
                            "voice_line_id": line["voice_line_id"],
                            "shot_id": shot["shot_id"],
                            "character_id": line["character_id"],
                            "text": line["text"],
                            "language": line["language"],
                            "local_start_frame": line["start_frame"],
                            "audio_linked": "audio_asset_id" in line,
                            **timing(start, start + line["duration_frames"]),
                        }
                    )
                    if "audio_asset_id" not in line:
                        warnings.append(
                            {"code": "voice_audio_unlinked", "entity_id": line["voice_line_id"]}
                        )
                offset = end
    # Same-speaker overlaps deserve review; overlaps between speakers can be intentional.
    active: dict[str, dict[str, Any]] = {}
    for line in voice_lines:
        previous = active.get(line["character_id"])
        if previous and line["start_frame"] < previous["end_frame_exclusive"]:
            warnings.append(
                {
                    "code": "same_speaker_overlap",
                    "entity_id": line["voice_line_id"],
                    "related_entity_id": previous["voice_line_id"],
                }
            )
        if previous is None or line["end_frame_exclusive"] > previous["end_frame_exclusive"]:
            active[line["character_id"]] = line
    return {
        "schema_version": "1.0.0",
        "project_id": project["project_id"],
        "project_revision": revision,
        "assembly": "sequential_cuts",
        "fps": deepcopy(fps),
        "audio_sample_rate": canvas["audio_sample_rate"],
        "duration_frames": offset,
        "duration_samples": sample(offset),
        "shots": shots,
        "voice_lines": voice_lines,
        "warnings": warnings,
    }


def plan_story_edit(project: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    """Apply operations to a copy, validate final timing and describe advisory rebuilds."""
    issues = schema_issues("story-edit", request) or validate_project(project)
    if issues:
        raise StoryEditError(issues)
    candidate = deepcopy(project)
    scenes = {
        scene["scene_id"]: scene
        for sequence in candidate["sequences"]
        for scene in sequence["scenes"]
    }
    shots = {shot["shot_id"]: shot for scene in scenes.values() for shot in scene["shots"]}
    lines = {line["voice_line_id"]: line for line in candidate["voice_lines"]}

    def fail(index: int, code: str, message: str) -> None:
        raise StoryEditError([{"path": f"/operations/{index}", "code": code, "message": message}])

    for index, operation in enumerate(request["operations"]):
        op = operation["op"]
        if op == "reorder_shots":
            scene = scenes.get(str(UUID(operation["scene_id"])))
            if scene is None:
                fail(index, "missing_scene", "Scene does not exist.")
            order = [str(UUID(value)) for value in operation["shot_ids"]]
            existing = {shot["shot_id"]: shot for shot in scene["shots"]}
            if len(order) != len(existing) or set(order) != set(existing):
                fail(
                    index, "invalid_shot_order", "Order must contain every shot in this scene once."
                )
            scene["shots"] = [existing[key] for key in order]
        elif op == "set_shot_duration":
            shot = shots.get(str(UUID(operation["shot_id"])))
            if shot is None:
                fail(index, "missing_shot", "Shot does not exist.")
            shot["duration_frames"] = operation["duration_frames"]
        elif op == "set_voice_text":
            line = lines.get(str(UUID(operation["voice_line_id"])))
            if line is None:
                fail(index, "missing_voice_line", "Voice line does not exist.")
            if line["text"] != operation["text"]:
                if "audio_asset_id" in line:
                    if operation.get("audio_policy", "reject") != "detach":
                        fail(
                            index,
                            "linked_audio_requires_detach",
                            "Changing spoken text requires explicit audio_policy=detach.",
                        )
                    del line["audio_asset_id"]
                line["text"] = operation["text"]
    issues = validate_project(candidate)
    if issues:
        raise StoryEditError(issues)

    revision = request["expected_revision"]
    before = editorial_report(project, revision)
    after = editorial_report(candidate, revision)
    before_shots = {shot["shot_id"]: shot for shot in before["shots"]}
    old_shots = {
        shot["shot_id"]: shot
        for sequence in project["sequences"]
        for scene in sequence["scenes"]
        for shot in scene["shots"]
    }
    old_lines = {line["voice_line_id"]: line for line in project["voice_lines"]}
    repositioned = [
        shot["shot_id"]
        for shot in after["shots"]
        if shot["start_frame"] != before_shots[shot["shot_id"]]["start_frame"]
    ]
    resized = [key for key, shot in shots.items() if shot != old_shots[key]]
    edited_lines = [key for key, line in lines.items() if line != old_lines[key]]
    detached = [
        key
        for key in edited_lines
        if "audio_asset_id" in old_lines[key] and "audio_asset_id" not in lines[key]
    ]
    changed = candidate != project
    render_review = sorted(set(resized) | {lines[key]["shot_id"] for key in edited_lines})
    steps = {"animatic", "subtitles", "audio_mix", "video_mux"} if changed else set()
    if edited_lines:
        steps.update({"voice", "alignment", "lip_sync"})
    if render_review:
        steps.add("shot_render")
    return {
        "project": candidate,
        "changed": changed,
        "report": after,
        "impact": {
            "dependency_tracking": "advisory",
            "repositioned_shot_ids": repositioned,
            "resized_shot_ids": resized,
            "edited_voice_line_ids": edited_lines,
            "detached_audio_line_ids": detached,
            "render_review_shot_ids": render_review,
            "rebuild_candidates": sorted(steps),
            "extensions_require_review": changed
            and (
                any(
                    entity.get("extensions")
                    for entity in [
                        project,
                        *candidate["characters"],
                        *candidate["sequences"],
                        *scenes.values(),
                        *shots.values(),
                        *lines.values(),
                    ]
                )
            ),
        },
    }
