"""Regression tests for the Topic 0.11 Noether dependency boundary."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
import json
from pathlib import Path


ROOT = repo_root()
SCRIPT = (
    ROOT
    / "docs/topics/0.11_Phase_Transitions/Code/03_Research"
    / "Research_Noether_Phase_Field_Dependency_Gate.py"
)
ARTIFACT = (
    ROOT
    / "docs/topics/0.11_Phase_Transitions/Result/artifacts"
    / "0_11_noether_phase_field_dependency_gate.json"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("topic_0_11_noether_dependency", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _stable_payload(payload: dict) -> dict:
    stable = json.loads(json.dumps(payload))
    stable.pop("generated_at", None)
    return stable


def test_persisted_artifact_matches_the_current_generator() -> None:
    module = _load_module()
    assert _stable_payload(module.build_artifact()) == _stable_payload(_load_artifact())


def test_coordinate_layer_passes_without_promoting_topic_C_identity() -> None:
    artifact = _load_artifact()
    gates = artifact["gates"]
    assert artifact["status"] == "BLOCKED"
    assert artifact["evidence_status"] == "CONDITIONAL_HYDRODYNAMIC_COORDINATE_COMPATIBILITY"
    assert gates["core_hydrodynamic_coordinate_gate"]["status"] == "PASS"
    assert gates["topic_C_signed_charge_identity_gate"]["status"] == "BLOCKED"
    assert gates["topic_C_signed_charge_identity_gate"]["mapping_exists"] is True
    assert (
        gates["topic_C_signed_charge_identity_gate"]["mapping_status"]
        == "DECLARED_CANDIDATE_BLOCKED"
    )


def test_microscopic_inverse_remains_a_no_go_boundary() -> None:
    artifact = _load_artifact()
    gate = artifact["gates"]["microscopic_inverse_boundary_gate"]
    assert gate["status"] == "PASS"
    assert all(gate["checks"].values())
    assert "microscopic reconstruction is many-to-one" in artifact["allowed_language"]


def test_constitutive_eos_and_transport_remain_blocked() -> None:
    artifact = _load_artifact()
    gate = artifact["gates"]["equation_of_state_and_transport_gate"]
    assert gate["status"] == "BLOCKED"
    assert gate["checks"]["double_well_is_constitutive"] is True
    assert gate["checks"]["equation_of_state_still_blocked"] is True
    assert gate["checks"]["transport_matching_still_blocked"] is True


def test_trace_and_space_response_are_not_imported_into_the_map() -> None:
    artifact = _load_artifact()
    gate = artifact["gates"]["trace_and_space_separation_gate"]
    assert gate["status"] == "PASS"
    assert all(gate["checks"].values())
    assert "the Noether map validates the matter-space Phi field or trace" in artifact[
        "blocked_language"
    ]


def test_wave55_controller_and_claim_ceiling_are_unchanged() -> None:
    artifact = _load_artifact()
    assert artifact["topic_controlling_blocker_unchanged"] == (
        "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open"
    )
    assert artifact["gates"]["wave55_controller_preservation_gate"]["status"] == "PASS"
    assert artifact["gates"]["topic_promotion_gate"]["status"] == "BLOCKED"
    assert artifact["topic_status_impact"] == "NONE"


def test_canonical_status_is_structured_tier_b_without_promotion() -> None:
    artifact = _load_artifact()
    assert artifact["canonical_topic_status"] == "Structured"
    assert artifact["canonical_topic_tier"] == "B"
    gate = artifact["gates"]["canonical_topic_status_gate"]
    assert gate["status"] == "PASS"
    assert gate["status_before"] == gate["status_after"] == "Structured"
    assert gate["tier_before"] == gate["tier_after"] == "B"


def test_scientific_input_hashes_ignore_only_declared_volatile_metadata() -> None:
    module = _load_module()
    artifact = _load_artifact()
    for record in artifact["scientific_inputs"]:
        path = ROOT / record["path"]
        assert path.exists()
        assert module.scientific_payload_sha256(path) == record[
            "scientific_payload_sha256"
        ]
        assert record["hash_scope"] == (
            "canonical_json_without_generated_at_timestamp_utc_or_environment"
        )


def test_gr_response_null_is_not_global_universe_closure() -> None:
    artifact = _load_artifact()
    gate = artifact["gates"]["global_closure_boundary_gate"]
    assert gate["status"] == "PASS"
    assert gate["global_universe_closure"] == "UNRESOLVED"
    assert gate["gr_null_model"]["value"] == 0
    assert "epsilon_nc=0 proves that the universe is globally closed" in artifact[
        "blocked_language"
    ]
