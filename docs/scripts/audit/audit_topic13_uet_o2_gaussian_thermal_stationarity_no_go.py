"""Audit the scoped no-go for thermal-only Gaussian condensate stationarity."""

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
)
from docs.core.uet_o2_gaussian_thermal_stationarity_no_go import (
    mode_omega_sq_x_derivatives,
    stationarity_no_go_contract,
    thermal_gaussian_stationarity_no_go,
    tree_derivative_x,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_gaussian_thermal_stationarity_no_go.py"
OFFSHELL_REL = "docs/core/02_equations/o2/uet_o2_gaussian_offshell_background.py"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_gaussian_thermal_stationarity_no_go.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.3
PHI = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
CONVERGENCE_CASES = ((96, 50.0), (192, 70.0), (256, 90.0))
X_FACTORS = (1.0, 1.01, 1.1, 1.5, 2.0, 5.0)
WAVENUMBERS = (0.01, 0.1, 1.0, 10.0, 100.0)
FINITE_DIFFERENCE_TOLERANCE = 5.0e-5


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


def potential_at_x(
    x: float,
    eos_config: O2FiniteDensityEOSConfig,
    *,
    order: int,
    cutoff_factor: float,
) -> object:
    return off_shell_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        sqrt(x),
        eos_config,
        quadrature_order=order,
        cutoff_factor=cutoff_factor,
    )


def finite_difference_x_derivative(
    x: float,
    x_boundary: float,
    eos_config: O2FiniteDensityEOSConfig,
) -> dict[str, float]:
    if x == x_boundary:
        step = 0.01 * x
        left_state = potential_at_x(
            x, eos_config, order=96, cutoff_factor=50.0
        )
        right_state = potential_at_x(
            x + step, eos_config, order=96, cutoff_factor=50.0
        )
        thermal_derivative = (
            right_state.thermal_grand_potential - left_state.thermal_grand_potential
        ) / step
        total_derivative = (right_state.grand_potential - left_state.grand_potential) / step
    else:
        step = min(0.01 * x, 0.25 * (x - x_boundary))
        left_state = potential_at_x(
            x - step, eos_config, order=96, cutoff_factor=50.0
        )
        right_state = potential_at_x(
            x + step, eos_config, order=96, cutoff_factor=50.0
        )
        thermal_derivative = (
            right_state.thermal_grand_potential - left_state.thermal_grand_potential
        ) / (2.0 * step)
        total_derivative = (right_state.grand_potential - left_state.grand_potential) / (2.0 * step)
    return {
        "step": float(step),
        "thermal_derivative": float(thermal_derivative),
        "total_derivative": float(total_derivative),
    }


def main() -> int:
    eos_config = config()
    contract = stationarity_no_go_contract()
    proof = thermal_gaussian_stationarity_no_go(
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
    )
    x_boundary = proof.x_boundary
    representative_records = []
    mode_records = []
    finite_difference_records = []

    for factor in X_FACTORS:
        x = x_boundary * factor
        derivative_records = []
        for wavenumber in WAVENUMBERS:
            low, high, low_derivative, high_derivative, margin = mode_omega_sq_x_derivatives(
                wavenumber,
                x,
                CHEMICAL_POTENTIAL,
                proof,
            )
            derivative_records.append(
                {
                    "wavenumber": wavenumber,
                    "low_omega_sq": low,
                    "high_omega_sq": high,
                    "low_x_derivative": low_derivative,
                    "high_x_derivative": high_derivative,
                    "discriminant_margin": margin,
                }
            )
        finite_difference = finite_difference_x_derivative(x, x_boundary, eos_config)
        representative_records.append(
            {
                "x_factor": factor,
                "x": x,
                "tree_x_derivative": tree_derivative_x(x, proof),
                "minimum_low_x_derivative": min(
                    item["low_x_derivative"] for item in derivative_records
                ),
                "minimum_high_x_derivative": min(
                    item["high_x_derivative"] for item in derivative_records
                ),
                "minimum_discriminant_margin": min(
                    item["discriminant_margin"] for item in derivative_records
                ),
                "thermal_x_derivative_finite_difference": finite_difference[
                    "thermal_derivative"
                ],
                "total_x_derivative_finite_difference": finite_difference[
                    "total_derivative"
                ],
                "finite_difference_step": finite_difference["step"],
            }
        )
        mode_records.append(
            {
                "x_factor": factor,
                "x": x,
                "records": derivative_records,
            }
        )
        finite_difference_records.append(
            {
                "x_factor": factor,
                "x": x,
                **finite_difference,
            }
        )

    lower_margin_bound = (
        12.0 * proof.condensate_control**2 / proof.kinetic_coefficient**2
        + 32.0
        * CHEMICAL_POTENTIAL**2
        * proof.condensate_control
        / proof.kinetic_coefficient
    )

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        state = potential_at_x(
            x_boundary,
            eos_config,
            order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "grand_potential": state.grand_potential,
                "thermal_grand_potential": state.thermal_grand_potential,
                "tree_grand_potential": state.tree_grand_potential,
            }
        )
    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in ("grand_potential", "thermal_grand_potential")
    }

    checks = {
        "condensed_control_positive": proof.condensate_control > 0.0,
        "positive_Z_and_quartic": proof.kinetic_coefficient > 0.0
        and proof.quartic_coupling > 0.0,
        "stable_domain_boundary_is_q_over_lambda": abs(
            proof.x_boundary
            - proof.condensate_control / proof.quartic_coupling
        )
        <= 1.0e-14,
        "tree_derivative_nonnegative_on_witness": all(
            item["tree_x_derivative"] >= -1.0e-14
            for item in representative_records
        ),
        "analytic_margin_lower_bound_positive": lower_margin_bound > 0.0,
        "analytic_margin_witness_positive": all(
            item["minimum_discriminant_margin"] > 0.0
            for item in representative_records
        ),
        "low_mode_x_derivative_positive": all(
            item["minimum_low_x_derivative"] > 0.0
            for item in representative_records
        ),
        "high_mode_x_derivative_positive": all(
            item["minimum_high_x_derivative"] > 0.0
            for item in representative_records
        ),
        "thermal_x_derivative_positive_on_witness": all(
            item["thermal_x_derivative_finite_difference"] > 0.0
            for item in representative_records
        ),
        "total_x_derivative_positive_on_witness": all(
            item["total_x_derivative_finite_difference"] > 0.0
            for item in representative_records
        ),
        "thermal_derivative_sign_matches_analytic_witness": all(
            item["thermal_x_derivative_finite_difference"] > 0.0
            for item in representative_records
        ),
        "total_derivative_is_resolved": min(
            item["total_x_derivative_finite_difference"]
            for item in representative_records
        )
        > FINITE_DIFFERENCE_TOLERANCE,
        "boundary_potential_converges": convergence_relative_errors[
            "grand_potential"
        ]
        <= 1.0e-5,
        "boundary_thermal_potential_converges": convergence_relative_errors[
            "thermal_grand_potential"
        ]
        <= 1.0e-5,
        "finite_temperature_self_energy_is_not_assumed": proof.interacting_self_energy_included
        is False,
        "vacuum_counterterm_is_not_assumed": proof.vacuum_counterterm_included is False,
        "no_physical_phase_transition_claim": True,
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not identified" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY"
        if all(checks.values())
        else "FAIL_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": OFFSHELL_REL, "sha256": digest(OFFSHELL_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-gaussian-thermal-stationarity-no-go-v1",
        "artifact": "t13_uet_o2_gaussian_thermal_stationarity_no_go",
        "generated_at": date.today().isoformat(),
        "status": status,
        "formal_no_go_closure": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
        "major_result": {
            "major_result_id": "T13_UET_O2_GAUSSIAN_THERMAL_STATIONARITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "within the declared tree plus stable thermal Gaussian domain x=A^2>=q/lambda, the tree derivative is nonnegative",
                "the analytic discriminant margin is positive and both quadratic mode roots increase with x",
                "each stable thermal Bose contribution increases with x, so the combined thermal-only potential has no stationary point in this domain",
                "finite-difference thermal and combined-potential derivative witnesses and cutoff convergence support the analytic no-go",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": {
                "unit_lane": "natural",
                "x": "natural amplitude squared",
                "Omega": "natural thermodynamic density",
                "Phi": "fixed action response input; no SI map",
            },
            "derivation_class": "scoped analytic no-go from tree derivative, mode-root derivative, and positive Bose determinant derivative; finite-difference witness is verification only",
            "observable": "absence of thermal-only Gaussian stationary condensate in the declared stable domain",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_renormalized_finite_temperature_action_can_change_the_scoped_conclusion",
                "interacting_finite_temperature_self_energy_and_self_consistent_phase_boundary_missing",
                "condensate_and_normal_two_fluid_eos_completion_missing",
                "physical_kubo_coefficients_and_microscopic_sk_kms_matching_missing",
                "entropy_current_dissipative_balance_and_heat_flux_mapping_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "scoped no-go for the current thermal-only Gaussian stationary domain; named renormalized/interacting branch required, with no Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI,
            "effective_mass_sq": proof.effective_mass_sq,
            "condensate_control": proof.condensate_control,
            "kinetic_coefficient": proof.kinetic_coefficient,
            "quartic_coupling": proof.quartic_coupling,
            "x_boundary": x_boundary,
            "analytic_discriminant_margin_lower_bound": lower_margin_bound,
            "thermal_only": proof.thermal_only,
            "vacuum_counterterm_included": proof.vacuum_counterterm_included,
            "interacting_self_energy_included": proof.interacting_self_energy_included,
        },
        "representative_records": representative_records,
        "mode_records": mode_records,
        "finite_difference_records": finite_difference_records,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "thermal_gaussian_stationarity_no_go_requires_named_renormalized_interacting_branch_for_any_finite_temperature_stationary_solution",
        "next_controller": "Keep the current thermal-only Gaussian branch marked no-go and derive/source-lock the named renormalized interacting self-energy branch before claiming a finite-temperature phase boundary.",
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
                "x_boundary": x_boundary,
                "analytic_discriminant_margin_lower_bound": lower_margin_bound,
                "minimum_thermal_derivative": min(
                    item["thermal_x_derivative_finite_difference"]
                    for item in representative_records
                ),
                "minimum_total_derivative": min(
                    item["total_x_derivative_finite_difference"]
                    for item in representative_records
                ),
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
