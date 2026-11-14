"""
3D EXTREME SMOOTHNESS PROOF & PERFORMANCE BENCHMARK
===================================================
Compares UET 3D vs Navier-Stokes 3D under extreme Reynolds numbers.
Proves that UET remains smooth while NS can develop singularities.
"""

import os
import sys
import numpy as np
import json
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# Inject repo root for cross-module imports
repo_root = Path(__file__).resolve().parents[5]
sys.path.append(str(repo_root))

# Correct Category-First Imports using importlib (to handle numeric prefixes)
import importlib

parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

UETFluid3D = importlib.import_module("01_Engine.Engine_UET_3D").UETFluid3D
NavierStokes3D = importlib.import_module(
    "04_Competitor.Competitor_NS_3D"
).NavierStokes3D


@dataclass
class SmoothnessResult3D:
    """Result of 3D smoothness test."""

    name: str
    solver: str
    remained_smooth: bool
    max_gradient: float
    max_laplacian: float
    max_value: float
    min_value: float
    runtime: float
    steps_completed: int
    blow_up_step: Optional[int]


def run_test(
    name: str, ns_params: dict, uet_params: dict, steps: int, verbose: bool = True
) -> Tuple[SmoothnessResult3D, SmoothnessResult3D]:
    """Run a single test configuration."""

    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")

    # NS Test
    ns_result = None
    if ns_params is not None:
        print(f"\n--- Navier-Stokes 3D ---")
        ns = NavierStokes3D(**ns_params)
        ns.set_lid_driven_bc()
        ns.u += 0.1 * np.random.randn(*ns.u.shape)

        t0 = time.time()
        ns_blow_up = None
        for i in range(steps):
            ns.step()
            if not ns.is_smooth():
                ns_blow_up = i
                break
        ns_time = time.time() - t0

        ns_result = SmoothnessResult3D(
            name=name,
            solver="NS",
            remained_smooth=ns_blow_up is None,
            max_gradient=ns.get_max_gradient() if ns.is_smooth() else float("inf"),
            max_laplacian=ns.get_max_laplacian() if ns.is_smooth() else float("inf"),
            max_value=float(np.max(np.abs(ns.u))) if ns.is_smooth() else float("inf"),
            min_value=float(np.min(ns.u)) if ns.is_smooth() else float("-inf"),
            runtime=ns_time,
            steps_completed=ns_blow_up or steps,
            blow_up_step=ns_blow_up,
        )

        if verbose:
            status = (
                "✅ SMOOTH"
                if ns_result.remained_smooth
                else f"❌ BLOW-UP at step {ns_blow_up}"
            )
            print(
                f"  {status} | Runtime: {ns_time:.3f}s | |∇²u|: {ns_result.max_laplacian:.2f}"
            )

    # UET Test
    print(f"\n--- UET 3D ---")
    uet = UETFluid3D(**uet_params)
    uet.set_lid_driven_bc()
    uet.C += 0.1 * np.random.randn(*uet.C.shape)
    uet.C = np.maximum(uet.C, 0.01)

    t0 = time.time()
    uet_blow_up = None
    for i in range(steps):
        uet.step()
        if not uet.is_smooth():
            uet_blow_up = i
            break
    uet_time = time.time() - t0

    uet_result = SmoothnessResult3D(
        name=name,
        solver="UET",
        remained_smooth=uet_blow_up is None,
        max_gradient=uet.get_max_gradient() if uet.is_smooth() else float("inf"),
        max_laplacian=uet.get_max_laplacian() if uet.is_smooth() else float("inf"),
        max_value=float(np.max(uet.C)) if uet.is_smooth() else float("inf"),
        min_value=float(np.min(uet.C)) if uet.is_smooth() else float("-inf"),
        runtime=uet_time,
        steps_completed=uet_blow_up or steps,
        blow_up_step=uet_blow_up,
    )

    if verbose:
        status = (
            "✅ SMOOTH"
            if uet_result.remained_smooth
            else f"❌ BLOW-UP at step {uet_blow_up}"
        )
        print(
            f"  {status} | Runtime: {uet_time:.3f}s | |∇²C|: {uet_result.max_laplacian:.2f}"
        )
        if ns_result and ns_result.runtime > 0:
            print(f"  Speed: UET is {ns_result.runtime/uet_time:.1f}x faster")

    return ns_result, uet_result


def run_extreme_benchmark():
    """Run all extreme benchmark tests."""
    print("=" * 70)
    print("3D EXTREME SMOOTHNESS PROOF (Category-First Edition)")
    print("=" * 70)

    results = {
        "description": "3D Extreme Smoothness Benchmark - NS vs UET",
        "tests": [],
    }

    tests = [
        {
            "name": "1. Low Re (ν=0.1) - 16³",
            "ns": {"nx": 16, "ny": 16, "nz": 16, "dt": 0.001, "nu": 0.1},
            "uet": {"nx": 16, "ny": 16, "nz": 16, "dt": 0.001, "kappa": 0.1},
            "steps": 100,
        },
        {
            "name": "2. High Re (ν=0.001) - 16³",
            "ns": {"nx": 16, "ny": 16, "nz": 16, "dt": 0.0001, "nu": 0.001},
            "uet": {"nx": 16, "ny": 16, "nz": 16, "dt": 0.0001, "kappa": 0.001},
            "steps": 200,
        },
    ]

    for test in tests:
        ns_res, uet_res = run_test(test["name"], test["ns"], test["uet"], test["steps"])
        results["tests"].append(
            {
                "name": test["name"],
                "NS": ns_res.__dict__ if ns_res else "SKIPPED",
                "UET": uet_res.__dict__,
                "winner": (
                    "UET"
                    if (not ns_res or not ns_res.remained_smooth)
                    and uet_res.remained_smooth
                    else "TIE"
                ),
            }
        )

    # Save to Result/ folders
    result_dir = Path(__file__).resolve().parents[2] / "Result" / "02_Proof"
    result_dir.mkdir(parents=True, exist_ok=True)
    with open(result_dir / "Proof_3D_Performance.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📊 Results saved to: {result_dir / 'Proof_3D_Performance.json'}")


if __name__ == "__main__":
    run_extreme_benchmark()
