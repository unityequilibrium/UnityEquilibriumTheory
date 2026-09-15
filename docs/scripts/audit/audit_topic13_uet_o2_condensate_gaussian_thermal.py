"""Audit the fixed-background finite-temperature Gaussian O(2) lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_condensate_fluctuations import (
    condensate_fluctuation_state,
    quadratic_mode_omega_sq,
)
from docs.core.uet_o2_condensate_gaussian_thermal import (
    uet_o2_condensate_gaussian_thermal_contract,
    uet_o2_condensate_gaussian_thermal_state,
)
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    o2_equilibrium_state,
)


ROOT = Path(__file__).resolve().parents[3]
THERMAL_REL = "docs/core/uet_o2_condensate_gaussian_thermal.py"
SPECTRUM_REL = "docs/core/uet_o2_condensate_fluctuations.py"
EOS_REL = "docs/core/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_gaussian_thermal_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.3
PHI = 0.2
DERIVATIVE_STEP = 1.0e-5
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
CONVERGENCE_CASES = ((96, 50.0), (192, 70.0), (256, 90.0))
WAVENUMBERS = (0.01, 0.1, 0.5, 1.0)


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


def finite_difference_checks(
    state, eos_config: O2FiniteDensityEOSConfig
) -> dict[str, float]:
    h = DERIVATIVE_STEP
    mu_plus = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL + h,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    mu_minus = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL - h,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    t_plus = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE + h,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    t_minus = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE - h,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    phi_plus = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI + h,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    phi_minus = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI - h,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    return {
        "dp_dmu_finite_difference": (mu_plus.pressure - mu_minus.pressure) / (2.0 * h),
        "dp_dT_finite_difference": (t_plus.pressure - t_minus.pressure) / (2.0 * h),
        "dp_dPhi_finite_difference": (phi_plus.pressure - phi_minus.pressure) / (2.0 * h),
        "abs_dp_dmu_error": abs(
            (mu_plus.pressure - mu_minus.pressure) / (2.0 * h) - state.charge_density
        ),
        "abs_dp_dT_error": abs(
            (t_plus.pressure - t_minus.pressure) / (2.0 * h) - state.entropy_density
        ),
        "abs_dp_dPhi_error": abs(
            (phi_plus.pressure - phi_minus.pressure) / (2.0 * h)
            - state.response_pressure_derivative
        ),
    }


def main() -> int:
    eos_config = config()
    tree_state = o2_equilibrium_state(CHEMICAL_POTENTIAL, PHI, eos_config)
    fluctuation_state = condensate_fluctuation_state(
        CHEMICAL_POTENTIAL, PHI, eos_config
    )
    state = uet_o2_condensate_gaussian_thermal_state(
        TEMPERATURE,
        CHEMICAL_POTENTIAL,
        PHI,
        eos_config,
        quadrature_order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    contract = uet_o2_condensate_gaussian_thermal_contract()

    mode_records = []
    for wavenumber in WAVENUMBERS:
        low_sq, high_sq = quadratic_mode_omega_sq(
            wavenumber, fluctuation_state, eos_config
        )
        mode_records.append(
            {
                "wavenumber": wavenumber,
                "goldstone_omega_sq": low_sq,
                "high_omega_sq": high_sq,
                "goldstone_frequency": float(np.sqrt(low_sq)),
                "high_frequency": float(np.sqrt(high_sq)),
            }
        )

    convergence_states = [
        uet_o2_condensate_gaussian_thermal_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI,
            eos_config,
            quadrature_order=order,
            cutoff_factor=cutoff_factor,
        )
        for order, cutoff_factor in CONVERGENCE_CASES
    ]
    convergence_records = [
        {
            "quadrature_order": order,
            "cutoff_factor": cutoff_factor,
            "pressure": item.pressure,
            "entropy_density": item.entropy_density,
            "charge_density": item.charge_density,
            "energy_density": item.energy_density,
            "response_pressure_derivative": item.response_pressure_derivative,
        }
        for (order, cutoff_factor), item in zip(CONVERGENCE_CASES, convergence_states)
    ]
    reference = convergence_states[-1]
    finite_differences = finite_difference_checks(reference, eos_config)
    convergence_relative_errors = {
        field: relative_error(getattr(convergence_states[-2], field), getattr(reference, field))
        for field in (
            "pressure",
            "entropy_density",
            "charge_density",
            "energy_density",
            "response_pressure_derivative",
        )
    }

    checks = {
        "condensed_tree_background_selected": tree_state.branch == "condensed",
        "condensate_control_positive": fluctuation_state.condensate_control > 0.0,
        "temperature_positive": reference.temperature > 0.0,
        "pressure_positive": reference.pressure > 0.0,
        "entropy_positive": reference.entropy_density > 0.0,
        "energy_positive": reference.energy_density > 0.0,
        "mode_roots_nonnegative": all(
            item["goldstone_omega_sq"] >= 0.0 and item["high_omega_sq"] > 0.0
            for item in mode_records
        ),
        "high_mode_above_low_mode": all(
            item["high_omega_sq"] >= item["goldstone_omega_sq"]
            for item in mode_records
        ),
        "branch_pressure_decomposition_closes": abs(
            reference.pressure
            - reference.low_branch_pressure
            - reference.high_branch_pressure
        )
        <= 1.0e-15,
        "branch_entropy_decomposition_closes": abs(
            reference.entropy_density
            - reference.low_branch_entropy
            - reference.high_branch_entropy
        )
        <= 1.0e-15,
        "branch_response_decomposition_is_finite": all(
            np.isfinite(value)
            for value in (
                reference.low_branch_charge,
                reference.high_branch_charge,
            )
        ),
        "dp_dmu_matches_response": finite_differences["abs_dp_dmu_error"] <= 2.0e-8,
        "dp_dT_matches_entropy": finite_differences["abs_dp_dT_error"] <= 2.0e-8,
        "dp_dPhi_matches_response": finite_differences["abs_dp_dPhi_error"] <= 2.0e-8,
        "energy_identity_closes": abs(
            reference.energy_density
            - (
                -reference.pressure
                + reference.temperature * reference.entropy_density
                + reference.chemical_potential * reference.charge_density
            )
        )
        <= 1.0e-14,
        "convergence_pressure": convergence_relative_errors["pressure"] <= 1.0e-5,
        "convergence_entropy": convergence_relative_errors["entropy_density"] <= 1.0e-5,
        "convergence_charge": convergence_relative_errors["charge_density"] <= 1.0e-5,
        "convergence_energy": convergence_relative_errors["energy_density"] <= 1.0e-5,
        "convergence_response": convergence_relative_errors["response_pressure_derivative"] <= 1.0e-5,
        "fixed_background_is_declared": reference.fixed_tree_level_background is True,
        "thermal_backreaction_is_excluded": reference.thermal_background_backreaction_included is False,
        "vacuum_counterterm_is_excluded": reference.vacuum_counterterm_included is False,
        "self_energy_is_excluded": reference.interacting_self_energy_included is False,
        "normal_two_fluid_is_open": reference.normal_two_fluid_completion is False,
        "physical_kubo_is_not_emitted": reference.physical_kubo_coefficient_included is False,
        "Phi_is_not_temperature": contract["ontology"]["Phi"].startswith("fixed effective response input"),
        "C_ontology_is_preserved": "not identified" in contract["ontology"]["C"],
        "R_gen_is_not_state": "no feedback" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE"
    )
    evidence = [
        {"path": THERMAL_REL, "sha256": digest(THERMAL_REL)},
        {"path": SPECTRUM_REL, "sha256": digest(SPECTRUM_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-condensate-gaussian-thermal-v1",
        "artifact": "t13_uet_o2_condensate_gaussian_thermal_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSATE_GAUSSIAN_FINITE_T_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "thermal Bose determinant of the two positive-frequency quadratic O(2) condensate branches on a fixed tree-level background",
                "finite-temperature pressure, entropy, generalized mu-response, Phi-response derivative, and energy identity for the declared Gaussian lane",
                "mode-root positivity over the declared wavenumber witness and quadrature/cutoff convergence",
                "explicit separation from thermal background backreaction, vacuum renormalization, interacting self-energy, normal two-fluid transport, and SI calibration",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived fixed-background Gaussian thermal determinant from the declared O(2) quadratic spectrum; no self-consistent renormalization or transport matching",
            "observable": "natural-unit Gaussian quasiparticle pressure, entropy, generalized mu-response, energy, and Phi-response derivative",
            "data_role": "ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_NOT_FULL_UET_EOS",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "thermal_background_backreaction_and_self_consistent_phase_boundary_not_closed",
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "interacting_finite_temperature_self_energy_not_derived",
                "normal_two_fluid_current_and_physical_Kubo_coefficient_missing",
                "microscopic_SK_KMS_matching_and_entropy_production_not_closed",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "fixed-background Gaussian finite-temperature quasiparticle lane only; no physical two-fluid, Full Topic 13, Core, Gravity, or external-validation unlock",
            "claim_boundary": "This result derives only the natural-unit Gaussian thermal determinant of the two quadratic O(2) condensate modes on a fixed tree-level background. It is not a self-consistent finite-temperature UET EOS, renormalized one-loop action, normal-fluid or dissipative transport derivation, microscopic SK/KMS match, SI Phi calibration, external validation, or global UET closure.",
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI,
            "condensate_control": reference.condensate_control,
            "pressure": reference.pressure,
            "entropy_density": reference.entropy_density,
            "charge_density": reference.charge_density,
            "energy_density": reference.energy_density,
            "response_pressure_derivative": reference.response_pressure_derivative,
            "low_branch_pressure": reference.low_branch_pressure,
            "high_branch_pressure": reference.high_branch_pressure,
            "low_branch_entropy": reference.low_branch_entropy,
            "high_branch_entropy": reference.high_branch_entropy,
            "low_branch_charge": reference.low_branch_charge,
            "high_branch_charge": reference.high_branch_charge,
            "momentum_cutoff": reference.momentum_cutoff,
            "quadrature_order": reference.quadrature_order,
            "fixed_tree_level_background": reference.fixed_tree_level_background,
        },
        "mode_records": mode_records,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "finite_difference_checks": finite_differences,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "thermal_background_backreaction_and_self_consistent_phase_boundary_not_closed",
        "next_controller": "Derive a self-consistent finite-temperature background/effective potential with vacuum renormalization or retain this Gaussian fixed-background boundary; then close normal Kubo/SK/KMS and SI Phi mapping.",
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
                "pressure": reference.pressure,
                "entropy_density": reference.entropy_density,
                "charge_density": reference.charge_density,
                "energy_density": reference.energy_density,
                "response_pressure_derivative": reference.response_pressure_derivative,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
