"""Artifact gates for the separate matter-space phase diagnostic."""

from __future__ import annotations

import json
from pathlib import Path


TOPIC = Path(__file__).resolve().parents[2]
ARTIFACT = TOPIC / "Result/artifacts/0_11_matter_space_phase_coupling_diagnostic.json"


def test_phase_pilot_is_internal_and_does_not_promote_topic() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["status"] == "INTERNAL_DIAGNOSTIC"
    assert artifact["verification_status"] == "PASS"
    assert artifact["simulation_status"] == "SIMULATION_ONLY"
    assert artifact["dependency_status"] == "BLOCKED"
    assert artifact["topic_status_impact"] == "NONE"
    assert artifact["controller"] == "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open"


def test_phase_pilot_keeps_trace_and_receiver_boundaries() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["same_complete_state_different_trace_history"]["trace_history_changes_physical_state"] is False
    assert artifact["local_checks"]["receiver_effect_explicit_and_nonzero"] is True
    assert artifact["causal_arrival"]["new_causal_claim"] is False
    assert "no universality, mass, particle, GR, or cosmological claim" in artifact["claim_boundary"]


def test_phase_pilot_has_all_declared_comparators_and_locked_inputs() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = {
        "standard_conserved_gradient_flow",
        "legacy_instantaneous_comparator",
        "C_plus_trace_only",
        "coupled_C_Phi_Pi",
        "coupled_receiver_effect",
        "adiabatic_reduced_model",
    }
    assert set(artifact["comparators"]) == expected
    assert artifact["preregistration"]["parameter_fitting"] is False
    assert artifact["preregistration"]["external_numeric_inputs"] == []
