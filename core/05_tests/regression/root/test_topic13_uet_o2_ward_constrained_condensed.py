from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_ward_constrained_condensed_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_ward_constrained_condensed_lane_closes_formal_stationarity() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_FORMAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY"
    assert audit["major_result"]["major_result_id"] == "T13_UET_O2_WARD_CONSTRAINED_CONDENSED_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_ward_coefficient_is_derived_and_branch_is_one_sided_stable() -> None:
    audit = load(AUDIT)
    reference = audit["reference"]
    assert abs(reference["ward_boundary_derivative"]) <= 1.0e-10
    assert abs(reference["ward_boundary_low_mode_sq"]) <= 1.0e-10
    assert reference["ward_boundary_high_mode_sq"] > 0.0
    assert reference["near_boundary_derivative"] > 0.0
    assert max(audit["reference"]["reference_counterterm_anchors"]) == 0.0
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_formal_lane_does_not_unlock_full_topic() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_ward_constrained_condensed_lane"
    ]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
