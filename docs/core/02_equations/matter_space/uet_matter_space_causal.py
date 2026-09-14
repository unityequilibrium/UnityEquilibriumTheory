"""Opt-in causal Phi/Pi discrete-gradient reference lane.

This module narrows the remaining matter-space blocker without changing the
default ``matter_space_coupled_v1`` operator.  During one causal substep ``C``
is frozen, the local Phi potential is advanced with a discrete gradient, and
the spatial gradient term uses the centered finite-volume Laplacian at the
current time level.  The resulting two-level energy identity is exact up to
the root-solver tolerance in the declared normalized reference lane.

It is not yet the full coupled C/Phi operator: the C update and its shared
ledger remain an explicit downstream integration task.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np

from docs.core.uet_matter_space import MatterSpaceConfig, MatterSpaceState
from docs.core.uet_spatial import (
    face_gradient_1d,
    integral_1d,
    laplacian_1d,
    validate_dx,
    validate_field_1d,
)


CAUSAL_DISCRETE_GRADIENT_OPERATOR_MODE = "causal_space_discrete_gradient_v1"
ROOT_TOLERANCE = 1.0e-13
ROOT_INTERVAL_TOLERANCE = 1.0e-15
ROOT_MAX_ITERATIONS = 160


def _space_local_potential(
    phi: np.ndarray,
    C: np.ndarray,
    config: MatterSpaceConfig,
) -> np.ndarray:
    return (
        0.5 * config.a_space * phi**2
        + 0.25 * config.b_space * phi**4
        - 0.5 * config.coupling_g * C**2 * phi
    )


def causal_space_discrete_energy(
    current_phi: np.ndarray,
    previous_phi: np.ndarray,
    C: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
) -> float:
    """Return the two-level Phi energy for fixed ``C``.

    The local potential is time-averaged while the spatial term is a
    cross-time finite-volume gradient product.  This is the energy paired
    with the centered recurrence, not a claim that the ordinary continuum
    energy is identical at every finite step.
    """

    spacing = validate_dx(dx)
    current = validate_field_1d(current_phi, "current_phi")
    previous = validate_field_1d(previous_phi, "previous_phi")
    matter = validate_field_1d(C, "C")
    if current.shape != previous.shape or current.shape != matter.shape:
        raise ValueError("current_phi, previous_phi, and C must share one shape")
    step = float(dt)
    if not np.isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")

    velocity = (current - previous) / step
    kinetic = config.tau_space / (2.0 * config.mobility_space)
    current_gradient = face_gradient_1d(current, spacing, config.boundary_condition)
    previous_gradient = face_gradient_1d(previous, spacing, config.boundary_condition)
    gradient = config.kappa_space / 2.0
    local = 0.5 * (
        _space_local_potential(current, matter, config)
        + _space_local_potential(previous, matter, config)
    )
    return float(
        kinetic * integral_1d(velocity**2, spacing)
        + gradient * float(np.sum(current_gradient * previous_gradient) * spacing)
        + integral_1d(local, spacing)
    )


def _local_discrete_gradient(
    next_phi: float,
    previous_phi: float,
    C: float,
    config: MatterSpaceConfig,
) -> float:
    """Return the exact local discrete gradient of the Phi potential."""

    quartic_difference = (
        (next_phi + previous_phi)
        * (next_phi**2 + previous_phi**2)
        / 4.0
    )
    return float(
        0.5 * config.a_space * (next_phi + previous_phi)
        + config.b_space * quartic_difference
        - 0.5 * config.coupling_g * C**2
    )


def _advance_local_root(
    current_phi: float,
    previous_phi: float,
    C: float,
    spatial_force: float,
    source: float,
    dt: float,
    config: MatterSpaceConfig,
) -> Tuple[float, int, float]:
    """Solve the monotone local discrete-gradient equation by bisection."""

    tau = config.tau_space
    mobility = config.mobility_space
    half_dt = 2.0 * dt

    def residual(next_phi: float) -> float:
        inertial = tau / (dt**2) * (next_phi - 2.0 * current_phi + previous_phi)
        damping = (next_phi - previous_phi) / half_dt
        return float(
            inertial
            + damping
            + mobility
            * (_local_discrete_gradient(next_phi, previous_phi, C, config) + spatial_force)
            - source
        )

    guess = 2.0 * current_phi - previous_phi
    span = max(1.0, abs(guess), abs(current_phi), abs(previous_phi), abs(C))
    lower = guess - span
    upper = guess + span
    f_lower = residual(lower)
    f_upper = residual(upper)
    for _ in range(ROOT_MAX_ITERATIONS):
        if f_lower <= 0.0 and f_upper >= 0.0:
            break
        span *= 2.0
        lower = guess - span
        upper = guess + span
        f_lower = residual(lower)
        f_upper = residual(upper)
    else:
        raise RuntimeError("failed to bracket monotone causal Phi root")

    midpoint = 0.5 * (lower + upper)
    for iteration in range(1, ROOT_MAX_ITERATIONS + 1):
        midpoint = 0.5 * (lower + upper)
        value = residual(midpoint)
        if abs(value) <= ROOT_TOLERANCE or abs(upper - lower) <= ROOT_INTERVAL_TOLERANCE:
            return float(midpoint), iteration, abs(value)
        if value < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    value = residual(midpoint)
    return float(midpoint), ROOT_MAX_ITERATIONS, abs(value)


def causal_space_discrete_gradient_step(
    state: MatterSpaceState,
    previous_space_response: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
    space_source: Optional[np.ndarray] = None,
) -> Tuple[MatterSpaceState, np.ndarray, Dict[str, Any]]:
    """Advance the causal Phi/Pi substep while holding ``C`` fixed.

    The strict CFL condition is required so the explicit spatial stencil has
    a one-cell discrete domain of dependence.  ``space_source`` is an
    explicit input and its work is returned in the normalized ledger.
    """

    step = float(dt)
    spacing = validate_dx(dx)
    if not np.isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")
    previous = validate_field_1d(previous_space_response, "previous_space_response")
    if previous.shape != state.space_response.shape:
        raise ValueError("previous_space_response must match state.space_response")
    source = (
        np.zeros_like(state.C)
        if space_source is None
        else validate_field_1d(space_source, "space_source")
    )
    if source.shape != state.C.shape:
        raise ValueError("space_source must match the physical state shape")

    cfl = config.space_speed * step / spacing
    if not np.isclose(cfl, 1.0, rtol=1.0e-10, atol=1.0e-12):
        raise ValueError(
            "causal_space_discrete_gradient_step requires CFL=1; "
            f"received CFL={cfl:.12g}, recommended_dt={spacing / config.space_speed:.12g}"
        )

    current = state.space_response
    spatial_force = -config.kappa_space * laplacian_1d(
        current, spacing, config.boundary_condition
    )
    next_phi = np.empty_like(current)
    root_iterations = 0
    max_root_residual = 0.0
    for index in range(current.size):
        next_phi[index], iterations, root_residual = _advance_local_root(
            current[index],
            previous[index],
            state.C[index],
            spatial_force[index],
            source[index],
            step,
            config,
        )
        root_iterations = max(root_iterations, iterations)
        max_root_residual = max(max_root_residual, root_residual)

    next_pi = (next_phi - previous) / (2.0 * step)
    updated = MatterSpaceState(state.C.copy(), next_phi, next_pi)
    source_work = integral_1d(
        source * (next_phi - previous) / (2.0 * config.mobility_space), spacing
    )
    ledger = {
        "cfl": float(cfl),
        "source_work": float(source_work),
        "root_iterations_max": int(root_iterations),
        "max_root_residual": float(max_root_residual),
        "state_feedback": "C_frozen_during_causal_substep",
        "trace_feedback": False,
        "unit_lane": config.unit_lane,
    }
    return updated, current.copy(), ledger


__all__ = [
    "CAUSAL_DISCRETE_GRADIENT_OPERATOR_MODE",
    "causal_space_discrete_energy",
    "causal_space_discrete_gradient_step",
]
