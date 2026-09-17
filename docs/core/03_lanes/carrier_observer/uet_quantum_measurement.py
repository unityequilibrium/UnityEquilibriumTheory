"""Operational quantum-measurement spine for UET interfaces.

The module is standard finite-dimensional quantum mechanics.  It separates
preparation, channel, instrument, outcome, and observer record; it introduces
no UET-specific quantum dynamics and does not identify C with |psi|^2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np


QUANTUM_MEASUREMENT_STATUS = "OPERATIONAL_QM_BASELINE_V1"
TOLERANCE = 1e-12


def _square(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=complex)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(result.real)) or not np.all(np.isfinite(result.imag)):
        raise ValueError(f"{name} must be finite")
    return result


def _hermitian_residual(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(matrix - matrix.conj().T)))


@dataclass(frozen=True)
class DensityOperator:
    matrix: np.ndarray
    preparation_id: str

    def __post_init__(self) -> None:
        matrix = _square(self.matrix, "density operator")
        if not self.preparation_id.strip():
            raise ValueError("preparation_id is required")
        if _hermitian_residual(matrix) > TOLERANCE:
            raise ValueError("density operator must be Hermitian")
        trace = np.trace(matrix)
        if abs(trace.imag) > TOLERANCE or abs(trace.real - 1.0) > TOLERANCE:
            raise ValueError("density operator must have trace one")
        if float(np.min(np.linalg.eigvalsh(matrix))) < -TOLERANCE:
            raise ValueError("density operator must be positive-semidefinite")
        object.__setattr__(self, "matrix", matrix)


@dataclass(frozen=True)
class QuantumChannel:
    kraus_operators: tuple[np.ndarray, ...]
    channel_id: str
    provenance: str

    def __post_init__(self) -> None:
        if not self.kraus_operators or not self.channel_id.strip() or not self.provenance.strip():
            raise ValueError("channel requires Kraus operators, id, and provenance")
        operators = tuple(_square(item, "Kraus operator") for item in self.kraus_operators)
        dimension = operators[0].shape[0]
        if any(item.shape != (dimension, dimension) for item in operators):
            raise ValueError("all Kraus operators must have one dimension")
        closure = sum((item.conj().T @ item for item in operators), np.zeros((dimension, dimension), dtype=complex))
        if np.max(np.abs(closure - np.eye(dimension))) > 1e-10:
            raise ValueError("channel Kraus operators must be trace preserving")
        object.__setattr__(self, "kraus_operators", operators)


@dataclass(frozen=True)
class POVMRecord:
    outcomes: tuple[str, ...]
    effects: tuple[np.ndarray, ...]
    instrument_id: str

    def __post_init__(self) -> None:
        if not self.outcomes or len(self.outcomes) != len(self.effects):
            raise ValueError("POVM outcomes and effects must be non-empty and aligned")
        if len(set(self.outcomes)) != len(self.outcomes) or not self.instrument_id.strip():
            raise ValueError("POVM outcomes must be unique and instrument_id declared")
        effects = tuple(_square(item, "POVM effect") for item in self.effects)
        dimension = effects[0].shape[0]
        for effect in effects:
            if effect.shape != (dimension, dimension) or _hermitian_residual(effect) > TOLERANCE:
                raise ValueError("POVM effects must be Hermitian with one dimension")
            if float(np.min(np.linalg.eigvalsh(effect))) < -TOLERANCE:
                raise ValueError("POVM effects must be positive-semidefinite")
        if np.max(np.abs(sum(effects, np.zeros_like(effects[0])) - np.eye(dimension))) > TOLERANCE:
            raise ValueError("POVM effects must sum to identity")
        object.__setattr__(self, "effects", effects)


@dataclass(frozen=True)
class QuantumInstrument:
    outcomes: tuple[str, ...]
    operations: tuple[tuple[np.ndarray, ...], ...]
    instrument_id: str
    detector_interaction_id: str

    def __post_init__(self) -> None:
        if not self.outcomes or len(self.outcomes) != len(self.operations):
            raise ValueError("instrument outcomes and operations must align")
        if len(set(self.outcomes)) != len(self.outcomes):
            raise ValueError("instrument outcomes must be unique")
        if not self.instrument_id.strip() or not self.detector_interaction_id.strip():
            raise ValueError("instrument and detector interaction ids are required")
        normalized = tuple(tuple(_square(item, "instrument Kraus operator") for item in operation) for operation in self.operations)
        if any(not operation for operation in normalized):
            raise ValueError("every outcome needs at least one Kraus operator")
        dimension = normalized[0][0].shape[0]
        if any(item.shape != (dimension, dimension) for operation in normalized for item in operation):
            raise ValueError("instrument operators must share one dimension")
        closure = sum((item.conj().T @ item for operation in normalized for item in operation), np.zeros((dimension, dimension), dtype=complex))
        if np.max(np.abs(closure - np.eye(dimension))) > 1e-10:
            raise ValueError("instrument operations must be trace preserving in total")
        object.__setattr__(self, "operations", normalized)

    def povm(self) -> POVMRecord:
        effects = tuple(sum((item.conj().T @ item for item in operation), np.zeros_like(operation[0])) for operation in self.operations)
        return POVMRecord(self.outcomes, effects, self.instrument_id)


@dataclass(frozen=True)
class MeasurementContext:
    preparation_id: str
    channel_id: str
    instrument_id: str
    observer_id: str
    spacetime_context: str


@dataclass(frozen=True)
class QuantumOutcome:
    outcome: str
    probability: float
    conditional_state: DensityOperator


@dataclass(frozen=True)
class ObserverQuantumRecord:
    context: MeasurementContext
    outcome: QuantumOutcome
    probabilities: Mapping[str, float]
    source_state_modified_by_metadata: bool = False


def born_probabilities(state: DensityOperator, povm: POVMRecord) -> dict[str, float]:
    if state.matrix.shape != povm.effects[0].shape:
        raise ValueError("state and POVM dimensions must match")
    values = np.asarray([np.trace(state.matrix @ effect).real for effect in povm.effects])
    if np.min(values) < -TOLERANCE:
        raise ValueError("Born probability is negative beyond tolerance")
    values = np.where(np.abs(values) <= TOLERANCE, 0.0, values)
    if abs(float(np.sum(values)) - 1.0) > TOLERANCE:
        raise ValueError("Born probabilities are not normalized")
    return {outcome: float(value) for outcome, value in zip(povm.outcomes, values)}


def apply_quantum_channel(state: DensityOperator, channel: QuantumChannel) -> DensityOperator:
    if state.matrix.shape != channel.kraus_operators[0].shape:
        raise ValueError("state and channel dimensions must match")
    matrix = sum((operator @ state.matrix @ operator.conj().T for operator in channel.kraus_operators), np.zeros_like(state.matrix))
    return DensityOperator(matrix, preparation_id=f"{state.preparation_id}|{channel.channel_id}")


def conditional_state_update(state: DensityOperator, instrument: QuantumInstrument, outcome: str) -> QuantumOutcome:
    if outcome not in instrument.outcomes:
        raise ValueError("unknown instrument outcome")
    index = instrument.outcomes.index(outcome)
    operation = instrument.operations[index]
    unnormalized = sum((operator @ state.matrix @ operator.conj().T for operator in operation), np.zeros_like(state.matrix))
    probability = float(np.trace(unnormalized).real)
    if probability <= TOLERANCE:
        raise ValueError("cannot condition on a zero-probability outcome")
    conditional = DensityOperator(unnormalized / probability, f"{state.preparation_id}|conditioned:{outcome}")
    return QuantumOutcome(outcome, probability, conditional)


def sample_or_record_outcome(
    state: DensityOperator, instrument: QuantumInstrument,
    context: MeasurementContext, selected_outcome: str | None = None,
    rng: np.random.Generator | None = None,
) -> ObserverQuantumRecord:
    probabilities = born_probabilities(state, instrument.povm())
    if selected_outcome is None:
        generator = np.random.default_rng() if rng is None else rng
        selected_outcome = str(generator.choice(instrument.outcomes, p=list(probabilities.values())))
    outcome = conditional_state_update(state, instrument, selected_outcome)
    return ObserverQuantumRecord(context, outcome, probabilities)


def partial_trace_bipartite(state: DensityOperator, dimensions: tuple[int, int], keep: int) -> DensityOperator:
    da, db = dimensions
    if state.matrix.shape != (da * db, da * db) or keep not in (0, 1):
        raise ValueError("invalid bipartite dimensions or subsystem")
    tensor = state.matrix.reshape(da, db, da, db)
    reduced = np.trace(tensor, axis1=1, axis2=3) if keep == 0 else np.trace(tensor, axis1=0, axis2=2)
    return DensityOperator(reduced, f"{state.preparation_id}|reduced:{keep}")


def expectation(state: DensityOperator, observable: Any) -> float:
    operator = _square(observable, "observable")
    if operator.shape != state.matrix.shape or _hermitian_residual(operator) > TOLERANCE:
        raise ValueError("observable must be Hermitian and match the state")
    return float(np.trace(state.matrix @ operator).real)


def quantum_measurement_contract() -> dict[str, Any]:
    return {
        "status": QUANTUM_MEASUREMENT_STATUS,
        "baseline": "finite-dimensional operational quantum mechanics",
        "born_rule": "implemented", "cptp_channels": "Kraus closure enforced",
        "povm": "positivity and identity closure enforced",
        "observer_metadata_changes_source": False,
        "uet_specific_quantum_dynamics": False,
        "legacy_C_equals_abs_psi_sq": "REJECTED_AS_DERIVATION",
        "claim_boundary": "standard operational interface; not a derivation of quantum mechanics from UET",
    }


__all__ = ["QUANTUM_MEASUREMENT_STATUS", "DensityOperator", "QuantumChannel", "QuantumInstrument", "POVMRecord", "MeasurementContext", "QuantumOutcome", "ObserverQuantumRecord", "born_probabilities", "apply_quantum_channel", "conditional_state_update", "sample_or_record_outcome", "partial_trace_bipartite", "expectation", "quantum_measurement_contract"]
