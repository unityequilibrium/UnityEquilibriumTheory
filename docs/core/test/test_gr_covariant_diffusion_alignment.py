"""Artifact alignment tests for the conserved-current reduction wave."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path

from docs.scripts.audit.audit_uet_gr_covariant_diffusion import build_artifacts

ROOT = repo_root()
ARTIFACT_DIR = ROOT / "docs/core/artifacts"


def _read(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _sha(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def test_diffusive_current_audit_passes_only_declared_partial_scope() -> None:
    artifact = _read("covariant_diffusive_current_verification.json")
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == "PARTIAL"
    assert set(artifact["achieved_gates"].values()) == {"PASS"}
    assert set(artifact["blocked_gates"].values()) == {"BLOCKED"}
    assert artifact["run_contract"]["local_convex_causal_control"] is True
    assert artifact["run_contract"]["full_gradient_phase_field_causality"] is False
    assert artifact["run_contract"]["trace_backreaction"] is False


def test_discrete_conservation_energy_and_model_b_metrics_pass() -> None:
    numeric = _read("covariant_diffusive_current_verification.json")["numeric"]
    assert max(numeric["mass_conservation_abs_residual"].values()) <= 1e-12
    assert max(numeric["energy_identity_abs_residual"].values()) <= 1e-11
    assert max(numeric["adiabatic_model_b_max_abs_residual"].values()) <= 1e-12
    assert numeric["matter_space_rhs_max_abs_residual"] <= 1e-12
    assert numeric["epsilon_zero_space_response_invariance_max_abs"] == 0.0


def test_causal_claim_is_restricted_to_local_convex_control() -> None:
    numeric = _read("covariant_diffusive_current_verification.json")["numeric"]
    assert numeric["local_principal_symbol"]["status"] == (
        "PASS_LOCAL_CONVEX_MAXWELL_CATTANEO"
    )
    assert numeric["local_cone_control"]["outside_cone_leakage_ratio"] <= 1e-12
    assert numeric["local_cone_control"]["arrival_speed_relative_error"] <= 0.05
    assert numeric["gradient_phase_field_principal_symbol"]["status"] == (
        "BLOCKED_FOURTH_ORDER_UV_CAUSALITY"
    )
    assert numeric["spinodal_principal_symbol"]["status"] == (
        "BLOCKED_NONCONVEX_OR_SPINODAL"
    )


def test_formula_and_contract_keep_microscopic_and_uv_gates_open() -> None:
    formula = _read("covariant_diffusion_formula_audit.json")
    contract = _read("covariant_diffusion_contract.json")
    assert formula["status"] == "WARN"
    assert formula["implementation_status"] == "PRESENT"
    assert formula["epsilon_denominator_lines"] == []
    assert "first_order_hyperbolic_gradient_phase_field" in formula[
        "open_formula_gates"
    ]
    assert "closed_time_path_kms_transport_derivation" in formula[
        "open_formula_gates"
    ]
    assert "not_the_scalar_amplitude" in contract["forbidden_identification"]
    assert contract["full_gradient_phase_field_causality"].startswith("BLOCKED")
    assert contract["derived_trace_backreaction"] is False


def test_artifact_hashes_match_current_sources() -> None:
    artifact = _read("covariant_diffusive_current_verification.json")
    for relative_path, expected_hash in artifact["source_hashes"].items():
        assert _sha(relative_path) == expected_hash


def test_program_advances_without_topic_or_global_closure_promotion() -> None:
    artifact = _read("uet_gr_research_program_gate.json")
    assert artifact["status"] == "BLOCKED"
    assert artifact["program_stage"] == (
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    )
    assert artifact["sector_status"]["diffusive_matter_reduction"] == (
        "PARTIAL_CONSTITUTIVE_WITH_EXACT_MODEL_B_LIMIT"
    )
    assert artifact["sector_status"]["local_convex_matter_causality"] == (
        "PASS_CONTROL"
    )
    assert artifact["sector_status"]["gradient_phase_field_causality"] == (
        "PASS_EXTERNAL_FIXED_PARAMETER_COMPARATOR_ONLY"
    )
    assert artifact["controlling_blocker"] == (
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
    )
    assert artifact["topic_0_11_status_impact"] == "NONE"
    assert artifact["topic_0_19_status_impact"] == "NONE"
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert artifact["claim_promotion"] == "BLOCKED"


def test_in_memory_diffusion_artifacts_match_persisted_state() -> None:
    verification, formula, contract, program = build_artifacts()
    assert verification["achieved_gates"] == _read(
        "covariant_diffusive_current_verification.json"
    )["achieved_gates"]
    assert formula["open_formula_gates"] == _read(
        "covariant_diffusion_formula_audit.json"
    )["open_formula_gates"]
    assert contract["status"] == _read("covariant_diffusion_contract.json")[
        "status"
    ]
    assert program["controlling_blocker"] == _read(
        "uet_gr_research_program_gate.json"
    )["controlling_blocker"]
