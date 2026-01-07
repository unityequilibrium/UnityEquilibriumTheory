"""
Phase A: Foundation Testing
============================

Comprehensive tests for Landauer and V function equations.
This is REAL testing, not just claims.

Author: Santa
Date: 2025-12-30
"""

import numpy as np
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uet_landauer import (
    energy_per_bit,
    value_function,
    K_B,
    LN_2,
    ThermodynamicSystem,
    FullSimulator,
    SimulationConfig,
)


def test_landauer_multiple_temperatures():
    """
    Test 1: E_bit = k_B T ln(2) at multiple temperatures

    Compare with known physics values.
    """
    print("=" * 60)
    print("TEST 1: Landauer E_bit at Multiple Temperatures")
    print("=" * 60)

    # Known values from literature
    # E_bit = k_B * T * ln(2) ≈ 2.87e-21 J at 300K

    temperatures = [100, 200, 300, 400, 500, 1000]

    results = []
    for T in temperatures:
        E_uet = energy_per_bit(T)
        E_expected = K_B * T * LN_2
        error = abs(E_uet - E_expected) / E_expected * 100

        results.append(
            {
                "T": T,
                "E_uet": E_uet,
                "E_expected": E_expected,
                "error_%": error,
                "pass": error < 0.01,  # <0.01% error
            }
        )

    print(f"\n{'T (K)':<10} {'E_uet (J)':<15} {'E_expected (J)':<15} {'Error %':<10} {'Status'}")
    print("-" * 60)

    all_pass = True
    for r in results:
        status = "✓ PASS" if r["pass"] else "✗ FAIL"
        if not r["pass"]:
            all_pass = False
        print(
            f"{r['T']:<10} {r['E_uet']:<15.4e} {r['E_expected']:<15.4e} {r['error_%']:<10.6f} {status}"
        )

    print("\n" + "=" * 60)
    if all_pass:
        print("RESULT: ALL PASSED - Landauer formula is correct")
    else:
        print("RESULT: SOME FAILED - Need investigation")
    print("=" * 60)

    return all_pass


def test_v_function_scenarios():
    """
    Test 2: V = M(C/I)^α in multiple scenarios

    Verify the function behaves as expected.
    """
    print("\n" + "=" * 60)
    print("TEST 2: V Function Scenarios")
    print("=" * 60)

    scenarios = [
        # (C, I, M, α, expected_V, description)
        (1, 1, 1, 1, 1.0, "Balance: C=I → V=M"),
        (2, 1, 1, 1, 2.0, "High C: C>I → V>M"),
        (1, 2, 1, 1, 0.5, "High I: C<I → V<M"),
        (4, 2, 1, 1, 2.0, "Ratio 2:1"),
        (10, 5, 2, 1, 4.0, "M=2, ratio 2:1"),
        (2, 1, 1, 2, 4.0, "α=2 (nonlinear)"),
        (3, 1, 1, 2, 9.0, "α=2, ratio 3:1"),
        (5, 5, 3, 1, 3.0, "Balance with M=3"),
    ]

    print(
        f"\n{'C':<5} {'I':<5} {'M':<5} {'α':<5} {'V_uet':<10} {'V_exp':<10} {'Status':<10} {'Description'}"
    )
    print("-" * 80)

    all_pass = True
    for C, I, M, alpha, expected, desc in scenarios:
        V_uet = value_function(C, I, M, alpha)
        match = np.isclose(V_uet, expected, rtol=1e-10)
        status = "✓ PASS" if match else "✗ FAIL"
        if not match:
            all_pass = False
        print(
            f"{C:<5} {I:<5} {M:<5} {alpha:<5} {V_uet:<10.2f} {expected:<10.2f} {status:<10} {desc}"
        )

    print("\n" + "=" * 60)
    if all_pass:
        print("RESULT: ALL PASSED - V function works correctly")
    else:
        print("RESULT: SOME FAILED - Need investigation")
    print("=" * 60)

    return all_pass


def test_v_increases_with_c():
    """
    Test 3: V should increase when C increases (I fixed)
    """
    print("\n" + "=" * 60)
    print("TEST 3: V Increases with C (I fixed)")
    print("=" * 60)

    I_fixed = 1.0
    C_values = [0.5, 1.0, 2.0, 5.0, 10.0]
    V_values = [value_function(C, I_fixed) for C in C_values]

    print(f"\nI = {I_fixed} (fixed)")
    print(f"\n{'C':<10} {'V':<10}")
    print("-" * 20)
    for C, V in zip(C_values, V_values):
        print(f"{C:<10.1f} {V:<10.2f}")

    # Check monotonically increasing
    is_increasing = all(V_values[i] < V_values[i + 1] for i in range(len(V_values) - 1))

    print("\n" + "=" * 60)
    if is_increasing:
        print("RESULT: PASSED - V increases with C (as expected)")
    else:
        print("RESULT: FAILED - V does NOT increase with C")
    print("=" * 60)

    return is_increasing


def test_v_decreases_with_i():
    """
    Test 4: V should decrease when I increases (C fixed)
    """
    print("\n" + "=" * 60)
    print("TEST 4: V Decreases with I (C fixed)")
    print("=" * 60)

    C_fixed = 1.0
    I_values = [0.5, 1.0, 2.0, 5.0, 10.0]
    V_values = [value_function(C_fixed, I) for I in I_values]

    print(f"\nC = {C_fixed} (fixed)")
    print(f"\n{'I':<10} {'V':<10}")
    print("-" * 20)
    for I, V in zip(I_values, V_values):
        print(f"{I:<10.1f} {V:<10.2f}")

    # Check monotonically decreasing
    is_decreasing = all(V_values[i] > V_values[i + 1] for i in range(len(V_values) - 1))

    print("\n" + "=" * 60)
    if is_decreasing:
        print("RESULT: PASSED - V decreases with I (as expected)")
    else:
        print("RESULT: FAILED - V does NOT decrease with I")
    print("=" * 60)

    return is_decreasing


def test_thermodynamic_law_2():
    """
    Test 5: Entropy should always increase (Law 2)
    """
    print("\n" + "=" * 60)
    print("TEST 5: Thermodynamic Law 2 (Entropy Always Increases)")
    print("=" * 60)

    system = ThermodynamicSystem(T=300)

    # Add behaviors and track entropy
    entropy_history = [0]
    for i in range(10):
        bits = 1000 * (i + 1)
        system.add_behavior(bits)
        entropy_history.append(system.state.S)

    print(f"\n{'Step':<10} {'Entropy (J/K)':<20} {'Change':<15}")
    print("-" * 45)
    for i, S in enumerate(entropy_history):
        if i == 0:
            change = "—"
        else:
            dS = S - entropy_history[i - 1]
            change = f"+{dS:.4e}" if dS > 0 else f"{dS:.4e}"
        print(f"{i:<10} {S:<20.4e} {change:<15}")

    # Check always increasing
    always_increasing = all(
        entropy_history[i] < entropy_history[i + 1] for i in range(len(entropy_history) - 1)
    )

    print("\n" + "=" * 60)
    if always_increasing:
        print("RESULT: PASSED - Entropy always increases (Law 2 satisfied)")
    else:
        print("RESULT: FAILED - Entropy decreased at some point")
    print("=" * 60)

    return always_increasing


def test_full_simulation():
    """
    Test 6: Full simulation runs correctly
    """
    print("\n" + "=" * 60)
    print("TEST 6: Full Simulation Run")
    print("=" * 60)

    config = SimulationConfig(T=300.0, dt=0.01, duration=5.0, n_agents=3)

    sim = FullSimulator(config)
    results = sim.run()

    print(f"\nSimulation completed:")
    print(f"  Duration: {results['duration']} s")
    print(f"  Steps: {results['steps']}")
    print(f"  Final Energy: {results['final_E']:.4e} J")
    print(f"  Final Entropy: {results['final_S']:.4e} J/K")
    print(f"  Law 2 OK: {results['law_2_ok']}")

    print(f"\nAgents final state:")
    for name, C, I, V in results["agents"]:
        ratio = C / I
        print(f"  {name}: C={C:.3f}, I={I:.3f}, C/I={ratio:.3f}, V={V:.3f}")

    # Check simulation ran without error and Law 2 holds
    success = results["law_2_ok"]

    print("\n" + "=" * 60)
    if success:
        print("RESULT: PASSED - Simulation ran correctly, Law 2 satisfied")
    else:
        print("RESULT: FAILED - Simulation had issues")
    print("=" * 60)

    return success


def run_all_tests():
    """Run all Phase A tests."""
    print("\n" + "=" * 70)
    print("          PHASE A: FOUNDATION TESTING")
    print("          Testing Landauer and V Function Equations")
    print("=" * 70 + "\n")

    results = {}

    # Run all tests
    results["landauer_temps"] = test_landauer_multiple_temperatures()
    results["v_scenarios"] = test_v_function_scenarios()
    results["v_increases_c"] = test_v_increases_with_c()
    results["v_decreases_i"] = test_v_decreases_with_i()
    results["thermo_law2"] = test_thermodynamic_law_2()
    results["full_sim"] = test_full_simulation()

    # Summary
    print("\n" + "=" * 70)
    print("                    PHASE A SUMMARY")
    print("=" * 70)

    print(f"\n{'Test':<40} {'Result'}")
    print("-" * 50)

    passed = 0
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        if result:
            passed += 1
        print(f"{name:<40} {status}")

    total = len(results)
    print("-" * 50)
    print(f"{'TOTAL':<40} {passed}/{total}")

    print("\n" + "=" * 70)
    if passed == total:
        print("ALL TESTS PASSED!")
        print("Foundation equations are working correctly.")
    else:
        print(f"SOME TESTS FAILED ({total-passed}/{total})")
        print("Investigation needed.")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_all_tests()
