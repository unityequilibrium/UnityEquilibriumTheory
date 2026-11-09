"""
Wave 20 conserved-order spectral seed-margin repair diagnostic.

Wave 19 found a single-grid spinodal-window candidate, but the target seed
replicate margin was not robust. This verifier keeps the same normalized
window, extends relaxation, and asks a narrower question: does the candidate
window pass the declared xi/L and order-signal thresholds across target seeds?

Passing this diagnostic is not a finite-size scaling result. It only decides
whether the next blocker can move from seed-margin repair to multi-grid
replication.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET docs root not found")


ROOT = _bootstrap()

from docs.core.uet_master_equation import CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_seed_margin.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_seed_margin_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE19_SCRIPT_PATH = (
    TOPIC_DIR / "Code" / "03_Research" / "Research_Conserved_Order_Spectral_Spinodal_Window.py"
)
WAVE19_ARTIFACT_PATH = (
    TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_spinodal_window.json"
)


def load_wave19_helpers():
    spec = importlib.util.spec_from_file_location("wave19_spinodal_window", WAVE19_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Wave 19 helper script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_group(rows: list[dict[str, float | int | str | bool]]) -> dict[str, Any]:
    xi_values = np.array([float(row["xi_over_L"]) for row in rows], dtype=float)
    order_values = np.array([float(row["order_parameter"]) for row in rows], dtype=float)
    pass_count = sum(1 for row in rows if bool(row["order_preserving_xi_pass"]))
    return {
        "case_count": len(rows),
        "pass_count": pass_count,
        "pass_fraction": float(pass_count / len(rows)) if rows else 0.0,
        "min_xi_over_L": float(np.min(xi_values)) if len(xi_values) else float("nan"),
        "median_xi_over_L": float(np.median(xi_values)) if len(xi_values) else float("nan"),
        "max_xi_over_L": float(np.max(xi_values)) if len(xi_values) else float("nan"),
        "min_order_parameter": float(np.min(order_values)) if len(order_values) else float("nan"),
        "median_order_parameter": float(np.median(order_values)) if len(order_values) else float("nan"),
    }


def run_seed_margin_diagnostic() -> dict[str, Any]:
    wave19_helpers = load_wave19_helpers()
    wave19 = load_json(WAVE19_ARTIFACT_PATH) if WAVE19_ARTIFACT_PATH.exists() else {}

    grid_L = 16
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    xi_threshold = 0.20
    order_floor = 0.005
    seeds = [20001, 20002, 20003, 20004]
    groups = [
        ("t0900_k0100_s2400", 2400),
        ("t0900_k0100_s3200", 3200),
        ("t0900_k0100_s4000", 4000),
    ]
    target_group = "t0900_k0100_s4000"

    rows: list[dict[str, float | int | str | bool]] = []
    for group_label, steps in groups:
        for seed in seeds:
            rows.append(
                wave19_helpers.run_case(
                    label=f"{group_label}_seed{seed}",
                    repair_family="seed_margin_repair",
                    replicate_group=group_label,
                    grid_L=grid_L,
                    temperature=temperature,
                    steps=steps,
                    dt=dt,
                    dx=dx,
                    kappa=kappa,
                    seed=seed,
                )
            )

    stable_rows = [row for row in rows if row["status"] == "OK"]
    positive_margin_rows = [row for row in stable_rows if float(row["spinodal_margin"]) > 0.0]
    group_summaries = {
        group_label: summarize_group([row for row in stable_rows if row["replicate_group"] == group_label])
        for group_label, _ in groups
    }
    baseline_summary = group_summaries["t0900_k0100_s2400"]
    intermediate_summary = group_summaries["t0900_k0100_s3200"]
    target_summary = group_summaries[target_group]
    target_rows = [row for row in stable_rows if row["replicate_group"] == target_group]
    best_target_case = max(target_rows, key=lambda row: float(row["xi_over_L"]))
    weakest_target_case = min(target_rows, key=lambda row: float(row["xi_over_L"]))

    wave19_chain_gate = {
        "status": (
            "PASS"
            if wave19.get("blocker_label") == "spectral_core_spinodal_window_seed_margin_not_robust"
            else "BLOCKED"
        ),
        "required_condition": "Wave 20 must start from the Wave 19 seed-margin blocker.",
        "wave19_status": wave19.get("status"),
        "wave19_blocker_label": wave19.get("blocker_label"),
    }
    seed_group_coverage_gate = {
        "status": "PASS" if len(stable_rows) == len(rows) and len(positive_margin_rows) == len(rows) else "BLOCKED",
        "required_condition": "All seed-margin repair cases must be stable and inside the positive spinodal-margin window.",
        "stable_case_count": len(stable_rows),
        "positive_margin_case_count": len(positive_margin_rows),
        "case_count": len(rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    seed_margin_repair_gate = {
        "status": (
            "PASS"
            if target_summary["pass_fraction"] >= 0.75
            and target_summary["min_xi_over_L"] >= xi_threshold
            and target_summary["min_order_parameter"] >= order_floor
            else "BLOCKED"
        ),
        "required_condition": "The target seed group must pass at least 75% of seeds and keep every target seed above xi/L and order thresholds.",
        "target_group": target_group,
        "target_summary": target_summary,
        "xi_threshold": xi_threshold,
        "order_floor": order_floor,
        "best_target_case": best_target_case,
        "weakest_target_case": weakest_target_case,
    }
    relaxation_margin_gate = {
        "status": (
            "PASS"
            if target_summary["pass_count"] > baseline_summary["pass_count"]
            and target_summary["min_xi_over_L"] > baseline_summary["min_xi_over_L"]
            else "BLOCKED"
        ),
        "required_condition": "The extended target should improve seed pass count and minimum xi/L over the 2400-step baseline group.",
        "baseline_group": "t0900_k0100_s2400",
        "baseline_summary": baseline_summary,
        "intermediate_group": "t0900_k0100_s3200",
        "intermediate_summary": intermediate_summary,
        "target_group": target_group,
        "target_summary": target_summary,
    }
    finite_size_replication_gate = {
        "status": "BLOCKED",
        "required_condition": "Seed-margin repair remains single-grid until the target window is replicated over multiple grid sizes.",
        "claim_boundary": "Do not treat a single-grid seed-margin pass as finite-size scaling or universality evidence.",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic may narrow the blocker but cannot validate universality, material, or RG closure claims.",
        "claim_boundary": "Use this artifact only to select the next finite-size replication design.",
    }

    if seed_margin_repair_gate["status"] != "PASS":
        blocker_label = "spectral_core_spinodal_window_seed_margin_not_robust"
    else:
        blocker_label = "spectral_core_seed_margin_passes_single_grid_needs_finite_size_replication"

    status = "WARN" if finite_size_replication_gate["status"] == "BLOCKED" else "PASS"

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    inputs = [
        {
            "path": relpath(CORE_ENGINE_PATH),
            "sha256": hash_file(CORE_ENGINE_PATH),
            "role": "core spectral conserved-order implementation",
        },
        {
            "path": relpath(WAVE19_SCRIPT_PATH),
            "sha256": hash_file(WAVE19_SCRIPT_PATH),
            "role": "Wave 19 metric helper and spinodal-window verifier",
        },
    ]
    if WAVE19_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE19_ARTIFACT_PATH),
                "sha256": hash_file(WAVE19_ARTIFACT_PATH),
                "role": "Wave 19 seed-margin controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 20 conserved_order_spectral_v1 seed-margin repair diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Seed_Margin.py",
        "status": status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_seed_margin_repair_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_L": grid_L,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "xi_threshold": xi_threshold,
            "order_floor": order_floor,
            "seeds": seeds,
            "step_groups": [steps for _, steps in groups],
            "case_count": len(rows),
        },
        "metrics": {
            "group_summaries": group_summaries,
            "best_target_case": best_target_case,
            "weakest_target_case": weakest_target_case,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave19_chain_gate": wave19_chain_gate,
            "seed_group_coverage_gate": seed_group_coverage_gate,
            "seed_margin_repair_gate": seed_margin_repair_gate,
            "relaxation_margin_gate": relaxation_margin_gate,
            "finite_size_replication_gate": finite_size_replication_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted single-grid seed-margin repair diagnostic, not a full finite-size scaling sweep.",
            "The target group passes the declared seed-margin gate only for L=16 under normalized parameters.",
            "The result narrows the next blocker to finite-size replication; it does not validate material, RG, or universality claims.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims until this window passes finite-size replication, exponent, material, and RG gates.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy_version": np.__version__,
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_seed_margin_diagnostic()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "blocker_label": result["blocker_label"],
            },
            indent=2,
        )
    )
