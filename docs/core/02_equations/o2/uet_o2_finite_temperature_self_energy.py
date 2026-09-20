"""Action-derived finite-temperature O(2) Hartree self-energy lane.

This module closes a narrowly scoped natural-unit derivation: the thermal
tadpole self-energy of the declared O(2) matter action on a homogeneous normal
background.  It is a self-consistent Hartree approximation, not a claim of a
unique microscopic finite-temperature effective action or physical transport.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)


@dataclass(frozen=True)
class UETO2FiniteTemperatureSelfEnergyState:
    """Self-consistent normal-branch Hartree state in natural units."""

    temperature: float
    chemical_potential: float
    space_response: float
    base_mass_sq: float
    dressed_mass_sq: float
    thermal_self_energy: float
    self_energy_mass_derivative: float
    dressed_mass_response_derivative: float
    gap_residual: float
    momentum_cutoff: float
    quadrature_order: int
    iterations: int
    unit_lane: str = "natural"
    approximation: str = "O(2) Hartree thermal tadpole on homogeneous normal branch"
    vacuum_counterterm_included: bool = False
    condensate_contribution_included: bool = False
    physical_kubo_coefficient_included: bool = False
    physical_si_mapping_included: bool = False
    data_role: str = "ACTION_DERIVED_SELF_ENERGY_LANE_NOT_PHYSICAL_CALIBRATION"


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


def _bose(argument: np.ndarray) -> np.ndarray:
    """Evaluate n_B(argument) without overflow on the high-energy tail."""

    values = np.asarray(argument, dtype=float)
    if np.any(values <= 0.0) or not np.all(np.isfinite(values)):
        raise ValueError("Bose occupation requires finite positive arguments")
    result = np.empty_like(values)
    high = values > 50.0
    result[high] = np.exp(-values[high])
    result[~high] = 1.0 / np.expm1(values[~high])
    return result


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    cutoff = _positive(cutoff, "cutoff")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    return momenta, scaled_weights


def _cutoff(
    temperature: float,
    chemical_potential: float,
    base_mass_sq: float,
    cutoff_factor: float,
) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    return max(
        factor * temperature,
        factor * abs(chemical_potential),
        factor * sqrt(max(base_mass_sq, 0.0)),
        1.0,
    )


def _thermal_tadpole_and_derivative(
    mass_sq: float,
    temperature: float,
    chemical_potential: float,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float]:
    """Return I_T and dI_T/d(m^2) for the complex O(2) normal determinant."""

    mass_sq = _positive(mass_sq, "mass_sq")
    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) >= sqrt(mass_sq):
        raise ValueError("normal tadpole requires |chemical_potential| < dressed mass")
    momenta, weights = _quadrature(quadrature_order, cutoff)
    energy = np.sqrt(momenta * momenta + mass_sq)
    beta = 1.0 / temperature
    n_minus = _bose((energy - chemical_potential) * beta)
    n_plus = _bose((energy + chemical_potential) * beta)
    measure = momenta * momenta / (2.0 * pi**2)
    n_sum = n_minus + n_plus
    tadpole = 0.5 * np.sum(weights * measure * n_sum / energy)
    occupation_derivative_sum = beta * (
        n_minus * (1.0 + n_minus) + n_plus * (1.0 + n_plus)
    )
    derivative = -0.25 * np.sum(
        weights
        * measure
        * (occupation_derivative_sum / energy**2 + n_sum / energy**3)
    )
    values = (float(tadpole), float(derivative))
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("thermal tadpole returned a non-finite value")
    if values[0] < 0.0 or values[1] > 1.0e-14:
        raise FloatingPointError("thermal tadpole sign contract failed")
    return values


def _gap_residual(
    dressed_mass_sq: float,
    base_mass_sq: float,
    temperature: float,
    chemical_potential: float,
    coupling: float,
    component_count: int,
    *,
    quadrature_order: int,
    cutoff: float,
) -> float:
    tadpole, _ = _thermal_tadpole_and_derivative(
        dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    return float(
        dressed_mass_sq
        - base_mass_sq
        - coupling * (component_count + 2) * tadpole
    )


def uet_o2_finite_temperature_self_energy_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
    component_count: int = 2,
    gap_tolerance: float = 1.0e-12,
    max_iterations: int = 256,
) -> UETO2FiniteTemperatureSelfEnergyState:
    """Solve the O(2) Hartree thermal gap equation on the normal branch.

    With ``V=lambda*(chi_a chi_a)^2/4`` the one-loop thermal tadpole gives
    ``Pi_T = (N+2)*lambda*I_T``.  The vacuum piece is not included; it remains
    governed by the separately declared subtraction scheme.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if isinstance(component_count, bool) or int(component_count) != component_count:
        raise ValueError("component_count must be an integer")
    component_count = int(component_count)
    if component_count < 1:
        raise ValueError("component_count must be positive")
    coupling = _positive(config.matter.matter_quartic, "matter_quartic")
    gap_tolerance = _positive(gap_tolerance, "gap_tolerance")
    if isinstance(max_iterations, bool) or int(max_iterations) != max_iterations:
        raise ValueError("max_iterations must be an integer")
    max_iterations = int(max_iterations)
    if max_iterations < 16:
        raise ValueError("max_iterations must be >= 16")
    base_mass_sq = float(effective_mass_sq(space_response, config))
    if base_mass_sq <= 0.0:
        raise ValueError("Hartree normal lane requires positive base mass-squared")
    kinetic = _positive(config.matter.matter_kinetic, "matter_kinetic")
    cutoff = _cutoff(
        temperature,
        chemical_potential,
        base_mass_sq,
        cutoff_factor,
    )
    lower = max(
        base_mass_sq,
        kinetic * chemical_potential**2 * (1.0 + 1.0e-10),
        1.0e-14,
    )
    lower_value = _gap_residual(
        lower,
        base_mass_sq,
        temperature,
        chemical_potential,
        coupling,
        component_count,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    if lower_value > 0.0:
        raise ValueError("no self-consistent Hartree solution in the normal branch")
    upper = max(lower * 2.0, lower + coupling * temperature**2)
    upper_value = _gap_residual(
        upper,
        base_mass_sq,
        temperature,
        chemical_potential,
        coupling,
        component_count,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    for _ in range(max_iterations):
        if upper_value > 0.0:
            break
        upper *= 2.0
        upper_value = _gap_residual(
            upper,
            base_mass_sq,
            temperature,
            chemical_potential,
            coupling,
            component_count,
            quadrature_order=quadrature_order,
            cutoff=cutoff,
        )
    else:
        raise RuntimeError("failed to bracket the Hartree normal gap")

    iterations = 0
    for iterations in range(1, max_iterations + 1):
        midpoint = 0.5 * (lower + upper)
        midpoint_value = _gap_residual(
            midpoint,
            base_mass_sq,
            temperature,
            chemical_potential,
            coupling,
            component_count,
            quadrature_order=quadrature_order,
            cutoff=cutoff,
        )
        if abs(midpoint_value) <= gap_tolerance:
            dressed_mass_sq = midpoint
            break
        if midpoint_value < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    else:
        raise RuntimeError("Hartree normal gap did not converge")

    dressed_mass_sq = float(midpoint)
    tadpole, tadpole_mass_derivative = _thermal_tadpole_and_derivative(
        dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    self_energy = coupling * (component_count + 2) * tadpole
    self_energy_mass_derivative = coupling * (component_count + 2) * tadpole_mass_derivative
    dm2_dphi = float(
        -config.response.epsilon_nc * config.matter.response_coupling
    )
    dressed_response_derivative = dm2_dphi / (1.0 - self_energy_mass_derivative)
    residual = float(dressed_mass_sq - base_mass_sq - self_energy)
    values = (
        base_mass_sq,
        dressed_mass_sq,
        self_energy,
        self_energy_mass_derivative,
        dressed_response_derivative,
        residual,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("Hartree state contains a non-finite value")
    if dressed_mass_sq <= kinetic * chemical_potential**2:
        raise FloatingPointError("Hartree solution left the normal branch")
    return UETO2FiniteTemperatureSelfEnergyState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        base_mass_sq=base_mass_sq,
        dressed_mass_sq=dressed_mass_sq,
        thermal_self_energy=float(self_energy),
        self_energy_mass_derivative=float(self_energy_mass_derivative),
        dressed_mass_response_derivative=float(dressed_response_derivative),
        gap_residual=residual,
        momentum_cutoff=float(cutoff),
        quadrature_order=int(quadrature_order),
        iterations=int(iterations),
    )


def uet_o2_finite_temperature_self_energy_contract() -> dict[str, Any]:
    """Return the equation and claim boundary for this lane."""

    return {
        "status": "ACTION_DERIVED_HARTREE_THERMAL_SELF_ENERGY",
        "equations": {
            "thermal_tadpole": "I_T(M^2;T,mu)=1/2 integral[(n_B(E-mu)+n_B(E+mu))/E] d^3k/(2*pi)^3",
            "hartree_self_energy": "Pi_T=(N+2)*lambda*I_T, N=2",
            "gap_equation": "M^2=m_eff^2(Phi)+Pi_T(M^2;T,mu)",
            "implicit_response": "dM^2/dPhi=(d m_eff^2/dPhi)/(1-dPi_T/dM^2)",
            "action_mass_map": "d m_eff^2/dPhi=-epsilon_nc*response_coupling",
        },
        "units": {
            "unit_lane": "natural",
            "T_mu_M": "natural energy",
            "mass_squared": "natural energy squared",
            "Pi_T": "natural energy squared",
            "Phi": "natural action response field; not temperature",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "derivation_class": "action-derived finite-temperature Hartree thermal tadpole with a self-consistent normal gap",
        "approximation": {
            "component_count": 2,
            "vacuum_counterterm": "NOT_INCLUDED; use the separately declared subtraction scheme",
            "condensate_branch": "NOT_INCLUDED",
            "two_fluid_transport": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms_microscopic_match": "NOT_INCLUDED",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not charge density",
            "Phi": "effective response variable in the action; not temperature",
            "R_gen": "derived history trace only; not state or feedback",
            "R_obs": "separate observer record; not part of the action state",
        },
        "claim_boundary": "This closes only the declared natural-unit O(2) Hartree self-energy and implicit response derivative on the homogeneous normal branch. It is not a unique microscopic finite-temperature action, a condensate/two-fluid closure, a physical Kubo coefficient, an SI Phi map, an alpha_Phi_K calibration, TTG validation, or global UET closure.",
    }


__all__ = [
    "UETO2FiniteTemperatureSelfEnergyState",
    "uet_o2_finite_temperature_self_energy_state",
    "uet_o2_finite_temperature_self_energy_contract",
]
