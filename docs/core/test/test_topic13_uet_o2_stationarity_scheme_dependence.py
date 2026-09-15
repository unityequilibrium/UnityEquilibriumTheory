from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_finite_temperature_stationarity_scheme_dependence_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_stationarity_scheme_boundary_is_closed_as_scoped_no_go() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE"
    assert audit["major_result"]["major_result_id"] == (
        "T13_UET_O2_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_two_schemes_share_anchors_but_differ_in_stationarity() -> None:
    audit = load(AUDIT)
    reference = audit["reference"]
    assert audit["reference_anchors"]["scheme_a"] == [0.0, 0.0, 0.0]
    assert audit["reference_anchors"]["scheme_b"] == [0.0, 0.0, 0.0]
    assert reference["scheme_a_grid_min_derivative"] > 0.0
    assert reference["scheme_b_boundary_derivative"] < 0.0
    assert reference["scheme_b_reference_derivative"] > 0.0
    assert reference["scheme_b_stationary_x"] > audit["reference_parameters"]["x_boundary"]
    assert reference["scheme_b_stationary_x"] < audit["reference_parameters"]["reference_x"]
    assert abs(reference["scheme_b_stationary_residual"]) <= 1.0e-10
    assert reference["scheme_b_min_low_omega_sq"] > 0.0
    assert reference["scheme_b_min_high_omega_sq"] > 0.0


def test_no_go_does_not_unlock_full_topic_or_holdout() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_renormalized_condensate_stationarity_scheme_dependence"
    ]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_AS_NO_GO"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
