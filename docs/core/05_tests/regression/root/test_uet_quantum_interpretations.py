"""Tests for prediction-invariant quantum interpretation adapters."""

from __future__ import annotations

import numpy as np

from docs.core.uet_quantum_interpretations import (
    compare_empirical_predictions, interpretation_contract, qbist_view,
    relational_view,
)
from docs.core.uet_quantum_measurement import DensityOperator, POVMRecord


def _state_and_povm() -> tuple[DensityOperator, POVMRecord]:
    plus = np.array([1.0, 1.0]) / np.sqrt(2.0)
    state = DensityOperator(np.outer(plus, plus), "plus")
    povm = POVMRecord(("0", "1"), (np.diag([1.0, 0.0]), np.diag([0.0, 1.0])), "z")
    return state, povm


def test_interpretations_share_operational_probabilities_exactly() -> None:
    state, povm = _state_and_povm()
    comparison = compare_empirical_predictions(state, povm)
    assert comparison.maximum_probability_residual <= 1e-12
    assert comparison.empirical_status == "IDENTICAL_OPERATIONAL_PREDICTIONS"
    assert comparison.physical_dynamics_changed is False
    assert comparison.generated_trace_changed is False


def test_metadata_changes_labels_not_predictions_or_source() -> None:
    state, povm = _state_and_povm()
    original = state.matrix.copy()
    a = qbist_view(state, povm, "agent-A")
    b = qbist_view(state, povm, "agent-B")
    r1 = relational_view(state, povm, "S", "R1")
    r2 = relational_view(state, povm, "S", "R2")
    assert a.agent_id != b.agent_id and a.probabilities == b.probabilities
    assert r1.reference_system_id != r2.reference_system_id and r1.probabilities == r2.probabilities
    assert np.array_equal(state.matrix, original)


def test_contract_forbids_hidden_interpretation_dynamics() -> None:
    contract = interpretation_contract()
    assert contract["new_dynamics"] is False
    assert contract["physical_state_inputs"] is False
    assert contract["generated_trace_input"] is False
