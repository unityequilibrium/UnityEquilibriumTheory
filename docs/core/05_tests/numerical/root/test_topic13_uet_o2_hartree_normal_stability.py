from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_hartree_normal_stability_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_hartree_normal_stability_boundary_lane_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_HARTREE_NORMAL_ONE_SIDED_STABILITY_BOUNDARY"
    assert audit["major_result"]["major_result_id"] == "T13_UET_O2_HARTREE_NORMAL_STABILITY_BOUNDARY_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_boundary_does_not_promote_condensed_or_physical_transport() -> None:
    audit = load(AUDIT)
    reference = audit["reference"]
    assert reference["condensed_branch_included"] is False
    assert reference["vacuum_counterterm_included"] is False
    assert "condensed_branch_and_renormalized_finite_temperature_phase_transition_missing" in audit["major_result"]["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["target_curve_used"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False


def test_full_gate_exposes_boundary_without_unlocking_topic() -> None:
    full = load(FULL)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_hartree_normal_stability_boundary_lane"
    ]
    assert lane["status"] == "PASS_ACTION_DERIVED_HARTREE_NORMAL_ONE_SIDED_STABILITY_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
