"""Audit the state-matched finite-cutoff heat-current Kubo lane."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_heat_current_kubo_match import (  # noqa: E402
    HEAT_CURRENT_KUBO_MATCH_STATUS,
    heat_current_kubo_match_contract,
    heat_current_kubo_match_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_match_audit.json"
MODULE = ROOT / "docs/core/uet_o2_heat_current_kubo_match.py"
HEAT_MODULE = ROOT / "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py"
CONTINUUM_MODULE = ROOT / "docs/core/uet_o2_continuum_collision_operator.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = heat_current_kubo_match_state(0.22, 0.35, 0.15)
    contract = heat_current_kubo_match_contract()
    checks = {
        "normal_branch_is_explicit": state.branch == "normal",
        "same_operator_state_is_verified": state.same_operator_state_verified,
        "finite_cutoff_is_declared": state.finite_cutoff_boundary_declared,
        "dc_matrix_matches_covariant_heat_response": state.dc_matrix_relative_residual <= 1.0e-10,
        "dc_scalar_matches_kappa_natural": state.dc_scalar_relative_residual <= 1.0e-10,
        "response_is_positive_semidefinite": state.response_matrix_min_eigenvalue >= -1.0e-10,
        "source_is_projected_from_conserved_moments": state.source_constraint_residual <= 1.0e-10,
        "entropy_witness_matches_shared_operator": state.entropy_match_residual <= 1.0e-10,
        "retarded_response_is_finite": all(
            np.isfinite(value)
            for value in (*state.retarded_response_real, *state.retarded_response_imag)
        ),
        "retarded_zero_frequency_is_positive": state.dc_response_scalar > 0.0,
        "kms_ratio_is_resolved": state.kms_ratio_residual <= 1.0e-10,
        "fdt_is_resolved": state.fdt_residual <= 1.0e-10,
        "heat_current_match_is_completed": state.retarded_heat_current_match_completed,
        "physical_kubo_is_not_emitted": state.physical_kubo_coefficient_emitted is False,
        "continuum_limit_is_not_claimed": state.continuum_limit_completed is False,
        "numeric_alpha_is_not_emitted": state.numeric_alpha_Phi_K_emitted is False,
        "no_parameter_fitting": state.parameter_fitting_performed is False,
        "no_target_data": state.target_data_used is False,
        "xie_holdout_is_unread": state.xie_2026_accessed is False,
        "Phi_ontology_is_preserved": "not temperature" in contract["unit_contract"]["Phi"],
        "C_ontology_is_preserved": "not mass or charge" in contract["unit_contract"]["C"],
        "R_gen_ontology_is_preserved": "no backreaction" in contract["unit_contract"]["R_gen"],
        "R_obs_remains_separate": "separate observer" in contract["unit_contract"]["R_obs"],
        "physical_shortcuts_are_excluded": all(contract["excluded"].values()),
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = [key for key, value in checks.items() if not value]
    status = HEAT_CURRENT_KUBO_MATCH_STATUS if not failed else "BLOCKED_T13_HEAT_CURRENT_KUBO_MATCH"
    major_result = {
        "major_result_id": "T13_UET_O2_HEAT_CURRENT_KUBO_MATCH",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
        "what_is_closed": [
            "the declared Landau-frame heat-current source is projected with the same conserved collision operator used by the entropy lane",
            "the zero-frequency retarded heat-current matrix matches the existing finite-cutoff pseudoinverse response",
            "the scalar response matches kappa_natural at one declared normal state",
            "the shared operator satisfies the stated KMS/FDT and entropy consistency checks",
        ] if not failed else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": contract["data_role"],
        "evidence_artifacts": [
            {"path": "docs/core/uet_o2_heat_current_kubo_match.py", "sha256": sha256(MODULE)},
            {"path": "docs/core/uet_o2_covariant_entropy_heat_flux_balance.py", "sha256": sha256(HEAT_MODULE)},
            {"path": "docs/core/uet_o2_continuum_collision_operator.py", "sha256": sha256(CONTINUUM_MODULE)},
        ],
        "verification_status": status,
        "open_blockers": [
            "continuum_limit_missing",
            "loop_renormalized_off_shell_self_energy_missing",
            "physical_heat_Kubo_coefficient_record_missing",
            "finite_temperature_condensed_two_fluid_completion_missing",
            "dimensional_Phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        ] if not failed else ["heat-current Kubo matching checks failed"],
        "dependency_unlocked": (
            "state-matched finite-cutoff natural-unit heat-current Kubo lane only; "
            "no continuum, SI, physical transport, alpha, TTG, Core, or Full Topic 13 unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    artifact = {
        "schema_version": "t13-uet-o2-heat-current-kubo-match-v1",
        "artifact": "t13_uet_o2_heat_current_kubo_match_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "contract": contract,
        "state": asdict(state),
        "checks": checks,
        "failed_checks": failed,
        "physical_kubo_coefficient_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "continuum_limit_completed": False,
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
        "controlling_blocker": "continuum_limit_and_physical_heat_Kubo_promotion_missing",
        "next_controller": (
            "complete the continuum and renormalized retarded heat-current match, "
            "then source-lock physical units and uncertainty without promoting the natural lane"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": failed, "kappa_natural": state.kappa_natural}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
