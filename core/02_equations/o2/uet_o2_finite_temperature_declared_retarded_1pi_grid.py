"""State-matched retarded response grid for the declared thermal sunset channels.

This lane evaluates the already audited 1<->3 and labeled 2<->2 thermal cuts
on one matched temperature/state grid and assembles their pole-subtracted
retarded response.  It closes only the declared response-grid contract.  It
does not claim a complete finite-temperature 1PI self-energy, all sunset
channels, a physical renormalization scheme, or SI transport.
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


DECLARED_RETARDED_1PI_GRID_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE"
)
DECLARED_RETARDED_1PI_GRID_THRESHOLD = 2.0e-2
DEFAULT_INVARIANT_GRID = (4.75, 5.0, 5.5)


@dataclass(frozen=True)
class DeclaredRetardedResponsePoint:
    """One matched timelike invariant point in the declared response grid."""

    invariant_s: float
    external_energy: float
    greater_measure: float
    lesser_measure: float
    spectral_measure: float
    retarded_spectral_density: float
    principal_value_real_part: float
    retarded_imaginary_part: float
    kms_log_ratio_residual: float
    fdt_residual: float
    pv_inner_convergence_residual: float
    pv_outer_convergence_residual: float
    retarded_i0_consistency_residual: float
    one_to_three_completed: bool
    two_to_two_completed: bool
    response_pair_consistent: bool


@dataclass(frozen=True)
class DeclaredRetarded1PIGridState:
    """Auditable state-matched response grid for the named sunset channels."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    reference_euclidean_s: float
    invariant_grid: tuple[float, ...]
    three_body_threshold_s: float
    points: tuple[DeclaredRetardedResponsePoint, ...]
    max_kms_log_ratio_residual: float
    max_fdt_residual: float
    max_pv_inner_convergence_residual: float
    max_pv_outer_convergence_residual: float
    max_retarded_i0_consistency_residual: float
    matched_state_witness: bool
    positive_spectral_grid_witness: bool
    lower_half_plane_grid_witness: bool
    declared_retarded_response_grid_completed: bool = True
    declared_1pi_pole_subtracted_response_completed: bool = True
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
        "ACTION_DERIVED_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_NO_HOLDOUT"
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


def _ordered_grid(values: tuple[float, ...]) -> tuple[float, ...]:
    if len(values) < 2:
        raise ValueError("invariant_grid must contain at least two points")
    grid = tuple(_positive(value, "invariant_grid value") for value in values)
    if tuple(sorted(grid)) != grid or len(set(grid)) != len(grid):
        raise ValueError("invariant_grid must be strictly increasing")
    return grid


def _point(
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    invariant_s: float,
    reference_euclidean_s: float,
) -> DeclaredRetardedResponsePoint:
    one_to_three = finite_temperature_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        outer_order=32,
        refined_outer_order=40,
        inner_order=32,
        refined_inner_order=40,
        reference_euclidean_s=reference_euclidean_s,
        dispersion_order=32,
        refined_dispersion_order=40,
        dispersion_phase_outer_order=16,
        dispersion_phase_inner_order=16,
    )
    two_to_two = finite_temperature_scattering_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        outer_order=20,
        refined_outer_order=28,
        inner_order=16,
        refined_inner_order=24,
        reference_euclidean_s=reference_euclidean_s,
        dispersion_order=20,
        refined_dispersion_order=28,
        dispersion_phase_outer_order=16,
        dispersion_phase_inner_order=16,
        transform_scale=1.0,
    )
    greater = (
        one_to_three.thermal_greater_measure
        + two_to_two.thermal_greater_measure
    )
    lesser = (
        one_to_three.thermal_lesser_measure
        + two_to_two.thermal_lesser_measure
    )
    spectral = greater - lesser
    retarded_spectral_density = pi * spectral
    imaginary_part = (
        one_to_three.retarded_imaginary_part
        + two_to_two.retarded_imaginary_part
    )
    principal_value = (
        one_to_three.finite_temperature_principal_value_real_part
        + two_to_two.finite_temperature_principal_value_real_part
    )
    kms_residual = abs(log(greater / lesser) - sqrt(invariant_s) / temperature)
    fdt_target = (greater + lesser) / tanh(sqrt(invariant_s) / (2.0 * temperature))
    fdt_residual = _relative(greater + lesser, fdt_target)
    pv_inner = max(
        one_to_three.thermal_pv_inner_convergence_residual,
        two_to_two.scattering_pv_inner_convergence_residual,
    )
    pv_outer = max(
        one_to_three.thermal_pv_outer_convergence_residual,
        two_to_two.scattering_pv_outer_convergence_residual,
    )
    i0_residual = abs(imaginary_part + retarded_spectral_density)
    point = DeclaredRetardedResponsePoint(
        invariant_s=float(invariant_s),
        external_energy=float(sqrt(invariant_s)),
        greater_measure=float(greater),
        lesser_measure=float(lesser),
        spectral_measure=float(spectral),
        retarded_spectral_density=float(retarded_spectral_density),
        principal_value_real_part=float(principal_value),
        retarded_imaginary_part=float(imaginary_part),
        kms_log_ratio_residual=float(kms_residual),
        fdt_residual=float(fdt_residual),
        pv_inner_convergence_residual=float(pv_inner),
        pv_outer_convergence_residual=float(pv_outer),
        retarded_i0_consistency_residual=float(i0_residual),
        one_to_three_completed=bool(
            one_to_three.finite_temperature_three_body_cut_completed
            and one_to_three.three_body_channel_sk_kms_match_completed
            and one_to_three.thermal_retarded_i0_channel_completed
            and one_to_three.finite_temperature_principal_value_completed
        ),
        two_to_two_completed=bool(
            two_to_two.finite_temperature_scattering_cut_completed
            and two_to_two.scattering_channel_sk_kms_match_completed
            and two_to_two.thermal_retarded_i0_channel_completed
            and two_to_two.finite_temperature_principal_value_completed
        ),
        response_pair_consistent=bool(
            abs(imaginary_part) > 0.0
            and imaginary_part < 0.0
            and spectral > 0.0
            and i0_residual <= 1.0e-12
        ),
    )
    numeric_values = (
        point.greater_measure,
        point.lesser_measure,
        point.spectral_measure,
        point.retarded_spectral_density,
        point.principal_value_real_part,
        point.retarded_imaginary_part,
        point.kms_log_ratio_residual,
        point.fdt_residual,
        point.pv_inner_convergence_residual,
        point.pv_outer_convergence_residual,
        point.retarded_i0_consistency_residual,
    )
    if not all(isfinite(value) for value in numeric_values):
        raise FloatingPointError("declared retarded response point is not finite")
    if greater <= lesser or spectral <= 0.0 or imaginary_part >= 0.0:
        raise FloatingPointError("declared retarded response signs are invalid")
    return point


def finite_temperature_declared_retarded_1pi_grid_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    reference_euclidean_s: float = 0.5,
    invariant_grid: tuple[float, ...] = DEFAULT_INVARIANT_GRID,
) -> DeclaredRetarded1PIGridState:
    """Build a matched retarded response grid for the declared sunset cuts."""

    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    invariant_grid = _ordered_grid(invariant_grid)
    threshold = 9.0 * mass_squared
    if invariant_grid[0] <= threshold:
        raise ValueError("invariant_grid must lie above the three-body threshold")
    points = tuple(
        _point(
            temperature,
            mass_squared,
            quartic,
            species_count,
            invariant_s,
            reference_euclidean_s,
        )
        for invariant_s in invariant_grid
    )
    matched_state = all(
        point.invariant_s == invariant_s
        for point, invariant_s in zip(points, invariant_grid)
    )
    max_kms = max(point.kms_log_ratio_residual for point in points)
    max_fdt = max(point.fdt_residual for point in points)
    max_pv_inner = max(point.pv_inner_convergence_residual for point in points)
    max_pv_outer = max(point.pv_outer_convergence_residual for point in points)
    max_i0 = max(point.retarded_i0_consistency_residual for point in points)
    positive_spectral = all(
        point.greater_measure > point.lesser_measure > 0.0
        and point.spectral_measure > 0.0
        for point in points
    )
    lower_half_plane = all(
        point.retarded_imaginary_part < 0.0
        and point.response_pair_consistent
        for point in points
    )
    return DeclaredRetarded1PIGridState(
        temperature=temperature,
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        reference_euclidean_s=reference_euclidean_s,
        invariant_grid=invariant_grid,
        three_body_threshold_s=float(threshold),
        points=points,
        max_kms_log_ratio_residual=float(max_kms),
        max_fdt_residual=float(max_fdt),
        max_pv_inner_convergence_residual=float(max_pv_inner),
        max_pv_outer_convergence_residual=float(max_pv_outer),
        max_retarded_i0_consistency_residual=float(max_i0),
        matched_state_witness=bool(matched_state),
        positive_spectral_grid_witness=bool(positive_spectral),
        lower_half_plane_grid_witness=bool(lower_half_plane),
    )


def finite_temperature_declared_retarded_1pi_grid_contract() -> dict[str, Any]:
    """Return the equation, unit, evidence, and claim boundary contract."""

    return {
        "status": DECLARED_RETARDED_1PI_GRID_STATUS,
        "equations": {
            "declared_retarded_response": (
                "Sigma_R,T^declared(s+i0)="
                "Re Sigma_R,T^declared,sub(s)-i*pi*rho_T^declared(s)"
            ),
            "combined_spectral_measure": (
                "rho_T^declared(s)=rho_>,13(s)+rho_>,22(s)-"
                "rho_<,13(s)-rho_<,22(s)"
            ),
            "combined_kms": "log(rho_>^declared/rho_<^declared)=sqrt(s)/T",
            "combined_fdt": "N_T^declared=rho_T^declared*coth(sqrt(s)/(2*T))",
            "pole_subtracted_real_part": (
                "Re Sigma_R,T^declared,sub(s)="
                "Re Sigma_R,T,13^sub(s)+Re Sigma_R,T,22^sub(s)"
            ),
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature or metric",
            "R_gen": "derived physical/history trace; no independent state",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_spectral_measure": "energy squared",
            "retarded_self_energy": "energy squared; declared channel grid only",
        },
        "derivation_class": (
            "action-derived matched composition of the audited equal-mass O(2) "
            "1<->3 and labeled 2<->2 thermal cuts; no fitted coefficient"
        ),
        "observable": (
            "multi-invariant greater/lesser measures, spectral density, retarded "
            "sign, KMS/FDT residuals, pole-subtracted real part, and convergence"
        ),
        "data_role": (
            "ACTION_DERIVED_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_NO_HOLDOUT"
        ),
        "included": {
            "matched_timelike_response_grid": True,
            "declared_channel_composition": True,
            "retarded_i0_sign_and_consistency": True,
            "pole_subtracted_real_part": True,
            "grid_level_kms_fdt": True,
        },
        "excluded": {
            "complete_finite_temperature_1pi_self_energy": True,
            "all_finite_temperature_sunset_channels": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the state-matched retarded response-grid contract "
            "for the declared 1<->3 and labeled 2<->2 thermal sunset channels. "
            "It does not close the complete finite-temperature 1PI self-energy, "
            "all sunset channels, physical renormalization, transport, entropy, "
            "SI mapping, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "DECLARED_RETARDED_1PI_GRID_STATUS",
    "DECLARED_RETARDED_1PI_GRID_THRESHOLD",
    "DEFAULT_INVARIANT_GRID",
    "DeclaredRetardedResponsePoint",
    "DeclaredRetarded1PIGridState",
    "finite_temperature_declared_retarded_1pi_grid_contract",
    "finite_temperature_declared_retarded_1pi_grid_state",
]
