"""Action-derived thermal response curvature on the O(2) normal branch.

The existing normal one-loop lane supplies the thermal matter determinant and
the linear action map ``m_eff^2(Phi)``.  This module differentiates that same
determinant twice with respect to the natural-unit response field and once
with respect to temperature.  The result is a natural-unit response
curvature/slope, not the normalized Topic 13 ``beta_T13`` and not an SI
observable calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_covariant_response import response_potential_hessian
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)


@dataclass(frozen=True)
class O2NormalResponseCurvatureState:
    """Thermal response curvature and temperature slope in natural units."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    dm_eff_sq_dphi: float
    bare_response_curvature: float
    thermal_response_curvature: float
    total_response_curvature: float
    thermal_response_curvature_temperature_derivative: float
    beta_action_natural: float
    momentum_cutoff: float
    quadrature_order: int
    unit_lane: str = "natural"
    normal_branch: bool = True
    thermal_only_loop: bool = True
    vacuum_counterterm_included: bool = False
    condensate_contribution_included: bool = False
    physical_beta_t13_identified: bool = False
    physical_si_mapping_included: bool = False
    data_role: str = "ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE_NOT_SI_BETA"


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


def _bose_occupation(argument: np.ndarray) -> np.ndarray:
    if np.any(argument <= 0.0) or not np.all(np.isfinite(argument)):
        raise ValueError("normal thermal Bose arguments must be positive and finite")
    clipped = np.asarray(argument, dtype=float)
    result = np.empty_like(clipped)
    high = clipped > 50.0
    result[high] = np.exp(-clipped[high]) / (1.0 - np.exp(-clipped[high]))
    result[~high] = 1.0 / np.expm1(clipped[~high])
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
    effective_mass: float,
    cutoff_factor: float,
) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    return max(
        factor * temperature,
        factor * abs(chemical_potential),
        factor * effective_mass,
        1.0,
    )


def uet_o2_normal_response_curvature_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 50.0,
) -> O2NormalResponseCurvatureState:
    """Evaluate thermal response curvature and its temperature derivative.

    The normal thermal grand potential is differentiated through the linear
    action mass map.  The response-sector bare curvature is the declared
    conservative response potential Hessian multiplied by ``epsilon_nc``.
    Vacuum/zero-point terms and condensate contributions are not inferred.
    """

    temperature = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(phi, config))
    if mass_sq <= 0.0:
        raise ValueError("response curvature lane requires positive effective mass squared")
    z = float(config.matter.matter_kinetic)
    if z * mu * mu >= mass_sq:
        raise ValueError("response curvature lane requires the normal branch")
    mass = sqrt(mass_sq)
    cutoff = _cutoff(temperature, mu, mass, cutoff_factor)
    momenta, weights = _quadrature(int(quadrature_order), cutoff)
    energy = np.sqrt(momenta * momenta + mass_sq)
    measure = momenta * momenta / (2.0 * pi**2)
    x_minus = (energy - mu) / temperature
    x_plus = (energy + mu) / temperature
    n_minus = _bose_occupation(x_minus)
    n_plus = _bose_occupation(x_plus)
    a_minus = n_minus * (1.0 + n_minus)
    a_plus = n_plus * (1.0 + n_plus)

    # s_M = partial Omega_T / partial(m_eff^2), and its mass derivative.
    scalar_mass_derivative = -0.25 * np.sum(
        weights
        * measure
        * (
            (a_minus + a_plus) / (temperature * energy**2)
            + (n_minus + n_plus) / energy**3
        )
    )
    dn_minus_dT = a_minus * (energy - mu) / temperature**2
    dn_plus_dT = a_plus * (energy + mu) / temperature**2
    da_minus_dT = (1.0 + 2.0 * n_minus) * dn_minus_dT
    da_plus_dT = (1.0 + 2.0 * n_plus) * dn_plus_dT
    integrand_temperature_derivative = (
        (da_minus_dT + da_plus_dT) / (temperature * energy**2)
        - (a_minus + a_plus) / (temperature**2 * energy**2)
        + (dn_minus_dT + dn_plus_dT) / energy**3
    )
    scalar_mass_derivative_temperature = -0.25 * np.sum(
        weights * measure * integrand_temperature_derivative
    )

    dm_eff_sq_dphi = float(
        -config.response.epsilon_nc * config.matter.response_coupling
    )
    thermal_curvature = dm_eff_sq_dphi**2 * scalar_mass_derivative
    thermal_curvature_temperature_derivative = (
        dm_eff_sq_dphi**2 * scalar_mass_derivative_temperature
    )
    bare_curvature = float(
        config.response.epsilon_nc
        * response_potential_hessian(phi, config.response)
    )
    total_curvature = bare_curvature + thermal_curvature
    beta_action_natural = temperature * thermal_curvature_temperature_derivative
    values = (
        mass_sq,
        dm_eff_sq_dphi,
        bare_curvature,
        thermal_curvature,
        total_curvature,
        thermal_curvature_temperature_derivative,
        beta_action_natural,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("normal response curvature produced a non-finite value")
    return O2NormalResponseCurvatureState(
        temperature=temperature,
        chemical_potential=mu,
        space_response=phi,
        effective_mass_sq=mass_sq,
        dm_eff_sq_dphi=dm_eff_sq_dphi,
        bare_response_curvature=bare_curvature,
        thermal_response_curvature=float(thermal_curvature),
        total_response_curvature=float(total_curvature),
        thermal_response_curvature_temperature_derivative=float(
            thermal_curvature_temperature_derivative
        ),
        beta_action_natural=float(beta_action_natural),
        momentum_cutoff=cutoff,
        quadrature_order=int(quadrature_order),
    )


def uet_o2_normal_response_curvature_contract() -> dict[str, Any]:
    """Return the action-derived scope and explicit non-identification rules."""

    return {
        "status": "ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE",
        "equations": {
            "mass_map": "m_eff(Phi)^2=m^2-epsilon_nc*h*(Phi-Phi_*)",
            "normal_domain": "Z*mu^2 < m_eff(Phi)^2",
            "thermal_grand_potential": "Omega_T=T integral sum_{s=+,-} log(1-exp(-(E_k+s*mu)/T)) d^3k/(2*pi)^3",
            "response_curvature": "kappa_Phi^T=partial_Phi^2 Omega_T=(partial_Phi m_eff^2)^2*partial_(m_eff^2) s_M",
            "scalar_mass_derivative": "partial_(m_eff^2) s_M=-1/4 integral [A_sum/(T*E_k^2)+n_sum/E_k^3] d^3k/(2*pi)^3",
            "temperature_slope": "beta_action_natural=T*partial_T kappa_Phi^T",
            "total_curvature": "kappa_Phi=epsilon_nc*U''(Phi)+kappa_Phi^T",
        },
        "units": {
            "unit_lane": "natural",
            "Phi": "natural response field with mass dimension one in the covariant action",
            "kappa_Phi": "natural mass dimension two",
            "partial_T_kappa_Phi": "natural mass dimension one",
            "beta_action_natural": "natural mass dimension two",
            "beta_T13": "not identified; its normalized K^-1 contract remains separate",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "scope": {
            "background": "homogeneous normal O(2) branch at fixed chemical potential and Phi",
            "loop_content": "thermal one-loop determinant only",
            "bare_response_sector": "declared conservative response potential Hessian",
            "vacuum_counterterm": "NOT_INCLUDED",
            "condensate_branch": "NOT_INCLUDED",
            "normal_two_fluid_completion": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "not identified with charge density or transport coefficient",
            "Phi": "natural action response field; not temperature or metric",
            "R_gen": "derived history trace only; not used as state or feedback",
            "R_obs": "not included in this action-derived lane",
        },
        "data_role": "ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE_NOT_SI_BETA",
        "claim_boundary": "This derives a natural-unit thermal response curvature and temperature slope on the normal one-loop branch. It does not identify that slope with beta_T13, provide a renormalized finite-temperature action, close the condensate/normal two-fluid sector, supply physical Kubo coefficients, create an SI Phi map, calibrate alpha_Phi_K, validate TTG data, or close Full Topic 13.",
    }


__all__ = [
    "O2NormalResponseCurvatureState",
    "uet_o2_normal_response_curvature_state",
    "uet_o2_normal_response_curvature_contract",
]
