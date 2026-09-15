"""Alignment tests for the Noether-charge/phase-field state-map wave."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import inspect
import json
from pathlib import Path

import docs.core as core
from docs.core.uet_noether_phase_field_map import (
    NOETHER_PHASE_FIELD_MAP_CONTROLLER,
    NOETHER_PHASE_FIELD_MAP_STATUS,
    NoetherPhaseFieldMapConfig,
    map_external_comparator_state,
    noether_phase_field_map_contract,
    normalize_noether_hydrodynamic_state,
)
from docs.scripts.audit.audit_uet_noether_phase_field_map import build_artifacts

ROOT = repo_root()
ARTIFACTS = ROOT / "docs/core/artifacts"
SOURCES = [
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions/cahn_hilliard_1958"
    / "source_record.json",
    ROOT
    / "docs/data/external/condensed_matter/phase_transitions/hohenberg_halperin_1977"
    / "source_record.json",
]


def _load(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_state_map_artifact_passes_only_the_hydrodynamic_coordinate_layer() -> None:
    artifact = _load("noether_phase_field_state_map_verification.json")
    assert artifact["audit_status"] == "PASS"
    assert artifact["evidence_status"] == NOETHER_PHASE_FIELD_MAP_STATUS
    assert artifact["claim_class"] == "B"
    assert artifact["version"] == "wave9_v1"
    assert artifact["benchmark_role"] == "analytic_state_map_gate"
    assert artifact["method_label"] == (
        "factorized_noether_to_hydrodynamic_phase_coordinate_map"
    )
    assert artifact["numeric"]["maximum_affine_roundtrip_error"] <= 1e-12
    assert artifact["numeric"]["microscopic_same_current_error"] <= 1e-12
    assert artifact["numeric"]["microscopic_state_difference"] >= 1e-3
    assert artifact["numeric"]["coarse_same_average_error"] <= 1e-12
    assert artifact["numeric"]["coarse_microstate_difference"] >= 1e-3
    assert artifact["numeric"]["trace_and_space_response_absent"] is True
    assert set(artifact["achieved_gates"].values()) == {"PASS"}
    assert artifact["blocked_gates"][
        "equation_of_state_from_covariant_O2_action"
    ] == "BLOCKED_CONTROLLING"
    assert artifact["next_controller"] == NOETHER_PHASE_FIELD_MAP_CONTROLLER


def test_formula_audit_separates_definition_conjugacy_and_derivation() -> None:
    audit = _load("noether_phase_field_map_formula_audit.json")
    assert audit["status"] == "WARN"
    assert audit["unit_lane"] == "natural_to_normalized"
    registry = {item["id"]: item for item in audit["formula_registry"]}
    assert registry["affine_phase_coordinate"]["status"] == (
        "DEFINITION_EXACT_FIXED_SCALES"
    )
    assert registry["continuity_residual_scaling"]["status"] == "DERIVED_EXACT"
    assert registry["symmetric_double_well_conjugacy"]["status"] == (
        "DERIVED_EXACT_CONSTITUTIVE"
    )
    assert registry["normalized_constitutive_scales"]["status"] == (
        "DIMENSIONAL_COORDINATE_MAP_NOT_MICROSCOPIC_DERIVATION"
    )
    assert "equation_of_state_from_covariant_O2_action" in audit[
        "open_formula_gates"
    ]


def test_dependency_gate_rejects_the_microscopic_inverse_category_error() -> None:
    gate = _load("noether_phase_field_dependency_gate.json")
    assert gate["status"] == "BLOCKED"
    assert gate["evidence_status"] == NOETHER_PHASE_FIELD_MAP_STATUS
    assert gate["completed_layers"]["physical_conserved_variable_declaration"] == (
        "PASS_SIGNED_O2_CHARGE"
    )
    assert gate["completed_layers"]["microscopic_inverse_requirement"] == (
        "REJECTED_AS_CATEGORY_ERROR"
    )
    assert gate["controlling_blocker"] == NOETHER_PHASE_FIELD_MAP_CONTROLLER
    assert "do_not_invert_C_to_microscopic_O2_fields" in gate[
        "forbidden_shortcuts"
    ]
    assert "do_not_import_trace_as_state_or_feedback" in gate[
        "forbidden_shortcuts"
    ]
    assert gate["global_universe_closure"] == "UNRESOLVED"
    assert gate["topic_0_11_status_impact"] == "NONE"
    assert gate["topic_0_19_status_impact"] == "NONE"


def test_primary_source_records_keep_narrow_external_roles() -> None:
    expected = {
        "10.1063/1.1744102": (
            "EXTERNAL_PHASE_FIELD_VARIABLE_ROLE_SOURCE_NOT_UET_DERIVATION"
        ),
        "10.1103/RevModPhys.49.435": (
            "EXTERNAL_MODEL_B_CLASSIFICATION_SOURCE_NOT_MICROSCOPIC_UET_MAP"
        ),
    }
    for path in SOURCES:
        source = json.loads(path.read_text(encoding="utf-8"))
        assert source["local_path"] is None
        assert source["benchmark_role"] == expected[source["doi"]]
        assert source["formula_locators"]
        assert source["known_access_limitations"]
        assert source["claim_boundary"]


def test_artifact_source_hashes_match_current_inputs() -> None:
    artifact = _load("noether_phase_field_state_map_verification.json")
    for relative, expected in artifact["source_hashes"].items():
        assert _sha(ROOT / relative) == expected


def test_generator_reproduces_stable_scientific_payload() -> None:
    generated = build_artifacts()
    persisted = (
        _load("noether_phase_field_state_map_verification.json"),
        _load("noether_phase_field_map_formula_audit.json"),
        _load("noether_phase_field_dependency_gate.json"),
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
    assert program["version"] == "wave10_v1"
    assert program["program_stage"] == (
        "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    )
    assert program["controlling_blocker"] == "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
    assert program["sector_status"]["signed_O2_noether_current"] == (
        "PASS_ON_SHELL"
    )
    assert "matter_number_current" not in program["sector_status"]
    assert program["sector_status"]["hydrodynamic_state_coordinate_map"] == (
        "PASS_AFFINE_FIXED_SCALE"
    )
    assert program["sector_status"]["microscopic_state_reconstruction"] == (
        "NO_GO_MANY_TO_ONE"
    )
    assert program["sector_status"]["equation_of_state_from_matter_action"] == (
        "PASS_TREE_LEVEL_T0"
    )
    assert program["gr_null_model"] == {
        "parameter": "epsilon_nc",
        "value": 0,
        "verification_status": "PASS",
    }
    assert program["global_universe_closure"] == "UNRESOLVED"
    assert program["topic_0_11_status_impact"] == "NONE"
    assert program["topic_0_19_status_impact"] == "NONE"
    assert program["claim_promotion"] == "BLOCKED"


def test_contract_and_signatures_keep_phi_and_trace_out() -> None:
    contract = noether_phase_field_map_contract()
    assert contract["status"] == NOETHER_PHASE_FIELD_MAP_STATUS
    assert contract["microscopic_inverse"] == "IMPOSSIBLE_WITHOUT_ADDITIONAL_STATE"
    assert contract["external_auxiliary_phase_to_UET_Phi"] == "FORBIDDEN"
    assert contract["trace_input"] is False
    assert contract["trace_backreaction"] is False
    assert contract["next_controller"] == NOETHER_PHASE_FIELD_MAP_CONTROLLER
    for function in (
        normalize_noether_hydrodynamic_state,
        map_external_comparator_state,
    ):
        parameters = inspect.signature(function).parameters
        assert "trace" not in parameters
        assert "Phi" not in parameters
        assert "space_response" not in parameters


def test_public_api_exports_the_state_map_without_aliasing_legacy_I() -> None:
    config = core.NoetherPhaseFieldMapConfig()
    assert isinstance(config, NoetherPhaseFieldMapConfig)
    assert core.NOETHER_PHASE_FIELD_MAP_STATUS == NOETHER_PHASE_FIELD_MAP_STATUS
    assert core.noether_phase_field_map_contract()["trace_input"] is False
    assert "I" not in inspect.signature(
        core.normalize_noether_hydrodynamic_state
    ).parameters


def test_gr_null_language_remains_response_null_not_universe_closure() -> None:
    gate = _load("noether_phase_field_dependency_gate.json")
    assert gate["gr_null_model"] == {
        "parameter": "epsilon_nc",
        "value": 0,
        "verification_status": "PASS_INHERITED_EXACT_GR_RESPONSE_NULL",
    }
    assert gate["global_universe_closure"] == "UNRESOLVED"
