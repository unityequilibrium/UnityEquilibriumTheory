from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ASSESSMENT = ROOT / "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_no_go_is_scoped_to_declared_conserved_c_class() -> None:
    artifact = load(ASSESSMENT)
    assert artifact["status"] == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS"
    assert artifact["checks"]["high_k_group_speed_flag"] is True
    assert artifact["checks"]["asymptotic_coefficient_match"] is True
    assert artifact["checks"]["finite_cone_compatibility"] is False
    assert "all UV regularizations" in artifact["not_claimed"][0]


def test_topic13_gate_keeps_original_baseline_blocked_after_no_go() -> None:
    gate = load(GATE)
    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    assert causal["formal_no_go_recorded"] is True
    assert causal["named_finite_cone_branch_pass"] is True
    assert causal["named_coupled_branch_pass"] is True
    assert causal["full_candidate_pass"] is False
    assert causal["status"] == "PASS"
    assert causal["status_role"] == "full_candidate_or_formal_no_go_gate"
    assert causal["status_basis"] == "FORMAL_NO_GO_AND_NAMED_BRANCH"
    assert causal["baseline_status"] == "BLOCKED"
    assert causal["baseline_controlling_blocker"] == "original_conserved_c_gradient_baseline_blocked"
    assert causal["lane_status"] == "PASS"
    assert causal["lane_status_role"] == "scoped_named_branch_lane"
    assert causal["lane_closure_level"] == "CLOSED_FOR_LANE"
    assert causal["structural_question_closure"] == "CLOSED_AS_NO_GO"
    assert causal["baseline_replaced"] is False
    assert causal["full_core_unlock"] is False
    assert any("original conserved-C" in item for item in gate["major_result"]["baseline_open_items"])
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["controlling_blocker"] == (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )
    assert "original_conserved_c_gradient_baseline_blocked" not in gate["major_result"]["what_remains_open"]
