"""Audit the action-derived condensed relative-flow collision lane."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_condensed_relative_flow_collision import (
    CONDENSED_RELATIVE_FLOW_STATUS,
    condensed_relative_flow_collision_contract,
    condensed_relative_flow_collision_state,
)


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensed_relative_flow_collision_audit.json"
MODULE = ROOT / "docs/core/uet_o2_condensed_relative_flow_collision.py"
TEST = ROOT / "docs/core/test/test_topic13_uet_o2_condensed_relative_flow_collision.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite(values: object) -> bool:
    return bool(np.all(np.isfinite(np.asarray(values, dtype=float))))


def main() -> int:
    reference = condensed_relative_flow_collision_state(
        0.2,
        1.28,
        0.15,
        radial_order=32,
        angular_order=16,
        cutoff_factor=20.0,
    )
    refined = condensed_relative_flow_collision_state(
        0.2,
        1.28,
        0.15,
        radial_order=48,
        angular_order=24,
        cutoff_factor=24.0,
    )
    low_temperature = condensed_relative_flow_collision_state(
        0.06,
        1.28,
        0.15,
        radial_order=32,
        angular_order=16,
        cutoff_factor=20.0,
    )
    reference_matrix = np.asarray(reference.collision_operator, dtype=float)
    refined_matrix = np.asarray(refined.collision_operator, dtype=float)
    reference_eigenvalues = np.linalg.eigvalsh(reference_matrix)
    refined_eigenvalues = np.linalg.eigvalsh(refined_matrix)
    refinement = abs(
        refined.dc_relative_response - reference.dc_relative_response
    ) / max(abs(reference.dc_relative_response), 1.0e-300)
    checks = {
        "condensed_branch_is_explicit": reference.branch == "condensed" and refined.branch == "condensed",
        "tree_scales_are_finite": _finite(
            [
                reference.effective_mass,
                reference.condensate_amplitude,
                reference.sound_speed_sq,
                reference.tree_radial_screening_sq,
            ]
        ),
        "mode_susceptibilities_are_positive": all(
            value > 0.0 for value in (*reference.mode_susceptibility, *refined.mode_susceptibility)
        ),
        "mode_rates_are_positive": all(
            value > 0.0 for value in (*reference.mode_rate, *refined.mode_rate)
        ),
        "collision_operator_is_symmetric": max(
            reference.symmetric_kernel_residual, refined.symmetric_kernel_residual
        )
        <= 1.0e-12,
        "collision_operator_is_positive_semidefinite": (
            float(np.min(reference_eigenvalues)) >= -1.0e-12
            and float(np.min(refined_eigenvalues)) >= -1.0e-12
        ),
        "common_flow_zero_mode_is_conserved": max(
            reference.common_flow_conservation_residual,
            refined.common_flow_conservation_residual,
        )
        <= 1.0e-12,
        "relative_source_has_no_common_mode": max(
            reference.source_common_mode_residual,
            refined.source_common_mode_residual,
        )
        <= 1.0e-12,
        "dc_response_is_positive": reference.dc_relative_response > 0.0 and refined.dc_relative_response > 0.0,
        "entropy_production_is_positive": reference.entropy_production_at_unit_force > 0.0 and refined.entropy_production_at_unit_force > 0.0,
        "retarded_spectral_density_is_nonnegative": all(
            value >= -1.0e-12 for value in refined.spectral_density
        ),
        "positive_frequency_retarded_imaginary_part_is_nonnegative": all(
            value >= -1.0e-12 for value in refined.retarded_response_imag[1:]
        ),
        "kms_interface_closes": refined.kms_residual <= 1.0e-10,
        "fdt_interface_closes": refined.fdt_residual <= 1.0e-10,
        "radial_and_angular_refinement_is_bounded": refinement <= 1.0e-3,
        "low_temperature_state_remains_finite": _finite(
            [
                low_temperature.relative_collision_rate,
                low_temperature.dc_relative_response,
                low_temperature.entropy_production_at_unit_force,
            ]
        ),
        "physical_kubo_is_not_emitted": not refined.physical_kubo_coefficient_emitted,
        "alpha_is_not_emitted": not refined.numeric_alpha_phi_k_emitted,
        "no_fit_target_or_holdout": (
            not refined.parameter_fitting_performed
            and not refined.target_data_used
            and not refined.xie_2026_accessed
        ),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = (
        CONDENSED_RELATIVE_FLOW_STATUS
        if all(checks.values())
        else "FAIL_T13_CONDENSED_RELATIVE_FLOW_COLLISION_AUDIT"
    )
    contract = condensed_relative_flow_collision_contract()
    report = {
        "schema_version": "t13-uet-o2-condensed-relative-flow-collision-v1",
        "artifact": "t13_uet_o2_condensed_relative_flow_collision_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSED_RELATIVE_FLOW_COLLISION_KERNEL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "the existing O(2) condensate scales define a positive screened contact channel",
                "the mode-space relative-flow operator is symmetric positive semidefinite with a common-flow zero mode",
                "the declared condensed state has a finite positive DC relative-flow response and entropy production",
                "the relative-mode retarded KMS/FDT interface passes the declared algebraic checks",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": str(MODULE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(MODULE)},
                {"path": str(TEST.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(TEST)},
            ],
            "verification_status": status,
            "open_blockers": [
                "complete_microscopic_condensed_vertex_and_all_scattering_channels_missing",
                "continuum_renormalized_physical_Kubo_coefficient_missing",
                "complete_two_fluid_constitutive_tensor_missing",
                "dimensional_phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            ],
            "dependency_unlocked": "condensed relative-flow collision kernel lane only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "contract": contract,
        "reference_state": reference.__dict__,
        "refined_state": refined.__dict__,
        "low_temperature_state": low_temperature.__dict__,
        "metrics": {
            "refinement_relative_change": refinement,
            "reference_min_eigenvalue": float(np.min(reference_eigenvalues)),
            "refined_min_eigenvalue": float(np.min(refined_eigenvalues)),
        },
        "checks": checks,
        "failed_checks": [key for key, value in checks.items() if not value],
        "physical_kubo_coefficient_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "claim_promotion": False,
        "controlling_blocker": "continuum_renormalized_physical_Kubo_coefficient_missing",
        "next_controller": "Complete the microscopic condensed vertex/continuum match or acquire a state-matched retarded correlator; keep this natural-unit kernel separate from physical Kubo and alpha calibration.",
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": report["failed_checks"],
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "refinement_relative_change": refinement,
            },
            indent=2,
        )
    )
    return 0 if status == CONDENSED_RELATIVE_FLOW_STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
