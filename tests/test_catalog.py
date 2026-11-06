import importlib.util
import json
from pathlib import Path

from animeflow_catalog import load_catalog


def test_catalog_is_deduplicated_and_rebuildable():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "build_research_catalog.py"
    spec = importlib.util.spec_from_file_location("catalog_builder", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    catalog = load_catalog()
    assert catalog == module.build()
    ids = [repo["repo_id"].lower() for repo in catalog["repositories"]]
    assert len(ids) == len(set(ids))
    assert {"pnnbao97/vieneu-tts", "zeroweight-ai/zerotts", "vinairesearch/phowhisper"} <= set(ids)
    assert all(repo["integration_status"] == "cataloged" for repo in catalog["repositories"])
    assert (
        json.loads(
            (root / "packages/catalog/src/animeflow_catalog/data/repos.json").read_text(
                encoding="utf-8"
            )
        )
        == catalog
    )
