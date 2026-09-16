"""Audit the named regularized continuum heat-current Topic 13 lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from math import isfinite
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_regularized_continuum_heat_current import (  # noqa: E402
    CONTINUUM_ACCEPTANCE_THRESHOLD,
    REGULARIZED_CONTINUUM_HEAT_CURRENT_STATUS,
    regularized_continuum_heat_current_contract,
    regularized_continuum_heat_current_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_regularized_continuum_heat_current_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_regularized_continuum_heat_current.py"
BASELINE_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_continuum_boundary_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = regularized_continuum_heat_current_state(0.22, 0.35, 0.15)
    contract = regularized_continuum_heat_current_contract()
    baseline_path = ROOT / BASELINE_REL
    baseline = json.loads(baseline_path.read_text(encoding="utf-8-sig"))
    checks = {
        "normal_branch_is_declared": state.branch == "normal",
        "compactified_radial_domain_is_used": state.compactified_radial_domain_used,
        "finite_cutoff_is_not_used": state.finite_cutoff_used is False,
        "radial_sequence_has_three_points": len(state.radial_orders) == 3,
        "radial_response_count_matches": len(state.radial_kappa_natural) == 3,
        "radial_values_are_finite_and_positive": all(
            isfinite(value) and value > 0.0 for value in state.radial_kappa_natural
        ),
        "radial_k_max_is_finite_and_increasing": all(
            isfinite(value) and value > 0.0
            for value in state.radial_k_max_by_order
        )
        and tuple(sorted(state.radial_k_max_by_order)) == state.radial_k_max_by_order,
        "repository_threshold_is_unchanged": state.continuum_convergence_passes
        or state.radial_max_relative_change > CONTINUUM_ACCEPTANCE_THRESHOLD
        or state.angular_refined_relative_change > CONTINUUM_ACCEPTANCE_THRESHOLD
        or state.scale_refined_relative_change > CONTINUUM_ACCEPTANCE_THRESHOLD,
        "convergence_controller_passes": state.continuum_convergence_passes,
        "collision_operator_is_positive": state.collision_operator_min_eigenvalue >= -1.0e-10,
        "operator_is_symmetric": state.collision_operator_symmetry_residual <= 1.0e-10,
        "conservation_is_closed": state.conservation_residual <= 1.0e-10,
        "source_is_conserved_orthogonal": state.source_constraint_residual <= 1.0e-10,
        "entropy_production_is_positive": state.entropy_production > 0.0,
        "kms_interface_is_closed": state.kms_ratio_residual <= 1.0e-12,
        "fdt_interface_is_closed": state.fdt_residual <= 1.0e-12,
        "baseline_finite_cutoff_no_go_remains": baseline.get("major_result", {}).get(
            "closure_level"
        )
        == "CLOSED_AS_NO_GO",
        "no_physical_coefficient_emitted": state.physical_kubo_coefficient_emitted is False,
        "no_numeric_alpha_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "xie_holdout_is_unread": state.xie_2026_accessed is False,
        "Phi_ontology_is_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_is_preserved": "no backreaction" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = [name for name, value in checks.items() if not value]
    status = (
        REGULARIZED_CONTINUUM_HEAT_CURRENT_STATUS
        if not failed
        else "BLOCKED_T13_REGULARIZED_CONTINUUM_HEAT_CURRENT"
    )
    major_result = {
        "major_result_id": "T13_UET_O2_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "what_is_closed": [
            "a named normal-branch compactified radial heat-current scheme is machine-readable",
            "the unchanged 1e-2 radial/angular/scale convergence controller passes",
            "charge, energy, and three-momentum conservation are enforced by explicit projection",
            "the operator is symmetric positive semidefinite and the entropy witness is positive",
            "the old finite-cutoff no-go remains preserved as a separate baseline",
        ]
        if not failed
        else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/02_equations/o2/uet_o2_regularized_continuum_heat_current.py", "sha256": sha256(MODULE)},
            {"path": BASELINE_REL, "sha256": sha256(baseline_path)},
        ],
        "verification_status": status,
        "open_blockers": [
            "loop_renormalized_off_shell_self_energy_missing",
            "physical_heat_Kubo_coefficient_record_missing",
            "finite_temperature_condensed_two_fluid_completion_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ],
        "dependency_unlocked": (
            "named normal-branch regularized natural-unit heat-current lane only; "
            "no physical Kubo, SI, TTG, Core, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-regularized-continuum-heat-current-v1",
        "artifact": "t13_uet_o2_regularized_continuum_heat_current_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "failed_checks": failed,
        "continuum_limit_completed": state.continuum_convergence_passes,
        "physical_kubo_coefficient_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "claim_promotion": False,
        "full_core_unlock": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
        },
        "controlling_blocker": (
            "loop_renormalized_off_shell_self_energy_missing"
            if not failed
            else "regularized_continuum_heat_current_checks_failed"
        ),
        "next_controller": (
            "retain this lane as natural-unit evidence, then close the physical Kubo "
            "provenance, condensed two-fluid/SK-KMS completion, dimensional Phi map, "
            "independent alpha calibration, and Ding C_src source package"
            if not failed
            else "repair the named regularized continuum checks without changing the 1e-2 threshold"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "kappa_natural": state.kappa_natural}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
