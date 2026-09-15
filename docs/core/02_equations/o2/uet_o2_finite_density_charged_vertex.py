"""Finite-density charged propagator and one-loop vertex scheme.

This lane extends the declared mass-squared reference subtraction from the
zero-density O(2) vertex to the stable normal branch with a non-zero chemical
potential.  It keeps the vacuum subtraction independent of ``mu`` and retains
the finite particle/antiparticle thermal contribution.  The result is an
action-derived natural-unit scheme, not a unique physical renormalization or
an interacting transport calculation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, sqrt, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_equilibrium_kms import equilibrium_kms_state
from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_one_loop_vertex_uv_boundary import (
    _tree_vertex_tensor,
    _zero_external_bubble,
)


FINITE_DENSITY_CHARGED_VERTEX_STATUS = (
    "PASS_ACTION_DERIVED_FINITE_DENSITY_CHARGED_O2_VERTEX_SCHEME"
)


@dataclass(frozen=True)
class FiniteDensityChargedO2VertexState:
    """Finite-cutoff charged propagator and vertex values."""

    temperature: float
    chemical_potential: float
    effective_chemical_potential: float
    space_response: float
    reference_space_response: float
    effective_mass: float
    reference_mass: float
    quartic_coupling: float
    static_gap: float
    sample_momentum: float
    sample_mode_energy: float
    particle_mode_energy: float
    antiparticle_mode_energy: float
    raw_vacuum_values: tuple[float, ...]
    reference_vacuum_values: tuple[float, ...]
    subtracted_vacuum_values: tuple[float, ...]
    charged_thermal_values: tuple[float, ...]
    renormalized_bubble_values: tuple[float, ...]
    renormalized_vertex_norms: tuple[float, ...]
    renormalized_correction_norms: tuple[float, ...]
    thermal_charge_density: float
    raw_vacuum_growth_ratio: float
    charged_thermal_cutoff_relative_change: float
    renormalized_bubble_last_relative_change: float
    renormalized_vertex_last_relative_change: float
    static_propagator_residual: float
    propagator_factorization_residual: float
    particle_kms_residual: float
    antiparticle_kms_residual: float
    charge_conjugation_bubble_residual: float
    charge_density_odd_residual: float
    finite_density_charged_vertex_completed: bool = True
    unique_physical_renormalization_scheme_matched: bool = False
    full_interacting_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_DENSITY_CHARGED_VERTEX_SCHEME_NOT_PHYSICAL"
    )


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


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


def _charged_bubble(
    temperature: float,
    mass: float,
    effective_chemical_potential: float,
    cutoff: float,
    *,
    kinetic_prefactor: float,
    quadrature_order: int,
) -> tuple[float, float, float, float]:
    """Return vacuum, charged thermal, total, and charge-density integrals.

    The thermal normalization is the symmetric particle/antiparticle average;
    at ``mu=0`` it reduces exactly to the neutral bubble used by the preceding
    renormalized-vertex lane.
    """

    nodes, weights = np.polynomial.legendre.leggauss(int(quadrature_order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    energy = np.sqrt(momenta * momenta + mass * mass)
    particle_argument = (energy - effective_chemical_potential) / temperature
    antiparticle_argument = (energy + effective_chemical_potential) / temperature
    if np.any(particle_argument <= 0.0) or np.any(antiparticle_argument <= 0.0):
        raise ValueError("charged normal branch requires positive particle energies")
    particle_occupation = 1.0 / np.expm1(particle_argument)
    antiparticle_occupation = 1.0 / np.expm1(antiparticle_argument)
    particle_factor = particle_occupation * (1.0 + particle_occupation)
    antiparticle_factor = antiparticle_occupation * (1.0 + antiparticle_occupation)
    measure = momenta * momenta / (2.0 * np.pi**2)
    vacuum = float(np.sum(scaled_weights * measure / (4.0 * energy**3)))
    thermal = float(
        np.sum(
            scaled_weights
            * measure
            * (
                (particle_occupation + antiparticle_occupation) / (4.0 * energy**3)
                + (particle_factor + antiparticle_factor)
                / (4.0 * temperature * energy**2)
            )
        )
    )
    charge_density = float(
        sqrt(kinetic_prefactor)
        * np.sum(scaled_weights * measure * (particle_occupation - antiparticle_occupation))
    )
    total = vacuum + thermal
    values = vacuum, thermal, total, charge_density
    if not all(isfinite(value) for value in values) or vacuum <= 0.0 or thermal <= 0.0:
        raise FloatingPointError("charged one-loop bubble is not finite and positive")
    return values


def charged_euclidean_inverse(
    omega_n: float,
    momentum: float,
    effective_chemical_potential: float,
    mass: float,
) -> complex:
    """Return ``D_E^{-1}=(omega_n+i*mu_eff)^2+k^2+m^2``."""

    omega = _finite(omega_n, "omega_n")
    wave_number = _positive(momentum, "momentum")
    mu_eff = _finite(effective_chemical_potential, "effective_chemical_potential")
    energy_mass = _positive(mass, "mass")
    return complex((omega + 1j * mu_eff) ** 2 + wave_number * wave_number + energy_mass**2)


def finite_density_charged_vertex_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    reference_space_response: float | None = None,
    quadrature_order: int = 192,
    cutoff_multipliers: tuple[float, ...] = (8.0, 16.0, 32.0, 64.0, 128.0),
) -> FiniteDensityChargedO2VertexState:
    """Evaluate the charged normal-branch one-loop vertex scheme."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 64:
        raise ValueError("quadrature_order must be >= 64")
    if not cutoff_multipliers or any(float(value) <= 0.0 for value in cutoff_multipliers):
        raise ValueError("cutoff_multipliers must contain positive values")
    if tuple(sorted(float(value) for value in cutoff_multipliers)) != tuple(
        float(value) for value in cutoff_multipliers
    ):
        raise ValueError("cutoff_multipliers must be sorted")

    if reference_space_response is None:
        reference_space_response = config.eos.response.phi_equilibrium
    reference_space_response = _finite(reference_space_response, "reference_space_response")
    mass_sq = effective_mass_sq(space_response, config.eos)
    reference_mass_sq = effective_mass_sq(reference_space_response, config.eos)
    mass = sqrt(_positive(mass_sq, "effective mass squared"))
    reference_mass = sqrt(_positive(reference_mass_sq, "reference mass squared"))
    kinetic = _positive(config.eos.matter.matter_kinetic, "matter kinetic")
    effective_mu = sqrt(kinetic) * chemical_potential
    static_gap = mass_sq - effective_mu * effective_mu
    if static_gap <= 0.0:
        raise ValueError("finite-density charged lane requires the stable normal branch")
    coupling = _positive(config.eos.matter.matter_quartic, "quartic coupling")
    tree = _tree_vertex_tensor(coupling)
    contraction = 0.5 * np.einsum("abef,efcd->abcd", tree, tree)

    raw_vacuum: list[float] = []
    reference_vacuum: list[float] = []
    subtracted_vacuum: list[float] = []
    charged_thermal: list[float] = []
    renormalized_bubble: list[float] = []
    vertex_norms: list[float] = []
    correction_norms: list[float] = []
    charge_densities: list[float] = []
    for multiplier in cutoff_multipliers:
        cutoff = max(mass, reference_mass) * float(multiplier)
        vacuum, _, _ = _zero_external_bubble(
            temperature,
            mass,
            cutoff,
            quadrature_order=quadrature_order,
        )
        reference_value, _, _ = _zero_external_bubble(
            temperature,
            reference_mass,
            cutoff,
            quadrature_order=quadrature_order,
        )
        _, thermal_value, _, charge_density = _charged_bubble(
            temperature,
            mass,
            effective_mu,
            cutoff,
            kinetic_prefactor=kinetic,
            quadrature_order=quadrature_order,
        )
        subtracted = vacuum - reference_value
        bubble = subtracted + thermal_value
        correction = -1.5 * bubble * contraction
        vertex = tree + correction
        raw_vacuum.append(float(vacuum))
        reference_vacuum.append(float(reference_value))
        subtracted_vacuum.append(float(subtracted))
        charged_thermal.append(float(thermal_value))
        renormalized_bubble.append(float(bubble))
        vertex_norms.append(float(np.linalg.norm(vertex)))
        correction_norms.append(float(np.linalg.norm(correction)))
        charge_densities.append(float(charge_density))

    sample_momentum = 0.37 * mass
    sample_mode_energy = sqrt(sample_momentum * sample_momentum + mass * mass)
    particle_energy = sample_mode_energy - effective_mu
    antiparticle_energy = sample_mode_energy + effective_mu
    if particle_energy <= 0.0 or antiparticle_energy <= 0.0:
        raise FloatingPointError("charged KMS sample has a non-positive mode energy")
    particle_kms = equilibrium_kms_state(temperature, particle_energy, spectral_weight=1.0)
    antiparticle_kms = equilibrium_kms_state(temperature, antiparticle_energy, spectral_weight=1.0)
    particle_kms_residual = _relative(
        exp(particle_kms.log_kms_ratio), exp(particle_energy / temperature)
    )
    antiparticle_kms_residual = _relative(
        exp(antiparticle_kms.log_kms_ratio), exp(antiparticle_energy / temperature)
    )
    omega_n = 0.41 * mass
    wave_number = 0.29 * mass
    direct_inverse = charged_euclidean_inverse(
        omega_n, wave_number, effective_mu, mass
    )
    energy_at_wave_number = sqrt(wave_number * wave_number + mass * mass)
    factorized_inverse = (
        (omega_n + 1j * effective_mu) - 1j * energy_at_wave_number
    ) * ((omega_n + 1j * effective_mu) + 1j * energy_at_wave_number)
    static_inverse = charged_euclidean_inverse(0.0, 1.0e-12, effective_mu, mass)
    static_propagator_residual = _relative(static_inverse.real, static_gap)
    propagator_factorization_residual = abs(direct_inverse - factorized_inverse) / max(
        abs(direct_inverse), 1.0e-300
    )

    _, negative_thermal, _, negative_charge = _charged_bubble(
        temperature,
        mass,
        -effective_mu,
        max(mass, reference_mass) * float(cutoff_multipliers[-1]),
        kinetic_prefactor=kinetic,
        quadrature_order=quadrature_order,
    )
    charge_conjugation_bubble_residual = _relative(
        charged_thermal[-1], negative_thermal
    )
    charge_density_odd_residual = abs(charge_densities[-1] + negative_charge) / max(
        abs(charge_densities[-1]), 1.0e-300
    )
    values = (
        effective_mu,
        static_gap,
        *raw_vacuum,
        *reference_vacuum,
        *subtracted_vacuum,
        *charged_thermal,
        *renormalized_bubble,
        *vertex_norms,
        *correction_norms,
        *charge_densities,
        particle_kms_residual,
        antiparticle_kms_residual,
        static_propagator_residual,
        propagator_factorization_residual,
        charge_conjugation_bubble_residual,
        charge_density_odd_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("finite-density charged vertex state is not finite")
    return FiniteDensityChargedO2VertexState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        effective_chemical_potential=float(effective_mu),
        space_response=space_response,
        reference_space_response=reference_space_response,
        effective_mass=mass,
        reference_mass=reference_mass,
        quartic_coupling=coupling,
        static_gap=float(static_gap),
        sample_momentum=float(sample_momentum),
        sample_mode_energy=float(sample_mode_energy),
        particle_mode_energy=float(particle_energy),
        antiparticle_mode_energy=float(antiparticle_energy),
        raw_vacuum_values=tuple(raw_vacuum),
        reference_vacuum_values=tuple(reference_vacuum),
        subtracted_vacuum_values=tuple(subtracted_vacuum),
        charged_thermal_values=tuple(charged_thermal),
        renormalized_bubble_values=tuple(renormalized_bubble),
        renormalized_vertex_norms=tuple(vertex_norms),
        renormalized_correction_norms=tuple(correction_norms),
        thermal_charge_density=float(charge_densities[-1]),
        raw_vacuum_growth_ratio=float(raw_vacuum[-1] / raw_vacuum[0]),
        charged_thermal_cutoff_relative_change=_relative(
            charged_thermal[-1], charged_thermal[-2]
        ),
        renormalized_bubble_last_relative_change=_relative(
            renormalized_bubble[-1], renormalized_bubble[-2]
        ),
        renormalized_vertex_last_relative_change=_relative(
            vertex_norms[-1], vertex_norms[-2]
        ),
        static_propagator_residual=float(static_propagator_residual),
        propagator_factorization_residual=float(propagator_factorization_residual),
        particle_kms_residual=float(particle_kms_residual),
        antiparticle_kms_residual=float(antiparticle_kms_residual),
        charge_conjugation_bubble_residual=float(charge_conjugation_bubble_residual),
        charge_density_odd_residual=float(charge_density_odd_residual),
    )


def finite_density_charged_vertex_contract() -> dict[str, Any]:
    """Return equations, units, and non-promotion boundaries."""

    return {
        "status": FINITE_DENSITY_CHARGED_VERTEX_STATUS,
        "equations": {
            "charged_euclidean_propagator": "D_E^{-1}(omega_n,k)=(omega_n+i*mu_eff)^2+k^2+m_eff(Phi)^2",
            "particle_antiparticle_energies": "E_particle=sqrt(k^2+m_eff^2)-mu_eff; E_antiparticle=sqrt(k^2+m_eff^2)+mu_eff",
            "normal_branch": "|mu_eff|<m_eff(Phi)",
            "renormalized_charged_bubble": "B_ch^R(mu)=B_vac(m)-B_vac(m_ref)+B_thermal(m,mu_eff)",
            "renormalized_vertex": "Gamma_R^(4)=V-(B_s^R*(V.V)+B_t^R*(V.V)+B_u^R*(V.V))/2",
            "charge_density_witness": "n_ch=sqrt(Z)*integral[(n_B(E-mu_eff)-n_B(E+mu_eff)) d^3k/(2*pi)^3]",
            "charged_kms": "G_particle^>/G_particle^<=exp(beta*(E-mu_eff)); G_antiparticle^>/G_antiparticle^<=exp(beta*(E+mu_eff))",
        },
        "units": {
            "unit_lane": "natural",
            "temperature_mass_momentum_chemical_potential": "natural energy",
            "bubble_vertex": "dimensionless",
            "charge_density": "natural charge density",
            "Phi": "effective action response variable; not temperature",
        },
        "scheme": {
            "name": "mass-squared reference subtraction at Phi_* with charged thermal sector",
            "vacuum_counterterm_origin": "declared reference condition, not external measurement",
            "cutoff_role": "numerical regulator with finite-cutoff convergence witness",
            "domain": "homogeneous normal branch, zero external Euclidean momentum, finite mu",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace only; no backreaction",
            "R_obs": "separate observer record; not included",
        },
        "included": {
            "charged_propagator": True,
            "particle_antiparticle_thermal_weights": True,
            "finite_density_vertex_scheme": True,
            "charged_mode_kms_fdt_witness": True,
            "charge_conjugation_witness": True,
        },
        "excluded": {
            "unique_physical_renormalization": True,
            "condensed_or_two_fluid_branch": True,
            "full_interacting_sk_kms_action": True,
            "continuum_limit": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_dissipative_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "derivation_class": "action-derived finite-density normal charged propagator and one-loop reference-subtraction scheme; not physical scheme matching",
        "observable": "finite natural-unit charged one-loop vertex and mode-level KMS witness",
        "data_role": "ACTION_DERIVED_FINITE_DENSITY_CHARGED_VERTEX_SCHEME_NOT_PHYSICAL",
        "claim_boundary": "This closes one declared natural-unit finite-density charged normal-branch scheme. It does not select a unique physical renormalization, close the condensed/two-fluid sector, match a full interacting SK/KMS action, establish a continuum limit, provide physical Kubo transport, map Phi to SI temperature, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
    }


__all__ = [
    "FINITE_DENSITY_CHARGED_VERTEX_STATUS",
    "FiniteDensityChargedO2VertexState",
    "charged_euclidean_inverse",
    "finite_density_charged_vertex_state",
    "finite_density_charged_vertex_contract",
]
