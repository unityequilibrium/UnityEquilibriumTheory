from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_normal_response_curvature_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_normal_response_curvature_lane_is_closed_for_lane() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE"
    assert audit["major_result"]["major_result_id"] == "T13_UET_O2_NORMAL_RESPONSE_CURVATURE_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_curvature_lane_does_not_promote_beta_or_si_mapping() -> None:
    audit = load(AUDIT)
    units = audit["major_result"]["units"]
    reference = audit["reference"]
    assert units["unit_lane"] == "natural"
    assert units["beta_T13"].startswith("not identified")
    assert units["alpha_Phi_K"].startswith("not emitted")
    assert reference["physical_beta_t13_identified"] is False
    assert reference["physical_si_mapping_included"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_full_gate_exposes_curvature_lane_without_unlocking_topic() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_normal_response_curvature_lane"
    ]
    assert lane["status"] == "PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
    assert "alpha_Phi_K_independent_calibration_missing" in full["major_result"]["what_remains_open"]
