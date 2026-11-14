"""Ward-preserving finite-temperature condensed auxiliary-field lane.

This module defines a fixed-prescription auxiliary-field completion of the
declared natural-unit O(2) action.  The auxiliary mass ``M^2`` and condensate
amplitude-squared ``rho`` are varied together.  The condensed stationarity
equations impose ``M^2=Z*mu^2`` and therefore keep the phase Ward gap zero
across the state domain without choosing a state-dependent counterterm.

The construction is a formal leading auxiliary-field/large-N-inspired lane.
It is not a microscopic 2PI or controlled 1/N result, does not emit a
physical Kubo coefficient, and does not provide an SI map for ``Phi``.
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
from docs.core.uet_o2_renormalized_normal_branch import _vacuum_terms


@dataclass(frozen=True)
class UETO2AuxiliaryFieldCondensedState:
    """Stationary state of the fixed auxiliary-field condensed functional."""

    temperature: float
    chemical_potential: float
    space_response: float
    base_mass_sq: float
    dressed_mass_sq: float
    reference_mass_sq: float
    condensate_amplitude_sq: float
    condensate_amplitude: float
    vacuum_grand_potential: float
    thermal_grand_potential: float
    loop_grand_potential: float
    renormalized_tadpole: float
    auxiliary_gap_residual: float
    condensed_stationarity_residual: float
    ward_phase_gap_sq: float
    tree_phase_curvature: float
    radial_curvature: float
    pressure: float
    charge_density: float
    entropy_density: float
    energy_density: float
    loop_charge_density: float
    loop_entropy_density: float
    loop_charge_susceptibility: float
    loop_heat_capacity_at_mu: float
    momentum_cutoff: float
    quadrature_order: int
    unit_lane: str = "natural"
    fixed_reference_subtraction: bool = True
    state_dependent_counterterm: bool = False
    auxiliary_field_included: bool = True
    ward_preserving_formal_lane: bool = True
    microscopic_2pi_or_1n_matching: bool = False
    normal_two_fluid_completion_included: bool = False
    physical_kubo_coefficient_included: bool = False
    physical_si_mapping_included: bool = False
    external_calibration_included: bool = False
    data_role: str = "ACTION_DERIVED_AUXILIARY_FIELD_CONDENSED_FORMAL_LANE"


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


def _loop_state(
    dressed_mass_sq: float,
    reference_mass_sq: float,
    temperature: float,
    chemical_potential: float,
    *,
    quadrature_order: int,
    cutoff: float,
) -> tuple[float, float, float, float, float, float, float, float, float]:
    """Return the fixed-subtraction one-loop terms used by the functional."""

    vacuum, vacuum_first, _ = _vacuum_terms(
        dressed_mass_sq,
        reference_mass_sq,
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
    ) = _thermal_one_loop_state(
        dressed_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    values = (
        vacuum,
        vacuum_first,
        thermal_pressure,
        charge_density,
        entropy_density,
        energy_density,
        charge_susceptibility,
        heat_capacity_at_mu,
        thermal_tadpole,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("auxiliary-field loop state is not finite")
    return (
        float(vacuum),
        float(vacuum_first),
        float(thermal_pressure),
        float(charge_density),
        float(entropy_density),
        float(energy_density),
        float(charge_susceptibility),
        float(heat_capacity_at_mu),
        float(thermal_tadpole),
    )


def auxiliary_field_grand_potential(
    condensate_amplitude_sq: float,
    dressed_mass_sq: float,
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff: float,
) -> float:
    """Evaluate the fixed-prescription auxiliary grand potential.

    The functional is

    ``Omega = (m_eff^2-Z*mu^2)rho/2 + lambda*rho^2/4``
    ``        + Omega_1^R(M^2) - (M^2-m_eff^2-lambda*rho)^2/(4*lambda)``.

    Its two stationarity equations are ``M^2=Z*mu^2`` and
    ``M^2=m_eff^2+lambda*rho+2*lambda*I_R``.
    """

    rho = _finite(condensate_amplitude_sq, "condensate_amplitude_sq")
    if rho <= 0.0:
        raise ValueError("condensed auxiliary-field lane requires rho > 0")
    mass_sq = float(effective_mass_sq(space_response, config))
    lam = _positive(config.matter.matter_quartic, "matter_quartic")
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    mu = _finite(chemical_potential, "chemical_potential")
    M2 = _positive(dressed_mass_sq, "dressed_mass_sq")
    temperature = _positive(temperature, "temperature")
    reference_mass_sq = float(effective_mass_sq(config.response.phi_equilibrium, config))
    vacuum, _, thermal_pressure, *_ = _loop_state(
        M2,
        reference_mass_sq,
        temperature,
        mu,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    loop_grand_potential = vacuum - thermal_pressure
    auxiliary_residual = M2 - mass_sq - lam * rho
    value = (
        0.5 * (mass_sq - z * mu * mu) * rho
        + 0.25 * lam * rho * rho
        + loop_grand_potential
        - auxiliary_residual * auxiliary_residual / (4.0 * lam)
    )
    if not isfinite(value):
        raise FloatingPointError("auxiliary-field grand potential is not finite")
    return float(value)


def auxiliary_field_condensed_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 70.0,
    momentum_cutoff: float | None = None,
) -> UETO2AuxiliaryFieldCondensedState:
    """Return the Ward-preserving formal condensed state.

    A fixed mass-squared Taylor subtraction is used for every state.  The
    auxiliary equations, rather than a state-wise counterterm, enforce the
    phase Ward condition.  The normal one-loop determinant is well-defined on
    this lane only when ``Z>1`` because ``M^2=Z*mu^2`` must stay above the
    charged Bose threshold.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 32:
        raise ValueError("quadrature_order must be >= 32")
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    if z <= 1.0:
        raise ValueError("auxiliary-field condensed lane requires Z > 1")
    lam = _positive(config.matter.matter_quartic, "matter_quartic")
    base_mass_sq = float(effective_mass_sq(space_response, config))
    reference_mass_sq = float(effective_mass_sq(config.response.phi_equilibrium, config))
    if base_mass_sq <= 0.0 or reference_mass_sq <= 0.0:
        raise ValueError("auxiliary-field lane requires positive mass-squared values")
    dressed_mass_sq = z * chemical_potential * chemical_potential
    if dressed_mass_sq <= 0.0:
        raise ValueError("auxiliary-field condensed lane requires nonzero chemical potential")
    cutoff = (
        _cutoff(
            temperature,
            chemical_potential,
            base_mass_sq,
            reference_mass_sq,
            cutoff_factor,
        )
        if momentum_cutoff is None
        else _positive(momentum_cutoff, "momentum_cutoff")
    )
    (
        vacuum,
        vacuum_first,
        thermal_pressure,
        loop_charge,
        loop_entropy,
        _,
        loop_susceptibility,
        loop_heat_capacity,
        thermal_tadpole,
    ) = _loop_state(
        dressed_mass_sq,
        reference_mass_sq,
        temperature,
        chemical_potential,
        quadrature_order=quadrature_order,
        cutoff=cutoff,
    )
    renormalized_tadpole = vacuum_first + thermal_tadpole
    condensate_amplitude_sq = (
        dressed_mass_sq
        - base_mass_sq
        - 2.0 * lam * renormalized_tadpole
    ) / lam
    if condensate_amplitude_sq <= 0.0:
        raise ValueError("auxiliary-field state is outside the condensed domain")
    auxiliary_gap_residual = (
        dressed_mass_sq
        - base_mass_sq
        - lam * condensate_amplitude_sq
        - 2.0 * lam * renormalized_tadpole
    )
    condensed_stationarity_residual = 0.5 * (
        dressed_mass_sq - z * chemical_potential * chemical_potential
    )
    ward_phase_gap_sq = dressed_mass_sq - z * chemical_potential * chemical_potential
    tree_phase_curvature = (
        -z * chemical_potential * chemical_potential
        + base_mass_sq
        + lam * condensate_amplitude_sq
    )
    radial_curvature = 2.0 * lam * condensate_amplitude_sq
    loop_grand_potential = vacuum - thermal_pressure
    auxiliary_residual = dressed_mass_sq - base_mass_sq - lam * condensate_amplitude_sq
    grand_potential = (
        0.5 * (base_mass_sq - z * chemical_potential**2) * condensate_amplitude_sq
        + 0.25 * lam * condensate_amplitude_sq**2
        + loop_grand_potential
        - auxiliary_residual**2 / (4.0 * lam)
    )
    pressure = -grand_potential
    charge_density = z * chemical_potential * condensate_amplitude_sq + loop_charge
    entropy_density = loop_entropy
    energy_density = -pressure + temperature * entropy_density + chemical_potential * charge_density
    values = (
        base_mass_sq,
        reference_mass_sq,
        dressed_mass_sq,
        condensate_amplitude_sq,
        renormalized_tadpole,
        auxiliary_gap_residual,
        condensed_stationarity_residual,
        ward_phase_gap_sq,
        tree_phase_curvature,
        radial_curvature,
        grand_potential,
        pressure,
        charge_density,
        entropy_density,
        energy_density,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("auxiliary-field condensed state is not finite")
    return UETO2AuxiliaryFieldCondensedState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        base_mass_sq=base_mass_sq,
        dressed_mass_sq=dressed_mass_sq,
        reference_mass_sq=reference_mass_sq,
        condensate_amplitude_sq=condensate_amplitude_sq,
        condensate_amplitude=sqrt(condensate_amplitude_sq),
        vacuum_grand_potential=float(vacuum),
        thermal_grand_potential=float(-thermal_pressure),
        loop_grand_potential=float(loop_grand_potential),
        renormalized_tadpole=float(renormalized_tadpole),
        auxiliary_gap_residual=float(auxiliary_gap_residual),
        condensed_stationarity_residual=float(condensed_stationarity_residual),
        ward_phase_gap_sq=float(ward_phase_gap_sq),
        tree_phase_curvature=float(tree_phase_curvature),
        radial_curvature=float(radial_curvature),
        pressure=float(pressure),
        charge_density=float(charge_density),
        entropy_density=float(entropy_density),
        energy_density=float(energy_density),
        loop_charge_density=float(loop_charge),
        loop_entropy_density=float(loop_entropy),
        loop_charge_susceptibility=float(loop_susceptibility),
        loop_heat_capacity_at_mu=float(loop_heat_capacity),
        momentum_cutoff=float(cutoff),
        quadrature_order=quadrature_order,
    )


def auxiliary_field_mode_omega_sq(
    wavenumber: float,
    state: UETO2AuxiliaryFieldCondensedState,
    config: O2FiniteDensityEOSConfig,
) -> tuple[float, float]:
    """Return the resummed radial/phase mode roots for the formal lane."""

    k = _finite(wavenumber, "wavenumber")
    if k < 0.0:
        raise ValueError("wavenumber must be non-negative")
    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    mu = state.chemical_potential
    radial = state.radial_curvature / z
    phase = state.ward_phase_gap_sq / z
    discriminant = (
        (radial - phase) ** 2
        + 8.0 * mu * mu * (radial + phase)
        + 16.0 * mu**4
        + 16.0 * mu * mu * k * k
    )
    if discriminant < -1.0e-12:
        raise FloatingPointError("auxiliary-field mode discriminant is negative")
    root = sqrt(max(discriminant, 0.0))
    base = k * k + 0.5 * (radial + phase + 4.0 * mu * mu)
    low = base - 0.5 * root
    high = base + 0.5 * root
    if not isfinite(low) or not isfinite(high):
        raise FloatingPointError("auxiliary-field mode roots are not finite")
    return float(low), float(high)


def auxiliary_field_condensed_contract() -> dict[str, Any]:
    """Return equations, units, approximation, and claim boundary."""

    return {
        "status": "FORMAL_WARD_PRESERVING_AUXILIARY_FIELD_CONDENSED_LANE",
        "equations": {
            "auxiliary_functional": "Omega=(m_eff^2-Z*mu^2)*rho/2+lambda*rho^2/4+Omega_1^R(M^2)-(M^2-m_eff^2-lambda*rho)^2/(4*lambda)",
            "condensed_stationarity": "partial_rho Omega=(M^2-Z*mu^2)/2=0",
            "auxiliary_gap": "partial_M2 Omega=I_R-(M^2-m_eff^2-lambda*rho)/(2*lambda)=0",
            "condensed_solution": "M^2=Z*mu^2; rho=(Z*mu^2-m_eff^2-2*lambda*I_R)/lambda",
            "ward_phase_gap": "Delta_W=M^2-Z*mu^2=0",
            "resummed_modes": "det[(y-k^2-r_sigma/Z)(y-k^2-r_pi/Z)-4*mu^2*y]=0 with r_pi=Delta_W and r_sigma=2*lambda*rho",
            "thermodynamics": "n=Z*mu*rho+n_1; s=s_1; epsilon=-p+T*s+mu*n",
        },
        "units": {
            "unit_lane": "natural",
            "temperature_and_chemical_potential": "natural energy",
            "mass_squared_and_tadpole": "natural energy squared",
            "rho": "natural amplitude squared",
            "pressure_and_energy_density": "natural energy density",
            "Phi": "effective action response input; no SI map",
        },
        "prescription": {
            "reference": "fixed mass-squared Taylor subtraction at Phi=Phi_equilibrium",
            "state_dependent_counterterm": False,
            "required_Z_domain": "Z>1 for the charged normal determinant at M^2=Z*mu^2",
        },
        "approximation": {
            "label": "formal auxiliary-field / leading-large-N-inspired completion",
            "microscopic_2pi_or_controlled_1N_match": False,
            "finite_temperature_normal_loop": True,
            "condensed_backreaction": True,
            "physical_kubo": False,
            "sk_kms_microscopic_match": False,
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective action response variable; not temperature",
            "R_gen": "derived history trace only; not a state or feedback",
            "R_obs": "separate observer record; not part of the action state",
        },
        "data_role": "ACTION_DERIVED_FORMAL_INTERNAL_NO_EXTERNAL_CALIBRATION",
        "claim_boundary": "This closes only a fixed-prescription Ward-preserving auxiliary-field condensed lane. It is not a microscopic 2PI or controlled 1/N completion, a physical finite-temperature renormalization, a full two-fluid EOS, a retarded Kubo/SK-KMS match, an SI Phi map, an alpha_Phi_K calibration, TTG validation, or Full Topic 13 closure.",
    }


__all__ = [
    "UETO2AuxiliaryFieldCondensedState",
    "auxiliary_field_grand_potential",
    "auxiliary_field_condensed_state",
    "auxiliary_field_mode_omega_sq",
    "auxiliary_field_condensed_contract",
]
