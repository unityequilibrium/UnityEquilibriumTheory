from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json"


def test_base_phi_reconciliation_is_fail_closed() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_BASE_PHI_RECONCILIATION_OPEN"
    assert artifact["summary"] == {
        "candidate_count": 10,
        "paired_alpha_search_candidate_count": 74,
        "eligible_paired_alpha_record_count": 0,
        "formal_or_structural_lane_count": 7,
        "source_boundary_count": 2,
        "named_phi_e_comparator_count": 1,
        "independent_base_phi_si_record_count": 0,
        "accepted_for_full_topic13_count": 0,
    }
    assert artifact["major_result"]["controlling_blocker"] == (
        "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing"
    )
    assert all(artifact["checks"].values())
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["alpha_Phi_K_fit_used"] is False


def test_phi_e_comparator_is_not_base_phi_calibration() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    candidate = next(
        item for item in artifact["candidates"]
        if item["candidate_id"] == "mp48_named_phi_e_comparator"
    )
    assert candidate["named_phi_e_comparator"] is True
    assert candidate["independent_base_phi_si_record"] is False
    assert candidate["eligible_for_full_topic13"] is False
    assert candidate["numeric_named_alpha_present"] is True
    assert candidate["base_phi_mapping_present"] is False
