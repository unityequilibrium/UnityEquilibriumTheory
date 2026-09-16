"""Artifact alignment tests for the controlled weak-field reduction."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path

from docs.scripts.audit.audit_uet_gr_weak_field_reduction import build_artifacts

def _read(name: str) -> dict[str, object]:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_reduction_audit_passes_implemented_gates_but_evidence_is_partial() -> None:
    artifact = _read("covariant_matter_space_reduction_verification.json")
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == "PARTIAL"
    assert set(artifact["achieved_gates"].values()) == {"PASS"}
    assert set(artifact["blocked_gates"].values()) == {"BLOCKED"}
    assert artifact["numeric"]["response_acceleration_max_abs_difference"] <= 1e-12
    assert artifact["numeric"]["epsilon_zero_branch_rejected"] is True
    assert artifact["run_contract"]["response_sector_only"] is True
    assert artifact["run_contract"]["full_matter_equation_derived"] is False
    assert artifact["run_contract"]["trace_backreaction"] is False


def test_reduction_contract_names_missing_matter_and_source_derivations() -> None:
    artifact = _read("covariant_reduction_contract.json")
    assert artifact["status"] == "PARTIAL_RESPONSE_SECTOR_EXACT"
    assert artifact["response_equation_mapping"] == "EXACT_ALGEBRAIC"
    assert artifact["matter_equation_mapping"] == (
        "PARTIAL_IN_SEPARATE_CONSTITUTIVE_CURRENT_BRIDGE"
    )
    assert artifact["reciprocal_coupling_derivation"] == (
        "IMPLEMENTED_ACTION_LEVEL_IN_SEPARATE_MATTER_MODULE"
    )
    assert artifact["causal_source_realization"] == "BLOCKED"
    assert "epsilon_nc>0" in artifact["epsilon_policy"]
    assert artifact["topic_0_11_status_impact"] == "NONE"
    assert artifact["topic_0_19_status_impact"] == "NONE"


def test_program_gate_reports_partial_reduction_without_promotion() -> None:
    artifact = _read("uet_gr_research_program_gate.json")
    assert artifact["status"] == "BLOCKED"
    assert artifact["program_stage"] in {
        "CONTROLLED_RESPONSE_REDUCTION_PARTIAL",
        "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED",
        "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED",
        "FIXED_LIGHT_CONE_FEASIBILITY_AND_LOCAL_CURRENT_MAP_VERIFIED",
        "NOETHER_PHASE_FIELD_STATE_COORDINATE_MAP_VERIFIED",
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
    }
    assert artifact["sector_status"]["weak_field_reduction"] == "PARTIAL_RESPONSE_ONLY"
    assert artifact["sector_status"]["covariant_matter_action"] in {
        "NOT_IMPLEMENTED",
        "PASS_O2_SCALAR_PILOT",
    }
    assert artifact["controlling_blocker"] in {
        "covariant_matter_action_and_reciprocal_coupling_missing",
        "regular_covariant_to_diffusive_matter_reduction_missing",
        "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing",
        "noether_density_to_phase_field_order_parameter_map_missing",
        "noether_charge_equation_of_state_and_covariant_transport_matching_missing",
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing",
    }
    assert artifact["topic_0_11_status_impact"] == "NONE"
    assert artifact["topic_0_19_status_impact"] == "NONE"
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["claim_promotion"] == "BLOCKED"


def test_in_memory_partial_artifacts_match_persisted_state() -> None:
    verification, contract, program = build_artifacts()
    assert verification["achieved_gates"] == _read("covariant_matter_space_reduction_verification.json")["achieved_gates"]
    assert contract["status"] == _read("covariant_reduction_contract.json")["status"]
    assert program["controlling_blocker"] == _read("uet_gr_research_program_gate.json")["controlling_blocker"]
