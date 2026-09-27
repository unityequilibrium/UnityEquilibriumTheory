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


def test_compressibility_source_route_has_no_invented_numeric_row():
    record = PLAN["source_route_screen"]
    path = ROOT / record["path"]
    assert _sha256(path) == record["sha256"]
    route = json.loads(path.read_text(encoding="utf-8"))
    assert route["status"] == "PARTIAL_SOURCE_ROUTE_NO_ACCEPTED_NUMERIC_ROW"
    assert route["numeric_response_rows"] == []
    assert record["numeric_response_rows_admitted"] == 0
    assert route["full_core_unlock"] is False
    assert all(not source["numeric_kappa_row_accepted"] for source in route["source_candidates"])
    for evidence in route["evidence_artifacts"]:
        source = ROOT / evidence["path"]
        assert _sha256(source) == evidence["sha256"]
