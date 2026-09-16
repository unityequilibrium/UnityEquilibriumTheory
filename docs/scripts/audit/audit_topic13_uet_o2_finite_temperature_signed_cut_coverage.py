"""Audit the finite-temperature O(2) signed-cut kinematic taxonomy."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_finite_temperature_signed_cut_coverage import (  # noqa: E402
    CURRENT_LABELED_SCATTERING_SIGNS,
    SCATTERING_SIGN_PERMUTATIONS,
    SIGNED_CUT_COVERAGE_STATUS,
    finite_temperature_signed_cut_coverage_contract,
    finite_temperature_signed_cut_coverage_state,
)


OUT = ROOT / (
    "docs/core/artifacts/"
    "t13_uet_o2_finite_temperature_signed_cut_coverage_audit.json"
)
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_signed_cut_coverage.py"
SCATTERING = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_scattering_sk_kms.py"
SUNSET = ROOT / "docs/core/02_equations/o2/uet_o2_finite_temperature_sunset_sk_kms.py"
ACTION = ROOT / "docs/core/02_equations/o2/uet_o2_action_1pi_sunset_tensor.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = finite_temperature_signed_cut_coverage_state(
        external_energy=math.sqrt(5.0),
        mass_squared=0.5,
    )
    contract = finite_temperature_signed_cut_coverage_contract()
    expected_allowed = {
        (-1, 1, 1),
        (1, -1, 1),
        (1, 1, -1),
        (1, 1, 1),
    }
    checks = {
        "all_eight_sign_assignments_enumerated": (
            state.all_sign_assignments_enumerated
            and len(state.assignments) == 8
        ),
        "allowed_sign_assignments_match_taxonomy": (
            set(state.allowed_signs) == expected_allowed
            and state.allowed_assignment_count == 4
        ),
        "one_to_three_threshold_is_checked": (
            state.one_to_three_threshold_checked
            and state.one_to_three_allowed_assignment_count == 1
        ),
        "all_three_two_to_two_permutations_are_enumerated": (
            state.two_to_two_permutations_enumerated
            and tuple(
                assignment.signs
                for assignment in state.assignments
                if assignment.process_class == "2<->2"
            )
            == SCATTERING_SIGN_PERMUTATIONS
            and len(SCATTERING_SIGN_PERMUTATIONS) == 3
        ),
        "current_module_is_one_labeled_scattering_pattern": (
            state.current_labeled_scattering_signs
            == CURRENT_LABELED_SCATTERING_SIGNS
            and state.current_labeled_scattering_assignment_count == 1
        ),
        "missing_scattering_permutations_are_explicit": (
            state.missing_scattering_permutation_count == 2
        ),
        "forbidden_one_plus_two_minus_assignments_are_explicit": (
            state.forbidden_one_plus_two_minus_count == 3
        ),
        "kinematic_taxonomy_completed": (
            state.signed_cut_kinematic_taxonomy_completed
        ),
        "action_level_multiplicity_remains_open": (
            not state.action_level_cut_multiplicity_completed
        ),
        "full_finite_temperature_1pi_remains_open": (
            not state.full_finite_temperature_1pi_self_energy_completed
        ),
        "all_finite_temperature_sunset_channels_remain_open": (
            not state.all_finite_temperature_sunset_channels_completed
        ),
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_data": not state.target_data_used,
        "xie_2026_not_accessed": not state.xie_2026_accessed,
        "contract_excludes_action_multiplicity": contract["excluded"][
            "action_level_cut_multiplicity"
        ],
        "contract_excludes_full_1pi": contract["excluded"][
            "complete_finite_temperature_1pi_self_energy"
        ],
        "contract_excludes_holdout": contract["excluded"]["Xie_2026_holdout"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed_checks = [key for key, value in checks.items() if not value]
    status = SIGNED_CUT_COVERAGE_STATUS if not failed_checks else (
        "FAIL_ACTION_DERIVED_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE"
    )
    evidence = [
        {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
        for path in (MODULE, SCATTERING, SUNSET, ACTION)
    ]
    closure_level = "CLOSED_FOR_LANE" if not failed_checks else "OPEN"
    payload = {
        "schema_version": "t13-uet-o2-finite-t-signed-cut-coverage-v1",
        "artifact": "t13_uet_o2_finite_temperature_signed_cut_coverage_audit",
        "generated_at": str(date.today()),
        "status": status,
        "major_result_id": (
            "T13_UET_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE"
        ),
        "closure_level": closure_level,
        "state": asdict(state),
        "contract": contract,
        "checks": checks,
        "failed_checks": failed_checks,
        "full_core_unlock": False,
        "claim_promotion": False,
        "evidence_artifacts": evidence,
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "controlling_blocker": (
            "action_level_signed_cut_multiplicity_and_complete_finite_temperature_"
            "1pi_missing"
        ),
        "next_action": (
            "Derive the action-level cut multiplicity for the three 2<->2 sign "
            "permutations and connect it to the complete retarded/advanced/Keldysh "
            "1PI object before physical renormalization or transport admission."
        ),
        "claim_boundary": contract["claim_boundary"],
    }
    payload["major_result"] = {
        "major_result_id": payload["major_result_id"],
        "topic": "Topic 13 Thermodynamic Bridge",
        "closure_level": closure_level,
        "what_is_closed": [
            "all eight positive-external-energy equal-mass signed-cut assignments",
            "one-to-three threshold classification",
            "three kinematically allowed two-to-two sign permutations",
            "three forbidden one-plus/two-minus assignments and the all-negative assignment",
            "explicit identification that the current scattering module is labeled to one of three 2-to-2 patterns",
        ] if not failed_checks else [],
        "equation_or_mapping": contract["equations"],
        "units": contract["unit_contract"],
        "derivation_class": contract["derivation_class"],
        "observable": contract["observable"],
        "data_role": state.data_role,
        "verification_status": status,
        "open_blockers": [
            "action_level_signed_cut_multiplicity_missing",
            "complete_finite_temperature_1pi_self_energy_missing",
            "physical_renormalization_anchor_missing",
        ],
        "dependency_unlocked": (
            "signed-cut kinematic taxonomy only; no action-level multiplicity, "
            "physical Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation unlock"
        ),
        "claim_boundary": contract["claim_boundary"],
        "evidence_artifacts": evidence,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "failed_checks": failed_checks,
                "artifact": str(OUT.relative_to(ROOT)),
                "allowed_signs": state.allowed_signs,
                "one_to_three_allowed_assignment_count": state.one_to_three_allowed_assignment_count,
                "two_to_two_allowed_assignment_count": state.two_to_two_allowed_assignment_count,
                "missing_scattering_permutation_count": state.missing_scattering_permutation_count,
            },
            indent=2,
        )
    )
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
