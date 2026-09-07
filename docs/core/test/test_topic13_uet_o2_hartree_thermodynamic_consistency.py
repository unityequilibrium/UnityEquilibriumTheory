from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_hartree_thermodynamic_consistency_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_hartree_equilibrium_thermodynamics_lane_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_HARTREE_EQUILIBRIUM_THERMODYNAMICS"
    assert (
        audit["major_result"]["major_result_id"]
        == "T13_UET_O2_HARTREE_EQUILIBRIUM_THERMODYNAMIC_LANE"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_hartree_equilibrium_lane_keeps_physical_boundaries_open() -> None:
    audit = load(AUDIT)
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
    assert "physical_Kubo_coefficient_record_missing" in audit["major_result"][
        "open_blockers"
    ]
    assert "alpha_Phi_K_independent_calibration_missing" in audit["major_result"][
        "open_blockers"
    ]


def test_full_gate_exposes_equilibrium_lane_without_unlocking_topic() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_hartree_equilibrium_thermodynamic_lane"
    ]
    assert lane["status"] == "PASS_ACTION_DERIVED_HARTREE_EQUILIBRIUM_THERMODYNAMICS"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
    component = full["verification_status"]["eos_transport_kms_entropy"][
        "topic13_flat_thermodynamic_bridge_components"
    ]
    assert component["closure_level"] == "CLOSED_FOR_LANE"
    assert "physical_Kubo_coefficient_record_missing" in full["major_result"][
        "what_remains_open"
    ]
