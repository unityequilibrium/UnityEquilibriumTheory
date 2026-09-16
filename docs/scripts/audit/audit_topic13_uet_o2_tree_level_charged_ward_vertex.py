"""Audit the tree-level charged Euclidean Ward-vertex lane for Topic 13."""

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

from docs.core.uet_o2_tree_level_charged_ward_vertex import (  # noqa: E402
    TREE_LEVEL_CHARGED_WARD_STATUS,
    tree_level_charged_ward_vertex_contract,
    tree_level_charged_ward_vertex_state,
)


OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_tree_level_charged_ward_vertex_audit.json"
MODULE = ROOT / "docs/core/02_equations/o2/uet_o2_tree_level_charged_ward_vertex.py"
PROPAGATOR = ROOT / "docs/core/02_equations/o2/uet_o2_finite_density_charged_vertex.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    state = tree_level_charged_ward_vertex_state(0.35, 0.1, 0.8)
    contract = tree_level_charged_ward_vertex_contract()
    checks = {
        "state_is_finite": all(
            value == value and abs(float(value)) < float("inf")
            for value in asdict(state).values()
            if isinstance(value, (int, float))
        ),
        "normal_branch_is_explicit": state.normal_branch,
        "ward_identity_residual": state.max_ward_residual <= 1.0e-12,
        "zero_transfer_vertex_limit": state.zero_transfer_vertex_residual <= 1.0e-12,
        "charge_conjugation_boundary": state.charge_conjugation_residual <= 1.0e-12,
        "tree_level_vertex_is_closed": state.tree_level_current_vertex_completed,
        "loop_renormalized_vertex_remains_open": not state.loop_renormalized_offshell_vertex_completed,
        "physical_kubo_not_emitted": not state.physical_kubo_coefficient_emitted,
        "numeric_alpha_not_emitted": not state.numeric_alpha_Phi_K_emitted,
        "no_parameter_fitting": not state.parameter_fitting_performed,
        "no_target_or_holdout": not state.target_data_used and not state.xie_2026_accessed,
        "Phi_ontology_preserved": "not temperature" in contract["ontology"]["Phi"],
        "C_ontology_preserved": "not mass or charge" in contract["ontology"]["C"],
        "R_gen_ontology_preserved": "derived physical/history trace" in contract["ontology"]["R_gen"],
        "R_obs_separate": "separate observer" in contract["ontology"]["R_obs"],
    }
    status = TREE_LEVEL_CHARGED_WARD_STATUS if all(checks.values()) else "FAIL_T13_TREE_LEVEL_CHARGED_WARD_VERTEX_LANE"
    open_blockers = [
        "loop_renormalized_off_shell_self_energy_and_current_vertex_missing",
        "continuum_limit_missing",
        "physical_kubo_coefficient_missing",
        "finite_temperature_two_fluid_completion_missing",
        "dimensional_Phi_to_thermal_observable_map_missing",
        "alpha_Phi_K_independent_calibration_missing",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    ]
    report = {
        "schema_version": "t13-tree-level-charged-ward-vertex-audit-v1",
        "artifact": "t13_uet_o2_tree_level_charged_ward_vertex_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_TREE_LEVEL_CHARGED_WARD_VERTEX_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS_") else "OPEN",
            "what_is_closed": [
                "tree-level finite-density charged Euclidean propagator/current-vertex pair",
                "finite-density Euclidean Ward identity on the declared normal branch",
                "zero-transfer vertex limit and charge-conjugation boundary",
            ],
            "what_remains_open": open_blockers,
            "equation_or_mapping": contract["equations"],
            "units": contract["units"],
            "derivation_class": contract["derivation_class"],
            "observable": contract["observable"],
            "data_role": contract["data_role"],
            "evidence_artifacts": [
                {"path": "docs/core/02_equations/o2/uet_o2_tree_level_charged_ward_vertex.py", "sha256": sha256(MODULE)},
                {"path": "docs/core/02_equations/o2/uet_o2_finite_density_charged_vertex.py", "sha256": sha256(PROPAGATOR)},
            ],
            "verification_status": status,
            "open_blockers": open_blockers,
            "dependency_unlocked": "tree-level charged Ward interface only; no loop, continuum, physical Kubo, SI, TTG, or Full Topic 13 unlock",
            "claim_boundary": contract["claim_boundary"],
        },
        "checks": checks,
        "contract": contract,
        "state": {"reference": asdict(state)},
        "controlling_blocker": "loop_renormalized_off_shell_self_energy_and_current_vertex_missing",
        "next_controller": "derive and renormalize the finite-temperature retarded self-energy and vertex together through the SK/KMS action before physical Kubo admission",
        "claim_boundary": contract["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                "failed_checks": [key for key, value in checks.items() if not value],
                "max_ward_residual": state.max_ward_residual,
                "zero_transfer_vertex_residual": state.zero_transfer_vertex_residual,
                "charge_conjugation_residual": state.charge_conjugation_residual,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
