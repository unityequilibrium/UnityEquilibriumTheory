"""Action-level multiplicity contract for the finite-temperature sunset cuts.

The finite-temperature sunset has one positive-energy ``1<->3`` sign pattern
and three relabelled ``2<->2`` patterns.  This module derives their graph
weights from the action sunset symmetry factor.  It keeps the species-resolved
identical-final-state convention of the physical scattering comparator
separate from the self-energy graph weight.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from docs.core.uet_o2_action_1pi_sunset_tensor import (
    SUNSET_SYMMETRY_FACTOR,
    expected_sunset_tensor_prefactor,
)
from docs.core.uet_o2_action_sunset_1pi_spectral import (
    action_sunset_spectral_contract,
)
from docs.core.uet_o2_finite_temperature_signed_cut_coverage import (
    SCATTERING_SIGN_PERMUTATIONS,
    finite_temperature_signed_cut_coverage_state,
)
from docs.core.uet_o2_finite_temperature_sunset_scattering_sk_kms import (
    SCATTERING_CHANNEL_SYMMETRY_FACTOR,
)


CUT_MULTIPLICITY_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE"
)
SCATTERING_SIGN_PERMUTATION_COUNT = len(SCATTERING_SIGN_PERMUTATIONS)


@dataclass(frozen=True)
class SunsetCutMultiplicityState:
    """Action-level weights and separate physical-final-state convention."""

    mass_squared: float
    quartic_coupling: float
    species_count: int
    one_to_three_sign_pattern_count: int
    two_to_two_sign_pattern_count: int
    sunset_symmetry_factor: float
    one_to_three_graph_weight: float
    two_to_two_graph_weight: float
    current_labeled_scattering_factor: float
    current_factor_matches_two_to_two_graph_weight: bool
    two_to_two_to_one_to_three_graph_weight_ratio: float
    action_sunset_tensor_prefactor: float
    one_to_three_tensor_weight: float
    two_to_two_tensor_weight: float
    physical_final_state_weight_formula_present: bool
    physical_final_state_weight_values: tuple[float, ...]
    physical_final_state_has_species_dependent_weights: bool
    action_level_signed_cut_multiplicity_completed: bool = True
    current_graph_weight_semantics_completed: bool = True
    physical_scattering_normalization_match_completed: bool = False
    full_finite_temperature_1pi_self_energy_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_FINITE_T_CUT_MULTIPLICITY_NO_HOLDOUT"


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _integer(value: int, name: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def finite_temperature_sunset_cut_multiplicity_state(
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
) -> SunsetCutMultiplicityState:
    """Derive the sign-pattern graph weights from the sunset symmetry factor."""

    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count")
    taxonomy = finite_temperature_signed_cut_coverage_state(
        external_energy=3.0,
        mass_squared=mass_squared,
    )
    one_to_three_count = taxonomy.one_to_three_allowed_assignment_count
    two_to_two_count = taxonomy.two_to_two_allowed_assignment_count
    one_to_three_weight = one_to_three_count * SUNSET_SYMMETRY_FACTOR
    two_to_two_weight = two_to_two_count * SUNSET_SYMMETRY_FACTOR
    tensor_prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    comparator_contract = action_sunset_spectral_contract()
    final_weight_formula = comparator_contract["equations"][
        "action_matrix_element_squared"
    ]
    final_state_weights = tuple(
        1.0 / (1.0 + float(first == second))
        for first in range(species_count)
        for second in range(species_count)
    )
    finite_values = (
        mass_squared,
        quartic,
        one_to_three_weight,
        two_to_two_weight,
        SCATTERING_CHANNEL_SYMMETRY_FACTOR,
        tensor_prefactor,
        *final_state_weights,
    )
    if not all(isfinite(float(value)) for value in finite_values):
        raise FloatingPointError("sunset cut multiplicity state is not finite")
    return SunsetCutMultiplicityState(
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        one_to_three_sign_pattern_count=one_to_three_count,
        two_to_two_sign_pattern_count=two_to_two_count,
        sunset_symmetry_factor=float(SUNSET_SYMMETRY_FACTOR),
        one_to_three_graph_weight=float(one_to_three_weight),
        two_to_two_graph_weight=float(two_to_two_weight),
        current_labeled_scattering_factor=float(
            SCATTERING_CHANNEL_SYMMETRY_FACTOR
        ),
        current_factor_matches_two_to_two_graph_weight=(
            _relative(
                SCATTERING_CHANNEL_SYMMETRY_FACTOR,
                two_to_two_weight,
            )
            <= 1.0e-15
        ),
        two_to_two_to_one_to_three_graph_weight_ratio=float(
            two_to_two_weight / one_to_three_weight
        ),
        action_sunset_tensor_prefactor=float(tensor_prefactor),
        one_to_three_tensor_weight=float(tensor_prefactor * one_to_three_weight),
        two_to_two_tensor_weight=float(tensor_prefactor * two_to_two_weight),
        physical_final_state_weight_formula_present=(
            "/(1+delta_cd)" in final_weight_formula
        ),
        physical_final_state_weight_values=final_state_weights,
        physical_final_state_has_species_dependent_weights=(
            len(set(final_state_weights)) > 1
        ),
    )


def finite_temperature_sunset_cut_multiplicity_contract() -> dict[str, Any]:
    """Return equations and the separation between graph and scattering weights."""

    return {
        "status": CUT_MULTIPLICITY_STATUS,
        "equations": {
            "sunset_graph_symmetry": "S_sunset=1/6",
            "positive_energy_sign_counts": "N_13=1, N_22=3",
            "one_to_three_graph_weight": "w_13=N_13*S_sunset=1/6",
            "two_to_two_graph_weight": "w_22=N_22*S_sunset=3/6=1/2",
            "representative_mapping": (
                "I_22^all=w_22*I_22^(++-) for equal-mass relabelled phase space"
            ),
            "physical_final_state_convention": (
                "w_final(c,d)=1/(1+delta_cd), kept in the action scattering "
                "comparator and not identified with the graph weight"
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
            "quartic_coupling": "dimensionless",
            "graph_weights": "dimensionless",
            "sunset_tensor_prefactor": "energy squared per loop integral",
        },
        "derivation_class": (
            "action-derived sunset graph symmetry and signed-cut permutation count; "
            "species-resolved physical final-state convention kept separate"
        ),
        "observable": (
            "sign-pattern counts, graph weights, representative-channel mapping, "
            "and explicit physical final-state symmetry convention"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_CUT_MULTIPLICITY_NO_HOLDOUT",
        "included": {
            "action_level_1_over_6_symmetry_factor": True,
            "three_two_to_two_sign_permutations": True,
            "two_to_two_graph_weight_three_sixths": True,
            "current_representative_factor_match": True,
            "species_resolved_final_state_factor_separation": True,
        },
        "excluded": {
            "physical_scattering_normalization_identity": True,
            "complete_finite_temperature_1pi_self_energy": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes the action-level graph multiplicity for the three equal-mass "
            "2<->2 signed cuts and shows that the current representative factor 1/2 "
            "matches 3*(1/6) in the declared loop convention. It keeps the physical "
            "species-resolved final-state factor separate and does not claim an identity "
            "between the self-energy cut and a transport scattering coefficient. It does "
            "not close the complete finite-temperature 1PI self-energy, physical "
            "renormalization, transport, entropy, SI mapping, alpha_Phi_K, TTG, or Full Topic 13."
        ),
    }


__all__ = [
    "CUT_MULTIPLICITY_STATUS",
    "SCATTERING_SIGN_PERMUTATION_COUNT",
    "SunsetCutMultiplicityState",
    "finite_temperature_sunset_cut_multiplicity_contract",
    "finite_temperature_sunset_cut_multiplicity_state",
]
