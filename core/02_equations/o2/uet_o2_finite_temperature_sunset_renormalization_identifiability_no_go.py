"""Show the scoped renormalization non-identifiability of the thermal sunset.

The declared pole-subtracted thermal cut preserves spectral/KMS/FDT data when
the subtraction reference changes, while its real principal-value response
changes.  This closes the current identifiability question as a no-go.  It
does not select a physical renormalization scheme.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from docs.core.uet_o2_finite_temperature_sunset_scattering_sk_kms import (
    finite_temperature_scattering_sunset_sk_kms_state,
)
from docs.core.uet_o2_finite_temperature_sunset_sk_kms import (
    finite_temperature_sunset_sk_kms_state,
)


RENORMALIZATION_IDENTIFIABILITY_NO_GO_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO"
)
RENORMALIZATION_SCHEME_DEPENDENCE_THRESHOLD = 1.0e-2
CUT_INVARIANCE_THRESHOLD = 1.0e-10
REFERENCE_POINTS = (0.25, 0.5, 0.8)


@dataclass(frozen=True)
class SunsetRenormalizationIdentifiabilityNoGoState:
    """Reference-dependence witness for the declared thermal sunset PV."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    invariant_s: float
    reference_euclidean_s_points: tuple[float, ...]
    combined_principal_value_real_parts: tuple[float, ...]
    combined_spectral_measures: tuple[float, ...]
    combined_kms_residuals: tuple[float, ...]
    combined_fdt_residuals: tuple[float, ...]
    principal_value_span: float
    principal_value_relative_span: float
    spectral_invariance_residual: float
    kms_invariance_residual: float
    fdt_invariance_residual: float
    reference_dependence_witness: bool
    cut_invariance_witness: bool
    renormalization_identifiability_no_go_completed: bool
    physical_renormalization_scheme_match_completed: bool = False
    full_finite_temperature_1pi_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_RENORMALIZATION_IDENTIFIABILITY_NO_GO_NO_HOLDOUT"
    )


def _relative(value: float, reference: float) -> float:
    return abs(float(value) - float(reference)) / max(abs(float(reference)), 1.0e-300)


def _state_for_reference(
    reference_euclidean_s: float,
    temperature: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    invariant_s: float,
) -> tuple[float, float, float, float]:
    one_to_three = finite_temperature_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        reference_euclidean_s=reference_euclidean_s,
        outer_order=32,
        refined_outer_order=48,
        inner_order=32,
        refined_inner_order=40,
        dispersion_order=32,
        refined_dispersion_order=48,
        dispersion_phase_outer_order=16,
        dispersion_phase_inner_order=16,
    )
    two_to_two = finite_temperature_scattering_sunset_sk_kms_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        invariant_s=invariant_s,
        reference_euclidean_s=reference_euclidean_s,
        outer_order=16,
        refined_outer_order=32,
        inner_order=16,
        refined_inner_order=24,
        dispersion_order=16,
        refined_dispersion_order=32,
        dispersion_phase_outer_order=16,
        dispersion_phase_inner_order=16,
    )
    return (
        float(
            one_to_three.finite_temperature_principal_value_real_part
            + two_to_two.finite_temperature_principal_value_real_part
        ),
        float(one_to_three.thermal_spectral_measure + two_to_two.thermal_spectral_measure),
        float(max(one_to_three.kms_log_ratio_residual, two_to_two.kms_log_ratio_residual)),
        float(max(one_to_three.fdt_residual, two_to_two.fdt_residual)),
    )


def sunset_renormalization_identifiability_no_go_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    invariant_s: float = 5.0,
    reference_euclidean_s_points: tuple[float, ...] = REFERENCE_POINTS,
) -> SunsetRenormalizationIdentifiabilityNoGoState:
    """Evaluate reference changes without fitting or changing the cut."""

    points = tuple(float(value) for value in reference_euclidean_s_points)
    if len(points) < 2 or tuple(sorted(points)) != points or any(value <= 0.0 for value in points):
        raise ValueError("reference points must be sorted, positive, and contain at least two values")
    results = tuple(
        _state_for_reference(
            point,
            temperature,
            mass_squared,
            quartic,
            species_count,
            invariant_s,
        )
        for point in points
    )
    pv_values = tuple(result[0] for result in results)
    spectral_values = tuple(result[1] for result in results)
    kms_values = tuple(result[2] for result in results)
    fdt_values = tuple(result[3] for result in results)
    pv_span = max(pv_values) - min(pv_values)
    pv_relative_span = pv_span / max(abs(pv_values[len(pv_values) // 2]), 1.0e-300)
    spectral_invariance = max(
        _relative(value, spectral_values[0]) for value in spectral_values[1:]
    )
    kms_invariance = max(kms_values)
    fdt_invariance = max(fdt_values)
    reference_dependence = pv_relative_span >= RENORMALIZATION_SCHEME_DEPENDENCE_THRESHOLD
    cut_invariance = (
        spectral_invariance <= CUT_INVARIANCE_THRESHOLD
        and kms_invariance <= CUT_INVARIANCE_THRESHOLD
        and fdt_invariance <= CUT_INVARIANCE_THRESHOLD
    )
    finite_values = pv_values + spectral_values + kms_values + fdt_values + (
        pv_span,
        pv_relative_span,
        spectral_invariance,
        kms_invariance,
        fdt_invariance,
    )
    if not all(isfinite(float(value)) for value in finite_values):
        raise FloatingPointError("renormalization identifiability state is not finite")
    return SunsetRenormalizationIdentifiabilityNoGoState(
        temperature=float(temperature),
        mass_squared=float(mass_squared),
        quartic_coupling=float(quartic),
        species_count=int(species_count),
        invariant_s=float(invariant_s),
        reference_euclidean_s_points=points,
        combined_principal_value_real_parts=pv_values,
        combined_spectral_measures=spectral_values,
        combined_kms_residuals=kms_values,
        combined_fdt_residuals=fdt_values,
        principal_value_span=float(pv_span),
        principal_value_relative_span=float(pv_relative_span),
        spectral_invariance_residual=float(spectral_invariance),
        kms_invariance_residual=float(kms_invariance),
        fdt_invariance_residual=float(fdt_invariance),
        reference_dependence_witness=reference_dependence,
        cut_invariance_witness=cut_invariance,
        renormalization_identifiability_no_go_completed=bool(
            reference_dependence and cut_invariance
        ),
    )


def sunset_renormalization_identifiability_no_go_contract() -> dict[str, Any]:
    """Return the no-go equations and the remaining physical boundary."""

    return {
        "status": RENORMALIZATION_IDENTIFIABILITY_NO_GO_STATUS,
        "equations": {
            "subtracted_real_part": "Re Sigma_R,T^sub(s;r)=PV integral rho_T(S) K_sub(S;r,s)dS",
            "reference_change": "Delta_r1_r2(s)=Re Sigma_R,T^sub(s;r1)-Re Sigma_R,T^sub(s;r2) != 0",
            "cut_invariance": "rho_T(s), KMS, and FDT are independent of the real-part subtraction reference",
            "identifiability_conclusion": "cut plus current natural-unit contract does not select a unique physical r",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_spectral_measure": "energy squared",
            "retarded_self_energy": "energy squared; identifiability no-go only",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-temperature 1<->3 and labeled 2<->2 cut composition "
            "evaluated under multiple declared subtraction references"
        ),
        "observable": (
            "reference-dependent summed PV real part versus reference-invariant spectral, "
            "KMS, and FDT quantities"
        ),
        "data_role": "ACTION_DERIVED_FINITE_T_RENORMALIZATION_IDENTIFIABILITY_NO_GO_NO_HOLDOUT",
        "included": {
            "reference_dependence_witness": True,
            "cut_invariance_witness": True,
            "scoped_physical_scheme_identifiability_no_go": True,
        },
        "excluded": {
            "physical_renormalization_scheme_selection": True,
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes the scoped identifiability no-go: the current action-derived cut and "
            "natural-unit subtraction contract leave the PV real part reference dependent while "
            "leaving cut/KMS/FDT observables invariant. It does not select a physical renormalization "
            "condition, close the complete 1PI object, derive transport or entropy, map Phi to SI, "
            "calibrate alpha_Phi_K, validate TTG, or close Full Topic 13."
        ),
    }


__all__ = [
    "CUT_INVARIANCE_THRESHOLD",
    "REFERENCE_POINTS",
    "RENORMALIZATION_IDENTIFIABILITY_NO_GO_STATUS",
    "RENORMALIZATION_SCHEME_DEPENDENCE_THRESHOLD",
    "SunsetRenormalizationIdentifiabilityNoGoState",
    "sunset_renormalization_identifiability_no_go_contract",
    "sunset_renormalization_identifiability_no_go_state",
]
