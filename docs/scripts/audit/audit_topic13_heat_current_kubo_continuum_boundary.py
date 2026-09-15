"""Audit the scoped continuum boundary of the Topic 13 heat-current lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_heat_current_kubo_continuum_boundary import (  # noqa: E402
    CONTINUUM_ACCEPTANCE_THRESHOLD,
    HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS,
    heat_current_kubo_continuum_boundary_contract,
    heat_current_kubo_continuum_boundary_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_continuum_boundary_audit.json"
MODULE = ROOT / "docs/core/uet_o2_heat_current_kubo_continuum_boundary.py"
HEAT_MATCH_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_match_audit.json"
COLLISION_MODULE = ROOT / "docs/core/uet_o2_continuum_collision_operator.py"
BALANCE_MODULE = ROOT / "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = heat_current_kubo_continuum_boundary_state(0.22, 0.35, 0.15)
    contract = heat_current_kubo_continuum_boundary_contract()
    heat_match_path = ROOT / HEAT_MATCH_REL
    heat_match = json.loads(heat_match_path.read_text(encoding="utf-8-sig"))
    checks = {
        "cutoff_sequence_has_four_points": len(state.cutoff_factors) == 4,
        "cutoff_response_count_matches": len(state.cutoff_kappa_natural) == 4,
        "adjacent_change_count_is_three": len(state.cutoff_relative_changes) == 3,
        "responses_are_finite": all(
            value == value
            and abs(float(value)) != float("inf")
            for value in (*state.cutoff_kappa_natural, *state.cutoff_relative_changes)
        ),
        "responses_are_positive": all(value > 0.0 for value in state.cutoff_kappa_natural),
        "repository_threshold_is_unchanged": state.acceptance_threshold
        == CONTINUUM_ACCEPTANCE_THRESHOLD
        == 1.0e-2,
        "cutoff_sequence_fails_continuum_acceptance": state.cutoff_sequence_fails_acceptance,
        "independent_refinement_fails_acceptance": state.refinement_fails_acceptance,
        "shared_operator_family_is_declared": state.operator_family_is_shared,
        "finite_cutoff_boundary_is_declared": state.finite_cutoff_boundary_declared,
        "finite_cutoff_heat_match_is_passing": heat_match.get("status")
        == "PASS_ACTION_MATCHED_FINITE_CUTOFF_HEAT_CURRENT_KUBO_LANE",
        "finite_cutoff_heat_match_is_lane_only": heat_match.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE",
        "no_extrapolated_response_emitted": state.extrapolated_response_emitted is False,
        "no_physical_coefficient_emitted": state.physical_kubo_coefficient_emitted is False,
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
        HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS
        if not failed
        else "BLOCKED_T13_HEAT_CURRENT_CONTINUUM_BOUNDARY"
    )
    major_result = {
        "major_result_id": "T13_UET_O2_HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_AS_NO_GO" if not failed else "OPEN",
        "what_is_closed": [
            "the heat-current cutoff response sequence is machine-readable and finite",
            "the repository continuum-controller threshold 1e-2 is applied without adjustment",
            "the declared cutoff sequence fails continuum promotion",
            "an independent radial/quadrature refinement also fails continuum promotion",
            "the finite-cutoff heat-current Kubo match remains separately bounded and is not relabeled as a continuum result",
        ] if not failed else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/uet_o2_heat_current_kubo_continuum_boundary.py", "sha256": sha256(MODULE)},
            {"path": HEAT_MATCH_REL, "sha256": sha256(heat_match_path)},
            {"path": "docs/core/uet_o2_continuum_collision_operator.py", "sha256": sha256(COLLISION_MODULE)},
            {"path": "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py", "sha256": sha256(BALANCE_MODULE)},
        ],
        "verification_status": status,
        "open_blockers": [
            "new_regularized_continuum_heat_current_scheme_missing",
            "loop_renormalized_off_shell_self_energy_missing",
            "physical_heat_Kubo_coefficient_record_missing",
            "finite_temperature_condensed_two_fluid_completion_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ] if not failed else ["heat-current continuum boundary checks failed"],
        "dependency_unlocked": (
            "scoped no-go for continuum promotion of the declared heat-current discretization; "
            "finite-cutoff formal Kubo lane remains available, but no continuum, physical Kubo, SI, TTG, Core, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-heat-current-kubo-continuum-boundary-v1",
        "artifact": "t13_uet_o2_heat_current_kubo_continuum_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "failed_checks": failed,
        "continuum_limit_completed": False,
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
        "controlling_blocker": "heat_current_continuum_scheme_no_go",
        "next_controller": (
            "replace or analytically control the declared heat-current cutoff/order dependence, "
            "then rerun the unchanged 1e-2 convergence gate before any physical Kubo or SI promotion"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": failed,
                "cutoff_maximum_relative_change": state.cutoff_maximum_relative_change,
                "baseline_to_refined_relative_change": state.baseline_to_refined_relative_change,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
