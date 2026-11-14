"""Tests for the bounded composition-reference recovery snapshot."""

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_T13_Nested_Reference_Recovery.py")
SPEC = importlib.util.spec_from_file_location("nested_recovery", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_saved_nested_references_and_claim_boundary():
    saved = json.loads(MODULE.RECORD.read_text(encoding="utf-8"))
    lineage = json.loads(MODULE.LINEAGE.read_text(encoding="utf-8"))
    by_recorded = {row["recorded_path"]: row for row in saved["records"]}
    assert len(by_recorded) == len(saved["records"]) == len(lineage["records"]) == 12
    assert saved["evidence_artifacts"][0]["sha256"] == MODULE.sha256(MODULE.LINEAGE)
    assert saved["counts"]["source_matches_recorded_hash"] == 8
    assert saved["counts"]["source_clean_parsed_json_identical"] == 9
    assert saved["counts"]["source_clean_field_delta"] == 3
    assert all(row["recorded_path_missing_in_both_worktrees"] for row in saved["records"])
    assert all(row["source_status_matches_recorded"] and row["clean_status_matches_recorded"]
               for row in saved["records"])
    assert all(MODULE.sha256(MODULE.ROOT / row["relocated_path"]) == row["clean_relocated_sha256"]
               for row in saved["records"])
    assert not saved["g0_ready"] and not saved["full_core_unlock"]


def test_nested_summary_closure_delta_is_visible():
    saved = json.loads(MODULE.RECORD.read_text(encoding="utf-8"))
    changed = [row for row in saved["records"] if row["source_vs_clean_state"] == "FIELD_DELTA"]
    assert len(changed) == 3
    causal = next(row for row in changed if row["relocated_path"].endswith("t13_causal_named_branch_core_compatibility.json"))
    assert "/major_result/evidence_artifacts/1/summary/closure_level" in causal["field_delta_pointers"]
    assert MODULE._changes({"x": {"status": "PARTIAL"}}, {"x": {"status": "PASS"}}) == ["/x/status"]
