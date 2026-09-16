"""Artifact alignment tests for the covariant O(2) matter-action wave."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path

from docs.scripts.audit.audit_uet_gr_covariant_matter import build_artifacts

def _read(name: str) -> dict[str, object]:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_matter_action_audit_passes_implemented_gates_but_stays_partial() -> None:
    artifact = _read("covariant_matter_action_verification.json")
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == "PARTIAL"
    assert set(artifact["achieved_gates"].values()) == {"PASS"}
    assert set(artifact["blocked_gates"].values()) == {"BLOCKED"}
    assert artifact["numeric"]["gr_limit_componentwise_max_abs_residual"] == 0.0
    assert artifact["numeric"]["noether_identity_max_abs_error"] == 0.0
    assert artifact["run_contract"]["diffusive_limit_derived"] is False
    assert artifact["run_contract"]["trace_backreaction"] is False


def test_formula_audit_keeps_diffusive_and_particle_claims_open() -> None:
    artifact = _read("covariant_matter_formula_audit.json")
    assert artifact["status"] == "WARN"
    assert artifact["implementation_status"] == "PRESENT"
    assert "cahn_hilliard_from_covariant_action" in artifact["open_formula_gates"]
    assert "particle_or_antimatter_identity" in artifact["open_formula_gates"]
    assert artifact["epsilon_denominator_lines"] == []


def test_matter_contract_separates_scalar_amplitude_from_density() -> None:
    artifact = _read("covariant_matter_action_contract.json")
    assert artifact["reciprocal_variation"] == "IMPLEMENTED_ACTION_LEVEL"
    assert artifact["matter_current"] == "ON_SHELL_GLOBAL_O2_NOETHER_CURRENT"
    assert artifact["matter_amplitude_role"] == "lorentz_scalar_amplitude_not_yet_density_C"
    assert artifact["diffusive_matter_dynamics"] == "NOT_DERIVED"
    assert artifact["regular_normalized_epsilon_limit"] == "NOT_IMPLEMENTED"
    assert artifact["particle_identity"] == "NOT_ESTABLISHED"
    assert artifact["derived_trace_backreaction"] is False


def test_program_advances_without_topic_or_global_closure_promotion() -> None:
    artifact = _read("uet_gr_research_program_gate.json")
    assert artifact["status"] == "BLOCKED"
    assert artifact["program_stage"] == (
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    )
    assert artifact["sector_status"]["covariant_matter_action"] == "PASS_O2_SCALAR_PILOT"
    assert artifact["sector_status"]["reciprocal_coupling"] == "PASS_ACTION_LEVEL"
    assert artifact["sector_status"]["signed_O2_noether_current"] == "PASS_ON_SHELL"
    assert "matter_number_current" not in artifact["sector_status"]
    assert artifact["sector_status"]["diffusive_matter_reduction"] == (
        "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT"
    )
    assert artifact["sector_status"]["local_convex_matter_causality"] == "PASS_CONTROL"
    assert artifact["sector_status"]["gradient_phase_field_causality"] == "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY"
    assert artifact["controlling_blocker"] == (
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
    )
    assert artifact["topic_0_11_status_impact"] == "NONE"
    assert artifact["topic_0_19_status_impact"] == "NONE"
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["claim_promotion"] == "BLOCKED"


def test_in_memory_matter_artifacts_match_persisted_state() -> None:
    verification, formula, contract, program = build_artifacts()
    assert verification["achieved_gates"] == _read(
        "covariant_matter_action_verification.json"
    )["achieved_gates"]
    assert formula["open_formula_gates"] == _read(
        "covariant_matter_formula_audit.json"
    )["open_formula_gates"]
    assert contract["status"] == _read("covariant_matter_action_contract.json")[
        "status"
    ]
    assert program["controlling_blocker"] == _read(
        "uet_gr_research_program_gate.json"
    )["controlling_blocker"]
