"""Match the declared finite-temperature sunset composition to vacuum.

This lane checks the low-temperature limit of the declared timelike thermal
cut composition against the action-derived vacuum retarded sunset at matched
mass, coupling, invariant, normalization, and subtraction reference.  It is
a consistency bridge, not a physical renormalization or full 1PI closure.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from docs.core.uet_o2_action_1pi_sunset_retarded import (
    retarded_vacuum_sunset_state,
)
from docs.core.uet_o2_finite_temperature_full_sunset_sk_kms import (
    finite_temperature_full_sunset_sk_kms_state,
)


FINITE_T_VACUUM_MATCH_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE"
)
FINITE_T_VACUUM_MATCH_THRESHOLD = 1.0e-3
LOW_TEMPERATURE_MAX = 0.1


@dataclass(frozen=True)
class FiniteTemperatureSunsetVacuumMatchState:
    """Low-temperature matching state for the declared sunset cut set."""

    temperature_low: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    invariant_s: float
    external_energy: float
    vacuum_spectral_measure: float
    thermal_spectral_measure: float
    vacuum_retarded_spectral_density: float
    thermal_retarded_spectral_density: float
    vacuum_retarded_imaginary_part: float
    thermal_retarded_imaginary_part: float
    vacuum_principal_value_real_part: float
    thermal_principal_value_real_part: float
    one_to_three_spectral_measure: float
    two_to_two_spectral_measure: float
    thermal_lesser_measure: float
    spectral_relative_residual: float
    retarded_spectral_relative_residual: float
    retarded_imaginary_relative_residual: float
    principal_value_relative_residual: float
    two_to_two_fraction: float
    one_to_three_relative_residual: float
    vacuum_match_completed: bool
    matched_invariant_and_normalization_witness: bool
    physical_renormalization_scheme_match_completed: bool = False
    full_finite_temperature_1pi_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_TO_VACUUM_SUNSET_MATCH_NO_HOLDOUT"
    )


def _relative(value: float, reference: float) -> float:
    return abs(float(value) - float(reference)) / max(abs(float(reference)), 1.0e-300)


def _finite(values: tuple[float, ...]) -> bool:
    return all(isfinite(float(value)) for value in values)


def finite_temperature_sunset_vacuum_match_state(
    temperature_low: float,
    mass_squared: float,
    quartic: float,
    vacuum_euclidean_reference_response: tuple[float, ...],
    *,
    species_count: int = 2,
    invariant_s: float = 5.0,
) -> FiniteTemperatureSunsetVacuumMatchState:
    """Compare the low-temperature composed thermal state with vacuum."""

    temperature_low = float(temperature_low)
    if not isfinite(temperature_low) or temperature_low <= 0.0:
        raise ValueError("temperature_low must be finite and positive")
    if temperature_low > LOW_TEMPERATURE_MAX:
        raise ValueError("temperature_low must be within the declared low-T window")
    if len(vacuum_euclidean_reference_response) != 5:
        raise ValueError("vacuum Euclidean reference response must contain five probes")

    vacuum = retarded_vacuum_sunset_state(
        mass_squared,
        quartic,
        tuple(float(value) for value in vacuum_euclidean_reference_response),
        species_count=species_count,
        timelike_probe_s=invariant_s,
    )
    thermal = finite_temperature_full_sunset_sk_kms_state(
        temperature_low,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
    )
    matched_inputs = (
        vacuum.mass_squared == thermal.mass_squared
        and vacuum.quartic_coupling == thermal.quartic_coupling
        and vacuum.species_count == thermal.species_count
        and vacuum.timelike_probe_s == thermal.invariant_s
        and abs(vacuum.sunset_tensor_prefactor - 5.12) <= 1.0e-12
    )
    spectral_residual = _relative(
        thermal.combined_spectral_measure,
        vacuum.spectral_measure_at_timelike_probe,
    )
    retarded_spectral_residual = _relative(
        thermal.combined_retarded_spectral_density,
        vacuum.retarded_spectral_density_at_timelike_probe,
    )
    imaginary_residual = _relative(
        thermal.combined_retarded_imaginary_part,
        vacuum.retarded_imaginary_part_at_timelike_probe,
    )
    principal_value_residual = _relative(
        thermal.combined_principal_value_real_part,
        vacuum.above_threshold_principal_value_real_part,
    )
    two_to_two_fraction = thermal.two_to_two_spectral_measure / max(
        thermal.combined_spectral_measure, 1.0e-300
    )
    one_to_three_residual = _relative(
        thermal.one_to_three_spectral_measure,
        vacuum.spectral_measure_at_timelike_probe,
    )
    finite_values = (
        thermal.combined_spectral_measure,
        thermal.combined_retarded_spectral_density,
        thermal.combined_retarded_imaginary_part,
        thermal.combined_principal_value_real_part,
        spectral_residual,
        retarded_spectral_residual,
        imaginary_residual,
        principal_value_residual,
        two_to_two_fraction,
        one_to_three_residual,
    )
    if not matched_inputs:
        raise ValueError("vacuum and thermal sunset inputs are not matched")
    if not _finite(finite_values):
        raise FloatingPointError("vacuum-match state is not finite")
    if vacuum.retarded_imaginary_part_at_timelike_probe >= 0.0:
        raise FloatingPointError("vacuum retarded imaginary sign is not negative")
    if thermal.combined_retarded_imaginary_part >= 0.0:
        raise FloatingPointError("thermal retarded imaginary sign is not negative")

    vacuum_match = (
        matched_inputs
        and spectral_residual <= FINITE_T_VACUUM_MATCH_THRESHOLD
        and retarded_spectral_residual <= FINITE_T_VACUUM_MATCH_THRESHOLD
        and imaginary_residual <= FINITE_T_VACUUM_MATCH_THRESHOLD
        and principal_value_residual <= FINITE_T_VACUUM_MATCH_THRESHOLD
        and two_to_two_fraction <= FINITE_T_VACUUM_MATCH_THRESHOLD
        and one_to_three_residual <= FINITE_T_VACUUM_MATCH_THRESHOLD
    )
    return FiniteTemperatureSunsetVacuumMatchState(
        temperature_low=temperature_low,
        mass_squared=float(mass_squared),
        quartic_coupling=float(quartic),
        species_count=int(species_count),
        invariant_s=float(invariant_s),
        external_energy=float(thermal.external_energy),
        vacuum_spectral_measure=float(vacuum.spectral_measure_at_timelike_probe),
        thermal_spectral_measure=float(thermal.combined_spectral_measure),
        vacuum_retarded_spectral_density=float(
            vacuum.retarded_spectral_density_at_timelike_probe
        ),
        thermal_retarded_spectral_density=float(
            thermal.combined_retarded_spectral_density
        ),
        vacuum_retarded_imaginary_part=float(
            vacuum.retarded_imaginary_part_at_timelike_probe
        ),
        thermal_retarded_imaginary_part=float(
            thermal.combined_retarded_imaginary_part
        ),
        vacuum_principal_value_real_part=float(
            vacuum.above_threshold_principal_value_real_part
        ),
        thermal_principal_value_real_part=float(
            thermal.combined_principal_value_real_part
        ),
        one_to_three_spectral_measure=float(thermal.one_to_three_spectral_measure),
        two_to_two_spectral_measure=float(thermal.two_to_two_spectral_measure),
        thermal_lesser_measure=float(thermal.combined_lesser_measure),
        spectral_relative_residual=float(spectral_residual),
        retarded_spectral_relative_residual=float(retarded_spectral_residual),
        retarded_imaginary_relative_residual=float(imaginary_residual),
        principal_value_relative_residual=float(principal_value_residual),
        two_to_two_fraction=float(two_to_two_fraction),
        one_to_three_relative_residual=float(one_to_three_residual),
        vacuum_match_completed=bool(vacuum_match),
        matched_invariant_and_normalization_witness=bool(matched_inputs),
    )


def finite_temperature_sunset_vacuum_match_contract() -> dict[str, Any]:
    """Return the low-temperature matching equations and claim boundary."""

    return {
        "status": FINITE_T_VACUUM_MATCH_STATUS,
        "equations": {
            "low_temperature_limit": "lim_(T->0+) rho_T^declared(s)=rho_vacuum(s)",
            "retarded_spectral_match": "lim_(T->0+) (-Im Sigma_R,T^declared/pi)=rho_vacuum(s)",
            "principal_value_match": "lim_(T->0+) Re Sigma_R,T^declared,sub(s)=Re Sigma_R,vacuum,sub(s)",
            "scattering_vacuum_boundary": "lim_(T->0+) rho_T^(2<->2)(s)=0",
            "matching_window": "T_low <= 0.1 in the declared natural-energy test lane",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_spectral_measure": "energy squared",
            "retarded_self_energy": "energy squared; consistency bridge only",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived low-temperature limit comparison between the declared "
            "finite-temperature cut composition and the vacuum retarded sunset"
        ),
        "observable": (
            "relative spectral, retarded-sign, imaginary-part, and PV matching residuals "
            "plus the vanishing 2<->2 fraction"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_TO_VACUUM_SUNSET_MATCH_NO_HOLDOUT",
        "included": {
            "matched_vacuum_and_thermal_invariant": True,
            "low_temperature_spectral_match": True,
            "low_temperature_retarded_sign_match": True,
            "low_temperature_principal_value_match": True,
            "two_to_two_vacuum_boundary": True,
        },
        "excluded": {
            "physical_renormalization_scheme_match": True,
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the declared low-temperature consistency match between the "
            "finite-temperature sunset cut composition and the action-derived vacuum retarded "
            "sunset. It does not select a physical renormalization scheme, close the complete "
            "off-shell 1PI self-energy, derive transport or entropy balance, map Phi to SI, "
            "calibrate alpha_Phi_K, validate TTG, or close Full Topic 13."
        ),
    }


__all__ = [
    "FINITE_T_VACUUM_MATCH_STATUS",
    "FINITE_T_VACUUM_MATCH_THRESHOLD",
    "LOW_TEMPERATURE_MAX",
    "FiniteTemperatureSunsetVacuumMatchState",
    "finite_temperature_sunset_vacuum_match_contract",
    "finite_temperature_sunset_vacuum_match_state",
]
