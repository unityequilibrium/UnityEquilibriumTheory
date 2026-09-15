"""Regression tests for the core GR to Topic 0.19 dependency gate."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import importlib.util
import json
from pathlib import Path


ROOT = repo_root()
SCRIPT = (
    ROOT
    / "docs/topics/0.19_Gravity_GR/Code/03_Research"
    / "Research_Core_GR_Program_Dependency_Gate.py"
)
ARTIFACT = (
    ROOT
    / "docs/topics/0.19_Gravity_GR/Result/artifacts"
    / "0_19_core_gr_program_dependency_gate.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("topic_0_19_core_gr_dependency", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _stable(payload: dict) -> dict:
    value = json.loads(json.dumps(payload))
    value.pop("generated_at", None)
    return value


def test_persisted_artifact_matches_current_generator() -> None:
    assert _stable(_module().build_artifact()) == _stable(_artifact())


def test_core_program_is_candidate_and_still_blocked() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["core_program_stage_gate"]
    assert artifact["status"] == "BLOCKED"
    assert artifact["core_program_stage"] == "O2_FINITE_DENSITY_EOS_AND_T0_SUPERFLUID_CONSTITUTIVE_VERIFIED"
    assert gate["status"] == "PASS"
    assert all(gate["checks"].values())


def test_epsilon_zero_is_exact_response_null_not_metric_pde_derivation() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["exact_gr_response_null_gate"]
    assert gate["status"] == "PASS"
    assert gate["checks"]["metric_residual_zero"] is True
    assert gate["checks"]["scalar_residual_zero"] is True
    assert gate["checks"]["metric_pde_not_solved"] is True


def test_local_balance_and_causal_scope_keep_declared_limits() -> None:
    artifact = _artifact()
    balance = artifact["gates"]["local_covariant_balance_gate"]
    causal = artifact["gates"]["causal_constitutive_scope_gate"]
    assert balance["status"] == causal["status"] == "PASS"
    assert balance["checks"]["global_energy_theorem_not_claimed"] is True
    assert balance["checks"]["curved_derivative_solver_absent"] is True
    assert causal["checks"]["one_spatial_dimension"] is True
    assert causal["checks"]["curved_green_solver_absent"] is True


def test_response_reduction_remains_partial() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["partial_response_reduction_gate"]
    assert gate["status"] == "PASS"
    assert gate["checks"]["evidence_is_partial"] is True
    assert gate["checks"]["full_matter_equation_not_derived"] is True
    assert gate["checks"]["full_coupled_reduction_blocked"] is True


def test_noether_map_keeps_eos_transport_and_trace_shortcut_blocked() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["noether_state_map_scope_gate"]
    assert gate["status"] == "PASS"
    assert gate["checks"]["microscopic_inverse_rejected"] is True
    assert gate["checks"]["equation_of_state_blocked"] is True
    assert gate["checks"]["transport_blocked"] is True
    assert gate["checks"]["trace_feedback_forbidden"] is True


def test_topic_constant_checkpoint_and_warn_controller_are_preserved() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["topic_constant_checkpoint_preservation_gate"]
    assert gate["status"] == "PASS"
    assert all(gate["checks"].values())
    assert artifact["topic_primary_status_unchanged"] == "PASS"
    assert artifact["topic_claim_scope_controller_unchanged"] == "WARN"


def test_physical_gr_and_topic_promotion_remain_blocked() -> None:
    artifact = _artifact()
    assert artifact["gates"]["physical_gr_benchmark_gate"]["status"] == "BLOCKED"
    assert artifact["gates"]["covariant_completion_gate"]["status"] == "BLOCKED"
    assert artifact["gates"]["topic_promotion_gate"]["status"] == "BLOCKED"
    assert "light_bending_artifact_missing" in artifact[
        "topic_controlling_blockers_unchanged"
    ]


def test_canonical_topic_status_remains_draft_tier_b() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["canonical_topic_status_gate"]
    assert artifact["topic_status_impact"] == "NONE"
    assert artifact["canonical_topic_status"] == "Draft"
    assert artifact["canonical_topic_tier"] == "B"
    assert gate["status"] == "PASS"
    assert gate["status_before"] == gate["status_after"] == "Draft"
    assert gate["tier_before"] == gate["tier_after"] == "B"


def test_global_universe_closure_remains_unresolved() -> None:
    artifact = _artifact()
    gate = artifact["gates"]["global_universe_closure_gate"]
    assert gate["status"] == "PASS"
    assert artifact["global_universe_closure"] == "UNRESOLVED"
    assert "the universe is proved open or closed" in artifact["blocked_language"]


def test_scientific_input_hashes_are_stable_across_timestamp_only_reruns() -> None:
    module = _module()
    artifact = _artifact()
    for record in artifact["scientific_inputs"]:
        path = ROOT / record["path"]
        assert path.exists()
        assert module.scientific_payload_sha256(path) == record[
            "scientific_payload_sha256"
        ]


def test_claim_language_keeps_core_math_separate_from_validation() -> None:
    artifact = _artifact()
    assert artifact["evidence_status"] == (
        "CORE_CANDIDATE_GR_PARENT_AVAILABLE_TOPIC_PHYSICAL_VALIDATION_OPEN"
    )
    assert "exact implemented GR response-null contract" in artifact[
        "allowed_language"
    ]
    assert "UET validates general relativity" in artifact["blocked_language"]
    assert "core candidate artifacts replace classical GR tests" in artifact[
        "blocked_language"
    ]
