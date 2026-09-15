"""Artifact alignment tests for the causal non-closed kernel wave."""

from __future__ import annotations
from docs.core.core_paths import CANONICAL_ARTIFACT_ROOT

import json
from pathlib import Path

from docs.scripts.audit.audit_uet_gr_causal_nonclosed import build_artifacts

ARTIFACT_DIR = CANONICAL_ARTIFACT_ROOT


def _read(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_causal_verification_passes_exact_support_and_dependency_gates() -> None:
    artifact = _read("causal_nonclosed_kernel_verification.json")
    assert artifact["status"] == "PASS"
    assert set(artifact["gates"].values()) == {"PASS"}
    assert artifact["numeric"]["outside_cone_max_abs"] == 0.0
    assert artifact["numeric"]["arrival_speed_relative_error_max"] == 0.0
    assert artifact["numeric"]["future_event_influence_error"] == 0.0
    assert artifact["run_contract"]["spatial_dimension"] == 1
    assert artifact["run_contract"]["curved_green_solver"] is False
    assert artifact["run_contract"]["closed_time_path_derivation"] is False
    assert artifact["run_contract"]["trace_backreaction"] is False


def test_causal_formula_audit_is_present_but_remains_an_ansatz() -> None:
    artifact = _read("causal_influence_formula_audit.json")
    assert artifact["status"] == "WARN"
    assert artifact["implementation_status"] == "PRESENT"
    assert artifact["derivation_status"] == "phenomenological retarded constitutive ansatz"
    assert artifact["unit_lane"] == "natural"
    assert artifact["spatial_dimension"] == 1
    assert "closed_time_path_derivation_missing" in artifact["open_formula_gates"]
    assert "curved_spacetime_green_function_missing" in artifact["open_formula_gates"]


def test_causal_contract_does_not_relabel_trace_or_global_universe() -> None:
    artifact = _read("causal_nonclosed_contract.json")
    assert artifact["source_role"] == "physical_constitutive_influence_j_phi"
    assert artifact["derived_trace_role"] == "separate_observable_no_feedback"
    assert artifact["derived_trace_imported"] is False
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["curved_green_solver"] is False


def test_program_gate_advances_only_the_restricted_constitutive_lane() -> None:
    artifact = _read("uet_gr_research_program_gate.json")
    assert artifact["status"] == "BLOCKED"
    assert artifact["program_stage"] in {
        "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED",
        "CONTROLLED_RESPONSE_REDUCTION_PARTIAL",
        "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED",
        "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED",
        "FIXED_LIGHT_CONE_FEASIBILITY_AND_LOCAL_CURRENT_MAP_VERIFIED",
        "NOETHER_PHASE_FIELD_STATE_COORDINATE_MAP_VERIFIED",
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
    }
    assert artifact["sector_status"]["causal_nonclosed_sector"] == "PASS_CONSTITUTIVE_1P1D"
    assert artifact["sector_status"]["weak_field_reduction"] in {
        "NOT_IMPLEMENTED",
        "PARTIAL_RESPONSE_ONLY",
    }
    assert artifact["controlling_blocker"] in {
        "controlled_covariant_to_matter_space_reduction_missing",
        "covariant_matter_action_and_reciprocal_coupling_missing",
        "regular_covariant_to_diffusive_matter_reduction_missing",
        "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing",
        "noether_density_to_phase_field_order_parameter_map_missing",
        "noether_charge_equation_of_state_and_covariant_transport_matching_missing",
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing",
    }
    if artifact["program_stage"] == "CONTROLLED_RESPONSE_REDUCTION_PARTIAL":
        assert artifact["sector_status"]["covariant_matter_action"] == "NOT_IMPLEMENTED"
    if artifact["program_stage"] == "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED":
        assert artifact["sector_status"]["covariant_matter_action"] == "PASS_O2_SCALAR_PILOT"
    assert artifact["topic_0_19_status_impact"] == "NONE"
    if artifact["program_stage"] == "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED":
        assert artifact["sector_status"]["diffusive_matter_reduction"] == (
            "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT"
        )
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["claim_promotion"] == "BLOCKED"


def test_in_memory_artifacts_match_persisted_status_and_gates() -> None:
    verification, formula, contract, program = build_artifacts()
    assert verification["gates"] == _read("causal_nonclosed_kernel_verification.json")["gates"]
    assert formula["status"] == _read("causal_influence_formula_audit.json")["status"]
    assert contract["status"] == _read("causal_nonclosed_contract.json")["status"]
    assert program["controlling_blocker"] == _read("uet_gr_research_program_gate.json")["controlling_blocker"]
