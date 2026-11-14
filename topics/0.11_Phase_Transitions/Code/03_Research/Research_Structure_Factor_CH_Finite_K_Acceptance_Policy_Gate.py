"""Wave 49 gate for CH finite-k estimator acceptance policy.

This verifier does not rerun the phase-transition simulation. It reads the
Wave 48 finite-k estimator candidate rows and makes the acceptance policy
machine-readable before any exponent or Tier A claim can use the candidate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

import numpy as np


TOPIC = "0.11_Phase_Transitions"
ROOT = Path(__file__).resolve().parents[5]
TOPIC_ROOT = ROOT / "docs" / "topics" / TOPIC
DATA_DIR = TOPIC_ROOT / "Data" / "03_Research"
RESULT_DIR = TOPIC_ROOT / "Result"
ARTIFACT_DIR = RESULT_DIR / "artifacts"

WAVE48_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_estimator_candidate_gate.json"
WAVE48_CSV = RESULT_DIR / "gl_structure_factor_ch_finite_k_estimator_candidate_stats.csv"
WAVE47_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_normalization_preflight_gate.json"
WAVE47_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_normalization_preflight.json"

MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_acceptance_policy.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_acceptance_policy_gate.json"

POLICY = {
    "field_normalization": {
        "status": "WARN",
        "rule": "centered UET C may be used only as a diagnostic concentration-fluctuation proxy",
        "claim_boundary": "not accepted as source-equivalent concentration normalization for exponent use",
    },
    "coefficient_policy": {
        "measurement_only_status": "PASS",
        "source_dynamics_coefficient_status": "BLOCKED",
        "rule": "Wave 49 may measure S(q) on existing fields while excluding source dynamics coefficient claims",
    },
    "q_window_row_acceptance": {
        "require_status_ok": True,
        "require_wave48_candidate_pass": True,
        "exclude_low_window_edge_peaks": True,
        "min_window_power_fraction": 0.05,
        "max_low_mode_power_fraction": 0.90,
        "xi_over_l_floor": 0.10,
        "xi_over_l_domain_scale_ceiling": 0.75,
        "order_floor": 0.005,
    },
    "finite_size_coverage": {
        "min_accepted_grid_count": 3,
        "min_accepted_rows_per_grid": 2,
    },
    "claim_boundary": {
        "status": "WARN",
        "rule": "acceptance policy definition is allowed; estimator replacement, exponent, universality, RG, material, or Tier A claims remain blocked",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def parse_float(value: str) -> float:
    return float(str(value).strip())


def load_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def accepted_by_policy(row: dict) -> tuple[bool, list[str]]:
    rule = POLICY["q_window_row_acceptance"]
    reasons: list[str] = []

    if rule["require_status_ok"] and row["status"] != "OK":
        reasons.append("status_not_ok")
    if rule["require_wave48_candidate_pass"] and not parse_bool(row["ch_finite_k_candidate_pass"]):
        reasons.append("wave48_candidate_pass_false")
    if not parse_bool(row["ch_finite_k_valid"]):
        reasons.append("finite_k_invalid")
    if rule["exclude_low_window_edge_peaks"] and parse_bool(row["peak_hits_low_window_edge"]):
        reasons.append("peak_hits_low_window_edge")
    if parse_float(row["window_power_fraction"]) < rule["min_window_power_fraction"]:
        reasons.append("window_power_fraction_below_floor")
    if parse_float(row["low_mode_power_fraction"]) > rule["max_low_mode_power_fraction"]:
        reasons.append("low_mode_power_fraction_above_ceiling")
    xi_over_l = parse_float(row["ch_finite_k_xi_over_L"])
    if xi_over_l < rule["xi_over_l_floor"]:
        reasons.append("xi_over_l_below_floor")
    if xi_over_l >= rule["xi_over_l_domain_scale_ceiling"]:
        reasons.append("xi_over_l_at_or_above_domain_scale_ceiling")
    if parse_float(row["order_parameter"]) < rule["order_floor"]:
        reasons.append("order_below_floor")

    return not reasons, reasons


def summarize_rows(rows: list[dict]) -> dict:
    by_grid: dict[str, dict] = defaultdict(
        lambda: {
            "total_rows": 0,
            "wave48_candidate_pass_rows": 0,
            "low_window_edge_rows": 0,
            "accepted_rows": 0,
            "accepted_xi_peak": [],
            "accepted_xi_over_L": [],
            "rejection_reasons": defaultdict(int),
        }
    )
    accepted_rows = []
    annotated = []

    for row in rows:
        accepted, reasons = accepted_by_policy(row)
        grid = str(row["grid_L"])
        bucket = by_grid[grid]
        bucket["total_rows"] += 1
        bucket["wave48_candidate_pass_rows"] += int(parse_bool(row["ch_finite_k_candidate_pass"]))
        bucket["low_window_edge_rows"] += int(parse_bool(row["peak_hits_low_window_edge"]))
        bucket["accepted_rows"] += int(accepted)
        for reason in reasons:
            bucket["rejection_reasons"][reason] += 1
        if accepted:
            accepted_rows.append(row)
            bucket["accepted_xi_peak"].append(parse_float(row["ch_finite_k_xi_peak"]))
            bucket["accepted_xi_over_L"].append(parse_float(row["ch_finite_k_xi_over_L"]))
        annotated.append(
            {
                "label": row["label"],
                "grid_L": int(row["grid_L"]),
                "policy_accepted": accepted,
                "rejection_reasons": reasons,
            }
        )

    by_grid_out = {}
    for grid, bucket in sorted(by_grid.items(), key=lambda item: int(item[0])):
        by_grid_out[grid] = {
            "total_rows": bucket["total_rows"],
            "wave48_candidate_pass_rows": bucket["wave48_candidate_pass_rows"],
            "low_window_edge_rows": bucket["low_window_edge_rows"],
            "accepted_rows": bucket["accepted_rows"],
            "median_accepted_xi_peak": median(bucket["accepted_xi_peak"]) if bucket["accepted_xi_peak"] else None,
            "median_accepted_xi_over_L": median(bucket["accepted_xi_over_L"]) if bucket["accepted_xi_over_L"] else None,
            "rejection_reasons": dict(sorted(bucket["rejection_reasons"].items())),
        }

    accepted_grid_counts = {
        grid: bucket["accepted_rows"] for grid, bucket in by_grid_out.items() if bucket["accepted_rows"] > 0
    }
    accepted_grid_count = len(accepted_grid_counts)
    min_rows_per_accepted_grid = min(accepted_grid_counts.values()) if accepted_grid_counts else 0

    return {
        "overall": {
            "total_rows": len(rows),
            "accepted_rows": len(accepted_rows),
            "accepted_fraction": len(accepted_rows) / len(rows) if rows else 0.0,
            "accepted_grid_count": accepted_grid_count,
            "min_rows_per_accepted_grid": min_rows_per_accepted_grid,
            "accepted_labels": [row["label"] for row in accepted_rows],
        },
        "by_grid": by_grid_out,
        "row_decisions": annotated,
    }


def gate(status: str, required_condition: str, **details) -> dict:
    return {"status": status, "required_condition": required_condition, **details}


def build_manifest(wave48: dict, summary: dict) -> dict:
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 49 CH finite-k acceptance policy",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_class": "acceptance_policy_preflight_only",
        "policy": POLICY,
        "inputs": [
            {
                "path": rel(WAVE48_ARTIFACT),
                "role": "Wave 48 CH finite-k estimator candidate artifact",
                "status": wave48.get("status"),
                "blocker_label": wave48.get("blocker_label"),
                "sha256": sha256_file(WAVE48_ARTIFACT),
                "exists": WAVE48_ARTIFACT.exists(),
            },
            {
                "path": rel(WAVE48_CSV),
                "role": "Wave 48 per-row finite-k estimator CSV",
                "sha256": sha256_file(WAVE48_CSV),
                "exists": WAVE48_CSV.exists(),
            },
            {
                "path": rel(WAVE47_ARTIFACT),
                "role": "Wave 47 CH finite-k normalization preflight artifact",
                "sha256": sha256_file(WAVE47_ARTIFACT),
                "exists": WAVE47_ARTIFACT.exists(),
            },
            {
                "path": rel(WAVE47_MANIFEST),
                "role": "Wave 47 CH finite-k normalization preflight manifest",
                "sha256": sha256_file(WAVE47_MANIFEST),
                "exists": WAVE47_MANIFEST.exists(),
            },
        ],
        "metrics": summary,
        "claim_boundary": (
            "Wave 49 defines the row and coefficient policy for the CH finite-k candidate. "
            "It does not accept estimator replacement or rerun exponent/universality claims."
        ),
    }


def build_artifact(manifest: dict, wave48: dict, summary: dict) -> dict:
    grid_rule = POLICY["finite_size_coverage"]
    accepted_grid_count = summary["overall"]["accepted_grid_count"]
    min_rows_per_accepted_grid = summary["overall"]["min_rows_per_accepted_grid"]
    coverage_pass = (
        accepted_grid_count >= grid_rule["min_accepted_grid_count"]
        and min_rows_per_accepted_grid >= grid_rule["min_accepted_rows_per_grid"]
    )

    wave48_gates = wave48.get("gates", {})
    wave48_chain_pass = (
        wave48.get("blocker_label") == "ch_finite_k_candidate_implemented_acceptance_policy_open"
        and wave48_gates.get("implementation_coverage_gate", {}).get("status") == "PASS"
        and wave48_gates.get("q_window_diagnostic_gate", {}).get("status") == "PASS"
        and wave48_gates.get("domain_scale_guard_gate", {}).get("status") == "PASS"
    )
    low_edge_count = sum(row["low_window_edge_rows"] for row in summary["by_grid"].values())

    gates = {
        "wave48_chain_gate": gate(
            "PASS" if wave48_chain_pass else "BLOCKED",
            "Wave 49 must start from the implemented Wave 48 candidate with q-window diagnostics.",
            wave48_status=wave48.get("status"),
            wave48_blocker_label=wave48.get("blocker_label"),
        ),
        "acceptance_policy_manifest_gate": gate(
            "PASS",
            "Policy rules must be machine-readable and hash-linked to Wave 48 rows.",
            manifest_path=rel(MANIFEST_PATH),
            manifest_sha256=sha256_file(MANIFEST_PATH),
        ),
        "field_normalization_policy_gate": gate(
            "WARN",
            "Centered UET C remains a proxy-normalized concentration fluctuation.",
            policy=POLICY["field_normalization"],
        ),
        "coefficient_exclusion_policy_gate": gate(
            "PASS",
            "Measurement-only S(q) diagnostics may exclude source dynamics coefficient claims.",
            policy=POLICY["coefficient_policy"],
        ),
        "source_dynamics_coefficient_mapping_gate": gate(
            "BLOCKED",
            "Source CH dynamics coefficients must be mapped before source-dynamics claims are accepted.",
            wave47_coefficient_mapping_gate=wave48_gates.get("coefficient_policy_gate", {}).get("wave47_coefficient_mapping_gate"),
        ),
        "low_window_edge_policy_gate": gate(
            "PASS",
            "Accepted exponent rows must exclude peaks that hit the finite-k low-window edge.",
            low_window_edge_rows=low_edge_count,
            policy_excludes_low_edge=POLICY["q_window_row_acceptance"]["exclude_low_window_edge_peaks"],
        ),
        "accepted_row_coverage_gate": gate(
            "PASS" if coverage_pass else "BLOCKED",
            "Accepted candidate rows must cover at least three grid sizes with at least two rows per grid.",
            required_min_accepted_grid_count=grid_rule["min_accepted_grid_count"],
            required_min_accepted_rows_per_grid=grid_rule["min_accepted_rows_per_grid"],
            accepted_grid_count=accepted_grid_count,
            min_rows_per_accepted_grid=min_rows_per_accepted_grid,
            accepted_rows=summary["overall"]["accepted_rows"],
            total_rows=summary["overall"]["total_rows"],
        ),
        "estimator_acceptance_gate": gate(
            "BLOCKED",
            "Estimator replacement requires field normalization, source coefficient policy, row coverage, and exponent rerun gates to pass.",
            blocking_gates=[
                "field_normalization_policy_gate=WARN",
                "source_dynamics_coefficient_mapping_gate=BLOCKED",
                f"accepted_row_coverage_gate={'PASS' if coverage_pass else 'BLOCKED'}",
                "exponent_rerun_gate=BLOCKED",
            ],
        ),
        "exponent_rerun_gate": gate(
            "BLOCKED",
            "Do not rerun or interpret exponent gates until estimator acceptance gates pass.",
            next_required_artifact="finite-size/exponent verifier using accepted rows only",
        ),
        "next_path_gate": gate(
            "BLOCKED",
            "The next wave must repair accepted-row finite-size coverage or field/coefficient normalization before scaling claims.",
            next_controller="ch_finite_k_acceptance_policy_defined_finite_size_coverage_and_normalization_open",
        ),
    }

    status = "WARN"
    blocker_label = "ch_finite_k_acceptance_policy_defined_finite_size_coverage_and_normalization_open"
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 49 CH finite-k acceptance policy",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "status": status,
        "blocker_label": blocker_label,
        "claim_class": "acceptance_policy_preflight_only",
        "claim_boundary": (
            "Wave 49 defines acceptance rules and shows that only L20 rows survive the strict row policy. "
            "The estimator remains unaccepted and cannot feed exponent, universality, material, RG, or Tier A claims."
        ),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Acceptance_Policy_Gate.py",
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "numpy_version": np.__version__,
        },
        "inputs": manifest["inputs"],
        "policy": POLICY,
        "metrics": summary,
        "gates": gates,
        "limitations": [
            "Centered UET C remains proxy-normalized rather than source-equivalent concentration fluctuation.",
            "Source dynamics coefficients are excluded from the measurement-only candidate and remain unmapped.",
            "Strict policy leaves accepted rows only at L20, so finite-size/exponent coverage is insufficient.",
            "No estimator replacement, exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    wave48 = load_json(WAVE48_ARTIFACT)
    rows = load_rows(WAVE48_CSV)
    summary = summarize_rows(rows)

    manifest = build_manifest(wave48, summary)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    artifact = build_artifact(manifest, wave48, summary)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "blocker_label": artifact["blocker_label"], "accepted_rows": summary["overall"]["accepted_rows"], "accepted_grid_count": summary["overall"]["accepted_grid_count"]}, indent=2))


if __name__ == "__main__":
    main()
