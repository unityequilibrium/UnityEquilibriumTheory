"""Continuum on-shell sunset-cut lane for the Topic 13 O(2) response.

This module evaluates the neutral, finite-temperature elastic 2-to-2 phase
space cut at zero external spatial momentum.  The radial bath momentum and
center-of-mass scattering angle are integrated with independent
Gauss-Legendre rules.  The result is an action-derived on-shell cut with
explicit cutoff and quadrature convergence checks.

It is not a complete 1PI retarded self-energy: the real-part subtraction,
off-shell analytic continuation, regulator matching, physical Kubo
coefficient, and SI observable map remain outside this lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


CONTINUUM_SUNSET_CUT_STATUS = "PASS_ACTION_DERIVED_CONTINUUM_SUNSET_CUT_LANE"
CONVERGENCE_THRESHOLD = 1.0e-8


@dataclass(frozen=True)
class ContinuumSunsetCutState:
    """Neutral p=0 continuum cut and its numerical controls."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    external_energy: float
    quartic_coupling: float
    radial_cutoff: float
    radial_order: int
    center_of_mass_order: int
    greater_cut: float
    lesser_cut: float
    spectral_cut: float
    noise_cut: float
    kms_ratio: float
    kms_target_ratio: float
    kms_residual: float
    positive_spectral_cut: bool
    radial_convergence_residual: float
    angular_convergence_residual: float
    cutoff_convergence_residual: float
    convergence_threshold: float
    convergence_passed: bool
    continuum_sunset_cut_completed: bool = True
    continuum_sunset_self_energy_completed: bool = False
    full_1pi_retarded_self_energy_completed: bool = False
    real_part_subtraction_completed: bool = False
    off_shell_matching_completed: bool = False
    physical_retarded_self_energy_completed: bool = False
    covariant_entropy_current_completed: bool = False
    physical_heat_flux_balance_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_INTERNAL_NEUTRAL_CONTINUUM_ON_SHELL_CUT_NO_HOLDOUT"
    )


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


def _validate_order(value: int, name: str) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < 24:
        raise ValueError(f"{name} must be an integer >= 24")
    return int(value)


def _bose_from_energy(energy: float, temperature: float) -> float:
    argument = _positive(energy / temperature, "beta energy")
    return exp(-argument) if argument > 50.0 else 1.0 / expm1(argument)


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return 0.5 * cutoff * (nodes + 1.0), 0.5 * cutoff * weights


def _relative_change(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def _cm_bose_averages(
    momentum: float,
    mass: float,
    temperature: float,
    angular_order: int,
) -> tuple[float, float]:
    """Return CM-angle averages of greater and lesser final-state factors."""

    energy = sqrt(momentum * momentum + mass * mass)
    invariant_s = 2.0 * mass * (mass + energy)
    root_s = sqrt(invariant_s)
    energy_star = 0.5 * root_s
    momentum_star = sqrt(max(0.25 * invariant_s - mass * mass, 0.0))
    beta = momentum / (mass + energy)
    gamma = (mass + energy) / root_s
    nodes, weights = np.polynomial.legendre.leggauss(angular_order)
    greater = 0.0
    lesser = 0.0
    for cosine, weight in zip(nodes, weights):
        energy_three = gamma * (energy_star + beta * momentum_star * float(cosine))
        energy_four = gamma * (energy_star - beta * momentum_star * float(cosine))
        occupation_three = _bose_from_energy(energy_three, temperature)
        occupation_four = _bose_from_energy(energy_four, temperature)
        greater += 0.5 * float(weight) * (1.0 + occupation_three) * (1.0 + occupation_four)
        lesser += 0.5 * float(weight) * occupation_three * occupation_four
    return float(greater), float(lesser)


def _integrate_cut(
    temperature: float,
    mass: float,
    quartic: float,
    radial_order: int,
    angular_order: int,
    cutoff: float,
) -> tuple[float, float]:
    """Integrate the declared neutral elastic cut in the p=0 convention."""

    momenta, weights = _quadrature(radial_order, cutoff)
    greater = 0.0
    lesser = 0.0
    for momentum, weight in zip(momenta, weights):
        k = float(momentum)
        bath_energy = sqrt(k * k + mass * mass)
        invariant_s = 2.0 * mass * (mass + bath_energy)
        relative_velocity = k / bath_energy
        cross_section = quartic * quartic / (16.0 * pi * invariant_s)
        final_greater, final_lesser = _cm_bose_averages(
            k, mass, temperature, angular_order
        )
        measure = float(weight) * k * k / (2.0 * pi * pi)
        bath_occupation = _bose_from_energy(bath_energy, temperature)
        greater += measure * bath_occupation * relative_velocity * cross_section * final_greater
        lesser += (
            measure
            * (1.0 + bath_occupation)
            * relative_velocity
            * cross_section
            * final_lesser
        )
    return float(greater), float(lesser)


def continuum_sunset_cut_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 32,
    center_of_mass_order: int = 32,
    cutoff_factor: float = 20.0,
) -> ContinuumSunsetCutState:
    """Evaluate the neutral continuum on-shell 2-to-2 sunset cut.

    The external momentum is fixed to ``p=(E_p, 0)`` with ``E_p=m_eff``.
    This is a neutral normal-state lane, so a nonzero chemical potential is
    intentionally rejected rather than silently treated as a charged result.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) > 1.0e-14:
        raise ValueError("continuum sunset cut lane locks chemical_potential=0")
    space_response = _finite(space_response, "space_response")
    radial_order = _validate_order(radial_order, "radial_order")
    center_of_mass_order = _validate_order(
        center_of_mass_order, "center_of_mass_order"
    )
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    mass_sq = effective_mass_sq(space_response, config.eos)
    if mass_sq <= 0.0:
        raise ValueError("continuum neutral cut requires positive effective mass squared")
    mass = sqrt(mass_sq)
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    cutoff = max(cutoff_factor * temperature, cutoff_factor * mass, 1.0)

    greater, lesser = _integrate_cut(
        temperature, mass, quartic, radial_order, center_of_mass_order, cutoff
    )
    radial_refined = _integrate_cut(
        temperature, mass, quartic, radial_order + 16, center_of_mass_order, cutoff
    )
    angular_refined = _integrate_cut(
        temperature, mass, quartic, radial_order, center_of_mass_order + 16, cutoff
    )
    cutoff_refined = _integrate_cut(
        temperature,
        mass,
        quartic,
        radial_order,
        center_of_mass_order,
        max((cutoff_factor + 4.0) * temperature, (cutoff_factor + 4.0) * mass, 1.0),
    )
    radial_residual = max(
        _relative_change(greater, radial_refined[0]),
        _relative_change(lesser, radial_refined[1]),
    )
    angular_residual = max(
        _relative_change(greater, angular_refined[0]),
        _relative_change(lesser, angular_refined[1]),
    )
    cutoff_residual = max(
        _relative_change(greater, cutoff_refined[0]),
        _relative_change(lesser, cutoff_refined[1]),
    )
    external_energy = mass
    kms_ratio = greater / lesser
    kms_target = exp(external_energy / temperature)
    kms_residual = _relative_change(kms_ratio, kms_target)
    spectral = 2.0 * external_energy * (greater - lesser)
    noise = 2.0 * external_energy * (greater + lesser)
    values = (
        greater,
        lesser,
        spectral,
        noise,
        kms_ratio,
        kms_target,
        kms_residual,
        radial_residual,
        angular_residual,
        cutoff_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("continuum sunset cut state is not finite")
    convergence_passed = max(radial_residual, angular_residual, cutoff_residual) <= CONVERGENCE_THRESHOLD
    return ContinuumSunsetCutState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=mass,
        external_energy=external_energy,
        quartic_coupling=quartic,
        radial_cutoff=cutoff,
        radial_order=radial_order,
        center_of_mass_order=center_of_mass_order,
        greater_cut=greater,
        lesser_cut=lesser,
        spectral_cut=spectral,
        noise_cut=noise,
        kms_ratio=kms_ratio,
        kms_target_ratio=kms_target,
        kms_residual=kms_residual,
        positive_spectral_cut=spectral > 0.0,
        radial_convergence_residual=radial_residual,
        angular_convergence_residual=angular_residual,
        cutoff_convergence_residual=cutoff_residual,
        convergence_threshold=CONVERGENCE_THRESHOLD,
        convergence_passed=convergence_passed,
    )


def continuum_sunset_cut_contract() -> dict[str, Any]:
    """Return the continuum-cut equations and its non-promotion boundary."""

    return {
        "status": CONTINUUM_SUNSET_CUT_STATUS,
        "equations": {
            "external_kinematics": "p=(E_p,0,0,0), E_p=m_eff, chemical_potential=0",
            "greater_cut": (
                "Gamma_>^cut=integral_0^Lambda d^3k/(2*pi)^3 n_k v_rel "
                "sigma_22 <(1+n_3)(1+n_4)>_CM"
            ),
            "lesser_cut": (
                "Gamma_<^cut=integral_0^Lambda d^3k/(2*pi)^3 (1+n_k) v_rel "
                "sigma_22 <n_3 n_4>_CM"
            ),
            "action_cross_section": "sigma_22=lambda^2/(16*pi*s), s=2*m_eff*(m_eff+E_k)",
            "cm_energies": "E_3,4=gamma_cm*(sqrt(s)/2 +/- beta_cm*p_star*cos(theta_cm))",
            "kms_ratio": "Gamma_>^cut/Gamma_<^cut=exp(beta_th*E_p) from four-momentum conservation",
            "spectral_cut": "rho_cut=2*E_p*(Gamma_>^cut-Gamma_<^cut)",
            "noise_cut": "N_cut=2*E_p*(Gamma_>^cut+Gamma_<^cut)",
            "convergence": "compare radial order, CM-angle order, and Lambda cutoff refinements",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass_momentum_energy": "energy",
            "cut_rate": "formal natural-unit on-shell phase-space rate",
            "spectral_and_noise_cut": "formal natural-unit cut normalization",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived neutral elastic 2-to-2 on-shell phase-space quadrature "
            "using the declared tree-level constant-amplitude cross-section branch"
        ),
        "observable": (
            "positive on-shell spectral-cut weight, greater/lesser KMS ratio, "
            "and radial/angular/cutoff convergence residuals"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_CONTINUUM_CUT_NO_SOURCE_ROWS_NO_HOLDOUT",
        "excluded": {
            "full_1PI_retarded_self_energy": True,
            "real_part_subtraction": True,
            "off_shell_matching": True,
            "regulator_scheme_matching": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current": True,
            "physical_heat_flux": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only the neutral p=0 continuum on-shell 2-to-2 sunset-cut "
            "integral in the declared natural-unit convention, with numerical "
            "convergence and KMS checks. It does not close the full 1PI retarded "
            "self-energy, real-part subtraction, off-shell matching, physical "
            "transport, entropy-current balance, SI Phi mapping, alpha_Phi_K, "
            "TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "CONVERGENCE_THRESHOLD",
    "CONTINUUM_SUNSET_CUT_STATUS",
    "ContinuumSunsetCutState",
    "continuum_sunset_cut_contract",
    "continuum_sunset_cut_state",
]
