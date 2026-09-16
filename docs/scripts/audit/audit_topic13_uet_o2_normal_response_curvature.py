"""Audit the action-derived natural-unit thermal response curvature lane."""

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
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_normal_response_curvature import (
    uet_o2_normal_response_curvature_contract,
    uet_o2_normal_response_curvature_state,
)
from docs.core.uet_o2_one_loop_normal_branch import uet_o2_one_loop_normal_state


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/02_equations/o2/uet_o2_normal_response_curvature.py"
ONE_LOOP_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
RESPONSE_REL = "docs/core/02_equations/covariant/uet_covariant_response.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_normal_response_curvature_audit.json"

TEMPERATURE = 0.35
CHEMICAL_POTENTIAL = 0.2
PHI = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 70.0
CONVERGENCE_CASES = ((96, 40.0), (192, 55.0), (256, 70.0))
PHI_STEP = 1.0e-4
TEMPERATURE_STEP = 1.0e-4


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


def normal_omega(
    temperature: float,
    chemical_potential: float,
    phi: float,
    eos_config: O2FiniteDensityEOSConfig,
    *,
    order: int,
    cutoff_factor: float,
) -> float:
    state = uet_o2_one_loop_normal_state(
        temperature,
        chemical_potential,
        phi,
        eos_config,
        quadrature_order=order,
        cutoff_factor=cutoff_factor,
    )
    return float(-state.pressure)


def total_omega_with_bare_response(
    temperature: float,
    chemical_potential: float,
    phi: float,
    eos_config: O2FiniteDensityEOSConfig,
    *,
    order: int,
    cutoff_factor: float,
) -> float:
    return normal_omega(
        temperature,
        chemical_potential,
        phi,
        eos_config,
        order=order,
        cutoff_factor=cutoff_factor,
    ) + float(
        eos_config.response.epsilon_nc
        * response_potential(phi, eos_config.response)
    )


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def main() -> int:
    eos_config = config()
    contract = uet_o2_normal_response_curvature_contract()
    state = uet_o2_normal_response_curvature_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    h_phi = PHI_STEP
    omega_phi_plus = normal_omega(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI + h_phi,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    omega_phi_minus = normal_omega(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI - h_phi,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    omega_reference = normal_omega(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    thermal_curvature_fd = (
        omega_phi_plus - 2.0 * omega_reference + omega_phi_minus
    ) / h_phi**2

    h_temperature = TEMPERATURE_STEP
    curvature_plus = uet_o2_normal_response_curvature_state(
        TEMPERATURE + h_temperature,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    curvature_minus = uet_o2_normal_response_curvature_state(
        TEMPERATURE - h_temperature,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    thermal_curvature_temperature_derivative_fd = (
        curvature_plus.thermal_response_curvature
        - curvature_minus.thermal_response_curvature
    ) / (2.0 * h_temperature)

    total_phi_plus = total_omega_with_bare_response(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI + h_phi,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    total_phi_minus = total_omega_with_bare_response(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI - h_phi,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    total_reference = total_omega_with_bare_response(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    total_curvature_fd = (
        total_phi_plus - 2.0 * total_reference + total_phi_minus
    ) / h_phi**2

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        item = uet_o2_normal_response_curvature_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI,
            eos_config,
            quadrature_order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "thermal_response_curvature": item.thermal_response_curvature,
                "total_response_curvature": item.total_response_curvature,
                "thermal_response_curvature_temperature_derivative": item.thermal_response_curvature_temperature_derivative,
                "beta_action_natural": item.beta_action_natural,
            }
        )
    reference_record = convergence_records[-1]
    previous_record = convergence_records[-2]
    convergence_relative_errors = {
        field: relative_error(previous_record[field], reference_record[field])
        for field in (
            "thermal_response_curvature",
            "total_response_curvature",
            "thermal_response_curvature_temperature_derivative",
            "beta_action_natural",
        )
    }

    finite_difference_checks = {
        "thermal_curvature_finite_difference": thermal_curvature_fd,
        "thermal_curvature_analytic": state.thermal_response_curvature,
        "thermal_curvature_abs_error": abs(
            thermal_curvature_fd - state.thermal_response_curvature
        ),
        "thermal_curvature_temperature_derivative_finite_difference": thermal_curvature_temperature_derivative_fd,
        "thermal_curvature_temperature_derivative_analytic": state.thermal_response_curvature_temperature_derivative,
        "thermal_curvature_temperature_derivative_abs_error": abs(
            thermal_curvature_temperature_derivative_fd
            - state.thermal_response_curvature_temperature_derivative
        ),
        "total_curvature_finite_difference": total_curvature_fd,
        "total_curvature_analytic": state.total_response_curvature,
        "total_curvature_abs_error": abs(
            total_curvature_fd - state.total_response_curvature
        ),
    }

    checks = {
        "normal_branch_selected": state.normal_branch,
        "mass_map_is_finite": isfinite(state.effective_mass_sq)
        and isfinite(state.dm_eff_sq_dphi),
        "bare_response_curvature_is_finite": isfinite(state.bare_response_curvature),
        "thermal_response_curvature_is_finite": isfinite(state.thermal_response_curvature),
        "total_response_curvature_is_finite": isfinite(state.total_response_curvature),
        "analytic_thermal_curvature_matches_finite_difference": finite_difference_checks[
            "thermal_curvature_abs_error"
        ]
        <= 2.0e-6,
        "analytic_temperature_slope_matches_finite_difference": finite_difference_checks[
            "thermal_curvature_temperature_derivative_abs_error"
        ]
        <= 2.0e-5,
        "analytic_total_curvature_matches_finite_difference": finite_difference_checks[
            "total_curvature_abs_error"
        ]
        <= 2.0e-6,
        "thermal_only_convergence": convergence_relative_errors[
            "thermal_response_curvature"
        ]
        <= 1.0e-5,
        "temperature_slope_convergence": convergence_relative_errors[
            "thermal_response_curvature_temperature_derivative"
        ]
        <= 1.0e-5,
        "beta_action_is_not_beta_t13": contract["units"]["beta_T13"]
        == "not identified; its normalized K^-1 contract remains separate",
        "alpha_is_not_emitted": contract["units"]["alpha_Phi_K"]
        == "not emitted; SI map remains open",
        "vacuum_counterterm_is_excluded": state.vacuum_counterterm_included is False,
        "condensate_is_excluded": state.condensate_contribution_included is False,
        "physical_beta_is_not_identified": state.physical_beta_t13_identified is False,
        "physical_si_mapping_is_not_included": state.physical_si_mapping_included is False,
        "Phi_is_not_temperature": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_is_preserved": "not identified" in contract["ontology"]["C"],
        "R_gen_is_not_state": "not used as state" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE"
    )
    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": ONE_LOOP_REL, "sha256": digest(ONE_LOOP_REL)},
        {"path": RESPONSE_REL, "sha256": digest(RESPONSE_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-normal-response-curvature-v1",
        "artifact": "t13_uet_o2_normal_response_curvature_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_NORMAL_RESPONSE_CURVATURE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "natural-unit thermal response curvature of the normal one-loop branch from the declared m_eff(Phi) action map",
                "temperature derivative T*d_T(kappa_Phi^T) with analytic and finite-difference verification",
                "addition of the declared bare response-potential Hessian as a separate action term",
                "explicit separation from normalized beta_T13, SI alpha_Phi_K, vacuum renormalization, condensate, and physical transport",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived thermal one-loop normal response curvature and temperature derivative; no vacuum renormalization or SI identification",
            "observable": "natural-unit response free-energy curvature and temperature slope",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "condensate_and_finite_temperature_normal_two_fluid_completion_not_closed",
                "beta_T13_normalized_correspondence_and_source_provenance_missing",
                "physical_Kubo_coefficient_record_missing",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "action-derived natural-unit normal response curvature lane only; no normalized beta, physical transport, SI, Full Topic 13, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI,
            "effective_mass_sq": state.effective_mass_sq,
            "dm_eff_sq_dphi": state.dm_eff_sq_dphi,
            "bare_response_curvature": state.bare_response_curvature,
            "thermal_response_curvature": state.thermal_response_curvature,
            "total_response_curvature": state.total_response_curvature,
            "thermal_response_curvature_temperature_derivative": state.thermal_response_curvature_temperature_derivative,
            "beta_action_natural": state.beta_action_natural,
            "momentum_cutoff": state.momentum_cutoff,
            "quadrature_order": state.quadrature_order,
            "thermal_only_loop": state.thermal_only_loop,
            "vacuum_counterterm_included": state.vacuum_counterterm_included,
            "physical_beta_t13_identified": state.physical_beta_t13_identified,
            "physical_si_mapping_included": state.physical_si_mapping_included,
        },
        "finite_difference_checks": finite_difference_checks,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "beta_T13_normalized_correspondence_and_source_provenance_missing",
        "next_controller": "Match the natural-unit response curvature to a declared normalized finite-temperature functional or independent source-backed coefficient without identifying it with beta_T13 by notation; separately close vacuum renormalization, normal/two-fluid transport, SI Phi mapping, and alpha calibration.",
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
                "thermal_response_curvature": state.thermal_response_curvature,
                "total_response_curvature": state.total_response_curvature,
                "beta_action_natural": state.beta_action_natural,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
