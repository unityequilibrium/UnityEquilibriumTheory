import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

import sys
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Setup local imports for Topic 0.10 (Handling numeric folder names)
topic_path = root_path / "docs" / "topics" / "0.10_Fluid_Dynamics_Chaos"
engine_path = topic_path / "Code" / "01_Engine"
competitor_path = topic_path / "Code" / "04_Competitor"

if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))
if str(competitor_path) not in sys.path:
    sys.path.insert(0, str(competitor_path))

from docs.core.uet_glass_box import UETPathManager, UETMetricLogger
from Competitor_NS_2D import NavierStokesSolver
from Engine_UET_2D import UETFluidSolver
from docs.core.uet_master_equation import UETParameters

import numpy as np
import json
import time


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def compare_lid_driven_cavity():
    """
    Compare NS and UET on lid-driven cavity problem.
    """
    print("=" * 70)
    print("COMPARISON: Lid-Driven Cavity")
    print("=" * 70)

    nx, ny = 32, 32
    steps = 500

    results = {
        "test_case": "lid_driven_cavity",
        "grid": f"{nx}x{ny}",
        "steps": steps,
        "solvers": {},
    }

    # ===== NS SOLVER =====
    print("\n--- Navier-Stokes Solver ---")
    ns = NavierStokesSolver(nx=nx, ny=ny, dt=0.001)
    ns.set_boundary_conditions("lid_driven")

    t0 = time.time()
    ns.run(steps=steps, verbose=False)
    ns_time = time.time() - t0

    ns_energy = ns.energy_history[-1]
    ns_max_v = np.max(ns.get_velocity_magnitude())
    ns_stable = not (np.isnan(ns.u).any() or np.isinf(ns.u).any())

    print(f"  Runtime: {ns_time:.3f}s")
    print(f"  Final KE: {ns_energy:.4e}")
    print(f"  Max velocity: {ns_max_v:.4f}")
    print(f"  Stable: {ns_stable}")

    results["solvers"]["NS"] = {
        "runtime_s": ns_time,
        "final_energy": ns_energy,
        "max_velocity": ns_max_v,
        "stable": ns_stable,
    }

    # ===== UET SOLVER =====
    print("\n--- UET Solver ---")
    params = UETParameters(kappa=0.01, beta=0.1, alpha=1.0)
    uet = UETFluidSolver(nx=nx, ny=ny, dt=0.001, params=params)
    uet.set_boundary_conditions("lid_driven")

    t0 = time.time()
    uet.run(steps=steps, verbose=False)
    uet_time = time.time() - t0

    uet_omega = uet.omega_history[-1]
    uet_energy = uet.energy_history[-1]
    uet_max_v = np.max(uet.get_velocity_magnitude())
    uet_stable = not (np.isnan(uet.C).any() or np.isinf(uet.C).any())

    print(f"  Runtime: {uet_time:.3f}s")
    print(f"  Final Ω: {uet_omega:.4e}")
    print(f"  Final energy proxy: {uet_energy:.4e}")
    print(f"  Max velocity: {uet_max_v:.4f}")
    print(f"  Stable: {uet_stable}")

    results["solvers"]["UET"] = {
        "runtime_s": uet_time,
        "final_omega": uet_omega,
        "final_energy": uet_energy,
        "max_velocity": uet_max_v,
        "stable": uet_stable,
    }

    # ===== COMPARISON =====
    print("\n--- Comparison ---")
    print(f"  Speed ratio (NS/UET): {ns_time/uet_time:.2f}x")
    print(f"  Both stable: {ns_stable and uet_stable}")

    results["comparison"] = {
        "speed_ratio_ns_over_uet": ns_time / uet_time,
        "both_stable": ns_stable and uet_stable,
    }

    return results


def compare_stability_high_re():
    """
    Compare stability at high Reynolds number (low viscosity).
    This is where NS may have issues and UET should show advantage.
    """
    print("\n" + "=" * 70)
    print("COMPARISON: High Reynolds Number Stability")
    print("=" * 70)

    nx, ny = 32, 32
    steps = 200

    results = {
        "test_case": "high_reynolds_stability",
        "grid": f"{nx}x{ny}",
        "steps": steps,
        "solvers": {},
    }

    # ===== NS with very low viscosity =====
    print("\n--- Navier-Stokes (low viscosity) ---")
    ns = NavierStokesSolver(nx=nx, ny=ny, dt=0.0001)
    ns.fluid.viscosity = 0.0001  # Very low → high Re
    ns.nu = ns.fluid.viscosity / ns.fluid.density
    ns.set_boundary_conditions("lid_driven")

    # Add perturbation
    ns.u += 0.01 * np.random.randn(*ns.u.shape)

    t0 = time.time()
    try:
        ns.run(steps=steps, verbose=False)
        ns_stable = not (np.isnan(ns.u).any() or np.isinf(ns.u).any())
    except Exception as e:
        ns_stable = False
        print(f"  NS crashed: {e}")
    ns_time = time.time() - t0

    ns_re = ns.compute_reynolds_number() if ns_stable else float("inf")
    print(f"  Reynolds: {ns_re:.0f}")
    print(f"  Stable: {ns_stable}")

    results["solvers"]["NS"] = {
        "reynolds": ns_re if ns_stable else "crashed",
        "stable": ns_stable,
        "runtime_s": ns_time,
    }

    # ===== UET with low kappa (high Re equivalent) =====
    print("\n--- UET (low kappa = high Re equivalent) ---")
    params = UETParameters(kappa=0.0001, beta=0.01, alpha=1.0)
    uet = UETFluidSolver(nx=nx, ny=ny, dt=0.0001, params=params)
    uet.set_boundary_conditions("lid_driven")

    # Add perturbation
    uet.C += 0.01 * np.random.randn(nx, ny)

    t0 = time.time()
    try:
        uet.run(steps=steps, verbose=False)
        uet_stable = not (np.isnan(uet.C).any() or np.isinf(uet.C).any())
    except Exception as e:
        uet_stable = False
        print(f"  UET crashed: {e}")
    uet_time = time.time() - t0

    print(f"  Stable: {uet_stable}")
    print(f"  (UET has natural regularization via V(C) bounded)")

    results["solvers"]["UET"] = {
        "stable": uet_stable,
        "kappa": params.kappa,
        "runtime_s": uet_time,
    }

    # ===== COMPARISON =====
    print("\n--- Stability Comparison ---")
    if uet_stable and not ns_stable:
        print("  ✅ UET ADVANTAGE: UET stable where NS crashed!")
        results["comparison"] = {"winner": "UET", "reason": "stability at high Re"}
    elif ns_stable and uet_stable:
        print("  ⚖️ TIE: Both stable")
        results["comparison"] = {"winner": "tie", "reason": "both stable"}
    elif not ns_stable and not uet_stable:
        print("  ❌ BOTH FAILED: Both unstable at this Re")
        results["comparison"] = {"winner": "none", "reason": "both unstable"}
    else:
        print("  ⚠️ NS stable, UET crashed (unexpected)")
        results["comparison"] = {"winner": "NS", "reason": "NS more stable"}

    return results


def run_all_comparisons():
    """Run all comparison tests and save results."""
    print("\n" + "=" * 70)
    print("UET vs NAVIER-STOKES: COMPREHENSIVE COMPARISON")
    print("=" * 70)

    all_results = {
        "date": "2026-01-11",
        "description": "Head-to-head comparison of NS and UET fluid solvers",
        "tests": [],
    }

    # Initialize Standard Logger
    result_dir = UETPathManager.get_result_dir(
                topic_id="0.10",
                experiment_name="Research_3D_Comparison",
                pillar="03_Research",
                category="log",
            )
    logger = None
    try:
        logger = UETMetricLogger("Fluid_Comparison_NS_vs_UET", topic_id="0.10", category="log")
        logger.set_metadata(
            {
                "test_suite": "Lid Driven Cavity + High Re",
                "competitor": "Navier-Stokes Solver",
            }
        )
        print(f"\\n📂 Logging detailed results to: {logger.run_dir}")
    except Exception:
        pass

    # Run tests
    all_results["tests"].append(compare_lid_driven_cavity())
    all_results["tests"].append(compare_stability_high_re())

    # Save results
    # Save results to standardized Result pillar
    if logger:
        result_dir = logger.run_dir
    else:
        result_dir = (
            UETPathManager.get_result_dir(
                topic="0.10_Fluid_Dynamics_Chaos",
                name="Research_3D_Comparison",
                pillar="03_Research",
                category="log",
            )
            / "03_Research"
        )
        result_dir.mkdir(parents=True, exist_ok=True)

    result_file = result_dir / "ns_vs_uet_comparison.json"
    with open(result_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n📊 Results saved to: {result_file}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for test in all_results["tests"]:
        name = test["test_case"]
        comparison = test.get("comparison", {})
        winner = comparison.get("winner", "unknown")
        reason = comparison.get("reason", "")
        print(f"  {name}: {winner} ({reason})")

    # Save Final Report
    if logger:
        logger.log_step(
            step=1,
            time_val=1.0,
            omega=1.0,
            extra_metrics={"total_tests": len(all_results["tests"])},
        )
        logger.save_report()

    return all_results


if __name__ == "__main__":
    run_all_comparisons()
