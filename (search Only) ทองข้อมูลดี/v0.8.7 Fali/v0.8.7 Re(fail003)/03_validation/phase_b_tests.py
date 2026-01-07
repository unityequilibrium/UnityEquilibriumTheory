"""
Phase B: Original UECT Implementation
======================================

Testing the ORIGINAL UECT equation from Before_Equation.md:

dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C

And the collapse conditions:
- UECT → Newton:   if S=0, Φ=0, C=v → F = ma
- UECT → Einstein: if S=0, Φ=0, C=c → E = mc²

Author: Santa
Date: 2025-12-30
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import matplotlib.pyplot as plt
import os


@dataclass
class UECTState:
    """State of the UECT system."""

    E: float = 0.0  # Total energy [J]
    M: float = 1.0  # Mass-Mechanism (inertia) [kg]
    S: float = 0.0  # Entropy [J/K]
    C: float = 1.0  # Communication rate [m/s]
    Phi: float = 0.0  # Synergy potential [J]


@dataclass
class UECTParams:
    """Parameters for UECT."""

    k1: float = 1.0  # Entropy diffusion coefficient
    k2: float = 1.0  # Communication diffusion coefficient
    dt: float = 0.01  # Time step


class UECTSystem:
    """
    Original UECT System Implementation.

    Equation:
    dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C

    Simplified 1D form (for testing):
    dE/dt = M·dC²/dt - S·dC/dt + dΦ/dx - k₁·dS/dx + k₂·dC/dx
    """

    def __init__(self, state: Optional[UECTState] = None, params: Optional[UECTParams] = None):
        """Initialize UECT system."""
        self.state = state or UECTState()
        self.params = params or UECTParams()
        self.time = 0.0

        # History
        self.history = {"E": [], "M": [], "S": [], "C": [], "Phi": [], "dE_dt": [], "t": []}

    def compute_dE_dt(
        self, dC_dt: float = 0.0, grad_Phi: float = 0.0, grad_S: float = 0.0, grad_C: float = 0.0
    ) -> float:
        """
        Compute dE/dt from UECT equation.

        dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁·∇S + k₂·∇C

        Args:
            dC_dt: Rate of change of C
            grad_Phi: Spatial gradient of Φ
            grad_S: Spatial gradient of S
            grad_C: Spatial gradient of C

        Returns:
            dE/dt: Rate of energy change
        """
        M = self.state.M
        S = self.state.S
        k1 = self.params.k1
        k2 = self.params.k2

        # UECT equation terms
        term1 = M * (dC_dt**2)  # Kinetic-like term
        term2 = -S * dC_dt  # Entropy-communication coupling
        term3 = grad_Phi  # Synergy gradient (potential energy)
        term4 = -k1 * grad_S  # Entropy diffusion
        term5 = k2 * grad_C  # Communication diffusion

        dE_dt = term1 + term2 + term3 + term4 + term5

        return dE_dt

    def step(
        self, dC_dt: float = 0.1, grad_Phi: float = 0.0, grad_S: float = 0.0, grad_C: float = 0.0
    ):
        """Advance one time step."""
        dt = self.params.dt

        # Compute energy change rate
        dE_dt = self.compute_dE_dt(dC_dt, grad_Phi, grad_S, grad_C)

        # Update state
        self.state.E += dE_dt * dt
        self.state.C += dC_dt * dt
        self.time += dt

        # Record history
        self.history["E"].append(self.state.E)
        self.history["M"].append(self.state.M)
        self.history["S"].append(self.state.S)
        self.history["C"].append(self.state.C)
        self.history["Phi"].append(self.state.Phi)
        self.history["dE_dt"].append(dE_dt)
        self.history["t"].append(self.time)


def test_newton_collapse():
    """
    Test Newton Collapse:

    If S=0, Φ=0, C=v (velocity), then UECT should give F = ma

    From UECT: dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C

    If S=0, Φ=0, ∇S=0, ∇C=0:
    dE/dt = M·dC²/dt

    For constant dC/dt (acceleration a):
    dC/dt = a (velocity change rate)
    dE/dt = M·a²

    Hmm, this gives power = M·a², not F=ma directly.

    Let's reinterpret:
    - E = kinetic energy = ½mv²
    - dE/dt = mv·(dv/dt) = mv·a

    If C = v:
    dE/dt = M·C·dC/dt = M·v·a = power

    But UECT gives: dE/dt = M·(dC/dt)² = M·a²

    This is DIFFERENT!

    Let's test if there's a factor of 2 issue.
    """
    print("=" * 60)
    print("TEST: Newton Collapse (S=0, Φ=0)")
    print("=" * 60)

    print("\nTheory check:")
    print("  If S=0, Φ=0, ∇S=0, ∇C=0:")
    print("  UECT: dE/dt = M·(dC/dt)²")
    print("")
    print("  Newton expects:")
    print("  E = ½mv², dE/dt = mv·a = F·v (power)")
    print("")
    print("  UECT gives: dE/dt = M·a²")
    print("  Newton gives: dE/dt = M·v·a")
    print("")
    print("  These are DIFFERENT unless we reinterpret!")

    # Numerical test
    state = UECTState(M=1.0, S=0.0, Phi=0.0, C=0.0)
    system = UECTSystem(state=state)

    a = 2.0  # acceleration m/s²

    # Run for 5 seconds
    for _ in range(500):
        dE_dt_uect = system.compute_dE_dt(dC_dt=a, grad_Phi=0, grad_S=0, grad_C=0)
        system.step(dC_dt=a)

    # Final state
    v_final = system.state.C
    E_uect = system.state.E
    E_newton = 0.5 * system.state.M * v_final**2

    print(f"\nNumerical comparison (M=1, a=2, t=5s):")
    print(f"  Final velocity: v = {v_final:.2f} m/s")
    print(f"  UECT Energy:    E = {E_uect:.2f} J")
    print(f"  Newton Energy:  E = ½mv² = {E_newton:.2f} J")
    print(f"  Ratio: UECT/Newton = {E_uect/E_newton if E_newton > 0 else 'inf':.2f}")

    # The issue: UECT has E ∝ a²t, Newton has E ∝ v² = (at)²
    # Actually, integrating dE/dt = M·a² gives E = M·a²·t
    # Newton: E = ½m(at)² = ½m·a²·t²
    # These scale differently with time!

    print("\n" + "=" * 60)
    print("RESULT: UECT ≠ Newton directly")
    print("  UECT: E ∝ a²·t (linear in time)")
    print("  Newton: E ∝ a²·t² (quadratic in time)")
    print("  Need to investigate the original claim more carefully")
    print("=" * 60)

    return False  # Test shows discrepancy


def test_einstein_collapse():
    """
    Test Einstein Collapse:

    Claim: If S=0, Φ=0, C=c → E = mc²

    This claim is about STATIC energy, not dynamics.

    If C is constant (C=c), then dC/dt = 0:
    dE/dt = M·0 - 0·0 + 0 - 0 + 0 = 0

    This means energy is constant, not E=mc².

    The original claim might mean something different:
    Perhaps when C reaches c, the energy stored is E = mc²?

    Let's test this interpretation.
    """
    print("\n" + "=" * 60)
    print("TEST: Einstein Collapse (S=0, Φ=0, C=c)")
    print("=" * 60)

    c = 299792458  # speed of light m/s
    m = 1.0  # 1 kg

    print("\nTheory check:")
    print("  Claim: When C=c, E = mc²")
    print("")
    print("  If C is constant, dC/dt = 0:")
    print("  dE/dt = M·0² - 0 + 0 - 0 + 0 = 0")
    print("  This means dE/dt = 0, not E = mc²!")
    print("")
    print("  The claim might mean the TOTAL energy when C=c:")
    print("  E = ∫(dE/dt)dt from C=0 to C=c")

    # Let's compute total energy if we accelerate from 0 to c
    state = UECTState(M=m, S=0.0, Phi=0.0, C=0.0)
    params = UECTParams(dt=1e5)  # Large time step for speed
    system = UECTSystem(state=state, params=params)

    # Accelerate to near c
    a = 1e4  # m/s² (very fast acceleration)
    steps = int(c / (a * params.dt)) + 1

    for _ in range(min(steps, 30000)):
        if system.state.C >= c:
            break
        system.step(dC_dt=a)

    E_uect = system.state.E
    E_einstein = m * c**2

    print(f"\nNumerical (accelerating from 0 to c):")
    print(f"  Final C: {system.state.C:.2e} m/s")
    print(f"  Speed of light: {c:.2e} m/s")
    print(f"  UECT Energy: {E_uect:.2e} J")
    print(f"  Einstein E=mc²: {E_einstein:.2e} J")

    if E_uect > 0:
        ratio = E_uect / E_einstein
        print(f"  Ratio: {ratio:.4e}")

    print("\n" + "=" * 60)
    print("RESULT: Cannot verify E=mc² from UECT directly")
    print("  The equation dE/dt = M·(dC/dt)² does not lead to E=mc²")
    print("  The original claim needs clarification")
    print("=" * 60)

    return False


def test_thermodynamic_limit():
    """
    Test Thermodynamic Limit:

    Claim: If C is constant → dE/dt = -k₁∇S

    This makes more sense!
    If dC/dt = 0 and Φ = 0:
    dE/dt = 0 - 0 + 0 - k₁∇S + 0 = -k₁∇S

    This is like heat flow!
    """
    print("\n" + "=" * 60)
    print("TEST: Thermodynamic Limit (C constant)")
    print("=" * 60)

    print("\nTheory check:")
    print("  If dC/dt = 0, Φ = 0, ∇C = 0:")
    print("  dE/dt = -k₁∇S")
    print("")
    print("  This is heat diffusion equation!")
    print("  Energy flows from high to low entropy gradient")

    # Test with non-zero entropy gradient
    state = UECTState(M=1.0, S=0.0, Phi=0.0, C=1.0)
    params = UECTParams(k1=1.0)
    system = UECTSystem(state=state, params=params)

    grad_S = 2.0  # Entropy gradient

    dE_dt = system.compute_dE_dt(dC_dt=0, grad_Phi=0, grad_S=grad_S, grad_C=0)
    expected = -params.k1 * grad_S

    print(f"\nNumerical test:")
    print(f"  ∇S = {grad_S}")
    print(f"  k₁ = {params.k1}")
    print(f"  dE/dt (UECT) = {dE_dt:.2f}")
    print(f"  dE/dt (expected -k₁∇S) = {expected:.2f}")
    print(f"  Match: {np.isclose(dE_dt, expected)}")

    passed = np.isclose(dE_dt, expected)

    print("\n" + "=" * 60)
    if passed:
        print("RESULT: PASSED - Thermodynamic limit recovers heat flow")
    else:
        print("RESULT: FAILED")
    print("=" * 60)

    return passed


def run_all_phase_b_tests():
    """Run all Phase B tests."""
    print("\n" + "=" * 70)
    print("          PHASE B: ORIGINAL UECT IMPLEMENTATION")
    print("          Testing Collapse Conditions")
    print("=" * 70 + "\n")

    results = {}

    results["newton"] = test_newton_collapse()
    results["einstein"] = test_einstein_collapse()
    results["thermo"] = test_thermodynamic_limit()

    # Summary
    print("\n" + "=" * 70)
    print("                    PHASE B SUMMARY")
    print("=" * 70)

    print(f"\n{'Test':<40} {'Result'}")
    print("-" * 50)

    passed = 0
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL/UNCLEAR"
        if result:
            passed += 1
        print(f"{name:<40} {status}")

    total = len(results)
    print("-" * 50)
    print(f"{'TOTAL':<40} {passed}/{total}")

    print("\n" + "=" * 70)
    print("HONEST CONCLUSION:")
    print("  - Newton collapse: DOES NOT MATCH as claimed")
    print("  - Einstein collapse: CANNOT VERIFY E=mc²")
    print("  - Thermodynamic: WORKS (heat flow)")
    print("")
    print("The original UECT collapse claims need more investigation.")
    print("Either the claims are incorrect, or we're missing something.")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_all_phase_b_tests()
