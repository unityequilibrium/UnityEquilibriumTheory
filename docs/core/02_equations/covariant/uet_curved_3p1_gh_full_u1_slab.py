"""Frozen-background one-dimensional GH slab with Rinne U1 boundary RHSs.

This module evolves all ten symmetric spacetime components on a flat,
zero-shift, normal-incidence slab. It is not a variable-coefficient or
nonlinear GH initial-boundary value solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np

from .uet_curved_3p1_gh_boundary_projectors import (
    SYMMETRIC_PAIRS,
    build_gh_boundary_projectors,
)


_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


@dataclass(frozen=True)
class GHSlabState:
    metric: np.ndarray
    normal_derivative: np.ndarray
    normal_spatial_derivative: np.ndarray


def pack_symmetric(tensor: Any) -> np.ndarray:
    value = np.asarray(tensor, dtype=float)
    if value.shape != (4, 4) or not np.all(np.isfinite(value)):
        raise ValueError("tensor must be a finite 4x4 array")
    if not np.allclose(value, value.T, atol=1e-12, rtol=0.0):
        raise ValueError("tensor must be symmetric")
    return np.asarray([value[i, j] for i, j in SYMMETRIC_PAIRS])


def unpack_symmetric(coordinates: Any) -> np.ndarray:
    values = np.asarray(coordinates, dtype=float)
    if values.shape != (len(SYMMETRIC_PAIRS),) or not np.all(np.isfinite(values)):
        raise ValueError("coordinates must be a finite ten-vector")
    tensor = np.zeros((4, 4), dtype=float)
    for value, (i, j) in zip(values, SYMMETRIC_PAIRS):
        tensor[i, j] = value
        tensor[j, i] = value
    return tensor


def validate_state(state: GHSlabState, node_count: int) -> None:
    expected = (node_count, len(SYMMETRIC_PAIRS))
    for name, value in (
        ("metric", state.metric),
        ("normal_derivative", state.normal_derivative),
        ("normal_spatial_derivative", state.normal_spatial_derivative),
    ):
        array = np.asarray(value, dtype=float)
        if array.shape != expected or not np.all(np.isfinite(array)):
            raise ValueError(f"{name} must be finite with shape {expected}")


def characteristic_u1_minus(
    state: GHSlabState, face_index: int, normal: int, gamma2: float
) -> np.ndarray:
    """Return Pi - Phi_n - gamma2*delta_psi at one slab face."""

    return (
        state.normal_derivative[face_index]
        - normal * state.normal_spatial_derivative[face_index]
        - gamma2 * state.metric[face_index]
    )


def full_u1_boundary_target(
    state: GHSlabState,
    metric_gradient: np.ndarray,
    *,
    face_index: int,
    normal: int,
    gamma2: float,
    gauge_data_rate: np.ndarray,
) -> np.ndarray:
    """Build the incoming characteristic RHS from the 4+2+4 Rinne split.

    In the one-dimensional zero-shift branch, all tangential derivative terms
    vanish. Constraint data are homogeneous, incoming Weyl data are zero, and
    gauge data are supplied through the time derivative of P_G u1_minus.
    """

    if normal not in (-1, 1):
        raise ValueError("normal must be -1 or +1 for the one-dimensional slab")
    if not isfinite(float(gamma2)) or gamma2 <= 0.0:
        raise ValueError("gamma2 must be finite and positive")
    node_count = state.metric.shape[0]
    validate_state(state, node_count)
    d_metric = np.asarray(metric_gradient, dtype=float)
    expected = (node_count, len(SYMMETRIC_PAIRS))
    if d_metric.shape != expected or not np.all(np.isfinite(d_metric)):
        raise ValueError(f"metric_gradient must be finite with shape {expected}")
    if not isinstance(face_index, (int, np.integer)) or not 0 <= face_index < node_count:
        raise ValueError("face_index must identify a node in the slab")

    projectors = build_gh_boundary_projectors((float(normal), 0.0, 0.0))
    pc = projectors.constraint
    pp = projectors.physical
    pg = projectors.gauge
    gauge_rate = np.asarray(gauge_data_rate, dtype=float)
    if gauge_rate.shape != (len(SYMMETRIC_PAIRS),) or not np.all(np.isfinite(gauge_rate)):
        raise ValueError("gauge_data_rate must be a finite ten-vector")
    gauge_projection_error = np.max(np.abs(pg @ gauge_rate - gauge_rate))
    if gauge_projection_error > 1.0e-10:
        raise ValueError("gauge_data_rate must lie in the gauge-projector subspace")

    pi = state.normal_derivative[face_index]
    phi_n = normal * state.normal_spatial_derivative[face_index]
    normal_source = gamma2 * (pi + phi_n)
    d_n_metric = normal * d_metric[face_index]

    # q_t = d_n q + gamma2*(Pi + Phi_n) for this frozen linear system.
    # Rinne's homogeneous conditions set P_C d_n q=0 and
    # P_P[d_n q + gamma2*d_n psi]=0; P_G q=h_G is differentiated in time.
    return (
        pc @ normal_source
        + pp @ (normal_source - gamma2 * d_n_metric)
        + pg @ gauge_rate
    )


def constraint_compatible_u1_lift(
    nodes: Any,
    derivative: Any,
    correction_left: Any,
    correction_right: Any,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Lift endpoint incoming-RHS corrections while preserving D(psi)-Phi.

    Cubic Hermite lifts vanish in psi at both endpoints, have unit outward-
    coordinate derivative at their associated endpoint, and zero derivative
    at the opposite endpoint. The Pi lift changes only the incoming u1-minus
    RHS at each endpoint; Phi's lift is defined as D(psi)'s lift.
    """

    x = np.asarray(nodes, dtype=float)
    d_matrix = np.asarray(derivative, dtype=float)
    left = np.asarray(correction_left, dtype=float)
    right = np.asarray(correction_right, dtype=float)
    if x.ndim != 1 or x.size < 4 or not np.all(np.isfinite(x)):
        raise ValueError("nodes must be a finite one-dimensional grid with >=4 nodes")
    if d_matrix.shape != (x.size, x.size) or not np.all(np.isfinite(d_matrix)):
        raise ValueError("derivative must be a finite square matrix matching nodes")
    if not np.all(np.diff(x) > 0.0) or not np.allclose(
        (x[0], x[-1]), (-1.0, 1.0), atol=1.0e-12, rtol=0.0
    ):
        raise ValueError("nodes must increase strictly from -1 to +1")
    expected = (len(SYMMETRIC_PAIRS),)
    if (
        left.shape != expected
        or right.shape != expected
        or not np.all(np.isfinite(left))
        or not np.all(np.isfinite(right))
    ):
        raise ValueError("endpoint corrections must be finite ten-vectors")

    left_metric_lift = (x - 1.0) ** 2 * (x + 1.0) / 4.0
    right_metric_lift = (x + 1.0) ** 2 * (x - 1.0) / 4.0
    left_value_lift = (1.0 - x) / 2.0
    right_value_lift = (1.0 + x) / 2.0
    metric_rhs_lift = (
        0.5 * left_metric_lift[:, None] * left[None, :]
        - 0.5 * right_metric_lift[:, None] * right[None, :]
    )
    pi_rhs_lift = (
        0.5 * left_value_lift[:, None] * left[None, :]
        + 0.5 * right_value_lift[:, None] * right[None, :]
    )
    phi_rhs_lift = d_matrix @ metric_rhs_lift
    return metric_rhs_lift, pi_rhs_lift, phi_rhs_lift


def gh_full_u1_slab_rhs(
    state: GHSlabState,
    derivative: np.ndarray,
    gamma2: float,
    gauge_data_rate: Any | None = None,
    *,
    nodes: Any,
    boundary_method: str = "rinne_pointwise",
) -> GHSlabState:
    """Evaluate the linear GH RHS with a declared incoming-u1 treatment.

    ``rinne_pointwise`` replaces endpoint characteristic RHSs as in Rinne's
    spectral prescription. ``constraint_compatible_lift`` is an experimental
    cubic lift that preserves the discrete reduction constraint but is not
    assumed stable. ``reduced_wave_algebraic_phi`` evolves only on the
    algebraic subspace Phi_x=D(psi), as a separate second-order comparator.
    No mode applies filtering or clipping.
    """

    d_matrix = np.asarray(derivative, dtype=float)
    if d_matrix.ndim != 2 or d_matrix.shape[0] != d_matrix.shape[1]:
        raise ValueError("derivative must be a square matrix")
    grid = np.asarray(nodes, dtype=float)
    if grid.shape != (d_matrix.shape[0],) or not np.all(np.isfinite(grid)):
        raise ValueError("nodes must be a finite vector matching derivative")
    if not isfinite(float(gamma2)) or gamma2 <= 0.0:
        raise ValueError("gamma2 must be finite and positive")
    if boundary_method not in (
        "rinne_pointwise",
        "constraint_compatible_lift",
        "reduced_wave_algebraic_phi",
    ):
        raise ValueError("unknown incoming-u1 boundary method")
    validate_state(state, d_matrix.shape[0])
    if boundary_method == "reduced_wave_algebraic_phi" and np.max(
        np.abs(d_matrix @ state.metric - state.normal_spatial_derivative)
    ) > 1.0e-10:
        raise ValueError("reduced-wave mode requires Phi_x = D(psi) at input")

    if gauge_data_rate is None:
        gauge_rates = np.zeros((2, len(SYMMETRIC_PAIRS)), dtype=float)
    else:
        gauge_rates = np.asarray(gauge_data_rate, dtype=float)
        if gauge_rates.shape != (2, len(SYMMETRIC_PAIRS)) or not np.all(
            np.isfinite(gauge_rates)
        ):
            raise ValueError("gauge_data_rate must have shape (2,10) and be finite")

    d_metric = d_matrix @ state.metric
    d_pi = d_matrix @ state.normal_derivative
    d_phi = d_matrix @ state.normal_spatial_derivative

    metric_rhs = -state.normal_derivative.copy()
    pi_rhs = -d_phi
    phi_rhs = -d_pi + gamma2 * d_metric - gamma2 * state.normal_spatial_derivative

    if boundary_method == "constraint_compatible_lift" and d_matrix.shape[0] < 4:
        raise ValueError("the cubic boundary lift requires at least four nodes")
    corrections = [np.zeros(len(SYMMETRIC_PAIRS)), np.zeros(len(SYMMETRIC_PAIRS))]
    faces = ((0, -1, 0), (d_matrix.shape[0] - 1, 1, 1))
    for face_index, normal, face_slot in faces:
        target = full_u1_boundary_target(
            state,
            d_metric,
            face_index=face_index,
            normal=normal,
            gamma2=gamma2,
            gauge_data_rate=gauge_rates[face_slot],
        )
        qdot_raw = (
            pi_rhs[face_index]
            - normal * phi_rhs[face_index]
            - gamma2 * metric_rhs[face_index]
        )
        correction = target - qdot_raw
        if boundary_method == "rinne_pointwise":
            # The incoming right eigenvector is (0, 1, -normal), with q·r=2.
            pi_rhs[face_index] += 0.5 * correction
            phi_rhs[face_index] -= 0.5 * normal * correction
        else:
            corrections[face_slot] = correction

    if boundary_method == "reduced_wave_algebraic_phi":
        for face_index, _, face_slot in faces:
            pi_rhs[face_index] += corrections[face_slot]
        phi_rhs = d_matrix @ metric_rhs

    elif boundary_method == "constraint_compatible_lift":
        metric_lift, pi_lift, phi_lift = constraint_compatible_u1_lift(
            grid, d_matrix, corrections[0], corrections[1]
        )
        metric_rhs += metric_lift
        pi_rhs += pi_lift
        phi_rhs += phi_lift

    return GHSlabState(metric_rhs, pi_rhs, phi_rhs)


def reduction_constraint(state: GHSlabState, derivative: np.ndarray) -> np.ndarray:
    return np.asarray(derivative, dtype=float) @ state.metric - state.normal_spatial_derivative


def linearized_harmonic_constraint(state: GHSlabState) -> np.ndarray:
    """Compute Gamma_a for a perturbation about Minkowski with H_a=0."""

    count = state.metric.shape[0]
    result = np.zeros((count, 4), dtype=float)
    metric_derivative = np.zeros((count, 4, 4, 4), dtype=float)
    metric_derivative[:, 0, :, :] = -state.normal_derivative
    metric_derivative[:, 1, :, :] = state.normal_spatial_derivative

    for a in range(4):
        divergence = np.zeros(count, dtype=float)
        for b in range(4):
            divergence += _ETA[b, b] * metric_derivative[:, b, a, b]
        trace_derivative = np.zeros(count, dtype=float)
        for b in range(4):
            for c in range(4):
                trace_derivative += _ETA[b, c] * metric_derivative[:, a, b, c]
        result[:, a] = divergence - 0.5 * trace_derivative
    return result


def gh_symmetrizer_energy(
    state: GHSlabState,
    norm_weights: np.ndarray,
    gamma2: float,
    symmetrizer_lambda: float = 2.0,
) -> float:
    """Return the positive GH symmetrizer quadratic on the 1D principal state."""

    weights = np.asarray(norm_weights, dtype=float)
    if weights.shape != (state.metric.shape[0],) or np.any(weights <= 0.0):
        raise ValueError("norm_weights must be positive and match the slab nodes")
    if symmetrizer_lambda**2 <= gamma2**2:
        raise ValueError("symmetrizer_lambda^2 must exceed gamma2^2")
    density = (
        symmetrizer_lambda**2 * state.metric**2
        - 2.0 * gamma2 * state.metric * state.normal_derivative
        + state.normal_derivative**2
        + state.normal_spatial_derivative**2
    )
    return float(0.5 * np.sum(weights[:, None] * density))


__all__ = [
    "GHSlabState",
    "characteristic_u1_minus",
    "constraint_compatible_u1_lift",
    "full_u1_boundary_target",
    "gh_full_u1_slab_rhs",
    "gh_symmetrizer_energy",
    "linearized_harmonic_constraint",
    "pack_symmetric",
    "reduction_constraint",
    "unpack_symmetric",
]
