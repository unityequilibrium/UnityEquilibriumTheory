"""Equilibrium thermodynamics for the declared O(2) Hartree normal branch.

The module adds the stationary thermal 2PI/Hartree functional around the
finite-temperature self-energy lane.  It is intentionally limited to the
equilibrium normal branch in natural units: the vacuum subtraction,
condensate/two-fluid sector, physical Kubo coefficients, and SI mapping stay
outside this contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_self_energy import (
    uet_o2_finite_temperature_self_energy_state,
)


@dataclass(frozen=True)
class UETO2HartreeThermodynamicState:
    """Stationary equilibrium thermodynamics in the Hartree normal lane."""

    temperature: float
    chemical_potential: float
    space_response: float
    base_mass_sq: float
    dressed_mass_sq: float
    thermal_tadpole: float
    one_loop_pressure: float
    double_bubble_pressure: float
    pressure: float
    charge_density: float
    entropy_density: float
    energy_density: float
    charge_susceptibility: float
    heat_capacity_at_mu: float
    gap_residual: float
    pressure_stationarity_residual: float
    momentum_cutoff: float
    quadrature_order: int
    unit_lane: str = "natural"
    equilibrium_normal_branch: bool = True
    vacuum_counterterm_included: bool = False
    condensate_contribution_included: bool = False
    physical_kubo_coefficient_included: bool = False
    physical_si_mapping_included: bool = False
    data_role: str = "ACTION_DERIVED_HARTREE_EQUILIBRIUM_NOT_PHYSICAL_TRANSPORT"


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


def _bose(argument: np.ndarray) -> np.ndarray:
    values = np.asarray(argument, dtype=float)
    if np.any(values <= 0.0) or not np.all(np.isfinite(values)):
        raise ValueError("Bose occupation requires finite positive arguments")
    result = np.empty_like(values)
    high = values > 50.0
    result[high] = np.exp(-values[high])
    result[~high] = 1.0 / np.expm1(values[~high])
    return result


def _bose_log(argument: np.ndarray) -> np.ndarray:
    values = np.asarray(argument, dtype=float)
    if np.any(values <= 0.0) or not np.all(np.isfinite(values)):
        raise ValueError("Bose logarithm requires finite positive arguments")
    result = np.empty_like(values)
    high = values > 50.0
    result[high] = np.exp(-values[high])
    result[~high] = -np.log(-np.expm1(-values[~high]))
    return result


def _thermal_one_loop_state(
    mass_sq: float,
    temperature: float,
    chemical_potential: float,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float, float, float, float, float]:
    """Return p, n, s, epsilon, chi, and I_T for a dressed mass."""

    mass_sq = _positive(mass_sq, "mass_sq")
    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) >= sqrt(mass_sq):
        raise ValueError("thermal normal state requires |chemical_potential| < mass")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 32:
        raise ValueError("quadrature_order must be >= 32")
    cutoff = _positive(cutoff, "cutoff")
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    momenta = 0.5 * cutoff * (nodes + 1.0)
    weights = 0.5 * cutoff * weights
    energy = np.sqrt(momenta * momenta + mass_sq)
    measure = momenta * momenta / (2.0 * pi**2)
    beta = 1.0 / temperature
    argument_minus = (energy - chemical_potential) * beta
    argument_plus = (energy + chemical_potential) * beta
    n_minus = _bose(argument_minus)
    n_plus = _bose(argument_plus)
    log_minus = _bose_log(argument_minus)
    log_plus = _bose_log(argument_plus)
    pressure = temperature * float(np.sum(weights * measure * (log_minus + log_plus)))
    charge_density = float(np.sum(weights * measure * (n_minus - n_plus)))
    entropy_density = float(
        np.sum(
            weights
            * measure
            * (
                log_minus
                + argument_minus * n_minus
                + log_plus
                + argument_plus * n_plus
            )
        )
    )
    energy_density = -pressure + temperature * entropy_density + chemical_potential * charge_density
    charge_susceptibility = float(
        np.sum(
            weights
            * measure
            * (
                n_minus * (1.0 + n_minus) * beta
                + n_plus * (1.0 + n_plus) * beta
            )
        )
    )
    heat_capacity_at_mu = float(
        np.sum(
            weights
            * measure
            * (
                argument_minus**2 * n_minus * (1.0 + n_minus)
                + argument_plus**2 * n_plus * (1.0 + n_plus)
            )
        )
    )
    thermal_tadpole = 0.5 * float(
        np.sum(weights * measure * (n_minus + n_plus) / energy)
    )
    values = (
        pressure,
        charge_density,
        entropy_density,
        energy_density,
        charge_susceptibility,
        heat_capacity_at_mu,
        thermal_tadpole,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("thermal one-loop state contains a non-finite value")
    return values


def uet_o2_hartree_thermodynamic_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
    component_count: int = 2,
) -> UETO2HartreeThermodynamicState:
    """Evaluate the stationary thermal Hartree functional."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    if isinstance(component_count, bool) or int(component_count) != component_count:
        raise ValueError("component_count must be an integer")
    component_count = int(component_count)
    if component_count < 1:
        raise ValueError("component_count must be positive")
    hartree = uet_o2_finite_temperature_self_energy_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
        component_count=component_count,
    )
    one_loop = _thermal_one_loop_state(
        hartree.dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=hartree.momentum_cutoff,
    )
    (
        one_loop_pressure,
        charge_density,
        entropy_density,
        one_loop_energy_density,
        charge_susceptibility,
        heat_capacity_at_mu,
        tadpole,
    ) = one_loop
    coupling = _positive(config.matter.matter_quartic, "matter_quartic")
    combinatorial_factor = component_count + 2
    double_bubble_pressure = 0.5 * combinatorial_factor * coupling * tadpole**2
    pressure = one_loop_pressure + double_bubble_pressure
    energy_density = (
        -pressure + temperature * entropy_density + chemical_potential * charge_density
    )
    tadpole_mass_derivative = hartree.self_energy_mass_derivative / (
        coupling * combinatorial_factor
    )
    pressure_stationarity_residual = hartree.gap_residual * tadpole_mass_derivative
    values = (
        pressure,
        charge_density,
        entropy_density,
        energy_density,
        charge_susceptibility,
        heat_capacity_at_mu,
        pressure_stationarity_residual,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("Hartree thermodynamics contains a non-finite value")
    return UETO2HartreeThermodynamicState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        base_mass_sq=hartree.base_mass_sq,
        dressed_mass_sq=hartree.dressed_mass_sq,
        thermal_tadpole=tadpole,
        one_loop_pressure=one_loop_pressure,
        double_bubble_pressure=double_bubble_pressure,
        pressure=pressure,
        charge_density=charge_density,
        entropy_density=entropy_density,
        energy_density=energy_density,
        charge_susceptibility=charge_susceptibility,
        heat_capacity_at_mu=heat_capacity_at_mu,
        gap_residual=hartree.gap_residual,
        pressure_stationarity_residual=float(pressure_stationarity_residual),
        momentum_cutoff=hartree.momentum_cutoff,
        quadrature_order=hartree.quadrature_order,
    )


def uet_o2_hartree_thermodynamic_contract() -> dict[str, Any]:
    """Return the equilibrium Hartree functional and claim boundary."""

    return {
        "status": "ACTION_DERIVED_HARTREE_EQUILIBRIUM_THERMODYNAMIC_LANE",
        "equations": {
            "one_loop_pressure": "p_1(T,mu;M)=T integral[L(E-Mu)+L(E+mu)] d^3k/(2*pi)^3",
            "hartree_2pi_functional": "Omega_H=Omega_1+(m_eff^2-M^2)I_T+(N+2)*lambda*I_T^2/2",
            "stationary_pressure": "p_H=p_1+(N+2)*lambda*I_T^2/2 at M^2=m_eff^2+(N+2)*lambda*I_T",
            "charge": "n_H=(partial p_H/partial mu)_stationary=n_1",
            "entropy": "s_H=(partial p_H/partial T)_stationary=s_1",
            "energy": "epsilon_H=-p_H+T*s_H+mu*n_H",
            "stability_checks": "chi_H=(partial n_H/partial mu)_T>=0; c_mu=T*(partial s_H/partial T)_mu>=0",
        },
        "units": {
            "unit_lane": "natural",
            "pressure_energy_density": "natural energy density",
            "charge_density": "natural charge density",
            "entropy_density": "natural entropy density",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "derivation_class": "action-derived stationary thermal 2PI/Hartree functional on the homogeneous normal branch; vacuum piece excluded",
        "approximation": {
            "vacuum_counterterm": "NOT_INCLUDED",
            "condensate_branch": "NOT_INCLUDED",
            "normal_two_fluid_transport": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms_microscopic_match": "NOT_INCLUDED",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not charge density",
            "Phi": "effective action response variable; not temperature",
            "R_gen": "derived history trace only; not a state or feedback",
            "R_obs": "separate observer record; not part of the action state",
        },
        "data_role": "ACTION_DERIVED_EQUILIBRIUM_INTERNAL_NO_EXTERNAL_CALIBRATION",
        "claim_boundary": "This closes only equilibrium thermodynamic consistency of the declared natural-unit O(2) Hartree normal branch. It is not a unique microscopic finite-temperature theory, a condensate/two-fluid EOS, a physical Kubo or SK/KMS match, an entropy-current transport closure, an SI Phi map, an alpha_Phi_K calibration, TTG validation, or global UET closure.",
    }


__all__ = [
    "UETO2HartreeThermodynamicState",
    "uet_o2_hartree_thermodynamic_state",
    "uet_o2_hartree_thermodynamic_contract",
]
