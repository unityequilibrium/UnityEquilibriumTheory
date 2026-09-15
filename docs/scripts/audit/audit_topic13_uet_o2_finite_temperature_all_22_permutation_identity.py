"""Audit the equal-mass identity for all allowed 2<->2 sunset cuts."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_temperature_all_22_permutation_identity import (  # noqa: E402
    ALL_22_PERMUTATION_IDENTITY_STATUS,
    all_22_permutation_identity_contract,
    all_22_permutation_identity_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_all_22_permutation_identity_audit.json"
MODULE = ROOT / "docs/core/uet_o2_finite_temperature_all_22_permutation_identity.py"


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = all_22_permutation_identity_state(0.35, 0.5, 0.8)
    contract = all_22_permutation_identity_contract()
    first_grid_maps = tuple(
        point.relabeling_to_reference
        for point in state.points
        if point.invariant_s == state.invariant_grid[0]
    )
    checks = {
        "status": state.all_three_permutation_identity_completed,
        "three_allowed_permutations": state.signs
        == ((-1, 1, 1), (1, -1, 1), (1, 1, -1)),
        "reference_maps": first_grid_maps == ((2, 3, 1), (1, 3, 2), (1, 2, 3)),
        "unit_jacobians": all(
            point.relabeling_jacobian_absolute == 1.0 for point in state.points
        ),
        "response_identity": state.max_response_identity_residual == 0.0,
        "action_graph_weight": state.action_level_multiplicity_contract_preserved,
        "kms_convergence": state.max_kms_log_ratio_residual <= 2.0e-2,
        "fdt_convergence": state.max_fdt_residual <= 2.0e-2,
        "pv_inner_convergence": state.max_pv_inner_convergence_residual <= 2.0e-2,
        "pv_outer_convergence": state.max_pv_outer_convergence_residual <= 2.0e-2,
        "no_fit": not state.parameter_fitting_performed,
        "no_target_data": not state.target_data_used,
        "no_holdout": not state.xie_2026_accessed,
        "full_1pi_still_open": not state.complete_off_shell_finite_temperature_1pi_self_energy_completed,
        "physical_renormalization_still_open": not state.unique_physical_renormalization_scheme_match_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
    }
    failed = [name for name, passed in checks.items() if not passed]
    artifact = {
        "schema_version": "t13-uet-o2-finite-t-all-22-permutation-identity-audit-v1",
        "artifact": "t13_uet_o2_finite_temperature_all_22_permutation_identity_audit",
        "status": ALL_22_PERMUTATION_IDENTITY_STATUS
        if not failed
        else "BLOCKED_" + ALL_22_PERMUTATION_IDENTITY_STATUS,
        "failed_checks": failed,
        "checks": checks,
        "contract": contract,
        "state": asdict(state),
        "evidence": {
            "module": {"path": str(MODULE.relative_to(ROOT)), "sha256": _hash(MODULE)},
            "data_role": state.data_role,
            "holdout_accessed": state.xie_2026_accessed,
            "parameter_fitting_performed": state.parameter_fitting_performed,
            "target_data_used": state.target_data_used,
        },
        "major_result": {
            "major_result_id": "T13_UET_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if not failed else "OPEN",
            "what_is_closed": [
                "all three allowed equal-mass 2<->2 signed-cut permutations",
                "unit-Jacobian dummy-line relabeling to the reference kernel",
                "action-level aggregate graph weight 3*(1/6)=1/2",
            ],
            "equation_or_mapping": contract["equations"],
            "units": contract["unit_contract"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": state.data_role,
            "evidence_artifacts": [
                str(MODULE.relative_to(ROOT)),
                "docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_all_22_permutation_identity.py",
                "docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_all_22_permutation_identity_audit.json",
            ],
            "verification_status": ALL_22_PERMUTATION_IDENTITY_STATUS
            if not failed
            else "BLOCKED",
            "open_blockers": [
                "complete_off_shell_all_channel_1pi_missing",
                "physical_renormalization_anchor_missing",
                "physical_kubo_coefficient_missing",
                "dimensional_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "dependency_unlocked": "equal-mass 2<->2 permutation identity and action-level coverage only",
            "claim_boundary": contract["claim_boundary"],
        },
    }
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "failed_checks": failed,
                "artifact": str(OUT.relative_to(ROOT)),
                "max_response_identity_residual": state.max_response_identity_residual,
                "max_pv_inner_convergence_residual": state.max_pv_inner_convergence_residual,
                "max_pv_outer_convergence_residual": state.max_pv_outer_convergence_residual,
            },
            indent=2,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
