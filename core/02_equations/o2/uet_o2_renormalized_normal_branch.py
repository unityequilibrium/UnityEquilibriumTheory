"""Renormalized normal-branch one-loop lane in natural units.

The existing normal branch keeps only the thermal determinant.  This module
adds an explicit BPHZ-style Taylor subtraction in the mass-squared variable at
the declared response reference point.  The subtraction is a scheme contract,
not a claim that the physical finite-temperature action or its microscopic
counterterms have been matched.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_covariant_response import (
    response_potential,
    response_potential_hessian,
)
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_normal_response_curvature import (
    uet_o2_normal_response_curvature_state,
)
from docs.core.uet_o2_one_loop_normal_branch import (
    uet_o2_one_loop_normal_state,
)


@dataclass(frozen=True)
class UETO2RenormalizedNormalState:
    """Thermal plus scheme-subtracted normal one-loop state."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    reference_mass_sq: float
    vacuum_grand_potential: float
    vacuum_mass_derivative: float
    vacuum_mass_second_derivative: float
    thermal_grand_potential: float
    total_grand_potential: float
    pressure: float
    charge_density: float
    entropy_density: float
    energy_density: float
    vacuum_response_curvature: float
    total_response_curvature: float
    momentum_cutoff: float
    quadrature_order: int
    unit_lane: str = "natural"
    normal_branch: bool = True
    vacuum_counterterm_included: bool = True
    vacuum_subtraction_order: int = 2
    condensate_contribution_included: bool = False
    normal_two_fluid_completion: bool = False
    physical_kubo_coefficient_included: bool = False
    physical_si_mapping_included: bool = False
    data_role: str = "ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME_NOT_PHYSICAL"


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    return momenta, scaled_weights


def _cutoff(
    temperature: float,
    chemical_potential: float,
    mass_sq: float,
    reference_mass_sq: float,
    cutoff_factor: float,
) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    return max(
        factor * temperature,
        factor * abs(chemical_potential),
        factor * sqrt(mass_sq),
        factor * sqrt(reference_mass_sq),
        1.0,
    )


def _vacuum_terms(
    mass_sq: float,
    reference_mass_sq: float,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float, float]:
    """Return subtracted vacuum potential and its first two mass derivatives.

    For ``x=m_eff^2`` and ``x0=m_ref^2`` the integrand is

    ``E(x)-E(x0)-(x-x0)E'(x0)-1/2*(x-x0)^2 E''(x0)``.

    The Taylor subtraction removes the quadratic, logarithmic, and constant
    ultraviolet pieces of the zero-point integral in this declared scheme.
    """

    momenta, weights = _quadrature(quadrature_order, cutoff)
    energy = np.sqrt(momenta * momenta + mass_sq)
    reference_energy = np.sqrt(momenta * momenta + reference_mass_sq)
    delta = mass_sq - reference_mass_sq
    measure = momenta * momenta / (2.0 * pi**2)
    potential_integrand = (
        energy
        - reference_energy
        - delta / (2.0 * reference_energy)
        + delta**2 / (8.0 * reference_energy**3)
    )
    first_integrand = (
        1.0 / (2.0 * energy)
        - 1.0 / (2.0 * reference_energy)
        + delta / (4.0 * reference_energy**3)
    )
    second_integrand = -1.0 / (4.0 * energy**3) + 1.0 / (4.0 * reference_energy**3)
    values = tuple(
        float(np.sum(weights * measure * integrand))
        for integrand in (potential_integrand, first_integrand, second_integrand)
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("renormalized vacuum terms are not finite")
    return values


def uet_o2_renormalized_normal_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 50.0,
) -> UETO2RenormalizedNormalState:
    """Evaluate the scheme-subtracted normal one-loop state."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(space_response, config))
    reference_mass_sq = float(effective_mass_sq(config.response.phi_equilibrium, config))
    if mass_sq <= 0.0 or reference_mass_sq <= 0.0:
        raise ValueError("renormalized normal lane requires positive mass-squared values")
    if config.matter.matter_kinetic * chemical_potential**2 >= mass_sq:
        raise ValueError("renormalized normal lane requires the normal branch")
    cutoff = _cutoff(
        temperature,
        chemical_potential,
        mass_sq,
        reference_mass_sq,
        cutoff_factor,
    )
    vacuum, vacuum_mass_derivative, vacuum_mass_second_derivative = _vacuum_terms(
        mass_sq,
        reference_mass_sq,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    thermal = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
    )
    curvature = uet_o2_normal_response_curvature_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
    )
    dm_eff_sq_dphi = float(
        -config.response.epsilon_nc * config.matter.response_coupling
    )
    vacuum_response_curvature = dm_eff_sq_dphi**2 * vacuum_mass_second_derivative
    total_response_curvature = (
        float(config.response.epsilon_nc * response_potential_hessian(space_response, config.response))
        + curvature.thermal_response_curvature
        + vacuum_response_curvature
    )
    total_grand_potential = vacuum + thermal.matter_grand_potential + thermal.one_loop_thermal_grand_potential
    pressure = -total_grand_potential
    charge_density = thermal.charge_density
    entropy_density = thermal.entropy_density
    energy_density = -pressure + temperature * entropy_density + chemical_potential * charge_density
    values = (
        vacuum,
        vacuum_mass_derivative,
        vacuum_mass_second_derivative,
        thermal.charge_density,
        entropy_density,
        energy_density,
        vacuum_response_curvature,
        total_response_curvature,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("renormalized normal state contains a non-finite value")
    return UETO2RenormalizedNormalState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass_sq=mass_sq,
        reference_mass_sq=reference_mass_sq,
        vacuum_grand_potential=vacuum,
        vacuum_mass_derivative=vacuum_mass_derivative,
        vacuum_mass_second_derivative=vacuum_mass_second_derivative,
        thermal_grand_potential=thermal.one_loop_thermal_grand_potential,
        total_grand_potential=total_grand_potential,
        pressure=pressure,
        charge_density=charge_density,
        entropy_density=entropy_density,
        energy_density=energy_density,
        vacuum_response_curvature=float(vacuum_response_curvature),
        total_response_curvature=float(total_response_curvature),
        momentum_cutoff=cutoff,
        quadrature_order=int(quadrature_order),
    )


def uet_o2_renormalized_normal_contract() -> dict[str, Any]:
    """Return the declared subtraction scheme and its physical boundaries."""

    return {
        "status": "ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME",
        "equations": {
            "reference": "m_ref^2=m_eff(Phi_*)^2",
            "vacuum_subtraction": "V_vac^R(x)=integral[E(x)-E(x0)-(x-x0)E'(x0)-1/2*(x-x0)^2 E''(x0)] d^3k/(2*pi)^3",
            "conditions": "V_vac^R(x0)=partial_x V_vac^R(x0)=partial_x^2 V_vac^R(x0)=0",
            "total_grand_potential": "Omega_R=V_vac^R+Omega_N^(1,T)",
            "response_curvature": "kappa_Phi^R=epsilon_nc U''(Phi)+kappa_Phi^T+(partial_Phi m_eff^2)^2 partial_x^2 V_vac^R",
        },
        "units": {
            "unit_lane": "natural",
            "vacuum_grand_potential": "natural energy density",
            "mass_derivatives": "natural derivative with respect to mass-squared",
            "response_curvature": "natural mass dimension two",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "renormalization_scheme": {
            "name": "mass-squared Taylor subtraction at Phi_*",
            "subtraction_order": 2,
            "reference_point": "Phi=Phi_* = response.phi_equilibrium",
            "finite_counterterm_origin": "declared scheme condition, not external measurement",
            "cutoff_role": "numerical quadrature regulator; convergence is audited",
        },
        "scope": {
            "normal_branch": "Z*mu^2 < m_eff(Phi)^2",
            "thermal_loop": "complex O(2) normal determinant",
            "condensate_branch": "NOT_INCLUDED",
            "interacting_thermal_self_energy": "NOT_INCLUDED",
            "normal_two_fluid": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "not identified with charge density or mass",
            "Phi": "natural action response field; not temperature",
            "R_gen": "derived history trace only; not a state or feedback",
            "R_obs": "separate observer record; not included",
        },
        "data_role": "ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME_NOT_PHYSICAL",
        "claim_boundary": "This closes a declared natural-unit subtraction scheme for the normal one-loop vacuum plus thermal determinant. It does not establish the unique physical renormalization scheme, interacting finite-temperature self-energy, condensate/two-fluid EOS, physical Kubo coefficients, microscopic SK/KMS matching, entropy production, SI Phi mapping, alpha_Phi_K, or external validation.",
    }


__all__ = [
    "UETO2RenormalizedNormalState",
    "uet_o2_renormalized_normal_state",
    "uet_o2_renormalized_normal_contract",
]
