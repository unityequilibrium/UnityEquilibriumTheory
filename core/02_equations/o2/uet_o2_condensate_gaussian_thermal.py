"""Fixed-background finite-temperature Gaussian O(2) condensate lane.

The quadratic condensate determinant is inherited from the declared natural-
unit O(2) action.  This module adds only the thermal Bose contribution of the
two positive-frequency quadratic branches on a tree-level condensate
background.  The background is not re-minimized after adding the thermal
determinant, and no vacuum counterterm, self-energy, normal-fluid current, or
SI conversion is supplied here.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_condensate_fluctuations import (
    O2CondensateFluctuationState,
    condensate_fluctuation_state,
    quadratic_mode_omega_sq,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig


@dataclass(frozen=True)
class O2CondensateGaussianThermalState:
    """Thermal Gaussian quasiparticle contribution in natural units."""

    temperature: float
    chemical_potential: float
    space_response: float
    condensate_control: float
    pressure: float
    entropy_density: float
    charge_density: float
    energy_density: float
    response_pressure_derivative: float
    low_branch_pressure: float
    high_branch_pressure: float
    low_branch_entropy: float
    high_branch_entropy: float
    low_branch_charge: float
    high_branch_charge: float
    momentum_cutoff: float
    quadrature_order: int
    unit_lane: str = "natural"
    fixed_tree_level_background: bool = True
    thermal_background_backreaction_included: bool = False
    vacuum_counterterm_included: bool = False
    interacting_self_energy_included: bool = False
    response_fluctuation_included: bool = False
    normal_two_fluid_completion: bool = False
    physical_kubo_coefficient_included: bool = False
    data_role: str = (
        "ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_NOT_FULL_UET_EOS"
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


def _bose_log(argument: float) -> float:
    """Return ``-log(1-exp(-argument))`` stably for positive argument."""

    x = _positive(argument, "Bose argument")
    if x > 50.0:
        return exp(-x)
    return -log(1.0 - exp(-x))


def _bose_occupation(argument: float) -> float:
    """Return ``1/(exp(argument)-1)`` stably for positive argument."""

    x = _positive(argument, "Bose argument")
    if x > 50.0:
        e = exp(-x)
        return e / (1.0 - e)
    return 1.0 / np.expm1(x)


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    return momenta, scaled_weights


def _cutoff(temperature: float, state: O2CondensateFluctuationState, cutoff_factor: float) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    return max(
        factor * temperature,
        factor * abs(state.chemical_potential),
        factor * sqrt(max(state.effective_mass_sq, 0.0)),
        factor * sqrt(state.zero_momentum_high_mode_sq),
        1.0,
    )


def _mode_data(
    wavenumber: float,
    state: O2CondensateFluctuationState,
    config: O2FiniteDensityEOSConfig,
) -> tuple[float, float, float, float, float, float]:
    """Return frequencies and their ``mu``/``Phi`` derivatives.

    The derivatives are analytic derivatives of the declared quadratic roots;
    they are not fitted to a thermal target curve.
    """

    k = _finite(wavenumber, "wavenumber")
    if k <= 0.0:
        raise ValueError("quadrature wavenumbers must be strictly positive")
    low_sq, high_sq = quadratic_mode_omega_sq(k, state, config)
    if low_sq <= 0.0 or high_sq <= 0.0:
        raise FloatingPointError("finite-T quadrature encountered a non-positive mode")

    z = float(config.matter.matter_kinetic)
    mu = state.chemical_potential
    mass_sq = state.effective_mass_sq
    a = state.condensate_control / z
    capital_a = a + 2.0 * mu * mu
    discriminant = capital_a * capital_a + 4.0 * mu * mu * k * k
    root = sqrt(discriminant)
    if root <= 0.0:
        raise FloatingPointError("quadratic mode discriminant must be positive")

    dcapital_a_dmu = 6.0 * mu
    droot_dmu = (capital_a * dcapital_a_dmu + 4.0 * mu * k * k) / root
    dcapital_a_dphi = (
        config.response.epsilon_nc * config.matter.response_coupling / z
    )
    droot_dphi = capital_a * dcapital_a_dphi / root

    low = sqrt(low_sq)
    high = sqrt(high_sq)
    dlow_sq_dmu = dcapital_a_dmu - droot_dmu
    dhigh_sq_dmu = dcapital_a_dmu + droot_dmu
    dlow_sq_dphi = dcapital_a_dphi - droot_dphi
    dhigh_sq_dphi = dcapital_a_dphi + droot_dphi
    return (
        low,
        high,
        dlow_sq_dmu / (2.0 * low),
        dhigh_sq_dmu / (2.0 * high),
        dlow_sq_dphi / (2.0 * low),
        dhigh_sq_dphi / (2.0 * high),
    )


def uet_o2_condensate_gaussian_thermal_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 70.0,
) -> O2CondensateGaussianThermalState:
    """Evaluate the thermal determinant on a fixed tree-level condensate.

    The returned pressure is the sum of ``-T log(1-exp(-omega/T))`` for the
    Goldstone and high branches.  The ``mu`` and ``Phi`` responses are analytic
    derivatives of this same fixed-background determinant.
    """

    temperature = _positive(temperature, "temperature")
    state = condensate_fluctuation_state(chemical_potential, space_response, config)
    cutoff = _cutoff(temperature, state, cutoff_factor)
    momenta, weights = _quadrature(int(quadrature_order), cutoff)
    measure = momenta * momenta / (2.0 * pi**2)

    branch_pressure = [0.0, 0.0]
    branch_entropy = [0.0, 0.0]
    branch_charge = [0.0, 0.0]
    response_derivative = 0.0
    for index, k in enumerate(momenta):
        low, high, low_mu, high_mu, low_phi, high_phi = _mode_data(
            float(k), state, config
        )
        frequencies = (low, high)
        mu_derivatives = (low_mu, high_mu)
        phi_derivatives = (low_phi, high_phi)
        for branch_index, (frequency, mu_derivative, phi_derivative) in enumerate(
            zip(frequencies, mu_derivatives, phi_derivatives)
        ):
            argument = frequency / temperature
            log_weight = _bose_log(argument)
            occupation = _bose_occupation(argument)
            weighted_measure = weights[index] * measure[index]
            branch_pressure[branch_index] += (
                weighted_measure * temperature * log_weight
            )
            branch_entropy[branch_index] += weighted_measure * (
                log_weight + argument * occupation
            )
            branch_charge[branch_index] += weighted_measure * (
                -occupation * mu_derivative
            )
            response_derivative += weighted_measure * (
                -occupation * phi_derivative
            )

    pressure = sum(branch_pressure)
    entropy = sum(branch_entropy)
    charge = sum(branch_charge)
    energy = -pressure + temperature * entropy + chemical_potential * charge
    values = (*branch_pressure, *branch_entropy, *branch_charge, pressure, entropy, charge, energy, response_derivative)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("Gaussian finite-temperature lane produced a non-finite value")
    return O2CondensateGaussianThermalState(
        temperature=temperature,
        chemical_potential=float(chemical_potential),
        space_response=float(space_response),
        condensate_control=state.condensate_control,
        pressure=pressure,
        entropy_density=entropy,
        charge_density=charge,
        energy_density=energy,
        response_pressure_derivative=response_derivative,
        low_branch_pressure=branch_pressure[0],
        high_branch_pressure=branch_pressure[1],
        low_branch_entropy=branch_entropy[0],
        high_branch_entropy=branch_entropy[1],
        low_branch_charge=branch_charge[0],
        high_branch_charge=branch_charge[1],
        momentum_cutoff=cutoff,
        quadrature_order=int(quadrature_order),
    )


def uet_o2_condensate_gaussian_thermal_contract() -> dict[str, Any]:
    """Return the finite-temperature Gaussian lane scope and exclusions."""

    return {
        "status": "ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE",
        "equations": {
            "condensed_control": "q=Z*mu^2-m_eff(Phi)^2 > 0",
            "quadratic_roots": "omega_+-^2=k^2+q/Z+2*mu^2 +- sqrt((q/Z+2*mu^2)^2+4*mu^2*k^2)",
            "thermal_grand_potential": "Omega_G=T integral sum_{a=+,-} log(1-exp(-omega_a/T)) d^3k/(2 pi)^3",
            "thermal_pressure": "p_G=-Omega_G",
            "entropy": "s_G=partial_T p_G at fixed tree-level background",
            "charge_response": "n_G=partial_mu p_G at fixed Phi and background branch",
            "response_derivative": "partial_Phi p_G at fixed tree-level background",
            "energy_identity": "epsilon_G=-p_G+T*s_G+mu*n_G",
        },
        "units": {
            "unit_lane": "natural",
            "T_mu_omega_k": "natural energy",
            "pressure_entropy_energy": "natural thermodynamic densities",
            "charge_density": "natural grand-canonical O(2) response density",
            "Phi": "fixed action response input; no SI map",
        },
        "scope": {
            "background": "tree-level homogeneous condensed O(2) state held fixed",
            "thermal_order": "Gaussian quadratic quasiparticle determinant",
            "vacuum_counterterm": "NOT_INCLUDED",
            "interacting_self_energy": "NOT_INCLUDED",
            "thermal_background_backreaction": "NOT_INCLUDED",
            "normal_two_fluid_completion": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "not identified with matter amplitude or O(2) charge",
            "Phi": "fixed effective response input; not temperature, metric, or particle",
            "R_gen": "derived history trace only; absent from the determinant and has no feedback",
            "R_obs": "not included in the action-derived lane",
        },
        "data_role": "ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_NOT_FULL_UET_EOS",
        "claim_boundary": "This closes only the natural-unit Gaussian thermal determinant of the two quadratic O(2) condensate branches on a fixed tree-level background. It does not close thermal background backreaction, vacuum renormalization, interacting self-energy, a normal two-fluid current, physical Kubo transport, microscopic SK/KMS matching, SI Phi calibration, external validation, or global UET closure.",
    }


__all__ = [
    "O2CondensateGaussianThermalState",
    "uet_o2_condensate_gaussian_thermal_state",
    "uet_o2_condensate_gaussian_thermal_contract",
]
