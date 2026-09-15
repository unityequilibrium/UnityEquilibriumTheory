"""Finite-temperature renormalized Hartree normal branch.

This module composes the existing mass-squared Taylor subtraction with the
stationary O(2) Hartree functional.  The vacuum and thermal tadpoles enter one
gap equation, so the pressure and its charge/entropy derivatives are evaluated
on the same stationary state.  The result is a declared natural-unit scheme,
not a microscopic finite-temperature matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_hartree_thermodynamics import (
    _thermal_one_loop_state,
)
from docs.core.uet_o2_finite_temperature_self_energy import (
    _thermal_tadpole_and_derivative,
)
from docs.core.uet_o2_renormalized_normal_branch import _vacuum_terms


@dataclass(frozen=True)
class UETO2RenormalizedHartreeNormalState:
    """Stationary renormalized Hartree state on the normal branch."""

    temperature: float
    chemical_potential: float
    space_response: float
    base_mass_sq: float
    dressed_mass_sq: float
    reference_mass_sq: float
    vacuum_grand_potential: float
    thermal_grand_potential: float
    total_one_loop_grand_potential: float
    vacuum_tadpole: float
    thermal_tadpole: float
    total_tadpole: float
    thermal_self_energy: float
    double_bubble_pressure: float
    pressure: float
    charge_density: float
    entropy_density: float
    energy_density: float
    charge_susceptibility: float
    heat_capacity_at_mu: float
    gap_residual: float
    functional_stationarity_residual: float
    vacuum_mass_second_derivative: float
    total_tadpole_mass_derivative: float
    momentum_cutoff: float
    quadrature_order: int
    iterations: int
    component_count: int = 2
    unit_lane: str = "natural"
    vacuum_counterterm_included: bool = True
    hartree_interaction_included: bool = True
    condensed_branch_included: bool = False
    physical_kubo_coefficient_included: bool = False
    physical_si_mapping_included: bool = False
    data_role: str = "ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME_NOT_PHYSICAL"


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


def _cutoff(
    temperature: float,
    chemical_potential: float,
    base_mass_sq: float,
    reference_mass_sq: float,
    cutoff_factor: float,
) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    return factor * max(
        temperature,
        abs(chemical_potential),
        sqrt(base_mass_sq),
        sqrt(reference_mass_sq),
        1.0,
    )


def _one_loop_terms(
    dressed_mass_sq: float,
    base_mass_sq: float,
    reference_mass_sq: float,
    temperature: float,
    chemical_potential: float,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float, float, float, float, float, float, float]:
    """Return one-loop potentials, tadpoles, and derivative data."""

    vacuum, vacuum_first, vacuum_second = _vacuum_terms(
        dressed_mass_sq,
        reference_mass_sq,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    thermal = _thermal_one_loop_state(
        dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    (
        thermal_pressure,
        charge_density,
        entropy_density,
        energy_density,
        charge_susceptibility,
        heat_capacity_at_mu,
        thermal_tadpole,
    ) = thermal
    _, thermal_tadpole_derivative = _thermal_tadpole_and_derivative(
        dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    del base_mass_sq, energy_density
    values = (
        vacuum,
        vacuum_first,
        vacuum_second,
        thermal_pressure,
        charge_density,
        entropy_density,
        thermal_tadpole,
        thermal_tadpole_derivative,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("renormalized Hartree one-loop terms are not finite")
    return (
        float(vacuum),
        float(thermal_pressure),
        float(vacuum_first),
        float(vacuum_second),
        float(thermal_tadpole),
        float(thermal_tadpole_derivative),
        float(charge_density),
        float(entropy_density),
    )


def _gap_terms(
    dressed_mass_sq: float,
    base_mass_sq: float,
    reference_mass_sq: float,
    temperature: float,
    chemical_potential: float,
    coupling: float,
    component_count: int,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float, float, float, float, float]:
    terms = _one_loop_terms(
        dressed_mass_sq,
        base_mass_sq,
        reference_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    vacuum, thermal_pressure, vacuum_first, vacuum_second, thermal_tadpole, thermal_derivative, _, _ = terms
    total_tadpole = vacuum_first + thermal_tadpole
    total_derivative = vacuum_second + thermal_derivative
    residual = dressed_mass_sq - base_mass_sq - coupling * (component_count + 2) * total_tadpole
    del thermal_pressure
    return (
        float(residual),
        float(total_tadpole),
        float(total_derivative),
        float(vacuum),
        float(vacuum_second),
        float(thermal_tadpole),
    )


def uet_o2_renormalized_hartree_normal_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 60.0,
    component_count: int = 2,
    gap_tolerance: float = 1.0e-11,
    max_iterations: int = 256,
) -> UETO2RenormalizedHartreeNormalState:
    """Solve the renormalized Hartree gap equation in the normal domain."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if isinstance(component_count, bool) or int(component_count) != component_count:
        raise ValueError("component_count must be an integer")
    component_count = int(component_count)
    if component_count < 1:
        raise ValueError("component_count must be positive")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 32:
        raise ValueError("quadrature_order must be >= 32")
    gap_tolerance = _positive(gap_tolerance, "gap_tolerance")
    if isinstance(max_iterations, bool) or int(max_iterations) != max_iterations:
        raise ValueError("max_iterations must be an integer")
    max_iterations = int(max_iterations)
    if max_iterations < 32:
        raise ValueError("max_iterations must be >= 32")

    base_mass_sq = float(effective_mass_sq(space_response, config))
    reference_mass_sq = float(effective_mass_sq(config.response.phi_equilibrium, config))
    if base_mass_sq <= 0.0 or reference_mass_sq <= 0.0:
        raise ValueError("renormalized Hartree lane requires positive mass-squared values")
    kinetic = _positive(config.matter.matter_kinetic, "matter_kinetic")
    coupling = _positive(config.matter.matter_quartic, "matter_quartic")
    normal_threshold = max(kinetic * chemical_potential**2, chemical_potential**2) * (1.0 + 1.0e-10)
    lower = max(base_mass_sq, normal_threshold, 1.0e-14)
    cutoff = _cutoff(
        temperature,
        chemical_potential,
        base_mass_sq,
        reference_mass_sq,
        cutoff_factor,
    )

    def residual(mass_sq: float) -> float:
        return _gap_terms(
            mass_sq,
            base_mass_sq,
            reference_mass_sq,
            temperature,
            chemical_potential,
            coupling,
            component_count,
            quadrature_order=quadrature_order,
            cutoff=cutoff,
        )[0]

    lower_value = residual(lower)
    if lower_value > 0.0:
        raise ValueError("no renormalized Hartree solution in the normal branch")
    upper = max(2.0 * lower, lower + coupling * temperature**2)
    upper_value = residual(upper)
    for _ in range(max_iterations):
        if upper_value > 0.0:
            break
        upper *= 2.0
        upper_value = residual(upper)
    else:
        raise RuntimeError("failed to bracket the renormalized Hartree normal gap")

    iterations = 0
    midpoint = lower
    for iterations in range(1, max_iterations + 1):
        midpoint = 0.5 * (lower + upper)
        midpoint_value = residual(midpoint)
        if abs(midpoint_value) <= gap_tolerance:
            break
        if midpoint_value < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    else:
        raise RuntimeError("renormalized Hartree normal gap did not converge")
    dressed_mass_sq = float(midpoint)
    (
        gap_residual,
        total_tadpole,
        total_tadpole_derivative,
        vacuum,
        vacuum_second,
        thermal_tadpole,
    ) = _gap_terms(
        dressed_mass_sq,
        base_mass_sq,
        reference_mass_sq,
        temperature,
        chemical_potential,
        coupling,
        component_count,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    terms = _one_loop_terms(
        dressed_mass_sq,
        base_mass_sq,
        reference_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    _, thermal_pressure, _, _, _, _, charge_density, entropy_density = terms
    thermal_state = _thermal_one_loop_state(
        dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    _, _, _, _, charge_susceptibility, heat_capacity_at_mu, _ = thermal_state
    combinatorial_factor = component_count + 2
    thermal_self_energy = coupling * combinatorial_factor * total_tadpole
    double_bubble_pressure = 0.5 * combinatorial_factor * coupling * total_tadpole**2
    total_one_loop_grand_potential = vacuum - thermal_pressure
    pressure = thermal_pressure - vacuum + double_bubble_pressure
    energy_density = -pressure + temperature * entropy_density + chemical_potential * charge_density
    functional_stationarity_residual = gap_residual * total_tadpole_derivative
    values = (
        base_mass_sq,
        dressed_mass_sq,
        vacuum,
        thermal_tadpole,
        total_tadpole,
        thermal_self_energy,
        pressure,
        charge_density,
        entropy_density,
        energy_density,
        charge_susceptibility,
        heat_capacity_at_mu,
        gap_residual,
        functional_stationarity_residual,
        vacuum_second,
        total_tadpole_derivative,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("renormalized Hartree state contains a non-finite value")
    if dressed_mass_sq <= normal_threshold:
        raise FloatingPointError("renormalized Hartree solution left the normal branch")
    return UETO2RenormalizedHartreeNormalState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        base_mass_sq=base_mass_sq,
        dressed_mass_sq=dressed_mass_sq,
        reference_mass_sq=reference_mass_sq,
        vacuum_grand_potential=float(vacuum),
        thermal_grand_potential=float(-thermal_pressure),
        total_one_loop_grand_potential=float(total_one_loop_grand_potential),
        vacuum_tadpole=float(terms[2]),
        thermal_tadpole=float(thermal_tadpole),
        total_tadpole=float(total_tadpole),
        thermal_self_energy=float(thermal_self_energy),
        double_bubble_pressure=float(double_bubble_pressure),
        pressure=float(pressure),
        charge_density=float(charge_density),
        entropy_density=float(entropy_density),
        energy_density=float(energy_density),
        charge_susceptibility=float(charge_susceptibility),
        heat_capacity_at_mu=float(heat_capacity_at_mu),
        gap_residual=float(gap_residual),
        functional_stationarity_residual=float(functional_stationarity_residual),
        vacuum_mass_second_derivative=float(vacuum_second),
        total_tadpole_mass_derivative=float(total_tadpole_derivative),
        momentum_cutoff=float(cutoff),
        quadrature_order=quadrature_order,
        iterations=iterations,
        component_count=component_count,
    )


def uet_o2_renormalized_hartree_normal_contract() -> dict[str, Any]:
    """Return the combined gap, functional, and claim boundary contract."""

    return {
        "status": "ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME",
        "equations": {
            "vacuum_subtraction": "V_vac^R(x)=integral[E(x)-E(x_*)-(x-x_*)E'(x_*)-1/2*(x-x_*)^2 E''(x_*)] d^3k/(2*pi)^3",
            "total_tadpole": "I_R(M^2;T,mu)=partial_M2[V_vac^R(M^2)+Omega_1^T(M^2;T,mu)]=I_vac^R+I_T",
            "renormalized_gap": "M^2=m_eff(Phi)^2+(N+2)*lambda*I_R(M^2;T,mu)",
            "hartree_functional": "Omega_H^R=Omega_1^R+(m_eff^2-M^2)I_R+(N+2)*lambda*I_R^2/2",
            "stationary_pressure": "p_H^R=p_1^T-V_vac^R+(N+2)*lambda*I_R^2/2",
            "thermodynamic_derivatives": "n=partial_mu p_H^R=n_1^T; s=partial_T p_H^R=s_1^T; epsilon=-p+T*s+mu*n",
        },
        "units": {
            "unit_lane": "natural",
            "mass_squared_and_tadpole": "natural energy squared",
            "pressure_energy_density": "natural energy density",
            "alpha_Phi_K": "not emitted; SI map remains open",
        },
        "derivation_class": "action-derived mass-squared Taylor subtraction combined with stationary O(2) 2PI/Hartree normal functional; not microscopic matching",
        "approximation": {
            "vacuum_scheme": "mass-squared Taylor subtraction through second order at Phi_*",
            "interacting_self_energy": "Hartree tadpole with vacuum plus thermal contribution",
            "condensate_branch": "NOT_INCLUDED",
            "normal_two_fluid_transport": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms_microscopic_match": "NOT_INCLUDED",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective action response variable; not temperature",
            "R_gen": "derived history trace only; not a state or feedback",
            "R_obs": "separate observer record; not part of the action state",
        },
        "data_role": "ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME_NOT_PHYSICAL",
        "claim_boundary": "This closes one declared natural-unit renormalized Hartree normal-branch functional and its stationary thermodynamic identities. It does not select the physical finite-temperature renormalization scheme, close the condensed/two-fluid EOS, provide physical Kubo or microscopic SK/KMS coefficients, close entropy/heat-flux transport, map Phi to SI temperature, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
    }


__all__ = [
    "UETO2RenormalizedHartreeNormalState",
    "uet_o2_renormalized_hartree_normal_state",
    "uet_o2_renormalized_hartree_normal_contract",
]
