"""Build a reproducible GitHub repo inventory from the Vietnamese source reports."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    "all-repos-researched-2026-11-06.md",
    "repo-animation-research-additions-2026-11-06.md",
    "research-2d-3d-voiceover-repos-2026-11-06.md",
    "vietnamese-voice-research-2026-11-06.md",
]
SOURCE_DIR = ROOT / "docs" / "research" / "sources"
DESTINATION = ROOT / "packages" / "catalog" / "src" / "animeflow_catalog" / "data" / "repos.json"
URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", re.IGNORECASE)
TABLE_ROW = re.compile(r"^\|\s*\d+\s*\|")
BOLD_BULLET = re.compile(r"^- \*\*([^*]+)\*\*")


def build() -> dict:
    repos: dict[str, dict] = {}
    unresolved: list[dict] = []
    for source in SOURCES:
        section = ""
        in_original_tool_section = False
        for number, line in enumerate(
            (SOURCE_DIR / source).read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            if line.startswith("## "):
                section = line.removeprefix("## ").strip()
                in_original_tool_section = source == SOURCES[0] and section.startswith("H.")
            bold = BOLD_BULLET.match(line)
            is_row = bool(TABLE_ROW.match(line))
            is_plain_tool = in_original_tool_section and line.startswith("- ") and not bold
            if not (bold or is_row or is_plain_tool):
                continue
            match = URL.search(line)
            if not match:
                if bold or is_plain_tool:
                    label = bold.group(1) if bold else line[2:].strip()
                    unresolved.append(
                        {"name": label, "source": source, "line": number, "section": section}
                    )
                continue
            owner, name = match.groups()
            name = re.sub(r"\.git$", "", name.rstrip("."), flags=re.IGNORECASE)
            key = f"{owner}/{name}".lower()
            if key not in repos:
                repos[key] = {
                    "repo_id": f"{owner}/{name}",
                    "url": f"https://github.com/{owner}/{name}",
                    "integration_status": "cataloged",
                    "evidence": [],
                }
            if is_row:
                columns = [part.strip() for part in line.strip().strip("|").split("|")]
                summary = columns[2] if len(columns) > 2 else ""
            else:
                summary = line[2:].strip()
            repos[key]["evidence"].append(
                {"source": source, "line": number, "section": section, "summary": summary}
            )
    return {
        "schema_version": "1.0.0",
        "description": (
            "Dedupe of explicit GitHub repo links in source lists. "
            "Inclusion is not integration or license approval."
        ),
        "sources": SOURCES,
        "repositories": [repos[key] for key in sorted(repos)],
        "unresolved_names": unresolved,
    }


if __name__ == "__main__":
    result = build()
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Cataloged {len(result['repositories'])} repositories; "
        f"{len(result['unresolved_names'])} names need links."
    )
