"""Curved 3+1 ADM constraint interface for the UET Core parent.

This module evaluates the standard Hamiltonian and momentum constraints from
declared 3+1 geometric inputs. It does not evolve the metric, choose a gauge,
or infer matter projections from ``C`` or ``Phi``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi
from typing import Any, Final

import numpy as np


ADM_CONSTRAINT_INTERFACE_STATUS: Final[str] = (
    "CURVED_3P1_ADM_CONSTRAINT_INTERFACE_ONLY"
)


def _finite_array(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


def _field(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    result = _finite_array(value, name)
    if result.ndim == 0:
        return np.full(shape, float(result), dtype=float)
    if result.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    return result


def _vector(value: Any, leading: tuple[int, ...], name: str) -> np.ndarray:
    result = _finite_array(value, name)
    expected = leading + (3,)
    if result.shape != expected:
        raise ValueError(f"{name} must have shape {expected}")
    return result


@dataclass(frozen=True)
class ADMGeometryState:
    """One or more spatial-slice states in the (-,+,+,+) convention."""

    lapse: Any
    shift: Any
    spatial_metric: Any
    extrinsic_curvature: Any
    spatial_ricci_scalar: Any
    momentum_tensor_divergence: Any

    def normalized(self) -> tuple[np.ndarray, ...]:
        metric = _finite_array(self.spatial_metric, "spatial_metric")
        if metric.ndim < 2 or metric.shape[-2:] != (3, 3):
            raise ValueError("spatial_metric must end in shape (3, 3)")
        leading = metric.shape[:-2]
        if not np.allclose(metric, np.swapaxes(metric, -1, -2), atol=1e-12, rtol=0.0):
            raise ValueError("spatial_metric must be symmetric")
        if float(np.min(np.linalg.eigvalsh(metric))) <= 0.0:
            raise ValueError("spatial_metric must be positive definite")

        curvature = _finite_array(self.extrinsic_curvature, "extrinsic_curvature")
        if curvature.shape != metric.shape:
            raise ValueError("extrinsic_curvature must match spatial_metric shape")
        if not np.allclose(
            curvature, np.swapaxes(curvature, -1, -2), atol=1e-12, rtol=0.0
        ):
            raise ValueError("extrinsic_curvature must be symmetric")

        lapse = _field(self.lapse, leading, "lapse")
        if np.any(lapse <= 0.0):
            raise ValueError("lapse must be strictly positive")
        shift = _vector(self.shift, leading, "shift")
        ricci = _field(self.spatial_ricci_scalar, leading, "spatial_ricci_scalar")
        divergence = _vector(
            self.momentum_tensor_divergence,
            leading,
            "momentum_tensor_divergence",
        )
        return lapse, shift, metric, curvature, ricci, divergence


@dataclass(frozen=True)
class ADMMatterProjection:
    """Eulerian energy and covariant momentum density on a spatial slice."""

    energy_density: Any
    momentum_density: Any


@dataclass(frozen=True)
class ADMConstraintResult:
    hamiltonian_residual: np.ndarray
    momentum_residual: np.ndarray
    trace_extrinsic_curvature: np.ndarray
    extrinsic_curvature_contraction: np.ndarray
    hamiltonian_scale: np.ndarray
    momentum_scale: np.ndarray
    max_abs_hamiltonian_residual: float
    max_abs_momentum_residual: float
    max_normalized_hamiltonian_residual: float
    max_normalized_momentum_residual: float
    unit_lane: str
    diagnostics: dict[str, Any]


def evaluate_adm_constraints(
    geometry: ADMGeometryState,
    matter: ADMMatterProjection,
    *,
    gravitational_constant: float = 1.0,
) -> ADMConstraintResult:
    """Evaluate ADM constraints from precomputed spatial geometry inputs.

    The caller supplies ``R^(3)`` and
    ``D_j(K^j_i - delta^j_i K)``. Computing those differential-geometry
    operators from a grid metric is deliberately a later solver wave.
    """

    coupling = float(gravitational_constant)
    if not isfinite(coupling) or coupling <= 0.0:
        raise ValueError("gravitational_constant must be finite and positive")

    lapse, shift, metric, curvature, ricci, divergence = geometry.normalized()
    leading = metric.shape[:-2]
    energy = _field(matter.energy_density, leading, "energy_density")
    momentum = _vector(matter.momentum_density, leading, "momentum_density")

    inverse = np.linalg.inv(metric)
    trace = np.einsum("...ij,...ij->...", inverse, curvature)
    raised = np.einsum(
        "...ik,...jl,...kl->...ij", inverse, inverse, curvature, optimize=True
    )
    contraction = np.einsum("...ij,...ij->...", curvature, raised)

    matter_energy_term = 16.0 * pi * coupling * energy
    hamiltonian = ricci + trace**2 - contraction - matter_energy_term
    matter_momentum_term = 8.0 * pi * coupling * momentum
    momentum_residual = divergence - matter_momentum_term

    hamiltonian_scale = np.maximum.reduce(
        [np.abs(ricci), np.abs(trace**2), np.abs(contraction), np.abs(matter_energy_term)]
    )
    hamiltonian_scale = np.where(hamiltonian_scale > 0.0, hamiltonian_scale, 1.0)
    momentum_scale = np.maximum(np.abs(divergence), np.abs(matter_momentum_term))
    momentum_scale = np.max(momentum_scale, axis=-1)
    momentum_scale = np.where(momentum_scale > 0.0, momentum_scale, 1.0)

    return ADMConstraintResult(
        hamiltonian_residual=hamiltonian,
        momentum_residual=momentum_residual,
        trace_extrinsic_curvature=trace,
        extrinsic_curvature_contraction=contraction,
        hamiltonian_scale=hamiltonian_scale,
        momentum_scale=momentum_scale,
        max_abs_hamiltonian_residual=float(np.max(np.abs(hamiltonian))),
        max_abs_momentum_residual=float(np.max(np.abs(momentum_residual))),
        max_normalized_hamiltonian_residual=float(
            np.max(np.abs(hamiltonian) / hamiltonian_scale)
        ),
        max_normalized_momentum_residual=float(
            np.max(np.max(np.abs(momentum_residual), axis=-1) / momentum_scale)
        ),
        unit_lane="geometric_G_equals_1_or_declared_G",
        diagnostics={
            "status": ADM_CONSTRAINT_INTERFACE_STATUS,
            "lapse_min": float(np.min(lapse)),
            "shift_max_abs": float(np.max(np.abs(shift))),
            "minimum_spatial_metric_eigenvalue": float(
                np.min(np.linalg.eigvalsh(metric))
            ),
            "metric_evolution": False,
            "gauge_evolution": False,
            "differential_geometry_operator": "EXTERNAL_DECLARED_INPUT",
            "field_clipping": False,
            "parameter_fitting": False,
        },
    )


def minkowski_adm_control(
    shape: tuple[int, ...] = (),
) -> tuple[ADMGeometryState, ADMMatterProjection]:
    metric = np.broadcast_to(np.eye(3), shape + (3, 3)).copy()
    zero_tensor = np.zeros_like(metric)
    zero_vector = np.zeros(shape + (3,))
    return (
        ADMGeometryState(1.0, zero_vector, metric, zero_tensor, 0.0, zero_vector),
        ADMMatterProjection(0.0, zero_vector),
    )


def flat_flrw_adm_control(
    scale_factor: float,
    hubble_rate: float,
    *,
    shape: tuple[int, ...] = (),
    gravitational_constant: float = 1.0,
) -> tuple[ADMGeometryState, ADMMatterProjection]:
    scale = float(scale_factor)
    hubble = float(hubble_rate)
    coupling = float(gravitational_constant)
    if not isfinite(scale) or scale <= 0.0:
        raise ValueError("scale_factor must be finite and positive")
    if not isfinite(hubble):
        raise ValueError("hubble_rate must be finite")
    if not isfinite(coupling) or coupling <= 0.0:
        raise ValueError("gravitational_constant must be finite and positive")

    metric = np.broadcast_to((scale**2) * np.eye(3), shape + (3, 3)).copy()
    curvature = -hubble * metric
    zero_vector = np.zeros(shape + (3,))
    energy = 3.0 * hubble**2 / (8.0 * pi * coupling)
    return (
        ADMGeometryState(1.0, zero_vector, metric, curvature, 0.0, zero_vector),
        ADMMatterProjection(energy, zero_vector),
    )


def adm_constraint_contract() -> dict[str, Any]:
    return {
        "status": ADM_CONSTRAINT_INTERFACE_STATUS,
        "signature": "(-,+,+,+)",
        "unit_lane": "geometric units with explicitly supplied positive G",
        "equations": {
            "hamiltonian": "R3 + K^2 - K_ij K^ij - 16*pi*G*rho = 0",
            "momentum": "D_j(K^j_i - delta^j_i*K) - 8*pi*G*S_i = 0",
        },
        "ontology": {
            "spatial_metric": "standard 3-metric; not Phi",
            "matter_projection": "external stress-energy projection; not universal C",
            "R_gen": "excluded derived history trace",
            "R_obs": "excluded observer record",
        },
        "implemented": [
            "metric validation and index contraction",
            "Hamiltonian residual",
            "momentum residual from declared covariant divergence",
            "Minkowski and flat-FLRW analytic controls",
        ],
        "not_implemented": [
            "metric-to-Ricci differential operator",
            "lapse and shift gauge evolution",
            "spatial-metric and extrinsic-curvature evolution",
            "constraint propagation or damping",
            "well-posedness and convergence",
            "Topic 13 stress-energy projection wiring",
            "physical observable validation",
        ],
        "claim_boundary": (
            "curved 3+1 ADM constraint evaluation interface only; not a metric "
            "evolution solver, Einstein-equation derivation, or GR validation"
        ),
    }


__all__ = [
    "ADM_CONSTRAINT_INTERFACE_STATUS",
    "ADMGeometryState",
    "ADMMatterProjection",
    "ADMConstraintResult",
    "evaluate_adm_constraints",
    "minkowski_adm_control",
    "flat_flrw_adm_control",
    "adm_constraint_contract",
]
