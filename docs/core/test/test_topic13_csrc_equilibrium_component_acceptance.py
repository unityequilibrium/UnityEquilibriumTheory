from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_csrc_equilibrium_component_acceptance_audit.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_equilibrium_csrc_component_is_closed_without_full_topic13_promotion() -> None:
    artifact = load(ARTIFACT)
    acceptance = artifact["acceptance"]
    uncertainty = artifact["uncertainty"]

    assert artifact["status"] == "PASS_SCOPED_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY"
    assert artifact["major_result"]["major_result_id"] == "T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert acceptance["accepted_as_equilibrium_csrc_component"] is True
    assert acceptance["accepted_as_ding_ttg_source"] is False
    assert acceptance["accepted_for_full_topic13"] is False
    assert acceptance["source_grade_uncertainty_present"] is False
    assert uncertainty["status"] == "QUALIFIED_SENSITIVITY_BOUND_NOT_STANDARD_UNCERTAINTY"
    assert uncertainty["qualified_global_relative_sensitivity_bound"] == 0.044805097064529766
    assert len(artifact["rows"]) == 3
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["target_fit_performed"] is False
    assert artifact["holdout_accessed"] is False


def test_full_gate_exposes_component_lane_but_keeps_ding_source_gate_blocked() -> None:
    gate = load(GATE)
    source = gate["verification_status"]["source_package"]
    lane = source["csrc_equilibrium_component_acceptance"]

    assert lane["major_result_id"] == "T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["acceptance"]["accepted_for_full_topic13"] is False
    assert source["status"] == "BLOCKED"
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in gate["major_result"]["what_remains_open"]
    assert gate["claim_promotion"] is False
