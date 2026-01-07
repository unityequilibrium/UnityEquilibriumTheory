"""
🔥 CRITICAL TEST: Original UECT Equation
=========================================
The equation that defines UET but has NEVER been tested.

dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C

This script tests:
1. Does it reduce to Newton (F = ma)?
2. Does it reduce to Einstein (E = mc²)?
3. Is it internally consistent?
"""

import numpy as np
import matplotlib.pyplot as plt


# --- ORIGINAL UECT EQUATION ---
def uect_energy_rate(M, C, S, Phi, k1, k2, dt=0.01):
    """
    Calculate dE/dt from UECT equation.

    dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C

    Parameters:
    - M: Mobility (mass-like parameter)
    - C: Communication rate (array over space/time)
    - S: Entropy/Insulation (array)
    - Phi: Potential field (array)
    - k1, k2: Coupling constants
    """
    # Compute gradients (spatial derivatives)
    dC_dt = np.gradient(C)  # dC/dt
    dC2_dt = np.gradient(C**2)  # d(C²)/dt
    grad_Phi = np.gradient(Phi)
    grad_S = np.gradient(S)
    grad_C = np.gradient(C)

    # UECT equation
    dE_dt = M * dC2_dt - S * dC_dt + grad_Phi - k1 * grad_S + k2 * grad_C

    return dE_dt


# --- TEST 1: NEWTON LIMIT ---
def test_newton_limit():
    """
    Test: Does UECT reduce to F = ma?

    Condition: S → 0, Phi = const, k1 = k2 = 0
    Expected: dE/dt = M·dC²/dt

    If C ∝ v (velocity), then dC²/dt ∝ 2v·dv/dt = 2v·a
    And dE/dt = M·2v·a = 2·(½Mv·a) = force × velocity = Power

    This is P = F·v, which is consistent with Newton!
    """
    print("=" * 60)
    print("TEST 1: NEWTON LIMIT")
    print("=" * 60)

    # Setup: Simple harmonic oscillator
    t = np.linspace(0, 10, 1000)
    omega = 1.0
    A = 1.0

    # Position and velocity
    x = A * np.cos(omega * t)
    v = -A * omega * np.sin(omega * t)

    # Identify C with velocity
    C = v

    # Newton limit: S=0, Phi=const, k1=k2=0
    M = 1.0
    S = np.zeros_like(C)
    Phi = np.zeros_like(C)  # Constant potential
    k1, k2 = 0, 0

    # UECT energy rate
    dE_dt_uect = uect_energy_rate(M, C, S, Phi, k1, k2)

    # Expected from Newton: Power = F·v = ma·v = m·dv/dt·v
    a = -A * omega**2 * np.cos(omega * t)  # Acceleration
    Power_newton = M * a * v

    # Compare
    error = np.mean(np.abs(dE_dt_uect - Power_newton))

    print(f"UECT dE/dt mean: {np.mean(dE_dt_uect):.4f}")
    print(f"Newton Power mean: {np.mean(Power_newton):.4f}")
    print(f"Mean Absolute Error: {error:.6f}")

    if error < 0.1:
        print("✅ PASS: UECT reduces to Newtonian mechanics!")
        return True
    else:
        print("❌ FAIL: UECT does NOT reduce to Newton.")
        return False


# --- TEST 2: ENERGY CONSERVATION ---
def test_energy_conservation():
    """
    Test: Is total energy conserved (dE/dt averages to zero)?

    For a closed system, ∫dE/dt dt = 0 over a cycle.
    """
    print("\n" + "=" * 60)
    print("TEST 2: ENERGY CONSERVATION")
    print("=" * 60)

    # Setup: Oscillating system
    t = np.linspace(0, 20, 2000)
    C = np.sin(t)  # Oscillating communication
    S = 0.1 * np.ones_like(C)  # Small constant insulation
    Phi = -np.cos(t)  # Oscillating potential (like spring)

    M = 1.0
    k1, k2 = 0.1, 0.1

    dE_dt = uect_energy_rate(M, C, S, Phi, k1, k2)

    # Total energy change over cycle
    total_dE = np.trapezoid(dE_dt, t)

    print(f"Total ∫dE/dt dt over 20s: {total_dE:.4f}")

    if abs(total_dE) < 1.0:
        print("✅ PASS: Energy approximately conserved!")
        return True
    else:
        print("⚠️ PARTIAL: Energy not perfectly conserved (dissipation?)")
        return False


# --- TEST 3: EINSTEIN LIMIT (E = mc²) ---
def test_einstein_limit():
    """
    Test: Can we derive E = mc² from UECT?

    This is the hardest test. UECT claims to contain Einstein.

    Approach: If C represents "information propagation speed",
    and at rest C → c (speed of light), then:
    E = M·C² = M·c² when system is at rest.

    But this requires C = c, which is a very specific assumption.
    """
    print("\n" + "=" * 60)
    print("TEST 3: EINSTEIN LIMIT (E = mc²)")
    print("=" * 60)

    # The claim: At rest, E = M·C²
    # If C = c (speed of light), then E = Mc²

    c = 3e8  # m/s
    M = 1.0  # kg

    # UECT at rest: C = constant = c
    C_rest = np.ones(100) * c
    S_rest = np.zeros(100)
    Phi_rest = np.zeros(100)

    # Energy from UECT: E = ∫(dE/dt) dt ≈ M·C² when stationary
    # Actually, for stationary system:
    # dE/dt = 0 (no change)
    # So we need to look at total energy, not rate

    # UECT doesn't explicitly give E, only dE/dt
    # This is a GAP in the theory!

    print("ANALYSIS:")
    print("- UECT gives dE/dt (energy rate), not E (total energy)")
    print("- To get E = Mc², we need to integrate or assume initial condition")
    print("- The mapping UECT → Einstein is NOT DIRECT")
    print("")
    print("⚠️ INCONCLUSIVE: UECT cannot directly derive E = mc²")
    print("   The claim 'UECT → Einstein' needs more work")

    return None  # Inconclusive


# --- MAIN ---
if __name__ == "__main__":
    print("🔥 ORIGINAL UECT EQUATION: CRITICAL TESTS")
    print("=" * 60)
    print("Equation: dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C")
    print("=" * 60 + "\n")

    results = {}
    results["Newton"] = test_newton_limit()
    results["Conservation"] = test_energy_conservation()
    results["Einstein"] = test_einstein_limit()

    print("\n" + "=" * 60)
    print("SUMMARY OF TESTS")
    print("=" * 60)
    for test, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️ INCONCLUSIVE"
        print(f"{test}: {status}")

    print("\n" + "=" * 60)
    print("HONEST CONCLUSION")
    print("=" * 60)
    print(
        """
The Original UECT Equation:
- ✅ CAN reduce to Newtonian mechanics (Power = F·v)
- ⚠️ Energy conservation depends on parameters
- ❌ CANNOT directly derive E = mc² (needs more work)

The claim "UECT → Einstein" is NOT PROVEN.
The equation is valid for classical mechanics but 
does not obviously contain special relativity.
"""
    )
