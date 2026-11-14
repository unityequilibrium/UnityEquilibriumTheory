"""Wave 54 gate for CH finite-k source averaging and uncertainty policy.

This verifier does not rerun simulations. It checks whether the current
finite-k rows are strong enough for claim-bearing source averaging and
uncertainty, while preserving diagnostic-only use when they are not.
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

WAVE53_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_shape_only_normalization_policy_gate.json"
WAVE53_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_shape_only_normalization_policy.json"

MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_source_averaging_uncertainty_policy.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_source_averaging_uncertainty_gate.json"

MIN_DIAGNOSTIC_GRIDS = 3
MIN_DIAGNOSTIC_ROWS_PER_GRID = 2
MIN_CLAIM_ROWS_PER_GRID = 4


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


def build_manifest(wave53: dict[str, Any]) -> dict[str, Any]:
    row_summary = wave53.get("row_summary", {})
    accepted_counts = row_summary.get("accepted_grid_counts", {})
    by_grid = row_summary.get("by_grid", {})
    claim_row_shortfalls = {
        grid: max(0, MIN_CLAIM_ROWS_PER_GRID - int(count))
        for grid, count in accepted_counts.items()
        if int(count) < MIN_CLAIM_ROWS_PER_GRID
    }
    single_timepoint_grids = [
        grid for grid, summary in by_grid.items() if summary.get("has_single_timepoint_only")
    ]
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 54 CH finite-k source averaging/uncertainty policy gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_class": "source_averaging_uncertainty_policy_preflight",
        "inputs": [
            {
                "path": relpath(WAVE53_ARTIFACT),
                "role": "Wave 53 shape-only normalization policy gate",
                "status": wave53.get("status"),
                "blocker_label": wave53.get("blocker_label"),
                "sha256": hash_file(WAVE53_ARTIFACT),
                "exists": WAVE53_ARTIFACT.exists(),
            },
            {
                "path": relpath(WAVE53_MANIFEST),
                "role": "Wave 53 shape-only normalization policy manifest",
                "sha256": hash_file(WAVE53_MANIFEST),
                "exists": WAVE53_MANIFEST.exists(),
            },
        ],
        "row_summary": row_summary,
        "uncertainty_policy": {
            "diagnostic_seed_aggregation": {
                "status": "PASS",
                "minimum_accepted_grids": MIN_DIAGNOSTIC_GRIDS,
                "minimum_rows_per_grid": MIN_DIAGNOSTIC_ROWS_PER_GRID,
                "accepted_grid_counts": accepted_counts,
                "allowed_claim": "diagnostic robustness only",
            },
            "claim_bearing_replicate_policy": {
                "status": "BLOCKED",
                "minimum_rows_per_grid": MIN_CLAIM_ROWS_PER_GRID,
                "row_shortfalls": claim_row_shortfalls,
                "reason": "Claim-bearing uncertainty needs more than the current minimum diagnostic replicate count on L24/L28.",
            },
            "source_averaging_policy": {
                "status": "BLOCKED",
                "single_timepoint_grids": single_timepoint_grids,
                "missing": [
                    "accepted time-window averaging policy",
                    "source-equivalent ensemble expectation policy",
                    "uncertainty interval or bootstrap policy for accepted rows",
                ],
            },
        },
        "claim_boundary": (
            "Wave 54 keeps seed/grid aggregation diagnostic-only. It does not accept source S(q,t) "
            "averaging, uncertainty intervals, estimator replacement, or exponent rerun."
        ),
    }


def build_artifact(manifest: dict[str, Any], wave53: dict[str, Any]) -> dict[str, Any]:
    wave53_gates = wave53.get("gates", {})
    wave53_chain_pass = (
        wave53.get("blocker_label") == "ch_finite_k_source_averaging_and_uncertainty_policy_open"
        and wave53_gates.get("shape_only_diagnostic_lane_gate", {}).get("status") == "PASS"
        and wave53_gates.get("source_averaging_convention_gate", {}).get("status") == "BLOCKED"
    )
    policy = manifest["uncertainty_policy"]
    accepted_counts = policy["diagnostic_seed_aggregation"]["accepted_grid_counts"]
    diagnostic_pass = (
        len(accepted_counts) >= MIN_DIAGNOSTIC_GRIDS
        and min((int(v) for v in accepted_counts.values()), default=0) >= MIN_DIAGNOSTIC_ROWS_PER_GRID
    )
    claim_replicates_pass = not policy["claim_bearing_replicate_policy"]["row_shortfalls"]
    source_averaging_pass = not policy["source_averaging_policy"]["single_timepoint_grids"]

    gates = {
        "wave53_chain_gate": gate(
            "PASS" if wave53_chain_pass else "BLOCKED",
            "Wave 54 must start from Wave 53 with shape-only diagnostic lane passing and source averaging blocked.",
            wave53_status=wave53.get("status"),
            wave53_blocker_label=wave53.get("blocker_label"),
        ),
        "diagnostic_seed_aggregation_gate": gate(
            "PASS" if diagnostic_pass else "BLOCKED",
            "Diagnostic rows must preserve accepted multi-grid seed coverage.",
            accepted_grid_counts=accepted_counts,
            required_grid_count=MIN_DIAGNOSTIC_GRIDS,
            required_rows_per_grid=MIN_DIAGNOSTIC_ROWS_PER_GRID,
        ),
        "claim_bearing_replicate_gate": gate(
            "PASS" if claim_replicates_pass else "BLOCKED",
            "Claim-bearing uncertainty needs at least four accepted rows per accepted grid before exponent fitting.",
            required_rows_per_grid=MIN_CLAIM_ROWS_PER_GRID,
            row_shortfalls=policy["claim_bearing_replicate_policy"]["row_shortfalls"],
        ),
        "source_time_averaging_gate": gate(
            "PASS" if source_averaging_pass else "BLOCKED",
            "Source-equivalent S(q,t) averaging needs an accepted time-window or ensemble expectation policy.",
            single_timepoint_grids=policy["source_averaging_policy"]["single_timepoint_grids"],
            missing=policy["source_averaging_policy"]["missing"],
        ),
        "uncertainty_interval_policy_gate": gate(
            "BLOCKED",
            "No confidence interval, bootstrap, jackknife, or comparable uncertainty policy is accepted for claim-bearing rows.",
            missing=[
                "row-level uncertainty statistic",
                "grid-level uncertainty aggregation",
                "fit-level uncertainty propagation for beta/nu",
            ],
        ),
        "source_equivalent_estimator_gate": gate(
            "BLOCKED",
            "Estimator replacement requires claim-bearing replicates, source averaging, and uncertainty interval policies.",
            blocking_gates=[
                "claim_bearing_replicate_gate=BLOCKED",
                "source_time_averaging_gate=BLOCKED",
                "uncertainty_interval_policy_gate=BLOCKED",
            ],
        ),
        "exponent_rerun_gate": gate(
            "BLOCKED",
            "Do not rerun exponent gates until source-equivalent estimator acceptance passes.",
        ),
        "next_path_gate": gate(
            "BLOCKED",
            "The next controller is replicate/temporal averaging data or an accepted replacement observable policy.",
            next_controller="ch_finite_k_replicate_temporal_averaging_or_replacement_observable_open",
        ),
    }
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 54 CH finite-k source averaging/uncertainty policy gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Source_Averaging_Uncertainty_Gate.py",
        "status": "WARN",
        "blocker_label": "ch_finite_k_replicate_temporal_averaging_or_replacement_observable_open",
        "claim_class": "source_averaging_uncertainty_policy_preflight",
        "claim_boundary": (
            "Wave 54 accepts current rows only for diagnostic seed aggregation. Claim-bearing source averaging, uncertainty intervals, "
            "estimator replacement, exponent, universality, material, RG, and Tier A claims remain blocked."
        ),
        "inputs": manifest["inputs"],
        "row_summary": manifest["row_summary"],
        "uncertainty_policy": policy,
        "gates": gates,
        "limitations": [
            "No simulation or exponent verifier is rerun by this policy gate.",
            "Accepted L24/L28 rows have only two accepted rows each, below the claim-bearing replicate floor.",
            "Rows remain final-snapshot diagnostics without accepted source time-window averaging.",
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
    wave53 = load_json(WAVE53_ARTIFACT)
    manifest = build_manifest(wave53)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact = build_artifact(manifest, wave53)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = main()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
            },
            indent=2,
            sort_keys=True,
        )
    )
