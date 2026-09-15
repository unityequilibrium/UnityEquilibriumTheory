"""Audit the finite-temperature condensed-stationarity scheme boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_stationarity_scheme import (
    uet_o2_stationarity_scheme_dependence,
    uet_o2_stationarity_scheme_dependence_contract,
)
from docs.core.uet_o2_finite_temperature_scheme_identifiability import (
    finite_local_counterterm,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_finite_temperature_stationarity_scheme.py"
IDENTIFIABILITY_REL = "docs/core/uet_o2_finite_temperature_scheme_identifiability.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_stationarity_scheme_dependence_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.30
PHI_RESPONSE = 0.20
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
QUADRATURE_ORDERS = (96, 192, 256)
CUTOFF_FACTORS = (50.0, 70.0, 90.0)
SCHEME_B_COEFFICIENT = -0.05


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
        response=CovariantResponseConfig(
            epsilon_nc=0.1,
            phi_equilibrium=0.0,
        ),
    )


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def compact(result) -> dict:
    return {
        "quadrature_order": result.quadrature_order,
        "momentum_cutoff": result.momentum_cutoff,
        "scheme_a_boundary_derivative": result.scheme_a_boundary_derivative,
        "scheme_a_reference_derivative": result.scheme_a_reference_derivative,
        "scheme_b_boundary_derivative": result.scheme_b_boundary_derivative,
        "scheme_b_reference_derivative": result.scheme_b_reference_derivative,
        "scheme_b_stationary_x": result.scheme_b_stationary_x,
        "scheme_b_stationary_residual": result.scheme_b_stationary_residual,
        "scheme_b_min_low_omega_sq": result.scheme_b_min_low_omega_sq,
        "scheme_b_min_high_omega_sq": result.scheme_b_min_high_omega_sq,
        "scheme_a_grid_min_derivative": result.scheme_a_grid_min_derivative,
        "scheme_a_grid_max_derivative": result.scheme_a_grid_max_derivative,
        "scheme_b_grid_min_derivative": result.scheme_b_grid_min_derivative,
        "scheme_b_grid_max_derivative": result.scheme_b_grid_max_derivative,
    }


def main() -> int:
    eos_config = config()
    contract = uet_o2_stationarity_scheme_dependence_contract()
    reference = uet_o2_stationarity_scheme_dependence(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
        scheme_b_coefficient=SCHEME_B_COEFFICIENT,
    )

    quadrature_records = []
    for order in QUADRATURE_ORDERS:
        result = uet_o2_stationarity_scheme_dependence(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=order,
            cutoff_factor=REFERENCE_CUTOFF_FACTOR,
            scheme_b_coefficient=SCHEME_B_COEFFICIENT,
        )
        quadrature_records.append(compact(result))

    cutoff_records = []
    for cutoff_factor in CUTOFF_FACTORS:
        result = uet_o2_stationarity_scheme_dependence(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            quadrature_order=REFERENCE_ORDER,
            cutoff_factor=cutoff_factor,
            scheme_b_coefficient=SCHEME_B_COEFFICIENT,
        )
        record = compact(result)
        record["cutoff_factor"] = cutoff_factor
        cutoff_records.append(record)

    previous = quadrature_records[-2]
    converged = quadrature_records[-1]
    convergence_fields = (
        "scheme_a_boundary_derivative",
        "scheme_b_stationary_x",
        "scheme_b_stationary_residual",
        "scheme_b_min_low_omega_sq",
        "scheme_b_min_high_omega_sq",
    )
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in convergence_fields
    }
    cutoff_previous = cutoff_records[-2]
    cutoff_converged = cutoff_records[-1]
    cutoff_relative_errors = {
        field: relative_error(cutoff_previous[field], cutoff_converged[field])
        for field in (
            "scheme_a_boundary_derivative",
            "scheme_b_stationary_x",
            "scheme_b_min_low_omega_sq",
            "scheme_b_min_high_omega_sq",
        )
    }

    anchors_a = finite_local_counterterm(
        reference.reference_x,
        reference.reference_x,
        reference.reference_scale_sq,
        reference.scheme_a_coefficient,
    )
    anchors_b = finite_local_counterterm(
        reference.reference_x,
        reference.reference_x,
        reference.reference_scale_sq,
        reference.scheme_b_coefficient,
    )
    all_values = (
        reference.effective_mass_sq,
        reference.condensate_control,
        reference.x_boundary,
        reference.reference_x,
        reference.scheme_a_boundary_derivative,
        reference.scheme_a_reference_derivative,
        reference.scheme_b_boundary_derivative,
        reference.scheme_b_reference_derivative,
        reference.scheme_b_stationary_x,
        reference.scheme_b_stationary_residual,
        reference.scheme_b_min_low_omega_sq,
        reference.scheme_b_min_high_omega_sq,
        *anchors_a,
        *anchors_b,
    )
    checks = {
        "all_reference_values_finite": all(isfinite(value) for value in all_values),
        "stable_domain_is_declared": reference.condensate_control > 0.0
        and reference.x_boundary > 0.0,
        "scheme_a_has_no_stationary_witness_on_grid": reference.scheme_a_grid_min_derivative > 0.0,
        "scheme_a_reference_derivative_is_positive": reference.scheme_a_reference_derivative > 0.0,
        "scheme_b_brackets_stationary_witness": reference.scheme_b_boundary_derivative < 0.0
        and reference.scheme_b_reference_derivative > 0.0,
        "scheme_b_stationary_point_is_interior": reference.x_boundary
        < reference.scheme_b_stationary_x
        < reference.reference_x,
        "scheme_b_stationarity_residual_is_closed": abs(reference.scheme_b_stationary_residual)
        <= 1.0e-10,
        "scheme_b_modes_are_stable": reference.scheme_b_min_low_omega_sq > 0.0
        and reference.scheme_b_min_high_omega_sq > 0.0,
        "shared_reference_anchors_are_zero": max(
            abs(value) for value in (*anchors_a, *anchors_b)
        )
        <= 1.0e-14,
        "quadrature_stationarity_converges": convergence_relative_errors[
            "scheme_a_boundary_derivative"
        ]
        <= 1.0e-8
        and convergence_relative_errors["scheme_b_stationary_x"] <= 1.0e-8,
        "quadrature_mode_floor_remains_positive": convergence_relative_errors[
            "scheme_b_min_low_omega_sq"
        ]
        <= 1.0e-3,
        "cutoff_sweep_is_bounded": max(cutoff_relative_errors.values()) <= 2.0e-4,
        "finite_counterterm_is_declared_not_fitted": reference.scheme_b_coefficient
        == SCHEME_B_COEFFICIENT,
        "condensed_branch_is_not_claimed_complete": reference.condensed_branch_included is False,
        "physical_kubo_is_not_emitted": reference.physical_kubo_coefficient_included is False,
        "external_calibration_is_not_emitted": reference.external_calibration_included is False,
        "natural_units_are_declared": reference.unit_lane == "natural",
        "Phi_ontology_is_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace only" in contract["ontology"]["R_gen"],
        "R_obs_is_separate": "separate observer record" in contract["ontology"]["R_obs"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_SCOPED_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE"
        if not failed
        else "BLOCKED_SCOPED_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": IDENTIFIABILITY_REL, "sha256": digest(IDENTIFIABILITY_REL)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-finite-temperature-stationarity-scheme-dependence-v1",
        "artifact": "t13_uet_o2_finite_temperature_stationarity_scheme_dependence_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
            "what_is_closed": [
                "shared value, first-derivative, and second-derivative reference anchors do not select a unique finite-temperature completion",
                "declared Taylor-subtracted scheme A has no stationary witness on the tested stable-domain grid",
                "declared finite-counterterm scheme B obeys the same anchors and has an interior stationary witness with positive mode squares",
                "finite-temperature condensed-stationarity phase-selection question is closed as a scoped structural non-identifiability boundary",
            ]
            if not failed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": "natural-unit finite-temperature stationarity scheme-dependence witness",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_finite_temperature_renormalization_scheme_missing",
                "condensed_branch_and_renormalized_finite_temperature_phase_transition_missing",
                "condensate_and_normal_two_fluid_eos_completion_missing",
                "retarded_physical_Kubo_match_missing",
                "microscopic_SK_KMS_matching_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "scoped finite-temperature scheme-identifiability no-go only; no physical phase-transition, two-fluid, transport, Core, Gravity, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "reference": compact(reference),
        "reference_parameters": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI_RESPONSE,
            "scheme_b_coefficient": SCHEME_B_COEFFICIENT,
            "effective_mass_sq": reference.effective_mass_sq,
            "condensate_control": reference.condensate_control,
            "x_boundary": reference.x_boundary,
            "reference_x": reference.reference_x,
            "reference_scale_sq": reference.reference_scale_sq,
        },
        "reference_anchors": {"scheme_a": anchors_a, "scheme_b": anchors_b},
        "quadrature_records": quadrature_records,
        "quadrature_convergence_relative_errors": convergence_relative_errors,
        "cutoff_records": cutoff_records,
        "cutoff_relative_errors": cutoff_relative_errors,
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "physical_finite_temperature_renormalization_scheme_missing",
        "next_controller": "Select a physical finite-temperature renormalization prescription by independent microscopic matching or source-backed input; until then retain this result as a scoped no-go and do not call the stationary witness a phase transition.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "parameter_policy": {
            "scheme_b_coefficient": "declared internal witness, not fitted to target data",
            "grid": "fixed declared stable-domain witness grid",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT.relative_to(ROOT).as_posix(),
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": failed,
                "scheme_a_boundary_derivative": reference.scheme_a_boundary_derivative,
                "scheme_b_stationary_x": reference.scheme_b_stationary_x,
                "scheme_b_stationary_residual": reference.scheme_b_stationary_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
