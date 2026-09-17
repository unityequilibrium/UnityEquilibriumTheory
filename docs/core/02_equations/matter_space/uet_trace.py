"""Causal, history-dependent trace utilities for the opt-in UET trace lane.

The objects in this module deliberately separate three things that were
previously mixed together in the core engine:

* ``C`` is the material/structural state being evolved.
* ``sigma_C`` is a non-negative diagnostic source built from changes in ``C``.
* ``I_trace`` is a retarded functional of source history.  It is not a new
  substance and is not accepted as an independent state in this lane.

The first kernel is a causal finite-support constitutive approximation to a
telegraph-diffusion Green function.  It is useful for controlled experiments,
but remains an open/heuristic mechanism until its continuum derivation and
SI closure are completed.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class TraceKernelConfig:
    """Configuration for ``spacetime_trace_v1``.

    The default lane is normalized.  SI values require an external scale and
    source conversion; the kernel does not silently turn normalized engine
    values into joules, kelvin, or entropy units.
    """

    D_trace: float = 0.1
    tau_trace: float = 0.1
    lambda_trace: float = 0.0
    source_normalization: str = "normalized"
    boundary_condition: str = "periodic"
    c_limit: Optional[float] = None

    def __post_init__(self) -> None:
        if self.D_trace <= 0:
            raise ValueError("D_trace must be positive")
        if self.tau_trace <= 0:
            raise ValueError("tau_trace must be positive")
        if self.lambda_trace < 0:
            raise ValueError("lambda_trace must be non-negative")
        if self.source_normalization not in {"normalized", "si"}:
            raise ValueError("source_normalization must be 'normalized' or 'si'")
        if self.boundary_condition not in {"periodic", "zero"}:
            raise ValueError("boundary_condition must be 'periodic' or 'zero'")
        if self.c_limit is not None and self.c_limit <= 0:
            raise ValueError("c_limit must be positive when provided")
        if self.c_limit is not None and self.v_trace > self.c_limit * (1.0 + 1e-12):
            raise ValueError(
                "sqrt(D_trace/tau_trace) exceeds the configured causal speed limit"
            )

    @property
    def v_trace(self) -> float:
        """Resulting propagation speed in the units of ``dx/dt``."""

        return float(np.sqrt(self.D_trace / self.tau_trace))

    @property
    def operator_equation(self) -> str:
        return (
            "tau_trace*d2_t G + d_t G - D_trace*laplacian G "
            "+ lambda_trace*G = delta(x)delta(t)"
        )


@dataclass
class UETStepResult:
    """Structured result shared by trace and matter-space operator modes.

    The first five fields retain their original positional order. New physical
    space-state fields are optional and appended for backward compatibility.
    """

    C: np.ndarray
    V: Optional[np.ndarray]
    trace_observable: Optional[np.ndarray]
    energy_ledger: Dict[str, Any]
    diagnostics: Dict[str, Any]
    space_response: Optional[np.ndarray] = None
    space_rate: Optional[np.ndarray] = None


def compute_dissipation_source(
    C_previous: np.ndarray,
    C_current: np.ndarray,
    dt: float,
    M0: float = 1.0,
) -> np.ndarray:
    """Return ``sigma_C = |dC/dt|^2 / M0`` in the declared source lane."""

    if dt <= 0:
        raise ValueError("dt must be positive")
    if M0 <= 0:
        raise ValueError("M0 must be positive")
    previous = np.asarray(C_previous, dtype=float)
    current = np.asarray(C_current, dtype=float)
    if previous.shape != current.shape:
        raise ValueError("C_previous and C_current must have the same shape")
    return np.square((current - previous) / dt) / M0


def _shift_array(array: np.ndarray, offset: Tuple[int, ...], boundary: str) -> np.ndarray:
    """Shift an array without wrapping when zero boundary conditions are used."""

    if boundary == "periodic":
        return np.roll(array, shift=offset, axis=tuple(range(array.ndim)))

    shifted = np.zeros_like(array, dtype=float)
    source_slices = []
    target_slices = []
    for size, delta in zip(array.shape, offset):
        if abs(delta) >= size:
            return shifted
        if delta >= 0:
            source_slices.append(slice(0, size - delta))
            target_slices.append(slice(delta, size))
        else:
            source_slices.append(slice(-delta, size))
            target_slices.append(slice(0, size + delta))
    shifted[tuple(target_slices)] = array[tuple(source_slices)]
    return shifted


def _causal_offsets(shape: Tuple[int, ...], radius: float, dx: float) -> Sequence[Tuple[int, ...]]:
    """Enumerate grid offsets inside the retarded propagation cone."""

    max_step = int(np.floor(max(radius, 0.0) / dx + 1e-12))
    ranges = [range(-min(max_step, size - 1), min(max_step, size - 1) + 1) for size in shape]
    offsets = []
    for offset in product(*ranges):
        distance = dx * float(np.sqrt(sum(component * component for component in offset)))
        if distance <= radius + 1e-12:
            offsets.append(tuple(int(component) for component in offset))
    return offsets or [tuple(0 for _ in shape)]


def _spatial_kernel_weights(
    offsets: Sequence[Tuple[int, ...]],
    elapsed: float,
    config: TraceKernelConfig,
    dx: float,
) -> np.ndarray:
    if elapsed <= 0:
        return np.ones(len(offsets), dtype=float)
    variance = max(4.0 * config.D_trace * elapsed, dx * dx)
    distances_sq = np.asarray(
        [dx * dx * sum(component * component for component in offset) for offset in offsets],
        dtype=float,
    )
    weights = np.exp(-distances_sq / variance)
    total = float(np.sum(weights))
    return weights / total if total > 0 else np.full(len(offsets), 1.0 / len(offsets))


def compute_spacetime_trace(
    source_history: Sequence[np.ndarray],
    dx: float,
    dt: float,
    config: TraceKernelConfig,
    shape: Optional[Tuple[int, ...]] = None,
) -> np.ndarray:
    """Evaluate the retarded trace functional from source history.

    ``source_history`` is ordered oldest to newest.  A source sample at lag
    ``t`` contributes only inside ``|x-x'| <= v_trace*t``.  Consequently the
    discrete implementation has no support outside the causal cone, subject
    only to floating-point roundoff.  The temporal envelope is an explicit
    normalized constitutive choice, not a proof of the continuum Green
    function.
    """

    if dx <= 0 or dt <= 0:
        raise ValueError("dx and dt must be positive")
    if not source_history:
        if shape is None:
            raise ValueError("shape is required when source_history is empty")
        return np.zeros(shape, dtype=float)

    samples = [np.asarray(sample, dtype=float) for sample in source_history]
    field_shape = samples[-1].shape
    if shape is not None and tuple(shape) != field_shape:
        raise ValueError("shape does not match source_history")
    if any(sample.shape != field_shape for sample in samples):
        raise ValueError("all source_history samples must have the same shape")

    trace = np.zeros(field_shape, dtype=float)
    for index, source in enumerate(samples):
        lag = len(samples) - 1 - index
        elapsed = lag * dt
        radius = config.v_trace * elapsed
        offsets = _causal_offsets(field_shape, radius, dx)
        weights = _spatial_kernel_weights(offsets, elapsed, config, dx)
        temporal_weight = (dt / config.tau_trace) * np.exp(
            -elapsed / config.tau_trace - config.lambda_trace * elapsed
        )
        for offset, weight in zip(offsets, weights):
            trace += temporal_weight * weight * _shift_array(
                source, offset, config.boundary_condition
            )
    return trace


def markovian_trace(source: np.ndarray) -> np.ndarray:
    """Instantaneous baseline used for the ``tau_trace -> 0`` comparison lane."""

    return np.asarray(source, dtype=float).copy()


def build_trace_energy_ledger(
    source: np.ndarray,
    trace: np.ndarray,
    dx: float,
    config: TraceKernelConfig,
) -> Dict[str, Any]:
    """Report normalized production/storage proxies without calling them energy."""

    source_array = np.asarray(source, dtype=float)
    trace_array = np.asarray(trace, dtype=float)
    if source_array.shape != trace_array.shape:
        raise ValueError("source and trace must have the same shape")
    volume = dx ** max(source_array.ndim, 1)
    production = float(np.sum(source_array) * volume)
    storage = float(np.sum(np.maximum(trace_array, 0.0)) * volume)
    decay = float(config.lambda_trace * storage)
    return {
        "source_production_rate_proxy": production,
        "trace_storage_proxy": storage,
        "trace_decay_rate_proxy": decay,
        "environment_transfer_proxy": decay,
        "units_lane": config.source_normalization,
        "closure_status": "proxy_only_open_SI_accounting",
        "energy_not_lost_statement": (
            "source and trace terms are reported as normalized production/storage "
            "proxies; no Joule conservation claim is made"
        ),
    }


def trace_causal_leakage(
    response: np.ndarray,
    source_location: Tuple[int, ...],
    elapsed: float,
    dx: float,
    config: TraceKernelConfig,
) -> float:
    """Return the maximum response outside the discrete retarded cone."""

    response_array = np.asarray(response, dtype=float)
    if response_array.ndim != len(source_location):
        raise ValueError("source_location dimensionality must match response")
    coordinates = np.indices(response_array.shape)
    distance_sq = np.zeros(response_array.shape, dtype=float)
    for axis, location in enumerate(source_location):
        distance_sq += (coordinates[axis] - location) ** 2
    outside = np.sqrt(distance_sq) * dx > config.v_trace * elapsed + 1e-12
    if not np.any(outside):
        return 0.0
    return float(np.max(np.abs(response_array[outside])))
