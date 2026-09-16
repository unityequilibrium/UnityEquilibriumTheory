"""Artifact alignment tests for the covariant balance wave."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path

from docs.scripts.audit.audit_uet_gr_covariant_balance import build_artifacts

def _read(name: str) -> dict[str, object]:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_balance_verification_passes_local_identity_gates() -> None:
    artifact = _read("covariant_bianchi_exchange_verification.json")
    assert artifact["status"] == "PASS"
    assert set(artifact["gates"].values()) == {"PASS"}
    assert artifact["symbolic"]["identity_exact"] is True
    assert artifact["numeric"]["identity_max_abs_difference"] <= 1e-12
    assert artifact["run_contract"]["curved_derivative_solver"] is False
    assert artifact["run_contract"]["causal_kernel"] is False
    assert artifact["run_contract"]["global_energy_theorem"] is False


def test_exchange_contract_separates_matter_number_and_stress_balance() -> None:
    artifact = _read("covariant_exchange_contract.json")
    assert artifact["status"] == "CANDIDATE"
    assert "-epsilon_nc" in artifact["matter_stress_balance"]
    assert "+epsilon_nc" in artifact["response_balance"]
    assert "independent" in artifact["matter_number_balance"]
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["derived_trace_backreaction"] is False


def test_program_gate_advances_controller_without_topic_promotion() -> None:
    artifact = _read("uet_gr_research_program_gate.json")
    assert artifact["status"] == "BLOCKED"
    assert artifact["program_stage"] in {
        "COVARIANT_CONSERVATIVE_BALANCE_VERIFIED",
        "CAUSAL_NONCLOSED_CONSTITUTIVE_KERNEL_VERIFIED",
        "CONTROLLED_RESPONSE_REDUCTION_PARTIAL",
        "COVARIANT_MATTER_ACTION_RECIPROCITY_VERIFIED",
        "EXTERNAL_HYPERBOLIC_PHASE_FIELD_COMPARATOR_FORMULA_VERIFIED",
        "FIXED_LIGHT_CONE_FEASIBILITY_AND_LOCAL_CURRENT_MAP_VERIFIED",
        "NOETHER_PHASE_FIELD_STATE_COORDINATE_MAP_VERIFIED",
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED",
    }
    assert artifact["sector_status"]["covariant_exchange_bianchi_balance"] in {
        "PASS",
        "PASS_CONSERVATIVE_PARENT_ONLY",
    }
    assert artifact["sector_status"]["causal_nonclosed_sector"] in {
        "NOT_IMPLEMENTED",
        "PASS_CONSTITUTIVE_1P1D",
    }
    assert artifact["controlling_blocker"] in {
        "causal_nonclosed_influence_functional_missing",
        "controlled_covariant_to_matter_space_reduction_missing",
        "covariant_matter_action_and_reciprocal_coupling_missing",
        "regular_covariant_to_diffusive_matter_reduction_missing",
        "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing",
        "noether_density_to_phase_field_order_parameter_map_missing",
        "noether_charge_equation_of_state_and_covariant_transport_matching_missing",
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing",
    }
    assert artifact["topic_0_19_status_impact"] == "NONE"
    assert artifact["claim_promotion"] == "BLOCKED"


def test_in_memory_balance_artifacts_match_persisted_gate_state() -> None:
    verification, contract, program = build_artifacts()
    assert verification["gates"] == _read("covariant_bianchi_exchange_verification.json")["gates"]
    assert contract["status"] == _read("covariant_exchange_contract.json")["status"]
    assert program["controlling_blocker"] == _read("uet_gr_research_program_gate.json")["controlling_blocker"]
