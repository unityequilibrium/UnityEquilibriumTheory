"""Audit the named Topic 13 causal branch for Core handoff compatibility.

This audit promotes only the named normalized branch.  It never promotes the
original conserved-C local-gradient baseline and does not establish an SI or
external thermal result.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
NO_GO_REL = "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json"
TELEGRAPH_REL = "docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json"
COUPLED_REL = "docs/core/artifacts/matter_space_flux_phi_coupled_verification.json"
SELECTION_REL = "docs/core/artifacts/t13_causal_branch_selection_audit.json"
OUT_REL = "docs/core/artifacts/t13_causal_named_branch_core_compatibility.json"


def load(relative: str) -> dict[str, Any]:
    with (ROOT / relative).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def artifact_ref(relative: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": relative,
        "sha256": sha256(relative),
        "summary": {
            "status": value.get("status"),
            "closure_level": value.get("major_result", {}).get("closure_level"),
        },
    }


def main() -> int:
    no_go = load(NO_GO_REL)
    telegraph = load(TELEGRAPH_REL)
    coupled = load(COUPLED_REL)
    selection = load(SELECTION_REL) if (ROOT / SELECTION_REL).is_file() else {}

    threshold = 1.0e-6
    coupled_checks = coupled.get("verification", {}).get("checks", {})
    coupled_metrics = coupled.get("domain_of_dependence", {}).get("metrics", {})
    convergence_checks = coupled.get("convergence", {}).get("checks", {})
    no_go_scope = no_go.get("proof_scope", "")
    original_baseline_pass = coupled.get("verification", {}).get(
        "full_original_conserved_gradient_candidate_pass"
    )

    checks = {
        "scoped_no_go_is_recorded": no_go.get("status")
        == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS",
        "no_go_scope_is_not_global": (
            "local conserved-C Cattaneo equation" in no_go_scope
            and "not a global no-go theorem" in no_go.get("claim_boundary", "")
        ),
        "telegraph_lane_passes": telegraph.get("status") == "PASS"
        and all(telegraph.get("verification", {}).get("checks", {}).values()),
        "coupled_lane_passes": coupled.get("status") == "PASS"
        and all(coupled_checks.values()),
        "leakage_threshold_unchanged": (
            coupled.get("verification", {}).get("thresholds", {}).get(
                "prearrival_leakage_fraction"
            )
            == threshold
        ),
        "coupled_leakage_passes": float(
            coupled_metrics.get("prearrival_leakage_fraction", 1.0)
        )
        <= threshold,
        "C_arrival_is_nonzero": float(
            coupled_metrics.get("C_arrival_target_abs", 0.0)
        )
        > 0.0,
        "Phi_arrival_is_nonzero": float(
            coupled_metrics.get("Phi_arrival_target_abs", 0.0)
        )
        > 0.0,
        "energy_ledger_passes": float(
            coupled_metrics.get("max_combined_energy_relative_residual", 1.0)
        )
        <= threshold,
        "temporal_and_spatial_convergence_pass": all(convergence_checks.values()),
        "no_clipping_padding_or_fit": coupled_checks.get("no_clipping") is True
        and coupled_checks.get("no_cone_padding") is True
        and coupled_checks.get("no_parameter_fitting") is True,
        "ontology_is_preserved": (
            coupled.get("units", {}).get("C")
            == "normalized collective-coordinate density lane"
            and coupled.get("units", {}).get("Phi")
            == "normalized effective response variable"
            and coupled.get("units", {}).get("R_gen")
            == "derived history trace; absent from dynamics"
        ),
        "original_baseline_is_not_promoted": original_baseline_pass is False
        and coupled.get("verification", {}).get(
            "full_original_conserved_gradient_candidate_replaced"
        )
        is False,
        "trace_has_no_backreaction": coupled.get("verification", {}).get(
            "trace_backreaction"
        )
        is False,
        "holdout_is_unread": coupled.get("verification", {}).get(
            "xie_2026_accessed"
        )
        is False,
        "selection_boundary_is_preserved": (
            not selection
            or (
                selection.get("status", "").startswith("PASS")
                and selection.get("baseline_preservation", {}).get(
                    "baseline_replaced"
                )
                is False
            )
        ),
    }
    status = (
        "PASS_CAUSAL_NAMED_BRANCH_CORE_COMPATIBILITY"
        if all(checks.values())
        else "BLOCKED_CAUSAL_NAMED_BRANCH_CORE_COMPATIBILITY"
    )
    report = {
        "schema_version": "t13-causal-named-branch-core-compatibility-v1",
        "artifact": "t13_causal_named_branch_core_compatibility",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_CAUSAL_FLUX_PHI_COUPLED_CORE_COMPATIBILITY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_CORE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the named conserved-flux/Phi telegraph branch is admissible as a bounded Core input",
                "the unchanged finite-cone, arrival, convergence, ledger, and anti-manipulation contract",
                "the scoped conserved-C local-gradient no-go boundary and baseline preservation",
            ],
            "equation_or_mapping": {
                "selected_branch": "C_t + partial_x J_C = 0; tau_C J_C_t + J_C = -M_C partial_x(mu_C)",
                "response_branch": "tau_Phi Phi_tt + Phi_t + M_Phi mu_Phi = 0",
                "measurement": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            },
            "units": {
                "lane": "normalized internal candidate",
                "C": "normalized collective-coordinate density lane",
                "Phi": "normalized effective response variable",
                "R_gen": "derived history trace; absent from dynamics",
            },
            "derivation_class": "Core compatibility audit of a named normalized causal branch",
            "observable": "normalized coupled C/Phi response, compact support, arrival, and shared ledger",
            "data_role": "INTERNAL_VERIFICATION",
            "evidence_artifacts": [
                artifact_ref(NO_GO_REL, no_go),
                artifact_ref(TELEGRAPH_REL, telegraph),
                artifact_ref(COUPLED_REL, coupled),
            ],
            "verification_status": status,
            "open_blockers": [
                item for item, passed in checks.items() if not passed
            ],
            "dependency_unlocked": "Causal exception only; Full Topic 13 remains blocked until the other Core packages pass.",
            "claim_boundary": "CLOSED_FOR_CORE for the named normalized causal branch only. It does not pass the original kappa_C>0 baseline, establish SI thermal mapping, external validation, covariant 3+1 well-posedness, or global UET closure.",
        },
        "baseline_preservation": {
            "original_conserved_gradient_candidate_pass": original_baseline_pass,
            "baseline_replaced": False,
            "no_go_scope": no_go_scope,
            "locked_threshold": threshold,
        },
        "selected_branch": {
            "branch_id": coupled.get("branch_id"),
            "prearrival_leakage_fraction": coupled_metrics.get(
                "prearrival_leakage_fraction"
            ),
            "C_arrival_target_abs": coupled_metrics.get("C_arrival_target_abs"),
            "Phi_arrival_target_abs": coupled_metrics.get("Phi_arrival_target_abs"),
            "max_combined_energy_relative_residual": coupled_metrics.get(
                "max_combined_energy_relative_residual"
            ),
            "closure_level_before_compatibility": coupled.get("major_result", {}).get(
                "closure_level"
            ),
        },
        "checks": checks,
        "thresholds": {
            "prearrival_leakage_fraction_max": threshold,
            "energy_relative_residual_max": threshold,
        },
        "holdout_policy": {
            "xie_2026_accessed": False,
            "used_for_fit": False,
            "used_for_tuning": False,
            "used_for_calibration": False,
            "used_for_threshold_adjustment": False,
        },
        "next_controller": "Close the independent base-Phi SI/alpha/beta package, accepted Ding-compatible C_src/material uncertainty package, and physical Kubo/SK/KMS/entropy package; do not use this causal result as SI or external thermal evidence.",
        "claim_boundary": "This is a bounded Core handoff record for one named normalized causal branch, not a global theory closure or external prediction.",
    }
    out = ROOT / OUT_REL
    out.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT_REL,
                "failed_checks": [key for key, value in checks.items() if not value],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
