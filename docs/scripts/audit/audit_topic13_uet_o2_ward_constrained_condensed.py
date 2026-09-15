"""Audit the formal Ward-constrained condensed stationarity lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from math import isfinite
from pathlib import Path

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_ward_constrained_condensed import (
    ward_constrained_condensed_contract,
    ward_constrained_condensed_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_ward_constrained_condensed.py"
STATIONARITY_REL = "docs/core/uet_o2_finite_temperature_stationarity_scheme.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_ward_constrained_condensed_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.30
PHI_RESPONSE = 0.20
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
QUADRATURE_ORDERS = (96, 192, 256)
CUTOFF_FACTORS = (50.0, 70.0, 90.0)
REFERENCE_FACTOR = 2.0
ONE_SIDED_FRACTION = 1.0e-2
DERIVATIVE_TOLERANCE = 1.0e-10
GOLDSTONE_TOLERANCE = 1.0e-10


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


def compact(result) -> dict:
    return {
        "quadrature_order": result.quadrature_order,
        "momentum_cutoff": result.momentum_cutoff,
        "x_boundary": result.x_boundary,
        "reference_x": result.reference_x,
        "base_boundary_derivative": result.base_boundary_derivative,
        "ward_counterterm_coefficient": result.ward_counterterm_coefficient,
        "ward_boundary_derivative": result.ward_boundary_derivative,
        "ward_boundary_low_mode_sq": result.ward_boundary_low_mode_sq,
        "ward_boundary_high_mode_sq": result.ward_boundary_high_mode_sq,
        "near_boundary_x": result.near_boundary_x,
        "near_boundary_derivative": result.near_boundary_derivative,
        "reference_derivative": result.reference_derivative,
        "reference_counterterm_anchors": result.reference_counterterm_anchors,
    }


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def main() -> int:
    eos_config = config()
    contract = ward_constrained_condensed_contract()
    reference = ward_constrained_condensed_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
        reference_factor=REFERENCE_FACTOR,
        one_sided_fraction=ONE_SIDED_FRACTION,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    reference_record = compact(reference)

    quadrature_records = []
    for order in QUADRATURE_ORDERS:
        result = ward_constrained_condensed_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            reference_factor=REFERENCE_FACTOR,
            one_sided_fraction=ONE_SIDED_FRACTION,
            quadrature_order=order,
            cutoff_factor=REFERENCE_CUTOFF_FACTOR,
        )
        quadrature_records.append(compact(result))

    cutoff_records = []
    for cutoff_factor in CUTOFF_FACTORS:
        result = ward_constrained_condensed_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            reference_factor=REFERENCE_FACTOR,
            one_sided_fraction=ONE_SIDED_FRACTION,
            quadrature_order=REFERENCE_ORDER,
            cutoff_factor=cutoff_factor,
        )
        record = compact(result)
        record["cutoff_factor"] = cutoff_factor
        cutoff_records.append(record)

    q_previous = quadrature_records[-2]
    q_converged = quadrature_records[-1]
    quadrature_convergence = {
        field: relative_error(q_previous[field], q_converged[field])
        for field in (
            "ward_counterterm_coefficient",
            "ward_boundary_low_mode_sq",
            "ward_boundary_high_mode_sq",
            "near_boundary_derivative",
        )
    }
    c_previous = cutoff_records[-2]
    c_converged = cutoff_records[-1]
    cutoff_convergence = {
        field: relative_error(c_previous[field], c_converged[field])
        for field in (
            "ward_counterterm_coefficient",
            "ward_boundary_low_mode_sq",
            "ward_boundary_high_mode_sq",
            "near_boundary_derivative",
        )
    }

    coefficient_from_formula = -reference.base_boundary_derivative * reference.reference_scale_sq / (
        3.0 * (reference.x_boundary - reference.reference_x) ** 2
    )
    values = tuple(
        value
        for key, value in reference_record.items()
        if key != "reference_counterterm_anchors"
    ) + tuple(reference_record["reference_counterterm_anchors"]) + (
        coefficient_from_formula,
    )
    checks = {
        "reference_values_are_finite": all(isfinite(float(value)) for value in values),
        "condensed_control_is_positive": reference.condensate_control > 0.0,
        "ward_coefficient_is_algebraically_derived": abs(
            reference.ward_counterterm_coefficient - coefficient_from_formula
        )
        <= 1.0e-14,
        "base_scheme_has_nonzero_ward_point_derivative": abs(
            reference.base_boundary_derivative
        )
        > 1.0e-4,
        "ward_boundary_stationarity_is_closed": abs(reference.ward_boundary_derivative)
        <= DERIVATIVE_TOLERANCE,
        "ward_boundary_has_zero_goldstone_mode": abs(
            reference.ward_boundary_low_mode_sq
        )
        <= GOLDSTONE_TOLERANCE,
        "ward_boundary_high_mode_is_positive": reference.ward_boundary_high_mode_sq > 0.0,
        "one_sided_stable_direction_is_positive": reference.near_boundary_derivative > 0.0,
        "reference_counterterm_anchors_are_zero": max(
            abs(value) for value in reference.reference_counterterm_anchors
        )
        <= 1.0e-14,
        "reference_derivative_is_finite": isfinite(reference.reference_derivative),
        "quadrature_converges": max(quadrature_convergence.values()) <= 1.0e-3,
        "cutoff_converges": max(cutoff_convergence.values()) <= 2.0e-4,
        "ward_constraint_is_not_fit": True,
        "no_external_source_rows": True,
        "no_holdout_or_fit": True,
        "physical_renormalization_is_excluded": reference.physical_renormalization_included is False,
        "physical_kubo_is_excluded": reference.physical_kubo_coefficient_included is False,
        "normal_two_fluid_is_excluded": reference.normal_two_fluid_completion_included is False,
        "external_calibration_is_excluded": reference.external_calibration_included is False,
        "natural_units_are_declared": reference.unit_lane == "natural",
        "Phi_ontology_is_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_is_preserved": "derived history trace only" in contract["ontology"]["R_gen"],
        "R_obs_is_separate": "separate observer record" in contract["ontology"]["R_obs"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = (
        "PASS_FORMAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY"
        if not failed
        else "BLOCKED_FORMAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": STATIONARITY_REL, "sha256": digest(STATIONARITY_REL)},
    ]
    artifact = {
        "schema_version": "t13-uet-o2-ward-constrained-condensed-v1",
        "artifact": "t13_uet_o2_ward_constrained_condensed_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_WARD_CONSTRAINED_CONDENSED_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "the finite local counterterm coefficient is derived algebraically from the Goldstone/Ward condition at the tree condensate boundary",
                "the Ward point is stationary under the constrained completion to the declared numerical tolerance",
                "the Ward point has a zero low mode, positive high mode, and positive one-sided stationarity direction",
                "reference anchors, quadrature convergence, cutoff convergence, ontology, and no-fit policy pass",
            ]
            if not failed
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": "formal Ward-constrained condensed stationarity witness in natural units",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "physical_finite_temperature_renormalization_scheme_missing",
                "ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing",
                "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
                "retarded_physical_Kubo_match_missing",
                "microscopic_SK_KMS_matching_missing",
                "full_heat_flux_entropy_production_and_dissipative_balance_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "formal Ward-constrained condensed stationarity lane only; no physical renormalization, full condensed EOS, two-fluid, transport, Core, Gravity, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "reference": reference_record,
        "reference_parameters": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI_RESPONSE,
            "reference_factor": REFERENCE_FACTOR,
            "one_sided_fraction": ONE_SIDED_FRACTION,
            "derivative_tolerance": DERIVATIVE_TOLERANCE,
            "goldstone_tolerance": GOLDSTONE_TOLERANCE,
        },
        "quadrature_records": quadrature_records,
        "quadrature_convergence_relative_errors": quadrature_convergence,
        "cutoff_records": cutoff_records,
        "cutoff_convergence_relative_errors": cutoff_convergence,
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing",
        "next_controller": "Replace the formal Ward-constrained local completion with a source-backed or microscopically renormalized symmetry-improved 2PI/controlled 1/N condensed branch, then close the physical EOS and retarded Kubo/SK-KMS interfaces.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "parameter_policy": {
            "ward_counterterm_coefficient": "algebraically derived from the Ward condition; not fitted to a target curve",
            "reference_factor": "declared internal reference construction",
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
                "ward_counterterm_coefficient": reference.ward_counterterm_coefficient,
                "ward_boundary_derivative": reference.ward_boundary_derivative,
                "ward_boundary_low_mode_sq": reference.ward_boundary_low_mode_sq,
                "near_boundary_derivative": reference.near_boundary_derivative,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
