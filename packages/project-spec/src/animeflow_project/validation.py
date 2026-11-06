"""Cross-reference and timing checks for the canonical project contract."""

from pathlib import PurePosixPath, PureWindowsPath
from typing import Any
from uuid import UUID

from animeflow_contracts.validation import schema_issues


def validate_project(project: Any) -> list[dict[str, str]]:
    issues = schema_issues("project", project)
    if issues:
        return issues

    seen: dict[str, str] = {}
    assets: dict[str, dict[str, Any]] = {}
    characters: set[str] = set()
    shots: dict[str, dict[str, Any]] = {}

    def add_issue(path: str, code: str, message: str) -> None:
        issues.append({"path": path, "code": code, "message": message})

    def register(value: str, path: str) -> str:
        key = str(UUID(value))
        if value != key:
            add_issue(path, "noncanonical_id", "IDs must use lowercase canonical UUID format.")
        if key in seen:
            add_issue(path, "duplicate_id", f"ID already used at {seen[key]}.")
        else:
            seen[key] = path
        return key

    register(project["project_id"], "/project_id")
    fps = project["canvas"]["fps"]
    if fps["numerator"] > 240 * fps["denominator"]:
        add_issue("/canvas/fps", "fps_out_of_range", "Frame rate must be at most 240 fps.")

    for i, asset in enumerate(project["assets"]):
        base = f"/assets/{i}"
        key = register(asset["asset_id"], f"{base}/asset_id")
        assets[key] = asset
        if asset["uri"].lower() != f"asset://{key}":
            add_issue(f"{base}/uri", "asset_uri_mismatch", "Asset URI must contain its asset ID.")
        path = asset["path"]
        posix = PurePosixPath(path)
        windows = PureWindowsPath(path)
        if (
            "\\" in path
            or "\x00" in path
            or posix.is_absolute()
            or windows.drive
            or ".." in posix.parts
            or len(posix.parts) < 2
            or posix.parts[0] != "assets"
        ):
            add_issue(f"{base}/path", "unsafe_asset_path", "Asset path must stay inside assets/.")

    for i, character in enumerate(project["characters"]):
        base = f"/characters/{i}"
        characters.add(register(character["character_id"], f"{base}/character_id"))
        for j, asset_id in enumerate(character["asset_ids"]):
            if str(UUID(asset_id)) not in assets:
                add_issue(
                    f"{base}/asset_ids/{j}", "missing_asset", "Character asset does not exist."
                )

    for i, sequence in enumerate(project["sequences"]):
        seq_path = f"/sequences/{i}"
        register(sequence["sequence_id"], f"{seq_path}/sequence_id")
        for j, scene in enumerate(sequence["scenes"]):
            scene_path = f"{seq_path}/scenes/{j}"
            register(scene["scene_id"], f"{scene_path}/scene_id")
            for k, shot in enumerate(scene["shots"]):
                shot_path = f"{scene_path}/shots/{k}"
                key = register(shot["shot_id"], f"{shot_path}/shot_id")
                shots[key] = shot
                for n, event in enumerate(shot["events"]):
                    event_path = f"{shot_path}/events/{n}"
                    register(event["event_id"], f"{event_path}/event_id")
                    if event["frame"] >= shot["duration_frames"]:
                        add_issue(
                            f"{event_path}/frame",
                            "event_out_of_shot",
                            "Event must fall within the shot.",
                        )

    for i, line in enumerate(project["voice_lines"]):
        base = f"/voice_lines/{i}"
        register(line["voice_line_id"], f"{base}/voice_line_id")
        shot = shots.get(str(UUID(line["shot_id"])))
        if shot is None:
            add_issue(f"{base}/shot_id", "missing_shot", "Voice line references an unknown shot.")
        elif line["start_frame"] + line["duration_frames"] > shot["duration_frames"]:
            add_issue(base, "voice_line_out_of_shot", "Voice line must fit within the shot.")
        if str(UUID(line["character_id"])) not in characters:
            add_issue(
                f"{base}/character_id",
                "missing_character",
                "Voice line references an unknown character.",
            )
        if "audio_asset_id" in line:
            asset = assets.get(str(UUID(line["audio_asset_id"])))
            if asset is None or asset["kind"] != "audio":
                add_issue(
                    f"{base}/audio_asset_id",
                    "missing_audio_asset",
                    "Voice line must reference an audio asset.",
                )
    return issues
