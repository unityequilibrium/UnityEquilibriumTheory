"""Alignment tests for the fixed-cone and covariant-readiness wave."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from docs.core.core_paths import canonical_existing_path

from docs.core.uet_hyperbolic_phase_field_bridge import (
    HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER,
    HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS,
    fixed_light_cone_feasibility,
    hyperbolic_phase_field_bridge_contract,
    map_external_flux_law_to_current,
)
from docs.scripts.audit.audit_uet_hyperbolic_phase_field_bridge import (
    build_artifacts,
)
from docs.core.uet_noether_phase_field_map import (
    NOETHER_PHASE_FIELD_MAP_CONTROLLER,
)

ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCES = [
    ROOT
    / "docs/data/external/relativistic_transport/jain_kovtun_2024"
    / "source_record.json",
    ROOT
    / "docs/data/external/relativistic_transport/crossley_glorioso_liu_2017"
    / "source_record.json",
]


def _load(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_causal_feasibility_artifact_is_partial_analytic_control() -> None:
    artifact = _load("hyperbolic_phase_field_causal_feasibility.json")
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == "PARTIAL_ANALYTIC_CAUSAL_BRIDGE"
    assert artifact["topic"] == "docs/core UET GR non-closed response"
    assert artifact["version"] == "wave8_v1"
    assert artifact["benchmark_role"] == "analytic_gate"
    assert artifact["method_label"] == "fixed_light_cone_domain_feasibility"
    assert artifact["input_identity"]["source_records"]
    assert artifact["thresholds"]["maximum_dense_speed_residual"] == 1e-12
    assert artifact["thresholds"]["local_current_map_max_abs_residual"] == 1e-12
    assert artifact["run_contract"]["declared_amplitude_domain"] == "abs(C)<=1.25"
    assert artifact["notes"]

    assert set(artifact["achieved_gates"].values()) == {"PASS"}
    assert set(artifact["blocked_gates"].values()) == {"BLOCKED"}
    assert artifact["run_contract"]["parameter_fitting"] is False
    assert artifact["run_contract"]["trace_backreaction"] is False


def test_formula_audit_preserves_external_vs_uet_boundary() -> None:
    artifact = _load("hyperbolic_phase_field_bridge_formula_audit.json")
    assert artifact["status"] == "WARN"
    assert artifact["external_formula_status"] == "SOURCED"
    assert artifact["uet_covariant_derivation_status"] == "BLOCKED"
    assert artifact["topic"] == "docs/core UET GR non-closed response"
    assert artifact["version"] == "wave8_v1"
    assert artifact["benchmark_role"] == "formula_audit"
    assert artifact["method_label"] == "derived_bounds_and_local_current_map"
    assert artifact["source_hashes"]
    assert artifact["notes"]
    registry = {item["id"]: item for item in artifact["formula_registry"]}
    assert registry["external_q_to_current_law_map"]["status"] == (
        "EXACT_LOCAL_MOBILITY_ONE_ONLY"
    )


def test_mapping_gate_has_one_proximal_controller() -> None:
    gate = _load("hyperbolic_phase_field_covariant_mapping_gate.json")
    assert gate["status"] == "BLOCKED"
    assert gate["topic"] == "docs/core UET GR non-closed response"
    assert gate["version"] == "wave8_v1"
    assert gate["benchmark_role"] == "dependency_gate"
    assert gate["method_label"] == "covariant_transport_readiness"
    assert gate["input_identity"]["source_records"]
    assert gate["thresholds"]["required_covariant_state_map_status_for_promotion"] == (
        "PASS"
    )
    assert gate["notes"]
    assert gate["completed_layers"] == {
        "external_formula_transcription": "PASS",
        "fixed_light_cone_normalized_parameter_domain": "PASS",
        "external_q_to_local_current_law": "PASS_MOBILITY_ONE",
        "noether_charge_variable_declaration": "PASS_SIGNED_O2_CHARGE",
        "coarse_density_to_phase_coordinate": "PASS_AFFINE_FIXED_SCALE",
    }
    assert gate["controlling_blocker"] == (
        NOETHER_PHASE_FIELD_MAP_CONTROLLER
    )
    assert gate["classical_covariant_lane"][
        "noether_density_to_phase_field_order_parameter"
    ] == "PASS_HYDRODYNAMIC_AFFINE_ONLY"
    assert gate["classical_covariant_lane"][
        "equation_of_state_from_covariant_O2_action"
    ] == "BLOCKED_CONTROLLING"
    assert gate["thermal_stochastic_lane"]["dynamical_kms_symmetry"] == (
        "BLOCKED_DOWNSTREAM"
    )


def test_relativistic_transport_sources_have_identity_hash_and_locators() -> None:
    for path in SOURCES:
        source = json.loads(path.read_text(encoding="utf-8"))
        assert source["local_path"] is None
        assert source["local_copy_status"] == (
            "TEMPORARY_INSPECTION_ONLY_NOT_REDISTRIBUTED"
        )
        assert len(source["upstream_source_archive_sha256"]) == 64
        assert source["source_archive_size_bytes"] > 0
        assert source["formula_locators"]
        assert source["claim_boundary"]


def test_artifact_source_hashes_match_current_inputs() -> None:
    artifact = _load("hyperbolic_phase_field_causal_feasibility.json")
    for relative, expected in artifact["source_hashes"].items():
        assert _sha(canonical_existing_path(ROOT / relative)) == expected


def test_generator_reproduces_stable_scientific_payload() -> None:
    generated = build_artifacts()
    persisted = (
        _load("hyperbolic_phase_field_causal_feasibility.json"),
        _load("hyperbolic_phase_field_bridge_formula_audit.json"),
        _load("hyperbolic_phase_field_covariant_mapping_gate.json"),
        _load("uet_gr_research_program_gate.json"),
    )
    for live, stored in zip(generated, persisted):
        live = json.loads(json.dumps(live, default=lambda value: value.tolist()))
        live.pop("generated_at")
        stored.pop("generated_at")
        assert live == stored


def test_program_advances_without_topic_or_global_promotion() -> None:
    program = _load("uet_gr_research_program_gate.json")
    assert program["status"] == "BLOCKED"
    assert program["topic"] == "docs/core UET GR non-closed response"
    assert program["version"] == "wave10_v1"
    assert program["benchmark_role"] == "program_gate"
    assert program["method_label"] == "monotonic_gr_research_stage_gate"
    assert program["input_identity"]["eos_verification"].endswith(
        "o2_finite_density_eos_verification.json"
    )
    assert program["notes"]
    assert program["gr_null_model"] == {
        "parameter": "epsilon_nc",
        "value": 0,
        "verification_status": "PASS",
    }
    assert program["program_stage"] == (
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    )
    assert program["controlling_blocker"] == (
        "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
    )
    assert program["sector_status"]["fixed_light_cone_parameter_domain"] == (
        "PASS_NORMALIZED_ANALYTIC"
    )
    assert program["sector_status"]["uniform_subluminal_phase_field_limit"] == (
        "NO_GO_FOR_EXACT_PARABOLIC_LIMIT"
    )
    assert program["sector_status"]["hydrodynamic_state_coordinate_map"] == (
        "PASS_AFFINE_FIXED_SCALE"
)
    assert program["sector_status"]["equation_of_state_from_matter_action"] == (
        "PASS_TREE_LEVEL_T0"
    )
    assert program["global_universe_closure"] == "UNRESOLVED"
    assert program["topic_0_11_status_impact"] == "NONE"
    assert program["topic_0_19_status_impact"] == "NONE"
    assert program["claim_promotion"] == "BLOCKED"


def test_contract_and_public_api_keep_trace_out() -> None:
    contract = hyperbolic_phase_field_bridge_contract()
    assert contract["status"] == HYPERBOLIC_PHASE_FIELD_BRIDGE_STATUS
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
    assert contract["next_controller"] == (
        HYPERBOLIC_PHASE_FIELD_BRIDGE_CONTROLLER
    )
    assert "trace" not in inspect.signature(
        fixed_light_cone_feasibility
    ).parameters
    assert "trace" not in inspect.signature(
        map_external_flux_law_to_current
    ).parameters


def test_gr_null_language_remains_response_null_not_global_closure_claim() -> None:
    gate = _load("hyperbolic_phase_field_covariant_mapping_gate.json")
    assert gate["gr_null_model"] == {
        "parameter": "epsilon_nc",
        "value": 0,
        "verification_status": "PASS_INHERITED_EXACT_GR_RESPONSE_NULL",
    }
    assert gate["global_universe_closure"] == "UNRESOLVED"
