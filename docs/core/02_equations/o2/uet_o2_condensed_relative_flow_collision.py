"""Action-derived condensed relative-flow collision lane for Topic 13.

This module supplies the missing *structural* condensed collision interface
without pretending that a natural-unit response is an externally measured
transport coefficient.  The contact channel uses the existing O(2) tree
condensate amplitude and quasiparticle dispersions.  Its mode-space operator
is explicitly symmetric, positive semidefinite, and has a common-flow zero
mode; only the relative-flow mode is relaxed.

The lane is therefore stronger than the static identifiability witness, but it
is still not a continuum-renormalized microscopic Kubo calculation, an SI
observable, or an external validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
    finite_temperature_o2_state,
)


CONDENSED_RELATIVE_FLOW_STATUS = (
    "PASS_ACTION_DERIVED_CONDENSED_RELATIVE_FLOW_COLLISION_LANE"
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


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _bose(energy: np.ndarray, temperature: float) -> np.ndarray:
    argument = np.maximum(np.asarray(energy, dtype=float) / temperature, 1.0e-12)
    return np.where(argument > 50.0, np.exp(-argument), 1.0 / np.expm1(argument))


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return 0.5 * cutoff * (nodes + 1.0), 0.5 * cutoff * weights


def _mode_energies(
    momenta: np.ndarray,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> np.ndarray:
    values = np.asarray(
        [
            condensed_quasiparticle_energies(
                float(momentum), chemical_potential, space_response, config
            )
            for momentum in momenta
        ],
        dtype=float,
    )
    return values.T


def _mode_velocities(
    momenta: np.ndarray,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> np.ndarray:
    values = np.zeros((2, len(momenta)), dtype=float)
    for index, momentum in enumerate(momenta):
        step = 1.0e-5 * max(1.0, float(momentum))
        lower = max(0.0, float(momentum) - step)
        upper = float(momentum) + step
        lower_energy = condensed_quasiparticle_energies(
            lower, chemical_potential, space_response, config
        )
        upper_energy = condensed_quasiparticle_energies(
            upper, chemical_potential, space_response, config
        )
        denominator = upper - lower
        values[:, index] = (
            np.asarray(upper_energy, dtype=float)
            - np.asarray(lower_energy, dtype=float)
        ) / denominator
    return values


def _contact_rate_by_mode(
    momenta: np.ndarray,
    weights: np.ndarray,
    energies: np.ndarray,
    velocities: np.ndarray,
    occupations: np.ndarray,
    temperature: float,
    condensate_amplitude: float,
    quartic_coupling: float,
    angular_nodes: np.ndarray,
    angular_weights: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Return susceptibility-weighted contact rates and radial screening.

    The rate is the declared action-derived screened contact channel

    ``Gamma_a(k)=sum_b integral_p,x n_b(1+n_a) v_rel lambda^2 /
    [16*pi*(s_med+m_H^2)]``.

    ``m_H^2=2*lambda*A_*^2`` is the tree radial curvature scale.  Adding this
    positive scale keeps the Goldstone forward channel integrable without a
    numerical clip or an externally fitted infrared parameter.  ``s_med`` is
    the positive medium-frame pair invariant ``2*E_a*E_b*(1-cos(theta))``;
    the finite-density quasiparticle dispersions are not silently treated as
    vacuum Lorentz-invariant four-momenta.
    """

    measure = momenta * momenta / (2.0 * pi**2)
    dndenergy = occupations * (1.0 + occupations) / temperature
    mode_weight = np.asarray(
        [
            np.sum(
                weights
                * measure
                * momenta
                * momenta
                * dndenergy[mode]
                * velocities[mode]
                * velocities[mode]
            )
            for mode in range(2)
        ],
        dtype=float,
    )
    if not np.all(np.isfinite(mode_weight)) or np.any(mode_weight <= 0.0):
        raise FloatingPointError("condensed mode weights must be finite and positive")

    screening_sq = 2.0 * quartic_coupling * condensate_amplitude**2
    screening_sq = _positive(screening_sq, "tree radial screening scale")
    rates = np.zeros(2, dtype=float)
    cosines = angular_nodes[None, None, :]
    angular_measure = 0.5 * angular_weights[None, None, :]
    partner_measure = weights * measure

    for mode_a in range(2):
        mode_rate = np.zeros(len(momenta), dtype=float)
        for mode_b in range(2):
            energy_a = energies[mode_a][:, None, None]
            energy_b = energies[mode_b][None, :, None]
            momentum_a = momenta[:, None, None]
            momentum_b = momenta[None, :, None]
            velocity_a = velocities[mode_a][:, None, None]
            velocity_b = velocities[mode_b][None, :, None]
            medium_s = 2.0 * energy_a * energy_b * (1.0 - cosines)
            effective_s = medium_s + screening_sq
            relative_speed = np.sqrt(
                np.maximum(
                    velocity_a * velocity_a
                    + velocity_b * velocity_b
                    - 2.0 * velocity_a * velocity_b * cosines,
                    0.0,
                )
            )
            cross_section = quartic_coupling**2 / (16.0 * pi * effective_s)
            angular_integral = np.sum(
                angular_measure * relative_speed * cross_section, axis=2
            )
            occupation_factor = occupations[mode_b][None, :] * (
                1.0 + occupations[mode_a][:, None]
            )
            mode_rate += np.sum(
                angular_integral
                * partner_measure[None, :]
                * occupation_factor,
                axis=1,
            )
        rates[mode_a] = float(
            np.sum(
                weights
                * measure
                * momenta
                * momenta
                * dndenergy[mode_a]
                * velocities[mode_a]
                * velocities[mode_a]
                * mode_rate
            )
            / mode_weight[mode_a]
        )
    return rates, screening_sq


@dataclass(frozen=True)
class CondensedRelativeFlowCollisionState:
    """Natural-unit condensed relative-flow collision and KMS state."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    effective_mass: float
    condensate_amplitude: float
    sound_speed_sq: float
    radial_order: int
    angular_order: int
    momentum_cutoff: float
    tree_radial_screening_sq: float
    mode_susceptibility: tuple[float, float]
    mode_rate: tuple[float, float]
    relative_susceptibility: float
    relative_collision_rate: float
    collision_operator: tuple[tuple[float, float], tuple[float, float]]
    collision_eigenvalues: tuple[float, float]
    common_flow_conservation_residual: float
    relative_source: tuple[float, float]
    source_common_mode_residual: float
    dc_relative_response: float
    retarded_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    spectral_density: tuple[float, ...]
    kms_ratio: tuple[float, ...]
    kms_target_ratio: tuple[float, ...]
    kms_residual: float
    fdt_residual: float
    entropy_production_at_unit_force: float
    symmetric_kernel_residual: float
    data_role: str = (
        "ACTION_DERIVED_CONDENSED_RELATIVE_FLOW_KERNEL_NATURAL_UNIT_NOT_PHYSICAL_KUBO"
    )
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_phi_k_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False


def condensed_relative_flow_collision_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 48,
    angular_order: int = 24,
    cutoff_factor: float = 24.0,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
) -> CondensedRelativeFlowCollisionState:
    """Build the declared condensed relative-flow kernel.

    The common-flow mode is conserved and the relative mode is relaxed.  The
    returned KMS/FDT values are an algebraic retarded interface built from the
    positive kernel; they are not a claim of a complete microscopic SK action.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    radial_order = _integer(radial_order, "radial_order", 32)
    angular_order = _integer(angular_order, "angular_order", 16)
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    ratios = tuple(
        _finite(value, "retarded frequency ratio")
        for value in retarded_frequency_over_rate
    )
    if not ratios or ratios[0] != 0.0 or tuple(sorted(ratios)) != ratios:
        raise ValueError("frequency ratios must be sorted and start at zero")
    if any(value < 0.0 for value in ratios):
        raise ValueError("frequency ratios must be non-negative")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    state = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    if state.branch != "condensed":
        raise ValueError("condensed relative-flow lane requires the condensed branch")
    sound_speed_sq = float(
        config.eos.matter.matter_kinetic * (
            config.eos.matter.matter_kinetic * chemical_potential**2
            - state.effective_mass**2
        )
        / (
            config.eos.matter.matter_kinetic * chemical_potential**2
            + 3.0
            * config.eos.matter.matter_quartic
            * state.condensate_amplitude**2
        )
    )
    if not isfinite(sound_speed_sq) or sound_speed_sq <= 0.0:
        raise ValueError("condensed sound-speed contract must be positive")

    cutoff = max(
        cutoff_factor * temperature,
        cutoff_factor * state.effective_mass,
        cutoff_factor
        * sqrt(config.eos.matter.matter_quartic)
        * state.condensate_amplitude,
        1.0,
    )
    momenta, weights = _quadrature(radial_order, cutoff)
    energies = _mode_energies(
        momenta, chemical_potential, space_response, config
    )
    velocities = _mode_velocities(
        momenta, chemical_potential, space_response, config
    )
    occupations = _bose(energies, temperature)
    angular_nodes, angular_weights = np.polynomial.legendre.leggauss(angular_order)
    mode_rates, screening_sq = _contact_rate_by_mode(
        momenta,
        weights,
        energies,
        velocities,
        occupations,
        temperature,
        state.condensate_amplitude,
        config.eos.matter.matter_quartic,
        angular_nodes,
        angular_weights,
    )
    measure = momenta * momenta / (2.0 * pi**2)
    dndenergy = occupations * (1.0 + occupations) / temperature
    mode_weight = np.asarray(
        [
            np.sum(
                weights
                * measure
                * momenta
                * momenta
                * dndenergy[mode]
                * velocities[mode]
                * velocities[mode]
            )
            for mode in range(2)
        ],
        dtype=float,
    )
    relative_weight = float(
        mode_weight[0] * mode_weight[1] / np.sum(mode_weight)
    )
    relative_rate = float(
        np.dot(mode_weight, mode_rates) / np.sum(mode_weight)
    )
    relative_rate = _positive(relative_rate, "relative collision rate")
    collision_operator = relative_rate * np.asarray(
        ((1.0, -1.0), (-1.0, 1.0)), dtype=float
    )
    eigenvalues = np.linalg.eigvalsh(collision_operator)
    source = sqrt(relative_weight) * np.asarray((1.0, -1.0), dtype=float)
    common_residual = float(
        np.linalg.norm(collision_operator @ np.ones(2, dtype=float))
    )
    source_common_residual = abs(float(np.sum(source)))
    dc_response = float(relative_weight / relative_rate)
    frequencies = tuple(relative_rate * value for value in ratios)
    responses = tuple(
        2.0
        * relative_weight
        / complex(2.0 * relative_rate, -frequency)
        for frequency in frequencies
    )
    real_response = tuple(float(value.real) for value in responses)
    imag_response = tuple(float(value.imag) for value in responses)
    spectral = tuple(2.0 * value for value in imag_response)

    positive_frequency_indices = [
        index for index, frequency in enumerate(frequencies) if frequency > 0.0
    ]
    kms_ratios: list[float] = []
    kms_targets: list[float] = []
    kms_residual = 0.0
    fdt_residual = 0.0
    for index in positive_frequency_indices:
        frequency = frequencies[index]
        occupation = 1.0 / expm1(frequency / temperature)
        greater = spectral[index] * (1.0 + occupation)
        lesser = spectral[index] * occupation
        ratio = greater / lesser
        target = exp(frequency / temperature)
        kms_ratios.append(float(ratio))
        kms_targets.append(float(target))
        kms_residual = max(kms_residual, abs(ratio - target))
        noise = greater + lesser
        noise_target = spectral[index] / np.tanh(0.5 * frequency / temperature)
        fdt_residual = max(fdt_residual, abs(noise - noise_target))

    entropy_production = _positive(
        dc_response / temperature, "relative entropy production"
    )
    values = (
        *mode_weight,
        *mode_rates,
        relative_weight,
        relative_rate,
        *eigenvalues,
        dc_response,
        *real_response,
        *imag_response,
        *spectral,
        entropy_production,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("condensed relative-flow state is not finite")

    return CondensedRelativeFlowCollisionState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=state.branch,
        effective_mass=state.effective_mass,
        condensate_amplitude=state.condensate_amplitude,
        sound_speed_sq=sound_speed_sq,
        radial_order=radial_order,
        angular_order=angular_order,
        momentum_cutoff=cutoff,
        tree_radial_screening_sq=screening_sq,
        mode_susceptibility=(float(mode_weight[0]), float(mode_weight[1])),
        mode_rate=(float(mode_rates[0]), float(mode_rates[1])),
        relative_susceptibility=relative_weight,
        relative_collision_rate=relative_rate,
        collision_operator=tuple(
            tuple(float(value) for value in row) for row in collision_operator
        ),
        collision_eigenvalues=(float(eigenvalues[0]), float(eigenvalues[1])),
        common_flow_conservation_residual=common_residual,
        relative_source=(float(source[0]), float(source[1])),
        source_common_mode_residual=source_common_residual,
        dc_relative_response=dc_response,
        retarded_frequency_over_rate=ratios,
        retarded_response_real=real_response,
        retarded_response_imag=imag_response,
        spectral_density=spectral,
        kms_ratio=tuple(kms_ratios),
        kms_target_ratio=tuple(kms_targets),
        kms_residual=kms_residual,
        fdt_residual=fdt_residual,
        entropy_production_at_unit_force=entropy_production,
        symmetric_kernel_residual=float(
            np.linalg.norm(collision_operator - collision_operator.T)
        ),
    )


def condensed_relative_flow_collision_contract() -> dict[str, object]:
    """Return the equations, units, and non-promotion boundary."""

    return {
        "status": CONDENSED_RELATIVE_FLOW_STATUS,
        "equations": {
            "condensate_amplitude": "A_*^2=(Z*mu^2-m_eff^2)/lambda for q>0",
            "quasiparticle_modes": "E_+/-^2=S +/- sqrt(4*Z*mu^2*B+4*lambda^2*A_*^4)",
            "screened_contact_channel": "sigma_ab(s_med)=lambda^2/[16*pi*(s_med+m_H^2)]; s_med=2*E_a*E_b*(1-cos(theta)); m_H^2=2*lambda*A_*^2",
            "linearized_mode_rate": "Gamma_a(k)=sum_b integral_p,x n_b*(1+n_a)*v_rel*sigma_ab(s_med)",
            "mode_weight": "D_a=(1/3) integral[d^3k/(2*pi)^3] k^2*v_a^2*[-partial_E n_a]",
            "relative_kernel": "L_rel=Gamma_rel*((1,-1),(-1,1))",
            "retarded_response": "G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)",
            "entropy_production": "sigma_rel=X_rel*G_R^rel(0)*X_rel/T >= 0",
            "kms_fdt_interface": "N(omega)=coth(beta*omega/2)*2*Im G_R^rel(omega)",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass": "energy",
            "cross_section": "inverse energy squared",
            "collision_rate": "energy",
            "relative_response": "natural-unit response coefficient",
            "relative_flow_force": "dimensionless normalized relative-flow force",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state",
            "R_obs": "observer record; not physical dynamics",
        },
        "derivation_class": (
            "action-derived tree-condensate contact channel with tree radial "
            "screening, mode-space detailed-balance symmetrization, and retarded lift"
        ),
        "observable": (
            "condensed relative-flow collision response, common-flow conservation, "
            "entropy production, and KMS/FDT interface"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_NATURAL_RELATIVE_FLOW_LANE",
        "closed_scope": [
            "a declared condensed contact collision channel from the existing O(2) action scales",
            "a symmetric positive-semidefinite relative-flow operator with a common-flow zero mode",
            "finite positive DC response and entropy production on the declared condensed state",
            "algebraic retarded KMS/FDT interface for the relative mode",
        ],
        "excluded_scope": [
            "complete microscopic condensed vertex and all scattering channels",
            "continuum-renormalized physical Kubo coefficient",
            "SI Phi normalization and alpha_Phi_K",
            "TTG prediction, external validation, and Full Topic 13 closure",
        ],
        "claim_boundary": (
            "This closes a named action-derived condensed relative-flow kernel lane. "
            "It does not emit a physical SI Kubo coefficient, complete two-fluid "
            "transport tensor, alpha_Phi_K, TTG prediction, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "CONDENSED_RELATIVE_FLOW_STATUS",
    "CondensedRelativeFlowCollisionState",
    "condensed_relative_flow_collision_state",
    "condensed_relative_flow_collision_contract",
]
