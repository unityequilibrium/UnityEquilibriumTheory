from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_csrc_reconciliation_audit.json"


def test_csrc_reconciliation_is_fail_closed() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_CSRC_RECONCILIATION_OPEN"
    assert artifact["summary"] == {
        "route_count": 8,
        "numeric_csrc_candidate_count": 3,
        "source_grade_uncertainty_count": 0,
        "ding_material_state_match_count": 0,
        "ding_author_payload_count": 0,
        "accepted_independent_reproduction_count": 0,
        "accepted_ding_csrc_count": 0,
        "accepted_for_full_topic13_count": 0,
    }
    assert artifact["major_result"]["controlling_blocker"] == (
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    )
    assert all(artifact["checks"].values())
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False


def test_numeric_candidates_are_not_silently_accepted() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    numeric = [item for item in artifact["candidates"] if item["numeric_csrc_present"]]
    assert len(numeric) == 3
    assert all(item["accepted_for_independent_csrc"] is False for item in numeric)
    assert all(item["ding_material_state_match"] is False for item in numeric)
    assert all(item["source_grade_uncertainty_present"] is False for item in numeric)
