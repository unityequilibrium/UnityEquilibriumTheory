"""Loop-renormalized condensed contact channel for Topic 13.

This lane applies a finite thermal one-loop reference subtraction to the
screened relative-flow contact channel.  It is deliberately narrower than a
full condensed 1PI vertex: the loop is the declared relative-flow contact
channel and the reference subtraction is an internal natural-unit scheme.
The resulting retarded response is state matched and KMS/FDT checked, but it
is not admitted as a physical Kubo coefficient without an independent
physical anchor and source record.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_continuum_relative_flow_kubo import (
    _bose,
    _compactified_radial_quadrature,
    _mode_arrays,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
)


CONDENSED_LOOP_VERTEX_STATUS = (
    "PASS_ACTION_DERIVED_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE"
)
LOOP_VERTEX_ACCEPTANCE_THRESHOLD = 1.0e-2


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


def _relative_change(first: float, second: float) -> float:
    return float(abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300))


def _loop_bubble_matrix(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    radial_order: int,
    radial_scale: float,
    normalization_scale: float,
) -> np.ndarray:
    """Return the finite thermal derivative-channel bubble matrix.

    The factor ``(k/normalization_scale)^2`` makes the declared derivative
    contact channel dimensionless and removes the infrared singularity of the
    tree-level Goldstone mode.  The Bose weight makes the radial integral
    ultraviolet convergent, so ``radial_scale`` is only a compactification
    map scale and never a physical cutoff.
    """

    momentum, weights = _compactified_radial_quadrature(radial_order, radial_scale)
    energies, _ = _mode_arrays(
        momentum, chemical_potential, space_response, config
    )
    occupations = _bose(energies, temperature)
    measure = momentum * momentum / (2.0 * pi**2)
    dimensionless_momentum_sq = (momentum / normalization_scale) ** 2
    bubbles = np.zeros((2, 2), dtype=float)
    for mode_a in range(2):
        for mode_b in range(mode_a, 2):
            energy_a = energies[mode_a]
            energy_b = energies[mode_b]
            denominator = 2.0 * energy_a * energy_b * (energy_a + energy_b)
            numerator = occupations[mode_a] + occupations[mode_b]
            integrand = (
                weights
                * measure
                * dimensionless_momentum_sq
                * numerator
                / denominator
            )
            value = float(np.sum(integrand))
            if not isfinite(value) or value <= 0.0:
                raise FloatingPointError("condensed loop bubble is not finite and positive")
            bubbles[mode_a, mode_b] = value
            bubbles[mode_b, mode_a] = value
    return bubbles


def _loop_renormalized_coupling(
    quartic_coupling: float,
    target_bubble: np.ndarray,
    reference_bubble: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply the declared reference-subtracted one-loop contact scheme."""

    subtracted = np.asarray(target_bubble - reference_bubble, dtype=float)
    denominator = 1.0 + float(quartic_coupling) * subtracted
    if not np.all(np.isfinite(denominator)) or np.any(denominator <= 0.0):
        raise FloatingPointError("loop-renormalized contact denominator is not positive")
    effective = float(quartic_coupling) / denominator
    if not np.all(np.isfinite(effective)) or np.any(effective <= 0.0):
        raise FloatingPointError("loop-renormalized contact coupling is not positive")
    return subtracted, effective


def _contact_response(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    condensate_amplitude: float,
    quartic_coupling: float,
    effective_coupling: np.ndarray,
    radial_order: int,
    angular_order: int,
    radial_scale: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Evaluate the relative-flow contact response with channel couplings."""

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
        raise FloatingPointError("loop-renormalized mode susceptibilities must be positive")

    angular_nodes, angular_weights = np.polynomial.legendre.leggauss(angular_order)
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
        for mode_b in range(2):
            energy_b = energies[mode_b][None, :, None]
            velocity_b = velocities[mode_b][None, :, None]
            cosine = angular_nodes[None, None, :]
            relative_speed = np.sqrt(
                velocity_a**2 + velocity_b**2 - 2.0 * velocity_a * velocity_b * cosine
            )
            s_medium = 2.0 * energy_a * energy_b * (1.0 - cosine)
            cross_section = effective_coupling[mode_a, mode_b] ** 2 / (
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
        raise FloatingPointError("loop-renormalized mode rates must be positive")
    return mode_susceptibility, mode_rates, screening_sq


@dataclass(frozen=True)
class CondensedLoopRenormalizedVertexState:
    """State record for the loop-renormalized contact-channel lane."""

    temperature: float
    chemical_potential: float
    space_response: float
    reference_space_response: float
    branch: str
    reference_branch: str
    effective_mass: float
    reference_effective_mass: float
    condensate_amplitude: float
    reference_condensate_amplitude: float
    quartic_coupling: float
    radial_orders: tuple[int, ...]
    angular_order: int
    angular_refined_order: int
    radial_scale: float
    normalization_scale: float
    target_bubble_matrix: tuple[tuple[float, float], tuple[float, float]]
    reference_bubble_matrix: tuple[tuple[float, float], tuple[float, float]]
    subtracted_bubble_matrix: tuple[tuple[float, float], tuple[float, float]]
    effective_coupling_matrix: tuple[tuple[float, float], tuple[float, float]]
    reference_subtraction_residual: float
    loop_bubble_last_relative_change: float
    loop_coupling_relative_change: float
    mode_susceptibility: tuple[float, float]
    mode_rate: tuple[float, float]
    relative_susceptibility: float
    relative_collision_rate: float
    dc_relative_response: float
    radial_dc_responses: tuple[float, ...]
    radial_max_relative_change: float
    angular_refined_relative_change: float
    scale_refined_relative_change: float
    collision_eigenvalues: tuple[float, float]
    common_flow_conservation_residual: float
    symmetric_kernel_residual: float
    retarded_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    spectral_density: tuple[float, ...]
    kms_residual: float
    fdt_residual: float
    entropy_production_at_unit_force: float
    numerical_uncertainty_bound: float
    loop_integrals_finite: bool
    loop_renormalization_convergence_passes: bool
    state_matched_retarded_response_completed: bool = True
    physical_kubo_coefficient_emitted: bool = False
    physical_anchor_supplied: bool = False
    numeric_alpha_phi_k_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_CONDENSED_THERMAL_LOOP_CONTACT_RESPONSE_NOT_PHYSICAL_KUBO"
    )


def condensed_loop_renormalized_vertex_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    reference_space_response: float = 0.0,
    radial_orders: tuple[int, ...] = (24, 32, 40),
    angular_order: int = 24,
    angular_refined_order: int = 36,
    radial_scale_factor: float = 1.0,
    refined_scale_factor: float = 0.5,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
) -> CondensedLoopRenormalizedVertexState:
    """Evaluate the declared condensed loop-renormalized contact channel."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    reference_space_response = _finite(reference_space_response, "reference_space_response")
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
    if (
        not ratios
        or ratios[0] != 0.0
        or tuple(sorted(ratios)) != ratios
        or any(value < 0.0 for value in ratios)
    ):
        raise ValueError("retarded frequency ratios must be sorted, non-negative, and start at zero")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    target = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    reference = finite_temperature_o2_state(
        temperature, chemical_potential, reference_space_response, config
    )
    if target.branch != "condensed" or reference.branch != "condensed":
        raise ValueError("loop-renormalized vertex requires condensed target and reference branches")
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    normalization_scale = _positive(
        max(
            temperature,
            target.effective_mass,
            reference.effective_mass,
            sqrt(quartic) * target.condensate_amplitude,
            sqrt(quartic) * reference.condensate_amplitude,
            1.0e-6,
        ),
        "normalization_scale",
    )
    radial_scale = normalization_scale * radial_scale_factor

    target_bubbles: list[np.ndarray] = []
    reference_bubbles: list[np.ndarray] = []
    subtracted_bubbles: list[np.ndarray] = []
    effective_couplings: list[np.ndarray] = []
    responses: list[float] = []
    rates: list[float] = []
    for order in radial_orders:
        target_bubble = _loop_bubble_matrix(
            temperature,
            chemical_potential,
            space_response,
            config,
            radial_order=order,
            radial_scale=radial_scale,
            normalization_scale=normalization_scale,
        )
        reference_bubble = _loop_bubble_matrix(
            temperature,
            chemical_potential,
            reference_space_response,
            config,
            radial_order=order,
            radial_scale=radial_scale,
            normalization_scale=normalization_scale,
        )
        subtracted, effective = _loop_renormalized_coupling(
            quartic, target_bubble, reference_bubble
        )
        susceptibility, mode_rate, _ = _contact_response(
            temperature,
            chemical_potential,
            space_response,
            config,
            condensate_amplitude=target.condensate_amplitude,
            quartic_coupling=quartic,
            effective_coupling=effective,
            radial_order=order,
            angular_order=angular_order,
            radial_scale=radial_scale,
        )
        relative_susceptibility = float(
            susceptibility[0] * susceptibility[1] / np.sum(susceptibility)
        )
        relative_rate = float(np.dot(susceptibility, mode_rate) / np.sum(susceptibility))
        target_bubbles.append(target_bubble)
        reference_bubbles.append(reference_bubble)
        subtracted_bubbles.append(subtracted)
        effective_couplings.append(effective)
        responses.append(relative_susceptibility / relative_rate)
        rates.append(relative_rate)

    target_bubble = target_bubbles[-1]
    reference_bubble = reference_bubbles[-1]
    subtracted_bubble = subtracted_bubbles[-1]
    effective_coupling = effective_couplings[-1]
    susceptibility, mode_rate, _ = _contact_response(
        temperature,
        chemical_potential,
        space_response,
        config,
        condensate_amplitude=target.condensate_amplitude,
        quartic_coupling=quartic,
        effective_coupling=effective_coupling,
        radial_order=radial_orders[-1],
        angular_order=angular_order,
        radial_scale=radial_scale,
    )
    relative_susceptibility = float(
        susceptibility[0] * susceptibility[1] / np.sum(susceptibility)
    )
    relative_rate = float(np.dot(susceptibility, mode_rate) / np.sum(susceptibility))
    dc_response = relative_susceptibility / relative_rate

    refined_susceptibility, refined_rate, _ = _contact_response(
        temperature,
        chemical_potential,
        space_response,
        config,
        condensate_amplitude=target.condensate_amplitude,
        quartic_coupling=quartic,
        effective_coupling=effective_coupling,
        radial_order=radial_orders[-1],
        angular_order=angular_refined_order,
        radial_scale=radial_scale,
    )
    refined_angular_response = float(
        refined_susceptibility[0]
        * refined_susceptibility[1]
        / np.sum(refined_susceptibility)
        / (np.dot(refined_susceptibility, refined_rate) / np.sum(refined_susceptibility))
    )
    angular_change = _relative_change(refined_angular_response, dc_response)

    refined_scale = radial_scale * refined_scale_factor
    refined_target_bubble = _loop_bubble_matrix(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=radial_orders[-1],
        radial_scale=refined_scale,
        normalization_scale=normalization_scale,
    )
    refined_reference_bubble = _loop_bubble_matrix(
        temperature,
        chemical_potential,
        reference_space_response,
        config,
        radial_order=radial_orders[-1],
        radial_scale=refined_scale,
        normalization_scale=normalization_scale,
    )
    _, refined_effective_coupling = _loop_renormalized_coupling(
        quartic, refined_target_bubble, refined_reference_bubble
    )
    scale_susceptibility, scale_rate, _ = _contact_response(
        temperature,
        chemical_potential,
        space_response,
        config,
        condensate_amplitude=target.condensate_amplitude,
        quartic_coupling=quartic,
        effective_coupling=refined_effective_coupling,
        radial_order=radial_orders[-1],
        angular_order=angular_order,
        radial_scale=refined_scale,
    )
    scale_response = float(
        scale_susceptibility[0]
        * scale_susceptibility[1]
        / np.sum(scale_susceptibility)
        / (np.dot(scale_susceptibility, scale_rate) / np.sum(scale_susceptibility))
    )
    scale_change = _relative_change(scale_response, dc_response)
    radial_changes = tuple(
        _relative_change(previous, current)
        for previous, current in zip(responses, responses[1:])
    )
    radial_max_change = max(radial_changes, default=0.0)
    bubble_change = _relative_change(
        float(np.linalg.norm(target_bubbles[-1])),
        float(np.linalg.norm(target_bubbles[-2])),
    )
    coupling_change = _relative_change(
        float(np.linalg.norm(effective_couplings[-1])),
        float(np.linalg.norm(effective_couplings[-2])),
    )

    operator = relative_rate * np.asarray(((1.0, -1.0), (-1.0, 1.0)), dtype=float)
    eigenvalues = np.linalg.eigvalsh(operator)
    frequencies = tuple(relative_rate * ratio for ratio in ratios)
    retarded = tuple(
        2.0 * relative_susceptibility / complex(2.0 * relative_rate, -frequency)
        for frequency in frequencies
    )
    real_response = tuple(float(value.real) for value in retarded)
    imag_response = tuple(float(value.imag) for value in retarded)
    spectral = tuple(2.0 * value for value in imag_response)
    kms_residual = 0.0
    fdt_residual = 0.0
    for frequency, spectral_value in zip(frequencies, spectral):
        if frequency <= 0.0:
            continue
        occupation = 1.0 / expm1(frequency / temperature)
        greater = spectral_value * (1.0 + occupation)
        lesser = spectral_value * occupation
        kms_residual = max(kms_residual, abs(greater / lesser - exp(frequency / temperature)))
        fdt_residual = max(
            fdt_residual,
            abs(greater + lesser - spectral_value / np.tanh(0.5 * frequency / temperature)),
        )
    entropy = _positive(dc_response / temperature, "entropy production")
    numerical_uncertainty = max(radial_max_change, angular_change, scale_change)
    values = (
        *target_bubble.ravel(),
        *reference_bubble.ravel(),
        *subtracted_bubble.ravel(),
        *effective_coupling.ravel(),
        relative_susceptibility,
        relative_rate,
        dc_response,
        *responses,
        bubble_change,
        coupling_change,
        radial_max_change,
        angular_change,
        scale_change,
        *eigenvalues,
        *real_response,
        *imag_response,
        *spectral,
        entropy,
        numerical_uncertainty,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("condensed loop-renormalized state is not finite")
    convergence_passes = (
        numerical_uncertainty <= LOOP_VERTEX_ACCEPTANCE_THRESHOLD
        and bubble_change <= LOOP_VERTEX_ACCEPTANCE_THRESHOLD
        and coupling_change <= LOOP_VERTEX_ACCEPTANCE_THRESHOLD
    )
    return CondensedLoopRenormalizedVertexState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        reference_space_response=reference_space_response,
        branch=target.branch,
        reference_branch=reference.branch,
        effective_mass=target.effective_mass,
        reference_effective_mass=reference.effective_mass,
        condensate_amplitude=target.condensate_amplitude,
        reference_condensate_amplitude=reference.condensate_amplitude,
        quartic_coupling=quartic,
        radial_orders=radial_orders,
        angular_order=angular_order,
        angular_refined_order=angular_refined_order,
        radial_scale=radial_scale,
        normalization_scale=normalization_scale,
        target_bubble_matrix=tuple(tuple(float(value) for value in row) for row in target_bubble),
        reference_bubble_matrix=tuple(tuple(float(value) for value in row) for row in reference_bubble),
        subtracted_bubble_matrix=tuple(tuple(float(value) for value in row) for row in subtracted_bubble),
        effective_coupling_matrix=tuple(tuple(float(value) for value in row) for row in effective_coupling),
        reference_subtraction_residual=float(np.linalg.norm(reference_bubble - reference_bubble)),
        loop_bubble_last_relative_change=float(bubble_change),
        loop_coupling_relative_change=float(coupling_change),
        mode_susceptibility=tuple(float(value) for value in susceptibility),
        mode_rate=tuple(float(value) for value in mode_rate),
        relative_susceptibility=relative_susceptibility,
        relative_collision_rate=relative_rate,
        dc_relative_response=dc_response,
        radial_dc_responses=tuple(float(value) for value in responses),
        radial_max_relative_change=float(radial_max_change),
        angular_refined_relative_change=float(angular_change),
        scale_refined_relative_change=float(scale_change),
        collision_eigenvalues=tuple(float(value) for value in eigenvalues),
        common_flow_conservation_residual=float(np.linalg.norm(operator @ np.ones(2))),
        symmetric_kernel_residual=float(np.linalg.norm(operator - operator.T)),
        retarded_frequency_over_rate=ratios,
        retarded_response_real=real_response,
        retarded_response_imag=imag_response,
        spectral_density=spectral,
        kms_residual=float(kms_residual),
        fdt_residual=float(fdt_residual),
        entropy_production_at_unit_force=entropy,
        numerical_uncertainty_bound=float(numerical_uncertainty),
        loop_integrals_finite=True,
        loop_renormalization_convergence_passes=convergence_passes,
    )


def condensed_loop_renormalized_vertex_contract() -> dict[str, Any]:
    """Return equations, units, and the physical-Kubo admission boundary."""

    return {
        "status": CONDENSED_LOOP_VERTEX_STATUS,
        "equations": {
            "thermal_loop_bubble": "B_ab^th=(integral d^3k/(2*pi)^3)*(k/L)^2*(n_a+n_b)/(2 E_a E_b (E_a+E_b))",
            "reference_subtraction": "B_ab^R(T,mu,Phi)=B_ab^th(T,mu,Phi)-B_ab^th(T,mu,Phi_ref)",
            "loop_coupling": "lambda_ab^R=lambda/(1+lambda B_ab^R)",
            "screened_contact_channel": "sigma_ab^R=(lambda_ab^R)^2/[16*pi*(s_med+2 lambda A_*^2)]",
            "relative_kernel": "L_rel=Gamma_rel*((1,-1),(-1,1))",
            "retarded_response": "G_R^rel(omega)=2 D_rel/(2 Gamma_rel-i omega)",
            "kubo_zero_frequency": "K_rel^natural=lim_(omega->0) Re G_R^rel(omega)=D_rel/Gamma_rel",
        },
        "unit_contract": {
            "unit_lane": "natural continuum 3+1",
            "temperature_chemical_potential_mass_normalization_scale": "energy",
            "thermal_loop_bubble": "dimensionless derivative-channel bubble after (k/L)^2 normalization",
            "quartic_coupling_and_loop_coupling": "dimensionless",
            "collision_rate": "energy",
            "relative_response_and_Kubo_zero_frequency": "natural-unit response coefficient; not SI conductivity",
            "numerical_uncertainty_bound": "dimensionless relative quadrature bound only",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state or feedback input",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "derivation_class": (
            "action-derived thermal one-loop reference subtraction in the declared "
            "condensed relative-flow contact channel, followed by a state-matched "
            "natural-unit retarded response"
        ),
        "observable": (
            "loop-renormalized condensed contact-channel coupling and state-matched "
            "retarded relative-flow response"
        ),
        "data_role": "ACTION_DERIVED_CONDENSED_THERMAL_LOOP_CONTACT_RESPONSE_NOT_PHYSICAL_KUBO",
        "state_match_contract": {
            "requires": [
                "temperature",
                "chemical_potential",
                "space_response",
                "condensed_branch",
                "correlator_formula_id",
                "normalization_scale",
            ],
            "reference_state": "same T and mu with declared Phi_ref; no target-curve residual is used",
        },
        "physical_kubo_admission": {
            "status": "OPEN_PHYSICAL_KUBO",
            "required_external_or_microscopic_fields": [
                "coefficient_name",
                "value",
                "units",
                "hydrodynamic_frame",
                "temperature",
                "chemical_potential",
                "space_response",
                "correlator_formula_id",
                "source_path_or_url",
                "source_hash",
                "evidence_status",
            ],
            "accepted_evidence_statuses": [
                "KUBO_MATCHED",
                "SOURCE_LOCKED",
                "EXTERNALLY_MATCHED",
            ],
            "current_reason_open": (
                "the present coefficient is natural-unit action-derived evidence with "
                "numerical uncertainty only; no independent physical anchor or source "
                "record has been supplied"
            ),
        },
        "closed_scope": [
            "finite thermal loop bubble for the declared condensed contact channel",
            "explicit reference-subtracted loop coupling with positive denominator",
            "radial and compactification-scale convergence controller",
            "state-matched natural-unit retarded response with KMS/FDT checks",
            "symmetric positive semidefinite relative kernel and common-flow conservation",
        ],
        "excluded_scope": [
            "full condensed 1PI vertex and all scattering channels",
            "physical Kubo coefficient admission",
            "SI heat-flux or Phi normalization",
            "alpha_Phi_K calibration",
            "Ding C_src or TTG validation",
            "Full Topic 13 closure",
        ],
        "claim_boundary": (
            "This closes only the declared loop-renormalized condensed contact-channel "
            "lane and its state-matched natural-unit retarded interface. It does not "
            "emit a physical Kubo coefficient, complete the condensed two-fluid tensor, "
            "provide SI or alpha_Phi_K calibration, validate TTG, or close Full Topic 13."
        ),
    }


__all__ = [
    "CONDENSED_LOOP_VERTEX_STATUS",
    "LOOP_VERTEX_ACCEPTANCE_THRESHOLD",
    "CondensedLoopRenormalizedVertexState",
    "condensed_loop_renormalized_vertex_contract",
    "condensed_loop_renormalized_vertex_state",
]
