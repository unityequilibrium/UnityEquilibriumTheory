"""
Wave 22 conserved-order spectral L16 relaxation-repair diagnostic.

Wave 21 showed that the seed-margin-passing spinodal window does not replicate
robustly at L=16 under a fresh seed set. This verifier asks a narrower repair
question: is simply extending relaxation enough to restore the L=16 fresh-seed
xi/L margin?

The answer controls the next repair path. If longer runs do not lift the worst
fresh-seed cases over the threshold, the next work should revise the window,
estimator, or scaling design rather than rerunning longer single-grid cases.
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
    TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_l16_relaxation_repair.json"
)
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_l16_relaxation_repair_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE19_SCRIPT_PATH = (
    TOPIC_DIR / "Code" / "03_Research" / "Research_Conserved_Order_Spectral_Spinodal_Window.py"
)
WAVE21_ARTIFACT_PATH = (
    TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_finite_size_replication.json"
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


def run_l16_relaxation_repair_diagnostic() -> dict[str, Any]:
    wave19_helpers = load_wave19_helpers()
    wave21 = load_json(WAVE21_ARTIFACT_PATH) if WAVE21_ARTIFACT_PATH.exists() else {}

    grid_L = 16
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    seeds = [21001, 21002, 21003]
    step_groups = [4000, 4800, 5600]
    xi_threshold = 0.20
    order_floor = 0.005

    rows: list[dict[str, float | int | str | bool]] = []
    for steps in step_groups:
        for seed in seeds:
            rows.append(
                wave19_helpers.run_case(
                    label=f"L16_s{steps}_fresh_seed{seed}",
                    repair_family="l16_relaxation_repair",
                    replicate_group=f"L16_s{steps}",
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
    by_steps = {
        str(steps): summarize_rows(
            [row for row in stable_rows if int(row["steps"]) == steps]
        )
        for steps in step_groups
    }
    baseline_summary = by_steps["4000"]
    longest_summary = by_steps["5600"]
    weakest_case = min(stable_rows, key=lambda row: float(row["xi_over_L"]))
    best_case = max(stable_rows, key=lambda row: float(row["xi_over_L"]))

    wave21_chain_gate = {
        "status": (
            "PASS"
            if wave21.get("blocker_label") == "spectral_core_finite_size_replication_not_robust"
            else "BLOCKED"
        ),
        "required_condition": "Wave 22 must start from the Wave 21 finite-size replication blocker.",
        "wave21_status": wave21.get("status"),
        "wave21_blocker_label": wave21.get("blocker_label"),
    }
    l16_case_coverage_gate = {
        "status": "PASS" if len(stable_rows) == len(rows) and len(positive_margin_rows) == len(rows) else "BLOCKED",
        "required_condition": "All L16 fresh-seed relaxation cases must be stable and inside the positive spinodal-margin window.",
        "stable_case_count": len(stable_rows),
        "positive_margin_case_count": len(positive_margin_rows),
        "case_count": len(rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    relaxation_repair_gate = {
        "status": (
            "PASS"
            if longest_summary["pass_fraction"] >= 0.75
            and longest_summary["min_xi_over_L"] >= xi_threshold
            and longest_summary["min_order_parameter"] >= order_floor
            else "BLOCKED"
        ),
        "required_condition": "The longest tested relaxation group must pass at least 75% of fresh seeds and keep minimum xi/L and order above thresholds.",
        "xi_threshold": xi_threshold,
        "order_floor": order_floor,
        "by_steps": by_steps,
        "baseline_steps": 4000,
        "baseline_summary": baseline_summary,
        "longest_steps": 5600,
        "longest_summary": longest_summary,
        "weakest_case": weakest_case,
        "best_case": best_case,
    }
    order_signal_gate = {
        "status": "PASS" if all(summary["min_order_parameter"] >= order_floor for summary in by_steps.values()) else "BLOCKED",
        "required_condition": "Order signal should remain above the declared floor in every relaxation group.",
        "order_floor": order_floor,
        "by_steps": by_steps,
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "If relaxation-only repair is blocked, do not rerun longer single-grid cases as the next default path.",
        "claim_boundary": "Next work should revise the finite-size window, estimator, or scaling design before exponent claims.",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic cannot validate exponent, material, RG, or universality claims.",
        "claim_boundary": "A blocked relaxation repair only narrows the next design requirement.",
    }

    blocker_label = (
        "spectral_core_l16_relaxation_repair_passes_needs_finite_size_rerun"
        if relaxation_repair_gate["status"] == "PASS"
        else "spectral_core_l16_relaxation_only_repair_blocked"
    )
    status = "WARN"

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
    if WAVE21_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE21_ARTIFACT_PATH),
                "sha256": hash_file(WAVE21_ARTIFACT_PATH),
                "role": "Wave 21 finite-size replication controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 22 conserved_order_spectral_v1 L16 relaxation-repair diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_L16_Relaxation_Repair.py",
        "status": status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_l16_relaxation_repair_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_L": grid_L,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "seeds": seeds,
            "step_groups": step_groups,
            "xi_threshold": xi_threshold,
            "order_floor": order_floor,
            "case_count": len(rows),
        },
        "metrics": {
            "by_steps": by_steps,
            "weakest_case": weakest_case,
            "best_case": best_case,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave21_chain_gate": wave21_chain_gate,
            "l16_case_coverage_gate": l16_case_coverage_gate,
            "relaxation_repair_gate": relaxation_repair_gate,
            "order_signal_gate": order_signal_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted L16 fresh-seed relaxation diagnostic, not a finite-size scaling rerun.",
            "Longer relaxation increases order amplitude but does not by itself establish a robust xi/L margin in this artifact.",
            "The result must not be used as material validation, RG closure, or a universality-class claim.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims from relaxation-only L16 diagnostics.",
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
    result = run_l16_relaxation_repair_diagnostic()
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
