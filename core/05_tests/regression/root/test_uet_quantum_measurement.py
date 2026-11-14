"""Operational quantum measurement and no-signalling controls."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_quantum_measurement import (
    DensityOperator, MeasurementContext, POVMRecord, QuantumChannel,
    QuantumInstrument, apply_quantum_channel, born_probabilities,
    expectation, partial_trace_bipartite, quantum_measurement_contract,
    sample_or_record_outcome,
)


def _qubit_zero() -> DensityOperator:
    return DensityOperator(np.diag([1.0, 0.0]), "zero")


def _z_instrument() -> QuantumInstrument:
    p0 = np.diag([1.0, 0.0])
    p1 = np.diag([0.0, 1.0])
    return QuantumInstrument(("0", "1"), ((p0,), (p1,)), "z_measurement", "declared_detector_coupling")


def test_density_channel_and_povm_validation() -> None:
    with pytest.raises(ValueError, match="positive-semidefinite"):
        DensityOperator(np.diag([1.1, -0.1]), "bad")
    with pytest.raises(ValueError, match="trace preserving"):
        QuantumChannel((0.5 * np.eye(2),), "bad", "test")
    with pytest.raises(ValueError, match="sum to identity"):
        POVMRecord(("x",), (0.5 * np.eye(2),), "bad")


def test_born_rule_and_conditional_record() -> None:
    state = _qubit_zero()
    instrument = _z_instrument()
    assert born_probabilities(state, instrument.povm()) == {"0": 1.0, "1": 0.0}
    context = MeasurementContext("zero", "identity", "z_measurement", "agent-A", "lab-event-1")
    record = sample_or_record_outcome(state, instrument, context, selected_outcome="0")
    assert record.outcome.probability == 1.0
    assert np.array_equal(record.outcome.conditional_state.matrix, state.matrix)
    assert record.source_state_modified_by_metadata is False


def test_amplitude_damping_channel_is_cptp_and_trace_preserving() -> None:
    gamma = 0.3
    k0 = np.diag([1.0, np.sqrt(1.0 - gamma)])
    k1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]])
    channel = QuantumChannel((k0, k1), "amplitude_damping", "textbook-control")
    excited = DensityOperator(np.diag([0.0, 1.0]), "one")
    output = apply_quantum_channel(excited, channel)
    assert abs(np.trace(output.matrix) - 1.0) <= 1e-12
    assert np.max(np.abs(output.matrix - np.diag([gamma, 1.0 - gamma]))) <= 1e-12


def test_singlet_no_signalling_under_local_trace_preserving_channel() -> None:
    singlet = np.array([0.0, 1.0, -1.0, 0.0]) / np.sqrt(2.0)
    state = DensityOperator(np.outer(singlet, singlet.conj()), "singlet")
    before = partial_trace_bipartite(state, (2, 2), keep=0)
    x = np.array([[0.0, 1.0], [1.0, 0.0]])
    identity = np.eye(2)
    p = 0.37
    local_b = QuantumChannel((np.sqrt(1.0 - p) * np.kron(identity, identity), np.sqrt(p) * np.kron(identity, x)), "random_x_on_B", "textbook-control")
    after = partial_trace_bipartite(apply_quantum_channel(state, local_b), (2, 2), keep=0)
    assert np.max(np.abs(before.matrix - after.matrix)) <= 1e-12


def test_chsh_singlet_reaches_tsirelson_bound() -> None:
    singlet = np.array([0.0, 1.0, -1.0, 0.0]) / np.sqrt(2.0)
    state = DensityOperator(np.outer(singlet, singlet.conj()), "singlet")
    x = np.array([[0.0, 1.0], [1.0, 0.0]])
    z = np.diag([1.0, -1.0])
    b0 = (z + x) / np.sqrt(2.0)
    b1 = (z - x) / np.sqrt(2.0)
    chsh = np.kron(z, b0) + np.kron(z, b1) + np.kron(x, b0) - np.kron(x, b1)
    assert abs(abs(expectation(state, chsh)) - 2.0 * np.sqrt(2.0)) <= 1e-12


def test_contract_is_baseline_not_uet_quantum_derivation() -> None:
    contract = quantum_measurement_contract()
    assert contract["uet_specific_quantum_dynamics"] is False
    assert contract["observer_metadata_changes_source"] is False
    assert contract["legacy_C_equals_abs_psi_sq"] == "REJECTED_AS_DERIVATION"
