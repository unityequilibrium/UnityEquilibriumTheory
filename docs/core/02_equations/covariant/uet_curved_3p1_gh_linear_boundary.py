"""Linearized, frozen-background GH boundary residuals.

The inputs are perturbations about Minkowski space in a local orthonormal
frame. The formulas follow Rinne (2006), Eqs. (27)-(33), and are evaluated
as boundary residuals only. This module does not evolve a non-periodic IBVP.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

import numpy as np

from .uet_curved_3p1_gh_boundary_projectors import (
    SYMMETRIC_PAIRS,
    apply_gh_boundary_projector,
    build_gh_boundary_projectors,
)


_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
_ETA_INV = _ETA


@dataclass(frozen=True)
class GHLinearBoundaryResiduals:
    normal: tuple[float, float, float]
    normal_shift: float
    boundary_regime: str
    constraint_incoming: np.ndarray
    physical_weyl_incoming: np.ndarray
    gauge_incoming: np.ndarray
    u2_curl_incoming: np.ndarray
    diagnostics: dict[str, float]


def _finite(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _symmetric(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite(value, name)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if not np.allclose(array, np.swapaxes(array, -1, -2), atol=1.0e-12, rtol=0.0):
        raise ValueError(f"{name} must be symmetric in its spacetime indices")
    return array


def _unit_normal(normal: Any) -> np.ndarray:
    value = _finite(normal, "normal")
    if value.shape != (3,):
        raise ValueError("normal must have shape (3,)")
    norm = float(np.linalg.norm(value))
    if norm <= 0.0:
        raise ValueError("normal must be nonzero")
    return value / norm


def _tangent_basis(normal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    seed = np.array([1.0, 0.0, 0.0])
    if abs(float(normal @ seed)) > 0.8:
        seed = np.array([0.0, 1.0, 0.0])
    first = seed - float(seed @ normal) * normal
    first /= np.linalg.norm(first)
    second = np.cross(normal, first)
    second /= np.linalg.norm(second)
    return first, second


def _spatial_derivative(gradient: np.ndarray, direction: np.ndarray) -> np.ndarray:
    return np.tensordot(direction, gradient, axes=(0, 0))


def _trace(tensor: np.ndarray) -> float:
    return float(np.einsum("ab,ab->", _ETA_INV, tensor))


def gh_boundary_normal_maps(normal: Any) -> dict[str, np.ndarray]:
    """Return the four constraint and two physical normal-derivative maps.

    The maps act on ``d_n u1_minus`` for the constraint sector and on
    ``d_n (u1_minus + gamma2*delta_psi)`` for the physical sector. Their
    kernels should contain the complementary source-defined projectors.
    """

    unit = _unit_normal(normal)
    projectors = build_gh_boundary_projectors(unit)
    t_up = np.array([1.0, 0.0, 0.0, 0.0])
    n_up = np.concatenate(([0.0], unit))
    t_down = _ETA @ t_up
    k_up = (t_up - n_up) / sqrt(2.0)
    k_down = _ETA @ k_up
    tangents = tuple(np.concatenate(([0.0], value)) for value in _tangent_basis(unit))

    constraint_map = np.empty((4, len(SYMMETRIC_PAIRS)), dtype=float)
    physical_map = np.empty((2, len(SYMMETRIC_PAIRS)), dtype=float)
    for column, (i, j) in enumerate(SYMMETRIC_PAIRS):
        tensor = np.zeros((4, 4), dtype=float)
        tensor[i, j] = 1.0
        tensor[j, i] = 1.0
        constraint_map[:, column] = sqrt(2.0) * (
            k_up @ tensor - 0.5 * k_down * _trace(tensor)
        )
        xx = float(tangents[0] @ tensor @ tangents[0])
        yy = float(tangents[1] @ tensor @ tangents[1])
        xy = float(tangents[0] @ tensor @ tangents[1])
        physical_map[:, column] = (0.5 * (xx - yy), xy)

    constraint_map.setflags(write=False)
    physical_map.setflags(write=False)
    return {
        "constraint": constraint_map,
        "physical": physical_map,
        "constraint_projector": projectors.constraint,
        "physical_projector": projectors.physical,
    }


def gh_linear_boundary_residuals(
    *,
    metric_perturbation: Any,
    pi_perturbation: Any,
    phi_perturbation: Any,
    metric_gradient: Any,
    pi_gradient: Any,
    phi_gradient: Any,
    normal: Any,
    lapse: float = 1.0,
    normal_shift: float = 0.0,
    gamma2: float = 1.0,
    physical_data: Any | None = None,
    gauge_data: Any | None = None,
) -> GHLinearBoundaryResiduals:
    """Evaluate frozen-coefficient GH boundary residuals at one face point.

    ``metric_perturbation``, ``pi_perturbation``, and ``phi_perturbation`` are
    perturbations from Minkowski data. Gradient arrays have leading spatial
    derivative axes: 3 for metric/Pi and (3,3) for the spatial-derivative Phi
    state, followed by its symmetric spacetime indices. All values use
    geometric units in the local orthonormal frame.
    """

    lapse_value = float(lapse)
    shift_value = float(normal_shift)
    gamma2_value = float(gamma2)
    if not isfinite(lapse_value) or lapse_value <= 0.0:
        raise ValueError("lapse must be finite and positive")
    if not isfinite(shift_value):
        raise ValueError("normal_shift must be finite")
    if not -lapse_value < shift_value < lapse_value:
        raise ValueError("boundary residuals require a strictly subluminal normal shift")
    if not isfinite(gamma2_value) or gamma2_value <= 0.0:
        raise ValueError("gamma2 must be finite and positive")

    unit = _unit_normal(normal)
    tangents3 = _tangent_basis(unit)
    tangents4 = tuple(np.concatenate(([0.0], tangent)) for tangent in tangents3)
    normal4 = np.concatenate(([0.0], unit))
    t_up = np.array([1.0, 0.0, 0.0, 0.0])
    t_down = _ETA @ t_up
    k_up = (t_up - normal4) / sqrt(2.0)
    k_down = _ETA @ k_up

    metric = _symmetric(metric_perturbation, (4, 4), "metric_perturbation")
    pi = _symmetric(pi_perturbation, (4, 4), "pi_perturbation")
    phi = _symmetric(phi_perturbation, (3, 4, 4), "phi_perturbation")
    dmetric = _symmetric(metric_gradient, (3, 4, 4), "metric_gradient")
    dpi = _symmetric(pi_gradient, (3, 4, 4), "pi_gradient")
    dphi = _symmetric(phi_gradient, (3, 3, 4, 4), "phi_gradient")

    physical_target = np.zeros((4, 4), dtype=float) if physical_data is None else _symmetric(
        physical_data, (4, 4), "physical_data"
    )
    gauge_target = np.zeros((4, 4), dtype=float) if gauge_data is None else _symmetric(
        gauge_data, (4, 4), "gauge_data"
    )

    projector_set = build_gh_boundary_projectors(unit)
    physical_trace = float(
        np.einsum("ab,ab->", projector_set.spatial_projector_contravariant, physical_target)
    )
    if (
        np.max(np.abs(t_up @ physical_target)) > 1.0e-10
        or np.max(np.abs(normal4 @ physical_target)) > 1.0e-10
        or abs(physical_trace) > 1.0e-10
    ):
        raise ValueError("physical_data must be transverse and trace-free on the boundary")
    if np.max(
        np.abs(
            apply_gh_boundary_projector(gauge_target, projector_set.gauge)
            - gauge_target
        )
    ) > 1.0e-10:
        raise ValueError("gauge_data must lie in the gauge-projector subspace")

    dmetric_n = _spatial_derivative(dmetric, unit)
    dpi_n = _spatial_derivative(dpi, unit)
    dphi_n = _spatial_derivative(dphi, unit)
    dphi_n_n = np.tensordot(unit, dphi_n, axes=(0, 0))
    d_u1_minus_n = dpi_n - dphi_n_n - gamma2_value * dmetric_n

    # Rinne (2006), Eq. (27): incoming subsidiary-constraint field c^{0-}_a.
    constraint = sqrt(2.0) * (
        k_up @ d_u1_minus_n - 0.5 * k_down * _trace(d_u1_minus_n)
    )
    for tangent in tangents3:
        tangent4 = np.concatenate(([0.0], tangent))
        tangent_down = _ETA @ tangent4
        dmetric_a = _spatial_derivative(dmetric, tangent)
        dpi_a = _spatial_derivative(dpi, tangent)
        dphi_a = _spatial_derivative(dphi, tangent)
        phi_tangent = np.tensordot(tangent, dphi_a, axes=(0, 0))
        phi_normal = np.tensordot(unit, dphi_a, axes=(0, 0))

        constraint += 0.5 * tangent_down * _trace(dpi_a)
        constraint -= tangent4 @ dpi_a
        constraint -= t_up @ phi_tangent
        constraint += 0.5 * t_down * _trace(phi_tangent)
        constraint += gamma2_value * (
            tangent4 @ dmetric_a - 0.5 * tangent_down * _trace(dmetric_a)
        )
        constraint += tangent4 @ phi_normal
        constraint -= 0.5 * tangent_down * _trace(phi_normal)

    # Rinne (2006), Eqs. (30)-(33): incoming Weyl/Psi_0 field.
    # The normal derivative is d_n(Pi - Phi_n), since gamma2*delta_psi cancels.
    d_u1_plus_gamma2_metric_n = dpi_n - dphi_n_n
    physical_bracket = np.zeros((2, 2), dtype=float)
    for a_index, tangent_a in enumerate(tangents3):
        tangent_a4 = np.concatenate(([0.0], tangent_a))
        dpi_a = _spatial_derivative(dpi, tangent_a)
        dphi_a = _spatial_derivative(dphi, tangent_a)
        phi_normal = np.tensordot(unit, dphi_a, axes=(0, 0))
        phi_a = np.tensordot(tangent_a, dphi_a, axes=(0, 0))
        for b_index, tangent_b in enumerate(tangents3):
            tangent_b4 = np.concatenate(([0.0], tangent_b))
            value = float(
                tangent_a4 @ d_u1_plus_gamma2_metric_n @ tangent_b4
            )

            for spatial_i in range(3):
                value += 2.0 * float(
                    dphi_a[spatial_i, spatial_i + 1, :] @ tangent_b4
                )
            phi_b = np.tensordot(tangent_b, dphi_a, axes=(0, 0))
            value -= float(np.trace(phi_b[1:, 1:]))

            for tangent_c in tangents3:
                dphi_c = _spatial_derivative(dphi, tangent_c)
                phi_c = np.tensordot(tangent_c, dphi_c, axes=(0, 0))
                value -= float(tangent_a4 @ phi_c @ tangent_b4)

            value += float(tangent_b4 @ phi_normal @ t_up)
            value -= float(tangent_b4 @ dpi_a @ normal4)
            value -= float(normal4 @ phi_b @ t_up)
            physical_bracket[a_index, b_index] = value

    physical_symmetric = 0.5 * (physical_bracket + physical_bracket.T)
    physical_trace_2d = 0.5 * float(np.trace(physical_symmetric))
    physical_weyl = np.zeros((4, 4), dtype=float)
    for a_index, tangent_a in enumerate(tangents4):
        for b_index, tangent_b in enumerate(tangents4):
            component = physical_symmetric[a_index, b_index]
            if a_index == b_index:
                component -= physical_trace_2d
            physical_weyl += component * np.outer(tangent_a, tangent_b)
    physical_residual = physical_weyl - physical_target

    incoming_u1_minus = pi - np.tensordot(unit, phi, axes=(0, 0)) - gamma2_value * metric
    gauge_residual = apply_gh_boundary_projector(
        incoming_u1_minus, projector_set.gauge
    ) - gauge_target

    u2_curl = np.zeros((2, 4, 4), dtype=float)
    for tangent_index, tangent in enumerate(tangents3):
        dphi_a = _spatial_derivative(dphi, tangent)
        dphi_normal_direction = _spatial_derivative(dphi, unit)
        derivative_n_phi_a = np.tensordot(tangent, dphi_normal_direction, axes=(0, 0))
        derivative_a_phi_n = np.tensordot(unit, dphi_a, axes=(0, 0))
        u2_curl[tangent_index] = derivative_n_phi_a - derivative_a_phi_n

    incoming_u2 = shift_value > 0.0
    diagnostics = {
        "constraint_residual_l2": float(np.linalg.norm(constraint)),
        "physical_weyl_residual_l2": float(np.linalg.norm(physical_residual)),
        "gauge_residual_l2": float(np.linalg.norm(gauge_residual)),
        "u2_curl_residual_l2": float(np.linalg.norm(u2_curl)),
        "physical_bracket_antisymmetry_l2": float(
            np.linalg.norm(physical_bracket - physical_bracket.T)
        ),
    }
    outputs = (constraint, physical_residual, gauge_residual, u2_curl)
    for output in outputs:
        output.setflags(write=False)
    return GHLinearBoundaryResiduals(
        normal=tuple(float(value) for value in unit),
        normal_shift=shift_value,
        boundary_regime=(
            "U1_AND_U2_INCOMING_SUBLUMINAL" if incoming_u2 else "U1_ONLY_INCOMING_SUBLUMINAL"
        ),
        constraint_incoming=constraint,
        physical_weyl_incoming=physical_residual,
        gauge_incoming=gauge_residual,
        u2_curl_incoming=u2_curl,
        diagnostics=diagnostics,
    )


__all__ = [
    "GHLinearBoundaryResiduals",
    "gh_boundary_normal_maps",
    "gh_linear_boundary_residuals",
]
