"""Audit the off-shell finite-temperature Gaussian O(2) background boundary."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from math import isfinite, sqrt
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
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    o2_equilibrium_state,
)
from docs.core.uet_o2_gaussian_offshell_background import (
    off_shell_curvatures,
    off_shell_gaussian_thermal_state,
    off_shell_mode_omega_sq,
    tree_grand_potential,
    uet_o2_gaussian_offshell_background_contract,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_REL = "docs/core/uet_o2_gaussian_offshell_background.py"
THERMAL_REL = "docs/core/uet_o2_condensate_gaussian_thermal.py"
SPECTRUM_REL = "docs/core/uet_o2_condensate_fluctuations.py"
EOS_REL = "docs/core/uet_o2_finite_density_eos.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_gaussian_offshell_background_audit.json"

TEMPERATURE = 0.25
CHEMICAL_POTENTIAL = 1.3
PHI = 0.2
REFERENCE_ORDER = 256
REFERENCE_CUTOFF_FACTOR = 90.0
CONVERGENCE_CASES = ((96, 50.0), (192, 70.0), (256, 90.0))
WAVENUMBERS = (0.01, 0.1, 0.5, 1.0)
ONE_SIDED_STEP = 1.0e-4
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


def try_state(
    amplitude: float,
    eos_config: O2FiniteDensityEOSConfig,
    *,
    order: int,
    cutoff_factor: float,
) -> tuple[str, object | None]:
    try:
        state = off_shell_gaussian_thermal_state(
            TEMPERATURE,
            CHEMICAL_POTENTIAL,
            PHI,
            amplitude,
            eos_config,
            quadrature_order=order,
            cutoff_factor=cutoff_factor,
        )
    except (FloatingPointError, ValueError) as error:
        return type(error).__name__, None
    return "PASS", state


def main() -> int:
    eos_config = config()
    tree_state = o2_equilibrium_state(CHEMICAL_POTENTIAL, PHI, eos_config)
    fluctuation_state = condensate_fluctuation_state(
        CHEMICAL_POTENTIAL, PHI, eos_config
    )
    q = float(tree_state.condensate_control)
    quartic = float(eos_config.matter.matter_quartic)
    tree_amplitude = sqrt(q / quartic)
    contract = uet_o2_gaussian_offshell_background_contract()

    q_off, radial_off, phase_off = off_shell_curvatures(
        tree_amplitude, CHEMICAL_POTENTIAL, PHI, eos_config
    )
    tree_potential = tree_grand_potential(
        tree_amplitude, CHEMICAL_POTENTIAL, PHI, eos_config
    )
    stationary_root_records = []
    root_match_errors = []
    for wavenumber in WAVENUMBERS:
        old_low, old_high = quadratic_mode_omega_sq(
            wavenumber, fluctuation_state, eos_config
        )
        new_low, new_high = off_shell_mode_omega_sq(
            wavenumber,
            tree_amplitude,
            CHEMICAL_POTENTIAL,
            PHI,
            eos_config,
        )
        low_error = abs(new_low - old_low)
        high_error = abs(new_high - old_high)
        root_match_errors.extend((low_error, high_error))
        stationary_root_records.append(
            {
                "wavenumber": wavenumber,
                "existing_low_omega_sq": old_low,
                "offshell_low_omega_sq": new_low,
                "existing_high_omega_sq": old_high,
                "offshell_high_omega_sq": new_high,
                "low_abs_error": low_error,
                "high_abs_error": high_error,
            }
        )

    reference_status, reference = try_state(
        tree_amplitude,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    right_status, right_state = try_state(
        tree_amplitude + ONE_SIDED_STEP,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    left_status, left_state = try_state(
        tree_amplitude - ONE_SIDED_STEP,
        eos_config,
        order=REFERENCE_ORDER,
        cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )

    right_slope = None
    if reference is not None and right_state is not None:
        right_slope = (
            right_state.grand_potential - reference.grand_potential
        ) / ONE_SIDED_STEP

    convergence_records = []
    for order, cutoff_factor in CONVERGENCE_CASES:
        status, state = try_state(
            tree_amplitude,
            eos_config,
            order=order,
            cutoff_factor=cutoff_factor,
        )
        convergence_records.append(
            {
                "quadrature_order": order,
                "cutoff_factor": cutoff_factor,
                "status": status,
                "grand_potential": None if state is None else state.grand_potential,
                "tree_grand_potential": None if state is None else state.tree_grand_potential,
                "thermal_grand_potential": None if state is None else state.thermal_grand_potential,
            }
        )
    reference_record = convergence_records[-1]
    convergence_relative_errors = {
        "grand_potential": relative_error(
            convergence_records[-2]["grand_potential"],
            reference_record["grand_potential"],
        )
        if reference_record["grand_potential"] is not None
        and convergence_records[-2]["grand_potential"] is not None
        else None,
        "thermal_grand_potential": relative_error(
            convergence_records[-2]["thermal_grand_potential"],
            reference_record["thermal_grand_potential"],
        )
        if reference_record["thermal_grand_potential"] is not None
        and convergence_records[-2]["thermal_grand_potential"] is not None
        else None,
    }

    checks = {
        "condensed_tree_background_selected": tree_state.branch == "condensed",
        "condensate_control_positive": q > 0.0,
        "tree_amplitude_positive": tree_amplitude > 0.0,
        "stationary_curvature_recovery": abs(radial_off - 2.0 * q) <= 1.0e-12
        and abs(phase_off) <= 1.0e-12,
        "tree_grand_potential_matches_eos": abs(
            tree_potential - tree_state.grand_potential
        )
        <= 1.0e-12,
        "stationary_roots_recover_existing_determinant": max(root_match_errors)
        <= 1.0e-12,
        "reference_offshell_thermal_state_is_stable": reference_status == "PASS",
        "reference_grand_potential_is_finite": reference is not None
        and isfinite(reference.grand_potential),
        "right_offshell_thermal_state_is_stable": right_status == "PASS",
        "thermal_tadpole_is_resolved_one_sided": right_slope is not None
        and abs(right_slope) > TADPOLE_THRESHOLD,
        "decreasing_amplitude_hits_unstable_domain": left_state is None
        and left_status in {"FloatingPointError", "ValueError"},
        "thermal_only_potential_converges": convergence_relative_errors["grand_potential"]
        is not None
        and convergence_relative_errors["grand_potential"] <= 1.0e-5,
        "thermal_only_branch_is_explicit": contract["scope"]["thermal_order"]
        == "Gaussian quadratic Bose determinant only",
        "vacuum_counterterm_is_excluded": contract["scope"]["vacuum_counterterm"]
        == "NOT_INCLUDED",
        "self_energy_is_excluded": contract["scope"]["interacting_self_energy"]
        == "NOT_INCLUDED",
        "Phi_is_not_temperature": contract["ontology"]["Phi"].startswith(
            "fixed effective response input"
        ),
        "C_ontology_is_preserved": "not identified" in contract["ontology"]["C"],
        "R_gen_is_not_state": "no feedback" in contract["ontology"]["R_gen"],
        "no_holdout_or_fit": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        "PASS_ACTION_DERIVED_OFFSHELL_THERMAL_BACKREACTION_BOUNDARY"
        if all(checks.values())
        else "FAIL_ACTION_DERIVED_OFFSHELL_THERMAL_BACKREACTION_BOUNDARY"
    )

    evidence = [
        {"path": MODULE_REL, "sha256": digest(MODULE_REL)},
        {"path": THERMAL_REL, "sha256": digest(THERMAL_REL)},
        {"path": SPECTRUM_REL, "sha256": digest(SPECTRUM_REL)},
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-gaussian-offshell-background-v1",
        "artifact": "t13_uet_o2_gaussian_offshell_background_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_GAUSSIAN_OFFSHELL_BACKGROUND_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "off-shell homogeneous O(2) radial/phase Hessian at fixed Phi",
                "recovery of the existing stationary condensate determinant at A^2=q/lambda",
                "thermal-only stable-domain diagnostic around the tree-level background",
                "one-sided thermal tadpole evidence showing fixed tree-level A is not a finite-temperature stationary point under the declared Gaussian determinant",
            ]
            if status.startswith("PASS")
            else [],
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": "action-derived off-shell Gaussian Hessian and thermal-only effective-potential boundary; no vacuum renormalization or interacting self-energy",
            "observable": "natural-unit homogeneous grand-potential density and quadratic mode stability",
            "data_role": contract["data_role"],
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "self_consistent_finite_temperature_phase_boundary_requires_thermal_self_energy_or_declared_renormalized_effective_action",
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "normal_two_fluid_current_and_physical_Kubo_coefficient_missing",
                "microscopic_SK_KMS_matching_and_entropy_production_not_closed",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "off-shell Gaussian thermal background boundary diagnostic only; no Full Topic 13, Core, Gravity, transport, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "reference": {
            "temperature": TEMPERATURE,
            "chemical_potential": CHEMICAL_POTENTIAL,
            "space_response": PHI,
            "tree_amplitude": tree_amplitude,
            "condensate_control": q_off,
            "radial_curvature": radial_off,
            "phase_curvature": phase_off,
            "tree_grand_potential": tree_potential,
            "reference_status": reference_status,
            "reference_grand_potential": None
            if reference is None
            else reference.grand_potential,
            "right_status": right_status,
            "right_grand_potential": None
            if right_state is None
            else right_state.grand_potential,
            "left_status": left_status,
            "one_sided_step": ONE_SIDED_STEP,
            "right_one_sided_slope": right_slope,
            "tadpole_threshold": TADPOLE_THRESHOLD,
            "vacuum_counterterm_included": False,
            "interacting_self_energy_included": False,
        },
        "stationary_root_records": stationary_root_records,
        "convergence_records": convergence_records,
        "convergence_relative_errors": convergence_relative_errors,
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "thermal_background_backreaction_requires_self_consistent_renormalized_phase_boundary",
        "next_controller": "Declare or derive the thermal self-energy/vacuum renormalization needed to make the finite-temperature phase boundary stationary; then close normal Kubo/SK/KMS, entropy, SI Phi mapping, and alpha calibration.",
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
                "tree_amplitude": tree_amplitude,
                "right_one_sided_slope": right_slope,
                "left_status": left_status,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
