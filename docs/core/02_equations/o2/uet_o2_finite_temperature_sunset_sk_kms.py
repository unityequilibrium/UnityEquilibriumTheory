"""Finite-temperature 1<->3 sunset-channel SK/KMS interface.

This module extends the action-derived equal-mass O(2) vacuum sunset cut by
including Bose weights on the same three-body phase space.  It closes only
the named 1<->3 thermal channel: finite-temperature scattering/Landau
channels, the complete retarded 1PI real part, physical renormalization,
transport, and the SI observable map remain outside this lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import expm1, isfinite, log, pi, sqrt, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_action_1pi_sunset_retarded import (
    three_body_phase_space,
    vacuum_sunset_spectral_measure,
)
from docs.core.uet_o2_action_1pi_sunset_tensor import (
    expected_sunset_tensor_prefactor,
)


FINITE_T_SUNSET_SK_KMS_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE"
)
FINITE_T_SUNSET_CONVERGENCE_THRESHOLD = 2.0e-2


@dataclass(frozen=True)
class FiniteTemperatureSunsetSKKMSState:
    """Thermal Bose-weighted 1<->3 sunset-channel state."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    invariant_s: float
    external_energy: float
    three_body_threshold_s: float
    vacuum_spectral_measure: float
    thermal_greater_measure: float
    thermal_lesser_measure: float
    thermal_spectral_measure: float
    thermal_retarded_spectral_density: float
    retarded_imaginary_part: float
    thermal_noise_measure: float
    finite_temperature_principal_value_real_part: float
    thermal_pv_inner_convergence_residual: float
    thermal_pv_outer_convergence_residual: float
    vacuum_phase_space_normalization_residual: float
    kms_log_ratio_residual: float
    fdt_residual: float
    inner_quadrature_convergence_residual: float
    outer_quadrature_convergence_residual: float
    thermal_enhancement_ratio: float
    greater_is_positive: bool
    lesser_is_positive: bool
    spectral_difference_is_positive: bool
    retarded_imaginary_sign_witness: bool
    finite_temperature_three_body_cut_completed: bool = True
    three_body_channel_sk_kms_match_completed: bool = True
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
        "ACTION_DERIVED_FINITE_T_1_TO_3_SUNSET_SK_KMS_CHANNEL_NO_HOLDOUT"
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


def _thermal_three_body_phase_space(
    invariant_s: float,
    mass_squared: float,
    temperature: float,
    *,
    outer_order: int,
    inner_order: int,
) -> tuple[float, float, float]:
    """Return greater, lesser, and unweighted equal-mass three-body phase space.

    The pair invariant is the outer variable.  The pair-rest-frame angle is
    retained so the Bose weights use the individual daughter energies rather
    than an angle-averaged surrogate.
    """

    invariant_s = _positive(invariant_s, "invariant_s")
    mass_squared = _positive(mass_squared, "mass_squared")
    temperature = _positive(temperature, "temperature")
    outer_order = _integer(outer_order, "outer_order", 16)
    inner_order = _integer(inner_order, "inner_order", 16)
    threshold = 9.0 * mass_squared
    if invariant_s <= threshold:
        return 0.0, 0.0, 0.0
    mass = sqrt(mass_squared)
    root_s = sqrt(invariant_s)
    lower = 4.0 * mass_squared
    upper = (root_s - mass) ** 2
    if upper <= lower:
        return 0.0, 0.0, 0.0

    outer_nodes, outer_weights = np.polynomial.legendre.leggauss(outer_order)
    inner_nodes, inner_weights = np.polynomial.legendre.leggauss(inner_order)
    pair_invariants = 0.5 * (upper - lower) * (outer_nodes + 1.0) + lower
    pair_weights = 0.5 * (upper - lower) * outer_weights
    greater_total = 0.0
    lesser_total = 0.0
    phase_total = 0.0
    for pair_s, pair_weight in zip(pair_invariants, pair_weights):
        pair_s = float(pair_s)
        kallen_parent = (
            invariant_s - pair_s - mass_squared
        ) ** 2 - 4.0 * pair_s * mass_squared
        kallen_pair = pair_s * (pair_s - 4.0 * mass_squared)
        common = sqrt(max(kallen_parent, 0.0)) * sqrt(
            max(kallen_pair, 0.0)
        ) / (invariant_s * pair_s)
        pair_root = sqrt(pair_s)
        pair_energy = (invariant_s + pair_s - mass_squared) / (2.0 * root_s)
        spectator_energy = (
            invariant_s - pair_s + mass_squared
        ) / (2.0 * root_s)
        pair_momentum = sqrt(max(kallen_parent, 0.0)) / (2.0 * root_s)
        boost = pair_momentum / pair_energy
        gamma = pair_energy / pair_root
        daughter_energy_star = 0.5 * pair_root
        daughter_momentum_star = sqrt(max(0.25 * pair_s - mass_squared, 0.0))
        greater_average = 0.0
        lesser_average = 0.0
        for cosine, angle_weight in zip(inner_nodes, inner_weights):
            cosine = float(cosine)
            energy_one = gamma * (
                daughter_energy_star + boost * daughter_momentum_star * cosine
            )
            energy_two = gamma * (
                daughter_energy_star - boost * daughter_momentum_star * cosine
            )
            occupation_one = _bose(energy_one, temperature)
            occupation_two = _bose(energy_two, temperature)
            occupation_three = _bose(spectator_energy, temperature)
            greater_average += 0.5 * float(angle_weight) * (
                1.0 + occupation_one
            ) * (1.0 + occupation_two) * (1.0 + occupation_three)
            lesser_average += 0.5 * float(angle_weight) * occupation_one * occupation_two * occupation_three
        weighted_measure = float(pair_weight) * common
        greater_total += weighted_measure * greater_average
        lesser_total += weighted_measure * lesser_average
        phase_total += weighted_measure
    normalization = 128.0 * pi**3
    return (
        float(greater_total / normalization),
        float(lesser_total / normalization),
        float(phase_total / normalization),
    )


def _thermal_spectral_measure(
    invariant_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    *,
    phase_outer_order: int,
    phase_inner_order: int,
) -> float:
    greater, lesser, _ = _thermal_three_body_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=phase_outer_order,
        inner_order=phase_inner_order,
    )
    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    result = prefactor * (greater - lesser) / (2.0 * pi)
    if not isfinite(result) or result <= 0.0:
        raise FloatingPointError("thermal spectral measure is not finite and positive")
    return float(result)


def _finite_temperature_principal_value(
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
    """Evaluate the thermal channel real part with an analytic pole term."""

    timelike_s = _positive(timelike_s, "timelike_s")
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    dispersion_order = _integer(dispersion_order, "dispersion_order", 32)
    phase_outer_order = _integer(phase_outer_order, "phase_outer_order", 16)
    phase_inner_order = _integer(phase_inner_order, "phase_inner_order", 16)
    transform_scale = _positive(transform_scale, "transform_scale")
    threshold = 9.0 * mass_squared
    if timelike_s <= threshold:
        raise ValueError("timelike_s must be above the three-body threshold")

    reference_minkowski_s = -reference_euclidean_s
    nodes, weights = np.polynomial.legendre.leggauss(dispersion_order)
    unit_x = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    spectral_s = threshold + transform_scale * unit_x / (1.0 - unit_x)
    jacobian = transform_scale / (1.0 - unit_x) ** 2
    measures = np.array(
        [
            _thermal_spectral_measure(
                float(value),
                temperature,
                mass_squared,
                quartic,
                species_count,
                phase_outer_order=phase_outer_order,
                phase_inner_order=phase_inner_order,
            )
            for value in spectral_s
        ]
    )
    probe_measure = _thermal_spectral_measure(
        timelike_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        phase_outer_order=phase_outer_order,
        phase_inner_order=phase_inner_order,
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
        (threshold - reference_minkowski_s)
        / abs(threshold - timelike_s)
    ) - (timelike_s - reference_minkowski_s) / (
        threshold - reference_minkowski_s
    )
    result = regularized_integral + probe_measure * analytic_pole_integral
    if not isfinite(result):
        raise FloatingPointError("thermal principal-value real part is not finite")
    return float(result)


def finite_temperature_sunset_sk_kms_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    invariant_s: float = 5.0,
    outer_order: int = 64,
    refined_outer_order: int | None = None,
    inner_order: int = 48,
    refined_inner_order: int | None = None,
    reference_euclidean_s: float = 0.5,
    dispersion_order: int = 48,
    refined_dispersion_order: int | None = None,
    dispersion_phase_outer_order: int = 32,
    dispersion_phase_inner_order: int = 24,
    transform_scale: float | None = None,
) -> FiniteTemperatureSunsetSKKMSState:
    """Evaluate the action-derived finite-temperature 1<->3 channel."""

    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    invariant_s = _positive(invariant_s, "invariant_s")
    outer_order = _integer(outer_order, "outer_order", 32)
    inner_order = _integer(inner_order, "inner_order", 32)
    if refined_outer_order is None:
        refined_outer_order = outer_order + 32
    if refined_inner_order is None:
        refined_inner_order = inner_order + 24
    refined_outer_order = _integer(
        refined_outer_order,
        "refined_outer_order",
        outer_order + 1,
    )
    refined_inner_order = _integer(
        refined_inner_order,
        "refined_inner_order",
        inner_order + 1,
    )
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    dispersion_order = _integer(dispersion_order, "dispersion_order", 32)
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
    threshold = 9.0 * mass_squared
    if invariant_s <= threshold:
        raise ValueError("invariant_s must be above the three-body threshold")
    if transform_scale is None:
        transform_scale = threshold / 3.0
    transform_scale = _positive(transform_scale, "transform_scale")

    greater_phase, lesser_phase, base_phase = _thermal_three_body_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=outer_order,
        inner_order=inner_order,
    )
    refined_greater, refined_lesser, refined_base = (
        _thermal_three_body_phase_space(
            invariant_s,
            mass_squared,
            temperature,
            outer_order=refined_outer_order,
            inner_order=refined_inner_order,
        )
    )
    inner_refined_outer = _thermal_three_body_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=refined_outer_order,
        inner_order=inner_order,
    )
    outer_refined_inner = _thermal_three_body_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=outer_order,
        inner_order=refined_inner_order,
    )
    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    measure_scale = prefactor / (2.0 * pi)
    vacuum_measure = vacuum_sunset_spectral_measure(
        invariant_s,
        mass_squared,
        quartic,
        species_count=species_count,
        inner_order=refined_outer_order,
    )
    greater_measure = measure_scale * greater_phase
    lesser_measure = measure_scale * lesser_phase
    spectral_measure = greater_measure - lesser_measure
    retarded_spectral_density = pi * spectral_measure
    imaginary_part = -retarded_spectral_density
    noise_measure = greater_measure + lesser_measure
    external_energy = sqrt(invariant_s)
    log_kms_ratio = log(greater_measure) - log(lesser_measure)
    log_kms_target = external_energy / temperature
    fdt_target = spectral_measure / tanh(0.5 * log_kms_target)
    inner_convergence = max(
        _relative(inner_refined_outer[0], refined_greater),
        _relative(inner_refined_outer[1], refined_lesser),
    )
    outer_convergence = max(
        _relative(outer_refined_inner[0], refined_greater),
        _relative(outer_refined_inner[1], refined_lesser),
    )
    normalization_reference = three_body_phase_space(
        invariant_s,
        mass_squared,
        inner_order=refined_outer_order,
    )
    normalization_residual = _relative(base_phase, normalization_reference)
    pv_real = _finite_temperature_principal_value(
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
    pv_refined = _finite_temperature_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=refined_dispersion_order,
        phase_outer_order=dispersion_phase_outer_order + 16,
        phase_inner_order=dispersion_phase_inner_order + 16,
        transform_scale=transform_scale,
    )
    pv_inner_refined_phase = _finite_temperature_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=dispersion_order,
        phase_outer_order=dispersion_phase_outer_order + 16,
        phase_inner_order=dispersion_phase_inner_order + 16,
        transform_scale=transform_scale,
    )
    pv_outer_refined_dispersion = _finite_temperature_principal_value(
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
    pv_inner_convergence = _relative(pv_inner_refined_phase, pv_refined)
    pv_outer_convergence = _relative(pv_outer_refined_dispersion, pv_refined)
    values = (
        vacuum_measure,
        greater_measure,
        lesser_measure,
        spectral_measure,
        retarded_spectral_density,
        imaginary_part,
        noise_measure,
        fdt_target,
        log_kms_ratio,
        log_kms_target,
        inner_convergence,
        outer_convergence,
        normalization_residual,
        refined_base,
        pv_real,
        pv_refined,
        pv_inner_convergence,
        pv_outer_convergence,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("finite-temperature sunset state is not finite")
    if lesser_measure <= 0.0 or greater_measure <= lesser_measure:
        raise FloatingPointError("thermal 1<->3 Bose ordering is not positive")
    return FiniteTemperatureSunsetSKKMSState(
        temperature=temperature,
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        external_energy=external_energy,
        three_body_threshold_s=threshold,
        vacuum_spectral_measure=float(vacuum_measure),
        thermal_greater_measure=float(greater_measure),
        thermal_lesser_measure=float(lesser_measure),
        thermal_spectral_measure=float(spectral_measure),
        thermal_retarded_spectral_density=float(retarded_spectral_density),
        retarded_imaginary_part=float(imaginary_part),
        thermal_noise_measure=float(noise_measure),
        finite_temperature_principal_value_real_part=float(pv_real),
        thermal_pv_inner_convergence_residual=float(pv_inner_convergence),
        thermal_pv_outer_convergence_residual=float(pv_outer_convergence),
        vacuum_phase_space_normalization_residual=float(normalization_residual),
        kms_log_ratio_residual=float(abs(log_kms_ratio - log_kms_target)),
        fdt_residual=float(
            abs(noise_measure - fdt_target) / max(abs(fdt_target), 1.0e-300)
        ),
        inner_quadrature_convergence_residual=float(inner_convergence),
        outer_quadrature_convergence_residual=float(outer_convergence),
        thermal_enhancement_ratio=float(greater_measure / vacuum_measure),
        greater_is_positive=greater_measure > 0.0,
        lesser_is_positive=lesser_measure > 0.0,
        spectral_difference_is_positive=spectral_measure > 0.0,
        retarded_imaginary_sign_witness=imaginary_part < 0.0,
    )


def finite_temperature_sunset_sk_kms_contract() -> dict[str, Any]:
    """Return equations, units, and the channel-level claim boundary."""

    return {
        "status": FINITE_T_SUNSET_SK_KMS_STATUS,
        "equations": {
            "three_body_threshold": "s_th=9*m^2",
            "thermal_greater_cut": (
                "rho_>(s;T)=prefactor/(2*pi)*integral dPhi_3 "
                "prod_i(1+n_B(E_i))"
            ),
            "thermal_lesser_cut": (
                "rho_<(s;T)=prefactor/(2*pi)*integral dPhi_3 "
                "prod_i n_B(E_i)"
            ),
            "thermal_spectral_difference": "rho_T(s)=rho_>(s;T)-rho_<(s;T)",
            "thermal_kms": "log(rho_>/rho_<)=beta_th*sqrt(s)",
            "thermal_fdt": "N_T(s)=rho_T(s)*coth(beta_th*sqrt(s)/2)",
            "retarded_i0_channel": "Im Sigma_R,T(s)=-pi*rho_T(s)",
            "vacuum_normalization": "dPhi_3(T weights removed)=Phi_3(s)",
            "thermal_pole_subtracted_principal_value": (
                "Re Sigma_R,T^sub(s)=PV integral_[s_th,infty] "
                "[rho_T(S)-rho_T(s)] K_sub(S)dS + rho_T(s) A(s)"
            ),
            "thermal_pole_subtraction_kernel": (
                "K_sub(S)=1/(S-s)-1/(S-r)-(s-r)/(S-r)^2; r=-s_E"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_spectral_measure": "energy squared",
            "retarded_self_energy": "energy squared; channel interface only",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived O(2) sunset tensor prefactor and equal-mass three-body "
            "phase space with explicit finite-temperature Bose weights"
        ),
        "observable": (
            "thermal greater/lesser channel measures, retarded spectral sign, "
            "KMS log ratio, FDT noise relation, pole-subtracted retarded real part, and quadrature convergence"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_1_TO_3_SUNSET_SK_KMS_CHANNEL_NO_HOLDOUT",
        "included": {
            "finite_temperature_three_body_channel": True,
            "channel_level_sk_kms_match": True,
            "channel_level_fdt_noise_relation": True,
            "retarded_i0_channel_discontinuity": True,
            "vacuum_phase_space_normalization": True,
            "finite_temperature_principal_value_real_part": True,
        },
        "excluded": {
            "all_finite_temperature_sunset_channels": True,
            "full_finite_temperature_1pi_self_energy": True,
            "full_finite_temperature_real_part_subtraction": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the action-derived finite-temperature 1<->3 sunset "
            "channel, its channel-level SK/KMS/FDT identities, and its pole-subtracted "
            "retarded real part. It does not close the other thermal cuts, the full "
            "retarded 1PI self-energy, all-channel real-part subtraction, unique physical renormalization, transport, entropy-current "
            "balance, SI Phi mapping, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "FINITE_T_SUNSET_CONVERGENCE_THRESHOLD",
    "FINITE_T_SUNSET_SK_KMS_STATUS",
    "FiniteTemperatureSunsetSKKMSState",
    "finite_temperature_sunset_sk_kms_contract",
    "finite_temperature_sunset_sk_kms_state",
]
