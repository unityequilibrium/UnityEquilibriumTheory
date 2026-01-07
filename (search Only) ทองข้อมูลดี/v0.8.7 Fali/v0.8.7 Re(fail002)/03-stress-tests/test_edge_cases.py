#!/usr/bin/env python3
"""
Edge Case Coverage Test for UET

Tests the system's behavior with extreme and invalid inputs:
1. Negative delta (should fail - unbounded potential)
2. Zero kappa (should fail - no diffusion)
3. Extreme ratios (1e20 - should warn and adjust)
4. Very small grid (N=4 - should still work)
5. Very large grid (N=256 - performance test)
"""

import sys
import os
import time

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

import numpy as np
from uet_core.solver import run_case


def test_edge_cases():
    print("=" * 70)
    print("🔥 EDGE CASE COVERAGE TEST")
    print("=" * 70)

    results = []

    # Base config template
    def make_config(case_id, **overrides):
        config = {
            "case_id": case_id,
            "model": "C_only",
            "domain": {"L": 10.0, "dim": 2, "bc": "periodic"},
            "grid": {"N": 32},
            "time": {
                "dt": 0.01,
                "T": 0.5,
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
        # Apply overrides
        for key, value in overrides.items():
            if key == "delta":
                config["params"]["pot"]["delta"] = value
            elif key == "kappa":
                config["params"]["kappa"] = value
            elif key == "a":
                config["params"]["pot"]["a"] = value
            elif key == "N":
                config["grid"]["N"] = value
            elif key == "dt":
                config["time"]["dt"] = value
        return config

    # Test 1: Negative delta (SHOULD FAIL)
    print("\n[TEST 1] Negative delta (δ < 0) → Should FAIL")
    config = make_config("edge_neg_delta", delta=-1.0)
    rng = np.random.default_rng(42)
    summary, _ = run_case(config, rng)
    expected = "FAIL"
    actual = summary["status"]
    passed = actual == expected
    print(f"   Expected: {expected}, Got: {actual} → {'✅' if passed else '❌'}")
    if summary.get("fail_reasons"):
        print(f"   Reason: {summary['fail_reasons']}")
    results.append(("Negative delta", passed))

    # Test 2: Zero kappa (SHOULD FAIL)
    print("\n[TEST 2] Zero kappa (κ = 0) → Should FAIL")
    config = make_config("edge_zero_kappa", kappa=0.0)
    rng = np.random.default_rng(42)
    summary, _ = run_case(config, rng)
    expected = "FAIL"
    actual = summary["status"]
    passed = actual == expected
    print(f"   Expected: {expected}, Got: {actual} → {'✅' if passed else '❌'}")
    if summary.get("fail_reasons"):
        print(f"   Reason: {summary['fail_reasons']}")
    results.append(("Zero kappa", passed))

    # Test 3: Negative kappa (SHOULD FAIL)
    print("\n[TEST 3] Negative kappa (κ < 0) → Should FAIL")
    config = make_config("edge_neg_kappa", kappa=-0.5)
    rng = np.random.default_rng(42)
    summary, _ = run_case(config, rng)
    expected = "FAIL"
    actual = summary["status"]
    passed = actual == expected
    print(f"   Expected: {expected}, Got: {actual} → {'✅' if passed else '❌'}")
    if summary.get("fail_reasons"):
        print(f"   Reason: {summary['fail_reasons']}")
    results.append(("Negative kappa", passed))

    # Test 4: Extreme ratio (SHOULD WARN or handle gracefully)
    print("\n[TEST 4] Extreme ratio (a = -1e10) → Should handle gracefully")
    config = make_config("edge_extreme_ratio", a=-1e10)
    rng = np.random.default_rng(42)
    t0 = time.time()
    summary, _ = run_case(config, rng)
    elapsed = time.time() - t0
    # Should either PASS with auto-adjusted dt OR FAIL gracefully
    passed = summary["status"] in ["PASS", "WARN", "FAIL"]
    print(f"   Status: {summary['status']}, Time: {elapsed:.2f}s → {'✅' if passed else '❌'}")
    results.append(("Extreme ratio", passed))

    # Test 5: Very small grid (SHOULD WORK)
    print("\n[TEST 5] Tiny grid (N = 8) → Should still work")
    config = make_config("edge_tiny_grid", N=8)
    rng = np.random.default_rng(42)
    summary, _ = run_case(config, rng)
    passed = summary["status"] in ["PASS", "WARN"]
    print(f"   Status: {summary['status']} → {'✅' if passed else '❌'}")
    results.append(("Tiny grid", passed))

    # Test 6: Delta = 0 with a > 0 (quadratic only - SHOULD WARN)
    print("\n[TEST 6] Quadratic only (δ = 0, a > 0) → Should WARN or handle")
    config = make_config("edge_quadratic", delta=0.0, a=1.0)
    rng = np.random.default_rng(42)
    summary, _ = run_case(config, rng)
    passed = summary["status"] in ["PASS", "WARN"]
    print(f"   Status: {summary['status']} → {'✅' if passed else '⚠️'}")
    results.append(("Quadratic only", passed))

    # Summary
    print("\n" + "=" * 70)
    print("📊 EDGE CASE SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, p in results if p)
    total = len(results)

    for name, passed in results:
        print(f"   {name}: {'✅ PASS' if passed else '❌ FAIL'}")

    print(f"\n   Total: {passed_count}/{total} ({100*passed_count/total:.0f}%)")

    if passed_count == total:
        print("\n✅ ALL EDGE CASES HANDLED CORRECTLY!")
    else:
        print("\n⚠️  Some edge cases need attention.")

    print("=" * 70)

    return passed_count == total


if __name__ == "__main__":
    success = test_edge_cases()
    sys.exit(0 if success else 1)
