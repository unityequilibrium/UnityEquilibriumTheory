from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "docs/core/artifacts/uet_major_result_closure_contract.json"
REGISTER_PATH = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
T13_GATE_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_major_result_contract_has_required_fields_and_levels() -> None:
    contract = load(CONTRACT_PATH)
    assert contract["claim_promotion"] is False
    assert "CLOSED_FOR_CORE" in contract["closure_levels"]
    assert "major_result_id" in contract["required_fields"]
    assert "WHAT_IS_ACTUALLY_CLOSED" in contract["required_report_headings"]


def test_register_reports_results_without_counting_pass_as_closure() -> None:
    contract = load(CONTRACT_PATH)
    register = load(REGISTER_PATH)
    required = set(contract["required_fields"])
    allowed = set(contract["closure_levels"])
    assert register["claim_promotion"] is False
    assert register["closure_levels_are_progress_labels_not_readiness_labels"] is True
    for entry in register["entries"]:
        assert required <= set(entry)
        assert entry["closure_level"] in allowed
    o2 = next(entry for entry in register["entries"] if entry["major_result_id"] == "CORE_O2_TREE_LEVEL_EOS_LANE")
    assert o2["verification_status"] == "PASS_TREE_LEVEL_PARTIAL"
    assert o2["closure_level"] == "PARTIAL"


def test_topic13_full_gate_preserves_current_blockers_and_holdout_boundary() -> None:
    gate = load(T13_GATE_PATH)
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["major_result"]["closure_level"] == "PARTIAL"
    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    assert causal["status"] == "PASS"
    assert causal["status_role"] == "full_candidate_or_formal_no_go_gate"
    assert causal["status_basis"] == "FORMAL_NO_GO_AND_NAMED_BRANCH"
    assert causal["lane_status"] == "PASS"
    assert causal["lane_closure_level"] == "CLOSED_FOR_LANE"
    assert gate["verification_status"]["alpha_Phi_K"]["status"] == "BLOCKED"
    assert gate["verification_status"]["holdout_integrity"]["status"] == "PASS"
    assert gate["verification_status"]["holdout_integrity"]["holdout_consumed"] is False
    assert gate["equation_or_mapping"]["dimensional"] == "Delta_Tq = alpha_Phi_K * Delta_Phi"
    assert gate["claim_promotion"] is False


def test_topic13_full_gate_reports_machine_readable_closure_summary() -> None:
    gate = load(T13_GATE_PATH)
    summary = gate["major_result"]["closure_summary"]
    assert summary["open_blocker_count"] == len(gate["major_result"]["what_remains_open"])
    assert summary["closed_lane_count"] >= 1
    assert "alpha_Phi_K_independent_calibration_missing" in summary["open_blocker_groups"]["dimensional_and_calibration"]
    assert summary["downstream_dependency_unlocked"] is False

    register = load(REGISTER_PATH)
    entry = next(item for item in register["entries"] if item["major_result_id"] == "T13_FULL_THERMODYNAMIC_BRIDGE")
    assert entry["closure_summary"]["open_blocker_count"] == summary["open_blocker_count"]
    resolved = next(
        item
        for item in gate["major_result"]["resolved_blockers"]
        if item["blocker"] == "density_uncertainty_not_source_locked"
    )
    assert resolved["status"] == "CLOSED_FOR_LANE"
    assert resolved["resolution_source"]["row_count"] == 3
    assert resolved["resolution_source"]["coverage_factor"] == 2
    assert resolved["what_remains_open"] == [
        "same_state_IG210_isothermal_K_T_missing",
        "C_p_to_C_v_correction_not_closed",
        "material_regime_mapping_to_TTG_not_closed",
    ]
    assert next(
        item
        for item in entry["resolved_blockers"]
        if item["blocker"] == "density_uncertainty_not_source_locked"
    )["status"] == "CLOSED_FOR_LANE"

    resolved_by_blocker = {
        item["blocker"]: item["status"]
        for item in gate["major_result"]["resolved_blockers"]
    }
    assert resolved_by_blocker == {
        "density_uncertainty_not_source_locked": "CLOSED_FOR_LANE",
        "ding_public_numeric_C_src_route": "CLOSED_AS_NO_GO",
        "current_graphite_alpha_V_K_T_inventory": "CLOSED_FOR_LANE",
        "independent_harmonic_c_v_comparator_uncertainty_lane": "CLOSED_FOR_LANE",
        "action_beta_to_normalized_beta_identifiability": "CLOSED_AS_NO_GO",
        "base_phi_to_SI_anchor_identifiability": "CLOSED_AS_NO_GO",
        "normalized_alpha_Phi_K_scale_identifiability": "CLOSED_AS_NO_GO",
        "calorine_model_form_state_uncertainty_lane": "CLOSED_FOR_LANE",
        "calorine_full_lbte_stability_route": "CLOSED_AS_NO_GO",
    }
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in gate[
        "major_result"
    ]["what_remains_open"]
    assert "alpha_Phi_K_independent_calibration_missing" in gate[
        "major_result"
    ]["what_remains_open"]
    assert {
        item["blocker"]: item["status"]
        for item in entry["resolved_blockers"]
    } == resolved_by_blocker
