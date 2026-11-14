"""Continuum natural-unit relative-flow response for Topic 13.

This module removes the finite momentum cutoff from the declared screened
contact channel by using a compactified radial quadrature on ``[0, infinity)``.
The thermal Bose weights make the response integral convergent, so the result
tests a continuum *thermal contact-channel* lane rather than extrapolating the
non-convergent finite-cutoff collocation operator.

The contact coupling is still the tree/action input.  No vacuum loop
renormalization, physical Kubo coefficient, SI conversion, or Phi calibration
is claimed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import expm1, isfinite, pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
    finite_temperature_o2_state,
)


CONTINUUM_RELATIVE_FLOW_STATUS = (
    "PASS_ACTION_DERIVED_CONTINUUM_RELATIVE_FLOW_KUBO_LANE"
)
CONTINUUM_ACCEPTANCE_THRESHOLD = 1.0e-2
DEFAULT_RADIAL_ORDERS = (24, 32, 40)
DEFAULT_ANGULAR_ORDER = 24
DEFAULT_ANGULAR_REFINED_ORDER = 36


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


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _bose(energy: np.ndarray, temperature: float) -> np.ndarray:
    argument = np.asarray(energy, dtype=float) / float(temperature)
    if np.any(argument <= 0.0) or not np.all(np.isfinite(argument)):
        raise FloatingPointError("continuum Bose argument must be positive and finite")
    result = np.empty_like(argument)
    high = argument > 50.0
    result[high] = np.exp(-argument[high])
    result[~high] = 1.0 / np.expm1(argument[~high])
    return result


def _compactified_radial_quadrature(
    order: int,
    scale: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Map Gauss-Legendre nodes from ``u in (0,1)`` to ``k in (0,infinity)``."""

    order = _integer(order, "radial_order", 16)
    scale = _positive(scale, "radial_scale")
    nodes, weights = np.polynomial.legendre.leggauss(order)
    u = 0.5 * (nodes + 1.0)
    du = 0.5 * weights
    momentum = scale * u / (1.0 - u)
    jacobian = scale / (1.0 - u) ** 2
    return momentum, du * jacobian


def _mode_arrays(
    momentum: np.ndarray,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> tuple[np.ndarray, np.ndarray]:
    energies = np.asarray(
        [
            condensed_quasiparticle_energies(
                float(value), chemical_potential, space_response, config
            )
            for value in momentum
        ],
        dtype=float,
    ).T
    velocities = np.zeros_like(energies)
    for index, value in enumerate(momentum):
        step = 1.0e-5 * max(1.0, float(value))
        lower = max(0.0, float(value) - step)
        upper = float(value) + step
        lower_energy = np.asarray(
            condensed_quasiparticle_energies(
                lower, chemical_potential, space_response, config
            ),
            dtype=float,
        )
        upper_energy = np.asarray(
            condensed_quasiparticle_energies(
                upper, chemical_potential, space_response, config
            ),
            dtype=float,
        )
        velocities[:, index] = (upper_energy - lower_energy) / (upper - lower)
    if not np.all(np.isfinite(velocities)):
        raise FloatingPointError("continuum quasiparticle velocities are not finite")
    return energies, velocities


@dataclass(frozen=True)
class ContinuumRelativeFlowState:
    """Converged continuum thermal contact-channel response state."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    effective_mass: float
    condensate_amplitude: float
    tree_radial_screening_sq: float
    radial_orders: tuple[int, ...]
    angular_order: int
    angular_refined_order: int
    radial_scale: float
    mode_susceptibility: tuple[float, float]
    mode_rate: tuple[float, float]
    relative_susceptibility: float
    relative_collision_rate: float
    dc_relative_response: float
    radial_relative_collision_rates: tuple[float, ...]
    radial_dc_responses: tuple[float, ...]
    radial_max_relative_change: float
    angular_refined_relative_change: float
    scale_refined_relative_change: float
    collision_operator: tuple[tuple[float, float], tuple[float, float]]
    collision_eigenvalues: tuple[float, float]
    common_flow_conservation_residual: float
    source_common_mode_residual: float
    symmetric_kernel_residual: float
    retarded_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    spectral_density: tuple[float, ...]
    kms_ratio: tuple[float, ...]
    kms_target_ratio: tuple[float, ...]
    kms_residual: float
    fdt_residual: float
    entropy_production_at_unit_force: float
    continuum_integrals_finite: bool
    continuum_convergence_passes: bool
    finite_cutoff_used: bool = False
    loop_renormalized_vertex_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_phi_k_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_CONTINUUM_THERMAL_CONTACT_RESPONSE_NOT_PHYSICAL_KUBO"
    )


def _continuum_response(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    condensate_amplitude: float,
    quartic_coupling: float,
    radial_order: int,
    angular_order: int,
    radial_scale: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    momentum, weights = _compactified_radial_quadrature(radial_order, radial_scale)
    energies, velocities = _mode_arrays(
        momentum, chemical_potential, space_response, config
    )
    occupations = _bose(energies, temperature)
    dndenergy = occupations * (1.0 + occupations) / temperature
    measure = momentum * momentum / (2.0 * pi**2)
    mode_susceptibility = np.asarray(
        [
            np.sum(
                weights
                * measure
                * momentum**2
                * dndenergy[mode]
                * velocities[mode] ** 2
            )
            / 3.0
            for mode in range(2)
        ],
        dtype=float,
    )
    if not np.all(np.isfinite(mode_susceptibility)) or np.any(mode_susceptibility <= 0.0):
        raise FloatingPointError("continuum mode susceptibilities must be positive")

    angular_nodes, angular_weights = np.polynomial.legendre.leggauss(
        _integer(angular_order, "angular_order", 16)
    )
    screening_sq = _positive(
        2.0 * quartic_coupling * condensate_amplitude**2,
        "tree_radial_screening_sq",
    )
    partner_measure = weights * measure
    mode_rates = np.zeros(2, dtype=float)
    for mode_a in range(2):
        rate_integrand = np.zeros_like(momentum)
        energy_a = energies[mode_a][:, None, None]
        velocity_a = velocities[mode_a][:, None, None]
        occupation_a = occupations[mode_a][:, None]
        momentum_a = momentum[:, None, None]
        for mode_b in range(2):
            energy_b = energies[mode_b][None, :, None]
            velocity_b = velocities[mode_b][None, :, None]
            momentum_b = momentum[None, :, None]
            cosine = angular_nodes[None, None, :]
            relative_speed = np.sqrt(
                velocity_a**2
                + velocity_b**2
                - 2.0 * velocity_a * velocity_b * cosine
            )
            s_medium = 2.0 * energy_a * energy_b * (1.0 - cosine)
            cross_section = quartic_coupling**2 / (
                16.0 * pi * (s_medium + screening_sq)
            )
            angular_average = np.sum(
                0.5 * angular_weights[None, None, :]
                * relative_speed
                * cross_section,
                axis=2,
            )
            partner_factor = occupations[mode_b][None, :] * (1.0 + occupation_a)
            rate_integrand += np.sum(
                angular_average * partner_measure[None, :] * partner_factor,
                axis=1,
            )
        mode_rates[mode_a] = float(
            np.sum(
                weights
                * measure
                * momentum**2
                * dndenergy[mode_a]
                * velocities[mode_a] ** 2
                * rate_integrand
            )
            / mode_susceptibility[mode_a]
        )
    if not np.all(np.isfinite(mode_rates)) or np.any(mode_rates <= 0.0):
        raise FloatingPointError("continuum mode collision rates must be positive")
    return mode_susceptibility, mode_rates, screening_sq


def _relative_change(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def continuum_relative_flow_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_orders: tuple[int, ...] = DEFAULT_RADIAL_ORDERS,
    angular_order: int = DEFAULT_ANGULAR_ORDER,
    angular_refined_order: int = DEFAULT_ANGULAR_REFINED_ORDER,
    radial_scale_factor: float = 1.0,
    refined_scale_factor: float = 0.5,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
) -> ContinuumRelativeFlowState:
    """Evaluate a compactified ``[0, infinity)`` condensed response lane."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if len(radial_orders) < 2 or tuple(sorted(radial_orders)) != tuple(radial_orders):
        raise ValueError("radial_orders must be sorted and contain at least two orders")
    radial_orders = tuple(_integer(value, "radial_order", 16) for value in radial_orders)
    angular_order = _integer(angular_order, "angular_order", 16)
    angular_refined_order = _integer(
        angular_refined_order, "angular_refined_order", angular_order
    )
    radial_scale_factor = _positive(radial_scale_factor, "radial_scale_factor")
    refined_scale_factor = _positive(refined_scale_factor, "refined_scale_factor")
    ratios = tuple(_finite(value, "retarded frequency ratio") for value in retarded_frequency_over_rate)
    if not ratios or ratios[0] != 0.0 or tuple(sorted(ratios)) != ratios or any(value < 0.0 for value in ratios):
        raise ValueError("retarded frequency ratios must be sorted, non-negative, and start at zero")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    state = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    if state.branch != "condensed":
        raise ValueError("continuum relative-flow lane requires the condensed branch")
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    base_scale = max(
        temperature,
        state.effective_mass,
        sqrt(quartic) * state.condensate_amplitude,
        1.0e-6,
    )

    responses_by_order: list[float] = []
    rates_by_order: list[float] = []
    last_susceptibility: np.ndarray | None = None
    last_rates: np.ndarray | None = None
    screening_sq = 0.0
    for order in radial_orders:
        susceptibility, rates, screening_sq = _continuum_response(
            temperature,
            chemical_potential,
            space_response,
            config,
            state.condensate_amplitude,
            quartic,
            order,
            angular_order,
            base_scale * radial_scale_factor,
        )
        relative_susceptibility = float(
            susceptibility[0] * susceptibility[1] / np.sum(susceptibility)
        )
        relative_rate = float(np.dot(susceptibility, rates) / np.sum(susceptibility))
        responses_by_order.append(relative_susceptibility / relative_rate)
        rates_by_order.append(relative_rate)
        last_susceptibility = susceptibility
        last_rates = rates
    assert last_susceptibility is not None and last_rates is not None

    relative_susceptibility = float(
        last_susceptibility[0]
        * last_susceptibility[1]
        / np.sum(last_susceptibility)
    )
    relative_rate = float(
        np.dot(last_susceptibility, last_rates) / np.sum(last_susceptibility)
    )
    dc_response = relative_susceptibility / relative_rate
    refined_susceptibility, refined_rates, _ = _continuum_response(
        temperature,
        chemical_potential,
        space_response,
        config,
        state.condensate_amplitude,
        quartic,
        radial_orders[-1],
        angular_refined_order,
        base_scale * radial_scale_factor,
    )
    refined_angular_response = float(
        refined_susceptibility[0]
        * refined_susceptibility[1]
        / np.sum(refined_susceptibility)
        / (np.dot(refined_susceptibility, refined_rates) / np.sum(refined_susceptibility))
    )
    angular_change = _relative_change(refined_angular_response, dc_response)
    scale_susceptibility, scale_rates, _ = _continuum_response(
        temperature,
        chemical_potential,
        space_response,
        config,
        state.condensate_amplitude,
        quartic,
        radial_orders[-1],
        angular_order,
        base_scale * refined_scale_factor,
    )
    scale_response = float(
        scale_susceptibility[0]
        * scale_susceptibility[1]
        / np.sum(scale_susceptibility)
        / (np.dot(scale_susceptibility, scale_rates) / np.sum(scale_susceptibility))
    )
    scale_change = _relative_change(scale_response, dc_response)
    radial_changes = tuple(
        _relative_change(previous, current)
        for previous, current in zip(responses_by_order, responses_by_order[1:])
    )
    radial_max_change = max(radial_changes, default=0.0)

    operator = relative_rate * np.asarray(((1.0, -1.0), (-1.0, 1.0)), dtype=float)
    eigenvalues = np.linalg.eigvalsh(operator)
    source = sqrt(relative_susceptibility) * np.asarray((1.0, -1.0), dtype=float)
    frequencies = tuple(relative_rate * ratio for ratio in ratios)
    responses = tuple(
        2.0 * relative_susceptibility / complex(2.0 * relative_rate, -frequency)
        for frequency in frequencies
    )
    real_response = tuple(float(value.real) for value in responses)
    imag_response = tuple(float(value.imag) for value in responses)
    spectral = tuple(2.0 * value for value in imag_response)
    kms_ratios: list[float] = []
    kms_targets: list[float] = []
    kms_residual = 0.0
    fdt_residual = 0.0
    for frequency, spectral_value in zip(frequencies, spectral):
        if frequency <= 0.0:
            continue
        occupation = 1.0 / expm1(frequency / temperature)
        greater = spectral_value * (1.0 + occupation)
        lesser = spectral_value * occupation
        ratio = greater / lesser
        target = np.exp(frequency / temperature)
        kms_ratios.append(float(ratio))
        kms_targets.append(float(target))
        kms_residual = max(kms_residual, abs(ratio - target))
        fdt_residual = max(
            fdt_residual,
            abs(greater + lesser - spectral_value / np.tanh(0.5 * frequency / temperature)),
        )
    entropy = _positive(dc_response / temperature, "entropy production")
    all_values = (
        *last_susceptibility,
        *last_rates,
        relative_susceptibility,
        relative_rate,
        dc_response,
        *responses_by_order,
        *rates_by_order,
        radial_max_change,
        angular_change,
        scale_change,
        *eigenvalues,
        *real_response,
        *imag_response,
        *spectral,
        entropy,
    )
    if not all(isfinite(float(value)) for value in all_values):
        raise FloatingPointError("continuum relative-flow state is not finite")
    convergence_passes = (
        radial_max_change <= CONTINUUM_ACCEPTANCE_THRESHOLD
        and angular_change <= CONTINUUM_ACCEPTANCE_THRESHOLD
        and scale_change <= CONTINUUM_ACCEPTANCE_THRESHOLD
    )
    return ContinuumRelativeFlowState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=state.branch,
        effective_mass=state.effective_mass,
        condensate_amplitude=state.condensate_amplitude,
        tree_radial_screening_sq=float(screening_sq),
        radial_orders=radial_orders,
        angular_order=angular_order,
        angular_refined_order=angular_refined_order,
        radial_scale=float(base_scale * radial_scale_factor),
        mode_susceptibility=tuple(float(value) for value in last_susceptibility),
        mode_rate=tuple(float(value) for value in last_rates),
        relative_susceptibility=relative_susceptibility,
        relative_collision_rate=relative_rate,
        dc_relative_response=dc_response,
        radial_relative_collision_rates=tuple(rates_by_order),
        radial_dc_responses=tuple(responses_by_order),
        radial_max_relative_change=radial_max_change,
        angular_refined_relative_change=angular_change,
        scale_refined_relative_change=scale_change,
        collision_operator=tuple(tuple(float(value) for value in row) for row in operator),
        collision_eigenvalues=tuple(float(value) for value in eigenvalues),
        common_flow_conservation_residual=float(np.linalg.norm(operator @ np.ones(2))),
        source_common_mode_residual=abs(float(np.sum(source))),
        symmetric_kernel_residual=float(np.linalg.norm(operator - operator.T)),
        retarded_frequency_over_rate=ratios,
        retarded_response_real=real_response,
        retarded_response_imag=imag_response,
        spectral_density=spectral,
        kms_ratio=tuple(kms_ratios),
        kms_target_ratio=tuple(kms_targets),
        kms_residual=float(kms_residual),
        fdt_residual=float(fdt_residual),
        entropy_production_at_unit_force=entropy,
        continuum_integrals_finite=True,
        continuum_convergence_passes=convergence_passes,
    )


def continuum_relative_flow_contract() -> dict[str, object]:
    """Return equations, units, and the non-promotion boundary."""

    return {
        "status": CONTINUUM_RELATIVE_FLOW_STATUS,
        "equations": {
            "radial_map": "k=Lambda*u/(1-u), u in (0,1), dk=Lambda/(1-u)^2 du",
            "mode_susceptibility": "D_a=(1/3) integral[d^3k/(2*pi)^3] k^2 v_a^2[-partial_E n_a]",
            "screened_contact_channel": "sigma_ab=lambda^2/[16*pi*(s_med+m_H^2)]",
            "medium_invariant": "s_med=2*E_a*E_b*(1-cos(theta)); m_H^2=2*lambda*A_*^2",
            "relative_kernel": "L_rel=Gamma_rel*((1,-1),(-1,1))",
            "retarded_response": "G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)",
            "continuum_controller": "max(radial, angular, scale relative changes)<=1e-2",
        },
        "unit_contract": {
            "unit_lane": "natural continuum thermal integral",
            "temperature_chemical_potential_mass": "energy",
            "radial_map_scale": "energy",
            "collision_rate": "energy",
            "relative_response": "natural-unit response coefficient",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state",
            "R_obs": "observer record; not physical dynamics",
        },
        "derivation_class": (
            "action-derived tree-condensate screened contact channel with a compactified "
            "continuum thermal integral and explicit convergence controller"
        ),
        "observable": "continuum natural relative-flow response and retarded KMS/FDT interface",
        "data_role": "ACTION_DERIVED_CONTINUUM_THERMAL_CONTACT_RESPONSE_NOT_PHYSICAL_KUBO",
        "closed_scope": [
            "the screened thermal contact-channel integral is evaluated on k in [0,infinity)",
            "radial order, angular order, and compactification-scale refinements are checked",
            "the relative operator remains symmetric positive semidefinite with a common-flow zero mode",
            "the continuum thermal response has an explicit natural-unit retarded KMS/FDT interface",
        ],
        "excluded_scope": [
            "vacuum loop renormalization or running-coupling matching",
            "complete condensed microscopic vertex and all scattering channels",
            "physical SI Kubo coefficient and source uncertainty",
            "dimensional Phi map, alpha_Phi_K, TTG prediction, and Full Topic 13 closure",
        ],
        "claim_boundary": (
            "This closes only the continuum thermal integral of the declared screened "
            "contact channel. It is not a loop-renormalized physical Kubo coefficient, "
            "a complete two-fluid transport tensor, an SI Phi calibration, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "CONTINUUM_ACCEPTANCE_THRESHOLD",
    "CONTINUUM_RELATIVE_FLOW_STATUS",
    "DEFAULT_ANGULAR_ORDER",
    "DEFAULT_ANGULAR_REFINED_ORDER",
    "DEFAULT_RADIAL_ORDERS",
    "ContinuumRelativeFlowState",
    "continuum_relative_flow_contract",
    "continuum_relative_flow_state",
]
