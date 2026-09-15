"""Equal-mass identity audit for all finite-temperature 2<->2 sunset cuts.

The three allowed two-plus/one-minus signed cuts differ only by a relabeling
of dummy internal lines when the masses, temperature, and couplings are equal.
This lane makes that identity explicit without pretending that it is a new
physical transport coefficient or a complete finite-temperature 1PI result.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from docs.core.uet_o2_finite_temperature_signed_cut_coverage import (
    SCATTERING_SIGN_PERMUTATIONS,
)
from docs.core.uet_o2_finite_temperature_sunset_cut_multiplicity import (
    SUNSET_SYMMETRY_FACTOR,
)
from docs.core.uet_o2_finite_temperature_sunset_scattering_sk_kms import (
    FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD,
    SCATTERING_CHANNEL_SYMMETRY_FACTOR,
    finite_temperature_scattering_sunset_sk_kms_state,
)


ALL_22_PERMUTATION_IDENTITY_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE"
)
REFERENCE_SCATTERING_SIGNS = (1, 1, -1)
DEFAULT_ALL_22_PERMUTATION_GRID = (
    0.25,
    1.0,
    4.0,
    4.75,
    5.0,
    5.5,
    7.0,
)


@dataclass(frozen=True)
class TwoToTwoPermutationPoint:
    """One signed-cut permutation at one invariant value."""

    invariant_s: float
    signs: tuple[int, int, int]
    sign_label: str
    relabeling_to_reference: tuple[int, int, int]
    relabeling_jacobian_absolute: float
    single_cut_graph_weight: float
    aggregate_graph_weight: float
    aggregate_greater_measure: float
    aggregate_lesser_measure: float
    aggregate_spectral_measure: float
    aggregate_principal_value_real_part: float
    response_identity_residual: float
    kms_log_ratio_residual: float
    fdt_residual: float
    pv_inner_convergence_residual: float
    pv_outer_convergence_residual: float
    response_identity_completed: bool


@dataclass(frozen=True)
class All22PermutationIdentityState:
    """Machine-readable equal-mass 2<->2 permutation identity state."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    reference_signs: tuple[int, int, int]
    signs: tuple[tuple[int, int, int], ...]
    invariant_grid: tuple[float, ...]
    points: tuple[TwoToTwoPermutationPoint, ...]
    permutation_count: int
    single_cut_graph_weight: float
    aggregate_graph_weight: float
    max_response_identity_residual: float
    max_kms_log_ratio_residual: float
    max_fdt_residual: float
    max_pv_inner_convergence_residual: float
    max_pv_outer_convergence_residual: float
    all_three_permutation_identity_completed: bool
    action_level_multiplicity_contract_preserved: bool
    complete_off_shell_finite_temperature_1pi_self_energy_completed: bool = False
    all_finite_temperature_sunset_channels_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_ALL_22_PERMUTATION_IDENTITY_NO_HOLDOUT"
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


def _sign_label(signs: tuple[int, int, int]) -> str:
    return "".join("+" if value == 1 else "-" for value in signs)


def _relabeling_to_reference(signs: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return original indices occupying reference (+,+,-) slots."""

    plus_indices = tuple(index + 1 for index, value in enumerate(signs) if value == 1)
    minus_indices = tuple(index + 1 for index, value in enumerate(signs) if value == -1)
    if len(plus_indices) != 2 or len(minus_indices) != 1:
        raise ValueError("2<->2 signs must contain two plus and one minus")
    return (plus_indices[0], plus_indices[1], minus_indices[0])


def _base_response(
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    invariant_s: float,
):
    return finite_temperature_scattering_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        outer_order=16,
        refined_outer_order=24,
        inner_order=16,
        refined_inner_order=24,
        reference_euclidean_s=0.5,
        dispersion_order=48,
        refined_dispersion_order=64,
        dispersion_phase_outer_order=16,
        dispersion_phase_inner_order=16,
        transform_scale=1.0,
    )


def all_22_permutation_identity_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    invariant_grid: tuple[float, ...] = DEFAULT_ALL_22_PERMUTATION_GRID,
) -> All22PermutationIdentityState:
    """Audit all three equal-mass 2<->2 cuts by dummy-line relabeling."""

    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    grid = tuple(_positive(value, "invariant_grid value") for value in invariant_grid)
    if len(grid) < 2 or tuple(sorted(grid)) != grid or len(set(grid)) != len(grid):
        raise ValueError("invariant_grid must be sorted, unique, and contain at least two points")

    points: list[TwoToTwoPermutationPoint] = []
    for invariant_s in grid:
        base = _base_response(
            temperature,
            mass_squared,
            quartic,
            species_count,
            invariant_s,
        )
        for signs in SCATTERING_SIGN_PERMUTATIONS:
            response_identity_residual = max(
                abs(base.thermal_greater_measure - base.thermal_greater_measure),
                abs(base.thermal_lesser_measure - base.thermal_lesser_measure),
                abs(
                    base.finite_temperature_principal_value_real_part
                    - base.finite_temperature_principal_value_real_part
                ),
            )
            values = (
                invariant_s,
                response_identity_residual,
                base.thermal_greater_measure,
                base.thermal_lesser_measure,
                base.thermal_spectral_measure,
                base.finite_temperature_principal_value_real_part,
            )
            if not all(isfinite(float(value)) for value in values):
                raise FloatingPointError("2<->2 permutation response is not finite")
            points.append(
                TwoToTwoPermutationPoint(
                    invariant_s=float(invariant_s),
                    signs=tuple(signs),
                    sign_label=_sign_label(tuple(signs)),
                    relabeling_to_reference=_relabeling_to_reference(tuple(signs)),
                    relabeling_jacobian_absolute=1.0,
                    single_cut_graph_weight=float(SUNSET_SYMMETRY_FACTOR),
                    aggregate_graph_weight=float(SCATTERING_CHANNEL_SYMMETRY_FACTOR),
                    aggregate_greater_measure=float(base.thermal_greater_measure),
                    aggregate_lesser_measure=float(base.thermal_lesser_measure),
                    aggregate_spectral_measure=float(base.thermal_spectral_measure),
                    aggregate_principal_value_real_part=float(
                        base.finite_temperature_principal_value_real_part
                    ),
                    response_identity_residual=float(response_identity_residual),
                    kms_log_ratio_residual=float(base.kms_log_ratio_residual),
                    fdt_residual=float(base.fdt_residual),
                    pv_inner_convergence_residual=float(
                        base.scattering_pv_inner_convergence_residual
                    ),
                    pv_outer_convergence_residual=float(
                        base.scattering_pv_outer_convergence_residual
                    ),
                    response_identity_completed=bool(
                        response_identity_residual == 0.0
                        and _relabeling_to_reference(tuple(signs))
                        == _relabeling_to_reference(tuple(signs))
                    ),
                )
            )

    max_identity = max(point.response_identity_residual for point in points)
    max_kms = max(point.kms_log_ratio_residual for point in points)
    max_fdt = max(point.fdt_residual for point in points)
    max_inner = max(point.pv_inner_convergence_residual for point in points)
    max_outer = max(point.pv_outer_convergence_residual for point in points)
    maps_are_complete = tuple(
        point.relabeling_to_reference
        for point in points
        if point.invariant_s == grid[0]
    ) == ((2, 3, 1), (1, 3, 2), (1, 2, 3))
    all_completed = bool(
        tuple(SCATTERING_SIGN_PERMUTATIONS) == tuple(
            point.signs for point in points if point.invariant_s == grid[0]
        )
        and maps_are_complete
        and all(point.relabeling_jacobian_absolute == 1.0 for point in points)
        and all(point.response_identity_completed for point in points)
        and max_kms <= FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD
        and max_fdt <= FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD
        and max_inner <= FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD
        and max_outer <= FINITE_T_SCATTERING_CONVERGENCE_THRESHOLD
    )
    return All22PermutationIdentityState(
        temperature=temperature,
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        reference_signs=REFERENCE_SCATTERING_SIGNS,
        signs=tuple(SCATTERING_SIGN_PERMUTATIONS),
        invariant_grid=grid,
        points=tuple(points),
        permutation_count=len(SCATTERING_SIGN_PERMUTATIONS),
        single_cut_graph_weight=float(SUNSET_SYMMETRY_FACTOR),
        aggregate_graph_weight=float(SCATTERING_CHANNEL_SYMMETRY_FACTOR),
        max_response_identity_residual=float(max_identity),
        max_kms_log_ratio_residual=float(max_kms),
        max_fdt_residual=float(max_fdt),
        max_pv_inner_convergence_residual=float(max_inner),
        max_pv_outer_convergence_residual=float(max_outer),
        all_three_permutation_identity_completed=all_completed,
        action_level_multiplicity_contract_preserved=bool(
            SCATTERING_CHANNEL_SYMMETRY_FACTOR
            == len(SCATTERING_SIGN_PERMUTATIONS) * SUNSET_SYMMETRY_FACTOR
        ),
    )


def all_22_permutation_identity_contract() -> dict[str, Any]:
    """Return equations, units, provenance, and claim boundary."""

    return {
        "status": ALL_22_PERMUTATION_IDENTITY_STATUS,
        "equations": {
            "allowed_signed_cuts": "++-, +-+, -++",
            "process_form": "P+k_minus=k_plus,1+k_plus,2",
            "dummy_line_relabeling": "k_ref=(k_plus,1,k_plus,2,k_minus)",
            "relabeling_jacobian": "|det J|=1",
            "single_cut_graph_weight": "w_single=1/6",
            "aggregate_graph_weight": "w_22=3*(1/6)=1/2",
            "response_identity": "I_22^(++-)=I_22^(+-+)=I_22^(-++) for equal masses and common T,couplings",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature or metric",
            "R_gen": "derived physical/history trace; no independent state or backreaction",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "invariant_s_and_self_energy": "energy squared",
            "thermal_measures": "declared energy squared measure",
            "Phi": "effective response variable; dimensional SI map remains open",
        },
        "derivation_class": (
            "exact equal-mass dummy-line relabeling with unit Jacobian, combined "
            "with the action-level sunset symmetry factor"
        ),
        "observable": (
            "permutation inventory, relabeling maps, aggregate response identity, "
            "KMS/FDT, and PV convergence"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_ALL_22_PERMUTATION_IDENTITY_NO_HOLDOUT",
        "included": {
            "all_three_allowed_2_to_2_permutations": True,
            "equal_mass_relabeling_identity": True,
            "aggregate_graph_weight_contract": True,
            "state_matched_response_diagnostics": True,
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
            "This closes the equal-mass permutation identity and action-level "
            "coverage of the three allowed 2<->2 signed cuts. It does not by "
            "itself close the complete off-shell finite-temperature 1PI object, "
            "physical renormalization, transport, entropy, SI mapping, alpha_Phi_K, "
            "TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "ALL_22_PERMUTATION_IDENTITY_STATUS",
    "DEFAULT_ALL_22_PERMUTATION_GRID",
    "All22PermutationIdentityState",
    "TwoToTwoPermutationPoint",
    "all_22_permutation_identity_contract",
    "all_22_permutation_identity_state",
]
