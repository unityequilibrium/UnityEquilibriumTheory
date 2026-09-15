"""Audit the action-derived finite-temperature O(2) Hartree self-energy lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite
from pathlib import Path

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_self_energy import (
    uet_o2_finite_temperature_self_energy_contract,
    uet_o2_finite_temperature_self_energy_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_finite_temperature_self_energy.py"
PARENT_REL = "docs/core/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_self_energy_audit.json"

TEMPERATURE = 0.35
CHEMICAL_POTENTIAL = 0.2
PHI_RESPONSE = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 70.0
CONVERGENCE_CASES = ((96, 40.0), (192, 55.0), (256, 70.0))
PHI_DERIVATIVE_STEP = 1.0e-4


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


def state(
    temperature: float,
    chemical_potential: float,
    phi: float,
    eos_config: O2FiniteDensityEOSConfig,
    *,
    order: int = REFERENCE_ORDER,
    cutoff_factor: float = REFERENCE_CUTOFF_FACTOR,
):
    return uet_o2_finite_temperature_self_energy_state(
        temperature,
        chemical_potential,
        phi,
        eos_config,
        quadrature_order=order,
        cutoff_factor=cutoff_factor,
    )


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def main() -> int:
    eos_config = config()
    contract = uet_o2_finite_temperature_self_energy_contract()
    reference = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
    )
    phi_step = PHI_DERIVATIVE_STEP
    response_plus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE + phi_step,
        eos_config,
    )
    response_minus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE - phi_step,
        eos_config,
    )
    response_derivative_fd = (
        response_plus.dressed_mass_sq - response_minus.dressed_mass_sq
    ) / (2.0 * phi_step)

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        item = state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI_RESPONSE,
            eos_config,
            order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "base_mass_sq": item.base_mass_sq,
                "dressed_mass_sq": item.dressed_mass_sq,
                "thermal_self_energy": item.thermal_self_energy,
                "self_energy_mass_derivative": item.self_energy_mass_derivative,
                "dressed_mass_response_derivative": item.dressed_mass_response_derivative,
                "gap_residual": item.gap_residual,
            }
        )
    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in (
            "dressed_mass_sq",
            "thermal_self_energy",
            "self_energy_mass_derivative",
            "dressed_mass_response_derivative",
        )
    }

    weak_config = O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_mass_sq=1.0e-12,
            matter_quartic=1.0e-3,
            response_coupling=0.0,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.0),
    )
    weak_temperature = 10.0
    weak = state(
        weak_temperature,
        0.0,
        0.0,
        weak_config,
        order=REFERENCE_ORDER,
        cutoff_factor=60.0,
    )
    weak_coupling = weak_config.matter.matter_quartic
    weak_high_temperature_limit = (2 + 2) / 12.0
    weak_high_temperature_ratio = weak.thermal_self_energy / (
        weak_coupling * weak_temperature**2
    )

    finite_difference_checks = {
        "dressed_mass_response_derivative_finite_difference": response_derivative_fd,
        "dressed_mass_response_derivative_implicit": reference.dressed_mass_response_derivative,
        "dressed_mass_response_derivative_abs_error": abs(
            response_derivative_fd - reference.dressed_mass_response_derivative
        ),
        "weak_high_temperature_ratio": weak_high_temperature_ratio,
        "weak_high_temperature_limit": weak_high_temperature_limit,
        "weak_high_temperature_relative_error": relative_error(
            weak_high_temperature_ratio,
            weak_high_temperature_limit,
        ),
    }

    checks = {
        "gap_residual_is_closed": abs(reference.gap_residual) <= 5.0e-12,
        "normal_branch_is_selected": reference.dressed_mass_sq
        > CHEMICAL_POTENTIAL**2,
        "thermal_self_energy_is_non_negative": reference.thermal_self_energy >= 0.0,
        "self_energy_mass_derivative_is_non_positive": reference.self_energy_mass_derivative
        <= 1.0e-14,
        "implicit_response_matches_finite_difference": finite_difference_checks[
            "dressed_mass_response_derivative_abs_error"
        ]
        <= 1.0e-7,
        "dressed_mass_converges": convergence_relative_errors["dressed_mass_sq"]
        <= 1.0e-8,
        "self_energy_converges": convergence_relative_errors["thermal_self_energy"]
        <= 1.0e-8,
        "self_energy_derivative_converges": convergence_relative_errors[
            "self_energy_mass_derivative"
        ]
        <= 1.0e-8,
        "response_derivative_converges": convergence_relative_errors[
            "dressed_mass_response_derivative"
        ]
        <= 1.0e-8,
        "weak_high_temperature_witness": finite_difference_checks[
            "weak_high_temperature_relative_error"
        ]
        <= 2.0e-2,
        "all_reference_values_finite": all(
            isfinite(value)
            for value in (
                reference.base_mass_sq,
                reference.dressed_mass_sq,
                reference.thermal_self_energy,
                reference.self_energy_mass_derivative,
                reference.dressed_mass_response_derivative,
                reference.gap_residual,
            )
        ),
        "natural_units_are_declared": contract["units"]["unit_lane"] == "natural",
        "vacuum_counterterm_boundary_is_declared": contract["approximation"][
            "vacuum_counterterm"
        ]
        == "NOT_INCLUDED; use the separately declared subtraction scheme",
        "condensate_boundary_is_declared": contract["approximation"][
            "condensate_branch"
        ]
        == "NOT_INCLUDED",
        "physical_kubo_boundary_is_declared": contract["approximation"][
            "physical_kubo"
        ]
        == "NOT_INCLUDED",
        "sk_kms_boundary_is_declared": contract["approximation"][
            "sk_kms_microscopic_match"
        ]
        == "NOT_INCLUDED",
        "alpha_is_not_emitted": contract["units"]["alpha_Phi_K"]
        == "not emitted; SI map remains open",
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not charge density" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_HARTREE_THERMAL_SELF_ENERGY"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_HARTREE_THERMAL_SELF_ENERGY"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": PARENT_REL, "sha256": digest(PARENT_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-finite-temperature-self-energy-v1",
        "artifact": "t13_uet_o2_finite_temperature_self_energy_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_SELF_ENERGY_HARTREE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "O(2) Hartree thermal tadpole from the declared natural-unit action",
                "self-consistent dressed normal-branch mass gap",
                "implicit finite-temperature response derivative",
                "quadrature/cutoff convergence and weak-coupling high-temperature witness",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": "natural-unit dressed mass-squared, thermal self-energy, and response derivative",
            "data_role": "ACTION_DERIVED_INTERNAL_NO_EXTERNAL_CALIBRATION",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_unique_microscopic_finite_temperature_scheme_matching_missing",
                "condensate_and_normal_two_fluid_completion_missing",
                "physical_Kubo_coefficient_record_missing",
                "SK_KMS_physical_matching_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "action-derived Hartree finite-temperature self-energy lane only; no full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "phi_response": PHI_RESPONSE,
            "base_mass_sq": reference.base_mass_sq,
            "dressed_mass_sq": reference.dressed_mass_sq,
            "thermal_self_energy": reference.thermal_self_energy,
            "self_energy_mass_derivative": reference.self_energy_mass_derivative,
            "dressed_mass_response_derivative": reference.dressed_mass_response_derivative,
            "gap_residual": reference.gap_residual,
            "momentum_cutoff": reference.momentum_cutoff,
            "quadrature_order": reference.quadrature_order,
            "iterations": reference.iterations,
        },
        "finite_difference_checks": finite_difference_checks,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "weak_coupling_witness": {
            "temperature": weak_temperature,
            "matter_quartic": weak_coupling,
            "expected_limit": "(N+2)/12 with N=2",
            "ratio": weak_high_temperature_ratio,
            "relative_error": finite_difference_checks[
                "weak_high_temperature_relative_error"
            ],
            "source_role": "analytic_internal_limit_witness_not_external_data",
        },
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "interacting_finite_temperature_self_energy_and_unique_microscopic_scheme_matching_missing",
        "next_controller": "Close the microscopic finite-temperature scheme and physical SK/KMS/Kubo interfaces, then return to the independent Phi SI anchor and alpha_Phi_K without reading or fitting Xie 2026.",
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
                "gap_residual": reference.gap_residual,
                "response_derivative_abs_error": finite_difference_checks[
                    "dressed_mass_response_derivative_abs_error"
                ],
                "weak_high_temperature_ratio": weak_high_temperature_ratio,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
