"""Check saved pre-sprint evidence, not only freshly computed audit objects."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PLAN_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json"
PLAN = json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_saved_pre_sprint_artifacts_match_manifest_and_current_inputs():
    assert "Historical dirty-branch snapshot" in PLAN["baseline"]["hash_scope"]
    for result in PLAN["pre_sprint_evidence"]["results"]:
        path = ROOT / result["path"]
        assert path.is_file(), result["path"]
        assert _sha256(path) == result["sha256"], result["path"]
        artifact = json.loads(path.read_text(encoding="utf-8"))
        assert artifact["full_core_unlock"] is False
        for evidence in artifact["evidence_artifacts"]:
            source = (ROOT if evidence["path"].startswith("docs/") else ROOT / "docs") / evidence["path"]
            assert source.is_file(), evidence["path"]
            assert _sha256(source) == evidence["sha256"], evidence["path"]
