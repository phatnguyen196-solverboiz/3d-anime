"""Compute a small, deterministic project summary for a validation job."""

from pathlib import Path
from typing import Any

from animeflow_project.timebase import frames_to_samples
from animeflow_project.validation import validate_project


def summarize_project(project: dict[str, Any], data_dir: Path | None = None) -> dict[str, Any]:
    issues = validate_project(project)
    if issues:
        return {"valid": False, "issues": issues}
    if data_dir is not None:
        project_root = (data_dir / "projects" / project["project_id"]).resolve()
        for index, asset in enumerate(project["assets"]):
            path = (project_root / asset["path"]).resolve()
            if not path.is_relative_to(project_root) or not path.is_file():
                issues.append(
                    {
                        "path": f"/assets/{index}/path",
                        "code": "missing_asset_file",
                        "message": "Asset file is missing or outside the project directory.",
                    }
                )
    shots = [
        shot
        for sequence in project["sequences"]
        for scene in sequence["scenes"]
        for shot in scene["shots"]
    ]
    duration_frames = sum(shot["duration_frames"] for shot in shots)
    canvas = project["canvas"]
    return {
        "valid": not issues,
        "issues": issues,
        "sequence_count": len(project["sequences"]),
        "shot_count": len(shots),
        "voice_line_count": len(project["voice_lines"]),
        "duration_frames": duration_frames,
        "duration_samples": frames_to_samples(
            duration_frames,
            canvas["fps"]["numerator"],
            canvas["fps"]["denominator"],
            canvas["audio_sample_rate"],
        ),
    }
