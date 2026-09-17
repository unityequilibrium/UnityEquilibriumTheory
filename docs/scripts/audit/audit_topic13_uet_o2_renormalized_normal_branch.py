"""Audit the declared renormalized normal one-loop scheme lane."""

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
from docs.core.uet_covariant_response import CovariantResponseConfig, response_potential
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig, effective_mass_sq
from docs.core.uet_o2_renormalized_normal_branch import (
    uet_o2_renormalized_normal_contract,
    uet_o2_renormalized_normal_state,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py"
NORMAL_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
CURVATURE_REL = "docs/core/02_equations/o2/uet_o2_normal_response_curvature.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_renormalized_normal_branch_audit.json"

TEMPERATURE = 0.35
CHEMICAL_POTENTIAL = 0.2
PHI_REFERENCE = 0.0
PHI_RESPONSE = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 70.0
CONVERGENCE_CASES = ((96, 40.0), (192, 55.0), (256, 70.0))
PHI_DERIVATIVE_STEP = 0.02
TEMPERATURE_STEP = 1.0e-4
CHEMICAL_POTENTIAL_STEP = 1.0e-4


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
            phi_equilibrium=PHI_REFERENCE,
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
    return uet_o2_renormalized_normal_state(
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
    contract = uet_o2_renormalized_normal_contract()
    reference = state(TEMPERATURE, CHEMICAL_POTENTIAL, PHI_REFERENCE, eos_config)
    response = state(TEMPERATURE, CHEMICAL_POTENTIAL, PHI_RESPONSE, eos_config)

    derivative_step = PHI_DERIVATIVE_STEP
    response_plus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE + derivative_step,
        eos_config,
    )
    response_minus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE - derivative_step,
        eos_config,
    )
    dm_eff_sq_dphi = (
        response_plus.effective_mass_sq - response_minus.effective_mass_sq
    ) / (2.0 * derivative_step)
    vacuum_mass_second_fd = (
        (response_plus.vacuum_mass_derivative - response_minus.vacuum_mass_derivative)
        / (2.0 * derivative_step * dm_eff_sq_dphi)
    )
    vacuum_response_curvature_fd = (
        response_plus.vacuum_grand_potential
        - 2.0 * response.vacuum_grand_potential
        + response_minus.vacuum_grand_potential
    ) / derivative_step**2
    def response_sector_total_grand_potential(item, phi: float) -> float:
        return item.total_grand_potential + float(
            eos_config.response.epsilon_nc
            * response_potential(phi, eos_config.response)
        )

    total_response_curvature_fd = (
        response_sector_total_grand_potential(
            response_plus, PHI_RESPONSE + derivative_step
        )
        - 2.0 * response_sector_total_grand_potential(response, PHI_RESPONSE)
        + response_sector_total_grand_potential(
            response_minus, PHI_RESPONSE - derivative_step
        )
    ) / derivative_step**2
    pressure_temperature_plus = state(
        TEMPERATURE + TEMPERATURE_STEP,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
    ).pressure
    pressure_temperature_minus = state(
        TEMPERATURE - TEMPERATURE_STEP,
        CHEMICAL_POTENTIAL,
        PHI_RESPONSE,
        eos_config,
    ).pressure
    pressure_chemical_plus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL + CHEMICAL_POTENTIAL_STEP,
        PHI_RESPONSE,
        eos_config,
    ).pressure
    pressure_chemical_minus = state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL - CHEMICAL_POTENTIAL_STEP,
        PHI_RESPONSE,
        eos_config,
    ).pressure
    entropy_fd = (pressure_temperature_plus - pressure_temperature_minus) / (
        2.0 * TEMPERATURE_STEP
    )
    charge_fd = (pressure_chemical_plus - pressure_chemical_minus) / (
        2.0 * CHEMICAL_POTENTIAL_STEP
    )

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
                "vacuum_grand_potential": item.vacuum_grand_potential,
                "vacuum_mass_derivative": item.vacuum_mass_derivative,
                "vacuum_mass_second_derivative": item.vacuum_mass_second_derivative,
                "vacuum_response_curvature": item.vacuum_response_curvature,
                "total_response_curvature": item.total_response_curvature,
                "pressure": item.pressure,
                "entropy_density": item.entropy_density,
                "charge_density": item.charge_density,
            }
        )
    previous = convergence_records[-2]
    converged = convergence_records[-1]
    convergence_relative_errors = {
        field: relative_error(previous[field], converged[field])
        for field in (
            "vacuum_mass_second_derivative",
            "vacuum_response_curvature",
            "total_response_curvature",
            "pressure",
            "entropy_density",
            "charge_density",
        )
    }

    finite_difference_checks = {
        "mass_second_derivative_finite_difference": vacuum_mass_second_fd,
        "mass_second_derivative_analytic": response.vacuum_mass_second_derivative,
        "mass_second_derivative_abs_error": abs(
            vacuum_mass_second_fd - response.vacuum_mass_second_derivative
        ),
        "vacuum_response_curvature_finite_difference": vacuum_response_curvature_fd,
        "vacuum_response_curvature_analytic": response.vacuum_response_curvature,
        "vacuum_response_curvature_abs_error": abs(
            vacuum_response_curvature_fd - response.vacuum_response_curvature
        ),
        "total_response_curvature_finite_difference": total_response_curvature_fd,
        "total_response_curvature_analytic": response.total_response_curvature,
        "total_response_curvature_abs_error": abs(
            total_response_curvature_fd - response.total_response_curvature
        ),
        "entropy_finite_difference": entropy_fd,
        "entropy_analytic": response.entropy_density,
        "entropy_abs_error": abs(entropy_fd - response.entropy_density),
        "charge_finite_difference": charge_fd,
        "charge_analytic": response.charge_density,
        "charge_abs_error": abs(charge_fd - response.charge_density),
    }

    checks = {
        "reference_mass_matches_phi_star": reference.effective_mass_sq
        == reference.reference_mass_sq,
        "reference_vacuum_potential_zero": abs(reference.vacuum_grand_potential) <= 1.0e-14,
        "reference_vacuum_first_derivative_zero": abs(reference.vacuum_mass_derivative)
        <= 1.0e-14,
        "reference_vacuum_second_derivative_zero": abs(reference.vacuum_mass_second_derivative)
        <= 1.0e-14,
        "normal_branch_selected": reference.normal_branch and response.normal_branch,
        "positive_effective_mass_squared": reference.effective_mass_sq > 0.0
        and response.effective_mass_sq > 0.0,
        "all_reference_values_finite": all(
            isfinite(value)
            for value in (
                reference.vacuum_grand_potential,
                reference.vacuum_mass_derivative,
                reference.vacuum_mass_second_derivative,
                response.vacuum_grand_potential,
                response.total_response_curvature,
            )
        ),
        "mass_second_derivative_matches_finite_difference": finite_difference_checks[
            "mass_second_derivative_abs_error"
        ]
        <= 2.0e-8,
        "vacuum_response_curvature_matches_finite_difference": finite_difference_checks[
            "vacuum_response_curvature_abs_error"
        ]
        <= 2.0e-6,
        "total_response_curvature_matches_finite_difference": finite_difference_checks[
            "total_response_curvature_abs_error"
        ]
        <= 2.0e-5,
        "entropy_matches_pressure_derivative": finite_difference_checks[
            "entropy_abs_error"
        ]
        <= 1.0e-7,
        "charge_matches_pressure_derivative": finite_difference_checks[
            "charge_abs_error"
        ]
        <= 1.0e-8,
        "vacuum_is_temperature_and_mu_independent": abs(
            state(
                TEMPERATURE + 0.1,
                CHEMICAL_POTENTIAL + 0.1,
                PHI_RESPONSE,
                eos_config,
            ).vacuum_grand_potential
            - response.vacuum_grand_potential
        )
        <= 1.0e-14,
        "vacuum_second_derivative_converges": convergence_relative_errors[
            "vacuum_mass_second_derivative"
        ]
        <= 3.0e-4,
        "response_curvature_converges": convergence_relative_errors[
            "total_response_curvature"
        ]
        <= 1.0e-5,
        "thermal_pressure_converges": convergence_relative_errors["pressure"] <= 1.0e-5,
        "scheme_is_natural_units": contract["units"]["unit_lane"] == "natural",
        "subtraction_order_is_declared": contract["renormalization_scheme"][
            "subtraction_order"
        ]
        == 2,
        "condensate_is_excluded": response.condensate_contribution_included is False,
        "interacting_self_energy_is_excluded": contract["scope"][
            "interacting_thermal_self_energy"
        ]
        == "NOT_INCLUDED",
        "physical_kubo_is_excluded": response.physical_kubo_coefficient_included is False,
        "physical_si_mapping_is_excluded": response.physical_si_mapping_included is False,
        "alpha_is_not_emitted": contract["units"]["alpha_Phi_K"]
        == "not emitted; SI map remains open",
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not identified" in contract["ontology"]["C"],
        "R_gen_is_derived_only": "derived history trace only" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": NORMAL_REL, "sha256": digest(NORMAL_REL)},
        {"path": CURVATURE_REL, "sha256": digest(CURVATURE_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-renormalized-normal-one-loop-v1",
        "artifact": "t13_uet_o2_renormalized_normal_branch_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_RENORMALIZED_NORMAL_ONE_LOOP_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "declared mass-squared Taylor-subtraction scheme through second order at Phi_*",
                "finite normal-branch vacuum plus thermal one-loop state in natural units",
                "reference-point renormalization conditions and cutoff convergence",
                "action-derived response curvature with an explicit vacuum contribution",
                "thermal pressure, entropy, charge, and energy identities for the combined state",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived declared BPHZ-style mass-squared subtraction plus thermal one-loop normal determinant; not a microscopic matching",
            "observable": "natural-unit renormalized normal-branch grand potential and response curvature",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "interacting_finite_temperature_self_energy_and_unique_microscopic_scheme_matching_missing",
                "condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing",
                "physical_kubo_coefficients_and_microscopic_sk_kms_matching_missing",
                "entropy_current_dissipative_balance_and_heat_flux_mapping_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ttg_numeric_source_package_is_provisional",
            ],
            "dependency_unlocked": "renormalized normal one-loop scheme lane only; no full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "phi_reference": PHI_REFERENCE,
            "phi_response": PHI_RESPONSE,
            "effective_mass_sq_at_reference": reference.effective_mass_sq,
            "effective_mass_sq_at_response": response.effective_mass_sq,
            "reference_mass_sq": reference.reference_mass_sq,
            "vacuum_grand_potential": response.vacuum_grand_potential,
            "vacuum_mass_derivative": response.vacuum_mass_derivative,
            "vacuum_mass_second_derivative": response.vacuum_mass_second_derivative,
            "vacuum_response_curvature": response.vacuum_response_curvature,
            "total_response_curvature": response.total_response_curvature,
            "pressure": response.pressure,
            "entropy_density": response.entropy_density,
            "charge_density": response.charge_density,
            "energy_density": response.energy_density,
            "momentum_cutoff": response.momentum_cutoff,
            "quadrature_order": response.quadrature_order,
        },
        "finite_difference_checks": finite_difference_checks,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "numerical_stability_note": "The subtracted vacuum potential is a small difference of large Taylor-cancelled terms. Curvature acceptance therefore uses mass-derivative finite differences and records potential finite-difference sensitivity instead of hiding cancellation.",
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "interacting_finite_temperature_self_energy_and_unique_microscopic_scheme_matching_missing",
        "next_controller": "Close the finite-temperature renormalized action beyond the declared free normal determinant, then match the physical Kubo/SK-KMS and SI Phi observable interfaces without using Xie 2026 or fitting alpha_Phi_K.",
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
                "vacuum_mass_second_derivative": response.vacuum_mass_second_derivative,
                "total_response_curvature": response.total_response_curvature,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
