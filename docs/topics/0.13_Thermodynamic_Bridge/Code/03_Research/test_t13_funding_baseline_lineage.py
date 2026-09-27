"""Keep clean pre-sprint evidence separate from the unreconciled Core baseline."""

import hashlib
import importlib.util
from pathlib import Path


SOURCE = Path(__file__).with_name("Research_T13_Funding_Baseline_Lineage.py")
SPEC = importlib.util.spec_from_file_location("t13_funding_baseline_lineage", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUDIT = MODULE.audit()


def test_historical_snapshot_is_not_relabelled_clean_reproduction():
    counts = AUDIT["historical_snapshot"]["counts"]
    assert counts == {"MATCH": 0, "DRIFT": 4, "MISSING": 4}
    assert AUDIT["historical_snapshot"]["hashes_are_historical_not_required_to_equal_selected_clean_equivalents"]
    assert AUDIT["pre_sprint_saved_evidence"]["all_match"]
    assert len(AUDIT["pre_sprint_saved_evidence"]["records"]) == 5
    assert AUDIT["source_route_screen"]["current"]
    assert AUDIT["source_route_screen"]["numeric_rows_admitted"] == 0


def test_g0_remains_open_until_full_baseline_and_protocol_are_revalidated():
    assert not AUDIT["clean_core_baseline_revalidated"]
    assert not AUDIT["referenced_j02_protocol"]["present_in_this_checkout"]
    assert not AUDIT["g0_baseline_ready"]
    assert AUDIT["g0_status"] == "BLOCKED_LINEAGE_RECONCILIATION"
    assert "not this identity screen or a planning Boolean" in AUDIT["g0_evaluation_authority"]
    assert AUDIT["full_core_unlock"] is False
    assert AUDIT["dependency_unlocked"] == []


def test_source_hashes_match_and_no_holdout_source_is_opened():
    for item in AUDIT["evidence_artifacts"]:
        source = MODULE.ROOT / item["path"]
        assert source.is_file()
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["sha256"]
    assert all("xie" not in item["path"].lower() for item in AUDIT["evidence_artifacts"])
