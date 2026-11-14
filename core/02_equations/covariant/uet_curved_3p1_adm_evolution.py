"""Gauge-declared ADM evolution RHS and fixed-gauge hyperbolicity audit.

This module implements the standard nonlinear ADM right-hand sides on the
periodic single-chart geometry lane. It also exposes the linearized
fixed-geodesic-gauge principal symbol. That symbol is defective, so this ADM
branch is an equation/operator control and a formulation no-go, not the
strongly-hyperbolic curved parent.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi
from typing import Any, Final

import numpy as np

from docs.core.uet_curved_3p1_geometry import (
    SpatialGeometryResult,
    compute_periodic_spatial_geometry,
    periodic_central_derivative,
)


ADM_EVOLUTION_OPERATOR_STATUS: Final[str] = (
    "ADM_RHS_READY_FIXED_GAUGE_STRONG_HYPERBOLICITY_REJECTED"
)
SYMMETRIC_COMPONENTS: Final[tuple[tuple[int, int], ...]] = (
    (0, 0),
    (1, 1),
    (2, 2),
    (0, 1),
    (0, 2),
    (1, 2),
)


def _finite_array(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _field(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite_array(value, name)
    if array.ndim == 0:
        return np.full(shape, float(array), dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    return array


def _vector(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite_array(value, name)
    expected = shape + (3,)
    if array.shape != expected:
        raise ValueError(f"{name} must have shape {expected}")
    return array


def _symmetric_tensor(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite_array(value, name)
    expected = shape + (3, 3)
    if array.shape != expected:
        raise ValueError(f"{name} must have shape {expected}")
    if not np.allclose(array, np.swapaxes(array, -1, -2), atol=1e-12, rtol=0.0):
        raise ValueError(f"{name} must be symmetric")
    return array


def _spacing(spacing: Any) -> tuple[float, float, float]:
    values = tuple(float(value) for value in spacing)
    if len(values) != 3:
        raise ValueError("spacing must contain exactly three values")
    if any(not isfinite(value) or value <= 0.0 for value in values):
        raise ValueError("spacing values must be finite and positive")
    return values


@dataclass(frozen=True)
class ADMStressProjection:
    """Eulerian matter projections needed by the ADM evolution equations."""

    energy_density: Any
    momentum_density: Any
    spatial_stress: Any


@dataclass(frozen=True)
class ADMEvolutionRHS:
    spatial_metric_rhs: np.ndarray
    extrinsic_curvature_rhs: np.ndarray
    geometry: SpatialGeometryResult
    trace_extrinsic_curvature: np.ndarray
    trace_spatial_stress: np.ndarray
    lapse_hessian: np.ndarray
    diagnostics: dict[str, Any]


@dataclass(frozen=True)
class ADMPrincipalSymbolResult:
    direction: np.ndarray
    symbol: np.ndarray
    eigenvalues: np.ndarray
    zero_algebraic_multiplicity: int
    zero_geometric_multiplicity: int
    eigenvector_rank: int
    complete_eigenbasis: bool
    classification: str


def _scalar_hessian(
    scalar: np.ndarray,
    geometry: SpatialGeometryResult,
) -> np.ndarray:
    steps = geometry.spacing
    gradient = [
        periodic_central_derivative(scalar, axis=axis, spacing=steps[axis])
        for axis in range(3)
    ]
    hessian = np.zeros(scalar.shape + (3, 3), dtype=float)
    gamma = geometry.christoffel_symbols
    for first in range(3):
        for second in range(3):
            hessian[..., first, second] = periodic_central_derivative(
                gradient[second],
                axis=first,
                spacing=steps[first],
            )
            for contracted in range(3):
                hessian[..., first, second] -= (
                    gamma[..., contracted, first, second]
                    * gradient[contracted]
                )
    return hessian


def _lie_derivative_covariant_tensor(
    tensor: np.ndarray,
    shift: np.ndarray,
    spacing: tuple[float, float, float],
) -> np.ndarray:
    result = np.zeros_like(tensor)
    shift_gradient = np.stack(
        [
            periodic_central_derivative(
                shift,
                axis=axis,
                spacing=spacing[axis],
            )
            for axis in range(3)
        ],
        axis=0,
    )
    for first in range(3):
        for second in range(3):
            for advected in range(3):
                result[..., first, second] += shift[..., advected] * (
                    periodic_central_derivative(
                        tensor[..., first, second],
                        axis=advected,
                        spacing=spacing[advected],
                    )
                )
                result[..., first, second] += (
                    tensor[..., advected, second]
                    * shift_gradient[first, ..., advected]
                    + tensor[..., first, advected]
                    * shift_gradient[second, ..., advected]
                )
    return result


def compute_adm_evolution_rhs(
    *,
    spatial_metric: Any,
    extrinsic_curvature: Any,
    lapse: Any,
    shift: Any,
    matter: ADMStressProjection,
    spacing: Any,
    gravitational_constant: float = 1.0,
    cosmological_constant: float = 0.0,
) -> ADMEvolutionRHS:
    """Evaluate standard ADM ``d_t gamma_ij`` and ``d_t K_ij``.

    Sign convention: spacetime signature ``(-,+,+,+)`` and
    ``K_ij = -(1/2) L_n gamma_ij``.
    """

    coupling = float(gravitational_constant)
    cosmological = float(cosmological_constant)
    if not isfinite(coupling) or coupling <= 0.0:
        raise ValueError("gravitational_constant must be finite and positive")
    if not isfinite(cosmological):
        raise ValueError("cosmological_constant must be finite")

    geometry = compute_periodic_spatial_geometry(spatial_metric, spacing)
    metric = np.linalg.inv(geometry.inverse_metric)
    grid_shape = metric.shape[:3]
    curvature = _symmetric_tensor(
        extrinsic_curvature,
        grid_shape,
        "extrinsic_curvature",
    )
    alpha = _field(lapse, grid_shape, "lapse")
    if np.any(alpha <= 0.0):
        raise ValueError("lapse must be strictly positive")
    beta = _vector(shift, grid_shape, "shift")
    rho = _field(matter.energy_density, grid_shape, "energy_density")
    _vector(matter.momentum_density, grid_shape, "momentum_density")
    stress = _symmetric_tensor(matter.spatial_stress, grid_shape, "spatial_stress")
    steps = _spacing(spacing)

    inverse = geometry.inverse_metric
    trace_curvature = np.einsum("...ij,...ij->...", inverse, curvature)
    trace_stress = np.einsum("...ij,...ij->...", inverse, stress)
    mixed_curvature = np.einsum(
        "...ik,...kj->...ij", inverse, curvature, optimize=True
    )
    curvature_square = np.einsum(
        "...ik,...kj->...ij", curvature, mixed_curvature, optimize=True
    )
    lapse_hessian = _scalar_hessian(alpha, geometry)
    lie_metric = _lie_derivative_covariant_tensor(metric, beta, steps)
    lie_curvature = _lie_derivative_covariant_tensor(curvature, beta, steps)

    metric_rhs = -2.0 * alpha[..., None, None] * curvature + lie_metric
    matter_term = stress - 0.5 * metric * (
        trace_stress - rho
    )[..., None, None]
    curvature_rhs = (
        -lapse_hessian
        + alpha[..., None, None]
        * (
            geometry.ricci_tensor
            + trace_curvature[..., None, None] * curvature
            - 2.0 * curvature_square
            - 8.0 * pi * coupling * matter_term
            - cosmological * metric
        )
        + lie_curvature
    )
    return ADMEvolutionRHS(
        spatial_metric_rhs=metric_rhs,
        extrinsic_curvature_rhs=curvature_rhs,
        geometry=geometry,
        trace_extrinsic_curvature=trace_curvature,
        trace_spatial_stress=trace_stress,
        lapse_hessian=lapse_hessian,
        diagnostics={
            "status": ADM_EVOLUTION_OPERATOR_STATUS,
            "gauge": "declared_positive_lapse_and_shift",
            "fixed_geodesic_control": bool(
                np.all(alpha == 1.0) and np.all(beta == 0.0)
            ),
            "boundary_condition": "periodic_all_axes",
            "metric_evolution_rhs": True,
            "time_integrator": "NOT_IMPLEMENTED",
            "strong_hyperbolicity": "NOT_ESTABLISHED_BY_RHS",
            "field_clipping": False,
            "parameter_fitting": False,
        },
    )


def fixed_gauge_adm_principal_symbol(
    direction: Any,
    *,
    tolerance: float = 1e-10,
) -> ADMPrincipalSymbolResult:
    """Return the pseudo-differential principal symbol about Minkowski space."""

    normal = _finite_array(direction, "direction")
    if normal.shape != (3,):
        raise ValueError("direction must have shape (3,)")
    norm = float(np.linalg.norm(normal))
    if norm <= 0.0:
        raise ValueError("direction must be nonzero")
    normal = normal / norm
    tol = float(tolerance)
    if not isfinite(tol) or tol <= 0.0:
        raise ValueError("tolerance must be finite and positive")

    ricci_map = np.zeros((6, 6), dtype=float)
    for column, (row_index, column_index) in enumerate(SYMMETRIC_COMPONENTS):
        perturbation = np.zeros((3, 3), dtype=float)
        perturbation[row_index, column_index] = 1.0
        perturbation[column_index, row_index] = 1.0
        trace = float(np.trace(perturbation))
        ricci = np.zeros((3, 3), dtype=float)
        for first in range(3):
            for second in range(3):
                ricci[first, second] = 0.5 * (
                    -normal[first] * np.dot(normal, perturbation[:, second])
                    -normal[second] * np.dot(normal, perturbation[:, first])
                    + perturbation[first, second]
                    + normal[first] * normal[second] * trace
                )
        for row, (first, second) in enumerate(SYMMETRIC_COMPONENTS):
            ricci_map[row, column] = ricci[first, second]

    symbol = np.block(
        [
            [np.zeros((6, 6)), -2.0 * np.eye(6)],
            [-ricci_map, np.zeros((6, 6))],
        ]
    )
    eigenvalues = np.linalg.eigvals(symbol)
    zero_geometric = int(12 - np.linalg.matrix_rank(symbol, tol=tol))
    zero_algebraic = int(
        12 - np.linalg.matrix_rank(np.linalg.matrix_power(symbol, 2), tol=tol)
    )
    negative_geometric = int(
        12 - np.linalg.matrix_rank(symbol + np.eye(12), tol=tol)
    )
    positive_geometric = int(
        12 - np.linalg.matrix_rank(symbol - np.eye(12), tol=tol)
    )
    eigenvector_rank = (
        zero_geometric + negative_geometric + positive_geometric
    )
    complete = eigenvector_rank == 12 and zero_geometric == zero_algebraic
    return ADMPrincipalSymbolResult(
        direction=normal,
        symbol=symbol,
        eigenvalues=eigenvalues,
        zero_algebraic_multiplicity=zero_algebraic,
        zero_geometric_multiplicity=zero_geometric,
        eigenvector_rank=eigenvector_rank,
        complete_eigenbasis=complete,
        classification=(
            "STRONGLY_HYPERBOLIC_CANDIDATE"
            if complete
            else "DEFECTIVE_ZERO_SPEED_JORDAN_BLOCK"
        ),
    )


def adm_evolution_contract() -> dict[str, Any]:
    return {
        "status": ADM_EVOLUTION_OPERATOR_STATUS,
        "signature": "(-,+,+,+)",
        "extrinsic_curvature_convention": "K_ij = -(1/2) L_n gamma_ij",
        "unit_lane": "geometric periodic Cartesian chart",
        "relations": {
            "metric_evolution": "d_t gamma_ij = -2 alpha K_ij + L_beta gamma_ij",
            "curvature_evolution": "d_t K_ij = -D_i D_j alpha + alpha[R_ij + K K_ij - 2 K_ik K^k_j - 8 pi G(S_ij - gamma_ij(S-rho)/2) - Lambda gamma_ij] + L_beta K_ij",
        },
        "branch_decision": {
            "fixed_geodesic_adm": "REJECTED_FOR_STRONG_HYPERBOLIC_PARENT",
            "reason": "linearized pseudo-differential principal symbol has a defective zero-speed eigenspace",
            "next_branch": "FIRST_ORDER_GENERALIZED_HARMONIC",
            "next_branch_status": "PREREGISTERED_NOT_IMPLEMENTED",
        },
        "ontology": {
            "gamma_ij": "standard spatial metric; not Phi",
            "K_ij": "standard extrinsic curvature; not Pi",
            "matter_projection": "external stress-energy projection; not universal C",
            "R_gen": "excluded derived history trace",
            "R_obs": "excluded observer record",
        },
        "implemented": [
            "nonlinear periodic ADM metric RHS",
            "nonlinear periodic ADM extrinsic-curvature RHS",
            "declared lapse/shift and their derivative terms",
            "Eulerian matter-stress source term",
            "fixed-gauge linearized principal-symbol audit",
        ],
        "not_implemented": [
            "strongly-hyperbolic generalized-harmonic evolution",
            "time integration and CFL policy",
            "constraint damping and propagation verification",
            "non-periodic constraint-preserving boundaries",
            "Topic 13 stress-energy evolution/projection wiring",
            "SI detector-observable mapping",
        ],
        "claim_boundary": (
            "standard ADM RHS operator and fixed-gauge formulation no-go only; "
            "not a well-posed numerical-relativity evolution system or GR validation"
        ),
    }


__all__ = [
    "ADM_EVOLUTION_OPERATOR_STATUS",
    "ADMStressProjection",
    "ADMEvolutionRHS",
    "ADMPrincipalSymbolResult",
    "compute_adm_evolution_rhs",
    "fixed_gauge_adm_principal_symbol",
    "adm_evolution_contract",
]
