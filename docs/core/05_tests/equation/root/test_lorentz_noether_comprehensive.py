"""
Comprehensive Test Script for Lorentz Invariance and Noether's Theorem
======================================================================

This script tests all cases:
- Field complex
- Metrics (Minkowski, Schwarzschild, Kerr, FRW)
- Time-dependent fields

Testing:
1. Lorentz invariance for all cases
2. Noether's Theorem for all cases
3. Conservation laws for all cases
"""
from docs.core.core_paths import core_root

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(core_root()))

from docs.core.uet_lorentz import UETLorentz
from docs.core.uet_noether import UETNoether


def test_lorentz_invariance_comprehensive():
    """Test Lorentz invariance for all cases."""
    print("=" * 70)
    print("COMPREHENSIVE LORENTZ INVARIANCE TEST")
    print("=" * 70)

    # Create test field
    N = 100
    x = np.linspace(-5, 5, N)
    C_real = np.exp(-x**2)  # Real field
    C_complex = np.exp(-x**2) * np.exp(1j * x)  # Complex field
    dx = 0.1
    dt = 0.01
    v = 0.1 * 299792458  # 10% speed of light

    # Create Lorentz instance
    lorentz = UETLorentz()

    results = {}

    # 1. Test with real field (baseline)
    print("\n1. Testing with real field (baseline)")
    print("-" * 70)
    result_real = lorentz.check_lorentz_invariance(C_real, v, dx, dt)
    print(f"  Original Omega: {result_real['omega_original']:.6e}")
    print(f"  Transformed Omega: {result_real['omega_transformed']:.6e}")
    print(f"  Difference: {result_real['difference']:.6e}")
    print(f"  Status: {result_real['status']}")
    results["real_field"] = result_real

    # 2. Test with complex field
    print("\n2. Testing with complex field")
    print("-" * 70)
    result_complex = lorentz.check_lorentz_invariance_complex(C_complex, v, dx, dt)
    print(f"  Original Omega: {result_complex['omega_original']:.6e}")
    print(f"  Transformed Omega: {result_complex['omega_transformed']:.6e}")
    print(f"  Difference: {result_complex['difference']:.6e}")
    print(f"  Status: {result_complex['status']}")
    results["complex_field"] = result_complex

    # 3. Test with Schwarzschild metric
    print("\n3. Testing with Schwarzschild metric")
    print("-" * 70)
    result_schwarzschild = lorentz.check_lorentz_invariance_schwarzschild(C_real, v, dx, dt)
    print(f"  Original Omega: {result_schwarzschild['omega_original']:.6e}")
    print(f"  Transformed Omega: {result_schwarzschild['omega_transformed']:.6e}")
    print(f"  Difference: {result_schwarzschild['difference']:.6e}")
    print(f"  Status: {result_schwarzschild['status']}")
    print(f"  Metric: {result_schwarzschild['metric']}")
    results["schwarzschild_metric"] = result_schwarzschild

    # 4. Test with Kerr metric
    print("\n4. Testing with Kerr metric")
    print("-" * 70)
    result_kerr = lorentz.check_lorentz_invariance_kerr(C_real, v, dx, dt)
    print(f"  Original Omega: {result_kerr['omega_original']:.6e}")
    print(f"  Transformed Omega: {result_kerr['omega_transformed']:.6e}")
    print(f"  Difference: {result_kerr['difference']:.6e}")
    print(f"  Status: {result_kerr['status']}")
    print(f"  Metric: {result_kerr['metric']}")
    results["kerr_metric"] = result_kerr

    # 5. Test with FRW metric
    print("\n5. Testing with FRW metric")
    print("-" * 70)
    result_frw = lorentz.check_lorentz_invariance_frw(C_real, v, dx, dt)
    print(f"  Original Omega: {result_frw['omega_original']:.6e}")
    print(f"  Transformed Omega: {result_frw['omega_transformed']:.6e}")
    print(f"  Difference: {result_frw['difference']:.6e}")
    print(f"  Status: {result_frw['status']}")
    print(f"  Metric: {result_frw['metric']}")
    results["frw_metric"] = result_frw

    # 6. Test with time-dependent field
    print("\n6. Testing with time-dependent field")
    print("-" * 70)
    result_time_dependent = lorentz.check_lorentz_invariance_time_dependent(C_real, v, dx, dt)
    print(f"  Original Omega: {result_time_dependent['omega_original']:.6e}")
    print(f"  Transformed Omega: {result_time_dependent['omega_transformed']:.6e}")
    print(f"  Difference: {result_time_dependent['difference']:.6e}")
    print(f"  Status: {result_time_dependent['status']}")
    print(f"  Field type: {result_time_dependent['field_type']}")
    results["time_dependent_field"] = result_time_dependent

    # Summary
    print("\n" + "=" * 70)
    print("LORENTZ INVARIANCE SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results.values() if r["is_invariant"])
    total = len(results)

    for name, result in results.items():
        status_icon = "✅" if result["is_invariant"] else "❌"
        print(f"{status_icon} {name}: {result['status']}")

    print(f"\nPassed: {passed}/{total}")

    return results


def test_noether_comprehensive():
    """Test Noether's Theorem for all cases."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE NOETHER'S THEOREM TEST")
    print("=" * 70)

    # Create test fields
    N = 100
    x = np.linspace(-5, 5, N)
    C_real = np.exp(-x**2)  # Real field (symmetric)
    C_complex = np.exp(-x**2) * np.exp(1j * x)  # Complex field
    I = np.random.randn(N) * 0.1  # Information field
    dx = 0.1

    # Create Noether instance
    noether = UETNoether()

    results = {}

    # 1. Test with real field (baseline)
    print("\n1. Testing with real field (baseline)")
    print("-" * 70)
    result_real = noether.comprehensive_conservation_check(C_real, I, x, dx)
    for name, result in result_real.items():
        if name == "summary":
            continue
        status_icon = "✅" if result["is_conserved"] else "❌"
        print(f"  {status_icon} {name}: {result['status']}")
    print(f"  Passed: {result_real['summary']['passed']}/{result_real['summary']['total']}")
    results["real_field"] = result_real

    # 2. Test with complex field
    print("\n2. Testing with complex field")
    print("-" * 70)
    result_complex = noether.comprehensive_conservation_check_complex(C_complex, I, x, dx)
    for name, result in result_complex.items():
        if name == "summary":
            continue
        status_icon = "✅" if result["is_conserved"] else "❌"
        print(f"  {status_icon} {name}: {result['status']}")
    print(f"  Passed: {result_complex['summary']['passed']}/{result_complex['summary']['total']}")
    results["complex_field"] = result_complex

    # 3. Test with time-dependent field
    print("\n3. Testing with time-dependent field")
    print("-" * 70)
    # Create time-dependent field
    C_time = np.zeros((10, N))
    for i in range(10):
        C_time[i] = np.exp(-(x - i * 0.1)**2)
    C_time_flat = C_time.flatten()  # Flatten for 1D test

    result_time = noether.comprehensive_conservation_check_time_dependent(C_time_flat, I, x, dx)
    for name, result in result_time.items():
        if name == "summary":
            continue
        status_icon = "✅" if result["is_conserved"] else "❌"
        print(f"  {status_icon} {name}: {result['status']}")
    print(f"  Passed: {result_time['summary']['passed']}/{result_time['summary']['total']}")
    results["time_dependent_field"] = result_time

    # Summary
    print("\n" + "=" * 70)
    print("NOETHER'S THEOREM SUMMARY")
    print("=" * 70)

    passed_total = sum(1 for r in results.values() if r["summary"]["passed"])
    total_tests = sum(1 for r in results.values() if r["summary"]["total"])

    for name, result in results.items():
        print(f"  {name}: {result['summary']['passed']}/{result['summary']['total']} passed")

    print(f"\nTotal Passed: {passed_total}/{total_tests}")

    return results


def test_comprehensive():
    """Run all comprehensive tests."""
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    # Test Lorentz invariance
    lorentz_results = test_lorentz_invariance_comprehensive()

    # Test Noether's Theorem
    noether_results = test_noether_comprehensive()

    # Overall summary
    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)

    lorentz_passed = sum(1 for r in lorentz_results.values() if r["is_invariant"])
    lorentz_total = len(lorentz_results)

    noether_passed = sum(1 for r in noether_results.values() if r["summary"]["passed"])
    noether_total = sum(1 for r in noether_results.values() if r["summary"]["total"])

    print(f"\nLorentz Invariance: {lorentz_passed}/{lorentz_total} passed")
    print(f"Noether's Theorem: {noether_passed}/{noether_total} passed")

    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUITE COMPLETE")
    print("=" * 70)

    return {
        "lorentz": lorentz_results,
        "noether": noether_results
    }


if __name__ == "__main__":
    test_comprehensive()
