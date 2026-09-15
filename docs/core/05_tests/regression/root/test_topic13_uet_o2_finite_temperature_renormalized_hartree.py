from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_finite_temperature_renormalized_hartree_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_renormalized_hartree_normal_lane_closes_scoped_functional() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME"
    assert audit["major_result"]["major_result_id"] == "T13_UET_O2_RENORMALIZED_HARTREE_NORMAL_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_normal_lane_keeps_physical_and_si_boundaries_open() -> None:
    audit = load(AUDIT)
    reference = audit["reference"]
    assert reference["gap_residual"] < 1.0e-10
    assert reference["functional_stationarity_residual"] < 1.0e-10
    assert audit["contract"]["units"]["unit_lane"] == "natural"
    assert audit["contract"]["approximation"]["condensate_branch"] == "NOT_INCLUDED"
    assert audit["contract"]["approximation"]["physical_kubo"] == "NOT_INCLUDED"
    assert "alpha_Phi_K_independent_calibration_missing" in audit["major_result"]["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_normal_lane_does_not_unlock_full_topic() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_renormalized_hartree_normal_lane"
    ]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
