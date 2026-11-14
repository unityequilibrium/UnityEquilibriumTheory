"""Wave 55 next-path decision gate for CH finite-k estimator hardening.

This verifier does not rerun simulations. It decides whether the next accepted
hardening path should be more replicate/temporal evidence or a replacement
observable policy.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET repository root not found")


ROOT = _bootstrap()
TOPIC = "0.11_Phase_Transitions"
TOPIC_DIR = ROOT / "docs" / "topics" / TOPIC
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"

WAVE54_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_source_averaging_uncertainty_gate.json"
WAVE54_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_source_averaging_uncertainty_policy.json"
POLICY_REQUIREMENTS = DATA_DIR / "structure_factor_estimator_policy_requirements.json"

MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_next_path_decision.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_next_path_decision_gate.json"


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gate(status: str, required_condition: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "required_condition": required_condition, **details}


def replacement_policy_status(requirements: dict[str, Any]) -> dict[str, Any]:
    candidates = requirements.get("policy_candidates", [])
    blocked = [
        {
            "policy_id": candidate.get("policy_id"),
            "current_support_status": candidate.get("current_support_status"),
            "accepted_now": candidate.get("accepted_now"),
            "required_source_support": candidate.get("required_source_support", []),
        }
        for candidate in candidates
        if not candidate.get("accepted_now")
    ]
    accepted = [candidate.get("policy_id") for candidate in candidates if candidate.get("accepted_now")]
    return {
        "accepted_policy_ids": accepted,
        "blocked_policy_candidates": blocked,
        "replacement_observable_available_now": bool(accepted),
    }


def build_acquisition_plan(wave54: dict[str, Any]) -> dict[str, Any]:
    row_summary = wave54.get("row_summary", {})
    accepted_counts = row_summary.get("accepted_grid_counts", {})
    row_shortfalls = (
        wave54.get("uncertainty_policy", {})
        .get("claim_bearing_replicate_policy", {})
        .get("row_shortfalls", {})
    )
    target_rows_per_grid = (
        wave54.get("uncertainty_policy", {})
        .get("claim_bearing_replicate_policy", {})
        .get("minimum_rows_per_grid", 4)
    )
    return {
        "target_accepted_rows_per_grid": target_rows_per_grid,
        "current_accepted_grid_counts": accepted_counts,
        "minimum_additional_accepted_rows": row_shortfalls,
        "priority_grids": sorted(row_shortfalls, key=lambda grid: int(grid)),
        "temporal_averaging_requirement": {
            "status": "REQUIRED",
            "minimum_policy": "store at least one explicit averaging window or multi-snapshot ensemble rule before claim-bearing use",
            "blocked_until": "time-window/ensemble expectation and uncertainty propagation are emitted in the artifact",
        },
        "uncertainty_requirement": {
            "status": "REQUIRED",
            "minimum_policy": "define row-level, grid-level, and fit-level uncertainty propagation before exponent rerun",
        },
    }


def build_manifest(wave54: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
    replacement_status = replacement_policy_status(requirements)
    acquisition_plan = build_acquisition_plan(wave54)
    selected_path = (
        "replicate_temporal_acquisition"
        if not replacement_status["replacement_observable_available_now"]
        else "replacement_observable_review"
    )
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 55 CH finite-k next-path decision gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_class": "next_path_decision_preflight",
        "inputs": [
            {
                "path": relpath(WAVE54_ARTIFACT),
                "role": "Wave 54 source averaging/uncertainty gate",
                "status": wave54.get("status"),
                "blocker_label": wave54.get("blocker_label"),
                "sha256": hash_file(WAVE54_ARTIFACT),
                "exists": WAVE54_ARTIFACT.exists(),
            },
            {
                "path": relpath(WAVE54_MANIFEST),
                "role": "Wave 54 source averaging/uncertainty manifest",
                "sha256": hash_file(WAVE54_MANIFEST),
                "exists": WAVE54_MANIFEST.exists(),
            },
            {
                "path": relpath(POLICY_REQUIREMENTS),
                "role": "Estimator replacement policy requirements",
                "sha256": hash_file(POLICY_REQUIREMENTS),
                "exists": POLICY_REQUIREMENTS.exists(),
            },
        ],
        "replacement_policy_status": replacement_status,
        "replicate_temporal_acquisition_plan": acquisition_plan,
        "selected_next_path": selected_path,
        "claim_boundary": (
            "Wave 55 selects the next hardening path only. It does not create new rows, accept a replacement observable, "
            "accept an estimator, rerun exponent gates, or upgrade universality/material/RG claims."
        ),
    }


def build_artifact(manifest: dict[str, Any], wave54: dict[str, Any]) -> dict[str, Any]:
    wave54_gates = wave54.get("gates", {})
    wave54_chain_pass = (
        wave54.get("blocker_label") == "ch_finite_k_replicate_temporal_averaging_or_replacement_observable_open"
        and wave54_gates.get("diagnostic_seed_aggregation_gate", {}).get("status") == "PASS"
        and wave54_gates.get("source_equivalent_estimator_gate", {}).get("status") == "BLOCKED"
    )
    replacement_available = manifest["replacement_policy_status"]["replacement_observable_available_now"]
    acquisition_plan = manifest["replicate_temporal_acquisition_plan"]
    acquisition_plan_defined = bool(acquisition_plan["minimum_additional_accepted_rows"])

    gates = {
        "wave54_chain_gate": gate(
            "PASS" if wave54_chain_pass else "BLOCKED",
            "Wave 55 must start from Wave 54 with diagnostic aggregation passing and estimator acceptance blocked.",
            wave54_status=wave54.get("status"),
            wave54_blocker_label=wave54.get("blocker_label"),
        ),
        "replacement_observable_available_gate": gate(
            "PASS" if replacement_available else "BLOCKED",
            "A replacement observable path requires at least one accepted source-backed policy candidate.",
            accepted_policy_ids=manifest["replacement_policy_status"]["accepted_policy_ids"],
            blocked_policy_candidates=manifest["replacement_policy_status"]["blocked_policy_candidates"],
        ),
        "replicate_temporal_acquisition_plan_gate": gate(
            "PASS" if acquisition_plan_defined else "BLOCKED",
            "If no replacement observable is accepted, the next path must define replicate and temporal averaging requirements.",
            acquisition_plan=acquisition_plan,
        ),
        "selected_next_path_gate": gate(
            "PASS",
            "The selected next path must be machine-readable and claim-bounded.",
            selected_next_path=manifest["selected_next_path"],
            reason=(
                "replacement observable policies remain unaccepted, so replicate/temporal acquisition is the narrower next controller"
                if manifest["selected_next_path"] == "replicate_temporal_acquisition"
                else "an accepted replacement observable exists and should be reviewed next"
            ),
        ),
        "estimator_acceptance_gate": gate(
            "BLOCKED",
            "Estimator acceptance remains blocked until the selected next path produces accepted evidence.",
            blocking_gates=[
                "replacement_observable_available_gate=BLOCKED",
                "replicate_temporal_acquisition_not_yet_run",
                "exponent_rerun_gate=BLOCKED",
            ],
        ),
        "exponent_rerun_gate": gate(
            "BLOCKED",
            "Do not rerun exponent gates until estimator acceptance passes.",
        ),
        "next_path_gate": gate(
            "BLOCKED",
            "The next controller is executing the replicate/temporal acquisition plan or accepting a source-backed replacement observable.",
            next_controller="ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open",
        ),
    }

    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 55 CH finite-k next-path decision gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Next_Path_Decision_Gate.py",
        "status": "WARN",
        "blocker_label": "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open",
        "claim_class": "next_path_decision_preflight",
        "claim_boundary": (
            "Wave 55 selects replicate/temporal acquisition as the narrower next controller because no replacement observable policy is accepted. "
            "It does not create evidence rows, accept an estimator, rerun exponent gates, or upgrade claims."
        ),
        "inputs": manifest["inputs"],
        "replacement_policy_status": manifest["replacement_policy_status"],
        "replicate_temporal_acquisition_plan": manifest["replicate_temporal_acquisition_plan"],
        "selected_next_path": manifest["selected_next_path"],
        "gates": gates,
        "limitations": [
            "No simulation or exponent verifier is rerun by this decision gate.",
            "Replacement observable policies remain unaccepted by the source-policy requirements manifest.",
            "The replicate/temporal acquisition plan is defined but not executed.",
            "No estimator replacement, exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }


def main() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    wave54 = load_json(WAVE54_ARTIFACT)
    requirements = load_json(POLICY_REQUIREMENTS)
    manifest = build_manifest(wave54, requirements)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact = build_artifact(manifest, wave54)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = main()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "selected_next_path": result["selected_next_path"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
            },
            indent=2,
            sort_keys=True,
        )
    )
