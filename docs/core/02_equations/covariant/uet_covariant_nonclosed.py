"""Causal non-closed constitutive kernel for the UET response program.

The first implementation is an exact retarded Green-function evaluator on a
declared 1+1-dimensional local rest-frame slice.  The construction is
coordinate-covariant at a point because the observer time and axial distance
are obtained from a Lorentz metric, a unit timelike frame, and a unit spacelike
axis.  It is not yet a curved-spacetime Green solver or a derivation from a
closed-time-path influence action.

The resulting influence ``j_phi`` is a physical constitutive source and may
enter the scalar response equation through ``epsilon_nc * j_phi``.  It is not
the derived dissipation trace ``R``; this module never imports or feeds back
that trace.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any, Final, Sequence

import numpy as np
from scipy.special import i0, j0

from docs.core.uet_covariant_balance import (
    CovariantExchangeLedger,
    exchange_completed_ledger,
)
from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    validate_lorentz_metric,
)

CAUSAL_NONCLOSED_STATUS: Final[str] = "CANDIDATE_RETARDED_CONSTITUTIVE_KERNEL_1P1D"

NATURAL_UNIT_CAUSAL_DIMENSIONS: Final[dict[str, int]] = {
    "coordinate": -1,
    "tau_memory": -1,
    "diffusivity": -1,
    "decay_rate": 1,
    "propagation_speed": 0,
    "kernel_operator": 1,
}


def _scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _vector(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (4,):
        raise ValueError(f"{name} must have shape (4,), got {result.shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


@dataclass(frozen=True)
class CausalInfluenceConfig:
    """Natural-unit parameters for the retarded 1+1 telegraph kernel."""

    tau_memory: float = 1.0
    diffusivity: float = 1.0
    decay_rate: float = 0.0
    source_coupling: float = 1.0
    kernel_dimension: int = 1
    unit_lane: str = "natural"
    frame_tolerance: float = 1e-10
    cone_tolerance: float = 1e-12

    def __post_init__(self) -> None:
        values = {
            "tau_memory": self.tau_memory,
            "diffusivity": self.diffusivity,
            "decay_rate": self.decay_rate,
            "source_coupling": self.source_coupling,
            "frame_tolerance": self.frame_tolerance,
            "cone_tolerance": self.cone_tolerance,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("causal influence parameters must be finite")
        if self.tau_memory <= 0.0:
            raise ValueError("tau_memory must be positive")
        if self.diffusivity <= 0.0:
            raise ValueError("diffusivity must be positive")
        if self.decay_rate < 0.0:
            raise ValueError("decay_rate must be non-negative")
        if self.frame_tolerance <= 0.0 or self.cone_tolerance <= 0.0:
            raise ValueError("frame and cone tolerances must be positive")
        if self.kernel_dimension != 1:
            raise NotImplementedError("v1 implements only a 1+1-dimensional rest-frame slice")
        if self.unit_lane != "natural":
            raise NotImplementedError("v1 implements only unit_lane='natural'")
        if self.propagation_speed > 1.0 + self.cone_tolerance:
            raise ValueError("retarded influence speed must not exceed c=1")

    @property
    def propagation_speed(self) -> float:
        return sqrt(self.diffusivity / self.tau_memory)

    @property
    def damping_rate(self) -> float:
        return 1.0 / (2.0 * self.tau_memory)

    @property
    def effective_mass_sq(self) -> float:
        return (
            self.decay_rate / self.tau_memory
            - 1.0 / (4.0 * self.tau_memory**2)
        )


@dataclass(frozen=True)
class CausalSourceEvent:
    """A point impulse on the declared 1+1 slice."""

    position: np.ndarray
    amplitude: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "position", _vector(self.position, "event.position").copy())
        object.__setattr__(self, "amplitude", _scalar(self.amplitude, "event.amplitude"))


def validate_rest_frame_slice(
    metric: Any,
    timelike_frame: Any,
    spatial_axis: Any,
    *,
    tolerance: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Validate unit vectors ``u.u=-1``, ``e.e=1``, and ``u.e=0``."""

    g, _ = validate_lorentz_metric(metric, tolerance=tolerance)
    u = _vector(timelike_frame, "timelike_frame")
    axis = _vector(spatial_axis, "spatial_axis")
    u_norm = float(u @ g @ u)
    axis_norm = float(axis @ g @ axis)
    orthogonality = float(u @ g @ axis)
    if abs(u_norm + 1.0) > tolerance:
        raise ValueError("timelike_frame must be future unit timelike with norm -1")
    if u[0] <= 0.0:
        raise ValueError("timelike_frame must be future directed in the declared chart")
    if abs(axis_norm - 1.0) > tolerance:
        raise ValueError("spatial_axis must be unit spacelike with norm +1")
    if abs(orthogonality) > tolerance:
        raise ValueError("timelike_frame and spatial_axis must be orthogonal")
    return g, u, axis


def rest_frame_separation(
    separation: Any,
    metric: Any,
    timelike_frame: Any,
    spatial_axis: Any,
    *,
    tolerance: float = 1e-10,
) -> tuple[float, float, float]:
    """Return observer time, signed axial distance, and transverse residual."""

    delta = _vector(separation, "separation")
    g, u, axis = validate_rest_frame_slice(
        metric, timelike_frame, spatial_axis, tolerance=tolerance
    )
    time = -float(u @ g @ delta)
    distance = float(axis @ g @ delta)
    reconstruction = time * u + distance * axis
    transverse_max_abs = float(np.max(np.abs(delta - reconstruction)))
    if transverse_max_abs > tolerance:
        raise ValueError("separation leaves the declared 1+1-dimensional frame slice")
    return time, distance, transverse_max_abs


def causal_cone_margin(
    observer_time: float,
    axial_distance: float,
    config: CausalInfluenceConfig,
) -> float:
    """Return ``t^2 - x^2/v^2``; non-negative values are inside the cone."""

    time = _scalar(observer_time, "observer_time")
    distance = _scalar(axial_distance, "axial_distance")
    return float(time**2 - (distance / config.propagation_speed) ** 2)


def retarded_telegraph_kernel_1p1(
    observer_time: float,
    axial_distance: float,
    config: CausalInfluenceConfig,
) -> float:
    """Evaluate the exact retarded Green function of the 1+1 telegraph operator.

    The operator is ``tau d_t^2 + d_t - D d_x^2 + lambda``.  The returned
    regular Green function has exact support ``t >= |x|/sqrt(D/tau)``.
    """

    time = _scalar(observer_time, "observer_time")
    distance = _scalar(axial_distance, "axial_distance")
    if time <= 0.0:
        return 0.0
    margin = causal_cone_margin(time, distance, config)
    if margin < -config.cone_tolerance:
        return 0.0
    proper_interval_sq = max(margin, 0.0)
    mass_sq = config.effective_mass_sq
    argument = sqrt(abs(mass_sq) * proper_interval_sq)
    shape = float(j0(argument) if mass_sq >= 0.0 else i0(argument))
    normalization = 1.0 / (
        2.0 * config.tau_memory * config.propagation_speed
    )
    return float(normalization * np.exp(-config.damping_rate * time) * shape)


def covariant_retarded_kernel_value(
    separation: Any,
    metric: Any,
    timelike_frame: Any,
    spatial_axis: Any,
    config: CausalInfluenceConfig,
) -> float:
    """Evaluate the 1+1 kernel from coordinate-covariant local invariants."""

    time, distance, _ = rest_frame_separation(
        separation,
        metric,
        timelike_frame,
        spatial_axis,
        tolerance=config.frame_tolerance,
    )
    return retarded_telegraph_kernel_1p1(time, distance, config)


def retarded_influence_from_events(
    observation: Any,
    events: Sequence[CausalSourceEvent],
    metric: Any,
    timelike_frame: Any,
    spatial_axis: Any,
    config: CausalInfluenceConfig,
) -> float:
    """Convolve point-event history with the retarded constitutive kernel."""

    point = _vector(observation, "observation")
    influence = 0.0
    for event in events:
        influence += event.amplitude * covariant_retarded_kernel_value(
            point - event.position,
            metric,
            timelike_frame,
            spatial_axis,
            config,
        )
    return float(config.source_coupling * influence)


def causal_exchange_from_events(
    observation: Any,
    events: Sequence[CausalSourceEvent],
    metric: Any,
    timelike_frame: Any,
    spatial_axis: Any,
    gradient_phi: Any,
    influence_config: CausalInfluenceConfig,
    response_config: CovariantResponseConfig,
) -> CovariantExchangeLedger:
    """Map causal history to the regular exchange-completed scalar source."""

    reduced_source = retarded_influence_from_events(
        observation,
        events,
        metric,
        timelike_frame,
        spatial_axis,
        influence_config,
    )
    return exchange_completed_ledger(reduced_source, gradient_phi, response_config)


def causal_nonclosed_contract() -> dict[str, Any]:
    """Return the ontology and claim ceiling for the first causal kernel."""

    return {
        "status": CAUSAL_NONCLOSED_STATUS,
        "operator": "tau(u.nabla)^2 + (u.nabla) - D(e.nabla)^2 + lambda",
        "kernel_support": "retarded_1p1_local_rest_frame_cone",
        "characteristic_speed": "sqrt(D/tau) <= 1",
        "source_role": "physical_constitutive_influence_j_phi",
        "source_nesting": "J_phi = epsilon_nc * j_phi",
        "derived_trace_role": "separate_observable_no_feedback",
        "derived_trace_imported": False,
        "history_cache_is_new_ontology": False,
        "global_universe_closure": "UNRESOLVED",
        "curved_green_solver": False,
        "closed_time_path_derivation": False,
        "spatial_dimension": 1,
        "unit_lane": "natural",
        "mass_dimensions": dict(NATURAL_UNIT_CAUSAL_DIMENSIONS),
    }
