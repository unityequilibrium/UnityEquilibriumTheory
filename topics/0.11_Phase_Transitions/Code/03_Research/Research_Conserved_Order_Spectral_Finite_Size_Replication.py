"""
Wave 21 conserved-order spectral finite-size replication diagnostic.

Wave 20 repaired the seed-margin gate at L=16 for one seed set. This verifier
asks the next required question: does the same spinodal-window target replicate
over multiple grid sizes and a fresh seed set?

The artifact is deliberately claim-bounded. Passing seed-margin on one grid is
not finite-size scaling, and this diagnostic still does not fit critical
exponents or validate RG/material claims.
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
ARTIFACT_PATH = (
    TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_finite_size_replication.json"
)
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_finite_size_replication_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE19_SCRIPT_PATH = (
    TOPIC_DIR / "Code" / "03_Research" / "Research_Conserved_Order_Spectral_Spinodal_Window.py"
)
WAVE20_ARTIFACT_PATH = (
    TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_seed_margin.json"
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


def summarize_rows(rows: list[dict[str, float | int | str | bool]]) -> dict[str, Any]:
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


def run_finite_size_replication_diagnostic() -> dict[str, Any]:
    wave19_helpers = load_wave19_helpers()
    wave20 = load_json(WAVE20_ARTIFACT_PATH) if WAVE20_ARTIFACT_PATH.exists() else {}

    grid_sizes = [8, 12, 16]
    seed_sets = {
        "wave20_seed_set": [20001, 20002, 20003],
        "fresh_seed_set": [21001, 21002, 21003],
    }
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    steps = 4000
    xi_threshold = 0.20
    order_floor = 0.005

    rows: list[dict[str, float | int | str | bool]] = []
    for grid_L in grid_sizes:
        for seed_set_label, seeds in seed_sets.items():
            for seed in seeds:
                row = wave19_helpers.run_case(
                    label=f"L{grid_L}_{seed_set_label}_seed{seed}",
                    repair_family="finite_size_replication",
                    replicate_group=f"L{grid_L}_{seed_set_label}",
                    grid_L=grid_L,
                    temperature=temperature,
                    steps=steps,
                    dt=dt,
                    dx=dx,
                    kappa=kappa,
                    seed=seed,
                )
                row["seed_set"] = seed_set_label
                rows.append(row)

    stable_rows = [row for row in rows if row["status"] == "OK"]
    positive_margin_rows = [row for row in stable_rows if float(row["spinodal_margin"]) > 0.0]
    by_grid: dict[str, Any] = {}
    by_seed_set: dict[str, Any] = {}

    for grid_L in grid_sizes:
        grid_rows = [row for row in stable_rows if int(row["grid_L"]) == grid_L]
        by_grid[str(grid_L)] = summarize_rows(grid_rows)
        by_grid[str(grid_L)]["seed_sets"] = {
            seed_set_label: summarize_rows(
                [row for row in grid_rows if str(row["seed_set"]) == seed_set_label]
            )
            for seed_set_label in seed_sets
        }

    for seed_set_label in seed_sets:
        by_seed_set[seed_set_label] = summarize_rows(
            [row for row in stable_rows if str(row["seed_set"]) == seed_set_label]
        )

    weakest_grid_label, weakest_grid_summary = min(
        by_grid.items(), key=lambda item: float(item[1]["min_xi_over_L"])
    )
    weakest_case = min(stable_rows, key=lambda row: float(row["xi_over_L"]))
    best_case = max(stable_rows, key=lambda row: float(row["xi_over_L"]))

    wave20_chain_gate = {
        "status": (
            "PASS"
            if wave20.get("blocker_label")
            == "spectral_core_seed_margin_passes_single_grid_needs_finite_size_replication"
            else "BLOCKED"
        ),
        "required_condition": "Wave 21 must start from the Wave 20 finite-size replication blocker.",
        "wave20_status": wave20.get("status"),
        "wave20_blocker_label": wave20.get("blocker_label"),
    }
    finite_size_coverage_gate = {
        "status": "PASS" if len(stable_rows) == len(rows) and len(positive_margin_rows) == len(rows) else "BLOCKED",
        "required_condition": "All grid/seed cases must be stable and inside the positive spinodal-margin window.",
        "grid_sizes": grid_sizes,
        "seed_sets": seed_sets,
        "stable_case_count": len(stable_rows),
        "positive_margin_case_count": len(positive_margin_rows),
        "case_count": len(rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    grid_replication_gate = {
        "status": (
            "PASS"
            if all(summary["pass_fraction"] >= 0.75 for summary in by_grid.values())
            and all(summary["min_xi_over_L"] >= xi_threshold for summary in by_grid.values())
            and all(summary["min_order_parameter"] >= order_floor for summary in by_grid.values())
            else "BLOCKED"
        ),
        "required_condition": "Every grid size must pass at least 75% of cases and keep minimum xi/L and order above thresholds.",
        "xi_threshold": xi_threshold,
        "order_floor": order_floor,
        "by_grid": by_grid,
        "weakest_grid": {
            "grid_L": weakest_grid_label,
            "summary": weakest_grid_summary,
        },
        "weakest_case": weakest_case,
    }
    seed_set_generalization_gate = {
        "status": (
            "PASS"
            if all(summary["pass_fraction"] >= 0.75 for summary in by_seed_set.values())
            and all(summary["min_xi_over_L"] >= xi_threshold for summary in by_seed_set.values())
            else "BLOCKED"
        ),
        "required_condition": "The finite-size window should pass both the Wave 20 seed set and a fresh seed set.",
        "by_seed_set": by_seed_set,
        "xi_threshold": xi_threshold,
    }
    exponent_claim_gate = {
        "status": "BLOCKED",
        "required_condition": "Finite-size replication is not an exponent fit; beta/nu/universality gates must be rerun separately.",
        "claim_boundary": "Do not infer a critical exponent or universality class from this replication diagnostic.",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic can only narrow the finite-size blocker.",
        "claim_boundary": "No material, RG, or universality claim is supported by this artifact.",
    }

    if grid_replication_gate["status"] != "PASS":
        blocker_label = "spectral_core_finite_size_replication_not_robust"
    elif seed_set_generalization_gate["status"] != "PASS":
        blocker_label = "spectral_core_finite_size_seed_generalization_not_robust"
    else:
        blocker_label = "spectral_core_finite_size_window_passes_needs_exponent_gate"

    status = "WARN" if exponent_claim_gate["status"] == "BLOCKED" else "PASS"

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
    if WAVE20_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE20_ARTIFACT_PATH),
                "sha256": hash_file(WAVE20_ARTIFACT_PATH),
                "role": "Wave 20 seed-margin controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 21 conserved_order_spectral_v1 finite-size replication diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Finite_Size_Replication.py",
        "status": status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_finite_size_replication_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_sizes": grid_sizes,
            "seed_sets": seed_sets,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "steps": steps,
            "xi_threshold": xi_threshold,
            "order_floor": order_floor,
            "case_count": len(rows),
        },
        "metrics": {
            "by_grid": by_grid,
            "by_seed_set": by_seed_set,
            "best_case": best_case,
            "weakest_case": weakest_case,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave20_chain_gate": wave20_chain_gate,
            "finite_size_coverage_gate": finite_size_coverage_gate,
            "grid_replication_gate": grid_replication_gate,
            "seed_set_generalization_gate": seed_set_generalization_gate,
            "exponent_claim_gate": exponent_claim_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted finite-size replication diagnostic for one normalized spinodal window.",
            "The diagnostic does not fit beta, nu, Binder crossings, or universal scaling functions.",
            "The result must not be used as material validation, RG closure, or a universality-class claim.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims until finite-size replication and separate exponent/universality gates pass.",
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
    result = run_finite_size_replication_diagnostic()
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
