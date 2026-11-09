"""Wave 53 gate for CH finite-k shape-only normalization policy.

This verifier does not rerun simulations. It separates amplitude-invariant
finite-k peak location diagnostics from source-equivalent S(q) amplitude or
susceptibility claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from collections import defaultdict
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
RESULT_DIR = TOPIC_DIR / "Result"
ARTIFACT_DIR = RESULT_DIR / "artifacts"

WAVE52_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_field_normalization_decision_gate.json"
WAVE52_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_field_normalization_decision.json"
WAVE50_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_extended_grid_coverage_probe.json"
WAVE48_CSV = RESULT_DIR / "gl_structure_factor_ch_finite_k_estimator_candidate_stats.csv"
WAVE50_CSV = RESULT_DIR / "gl_structure_factor_ch_finite_k_extended_grid_coverage_probe_stats.csv"

MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_shape_only_normalization_policy.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_shape_only_normalization_policy_gate.json"


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


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def gate(status: str, required_condition: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "required_condition": required_condition, **details}


def summarize_rows(wave48_rows: list[dict[str, Any]], wave50_rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = wave48_rows + wave50_rows
    by_grid: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "total_rows": 0,
            "candidate_pass_rows": 0,
            "accepted_shape_rows": 0,
            "seed_labels": set(),
            "has_single_timepoint_only": True,
        }
    )
    for row in rows:
        grid = str(int(float(row["grid_L"])))
        bucket = by_grid[grid]
        bucket["total_rows"] += 1
        candidate_pass = as_bool(row.get("ch_finite_k_candidate_pass"))
        bucket["candidate_pass_rows"] += int(candidate_pass)
        shape_ok = (
            row.get("status") == "OK"
            and as_bool(row.get("ch_finite_k_valid"))
            and candidate_pass
            and not as_bool(row.get("peak_hits_low_window_edge"))
        )
        bucket["accepted_shape_rows"] += int(shape_ok)
        bucket["seed_labels"].add(str(row.get("seed")))

    by_grid_out = {}
    for grid, bucket in sorted(by_grid.items(), key=lambda item: int(item[0])):
        by_grid_out[grid] = {
            "total_rows": bucket["total_rows"],
            "candidate_pass_rows": bucket["candidate_pass_rows"],
            "accepted_shape_rows": bucket["accepted_shape_rows"],
            "seed_count": len(bucket["seed_labels"]),
            "has_single_timepoint_only": bucket["has_single_timepoint_only"],
        }
    accepted_grid_counts = {
        grid: bucket["accepted_shape_rows"]
        for grid, bucket in by_grid_out.items()
        if bucket["accepted_shape_rows"] > 0
    }
    return {
        "source_rows": {
            "wave48_csv": relpath(WAVE48_CSV),
            "wave50_csv": relpath(WAVE50_CSV),
        },
        "total_rows": len(rows),
        "by_grid": by_grid_out,
        "accepted_grid_counts": accepted_grid_counts,
        "accepted_grid_count": len(accepted_grid_counts),
        "min_accepted_rows_per_grid": min(accepted_grid_counts.values()) if accepted_grid_counts else 0,
    }


def build_manifest(wave52: dict[str, Any], row_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 53 CH finite-k shape-only normalization policy gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_class": "shape_only_normalization_policy_preflight",
        "inputs": [
            {
                "path": relpath(WAVE52_ARTIFACT),
                "role": "Wave 52 field-normalization decision gate",
                "status": wave52.get("status"),
                "blocker_label": wave52.get("blocker_label"),
                "sha256": hash_file(WAVE52_ARTIFACT),
                "exists": WAVE52_ARTIFACT.exists(),
            },
            {
                "path": relpath(WAVE52_MANIFEST),
                "role": "Wave 52 field-normalization decision manifest",
                "sha256": hash_file(WAVE52_MANIFEST),
                "exists": WAVE52_MANIFEST.exists(),
            },
            {
                "path": relpath(WAVE50_ARTIFACT),
                "role": "Wave 50 accepted-row coverage artifact",
                "sha256": hash_file(WAVE50_ARTIFACT),
                "exists": WAVE50_ARTIFACT.exists(),
            },
            {
                "path": relpath(WAVE48_CSV),
                "role": "Wave 48 finite-k candidate rows",
                "sha256": hash_file(WAVE48_CSV),
                "exists": WAVE48_CSV.exists(),
            },
            {
                "path": relpath(WAVE50_CSV),
                "role": "Wave 50 extended-grid rows",
                "sha256": hash_file(WAVE50_CSV),
                "exists": WAVE50_CSV.exists(),
            },
        ],
        "shape_only_policy": {
            "q_peak_amplitude_invariance": {
                "status": "PASS",
                "relation": "argmax_q[a * S(q)] = argmax_q[S(q)] for a > 0",
                "allowed_claim": "q_peak location and xi_peak = 2*pi/q_peak may be inspected as shape-only diagnostics",
            },
            "source_amplitude_policy": {
                "status": "BLOCKED",
                "blocked_claims": [
                    "source-equivalent S(q) amplitude",
                    "susceptibility amplitude",
                    "material concentration fluctuation magnitude",
                    "accepted exponent input",
                ],
            },
            "averaging_policy": {
                "diagnostic_seed_aggregation_status": "PASS",
                "source_time_or_ensemble_average_status": "BLOCKED",
                "reason": "Rows provide seed/grid final-snapshot diagnostics, but not an accepted source S(q,t) ensemble or time-average convention.",
            },
        },
        "row_summary": row_summary,
        "claim_boundary": (
            "Wave 53 permits amplitude-invariant q_peak inspection as a diagnostic shape-only lane. "
            "It does not accept S(q) amplitude, susceptibility, source-equivalent field normalization, estimator replacement, or exponent rerun."
        ),
    }


def build_artifact(manifest: dict[str, Any], wave52: dict[str, Any]) -> dict[str, Any]:
    wave52_gates = wave52.get("gates", {})
    wave52_chain_pass = (
        wave52.get("blocker_label") == "ch_finite_k_field_amplitude_and_averaging_normalization_open"
        and wave52_gates.get("source_field_symbol_gate", {}).get("status") == "PASS"
        and wave52_gates.get("uet_centered_field_proxy_gate", {}).get("status") == "PASS"
        and wave52_gates.get("amplitude_normalization_gate", {}).get("status") == "BLOCKED"
    )
    row_summary = manifest["row_summary"]
    diagnostic_seed_pass = row_summary["accepted_grid_count"] >= 3 and row_summary["min_accepted_rows_per_grid"] >= 2

    gates = {
        "wave52_chain_gate": gate(
            "PASS" if wave52_chain_pass else "BLOCKED",
            "Wave 53 must start from Wave 52 with diagnostic field symbols passing and source-equivalent amplitude normalization blocked.",
            wave52_status=wave52.get("status"),
            wave52_blocker_label=wave52.get("blocker_label"),
        ),
        "q_peak_amplitude_invariance_gate": gate(
            "PASS",
            "Positive scalar amplitude normalization does not change q_peak location.",
            relation="argmax_q[a * S(q)] = argmax_q[S(q)] for a > 0",
            accepted_use="diagnostic shape-only q_peak and xi_peak inspection",
        ),
        "diagnostic_seed_aggregation_gate": gate(
            "PASS" if diagnostic_seed_pass else "BLOCKED",
            "Diagnostic shape-only rows must preserve accepted multi-grid seed coverage.",
            accepted_grid_count=row_summary["accepted_grid_count"],
            min_accepted_rows_per_grid=row_summary["min_accepted_rows_per_grid"],
            accepted_grid_counts=row_summary["accepted_grid_counts"],
        ),
        "source_amplitude_normalization_gate": gate(
            "BLOCKED",
            "Shape-only q_peak invariance does not accept source S(q) amplitude or susceptibility normalization.",
            blocked_claims=manifest["shape_only_policy"]["source_amplitude_policy"]["blocked_claims"],
        ),
        "source_averaging_convention_gate": gate(
            "BLOCKED",
            "Current rows are final-snapshot seed diagnostics, not an accepted source ensemble/time average for S(q,t).",
            missing=[
                "time-window averaging policy",
                "ensemble expectation policy matching source S(q,t)",
                "claim-bearing seed aggregation uncertainty policy",
            ],
        ),
        "shape_only_diagnostic_lane_gate": gate(
            "PASS" if wave52_chain_pass and diagnostic_seed_pass else "BLOCKED",
            "Shape-only finite-k diagnostics may continue without amplitude acceptance.",
            allowed_claim="diagnostic q_peak/xi_peak row filtering only",
        ),
        "source_equivalent_estimator_gate": gate(
            "BLOCKED",
            "Accepted estimator replacement still requires source amplitude normalization and source averaging convention.",
            blocking_gates=[
                "source_amplitude_normalization_gate=BLOCKED",
                "source_averaging_convention_gate=BLOCKED",
            ],
        ),
        "exponent_rerun_gate": gate(
            "BLOCKED",
            "Do not rerun exponent gates until source-equivalent estimator acceptance passes.",
        ),
        "next_path_gate": gate(
            "BLOCKED",
            "The next controller is source averaging/uncertainty policy or explicit replacement observable acceptance.",
            next_controller="ch_finite_k_source_averaging_and_uncertainty_policy_open",
        ),
    }

    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 53 CH finite-k shape-only normalization policy gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Shape_Only_Normalization_Policy_Gate.py",
        "status": "WARN",
        "blocker_label": "ch_finite_k_source_averaging_and_uncertainty_policy_open",
        "claim_class": "shape_only_normalization_policy_preflight",
        "claim_boundary": (
            "Wave 53 narrows amplitude normalization: amplitude-invariant q_peak location can remain a diagnostic shape-only lane, "
            "but source S(q) amplitude, susceptibility, source averaging, estimator replacement, exponent, universality, material, RG, and Tier A claims remain blocked."
        ),
        "inputs": manifest["inputs"],
        "shape_only_policy": manifest["shape_only_policy"],
        "row_summary": row_summary,
        "gates": gates,
        "limitations": [
            "No simulation or exponent verifier is rerun by this policy gate.",
            "q_peak shape-only diagnostics do not accept S(q) amplitude or susceptibility.",
            "Rows remain final-snapshot seed diagnostics rather than source-accepted ensemble/time averages.",
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
    wave52 = load_json(WAVE52_ARTIFACT)
    row_summary = summarize_rows(load_rows(WAVE48_CSV), load_rows(WAVE50_CSV))
    manifest = build_manifest(wave52, row_summary)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact = build_artifact(manifest, wave52)
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
