"""One-loop retarded self-energy no-go for physical dissipation.

For the local quartic O(2) action, the one-loop retarded two-point correction
is a tadpole.  It is independent of external frequency and real after the
declared vacuum subtraction, so its spectral/dissipative part vanishes.  This
artifact closes that structural question as a no-go and keeps the required
two-loop or microscopic open-system completion explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_STATUS = (
    "PASS_ACTION_DERIVED_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO"
)


@dataclass(frozen=True)
class OneLoopRetardedSelfEnergyNoGoState:
    """One-loop tadpole reality and absent-dissipation witnesses."""

    temperature: float
    chemical_potential: float
    effective_chemical_potential: float
    space_response: float
    effective_mass: float
    quartic_coupling: float
    cutoff: float
    thermal_tadpole: float
    retarded_frequency_grid: tuple[float, ...]
    self_energy_real: tuple[float, ...]
    self_energy_imaginary: tuple[float, ...]
    self_energy_spectral_density: tuple[float, ...]
    imaginary_part_maximum: float
    spectral_density_maximum: float
    external_frequency_independence_residual: float
    tadpole_finite: bool
    one_loop_retarded_self_energy_completed: bool = True
    dissipative_self_energy_completed: bool = False
    two_loop_sunset_or_microscopic_source_required: bool = True
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_NOT_TRANSPORT"


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


def _thermal_tadpole(
    temperature: float,
    mass: float,
    effective_chemical_potential: float,
    cutoff: float,
    *,
    quadrature_order: int,
) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(int(quadrature_order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    energy = np.sqrt(momenta * momenta + mass * mass)
    particle_argument = (energy - effective_chemical_potential) / temperature
    antiparticle_argument = (energy + effective_chemical_potential) / temperature
    if np.any(particle_argument <= 0.0) or np.any(antiparticle_argument <= 0.0):
        raise ValueError("one-loop tadpole requires the stable normal branch")
    particle = 1.0 / np.expm1(particle_argument)
    antiparticle = 1.0 / np.expm1(antiparticle_argument)
    measure = momenta * momenta / (2.0 * np.pi**2)
    value = float(
        np.sum(scaled_weights * measure * (particle + antiparticle) / (4.0 * energy))
    )
    if not isfinite(value) or value <= 0.0:
        raise FloatingPointError("thermal one-loop tadpole is not finite and positive")
    return value


def one_loop_retarded_self_energy_no_go_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 48.0,
    retarded_frequency_grid: tuple[float, ...] = (0.05, 0.1, 0.2, 0.4, 0.8),
) -> OneLoopRetardedSelfEnergyNoGoState:
    """Evaluate the real one-loop tadpole and close its dissipation no-go."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 64:
        raise ValueError("quadrature_order must be >= 64")
    if not retarded_frequency_grid or tuple(sorted(float(value) for value in retarded_frequency_grid)) != tuple(
        float(value) for value in retarded_frequency_grid
    ):
        raise ValueError("retarded_frequency_grid must be non-empty and sorted")
    if any(float(value) <= 0.0 for value in retarded_frequency_grid):
        raise ValueError("retarded_frequency_grid must contain positive frequencies")
    mass_sq = effective_mass_sq(space_response, config.eos)
    mass = sqrt(_positive(mass_sq, "effective mass squared"))
    kinetic = _positive(config.eos.matter.matter_kinetic, "matter kinetic")
    effective_mu = sqrt(kinetic) * chemical_potential
    if abs(effective_mu) >= mass:
        raise ValueError("one-loop tadpole no-go requires the stable normal branch")
    coupling = _positive(config.eos.matter.matter_quartic, "quartic coupling")
    cutoff = max(cutoff_factor * temperature, cutoff_factor * mass, cutoff_factor * abs(effective_mu), 1.0)
    thermal_tadpole = _thermal_tadpole(
        temperature,
        mass,
        effective_mu,
        cutoff,
        quadrature_order=quadrature_order,
    )
    real_value = 3.0 * coupling * thermal_tadpole
    frequencies = tuple(float(value) for value in retarded_frequency_grid)
    real_values = tuple(real_value for _ in frequencies)
    imaginary_values = tuple(0.0 for _ in frequencies)
    spectral_values = tuple(0.0 for _ in frequencies)
    values = (mass, effective_mu, thermal_tadpole, real_value, *frequencies)
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("one-loop retarded self-energy no-go is not finite")
    return OneLoopRetardedSelfEnergyNoGoState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        effective_chemical_potential=effective_mu,
        space_response=space_response,
        effective_mass=mass,
        quartic_coupling=coupling,
        cutoff=float(cutoff),
        thermal_tadpole=float(thermal_tadpole),
        retarded_frequency_grid=frequencies,
        self_energy_real=real_values,
        self_energy_imaginary=imaginary_values,
        self_energy_spectral_density=spectral_values,
        imaginary_part_maximum=0.0,
        spectral_density_maximum=0.0,
        external_frequency_independence_residual=0.0,
        tadpole_finite=True,
    )


def one_loop_retarded_self_energy_no_go_contract() -> dict[str, Any]:
    """Return the one-loop no-go equations and required next completion."""

    return {
        "status": ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_STATUS,
        "equations": {
            "one_loop_retarded_self_energy": "Sigma_R^(1)(omega,k)=3*lambda*[I_vac^R(m_eff)+I_thermal(T,mu_eff)]",
            "tadpole_thermal_piece": "I_thermal=integral[(n_B(E-mu_eff)+n_B(E+mu_eff))/(4*E)] d^3k/(2*pi)^3",
            "one_loop_dissipative_part": "Im Sigma_R^(1)(omega,k)=0 for the local quartic tadpole",
            "one_loop_spectral_density": "rho_Sigma^(1)(omega,k)=-2*Im Sigma_R^(1)=0",
            "required_completion": "physical dissipation requires a two-loop sunset or a separately matched microscopic open-system kernel",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_mass_frequency": "natural energy/inverse time",
            "thermal_tadpole": "natural mass squared",
            "self_energy": "natural mass squared",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived one-loop local quartic tadpole with real thermal contribution; structural no-go for one-loop dissipation",
        "observable": "one-loop real self-energy boundary and zero dissipative spectral part",
        "data_role": "ACTION_DERIVED_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_NOT_TRANSPORT",
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "closed_as_no_go": "the local one-loop tadpole cannot provide a nonzero retarded dissipative spectral density",
        "required_next_branch": "two-loop sunset self-energy or source-locked microscopic open-system matching",
        "excluded": {
            "physical_retarded_self_energy": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_dissipative_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes only the structural one-loop no-go: a local quartic tadpole is real and frequency independent, so it cannot supply physical dissipation. It does not close the two-loop/microscopic retarded self-energy, transport, entropy-current balance, SI Phi map, alpha_Phi_K, TTG validation, or Full Topic 13.",
    }


__all__ = [
    "ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO_STATUS",
    "OneLoopRetardedSelfEnergyNoGoState",
    "one_loop_retarded_self_energy_no_go_state",
    "one_loop_retarded_self_energy_no_go_contract",
]
