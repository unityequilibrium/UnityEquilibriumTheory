"""Analytic GR correspondence controls for the UET parent contract.

These helpers provide known tensor inputs and weak-field identities.  They do
not compute curvature from a metric and are not a curved-spacetime solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

import numpy as np


GR_CORRESPONDENCE_STATUS = "ANALYTIC_TENSOR_INPUT_CONTROLS_V1"


@dataclass(frozen=True)
class GRBenchmarkRecord:
    benchmark_id: str
    metric: np.ndarray
    einstein_tensor: np.ndarray
    stress_energy: np.ndarray
    cosmological_constant: float
    kappa_e: float
    residual: np.ndarray
    diagnostics: Mapping[str, Any]


def _record(benchmark_id: str, metric: np.ndarray, einstein: np.ndarray, stress: np.ndarray, cosmological_constant: float, kappa_e: float, diagnostics: Mapping[str, Any]) -> GRBenchmarkRecord:
    residual = einstein + cosmological_constant * metric - kappa_e * stress
    return GRBenchmarkRecord(benchmark_id, metric, einstein, stress, cosmological_constant, kappa_e, residual, diagnostics)


def minkowski_null_control(kappa_e: float = 1.0) -> GRBenchmarkRecord:
    metric = np.diag([-1.0, 1.0, 1.0, 1.0])
    zero = np.zeros((4, 4))
    return _record("minkowski_null", metric, zero, zero, 0.0, kappa_e, {"curvature_computed_from_metric": False, "analytic_identity": True})


def flat_flrw_control(scale_factor: float, hubble: float, hubble_rate: float, kappa_e: float = 1.0, cosmological_constant: float = 0.0) -> GRBenchmarkRecord:
    for value, name in ((scale_factor, "scale_factor"), (kappa_e, "kappa_e")):
        if not isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and positive")
    if not isfinite(hubble) or not isfinite(hubble_rate) or not isfinite(cosmological_constant):
        raise ValueError("FLRW rates and cosmological constant must be finite")
    a2 = scale_factor ** 2
    metric = np.diag([-1.0, a2, a2, a2])
    einstein = np.diag([3.0 * hubble ** 2, -(2.0 * hubble_rate + 3.0 * hubble ** 2) * a2, -(2.0 * hubble_rate + 3.0 * hubble ** 2) * a2, -(2.0 * hubble_rate + 3.0 * hubble ** 2) * a2])
    rho = (3.0 * hubble ** 2 - cosmological_constant) / kappa_e
    pressure = (-(2.0 * hubble_rate + 3.0 * hubble ** 2) + cosmological_constant) / kappa_e
    stress = np.diag([rho, pressure * a2, pressure * a2, pressure * a2])
    return _record("flat_flrw_perfect_fluid", metric, einstein, stress, cosmological_constant, kappa_e, {"curvature_computed_from_metric": False, "analytic_tensor_formula": True, "rho": rho, "pressure": pressure})


def schwarzschild_exterior_null_control(radius: float, mass: float, newton_g: float = 1.0, theta: float = np.pi / 2.0, kappa_e: float = 1.0) -> GRBenchmarkRecord:
    if not all(isfinite(value) and value > 0.0 for value in (radius, mass, newton_g, kappa_e)):
        raise ValueError("radius, mass, G, and kappa_e must be finite and positive")
    schwarzschild_radius = 2.0 * newton_g * mass
    if radius <= schwarzschild_radius:
        raise ValueError("control point must lie outside the Schwarzschild radius")
    factor = 1.0 - schwarzschild_radius / radius
    metric = np.diag([-factor, 1.0 / factor, radius ** 2, radius ** 2 * np.sin(theta) ** 2])
    zero = np.zeros((4, 4))
    return _record("schwarzschild_exterior_vacuum", metric, zero, zero, 0.0, kappa_e, {"curvature_computed_from_metric": False, "einstein_tensor": "analytic vacuum input", "coordinate_chart": "Schwarzschild", "outside_horizon": True})


def newtonian_poisson_residual(laplacian_potential: Any, mass_density: Any, newton_g: float) -> np.ndarray:
    laplacian = np.asarray(laplacian_potential, dtype=float)
    density = np.asarray(mass_density, dtype=float)
    if laplacian.shape != density.shape or not np.all(np.isfinite(laplacian)) or not np.all(np.isfinite(density)):
        raise ValueError("laplacian potential and density must be aligned finite arrays")
    if not isfinite(newton_g) or newton_g <= 0.0 or np.min(density) < 0.0:
        raise ValueError("G must be positive and density non-negative")
    return laplacian - 4.0 * np.pi * newton_g * density


def gr_correspondence_contract() -> dict[str, Any]:
    return {
        "status": GR_CORRESPONDENCE_STATUS,
        "controls": ["Minkowski null", "flat FLRW perfect fluid", "Schwarzschild exterior vacuum", "Newtonian Poisson"],
        "curvature_from_metric": "NOT_IMPLEMENTED",
        "gauge_invariant_numerical_observables": "NOT_IMPLEMENTED",
        "constraint_evolution": "NOT_IMPLEMENTED",
        "nonzero_phi_comparison": "available only as algebraic parent formula evaluation",
        "claim_boundary": "analytic tensor-input correspondence, not curved numerical GR validation",
    }


__all__ = ["GR_CORRESPONDENCE_STATUS", "GRBenchmarkRecord", "minkowski_null_control", "flat_flrw_control", "schwarzschild_exterior_null_control", "newtonian_poisson_residual", "gr_correspondence_contract"]
