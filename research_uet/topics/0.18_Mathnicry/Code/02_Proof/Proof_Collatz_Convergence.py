"""
Proof_Collatz_Convergence.py - Topic 0.18
=========================================
Massive Scale Validation of the Collatz Conjecture.
Goal: Scan a large range of integers and verify they all reach N=1.
Logs the distribution of 'Step Counts' and 'Max Potential' across the sample.
"""

import sys
import time
from pathlib import Path

# Add engine to path
current_path = Path(__file__).resolve()
engine_dir = current_path.parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

from Engine_Collatz_Field import CollatzFieldEngine


def run_convergence_proof(n_range: int = 10000, start_offset: int = 1):
    print(
        f"🔬 UET MASSIVE PROOF: Testing {n_range} numbers starting from {start_offset}..."
    )
    engine = CollatzFieldEngine()

    start_time = time.time()
    results = {
        "verified_count": 0,
        "failed_count": 0,
        "max_steps": 0,
        "max_potential": 0.0,
        "total_field_states": 0,
    }

    for n in range(start_offset, start_offset + n_range):
        trajectory = engine.solve_trajectory(n, max_steps=5000)

        if trajectory[-1]["n"] == 1:
            results["verified_count"] += 1
            steps = len(trajectory) - 1
            results["max_steps"] = max(results["max_steps"], steps)
            results["max_potential"] = max(
                results["max_potential"], max(p["omega"] for p in trajectory)
            )
            results["total_field_states"] += len(trajectory)
        else:
            results["failed_count"] += 1
            print(f"   ⚠️ WARNING: N={n} did not converge within limit.")

        if (n - start_offset + 1) % 2000 == 0:
            print(f"   ... Progress: {n - start_offset + 1}/{n_range} verified.")

    end_time = time.time()

    print("\n" + "=" * 50)
    print("📋 PROOF SUMMARY")
    print("=" * 50)
    print(f"   Numbers Tested:  {results['verified_count']}")
    print(f"   Failures Found:  {results['failed_count']}")
    print(f"   Max Steps:       {results['max_steps']}")
    print(f"   Max Potential:   {results['max_potential']:.4f}")
    print(f"   Total States:    {results['total_field_states']}")
    print(f"   Execution Time:  {end_time - start_time:.2f}s")
    print("=" * 50)

    if results["failed_count"] == 0:
        print("✅ CONCLUSION: All tested integers drain into the Unity Sink (1).")
        print("   The UET 'Information Dissipation' model is empirically stable.")
    else:
        print(
            "❌ CONCLUSION: Anomalous loops detected. Further field analysis required."
        )


if __name__ == "__main__":
    # Test 10k numbers as a benchmark
    run_convergence_proof(n_range=10000)
