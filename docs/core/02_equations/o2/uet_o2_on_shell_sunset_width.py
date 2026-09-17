"""Action-matched on-shell collision-width witness for Topic 13.

The width is obtained from the declared finite-temperature sunset cuts at a
timelike probe. It is a natural-unit on-shell witness, not a complete off-shell
self-energy, a transport coefficient, or an SI observable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi, sqrt, tanh
from typing import Any

from docs.core.uet_o2_finite_temperature_sunset_scattering_sk_kms import (
    finite_temperature_scattering_sunset_sk_kms_state,
)
from docs.core.uet_o2_finite_temperature_sunset_sk_kms import (
    finite_temperature_sunset_sk_kms_state,
)


ON_SHELL_SUNSET_WIDTH_STATUS = (
    "PASS_ACTION_MATCHED_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE"
)
SUNSET_WIDTH_CONVERGENCE_THRESHOLD = 2.0e-2


@dataclass(frozen=True)
class OnShellSunsetCollisionWidthState:
    """Neutral finite-temperature width from the declared sunset cut pair."""

    temperature: float
    chemical_potential: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    invariant_s: float
    external_energy: float
    one_to_three_collision_width: float
    two_to_two_collision_width: float
    combined_collision_width: float
    combined_greater_measure: float
    combined_lesser_measure: float
    combined_spectral_measure: float
    combined_retarded_imaginary_part: float
    combined_kms_log_ratio_residual: float
    combined_fdt_residual: float
    cut_convergence_bound: float
    retarded_sign_is_dissipative: bool
    width_is_positive: bool
    neutral_mu_scope_is_explicit: bool = True
    complete_off_shell_1pi_self_energy_completed: bool = False
    physical_transport_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_MATCHED_NEUTRAL_ON_SHELL_SUNSET_WIDTH_WITNESS_NO_HOLDOUT"
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


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def on_shell_sunset_collision_width_state(
    temperature: float,
    mass_squared: float,
    quartic_coupling: float,
    *,
    chemical_potential: float = 0.0,
    species_count: int = 2,
    invariant_s: float = 5.0,
) -> OnShellSunsetCollisionWidthState:
    """Return ``Gamma_cut=-Im Sigma_R^cut/sqrt(s)`` for the neutral lane.

    The imported sunset modules define the greater/lesser measures and their
    retarded sign. Their thermal weights have no charged chemical-potential
    argument, so only the explicitly declared neutral scope ``mu=0`` is valid.
    """

    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic_coupling = _positive(quartic_coupling, "quartic_coupling")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if chemical_potential != 0.0:
        raise ValueError("on-shell sunset width currently requires chemical_potential=0")
    species_count = _integer(species_count, "species_count", 1)
    invariant_s = _positive(invariant_s, "invariant_s")

    one_to_three = finite_temperature_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic_coupling,
        species_count=species_count,
        invariant_s=invariant_s,
    )
    two_to_two = finite_temperature_scattering_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic_coupling,
        species_count=species_count,
        invariant_s=invariant_s,
    )
    if one_to_three.external_energy != two_to_two.external_energy:
        raise ValueError("sunset channels do not share the declared external energy")

    greater = one_to_three.thermal_greater_measure + two_to_two.thermal_greater_measure
    lesser = one_to_three.thermal_lesser_measure + two_to_two.thermal_lesser_measure
    spectral = greater - lesser
    retarded_imaginary_part = (
        one_to_three.retarded_imaginary_part + two_to_two.retarded_imaginary_part
    )
    expected_retarded_imaginary_part = -pi * spectral
    if not isfinite(expected_retarded_imaginary_part) or spectral <= 0.0:
        raise FloatingPointError("combined sunset spectral measure is invalid")
    if _relative(retarded_imaginary_part, expected_retarded_imaginary_part) > 1.0e-12:
        raise FloatingPointError("combined sunset retarded cut does not compose")

    external_energy = float(one_to_three.external_energy)
    collision_widths = (
        -float(one_to_three.retarded_imaginary_part) / external_energy,
        -float(two_to_two.retarded_imaginary_part) / external_energy,
    )
    combined_collision_width = -float(retarded_imaginary_part) / external_energy
    kms_residual = abs(log(greater) - log(lesser) - external_energy / temperature)
    fdt_target = spectral / tanh(0.5 * external_energy / temperature)
    fdt_residual = _relative(greater + lesser, fdt_target)
    convergence_bound = max(
        one_to_three.inner_quadrature_convergence_residual,
        one_to_three.outer_quadrature_convergence_residual,
        two_to_two.scattering_inner_convergence_residual,
        two_to_two.scattering_outer_convergence_residual,
    )
    values = (
        greater,
        lesser,
        spectral,
        retarded_imaginary_part,
        *collision_widths,
        combined_collision_width,
        kms_residual,
        fdt_residual,
        convergence_bound,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("on-shell sunset width state is not finite")
    if not all(value > 0.0 for value in collision_widths) or combined_collision_width <= 0.0:
        raise FloatingPointError("on-shell sunset collision width is not positive")
    return OnShellSunsetCollisionWidthState(
        temperature=float(temperature),
        chemical_potential=float(chemical_potential),
        mass_squared=float(mass_squared),
        quartic_coupling=float(quartic_coupling),
        species_count=species_count,
        invariant_s=float(invariant_s),
        external_energy=external_energy,
        one_to_three_collision_width=float(collision_widths[0]),
        two_to_two_collision_width=float(collision_widths[1]),
        combined_collision_width=float(combined_collision_width),
        combined_greater_measure=float(greater),
        combined_lesser_measure=float(lesser),
        combined_spectral_measure=float(spectral),
        combined_retarded_imaginary_part=float(retarded_imaginary_part),
        combined_kms_log_ratio_residual=float(kms_residual),
        combined_fdt_residual=float(fdt_residual),
        cut_convergence_bound=float(convergence_bound),
        retarded_sign_is_dissipative=bool(retarded_imaginary_part < 0.0),
        width_is_positive=bool(combined_collision_width > 0.0),
    )


def on_shell_sunset_collision_width_contract() -> dict[str, Any]:
    """Return the width mapping and the boundary against physical promotion."""

    return {
        "status": ON_SHELL_SUNSET_WIDTH_STATUS,
        "equations": {
            "cut_composition": "Sigma_R^cut=Sigma_R^(1<->3)+Sigma_R^(2<->2)",
            "retarded_cut": "Im Sigma_R^cut=-pi*(rho_>^cut-rho_ <^cut)",
            "on_shell_width": "Gamma_cut(s;T)=-Im Sigma_R^cut(s;T)/sqrt(s)",
            "kms": "log(rho_>^cut/rho_ <^cut)=beta_th*sqrt(s)",
            "fdt": "N_cut=(rho_>^cut-rho_ <^cut)*coth(beta_th*sqrt(s)/2)",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "retarded_self_energy_and_spectral_measure": "energy squared",
            "on_shell_collision_width": "energy/inverse time",
            "chemical_potential_scope": "neutral lane only; chemical_potential=0",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived equal-mass O(2) finite-temperature 1<->3 plus labeled "
            "2<->2 sunset cuts; no fitted coefficient"
        ),
        "observable": (
            "declared timelike-probe on-shell collision-width witness, channel split, "
            "KMS/FDT residuals, retarded sign, and quadrature bound"
        ),
        "data_role": "ACTION_MATCHED_NEUTRAL_ON_SHELL_SUNSET_WIDTH_WITNESS_NO_HOLDOUT",
        "included": {
            "declared_timelike_cut_width": True,
            "one_to_three_and_two_to_two_channel_split": True,
            "positive_width_and_unit_closure": True,
            "channel_kms_fdt_and_retarded_sign": True,
            "quadrature_convergence_bound": True,
        },
        "excluded": {
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "unique_physical_renormalization": True,
            "charged_finite_temperature_transport_state": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only a neutral action-matched on-shell sunset collision-width "
            "witness at a declared timelike probe. It does not identify the width with "
            "a complete physical retarded self-energy, transport coefficient, SI map, "
            "alpha_Phi_K, TTG observable, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "ON_SHELL_SUNSET_WIDTH_STATUS",
    "SUNSET_WIDTH_CONVERGENCE_THRESHOLD",
    "OnShellSunsetCollisionWidthState",
    "on_shell_sunset_collision_width_state",
    "on_shell_sunset_collision_width_contract",
]
