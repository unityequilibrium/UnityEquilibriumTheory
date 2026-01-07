#!/usr/bin/env python3
"""
Determinism Test for UET

This script verifies that UET simulations are fully deterministic:
Given the same configuration and random seed, the output should be
identical across different runs and machines.

Uses SHA256 hash comparison for verification.
"""

import hashlib
import json
import numpy as np
import sys
import os

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from uet_core.solver import run_case


def hash_result(summary: dict, rows: list) -> str:
    """Create a deterministic hash of simulation results."""
    # Extract key values that should be deterministic
    key_values = {
        "status": summary.get("status"),
        "Omega0": round(summary.get("Omega0", 0), 10),
        "OmegaT": round(summary.get("OmegaT", 0), 10),
        "steps_total": summary.get("steps_total"),
        "steps_accepted": summary.get("steps_accepted"),
        "dt_backtracks_total": summary.get("dt_backtracks_total"),
    }

    # Add first and last row hashes
    if rows:
        key_values["first_Omega"] = round(rows[0].get("Omega", 0), 10)
        key_values["last_Omega"] = round(rows[-1].get("Omega", 0), 10)

    # Create deterministic JSON string
    json_str = json.dumps(key_values, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def run_determinism_test():
    print("=" * 60)
    print("🔐 DETERMINISM TEST: Same Input → Same Output")
    print("=" * 60)

    # Standard test configuration
    config = {
        "case_id": "determinism_test",
        "model": "C_only",
        "domain": {"L": 10.0, "dim": 2, "bc": "periodic"},
        "grid": {"N": 32},
        "time": {
            "dt": 0.01,
            "T": 1.0,
            "max_steps": 1000,
            "tol_abs": 1e-10,
            "tol_rel": 1e-10,
            "backtrack": {"factor": 0.5, "max_backtracks": 20},
        },
        "params": {
            "pot": {"type": "quartic", "a": -1.0, "delta": 1.0, "s": 0.0},
            "kappa": 0.5,
            "M": 1.0,
        },
    }

    # Run 3 times with SAME seed
    seed = 12345
    hashes = []

    print(f"\nRunning 3 simulations with seed={seed}...")

    for i in range(3):
        rng = np.random.default_rng(seed)
        summary, rows = run_case(config, rng)
        h = hash_result(summary, rows)
        hashes.append(h)
        print(f"  Run {i+1}: hash={h}, status={summary['status']}, steps={summary['steps_total']}")

    # Check all hashes match
    all_same = len(set(hashes)) == 1

    print("\n" + "=" * 60)
    if all_same:
        print("✅ DETERMINISM VERIFIED!")
        print(f"   All 3 runs produced identical hash: {hashes[0]}")
    else:
        print("❌ DETERMINISM FAILED!")
        print(f"   Hashes: {hashes}")
    print("=" * 60)

    # Also test different seeds
    print("\nVerifying different seeds produce different results...")

    rng1 = np.random.default_rng(11111)
    rng2 = np.random.default_rng(22222)

    summary1, rows1 = run_case(config, rng1)
    summary2, rows2 = run_case(config, rng2)

    h1 = hash_result(summary1, rows1)
    h2 = hash_result(summary2, rows2)

    print(f"  Seed 11111: {h1}")
    print(f"  Seed 22222: {h2}")

    if h1 != h2:
        print("✅ Different seeds produce different results (as expected)")
    else:
        print("⚠️  Different seeds produced same result (suspicious)")

    return all_same


if __name__ == "__main__":
    success = run_determinism_test()
    sys.exit(0 if success else 1)
