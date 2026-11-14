"""Kinematic taxonomy for the finite-temperature O(2) sunset cuts.

This lane audits the signs of the three cut internal energies for a positive
external energy in the equal-mass external rest frame.  It deliberately stops
before assigning a complete action-level cut multiplicity or a physical 1PI
renormalization scheme.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any


SIGNED_CUT_COVERAGE_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE"
)
SIGNED_CUT_MASS_THRESHOLD = 3.0
POSITIVE_EXTERNAL_SIGN_ASSIGNMENTS: tuple[tuple[int, int, int], ...] = (
    (-1, -1, -1),
    (-1, -1, 1),
    (-1, 1, -1),
    (-1, 1, 1),
    (1, -1, -1),
    (1, -1, 1),
    (1, 1, -1),
    (1, 1, 1),
)
CURRENT_LABELED_SCATTERING_SIGNS = (1, 1, -1)
SCATTERING_SIGN_PERMUTATIONS = ((-1, 1, 1), (1, -1, 1), (1, 1, -1))


@dataclass(frozen=True)
class SignedCutClassification:
    """One internal-energy sign assignment at positive external energy."""

    signs: tuple[int, int, int]
    sign_label: str
    process_class: str
    kinematically_allowed: bool
    energy_relation: str
    kinematic_reason: str
    lower_bound_energy: float


@dataclass(frozen=True)
class SignedCutCoverageState:
    """Machine-readable state for the positive-energy cut taxonomy."""

    external_energy: float
    mass: float
    mass_squared: float
    assignments: tuple[SignedCutClassification, ...]
    allowed_signs: tuple[tuple[int, int, int], ...]
    allowed_assignment_count: int
    one_to_three_allowed_assignment_count: int
    two_to_two_allowed_assignment_count: int
    current_labeled_scattering_signs: tuple[int, int, int]
    current_labeled_scattering_assignment_count: int
    missing_scattering_permutation_count: int
    forbidden_one_plus_two_minus_count: int
    all_sign_assignments_enumerated: bool
    one_to_three_threshold_checked: bool
    two_to_two_permutations_enumerated: bool
    equal_mass_permutation_identity_declared: bool
    signed_cut_kinematic_taxonomy_completed: bool = True
    action_level_cut_multiplicity_completed: bool = False
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
        "ACTION_DERIVED_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_NO_HOLDOUT"
    )


def _finite_positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _validate_signs(signs: tuple[int, int, int]) -> tuple[int, int, int]:
    result = tuple(int(value) for value in signs)
    if len(result) != 3 or any(value not in {-1, 1} for value in result):
        raise ValueError("signs must contain exactly three values from {-1, 1}")
    return result  # type: ignore[return-value]


def _label(signs: tuple[int, int, int]) -> str:
    return "".join("+" if value == 1 else "-" for value in signs)


def classify_signed_cut(
    signs: tuple[int, int, int],
    external_energy: float,
    mass: float,
) -> SignedCutClassification:
    """Classify one sign assignment using future-timelike kinematics.

    The external four-momentum is ``P=(external_energy, 0)`` and all internal
    lines have mass ``mass``.  A two-plus/one-minus assignment is open because
    an arbitrarily energetic bath line can make ``(P+k)^2`` exceed the two-body
    threshold.  A one-plus/two-minus assignment is forbidden because it would
    require the sum of three future-timelike momenta to equal one mass-shell
    momentum.
    """

    signs = _validate_signs(signs)
    external_energy = _finite_positive(external_energy, "external_energy")
    mass = _finite_positive(mass, "mass")
    plus_count = sum(value == 1 for value in signs)
    sign_label = _label(signs)
    if plus_count == 3:
        allowed = external_energy >= 3.0 * mass
        return SignedCutClassification(
            signs=signs,
            sign_label=sign_label,
            process_class="1<->3",
            kinematically_allowed=allowed,
            energy_relation="P=k1+k2+k3",
            kinematic_reason="three-body threshold sqrt(s)>=3m",
            lower_bound_energy=3.0 * mass,
        )
    if plus_count == 2:
        return SignedCutClassification(
            signs=signs,
            sign_label=sign_label,
            process_class="2<->2",
            kinematically_allowed=True,
            energy_relation="P+k_minus=k_plus,1+k_plus,2",
            kinematic_reason=(
                "the bath momentum is unbounded and can open the two-body "
                "final-state threshold"
            ),
            lower_bound_energy=0.0,
        )
    if plus_count == 1:
        return SignedCutClassification(
            signs=signs,
            sign_label=sign_label,
            process_class="3<->1_forbidden_for_positive_P0",
            kinematically_allowed=False,
            energy_relation="P+k_minus,1+k_minus,2=k_plus",
            kinematic_reason=(
                "a sum of P and two future-timelike mass-m momenta has mass "
                "at least sqrt(s)+2m>m"
            ),
            lower_bound_energy=external_energy + 2.0 * mass,
        )
    return SignedCutClassification(
        signs=signs,
        sign_label=sign_label,
        process_class="all_negative_forbidden_for_positive_P0",
        kinematically_allowed=False,
        energy_relation="P0=-(E1+E2+E3)",
        kinematic_reason="the right-hand side is strictly negative",
        lower_bound_energy=0.0,
    )


def finite_temperature_signed_cut_coverage_state(
    external_energy: float,
    mass_squared: float,
) -> SignedCutCoverageState:
    """Enumerate all positive-energy sign assignments for equal masses."""

    external_energy = _finite_positive(external_energy, "external_energy")
    mass_squared = _finite_positive(mass_squared, "mass_squared")
    mass = sqrt(mass_squared)
    assignments = tuple(
        classify_signed_cut(signs, external_energy, mass)
        for signs in POSITIVE_EXTERNAL_SIGN_ASSIGNMENTS
    )
    allowed = tuple(
        assignment.signs
        for assignment in assignments
        if assignment.kinematically_allowed
    )
    one_to_three = tuple(
        assignment
        for assignment in assignments
        if assignment.process_class == "1<->3"
    )
    two_to_two = tuple(
        assignment
        for assignment in assignments
        if assignment.process_class == "2<->2"
    )
    current = _validate_signs(CURRENT_LABELED_SCATTERING_SIGNS)
    current_count = int(current in tuple(assignment.signs for assignment in two_to_two))
    missing_permutations = len(
        tuple(signs for signs in SCATTERING_SIGN_PERMUTATIONS if signs != current)
    )
    forbidden_one_plus_two_minus_count = sum(
        assignment.process_class == "3<->1_forbidden_for_positive_P0"
        for assignment in assignments
    )
    all_enumerated = len(assignments) == len(POSITIVE_EXTERNAL_SIGN_ASSIGNMENTS)
    threshold_checked = bool(
        one_to_three
        and one_to_three[0].lower_bound_energy == 3.0 * mass
        and one_to_three[0].kinematically_allowed
        == (external_energy >= 3.0 * mass)
    )
    permutations_enumerated = tuple(
        assignment.signs for assignment in two_to_two
    ) == SCATTERING_SIGN_PERMUTATIONS
    return SignedCutCoverageState(
        external_energy=external_energy,
        mass=mass,
        mass_squared=mass_squared,
        assignments=assignments,
        allowed_signs=allowed,
        allowed_assignment_count=len(allowed),
        one_to_three_allowed_assignment_count=sum(
            assignment.kinematically_allowed for assignment in one_to_three
        ),
        two_to_two_allowed_assignment_count=sum(
            assignment.kinematically_allowed for assignment in two_to_two
        ),
        current_labeled_scattering_signs=current,
        current_labeled_scattering_assignment_count=current_count,
        missing_scattering_permutation_count=missing_permutations,
        forbidden_one_plus_two_minus_count=forbidden_one_plus_two_minus_count,
        all_sign_assignments_enumerated=all_enumerated,
        one_to_three_threshold_checked=threshold_checked,
        two_to_two_permutations_enumerated=permutations_enumerated,
        equal_mass_permutation_identity_declared=True,
        signed_cut_kinematic_taxonomy_completed=bool(
            all_enumerated
            and threshold_checked
            and permutations_enumerated
            and len(allowed) == 4
            and sum(assignment.process_class == "3<->1_forbidden_for_positive_P0" for assignment in assignments)
            == 3
        ),
    )


def finite_temperature_signed_cut_coverage_contract() -> dict[str, Any]:
    """Return equations and the deliberately narrow closure boundary."""

    return {
        "status": SIGNED_CUT_COVERAGE_STATUS,
        "equations": {
            "signed_cut_energy": "P0=sigma_1*E1+sigma_2*E2+sigma_3*E3, sigma_i in {+1,-1}",
            "positive_external_assignments": "{---,--+,-+-, -++, +--,+-+ ,++-,+++}",
            "one_to_three": "+++ : P=k1+k2+k3, sqrt(s)>=3m",
            "two_to_two_permutations": (
                "++-, +-+, -++ : P+k_minus=k_plus,1+k_plus,2"
            ),
            "forbidden_one_plus_two_minus": (
                "+--, -+-, --+ : P+k_minus,1+k_minus,2=k_plus is impossible "
                "for future-timelike equal-mass lines"
            ),
            "labeled_scattering_coverage": (
                "current module evaluates only ++-; equal-mass relabeling gives "
                "three kinematic patterns, so action-level multiplicity remains open"
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
            "external_energy_and_mass": "energy",
            "mass_squared": "energy squared",
            "signed_cut_relation": "energy",
        },
        "derivation_class": (
            "action-compatible future-timelike kinematic classification of all "
            "three-line signed cuts; no fitted coefficient or external data"
        ),
        "observable": (
            "complete positive-energy sign-assignment inventory, allowed process "
            "classes, threshold witness, and labeled 2<->2 permutation gap"
        ),
        "data_role": (
            "ACTION_DERIVED_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_NO_HOLDOUT"
        ),
        "included": {
            "all_eight_positive_external_sign_assignments": True,
            "one_to_three_threshold": True,
            "three_two_to_two_permutations": True,
            "forbidden_one_plus_two_minus_kinematics": True,
            "labeled_scattering_gap": True,
        },
        "excluded": {
            "action_level_cut_multiplicity": True,
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
            "This closes the positive-energy equal-mass signed-cut kinematic "
            "taxonomy and identifies that the current labeled 2<->2 module covers "
            "one of three allowed permutations. It does not close the action-level "
            "cut multiplicity, complete finite-temperature 1PI self-energy, physical "
            "renormalization, transport, entropy, SI mapping, alpha_Phi_K, TTG "
            "validation, or Full Topic 13."
        ),
    }


__all__ = [
    "CURRENT_LABELED_SCATTERING_SIGNS",
    "POSITIVE_EXTERNAL_SIGN_ASSIGNMENTS",
    "SCATTERING_SIGN_PERMUTATIONS",
    "SIGNED_CUT_COVERAGE_STATUS",
    "SignedCutClassification",
    "SignedCutCoverageState",
    "classify_signed_cut",
    "finite_temperature_signed_cut_coverage_contract",
    "finite_temperature_signed_cut_coverage_state",
]
