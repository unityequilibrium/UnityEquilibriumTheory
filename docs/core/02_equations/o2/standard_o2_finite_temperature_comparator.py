"""Standard finite-temperature O(2) normal-branch comparator.

This module evaluates the thermal excitation contribution of a free complex
scalar at finite temperature and chemical potential.  The UET action enters
only through its declared effective mass ``m_eff(Phi)``.  The result is a
standard thermodynamic comparator, not a finite-temperature UET derivation,
normal-fluid closure, Kubo coefficient, or SI observable map.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from .uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)


@dataclass(frozen=True)
class StandardO2ThermalNormalState:
    """Thermal excitation contribution in natural units."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    pressure: float
    charge_density: float
    entropy_density: float
    energy_density: float
    charge_susceptibility: float
    momentum_cutoff: float
    quadrature_order: int
    data_role: str = "STANDARD_THERMAL_QFT_COMPARATOR_NOT_UET_CLOSURE"


def _positive_finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _bose_occupation(argument: float) -> float:
    """Return 1/(exp(argument)-1) for a strictly positive argument."""

    x = _positive_finite(argument, "Bose argument")
    if x > 50.0:
        e = exp(-x)
        return e / (1.0 - e)
    return 1.0 / np.expm1(x)


def _bose_log(argument: float) -> float:
    """Return -log(1-exp(-argument)) stably for argument > 0."""

    x = _positive_finite(argument, "Bose argument")
    return -log(1.0 - exp(-x))


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    return momenta, scaled_weights


def standard_o2_normal_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 50.0,
) -> StandardO2ThermalNormalState:
    """Evaluate the ideal complex-scalar normal-branch thermal contribution.

    The domain is the normal Bose branch ``Z*mu^2 < m_eff(Phi)^2``.  The
    condensate and zero-point terms are intentionally excluded so the output
    cannot be mistaken for a completed finite-temperature UET EOS.
    """

    temperature = _positive_finite(temperature, "temperature")
    cutoff_factor = _positive_finite(cutoff_factor, "cutoff_factor")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(space_response, config))
    if not isfinite(mass_sq) or mass_sq <= 0.0:
        raise ValueError("normal comparator requires positive effective mass squared")
    mass = sqrt(mass_sq)
    kinetic = _positive_finite(config.matter.matter_kinetic, "matter_kinetic")
    if kinetic * chemical_potential**2 >= mass_sq:
        raise ValueError("normal comparator requires Z*mu^2 < m_eff(Phi)^2")

    cutoff = max(cutoff_factor * temperature, cutoff_factor * mass, cutoff_factor * abs(chemical_potential), 1.0)
    momenta, weights = _quadrature(int(quadrature_order), cutoff)
    energy = np.sqrt(momenta * momenta + mass_sq)
    argument_minus = (energy - chemical_potential) / temperature
    argument_plus = (energy + chemical_potential) / temperature
    measure = momenta * momenta / (2.0 * pi**2)

    n_minus = np.array([_bose_occupation(float(value)) for value in argument_minus])
    n_plus = np.array([_bose_occupation(float(value)) for value in argument_plus])
    log_minus = np.array([_bose_log(float(value)) for value in argument_minus])
    log_plus = np.array([_bose_log(float(value)) for value in argument_plus])

    pressure = temperature * float(np.sum(weights * measure * (log_minus + log_plus)))
    charge_density = float(np.sum(weights * measure * (n_minus - n_plus)))
    entropy_integrand = (
        log_minus
        + argument_minus * n_minus
        + log_plus
        + argument_plus * n_plus
    )
    entropy_density = float(np.sum(weights * measure * entropy_integrand))
    energy_density = -pressure + temperature * entropy_density + chemical_potential * charge_density
    susceptibility = float(
        np.sum(
            weights
            * measure
            * (
                n_minus * (1.0 + n_minus) / temperature
                + n_plus * (1.0 + n_plus) / temperature
            )
        )
    )
    values = (pressure, charge_density, entropy_density, energy_density, susceptibility)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("thermal comparator produced a non-finite value")
    return StandardO2ThermalNormalState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=mass,
        pressure=pressure,
        charge_density=charge_density,
        entropy_density=entropy_density,
        energy_density=energy_density,
        charge_susceptibility=susceptibility,
        momentum_cutoff=cutoff,
        quadrature_order=int(quadrature_order),
    )


def standard_o2_thermal_comparator_contract() -> dict[str, Any]:
    """Return the comparator scope and non-promotion boundary."""

    return {
        "status": "STANDARD_FINITE_TEMPERATURE_O2_NORMAL_COMPARATOR",
        "equations": {
            "dispersion": "E_k = sqrt(k^2 + m_eff(Phi)^2)",
            "pressure": "p_T = T integral [L(E_k-mu)+L(E_k+mu)] d^3k/(2 pi)^3",
            "occupation": "n_B(x) = 1/(exp(x/T)-1)",
            "charge_density": "n_T = integral [n_B(E_k-mu)-n_B(E_k+mu)] d^3k/(2 pi)^3",
            "entropy_density": "s_T = partial p_T / partial T",
            "energy_density": "epsilon_T = -p_T + T*s_T + mu*n_T",
            "susceptibility": "chi_T = partial n_T / partial mu >= 0",
        },
        "domain": {
            "unit_lane": "natural",
            "temperature": "T > 0",
            "normal_branch": "Z*mu^2 < m_eff(Phi)^2",
            "zero_point_term": "excluded",
            "condensate_term": "excluded",
        },
        "observable": "standard finite-temperature normal-branch pressure, charge, entropy, and energy contribution",
        "data_role": "STANDARD_THERMAL_QFT_COMPARATOR_NOT_UET_CLOSURE",
        "uET_boundary": {
            "Phi": "enters only through the declared m_eff(Phi) input; not temperature",
            "C": "not relabeled as charge density",
            "R_gen": "not used as state or feedback",
            "R_obs": "not part of the comparator state",
            "alpha_Phi_K": "not emitted",
            "physical_Kubo_coefficient": "not emitted",
            "si_map": "not emitted",
        },
        "next_controller": "derive or source-lock finite-temperature UET effective action, condensate/normal two-fluid sector, Kubo coefficients, and SI Phi observable map",
    }


__all__ = [
    "StandardO2ThermalNormalState",
    "standard_o2_normal_state",
    "standard_o2_thermal_comparator_contract",
]
