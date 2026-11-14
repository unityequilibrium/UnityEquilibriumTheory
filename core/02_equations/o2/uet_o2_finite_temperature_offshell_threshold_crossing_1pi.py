"""Finite-temperature off-shell response across the declared sunset threshold.

The existing real-time machinery is evaluated on a grid below and above the
equal-mass three-body threshold.  Below threshold the 1<->3 cut is absent,
while the declared graph-summed 2<->2 scattering channel can remain nonzero.
The principal-value integral is evaluated with the same subtraction reference
on both sides.  This is a numerical natural-unit response lane, not a claim
of complete microscopic 1PI or physical renormalization closure.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi, sqrt, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_action_1pi_sunset_tensor import (
    expected_sunset_tensor_prefactor,
)
from docs.core.uet_o2_finite_temperature_sunset_scattering_sk_kms import (
    finite_temperature_scattering_sunset_sk_kms_state,
)
from docs.core.uet_o2_finite_temperature_sunset_sk_kms import (
    _thermal_three_body_phase_space,
)


OFFSHELL_THRESHOLD_CROSSING_1PI_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_1PI_LANE"
)
OFFSHELL_THRESHOLD_CROSSING_CONVERGENCE_THRESHOLD = 2.0e-2
OFFSHELL_THRESHOLD_CROSSING_I0_THRESHOLD = 1.0e-12
DEFAULT_OFFSHELL_THRESHOLD_CROSSING_GRID = (
    0.25,
    1.0,
    4.0,
    4.75,
    5.0,
    5.5,
    7.0,
)


@dataclass(frozen=True)
class OffshellThresholdCrossingPoint:
    """One below- or above-threshold all-declared-channel response point."""

    invariant_s: float
    external_energy: float
    below_three_body_threshold: bool
    one_to_three_greater_measure: float
    one_to_three_lesser_measure: float
    one_to_three_spectral_measure: float
    one_to_three_principal_value_real_part: float
    two_to_two_greater_measure: float
    two_to_two_lesser_measure: float
    two_to_two_spectral_measure: float
    two_to_two_principal_value_real_part: float
    combined_greater_measure: float
    combined_lesser_measure: float
    combined_spectral_measure: float
    combined_noise_measure: float
    combined_principal_value_real_part: float
    retarded_imaginary_part: float
    advanced_imaginary_part: float
    keldysh_imaginary_part: float
    one_to_three_pv_convergence_residual: float
    two_to_two_pv_convergence_residual: float
    retarded_advanced_conjugacy_residual: float
    retarded_discontinuity_residual: float
    keldysh_component_residual: float
    keldysh_fdt_residual: float
    one_to_three_support_contract: bool
    two_to_two_below_threshold_nonzero: bool
    response_triplet_completed: bool


@dataclass(frozen=True)
class OffshellThresholdCrossing1PIState:
    """State for the below/above-threshold declared-channel response grid."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    reference_euclidean_s: float
    invariant_grid: tuple[float, ...]
    three_body_threshold_s: float
    points: tuple[OffshellThresholdCrossingPoint, ...]
    below_threshold_point_count: int
    above_threshold_point_count: int
    max_one_to_three_pv_convergence_residual: float
    max_two_to_two_pv_convergence_residual: float
    max_retarded_advanced_conjugacy_residual: float
    max_retarded_discontinuity_residual: float
    max_keldysh_component_residual: float
    max_keldysh_fdt_residual: float
    below_threshold_one_to_three_zero_witness: bool
    above_threshold_one_to_three_nonzero_witness: bool
    below_threshold_two_to_two_nonzero_witness: bool
    offshell_threshold_crossing_response_completed: bool
    complete_off_shell_finite_temperature_1pi_self_energy_completed: bool = False
    all_finite_temperature_sunset_channels_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_NO_HOLDOUT"


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _relative(value: float, reference: float) -> float:
    return abs(float(value) - float(reference)) / max(abs(float(reference)), 1.0e-300)


def _one_to_three_measures(
    invariant_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    *,
    outer_order: int,
    inner_order: int,
) -> tuple[float, float]:
    threshold = 9.0 * mass_squared
    if invariant_s <= threshold:
        return 0.0, 0.0
    greater, lesser, _ = _thermal_three_body_phase_space(
        invariant_s,
        mass_squared,
        temperature,
        outer_order=outer_order,
        inner_order=inner_order,
    )
    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    scale = prefactor / (2.0 * pi)
    return float(scale * greater), float(scale * lesser)


def _one_to_three_principal_value(
    invariant_s: float,
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
    """Evaluate the pole-subtracted 1<->3 PV response on either side of threshold."""

    threshold = 9.0 * mass_squared
    reference_minkowski_s = -reference_euclidean_s
    nodes, weights = np.polynomial.legendre.leggauss(dispersion_order)
    unit_x = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    spectral_s = threshold + transform_scale * unit_x / (1.0 - unit_x)
    jacobian = transform_scale / (1.0 - unit_x) ** 2
    measures = np.array(
        [
            _one_to_three_measures(
                float(value),
                temperature,
                mass_squared,
                quartic,
                species_count,
                outer_order=phase_outer_order,
                inner_order=phase_inner_order,
            )[0]
            - _one_to_three_measures(
                float(value),
                temperature,
                mass_squared,
                quartic,
                species_count,
                outer_order=phase_outer_order,
                inner_order=phase_inner_order,
            )[1]
            for value in spectral_s
        ],
        dtype=float,
    )
    probe_greater, probe_lesser = _one_to_three_measures(
        invariant_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        outer_order=phase_outer_order,
        inner_order=phase_inner_order,
    )
    probe_measure = probe_greater - probe_lesser
    kernel = (
        1.0 / (spectral_s - invariant_s)
        - 1.0 / (spectral_s - reference_minkowski_s)
        - (invariant_s - reference_minkowski_s)
        / (spectral_s - reference_minkowski_s) ** 2
    )
    regularized_integral = float(
        np.sum(scaled_weights * jacobian * (measures - probe_measure) * kernel)
    )
    analytic_pole_integral = log(
        (threshold - reference_minkowski_s)
        / abs(threshold - invariant_s)
    ) - (invariant_s - reference_minkowski_s) / (
        threshold - reference_minkowski_s
    )
    result = regularized_integral + probe_measure * analytic_pole_integral
    if not isfinite(result):
        raise FloatingPointError("one-to-three off-shell PV response is not finite")
    return float(result)


def _one_to_three_response(
    invariant_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    reference_euclidean_s: float,
) -> tuple[float, float, float, float, float]:
    base_greater, base_lesser = _one_to_three_measures(
        invariant_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        outer_order=16,
        inner_order=16,
    )
    refined_greater, refined_lesser = _one_to_three_measures(
        invariant_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        outer_order=24,
        inner_order=20,
    )
    threshold = 9.0 * mass_squared
    transform_scale = threshold / 3.0
    base_pv = _one_to_three_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=16,
        phase_outer_order=16,
        phase_inner_order=16,
        transform_scale=transform_scale,
    )
    refined_pv = _one_to_three_principal_value(
        invariant_s,
        reference_euclidean_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        dispersion_order=24,
        phase_outer_order=20,
        phase_inner_order=20,
        transform_scale=transform_scale,
    )
    return (
        float(refined_greater),
        float(refined_lesser),
        float(refined_pv),
        float(_relative(base_pv, refined_pv)),
        float(_relative(base_greater - base_lesser, refined_greater - refined_lesser)),
    )


def _point(
    invariant_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    reference_euclidean_s: float,
) -> OffshellThresholdCrossingPoint:
    threshold = 9.0 * mass_squared
    one_greater, one_lesser, one_pv, one_pv_residual, _ = _one_to_three_response(
        invariant_s,
        temperature,
        mass_squared,
        quartic,
        species_count,
        reference_euclidean_s,
    )
    scattering = finite_temperature_scattering_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        outer_order=16,
        refined_outer_order=24,
        inner_order=16,
        refined_inner_order=24,
        reference_euclidean_s=reference_euclidean_s,
        # Resolve the low-s PV kernel without changing its threshold or gate.
        dispersion_order=48,
        refined_dispersion_order=64,
        dispersion_phase_outer_order=16,
        dispersion_phase_inner_order=16,
        transform_scale=1.0,
    )
    two_greater = float(scattering.thermal_greater_measure)
    two_lesser = float(scattering.thermal_lesser_measure)
    two_spectral = float(scattering.thermal_spectral_measure)
    two_pv = float(scattering.finite_temperature_principal_value_real_part)
    combined_greater = one_greater + two_greater
    combined_lesser = one_lesser + two_lesser
    combined_spectral = combined_greater - combined_lesser
    combined_noise = combined_greater + combined_lesser
    combined_pv = one_pv + two_pv
    retarded_imaginary = -pi * combined_spectral
    advanced_imaginary = pi * combined_spectral
    keldysh_imaginary = -2.0 * pi * combined_noise
    fdt_target = combined_spectral / tanh(
        sqrt(invariant_s) / (2.0 * temperature)
    )
    conjugacy_residual = abs(retarded_imaginary + advanced_imaginary)
    discontinuity_residual = abs(
        (retarded_imaginary - advanced_imaginary) + 2.0 * pi * combined_spectral
    )
    keldysh_component_residual = abs(
        keldysh_imaginary + 2.0 * pi * combined_noise
    )
    fdt_residual = _relative(combined_noise, fdt_target)
    one_support = (
        abs(one_greater) <= 1.0e-30 and abs(one_lesser) <= 1.0e-30
        if invariant_s <= threshold
        else one_greater > one_lesser > 0.0
    )
    two_nonzero = invariant_s <= threshold and two_spectral > 0.0
    triplet = (
        one_support
        and conjugacy_residual <= OFFSHELL_THRESHOLD_CROSSING_I0_THRESHOLD
        and discontinuity_residual <= OFFSHELL_THRESHOLD_CROSSING_I0_THRESHOLD
        and keldysh_component_residual <= OFFSHELL_THRESHOLD_CROSSING_I0_THRESHOLD
        and fdt_residual <= OFFSHELL_THRESHOLD_CROSSING_CONVERGENCE_THRESHOLD
    )
    values = (
        invariant_s,
        one_greater,
        one_lesser,
        one_pv,
        one_pv_residual,
        two_greater,
        two_lesser,
        two_spectral,
        two_pv,
        combined_greater,
        combined_lesser,
        combined_spectral,
        combined_noise,
        combined_pv,
        retarded_imaginary,
        advanced_imaginary,
        keldysh_imaginary,
        conjugacy_residual,
        discontinuity_residual,
        keldysh_component_residual,
        fdt_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("off-shell threshold-crossing state is not finite")
    return OffshellThresholdCrossingPoint(
        invariant_s=float(invariant_s),
        external_energy=float(sqrt(invariant_s)),
        below_three_body_threshold=bool(invariant_s <= threshold),
        one_to_three_greater_measure=float(one_greater),
        one_to_three_lesser_measure=float(one_lesser),
        one_to_three_spectral_measure=float(one_greater - one_lesser),
        one_to_three_principal_value_real_part=float(one_pv),
        two_to_two_greater_measure=two_greater,
        two_to_two_lesser_measure=two_lesser,
        two_to_two_spectral_measure=two_spectral,
        two_to_two_principal_value_real_part=two_pv,
        combined_greater_measure=float(combined_greater),
        combined_lesser_measure=float(combined_lesser),
        combined_spectral_measure=float(combined_spectral),
        combined_noise_measure=float(combined_noise),
        combined_principal_value_real_part=float(combined_pv),
        retarded_imaginary_part=float(retarded_imaginary),
        advanced_imaginary_part=float(advanced_imaginary),
        keldysh_imaginary_part=float(keldysh_imaginary),
        one_to_three_pv_convergence_residual=float(one_pv_residual),
        two_to_two_pv_convergence_residual=float(
            max(
                scattering.scattering_pv_inner_convergence_residual,
                scattering.scattering_pv_outer_convergence_residual,
            )
        ),
        retarded_advanced_conjugacy_residual=float(conjugacy_residual),
        retarded_discontinuity_residual=float(discontinuity_residual),
        keldysh_component_residual=float(keldysh_component_residual),
        keldysh_fdt_residual=float(fdt_residual),
        one_to_three_support_contract=bool(one_support),
        two_to_two_below_threshold_nonzero=bool(two_nonzero),
        response_triplet_completed=bool(triplet),
    )


def finite_temperature_offshell_threshold_crossing_1pi_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    reference_euclidean_s: float = 0.5,
    invariant_grid: tuple[float, ...] = DEFAULT_OFFSHELL_THRESHOLD_CROSSING_GRID,
) -> OffshellThresholdCrossing1PIState:
    """Evaluate the declared all-channel response below and above threshold."""

    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    grid = tuple(_positive(value, "invariant_grid value") for value in invariant_grid)
    if len(grid) < 4 or tuple(sorted(grid)) != grid or len(set(grid)) != len(grid):
        raise ValueError("invariant_grid must be sorted, unique, and contain at least four points")
    threshold = 9.0 * mass_squared
    if not any(value < threshold for value in grid) or not any(value > threshold for value in grid):
        raise ValueError("invariant_grid must cross the three-body threshold")
    points = tuple(
        _point(
            value,
            temperature,
            mass_squared,
            quartic,
            species_count,
            reference_euclidean_s,
        )
        for value in grid
    )
    below = tuple(point for point in points if point.below_three_body_threshold)
    above = tuple(point for point in points if not point.below_three_body_threshold)
    max_one_pv = max(point.one_to_three_pv_convergence_residual for point in points)
    max_two_pv = max(point.two_to_two_pv_convergence_residual for point in points)
    max_conjugacy = max(point.retarded_advanced_conjugacy_residual for point in points)
    max_discontinuity = max(point.retarded_discontinuity_residual for point in points)
    max_keldysh = max(point.keldysh_component_residual for point in points)
    max_fdt = max(point.keldysh_fdt_residual for point in points)
    below_zero = all(
        abs(point.one_to_three_spectral_measure) <= 1.0e-30 for point in below
    )
    above_nonzero = all(
        point.one_to_three_spectral_measure > 0.0 for point in above
    )
    below_scattering = all(
        point.two_to_two_spectral_measure > 0.0 for point in below
    )
    completed = (
        len(below) >= 1
        and len(above) >= 1
        and all(point.response_triplet_completed for point in points)
        and below_zero
        and above_nonzero
        and below_scattering
        and max_one_pv <= OFFSHELL_THRESHOLD_CROSSING_CONVERGENCE_THRESHOLD
        and max_two_pv <= OFFSHELL_THRESHOLD_CROSSING_CONVERGENCE_THRESHOLD
    )
    return OffshellThresholdCrossing1PIState(
        temperature=temperature,
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        reference_euclidean_s=reference_euclidean_s,
        invariant_grid=grid,
        three_body_threshold_s=float(threshold),
        points=points,
        below_threshold_point_count=len(below),
        above_threshold_point_count=len(above),
        max_one_to_three_pv_convergence_residual=float(max_one_pv),
        max_two_to_two_pv_convergence_residual=float(max_two_pv),
        max_retarded_advanced_conjugacy_residual=float(max_conjugacy),
        max_retarded_discontinuity_residual=float(max_discontinuity),
        max_keldysh_component_residual=float(max_keldysh),
        max_keldysh_fdt_residual=float(max_fdt),
        below_threshold_one_to_three_zero_witness=bool(below_zero),
        above_threshold_one_to_three_nonzero_witness=bool(above_nonzero),
        below_threshold_two_to_two_nonzero_witness=bool(below_scattering),
        offshell_threshold_crossing_response_completed=bool(completed),
    )


def finite_temperature_offshell_threshold_crossing_1pi_contract() -> dict[str, Any]:
    """Return equations, units, evidence role, and claim boundary."""

    return {
        "status": OFFSHELL_THRESHOLD_CROSSING_1PI_STATUS,
        "equations": {
            "three_body_threshold": "s_th=9*m^2",
            "one_to_three_support": "rho_13(s)=0 for s<=s_th; rho_13(s)>0 for s>s_th",
            "two_to_two_support": "rho_22(s)>0 on the declared positive-s grid, including selected s<s_th",
            "retarded_component": "Sigma_R=Re Sigma_sub-i*pi*(rho_13+rho_22)",
            "advanced_component": "Sigma_A=Re Sigma_sub+i*pi*(rho_13+rho_22)=Sigma_R^*",
            "keldysh_component": "Sigma_K=-2*i*pi*N, N=rho_>+rho_<",
            "keldysh_fdt": "N/(rho_13+rho_22)=coth(sqrt(s)/(2*T))",
            "subtraction": "Re Sigma_sub(s)=Re Sigma(s)-Re Sigma(s_*)-(s-s_*)*dRe Sigma/ds|s_*",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature or metric",
            "R_gen": "derived physical/history trace; no independent state or backreaction",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_self_energy": "energy squared",
            "spectral_and_noise_measures": "declared energy squared measure",
            "Phi": "effective response variable; dimensional SI map remains open",
        },
        "derivation_class": (
            "action-derived finite-temperature 1<->3 support, graph-summed 2<->2 "
            "scattering response, pole-subtracted PV continuation, and real-time component identities"
        ),
        "observable": (
            "below/above-threshold spectral support, PV convergence, retarded/advanced "
            "relations, Keldysh FDT, and state-matched response over a crossing grid"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_NO_HOLDOUT",
        "included": {
            "below_threshold_offshell_response": True,
            "above_threshold_offshell_response": True,
            "all_declared_positive_energy_channels": True,
            "retarded_advanced_keldysh_components": True,
            "pole_subtracted_principal_value": True,
        },
        "excluded": {
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
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
            "This closes only a below/above-threshold numerical response lane for the "
            "declared action-derived sunset channels. It does not close the complete "
            "off-shell all-channel finite-temperature 1PI object, select a physical "
            "renormalization anchor, emit physical Kubo transport, close entropy or "
            "heat-flux balance, map Phi to SI, calibrate alpha_Phi_K, validate TTG, "
            "or close Full Topic 13."
        ),
    }


__all__ = [
    "DEFAULT_OFFSHELL_THRESHOLD_CROSSING_GRID",
    "OFFSHELL_THRESHOLD_CROSSING_1PI_STATUS",
    "OFFSHELL_THRESHOLD_CROSSING_CONVERGENCE_THRESHOLD",
    "OffshellThresholdCrossing1PIState",
    "OffshellThresholdCrossingPoint",
    "finite_temperature_offshell_threshold_crossing_1pi_contract",
    "finite_temperature_offshell_threshold_crossing_1pi_state",
]
