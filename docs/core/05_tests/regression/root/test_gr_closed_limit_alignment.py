"""Artifact and source-alignment gates for the UET GR closed-limit wave."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path

from docs.core.uet_covariant_response import (
    COVARIANT_RESPONSE_MODEL_STATUS,
    CovariantResponseConfig,
    model_contract,
)
from docs.scripts.audit.audit_uet_gr_closed_limit import build_artifacts

def _read(name: str) -> dict[str, object]:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_generated_closed_limit_artifact_passes_every_implemented_gate() -> None:
    artifact = _read("gr_closed_limit_verification.json")
    assert artifact["status"] == "PASS"
    assert set(artifact["gates"].values()) == {"PASS"}
    assert artifact["numeric"]["closed_limit_componentwise_exact"] is True
    assert artifact["numeric"]["closed_limit_max_abs_residual"] == 0.0
    assert artifact["run_contract"]["trace_backreaction"] is False
    assert artifact["run_contract"]["metric_pde_solved"] is False
    assert artifact["run_contract"]["bianchi_identity_proved"] is False


def test_formula_audit_is_implemented_but_keeps_open_gates_visible() -> None:
    artifact = _read("covariant_action_formula_audit.json")
    assert artifact["status"] == "WARN"
    assert artifact["implementation_status"] == "PRESENT"
    assert artifact["unit_lane"] == "natural"
    assert artifact["epsilon_denominator_lines"] == []
    assert all(
        entry["status"] == "IMPLEMENTED" for entry in artifact["formula_registry"]
    )
    assert any(
        gate in artifact["open_formula_gates"]
        for gate in ("causal_influence_functional_missing", "closed_time_path_derivation_missing")
    )
    assert "system_specific_SI_contract_missing" in artifact["open_formula_gates"]


def test_program_gate_advances_model_class_without_promoting_gr_topic() -> None:
    artifact = _read("uet_gr_research_program_gate.json")
    assert artifact["status"] == "BLOCKED"
    assert artifact["program_stage"] in {
        "CONSERVATIVE_PARENT_IMPLEMENTED",
        "COVARIANT_CONSERVATIVE_BALANCE_VERIFIED",
        "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED",
        "CONTROLLED_RESPONSE_REDUCTION_PARTIAL",
        "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED",
        "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED",
        "FIXED_LIGHT_CONE_FEASIBILITY_AND_LOCAL_CURRENT_MAP_VERIFIED",
        "NOETHER_PHASE_FIELD_STATE_COORDINATE_MAP_VERIFIED",
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
    }
    assert artifact["gr_null_model"]["verification_status"] == "PASS"
    assert artifact["topic_0_19_status_impact"] == "NONE"
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["claim_promotion"] == "BLOCKED"
    assert artifact["controlling_blocker"] in {
        "covariant_bianchi_exchange_balance_missing",
        "causal_nonclosed_influence_functional_missing",
        "controlled_covariant_to_matter_space_reduction_missing",
        "covariant_matter_action_and_reciprocal_coupling_missing",
        "regular_covariant_to_diffusive_matter_reduction_missing",
        "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing",
        "noether_density_to_phase_field_order_parameter_map_missing",
        "noether_charge_equation_of_state_and_covariant_transport_matching_missing",
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing",
    }


def test_in_memory_verifier_matches_persisted_status_contract() -> None:
    formula, closed, program = build_artifacts()
    assert formula["status"] == _read("covariant_action_formula_audit.json")["status"]
    assert closed["gates"] == _read("gr_closed_limit_verification.json")["gates"]
    assert _read("uet_gr_research_program_gate.json")["gr_null_model"]["verification_status"] == closed["status"]


def test_public_model_contract_is_candidate_only_and_si_is_rejected() -> None:
    assert COVARIANT_RESPONSE_MODEL_STATUS.startswith("CANDIDATE_")
    contract = model_contract()
    assert contract["unit_lane"] == "natural"
    assert contract["derived_trace_imported"] is False
    try:
        CovariantResponseConfig(unit_lane="SI")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("SI lane must remain blocked in the first covariant wave")
