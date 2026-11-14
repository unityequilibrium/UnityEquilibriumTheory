"""Finite-temperature two-to-two scattering cut of the O(2) sunset.

This module is a named, labeled scattering-cut lane.  It is separate from
the existing exact elastic transition-kernel lane and does not claim the
complete finite-temperature 1PI self-energy or a microscopic transport
coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import expm1, isfinite, log, pi, sqrt, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_action_1pi_sunset_tensor import (
    SUNSET_SYMMETRY_FACTOR,
    expected_sunset_tensor_prefactor,
)


FINITE_T_SCATTERING_SK_KMS_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_SCATTERING_SUNSET_SK_KMS_LANE"
)
FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD = 2.0e-2
# The representative integral carries the graph-summed weight from the
# three positive-energy 2<->2 sign permutations: 3*(1/6)=1/2.
SCATTERING_SIGN_PERMUTATION_COUNT = 3
SCATTERING_GRAPH_CUT_WEIGHT = (
    SCATTERING_SIGN_PERMUTATION_COUNT * SUNSET_SYMMETRY_FACTOR
)
# Retain the old public name for backward-compatible artifact readers.
SCATTERING_CHANNEL_SYMMETRY_FACTOR = SCATTERING_GRAPH_CUT_WEIGHT


@dataclass(frozen=True)
class FiniteTemperatureScatteringSunsetSKKMSState:
    """Labeled finite-temperature sunset scattering-channel state."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    invariant_s: float
    external_energy: float
    thermal_greater_measure: float
    thermal_lesser_measure: float
    thermal_spectral_measure: float
    thermal_retarded_spectral_density: float
    retarded_imaginary_part: float
    thermal_noise_measure: float
    finite_temperature_principal_value_real_part: float
    scattering_pv_inner_convergence_residual: float
    scattering_pv_outer_convergence_residual: float
    scattering_inner_convergence_residual: float
    scattering_outer_convergence_residual: float
    kms_log_ratio_residual: float
    fdt_residual: float
    thermal_enhancement_ratio: float
    greater_is_positive: bool
    lesser_is_positive: bool
    spectral_difference_is_positive: bool
    retarded_imaginary_sign_witness: bool
    finite_temperature_scattering_cut_completed: bool = True
    scattering_channel_sk_kms_match_completed: bool = True
    thermal_retarded_i0_channel_completed: bool = True
    finite_temperature_principal_value_completed: bool = True
    full_finite_temperature_1pi_self_energy_completed: bool = False
    all_finite_temperature_sunset_channels_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_2_TO_2_SUNSET_SK_KMS_CHANNEL_NO_HOLDOUT"
    )


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def _bose(energy: float, temperature: float) -> float:
    argument = _positive(energy / temperature, "beta energy")
    return 1.0 / expm1(argument) if argument < 50.0 else float(np.exp(-argument))


def _thermal_scattering_phase_space(
    invariant_s: float,
    mass_squared: float,
    temperature: float,
    *,
    outer_order: int,
    inner_order: int,
    transform_scale: float,
) -> tuple[float, float]:
    """Return labeled greater and lesser scattering phase-space measures.

    The cut is ``P + k3 = k1 + k2`` in the external rest frame.  The pair
    ``Q=P+k3`` is integrated in its own center-of-mass frame, while the bath
    momentum ``k3`` is integrated on ``[0,infinity)``.  The explicit factor
    ``SCATTERING_CHANNEL_SYMMETRY_FACTOR`` is the graph-summed weight in the measure;
    it equals three signed-cut permutations times the sunset graph symmetry factor and is not a fitted transport coefficient.
    """

    invariant_s = _positive(invariant_s, "invariant_s")
    mass_squared = _positive(mass_squared, "mass_squared")
    temperature = _positive(temperature, "temperature")
    outer_order = _integer(outer_order, "outer_order", 16)
    inner_order = _integer(inner_order, "inner_order", 16)
    transform_scale = _positive(transform_scale, "transform_scale")

    external_energy = sqrt(invariant_s)
    nodes, weights = np.polynomial.legendre.leggauss(outer_order)
    angle_nodes, angle_weights = np.polynomial.legendre.leggauss(inner_order)
    unit_x = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    bath_momentum = transform_scale * unit_x / (1.0 - unit_x)
    jacobian = transform_scale / (1.0 - unit_x) ** 2
    greater_total = 0.0
    lesser_total = 0.0
    mass = sqrt(mass_squared)

    for momentum, outer_weight, radial_jacobian in zip(
        bath_momentum,
        scaled_weights,
        jacobian,
    ):
        momentum = float(momentum)
        bath_energy = sqrt(momentum * momentum + mass_squared)
        pair_invariant = (
            invariant_s + mass_squared + 2.0 * external_energy * bath_energy
        )
        if pair_invariant <= 4.0 * mass_squared:
            continue

        pair_root = sqrt(pair_invariant)
        pair_beta = sqrt(max(1.0 - 4.0 * mass_squared / pair_invariant, 0.0))
        pair_gamma = (external_energy + bath_energy) / pair_root
        pair_boost = momentum / (external_energy + bath_energy)
        daughter_energy_star = 0.5 * pair_root
        daughter_momentum_star = sqrt(
            max(0.25 * pair_invariant - mass_squared, 0.0)
        )
        bath_occupation = _bose(bath_energy, temperature)
        greater_average = 0.0
        lesser_average = 0.0
        for cosine, angle_weight in zip(angle_nodes, angle_weights):
            cosine = float(cosine)
            energy_one = pair_gamma * (
                daughter_energy_star
                + pair_boost * daughter_momentum_star * cosine
            )
            energy_two = pair_gamma * (
                daughter_energy_star
                - pair_boost * daughter_momentum_star * cosine
            )
            occupation_one = _bose(energy_one, temperature)
            occupation_two = _bose(energy_two, temperature)
            greater_average += 0.5 * float(angle_weight) * (
                1.0 + occupation_one
            ) * (1.0 + occupation_two) * bath_occupation
            lesser_average += 0.5 * float(angle_weight) * occupation_one * occupation_two * (
                1.0 + bath_occupation
            )

        radial_measure = (
            SCATTERING_CHANNEL_SYMMETRY_FACTOR
            * momentum
            * momentum
            * pair_beta
            / (32.0 * pi**3 * bath_energy)
        )
        weighted_measure = float(outer_weight) * float(radial_jacobian) * radial_measure
        greater_total += weighted_measure * greater_average
        lesser_total += weighted_measure * lesser_average

    if not isfinite(greater_total) or not isfinite(lesser_total):
        raise FloatingPointError("thermal scattering phase space is not finite")
    if greater_total < 0.0 or lesser_total < 0.0:
        raise FloatingPointError("thermal scattering phase space is negative")
    return float(greater_total), float(lesser_total)


def _thermal_scattering_spectral_measure(
    invariant_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    *,
    outer_order: int,
    inner_order: int,
    transform_scale: float,
) -> float:
    greater, lesser = _thermal_scattering_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=outer_order,
        inner_order=inner_order,
        transform_scale=transform_scale,
    )
    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    result = prefactor * (greater - lesser) / (2.0 * pi)
    if not isfinite(result) or result < 0.0:
        raise FloatingPointError("thermal scattering spectral measure is invalid")
    return float(result)


def _finite_temperature_scattering_principal_value(
    timelike_s: float,
    reference_euclidean_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    *,
    dispersion_order: int,
    phase_outer_order: int,
    phase_inner_order: int,
    transform_scale: float,
) -> float:
    """Evaluate the scattering spectral real part with pole subtraction."""

    timelike_s = _positive(timelike_s, "timelike_s")
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    dispersion_order = _integer(dispersion_order, "dispersion_order", 16)
    phase_outer_order = _integer(phase_outer_order, "phase_outer_order", 16)
    phase_inner_order = _integer(phase_inner_order, "phase_inner_order", 16)
    transform_scale = _positive(transform_scale, "transform_scale")

    reference_minkowski_s = -reference_euclidean_s
    nodes, weights = np.polynomial.legendre.leggauss(dispersion_order)
    unit_x = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    spectral_s = transform_scale * unit_x / (1.0 - unit_x)
    jacobian = transform_scale / (1.0 - unit_x) ** 2
    measures = np.array(
        [
            _thermal_scattering_spectral_measure(
                float(value),
                temperature,
                mass_squared,
                quartic,
                species_count,
                outer_order=phase_outer_order,
                inner_order=phase_inner_order,
                transform_scale=transform_scale,
            )
            for value in spectral_s
        ]
    )
    probe_measure = _thermal_scattering_spectral_measure(
        timelike_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        outer_order=phase_outer_order,
        inner_order=phase_inner_order,
        transform_scale=transform_scale,
    )
    kernel = (
        1.0 / (spectral_s - timelike_s)
        - 1.0 / (spectral_s - reference_minkowski_s)
        - (timelike_s - reference_minkowski_s)
        / (spectral_s - reference_minkowski_s) ** 2
    )
    regularized_integral = float(
        np.sum(scaled_weights * jacobian * (measures - probe_measure) * kernel)
    )
    analytic_pole_integral = log(
        (-reference_minkowski_s) / abs(-timelike_s)
    ) - (timelike_s - reference_minkowski_s) / (-reference_minkowski_s)
    result = regularized_integral + probe_measure * analytic_pole_integral
    if not isfinite(result):
        raise FloatingPointError(
            "thermal scattering principal-value real part is not finite"
        )
    return float(result)


def finite_temperature_scattering_sunset_sk_kms_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    invariant_s: float = 5.0,
    outer_order: int = 32,
    refined_outer_order: int | None = None,
    inner_order: int = 24,
    refined_inner_order: int | None = None,
    reference_euclidean_s: float = 0.5,
    dispersion_order: int = 32,
    refined_dispersion_order: int | None = None,
    dispersion_phase_outer_order: int = 24,
    dispersion_phase_inner_order: int = 20,
    transform_scale: float = 1.0,
) -> FiniteTemperatureScatteringSunsetSKKMSState:
    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    invariant_s = _positive(invariant_s, "invariant_s")
    outer_order = _integer(outer_order, "outer_order", 16)
    if refined_outer_order is None:
        refined_outer_order = outer_order + 16
    refined_outer_order = _integer(
        refined_outer_order,
        "refined_outer_order",
        outer_order + 1,
    )
    inner_order = _integer(inner_order, "inner_order", 16)
    if refined_inner_order is None:
        refined_inner_order = inner_order + 8
    refined_inner_order = _integer(
        refined_inner_order,
        "refined_inner_order",
        inner_order + 1,
    )
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    dispersion_order = _integer(dispersion_order, "dispersion_order", 16)
    if refined_dispersion_order is None:
        refined_dispersion_order = dispersion_order + 16
    refined_dispersion_order = _integer(
        refined_dispersion_order,
        "refined_dispersion_order",
        dispersion_order + 1,
    )
    dispersion_phase_outer_order = _integer(
        dispersion_phase_outer_order,
        "dispersion_phase_outer_order",
        16,
    )
    dispersion_phase_inner_order = _integer(
        dispersion_phase_inner_order,
        "dispersion_phase_inner_order",
        16,
    )
    transform_scale = _positive(transform_scale, "transform_scale")

    greater_phase, lesser_phase = _thermal_scattering_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=outer_order,
        inner_order=inner_order,
        transform_scale=transform_scale,
    )
    refined_greater, refined_lesser = _thermal_scattering_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=refined_outer_order,
        inner_order=refined_inner_order,
        transform_scale=transform_scale,
    )
    inner_refined = _thermal_scattering_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=refined_outer_order,
        inner_order=inner_order,
        transform_scale=transform_scale,
    )
    outer_refined = _thermal_scattering_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=outer_order,
        inner_order=refined_inner_order,
        transform_scale=transform_scale,
    )

    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    measure_scale = prefactor / (2.0 * pi)
    greater_measure = measure_scale * greater_phase
    lesser_measure = measure_scale * lesser_phase
    spectral_measure = greater_measure - lesser_measure
    if greater_measure <= 0.0 or lesser_measure <= 0.0 or spectral_measure <= 0.0:
        raise FloatingPointError("canonical scattering measures must be positive")

    external_energy = sqrt(invariant_s)
    retarded_spectral_density = pi * spectral_measure
    imaginary_part = -retarded_spectral_density
    noise_measure = greater_measure + lesser_measure
    kms_log_ratio = log(greater_measure) - log(lesser_measure)
    kms_target = external_energy / temperature
    fdt_target = spectral_measure / tanh(0.5 * kms_target)
    pv_real = _finite_temperature_scattering_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=dispersion_order,
        phase_outer_order=dispersion_phase_outer_order,
        phase_inner_order=dispersion_phase_inner_order,
        transform_scale=transform_scale,
    )
    pv_refined = _finite_temperature_scattering_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=refined_dispersion_order,
        phase_outer_order=dispersion_phase_outer_order + 8,
        phase_inner_order=dispersion_phase_inner_order + 8,
        transform_scale=transform_scale,
    )
    pv_inner_refined = _finite_temperature_scattering_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=dispersion_order,
        phase_outer_order=dispersion_phase_outer_order + 8,
        phase_inner_order=dispersion_phase_inner_order + 8,
        transform_scale=transform_scale,
    )
    pv_outer_refined = _finite_temperature_scattering_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=refined_dispersion_order,
        phase_outer_order=dispersion_phase_outer_order,
        phase_inner_order=dispersion_phase_inner_order,
        transform_scale=transform_scale,
    )

    scattering_inner_convergence = max(
        _relative(inner_refined[0], refined_greater),
        _relative(inner_refined[1], refined_lesser),
    )
    scattering_outer_convergence = max(
        _relative(outer_refined[0], refined_greater),
        _relative(outer_refined[1], refined_lesser),
    )
    return FiniteTemperatureScatteringSunsetSKKMSState(
        temperature=temperature,
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        external_energy=external_energy,
        thermal_greater_measure=float(greater_measure),
        thermal_lesser_measure=float(lesser_measure),
        thermal_spectral_measure=float(spectral_measure),
        thermal_retarded_spectral_density=float(retarded_spectral_density),
        retarded_imaginary_part=float(imaginary_part),
        thermal_noise_measure=float(noise_measure),
        finite_temperature_principal_value_real_part=float(pv_real),
        scattering_pv_inner_convergence_residual=float(
            _relative(pv_inner_refined, pv_refined)
        ),
        scattering_pv_outer_convergence_residual=float(
            _relative(pv_outer_refined, pv_refined)
        ),
        scattering_inner_convergence_residual=float(scattering_inner_convergence),
        scattering_outer_convergence_residual=float(scattering_outer_convergence),
        kms_log_ratio_residual=float(abs(kms_log_ratio - kms_target)),
        fdt_residual=float(_relative(noise_measure, fdt_target)),
        thermal_enhancement_ratio=float(greater_measure / spectral_measure),
        greater_is_positive=bool(greater_measure > 0.0),
        lesser_is_positive=bool(lesser_measure > 0.0),
        spectral_difference_is_positive=bool(spectral_measure > 0.0),
        retarded_imaginary_sign_witness=bool(imaginary_part < 0.0),
    )


def finite_temperature_scattering_sunset_sk_kms_contract() -> dict[str, Any]:
    """Return the scattering-channel equations, units, and claim boundary."""

    return {
        "status": FINITE_T_SCATTERING_SK_KMS_STATUS,
        "equations": {
            "scattering_cut_kinematics": "P+k3=k1+k2; P=(sqrt(s),0); Q=P+k3",
            "pair_invariant": "Q^2=s+m^2+2*sqrt(s)*E3",
            "greater_scattering_cut": (
                "rho_>(s;T)=prefactor/(2*pi)*integral dPhi_22 "
                "n_B(E3)*prod_{i=1,2}(1+n_B(Ei))"
            ),
            "lesser_scattering_cut": (
                "rho_<(s;T)=prefactor/(2*pi)*integral dPhi_22 "
                "(1+n_B(E3))*prod_{i=1,2}n_B(Ei)"
            ),
            "thermal_scattering_spectral_difference": "rho_T,22(s)=rho_>(s;T)-rho_<(s;T)",
            "thermal_kms": "log(rho_>/rho_<)=beta_th*sqrt(s)",
            "thermal_fdt": "N_T(s)=rho_T,22(s)*coth(beta_th*sqrt(s)/2)",
            "retarded_i0_scattering": "Im Sigma_R,T,22(s)=-pi*rho_T,22(s)",
            "pole_subtracted_principal_value": (
                "Re Sigma_R,T,22^sub(s)=PV integral_[0,infty] "
                "[rho_T,22(S)-rho_T,22(s)]K_sub(S)dS + rho_T,22(s)A(s)"
            ),
            "pole_subtraction_kernel": (
                "K_sub(S)=1/(S-s)-1/(S-r)-(s-r)/(S-r)^2; r=-s_E"
            ),
            "scattering_channel_graph_weight": "S_22^graph=3*(1/6)=1/2 for the representative ++- integral",
            "physical_final_state_weight": "w_final(c,d)=1/(1+delta_cd) belongs to the separate action scattering comparator",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_spectral_measure": "energy squared",
            "retarded_self_energy": "energy squared; labeled scattering channel only",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived equal-mass O(2) sunset tensor prefactor, invariant "
            "two-body phase space for Q=P+k3, explicit Bose weights, and analytic PV subtraction"
        ),
        "observable": (
            "labeled thermal scattering greater/lesser measures, KMS/FDT residuals, "
            "retarded spectral sign, pole-subtracted real part, and quadrature convergence"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_2_TO_2_SUNSET_SK_KMS_CHANNEL_NO_HOLDOUT",
        "included": {
            "labeled_finite_temperature_scattering_cut": True,
            "channel_level_sk_kms_match": True,
            "channel_level_fdt_noise_relation": True,
            "retarded_i0_channel_discontinuity": True,
            "pole_subtracted_channel_real_part": True,
        },
        "excluded": {
            "other_finite_temperature_sunset_cuts": True,
            "full_finite_temperature_1pi_self_energy": True,
            "all_channel_real_part_and_subtraction": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only a representative action-derived finite-temperature 2<->2 "
            "sunset scattering integral with its graph-summed cut weight and channel-level SK/KMS/FDT/PV interface. "
            "It does not close the other thermal cuts, full finite-temperature 1PI, "
            "all-channel real-part subtraction, unique physical renormalization, "
            "transport, entropy-current balance, SI Phi mapping, alpha_Phi_K, TTG, "
            "external validation, or Full Topic 13."
        ),
    }


__all__ = [
    "FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD",
    "SCATTERING_GRAPH_CUT_WEIGHT",
    "SCATTERING_SIGN_PERMUTATION_COUNT",
    "FINITE_T_SCATTERING_SK_KMS_STATUS",
    "FiniteTemperatureScatteringSunsetSKKMSState",
    "finite_temperature_scattering_sunset_sk_kms_contract",
    "finite_temperature_scattering_sunset_sk_kms_state",
]
