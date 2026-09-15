"""Periodic-grid differential geometry for the curved 3+1 Core parent.

The operators in this module discretize standard spatial differential geometry
on a uniform periodic Cartesian chart. They supply geometric inputs to the ADM
constraint interface; they do not evolve the metric or identify ``Phi`` with a
metric degree of freedom.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_curved_3p1_constraints import ADMGeometryState


CURVED_3P1_GEOMETRY_OPERATOR_STATUS: Final[str] = (
    "CURVED_3P1_PERIODIC_GEOMETRY_OPERATOR_ONLY"
)


def _finite_array(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _spacing_tuple(spacing: Any) -> tuple[float, float, float]:
    values = tuple(float(value) for value in spacing)
    if len(values) != 3:
        raise ValueError("spacing must contain exactly three values")
    if any(not isfinite(value) or value <= 0.0 for value in values):
        raise ValueError("spacing values must be finite and positive")
    return values


def _metric_grid(spatial_metric: Any) -> np.ndarray:
    metric = _finite_array(spatial_metric, "spatial_metric")
    if metric.ndim != 5 or metric.shape[-2:] != (3, 3):
        raise ValueError("spatial_metric must have shape (nx, ny, nz, 3, 3)")
    if any(size < 5 for size in metric.shape[:3]):
        raise ValueError("each periodic grid axis must contain at least five points")
    if not np.allclose(metric, np.swapaxes(metric, -1, -2), atol=1e-12, rtol=0.0):
        raise ValueError("spatial_metric must be symmetric")
    if float(np.min(np.linalg.eigvalsh(metric))) <= 0.0:
        raise ValueError("spatial_metric must be positive definite")
    return metric


def _symmetric_tensor_grid(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    tensor = _finite_array(value, name)
    if tensor.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if not np.allclose(tensor, np.swapaxes(tensor, -1, -2), atol=1e-12, rtol=0.0):
        raise ValueError(f"{name} must be symmetric")
    return tensor


def periodic_central_derivative(
    field: Any,
    *,
    axis: int,
    spacing: float,
) -> np.ndarray:
    """Second-order central derivative on a declared periodic grid axis."""

    array = _finite_array(field, "field")
    if axis not in (0, 1, 2):
        raise ValueError("axis must be one of 0, 1, or 2")
    step = float(spacing)
    if not isfinite(step) or step <= 0.0:
        raise ValueError("spacing must be finite and positive")
    if array.shape[axis] < 5:
        raise ValueError("periodic derivative axes require at least five points")
    return (np.roll(array, -1, axis=axis) - np.roll(array, 1, axis=axis)) / (
        2.0 * step
    )


@dataclass(frozen=True)
class SpatialGeometryResult:
    inverse_metric: np.ndarray
    metric_derivatives: np.ndarray
    christoffel_symbols: np.ndarray
    ricci_tensor: np.ndarray
    ricci_scalar: np.ndarray
    max_abs_metric_compatibility_residual: float
    max_abs_ricci_antisymmetry: float
    minimum_metric_eigenvalue: float
    spacing: tuple[float, float, float]
    diagnostics: dict[str, Any]


def compute_periodic_spatial_geometry(
    spatial_metric: Any,
    spacing: Any,
) -> SpatialGeometryResult:
    """Compute the Levi-Civita connection and spatial Ricci curvature."""

    metric = _metric_grid(spatial_metric)
    steps = _spacing_tuple(spacing)
    inverse = np.linalg.inv(metric)
    derivatives = np.stack(
        [
            periodic_central_derivative(metric, axis=axis, spacing=steps[axis])
            for axis in range(3)
        ],
        axis=0,
    )

    grid_shape = metric.shape[:3]
    christoffel = np.zeros(grid_shape + (3, 3, 3), dtype=float)
    for upper in range(3):
        for first in range(3):
            for second in range(3):
                for contracted in range(3):
                    christoffel[..., upper, first, second] += 0.5 * inverse[
                        ..., upper, contracted
                    ] * (
                        derivatives[first, ..., contracted, second]
                        + derivatives[second, ..., contracted, first]
                        - derivatives[contracted, ..., first, second]
                    )

    metric_compatibility = np.zeros((3,) + metric.shape, dtype=float)
    for derivative_axis in range(3):
        for first in range(3):
            for second in range(3):
                metric_compatibility[derivative_axis, ..., first, second] = derivatives[
                    derivative_axis, ..., first, second
                ]
                for contracted in range(3):
                    metric_compatibility[
                        derivative_axis, ..., first, second
                    ] -= (
                        christoffel[..., contracted, derivative_axis, first]
                        * metric[..., contracted, second]
                        + christoffel[..., contracted, derivative_axis, second]
                        * metric[..., first, contracted]
                    )

    ricci = np.zeros(grid_shape + (3, 3), dtype=float)
    for first in range(3):
        for second in range(3):
            for contracted in range(3):
                ricci[..., first, second] += periodic_central_derivative(
                    christoffel[..., contracted, first, second],
                    axis=contracted,
                    spacing=steps[contracted],
                )
                ricci[..., first, second] -= periodic_central_derivative(
                    christoffel[..., contracted, first, contracted],
                    axis=second,
                    spacing=steps[second],
                )
                for nested in range(3):
                    ricci[..., first, second] += (
                        christoffel[..., contracted, first, second]
                        * christoffel[..., nested, contracted, nested]
                        - christoffel[..., nested, first, contracted]
                        * christoffel[..., contracted, second, nested]
                    )

    ricci_scalar = np.einsum("...ij,...ij->...", inverse, ricci, optimize=True)
    antisymmetry = ricci - np.swapaxes(ricci, -1, -2)
    return SpatialGeometryResult(
        inverse_metric=inverse,
        metric_derivatives=derivatives,
        christoffel_symbols=christoffel,
        ricci_tensor=ricci,
        ricci_scalar=ricci_scalar,
        max_abs_metric_compatibility_residual=float(
            np.max(np.abs(metric_compatibility))
        ),
        max_abs_ricci_antisymmetry=float(np.max(np.abs(antisymmetry))),
        minimum_metric_eigenvalue=float(np.min(np.linalg.eigvalsh(metric))),
        spacing=steps,
        diagnostics={
            "status": CURVED_3P1_GEOMETRY_OPERATOR_STATUS,
            "boundary_condition": "periodic_on_all_three_axes",
            "spatial_discretization": "second_order_centered",
            "metric_evolution": False,
            "gauge_evolution": False,
            "field_clipping": False,
            "parameter_fitting": False,
        },
    )


def compute_periodic_momentum_tensor_divergence(
    spatial_metric: Any,
    extrinsic_curvature: Any,
    spacing: Any,
    *,
    geometry: SpatialGeometryResult | None = None,
) -> np.ndarray:
    """Compute ``D_j(K^j_i - delta^j_i K)`` on a periodic grid."""

    metric = _metric_grid(spatial_metric)
    curvature = _symmetric_tensor_grid(
        extrinsic_curvature, metric.shape, "extrinsic_curvature"
    )
    steps = _spacing_tuple(spacing)
    spatial = geometry or compute_periodic_spatial_geometry(metric, steps)
    if spatial.inverse_metric.shape != metric.shape or spatial.spacing != steps:
        raise ValueError("geometry must correspond to spatial_metric and spacing")
    if not np.allclose(
        spatial.inverse_metric,
        np.linalg.inv(metric),
        atol=1e-12,
        rtol=1e-12,
    ):
        raise ValueError("geometry inverse metric does not match spatial_metric")

    mixed_curvature = np.einsum(
        "...jk,...ki->...ji", spatial.inverse_metric, curvature, optimize=True
    )
    trace = np.einsum("...ji,...ij->...", spatial.inverse_metric, curvature)
    momentum_tensor = mixed_curvature - trace[..., None, None] * np.eye(3)
    divergence = np.zeros(metric.shape[:3] + (3,), dtype=float)
    gamma = spatial.christoffel_symbols
    for lower in range(3):
        for derivative_axis in range(3):
            divergence[..., lower] += periodic_central_derivative(
                momentum_tensor[..., derivative_axis, lower],
                axis=derivative_axis,
                spacing=steps[derivative_axis],
            )
            for contracted in range(3):
                divergence[..., lower] += (
                    gamma[..., derivative_axis, derivative_axis, contracted]
                    * momentum_tensor[..., contracted, lower]
                    - gamma[..., contracted, derivative_axis, lower]
                    * momentum_tensor[..., derivative_axis, contracted]
                )
    return divergence


def adm_geometry_from_periodic_grid(
    *,
    lapse: Any,
    shift: Any,
    spatial_metric: Any,
    extrinsic_curvature: Any,
    spacing: Any,
) -> tuple[ADMGeometryState, SpatialGeometryResult]:
    """Build an ADM constraint input using computed spatial operators."""

    metric = _metric_grid(spatial_metric)
    curvature = _symmetric_tensor_grid(
        extrinsic_curvature, metric.shape, "extrinsic_curvature"
    )
    geometry = compute_periodic_spatial_geometry(metric, spacing)
    divergence = compute_periodic_momentum_tensor_divergence(
        metric,
        curvature,
        spacing,
        geometry=geometry,
    )
    return (
        ADMGeometryState(
            lapse=lapse,
            shift=shift,
            spatial_metric=metric,
            extrinsic_curvature=curvature,
            spatial_ricci_scalar=geometry.ricci_scalar,
            momentum_tensor_divergence=divergence,
        ),
        geometry,
    )


def curved_3p1_geometry_operator_contract() -> dict[str, Any]:
    return {
        "status": CURVED_3P1_GEOMETRY_OPERATOR_STATUS,
        "classification": "numerical_implementation_of_standard_spatial_geometry",
        "chart": "uniform Cartesian chart",
        "boundary_condition": "periodic on x, y, and z",
        "spatial_order": 2,
        "unit_lane": "geometric; coordinates and spacing carry length L",
        "relations": {
            "christoffel": "Gamma^k_ij = 1/2 gamma^kl (d_i gamma_lj + d_j gamma_li - d_l gamma_ij)",
            "ricci_tensor": "R_ij = d_k Gamma^k_ij - d_j Gamma^k_ik + Gamma^k_ij Gamma^l_kl - Gamma^l_ik Gamma^k_jl",
            "ricci_scalar": "R3 = gamma^ij R_ij",
            "momentum_divergence": "D_j B^j_i = d_j B^j_i + Gamma^j_jm B^m_i - Gamma^m_ji B^j_m",
            "momentum_tensor": "B^j_i = K^j_i - delta^j_i K",
        },
        "ontology": {
            "gamma_ij": "standard spatial metric; not Phi",
            "K_ij": "standard extrinsic curvature; not Pi",
            "C": "not used or relabelled by the geometry operator",
            "R_gen": "excluded derived history trace",
            "R_obs": "excluded observer record",
        },
        "implemented": [
            "periodic second-order central derivative",
            "Levi-Civita connection",
            "spatial Ricci tensor and scalar",
            "covariant momentum-tensor divergence",
            "ADM geometry-state adapter",
        ],
        "not_implemented": [
            "non-periodic boundary conditions or multiple charts",
            "lapse and shift gauge evolution",
            "spatial-metric and extrinsic-curvature evolution",
            "strong-hyperbolicity proof",
            "constraint propagation or damping",
            "temporal convergence",
            "Topic 13 stress-energy projection wiring",
            "SI detector-observable mapping",
        ],
        "claim_boundary": (
            "periodic-grid spatial differential-geometry operator with internal "
            "analytic controls only; not a spacetime evolution solver or GR validation"
        ),
    }


__all__ = [
    "CURVED_3P1_GEOMETRY_OPERATOR_STATUS",
    "SpatialGeometryResult",
    "periodic_central_derivative",
    "compute_periodic_spatial_geometry",
    "compute_periodic_momentum_tensor_divergence",
    "adm_geometry_from_periodic_grid",
    "curved_3p1_geometry_operator_contract",
]
