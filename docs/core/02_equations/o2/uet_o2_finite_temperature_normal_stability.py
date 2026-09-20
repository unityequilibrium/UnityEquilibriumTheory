"""One-sided Hartree normal-branch stability boundary for Topic 13.

This module uses the already declared natural-unit Hartree gap equation to
locate the point where the normal-branch curvature
``r_T = M^2 - Z*mu^2`` vanishes.  It is a stability boundary diagnostic, not a
renormalized condensed-phase solution or a physical finite-temperature phase
transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_self_energy import (
    _thermal_tadpole_and_derivative,
)


@dataclass(frozen=True)
class UETO2HartreeNormalStabilityBoundary:
    """One-sided normal-to-condensed stability boundary in natural units."""

    temperature: float
    space_response: float
    critical_chemical_potential: float
    critical_dressed_mass_sq: float
    base_mass_sq: float
    thermal_tadpole: float
    thermal_self_energy: float
    critical_residual: float
    bose_domain_margin: float
    lower_probe_residual: float
    upper_probe_residual: float
    momentum_cutoff: float
    quadrature_order: int
    iterations: int
    component_count: int = 2
    unit_lane: str = "natural"
    vacuum_counterterm_included: bool = False
    condensed_branch_included: bool = False
    physical_kubo_coefficient_included: bool = False
    data_role: str = "ACTION_DERIVED_HARTREE_ONE_SIDED_STABILITY_BOUNDARY"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _critical_residual(
    chemical_potential: float,
    temperature: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int,
    cutoff_factor: float,
    component_count: int,
) -> tuple[float, float, float, float, float]:
    """Return ``(gap residual, M^2, tadpole, self-energy, cutoff)`` at ``r_T=0``."""

    mu = _positive(chemical_potential, "chemical_potential")
    temperature = _positive(temperature, "temperature")
    phi = _finite(space_response, "space_response")
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    coupling = _positive(config.matter.matter_quartic, "matter_quartic")
    if z <= 1.0:
        raise ValueError(
            "the declared E_k+-mu thermal determinant needs matter_kinetic > 1 "
            "for a regular one-sided r_T=0 boundary"
        )
    base_mass_sq = float(effective_mass_sq(phi, config))
    if base_mass_sq <= 0.0:
        raise ValueError("normal stability boundary requires positive base mass-squared")
    cutoff = max(
        _positive(cutoff_factor, "cutoff_factor") * temperature,
        _positive(cutoff_factor, "cutoff_factor") * mu,
        _positive(cutoff_factor, "cutoff_factor") * sqrt(base_mass_sq),
        1.0,
    )
    critical_mass_sq = z * mu * mu
    tadpole, _ = _thermal_tadpole_and_derivative(
        critical_mass_sq,
        temperature,
        mu,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    self_energy = coupling * (component_count + 2) * tadpole
    residual = critical_mass_sq - base_mass_sq - self_energy
    bose_domain_margin = critical_mass_sq - mu * mu
    return (
        float(residual),
        float(critical_mass_sq),
        float(tadpole),
        float(self_energy),
        float(cutoff),
    )


def normal_stability_boundary_residual(
    chemical_potential: float,
    temperature: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
    component_count: int = 2,
) -> float:
    """Return the Hartree gap residual evaluated on ``M^2=Z*mu^2``."""

    return _critical_residual(
        chemical_potential,
        temperature,
        space_response,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )[0]


def uet_o2_hartree_normal_stability_boundary(
    temperature: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
    component_count: int = 2,
    residual_tolerance: float = 1.0e-12,
    max_iterations: int = 256,
) -> UETO2HartreeNormalStabilityBoundary:
    """Solve the one-sided Hartree normal stability condition.

    The returned root satisfies the existing normal Hartree gap equation at
    ``M^2=Z*mu_c^2``.  The condensed branch is deliberately not evaluated.
    """

    temperature = _positive(temperature, "temperature")
    phi = _finite(space_response, "space_response")
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    if z <= 1.0:
        raise ValueError(
            "the declared E_k+-mu thermal determinant needs matter_kinetic > 1 "
            "for a regular one-sided r_T=0 boundary"
        )
    base_mass_sq = float(effective_mass_sq(phi, config))
    if base_mass_sq <= 0.0:
        raise ValueError("normal stability boundary requires positive base mass-squared")
    if isinstance(component_count, bool) or int(component_count) != component_count:
        raise ValueError("component_count must be an integer")
    component_count = int(component_count)
    if component_count < 1:
        raise ValueError("component_count must be positive")
    residual_tolerance = _positive(residual_tolerance, "residual_tolerance")
    if isinstance(max_iterations, bool) or int(max_iterations) != max_iterations:
        raise ValueError("max_iterations must be an integer")
    max_iterations = int(max_iterations)
    if max_iterations < 16:
        raise ValueError("max_iterations must be >= 16")

    lower = max(1.0e-8, sqrt(base_mass_sq / z) * 1.0e-3)
    lower_value = normal_stability_boundary_residual(
        lower,
        temperature,
        phi,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )
    for _ in range(max_iterations):
        if lower_value < 0.0:
            break
        lower *= 0.5
        lower_value = normal_stability_boundary_residual(
            lower,
            temperature,
            phi,
            config,
            quadrature_order=quadrature_order,
            cutoff_factor=cutoff_factor,
            component_count=component_count,
        )
    else:
        raise RuntimeError("failed to bracket the stable side of the Hartree boundary")

    upper = max(1.0, sqrt(base_mass_sq / z) + 1.0)
    upper_value = normal_stability_boundary_residual(
        upper,
        temperature,
        phi,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )
    for _ in range(max_iterations):
        if upper_value > 0.0:
            break
        upper *= 2.0
        upper_value = normal_stability_boundary_residual(
            upper,
            temperature,
            phi,
            config,
            quadrature_order=quadrature_order,
            cutoff_factor=cutoff_factor,
            component_count=component_count,
        )
    else:
        raise RuntimeError("failed to bracket the unstable side of the Hartree boundary")

    iterations = 0
    for iterations in range(1, max_iterations + 1):
        midpoint = 0.5 * (lower + upper)
        midpoint_value = normal_stability_boundary_residual(
            midpoint,
            temperature,
            phi,
            config,
            quadrature_order=quadrature_order,
            cutoff_factor=cutoff_factor,
            component_count=component_count,
        )
        if abs(midpoint_value) <= residual_tolerance:
            break
        if midpoint_value < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    else:
        raise RuntimeError("Hartree normal stability boundary did not converge")

    residual, mass_sq, tadpole, self_energy, cutoff = _critical_residual(
        midpoint,
        temperature,
        phi,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )
    lower_probe = normal_stability_boundary_residual(
        0.95 * midpoint,
        temperature,
        phi,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )
    upper_probe = normal_stability_boundary_residual(
        1.05 * midpoint,
        temperature,
        phi,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )
    values = (
        midpoint,
        mass_sq,
        base_mass_sq,
        tadpole,
        self_energy,
        residual,
        mass_sq - midpoint * midpoint,
        lower_probe,
        upper_probe,
        cutoff,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("Hartree stability boundary contains a non-finite value")
    if lower_probe >= 0.0 or upper_probe <= 0.0:
        raise FloatingPointError("Hartree stability boundary probe signs are unresolved")
    return UETO2HartreeNormalStabilityBoundary(
        temperature=temperature,
        space_response=phi,
        critical_chemical_potential=float(midpoint),
        critical_dressed_mass_sq=float(mass_sq),
        base_mass_sq=base_mass_sq,
        thermal_tadpole=float(tadpole),
        thermal_self_energy=float(self_energy),
        critical_residual=float(residual),
        bose_domain_margin=float(mass_sq - midpoint * midpoint),
        lower_probe_residual=float(lower_probe),
        upper_probe_residual=float(upper_probe),
        momentum_cutoff=float(cutoff),
        quadrature_order=int(quadrature_order),
        iterations=int(iterations),
        component_count=component_count,
    )


def uet_o2_hartree_normal_stability_contract() -> dict[str, Any]:
    """Return the boundary equations and explicit claim limits."""

    return {
        "status": "ACTION_DERIVED_HARTREE_NORMAL_ONE_SIDED_STABILITY_BOUNDARY",
        "equations": {
            "normal_gap": "M^2=m_eff(Phi)^2+(N+2)*lambda*I_T(M^2;T,mu)",
            "normal_curvature": "r_T=M^2-Z*mu^2",
            "critical_boundary": "r_T(mu_c,T,Phi)=0, hence M_c^2=Z*mu_c^2",
            "boundary_residual": "F(mu_c)=Z*mu_c^2-m_eff(Phi)^2-(N+2)*lambda*I_T(Z*mu_c^2;T,mu_c)",
            "one_sided_sign": "F(mu<mu_c)<0 gives a stable normal gap; F(mu>mu_c)>0 places the Hartree root below r_T=0",
        },
        "units": {
            "unit_lane": "natural",
            "T_mu_M": "natural energy",
            "r_T_mass_squared": "natural energy squared",
            "Phi": "natural action response field; not temperature",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "derivation_class": "action-derived one-sided Hartree stability-boundary root with quadrature convergence",
        "approximation": {
            "component_count": 2,
            "matter_kinetic_condition": "Z>1 under the currently declared E_k+-mu determinant convention",
            "vacuum_counterterm": "NOT_INCLUDED; use the separately declared subtraction scheme",
            "condensate_branch": "NOT_INCLUDED",
            "two_fluid_transport": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms_microscopic_match": "NOT_INCLUDED",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not charge density",
            "Phi": "effective action response variable; not temperature",
            "R_gen": "derived history trace only; not a state or feedback",
            "R_obs": "separate observer record; not part of the action state",
        },
        "data_role": "ACTION_DERIVED_INTERNAL_NO_EXTERNAL_CALIBRATION",
        "claim_boundary": "This closes only the one-sided natural-unit Hartree normal-branch stability boundary under the declared thermal determinant convention. It does not close a renormalized finite-temperature phase transition, the condensed branch, a complete two-fluid EOS, physical Kubo/SK/KMS transport, an SI Phi map, alpha_Phi_K, TTG validation, or global UET closure.",
    }


__all__ = [
    "UETO2HartreeNormalStabilityBoundary",
    "normal_stability_boundary_residual",
    "uet_o2_hartree_normal_stability_boundary",
    "uet_o2_hartree_normal_stability_contract",
]
