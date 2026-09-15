"""Build the Topic 0.13 Wave 1 branch-separated causal/source gate."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
THERMAL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json"
REFERENCE = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json"
FULL = ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"
REVIEW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_thermal_source_review.json"
OUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main() -> int:
    thermal = load(THERMAL)
    reference = load(REFERENCE)
    full = load(FULL)
    package = load(PACKAGE)
    review = load(REVIEW)
    threshold = float(thermal.get("thresholds", {}).get("prearrival_leakage_fraction_max", 1.0e-6))
    reference_leakage = float(reference["reference"]["metrics"]["prearrival_leakage_fraction"])
    full_leakage = float(full["metrics"]["prearrival_leakage"]["value"])
    holdout_consumed = bool(review.get("holdout_consumed"))
    numeric_fitting = bool(review.get("numeric_fitting_allowed"))
    source_rows = package.get("sources", [])
    normalized_source_ready = any(
        row.get("source_id") == "ding_2022_fig1d_digitized"
        and row.get("status") == "FIGURE_DERIVED_NUMERIC_PACKAGE_WITH_CLOSED_MAPPING"
        for row in source_rows
    )
    raw_author_source_ready = any(
        row.get("status") == "SOURCE_LOCKED_NUMERIC"
        and row.get("source_id") != "ding_2022_fig1d_digitized"
        for row in source_rows
    )
    gates = {
        "selected_causal_reference_prearrival_leakage": reference_leakage <= threshold,
        "selected_causal_reference_compact_support": reference.get("reference", {}).get("status") == "PASS",
        "full_candidate_prearrival_leakage": full_leakage <= threshold,
        "locked_threshold_unchanged": threshold == 1.0e-6,
        "holdout_not_consumed": not holdout_consumed,
        "numeric_fitting_disabled": not numeric_fitting,
        "normalized_comparison_route_ready": normalized_source_ready,
        "raw_author_numeric_route_ready": raw_author_source_ready,
        "provisional_source_provenance_present": not raw_author_source_ready,
        "alpha_Phi_K_independent_calibration": False,
    }
    artifact = {
        "schema_version": "1.0",
        "artifact": "thermal_wave1_branch_gate",
        "generated_at": date.today().isoformat(),
        "status": "PASS_WITH_BLOCKED_DIMENSIONAL_AND_FULL_CANDIDATE_LANES" if all(gates[key] for key in ("selected_causal_reference_prearrival_leakage", "selected_causal_reference_compact_support", "locked_threshold_unchanged", "holdout_not_consumed", "numeric_fitting_disabled", "normalized_comparison_route_ready")) else "BLOCKED",
        "claim_promotion": False,
        "selected_causal_branch": {
            "operator_mode": "causal_linear_space_reference_v1",
            "scope": "frozen_C_linearized_Phi_Pi_normalized_control",
            "prearrival_leakage_fraction": reference_leakage,
            "arrival_target_abs": reference["reference"]["metrics"]["arrival_target_abs"],
            "threshold": threshold,
            "artifact": {"path": rel(REFERENCE), "sha256": sha256(REFERENCE)},
            "claim_boundary": "compact-support normalized control only; not a full coupled physical causal law",
        },
        "full_candidate_branch": {
            "prearrival_leakage_fraction": full_leakage,
            "threshold": threshold,
            "gate": full["metrics"]["prearrival_leakage"].get("gate"),
            "artifact": {"path": rel(FULL), "sha256": sha256(FULL)},
            "controlling_blocker": "conserved_C_gradient_term_has_unbounded_k4_characteristic_speed",
            "claim_boundary": "full coupled candidate remains blocked; selected reference does not replace this gate",
        },
        "measurement_contract": {
            "standard": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            "uet_normalized": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "alpha_Phi_K_status": "OPEN_CALIBRATION_DEPENDENT",
            "uncertainty_status": "source digitization uncertainty is recorded; experimental uncertainty and alpha uncertainty remain open",
        },
        "source_contract": {
            "package": {"path": rel(PACKAGE), "sha256": sha256(PACKAGE), "status": package.get("status")},
            "numeric_fitting_allowed": numeric_fitting,
            "holdout_consumed": holdout_consumed,
            "provisional_source_present": not raw_author_source_ready,
            "normalized_comparison_route_ready": normalized_source_ready,
            "raw_author_numeric_route_ready": raw_author_source_ready,
            "xie_2026_policy": "locked_holdout_metadata_only",
        },
        "gates": gates,
        "controlling_blocker": "full_candidate_prearrival_leakage_and_open_alpha_Phi_K_calibration",
        "next_action": "derive or independently calibrate alpha_Phi_K with uncertainty, then run a preregistered normalized comparison using only non-holdout source rows",
        "claim_boundary": "Wave 1 evidence-producing branch gate; no temperature prediction, external validation, fit-as-prediction, or UET closure",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "gates": gates, "artifact": rel(OUT)}, indent=2))
    return 0 if artifact["status"] != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
