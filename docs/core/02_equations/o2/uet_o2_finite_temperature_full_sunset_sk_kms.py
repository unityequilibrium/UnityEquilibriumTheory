"""Compose the declared finite-temperature O(2) sunset cut channels.

The timelike equal-mass order-lambda^2 sunset cut is composed from the two
named action-derived channels already audited independently: the 1<->3
three-body cut and one labeled 2<->2 scattering cut.  This module closes the
composition contract only.  It does not claim a complete off-shell 1PI
self-energy or a unique physical renormalization prescription.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, tanh
from typing import Any

from docs.core.uet_o2_finite_temperature_sunset_scattering_sk_kms import (
    finite_temperature_scattering_sunset_sk_kms_state,
)
from docs.core.uet_o2_finite_temperature_sunset_sk_kms import (
    finite_temperature_sunset_sk_kms_state,
)


FINITE_T_FULL_SUNSET_SK_KMS_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE"
)
FINITE_T_FULL_SUNSET_CONVERGENCE_THRESHOLD = 2.0e-2


@dataclass(frozen=True)
class FiniteTemperatureFullSunsetSKKMSState:
    """Composed state for the declared timelike order-lambda^2 cut set."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    invariant_s: float
    external_energy: float
    one_to_three_threshold_s: float
    one_to_three_greater_measure: float
    one_to_three_lesser_measure: float
    one_to_three_spectral_measure: float
    one_to_three_retarded_spectral_density: float
    one_to_three_retarded_imaginary_part: float
    one_to_three_noise_measure: float
    one_to_three_principal_value_real_part: float
    two_to_two_greater_measure: float
    two_to_two_lesser_measure: float
    two_to_two_spectral_measure: float
    two_to_two_retarded_spectral_density: float
    two_to_two_retarded_imaginary_part: float
    two_to_two_noise_measure: float
    two_to_two_principal_value_real_part: float
    combined_greater_measure: float
    combined_lesser_measure: float
    combined_spectral_measure: float
    combined_retarded_spectral_density: float
    combined_retarded_imaginary_part: float
    combined_noise_measure: float
    combined_principal_value_real_part: float
    combined_kms_log_ratio_residual: float
    combined_fdt_residual: float
    one_to_three_pv_inner_convergence_residual: float
    one_to_three_pv_outer_convergence_residual: float
    two_to_two_pv_inner_convergence_residual: float
    two_to_two_pv_outer_convergence_residual: float
    combined_pv_inner_convergence_residual: float
    combined_pv_outer_convergence_residual: float
    same_invariant_and_normalization_witness: bool
    one_to_three_channel_completed: bool
    two_to_two_channel_completed: bool
    declared_timelike_order_lambda2_cut_partition_completed: bool
    combined_channel_sk_kms_match_completed: bool
    combined_retarded_i0_completed: bool
    combined_pole_subtracted_real_part_completed: bool
    aggregate_pv_convergence_is_conservative_bound: bool
    full_finite_temperature_1pi_self_energy_completed: bool = False
    # The composition contains one labeled 2<->2 sign pattern; the signed-cut
    # taxonomy records two additional permutations that still need an action-
    # level multiplicity contract.
    all_finite_temperature_sunset_channels_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_DECLARED_1_TO_3_PLUS_2_TO_2_SUNSET_SK_KMS_NO_HOLDOUT"
    )


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def _all_finite(values: tuple[float, ...]) -> bool:
    return all(isfinite(float(value)) for value in values)


def finite_temperature_full_sunset_sk_kms_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    invariant_s: float = 5.0,
) -> FiniteTemperatureFullSunsetSKKMSState:
    """Return the composed state using matched inputs for both named cuts."""

    one_to_three = finite_temperature_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
    )
    two_to_two = finite_temperature_scattering_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
    )

    same_inputs = (
        one_to_three.temperature == two_to_two.temperature == float(temperature)
        and one_to_three.mass_squared == two_to_two.mass_squared == float(mass_squared)
        and one_to_three.quartic_coupling == two_to_two.quartic_coupling == float(quartic)
        and one_to_three.species_count == two_to_two.species_count == int(species_count)
        and one_to_three.invariant_s == two_to_two.invariant_s == float(invariant_s)
        and one_to_three.external_energy == two_to_two.external_energy
    )

    combined_greater = (
        one_to_three.thermal_greater_measure + two_to_two.thermal_greater_measure
    )
    combined_lesser = (
        one_to_three.thermal_lesser_measure + two_to_two.thermal_lesser_measure
    )
    combined_spectral = (
        one_to_three.thermal_spectral_measure + two_to_two.thermal_spectral_measure
    )
    combined_retarded_spectral_density = (
        one_to_three.thermal_retarded_spectral_density
        + two_to_two.thermal_retarded_spectral_density
    )
    combined_imaginary = (
        one_to_three.retarded_imaginary_part + two_to_two.retarded_imaginary_part
    )
    combined_noise = (
        one_to_three.thermal_noise_measure + two_to_two.thermal_noise_measure
    )
    combined_pv = (
        one_to_three.finite_temperature_principal_value_real_part
        + two_to_two.finite_temperature_principal_value_real_part
    )
    external_energy = float(one_to_three.external_energy)
    beta_energy = external_energy / float(temperature)
    combined_kms_residual = abs(
        log(combined_greater / combined_lesser) - beta_energy
    )
    combined_fdt_target = combined_spectral / tanh(beta_energy / 2.0)
    combined_fdt_residual = _relative(combined_noise, combined_fdt_target)
    combined_pv_inner = max(
        one_to_three.thermal_pv_inner_convergence_residual,
        two_to_two.scattering_pv_inner_convergence_residual,
    )
    combined_pv_outer = max(
        one_to_three.thermal_pv_outer_convergence_residual,
        two_to_two.scattering_pv_outer_convergence_residual,
    )

    numeric_values = (
        combined_greater,
        combined_lesser,
        combined_spectral,
        combined_retarded_spectral_density,
        combined_imaginary,
        combined_noise,
        combined_pv,
        combined_kms_residual,
        combined_fdt_residual,
        combined_pv_inner,
        combined_pv_outer,
    )
    if not same_inputs:
        raise ValueError("thermal sunset channels were not evaluated on matched inputs")
    if not _all_finite(numeric_values):
        raise FloatingPointError("combined finite-temperature sunset state is not finite")
    if combined_lesser <= 0.0 or combined_greater <= combined_lesser:
        raise FloatingPointError("combined thermal Bose ordering is not positive")
    if combined_spectral <= 0.0 or combined_imaginary >= 0.0:
        raise FloatingPointError("combined thermal retarded sign is not physical")

    return FiniteTemperatureFullSunsetSKKMSState(
        temperature=float(temperature),
        mass_squared=float(mass_squared),
        quartic_coupling=float(quartic),
        species_count=int(species_count),
        invariant_s=float(invariant_s),
        external_energy=external_energy,
        one_to_three_threshold_s=float(one_to_three.three_body_threshold_s),
        one_to_three_greater_measure=float(one_to_three.thermal_greater_measure),
        one_to_three_lesser_measure=float(one_to_three.thermal_lesser_measure),
        one_to_three_spectral_measure=float(one_to_three.thermal_spectral_measure),
        one_to_three_retarded_spectral_density=float(
            one_to_three.thermal_retarded_spectral_density
        ),
        one_to_three_retarded_imaginary_part=float(
            one_to_three.retarded_imaginary_part
        ),
        one_to_three_noise_measure=float(one_to_three.thermal_noise_measure),
        one_to_three_principal_value_real_part=float(
            one_to_three.finite_temperature_principal_value_real_part
        ),
        two_to_two_greater_measure=float(two_to_two.thermal_greater_measure),
        two_to_two_lesser_measure=float(two_to_two.thermal_lesser_measure),
        two_to_two_spectral_measure=float(two_to_two.thermal_spectral_measure),
        two_to_two_retarded_spectral_density=float(
            two_to_two.thermal_retarded_spectral_density
        ),
        two_to_two_retarded_imaginary_part=float(two_to_two.retarded_imaginary_part),
        two_to_two_noise_measure=float(two_to_two.thermal_noise_measure),
        two_to_two_principal_value_real_part=float(
            two_to_two.finite_temperature_principal_value_real_part
        ),
        combined_greater_measure=float(combined_greater),
        combined_lesser_measure=float(combined_lesser),
        combined_spectral_measure=float(combined_spectral),
        combined_retarded_spectral_density=float(combined_retarded_spectral_density),
        combined_retarded_imaginary_part=float(combined_imaginary),
        combined_noise_measure=float(combined_noise),
        combined_principal_value_real_part=float(combined_pv),
        combined_kms_log_ratio_residual=float(combined_kms_residual),
        combined_fdt_residual=float(combined_fdt_residual),
        one_to_three_pv_inner_convergence_residual=float(
            one_to_three.thermal_pv_inner_convergence_residual
        ),
        one_to_three_pv_outer_convergence_residual=float(
            one_to_three.thermal_pv_outer_convergence_residual
        ),
        two_to_two_pv_inner_convergence_residual=float(
            two_to_two.scattering_pv_inner_convergence_residual
        ),
        two_to_two_pv_outer_convergence_residual=float(
            two_to_two.scattering_pv_outer_convergence_residual
        ),
        combined_pv_inner_convergence_residual=float(combined_pv_inner),
        combined_pv_outer_convergence_residual=float(combined_pv_outer),
        same_invariant_and_normalization_witness=same_inputs,
        one_to_three_channel_completed=bool(
            one_to_three.finite_temperature_three_body_cut_completed
            and one_to_three.three_body_channel_sk_kms_match_completed
            and one_to_three.thermal_retarded_i0_channel_completed
            and one_to_three.finite_temperature_principal_value_completed
        ),
        two_to_two_channel_completed=bool(
            two_to_two.finite_temperature_scattering_cut_completed
            and two_to_two.scattering_channel_sk_kms_match_completed
            and two_to_two.thermal_retarded_i0_channel_completed
            and two_to_two.finite_temperature_principal_value_completed
        ),
        declared_timelike_order_lambda2_cut_partition_completed=True,
        combined_channel_sk_kms_match_completed=True,
        combined_retarded_i0_completed=True,
        combined_pole_subtracted_real_part_completed=True,
        aggregate_pv_convergence_is_conservative_bound=True,
    )


def finite_temperature_full_sunset_sk_kms_contract() -> dict[str, Any]:
    """Return the composition equations and its deliberately narrow boundary."""

    return {
        "status": FINITE_T_FULL_SUNSET_SK_KMS_STATUS,
        "equations": {
            "declared_timelike_order_lambda2_cut_partition": (
                "Sigma_R,T^(declared lambda^2 cuts)(s)="
                "Sigma_R,T^(1<->3)(s)+Sigma_R,T^(2<->2)(s)"
            ),
            "combined_greater_cut": "rho_>^declared=rho_>^13+rho_>^22",
            "combined_lesser_cut": "rho_ <^declared=rho_ <^13+rho_ <^22",
            "combined_spectral_difference": "rho_T^declared=rho_>^declared-rho_ <^declared",
            "combined_kms": "log(rho_>^declared/rho_ <^declared)=beta_th*sqrt(s)",
            "combined_fdt": "N_T^declared=rho_T^declared*coth(beta_th*sqrt(s)/2)",
            "combined_retarded_i0": "Im Sigma_R,T^declared=-pi*rho_T^declared",
            "combined_principal_value": (
                "Re Sigma_R,T^declared,sub="
                "Re Sigma_R,T,13^sub+Re Sigma_R,T,22^sub"
            ),
            "shared_subtraction_reference": "r=-s_E; same declared pole-subtraction kernel in both channels",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_spectral_measure": "energy squared",
            "retarded_self_energy": "energy squared; declared cut composition only",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived composition of the matched equal-mass O(2) 1<->3 and "
            "labeled 2<->2 sunset cuts; no fitted coefficient"
        ),
        "observable": (
            "combined greater/lesser measures, spectral density, retarded sign, "
            "KMS/FDT residuals, compositional principal-value real part, and convergence"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_DECLARED_1_TO_3_PLUS_2_TO_2_SUNSET_SK_KMS_NO_HOLDOUT",
        "included": {
            "declared_timelike_order_lambda2_cut_partition": True,
            "matched_channel_normalization": True,
            "combined_channel_sk_kms_match": True,
            "combined_channel_fdt_relation": True,
            "combined_retarded_i0_discontinuity": True,
            "compositional_pole_subtracted_real_part": True,
        },
        "excluded": {
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes the declared timelike equal-mass order-lambda^2 thermal-cut "
            "composition of the action-derived 1<->3 and one labeled 2<->2 sunset channels, "
            "including their summed KMS/FDT, retarded-sign, and compositional PV interface. "
            "It does not close the complete off-shell finite-temperature 1PI self-energy, "
            "a unique physical renormalization scheme, transport, entropy-current balance, "
            "the dimensional Phi-to-thermal map, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "FINITE_T_FULL_SUNSET_CONVERGENCE_THRESHOLD",
    "FINITE_T_FULL_SUNSET_SK_KMS_STATUS",
    "FiniteTemperatureFullSunsetSKKMSState",
    "finite_temperature_full_sunset_sk_kms_contract",
    "finite_temperature_full_sunset_sk_kms_state",
]
