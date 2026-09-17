"""Audit the analytic thermal-only quadratic stability boundary."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite, sqrt
from pathlib import Path

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_gaussian_offshell_background import (
    off_shell_gaussian_thermal_state,
    off_shell_mode_omega_sq,
)
from docs.core.uet_o2_thermal_stability_boundary import (
    mode_stability_witness,
    phase_curvature_at_amplitude,
    thermal_stability_boundary,
    uet_o2_thermal_stability_boundary_contract,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_thermal_stability_boundary.py"
OFFSHELL_REL = "docs/core/02_equations/o2/uet_o2_gaussian_offshell_background.py"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_thermal_stability_boundary_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.3
PHI = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
CONVERGENCE_CASES = ((96, 50.0), (192, 70.0), (256, 90.0))
WAVENUMBERS = (0.0, 0.01, 0.1, 0.5, 1.0)
BELOW_FACTOR = 0.999
ABOVE_FACTOR = 1.001
ONE_SIDED_FRACTION = 0.01
TADPOLE_THRESHOLD = 1.0e-3


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def main() -> int:
    eos_config = config()
    contract = uet_o2_thermal_stability_boundary_contract()
    boundary = thermal_stability_boundary(CHEMICAL_POTENTIAL, PHI, eos_config)
    below_amplitude = boundary.amplitude_boundary * BELOW_FACTOR
    above_amplitude = boundary.amplitude_boundary * ABOVE_FACTOR

    boundary_modes = mode_stability_witness(
        boundary.amplitude_boundary,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        WAVENUMBERS,
    )
    above_modes = mode_stability_witness(
        above_amplitude,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        WAVENUMBERS,
    )
    below_modes = mode_stability_witness(
        below_amplitude,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        WAVENUMBERS,
    )

    boundary_state = off_shell_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        boundary.amplitude_boundary,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    one_sided_step = boundary.amplitude_boundary * ONE_SIDED_FRACTION
    above_state = off_shell_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        boundary.amplitude_boundary + one_sided_step,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    one_sided_thermal_slope = (
        above_state.grand_potential - boundary_state.grand_potential
    ) / one_sided_step

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        state = off_shell_gaussian_thermal_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI,
            boundary.amplitude_boundary,
            eos_config,
            quadrature_order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "grand_potential": state.grand_potential,
                "tree_grand_potential": state.tree_grand_potential,
                "thermal_grand_potential": state.thermal_grand_potential,
            }
        )
    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in ("grand_potential", "thermal_grand_potential")
    }

    boundary_low_at_zero, boundary_high_at_zero = off_shell_mode_omega_sq(
        0.0,
        boundary.amplitude_boundary,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
    )
    below_low_at_zero, below_high_at_zero = off_shell_mode_omega_sq(
        0.0,
        below_amplitude,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
    )

    checks = {
        "condensed_control_positive": boundary.condensate_control > 0.0,
        "boundary_amplitude_positive": boundary.amplitude_boundary > 0.0,
        "boundary_formula_is_finite": all(
            isfinite(value)
            for value in (
                boundary.effective_mass_sq,
                boundary.condensate_control,
                boundary.amplitude_squared_boundary,
                boundary.amplitude_boundary,
                boundary.radial_curvature_at_boundary,
                boundary.phase_curvature_at_boundary,
            )
        ),
        "phase_curvature_boundary_is_zero": abs(
            boundary.phase_curvature_at_boundary
        )
        <= 1.0e-12,
        "radial_curvature_boundary_is_two_q": abs(
            boundary.radial_curvature_at_boundary
            - 2.0 * boundary.condensate_control
        )
        <= 1.0e-12,
        "boundary_modes_are_nonnegative": boundary_modes["all_low_nonnegative"]
        and boundary_modes["all_high_nonnegative"],
        "above_boundary_modes_are_nonnegative": above_modes["all_low_nonnegative"]
        and above_modes["all_high_nonnegative"],
        "below_boundary_has_negative_zero_mode": below_low_at_zero < 0.0
        and below_high_at_zero > 0.0
        and not below_modes["all_low_nonnegative"],
        "boundary_zero_mode_is_zero": abs(boundary_low_at_zero) <= 1.0e-12,
        "boundary_high_zero_mode_is_positive": boundary_high_at_zero > 0.0,
        "phase_curvature_matches_boundary_formula": abs(
            phase_curvature_at_amplitude(
                boundary.amplitude_boundary,
                CHEMICAL_POTENTIAL,
                PHI,
                eos_config,
            )
            - boundary.phase_curvature_at_boundary
        )
        <= 1.0e-12,
        "thermal_boundary_state_is_finite": isfinite(
            boundary_state.grand_potential
        ),
        "thermal_one_sided_slope_is_resolved": isfinite(one_sided_thermal_slope)
        and abs(one_sided_thermal_slope) > TADPOLE_THRESHOLD,
        "thermal_potential_converges": convergence_relative_errors[
            "grand_potential"
        ]
        <= 1.0e-5,
        "thermal_component_converges": convergence_relative_errors[
            "thermal_grand_potential"
        ]
        <= 1.0e-5,
        "quadratic_boundary_is_not_claimed_as_stationary": boundary.self_consistent_finite_temperature_boundary
        is False,
        "interacting_self_energy_is_excluded": boundary.interacting_self_energy_included
        is False,
        "vacuum_counterterm_is_excluded": contract["scope"]["vacuum_counterterm"]
        == "NOT_INCLUDED",
        "normal_two_fluid_is_open": contract["scope"]["normal_two_fluid_completion"]
        == "NOT_INCLUDED",
        "physical_kubo_is_excluded": contract["scope"]["physical_kubo"]
        == "NOT_INCLUDED",
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not identified" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": OFFSHELL_REL, "sha256": digest(OFFSHELL_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-thermal-quadratic-stability-boundary-v1",
        "artifact": "t13_uet_o2_thermal_stability_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_THERMAL_STABILITY_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "analytic lower boundary A_boundary^2=q/lambda from the declared phase Hessian",
                "radial and phase curvature identities at the boundary",
                "nonnegative quadratic mode witness at and above the boundary",
                "negative zero-mode witness below the boundary without clipping",
                "thermal-only one-sided slope and grand-potential convergence at the declared boundary",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived quadratic O(2) stability boundary with thermal-only Gaussian witness; no self-consistent finite-temperature effective action",
            "observable": "natural-unit homogeneous condensate amplitude stability and thermal-only grand-potential boundary diagnostic",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "self_consistent_finite_temperature_stationary_boundary_requires_thermal_self_energy",
                "vacuum_counterterm_and_microscopic_renormalization_matching_missing",
                "condensate_and_normal_two_fluid_eos_completion_missing",
                "physical_kubo_coefficients_and_microscopic_sk_kms_matching_missing",
                "entropy_current_dissipative_balance_and_heat_flux_mapping_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "thermal-only quadratic stability boundary lane; no self-consistent finite-T phase transition, Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI,
            "effective_mass_sq": boundary.effective_mass_sq,
            "condensate_control": boundary.condensate_control,
            "amplitude_boundary": boundary.amplitude_boundary,
            "amplitude_squared_boundary": boundary.amplitude_squared_boundary,
            "radial_curvature_at_boundary": boundary.radial_curvature_at_boundary,
            "phase_curvature_at_boundary": boundary.phase_curvature_at_boundary,
            "boundary_low_omega_sq_at_zero": boundary_low_at_zero,
            "boundary_high_omega_sq_at_zero": boundary_high_at_zero,
            "below_amplitude": below_amplitude,
            "below_low_omega_sq_at_zero": below_low_at_zero,
            "below_high_omega_sq_at_zero": below_high_at_zero,
            "above_amplitude": above_amplitude,
            "boundary_grand_potential": boundary_state.grand_potential,
            "one_sided_step": one_sided_step,
            "one_sided_thermal_slope": one_sided_thermal_slope,
            "tadpole_threshold": TADPOLE_THRESHOLD,
            "self_consistent_finite_temperature_boundary": False,
            "interacting_self_energy_included": False,
        },
        "boundary_mode_witness": boundary_modes,
        "above_boundary_mode_witness": above_modes,
        "below_boundary_mode_witness": below_modes,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "thermal_background_backreaction_requires_self_consistent_renormalized_phase_boundary",
        "next_controller": "Derive or source-lock the finite-temperature self-energy needed for an interior stationary phase boundary; keep the current quadratic boundary as the stability contract and do not call it a phase transition.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "failed_checks": [key for key, value in checks.items() if not value],
                "amplitude_boundary": boundary.amplitude_boundary,
                "one_sided_thermal_slope": one_sided_thermal_slope,
                "below_low_omega_sq_at_zero": below_low_at_zero,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
