"""Lane-bounded stress-energy wiring for the curved 3+1 Core parent."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_curved_3p1_adm_evolution import ADMStressProjection
from docs.core.uet_curved_3p1_constraints import ADMMatterProjection
from docs.core.uet_curved_3p1_generalized_harmonic import (
    GHNonlinearParameters,
    GHNonlinearVacuumRHS,
    compute_nonlinear_vacuum_gh_rhs,
    derive_gh_kinematics,
)


CURVED_3P1_MATTER_WIRING_STATUS: Final[str] = (
    "CURVED_3P1_PRESCRIBED_STRESS_ENERGY_WIRING"
)
ORTHOGONALITY_TOLERANCE: Final[float] = 1.0e-10


def _finite_array(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _symmetric_metric(value: Any) -> np.ndarray:
    metric = _finite_array(value, "spacetime_metric")
    if metric.ndim < 2 or metric.shape[-2:] != (4, 4):
        raise ValueError("spacetime_metric must end in shape (4,4)")
    if not np.allclose(metric, np.swapaxes(metric, -1, -2), atol=1e-12, rtol=0.0):
        raise ValueError("spacetime_metric must be symmetric")
    eigenvalues = np.linalg.eigvalsh(metric)
    signature_ok = (
        (np.sum(eigenvalues < 0.0, axis=-1) == 1)
        & (np.sum(eigenvalues > 0.0, axis=-1) == 3)
    )
    if not np.all(signature_ok):
        raise ValueError("spacetime_metric must have Lorentz signature (-,+,+,+)")
    return metric


def _field(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite_array(value, name)
    if array.ndim == 0:
        return np.full(shape, float(array), dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    return array


def _vector4(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite_array(value, name)
    if array.shape != shape + (4,):
        raise ValueError(f"{name} must have shape {shape + (4,)}")
    return array


def _tensor4(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = _finite_array(value, name)
    if array.shape != shape + (4, 4):
        raise ValueError(f"{name} must have shape {shape + (4, 4)}")
    if not np.allclose(array, np.swapaxes(array, -1, -2), atol=1e-12, rtol=0.0):
        raise ValueError(f"{name} must be symmetric")
    return array


@dataclass(frozen=True)
class RelativisticFluidState:
    energy_density: Any
    pressure: Any
    four_velocity: Any
    heat_flux: Any | None = None
    anisotropic_stress: Any | None = None
    unit_lane: str = "natural"
    data_role: str = "DECLARED_INPUT"


@dataclass(frozen=True)
class CurvedMatterProjection:
    energy_density: np.ndarray
    momentum_density: np.ndarray
    spatial_stress: np.ndarray
    trace_spatial_stress: np.ndarray
    reconstruction_residual: float
    unit_lane: str

    def for_constraints(self) -> ADMMatterProjection:
        return ADMMatterProjection(self.energy_density, self.momentum_density)

    def for_evolution(self) -> ADMStressProjection:
        return ADMStressProjection(
            self.energy_density,
            self.momentum_density,
            self.spatial_stress,
        )


@dataclass(frozen=True)
class GHNonlinearMatterRHS:
    metric_rhs: np.ndarray
    normal_derivative_rhs: np.ndarray
    spatial_derivative_rhs: np.ndarray
    gauge_constraint: np.ndarray
    lowered_christoffel: np.ndarray
    matter_source_term: np.ndarray
    trace_reversed_stress_energy: np.ndarray
    vacuum_rhs: GHNonlinearVacuumRHS
    diagnostics: dict[str, Any]


def relativistic_fluid_stress_energy(
    spacetime_metric: Any,
    state: RelativisticFluidState,
) -> np.ndarray:
    """Return covariant T_ab for a dissipative relativistic fluid."""

    metric = _symmetric_metric(spacetime_metric)
    shape = metric.shape[:-2]
    inverse = np.linalg.inv(metric)
    energy = _field(state.energy_density, shape, "energy_density")
    pressure = _field(state.pressure, shape, "pressure")
    velocity = _vector4(state.four_velocity, shape, "four_velocity")
    velocity_cov = np.einsum("...ab,...b->...a", metric, velocity)
    norm = np.einsum("...a,...a->...", velocity_cov, velocity)
    if not np.allclose(norm, -1.0, atol=ORTHOGONALITY_TOLERANCE, rtol=0.0):
        raise ValueError("four_velocity must be future timelike and normalized to -1")
    if np.any(velocity[..., 0] <= 0.0):
        raise ValueError("four_velocity must be future directed")

    heat_flux = (
        np.zeros(shape + (4,), dtype=float)
        if state.heat_flux is None
        else _vector4(state.heat_flux, shape, "heat_flux")
    )
    heat_flux_cov = np.einsum("...ab,...b->...a", metric, heat_flux)
    heat_orthogonality = np.einsum(
        "...a,...a->...", velocity_cov, heat_flux
    )
    if np.max(np.abs(heat_orthogonality)) > ORTHOGONALITY_TOLERANCE:
        raise ValueError("heat_flux must be orthogonal to four_velocity")

    anisotropic = (
        np.zeros(shape + (4, 4), dtype=float)
        if state.anisotropic_stress is None
        else _tensor4(state.anisotropic_stress, shape, "anisotropic_stress")
    )
    anisotropic_orthogonality = np.einsum(
        "...a,...ab->...b", velocity, anisotropic
    )
    if np.max(np.abs(anisotropic_orthogonality)) > ORTHOGONALITY_TOLERANCE:
        raise ValueError(
            "anisotropic_stress must be orthogonal to four_velocity"
        )
    anisotropic_trace = np.einsum("...ab,...ab->...", inverse, anisotropic)
    if np.max(np.abs(anisotropic_trace)) > ORTHOGONALITY_TOLERANCE:
        raise ValueError("anisotropic_stress must be trace free")

    return np.asarray(
        (energy + pressure)[..., None, None]
        * np.einsum("...a,...b->...ab", velocity_cov, velocity_cov)
        + pressure[..., None, None] * metric
        + np.einsum("...a,...b->...ab", velocity_cov, heat_flux_cov)
        + np.einsum("...a,...b->...ab", heat_flux_cov, velocity_cov)
        + anisotropic,
        dtype=float,
    )


def project_stress_energy_3p1(
    spacetime_metric: Any,
    stress_energy_covariant: Any,
    *,
    unit_lane: str,
) -> CurvedMatterProjection:
    """Project T_ab into Eulerian rho, S_i, and S_ij."""

    metric = _symmetric_metric(spacetime_metric)
    shape = metric.shape[:-2]
    stress = _tensor4(stress_energy_covariant, shape, "stress_energy_covariant")
    kinematics = derive_gh_kinematics(metric)
    normal = kinematics.unit_normal
    normal_cov = kinematics.unit_normal_covector
    projector = np.eye(4) + np.einsum(
        "...a,...b->...ab", normal_cov, normal
    )
    rho = np.einsum("...a,...b,...ab->...", normal, normal, stress)
    normal_stress = np.einsum("...d,...cd->...c", normal, stress)
    momentum_cov = -np.einsum("...ac,...c->...a", projector, normal_stress)
    spatial_full = np.einsum(
        "...ac,...bd,...cd->...ab",
        projector,
        projector,
        stress,
    )
    momentum = momentum_cov[..., 1:]
    spatial_stress = spatial_full[..., 1:, 1:]
    spatial_inverse = np.linalg.inv(metric[..., 1:, 1:])
    stress_trace = np.einsum(
        "...ij,...ij->...", spatial_inverse, spatial_stress
    )
    reconstructed = (
        rho[..., None, None]
        * np.einsum("...a,...b->...ab", normal_cov, normal_cov)
        + np.einsum("...a,...b->...ab", normal_cov, momentum_cov)
        + np.einsum("...a,...b->...ab", momentum_cov, normal_cov)
        + spatial_full
    )
    return CurvedMatterProjection(
        energy_density=np.asarray(rho, dtype=float),
        momentum_density=np.asarray(momentum, dtype=float),
        spatial_stress=np.asarray(spatial_stress, dtype=float),
        trace_spatial_stress=np.asarray(stress_trace, dtype=float),
        reconstruction_residual=float(np.max(np.abs(reconstructed - stress))),
        unit_lane=unit_lane,
    )


def trace_reversed_stress_energy(
    spacetime_metric: Any,
    stress_energy_covariant: Any,
) -> np.ndarray:
    metric = _symmetric_metric(spacetime_metric)
    stress = _tensor4(
        stress_energy_covariant,
        metric.shape[:-2],
        "stress_energy_covariant",
    )
    inverse = np.linalg.inv(metric)
    trace = np.einsum("...ab,...ab->...", inverse, stress)
    return stress - 0.5 * metric * trace[..., None, None]


def compute_nonlinear_prescribed_matter_gh_rhs(
    spacetime_metric: Any,
    normal_derivative: Any,
    spatial_derivative: Any,
    gauge_source: Any,
    gauge_source_covariant_derivative: Any,
    spacing: Any,
    stress_energy_covariant: Any,
    *,
    einstein_coupling: float,
    matter_unit_lane: str,
    parameters: GHNonlinearParameters = GHNonlinearParameters(),
) -> GHNonlinearMatterRHS:
    """Add a prescribed T_ab source to the nonlinear GH metric RHS."""

    coupling = float(einstein_coupling)
    if not isfinite(coupling) or coupling <= 0.0:
        raise ValueError("einstein_coupling must be finite and positive")
    vacuum = compute_nonlinear_vacuum_gh_rhs(
        spacetime_metric,
        normal_derivative,
        spatial_derivative,
        gauge_source,
        gauge_source_covariant_derivative,
        spacing,
        parameters,
    )
    metric = _symmetric_metric(spacetime_metric)
    reversed_stress = trace_reversed_stress_energy(metric, stress_energy_covariant)
    lapse = derive_gh_kinematics(metric).lapse
    matter_source = -2.0 * coupling * lapse[..., None, None] * reversed_stress
    diagnostics = {
        **vacuum.diagnostics,
        "matter_source": "PRESCRIBED_COVARIANT_STRESS_ENERGY",
        "matter_unit_lane": matter_unit_lane,
        "einstein_coupling": coupling,
        "matter_source_equation": "-2*alpha*kappa_E*(T_ab-psi_ab*T/2)",
        "matter_state_evolution": False,
        "stress_energy_conservation_evolved": False,
        "field_clipping": False,
        "parameter_fitting": False,
    }
    return GHNonlinearMatterRHS(
        metric_rhs=vacuum.metric_rhs,
        normal_derivative_rhs=vacuum.normal_derivative_rhs + matter_source,
        spatial_derivative_rhs=vacuum.spatial_derivative_rhs,
        gauge_constraint=vacuum.gauge_constraint,
        lowered_christoffel=vacuum.lowered_christoffel,
        matter_source_term=np.asarray(matter_source, dtype=float),
        trace_reversed_stress_energy=np.asarray(reversed_stress, dtype=float),
        vacuum_rhs=vacuum,
        diagnostics=diagnostics,
    )


def curved_3p1_matter_wiring_contract() -> dict[str, Any]:
    return {
        "status": CURVED_3P1_MATTER_WIRING_STATUS,
        "equations": {
            "fluid_stress_energy": "T_ab=(epsilon+p)u_a*u_b+p*psi_ab+u_a*q_b+u_b*q_a+pi_ab",
            "adm_energy": "rho=n^a*n^b*T_ab",
            "adm_momentum": "S_a=-gamma_a^c*n^d*T_cd",
            "adm_stress": "S_ab=gamma_a^c*gamma_b^d*T_cd",
            "gh_matter_source": "d_t Pi_ab|matter=-2*alpha*kappa_E*(T_ab-psi_ab*T/2)",
        },
        "ontology": {
            "C": "excluded collective coordinate; not stress-energy",
            "Phi": "excluded effective response variable; not metric or energy density",
            "R_gen": "excluded derived history trace; no backreaction",
            "R_obs": "excluded observer record",
            "psi_ab": "standard Lorentz metric",
            "T_ab": "independently declared lane-specific stress-energy tensor",
        },
        "unit_lanes": {
            "natural": "epsilon, p, q, and pi share one natural energy-density lane",
            "SI_projection": "epsilon, p, q, and pi are in J m^-3",
            "GH_source": "kappa_E*T_ab has inverse-coordinate-length squared units",
        },
        "included": [
            "relativistic fluid stress-energy construction",
            "ADM Eulerian energy, momentum, and spatial-stress projections",
            "trace-reversed prescribed GH matter source",
            "vacuum null source",
            "natural-to-SI multiplicative scale compatibility",
        ],
        "not_implemented": [
            "matter-state time evolution",
            "stress-energy conservation propagation",
            "self-consistent two-fluid curved transport",
            "numerical SI Einstein coupling provenance",
            "constraint-preserving non-periodic boundaries",
            "detector observable mapping",
        ],
        "claim_boundary": (
            "prescribed lane-specific stress-energy construction and projection only; "
            "not a self-consistent matter-coupled spacetime solution, Einstein-equation "
            "derivation, Gravity validation, or global UET closure"
        ),
    }


__all__ = [
    "CURVED_3P1_MATTER_WIRING_STATUS",
    "RelativisticFluidState",
    "CurvedMatterProjection",
    "GHNonlinearMatterRHS",
    "relativistic_fluid_stress_energy",
    "project_stress_energy_3p1",
    "trace_reversed_stress_energy",
    "compute_nonlinear_prescribed_matter_gh_rhs",
    "curved_3p1_matter_wiring_contract",
]
