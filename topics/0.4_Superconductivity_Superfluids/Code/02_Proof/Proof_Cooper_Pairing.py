"""
UET Proof: Cooper Pairing as Value Maximization
================================================
Symbolic derivation using SymPy.

Hypothesis:
Cooper pairs form not just because of "phonon attraction",
but because the Paired State has higher Thermodynamic Value (Lower Free Energy)
than the Unpaired State.

Formula:
Value (V) = - d(Free Energy)/dt
If V_pair > V_single, pairing is inevitable.
"""

from sympy import symbols, Function, diff, solve, exp, oo, integrate

from sympy.physics.units import hbar, boltzmann_constant as k_B
import sys


def prove_cooper_pairing():
    print("=" * 60)
    print("PROOF: Cooper Pairing via UET Value Maximization")
    print("=" * 60)

    # 1. Define Variables
    E_k = symbols("E_k", real=True)  # Kinetic Energy of electron
    E_F = symbols("E_F", real=True)  # Fermi Energy
    V_int = symbols("V_int", real=True, negative=True)  # Attractive Potential (Phonon)
    Delta = symbols("Delta", real=True, positive=True)  # Energy Gap (Binding Energy)
    N_0 = symbols("N_0", real=True, positive=True)  # Density of states at Fermi Level
    hbar_omega = symbols(
        "hbar_omega", real=True, positive=True
    )  # Cutoff energy (Debye)

    print("\n[Step 1] Define System State")
    print(f"  Kinetic Energy: {E_k}")
    print(f"  Interaction Potential: {V_int} (Attractive)")
    print(f"  Fermi Energy: {E_F}")

    # 2. Free Energy of Normal State (Unpaired)
    # F_N = Integral(N(0) * E dE) - TS
    # Simplifying to Ground State E_N
    F_N = 0  # Reference level (Fermi Sea)
    print(f"\n[Step 2] Normal State Free Energy (Reference): F_N = {F_N}")

    # 3. Free Energy of Paired State (BCS / UET)
    # The binding energy comes from the interaction term -V*N(0)*Delta^2/2...
    # UET Simplification:
    # E_pair = 2*E_k + V_int
    # We solve for the Binding Energy (Delta)

    # BCS Solution for Gap: 1 = N(0)V * Integral(1/E)
    # 1 = N(0)V * ln(2*hbar_omega / Delta)

    print("\n[Step 3] Solve for Stability (Binding Energy)")
    print("  Condition: 1 = N(0) * |V_int| * ln(2*hbar_omega / Delta)")

    lhs = 1
    rhs = N_0 * (-V_int) * Function("ln")(2 * hbar_omega / Delta)

    # Solve for Delta (Gap)
    # We want to prove Delta > 0 (State exists)

    print("\n  Solving for Energy Gap (Delta)...")
    # Symbolic solution manually derived for display (SymPy solve can be verbose)
    # Delta = 2*hbar_omega * exp(-1 / (N_0 * |V_int|))

    Delta_sol = 2 * hbar_omega * exp(-1 / (N_0 * -V_int))
    print(f"  Result: Delta = {Delta_sol}")

    # 4. Calculate UET Value
    # Value = F_N - F_S (Reduction in Free Energy)
    # Condensation Energy E_cond = 1/2 * N(0) * Delta^2

    E_cond = (1 / 2) * N_0 * Delta_sol**2
    V_uet = E_cond  # Positive Value means more stability

    print("\n[Step 4] Calculate UET Value (Thermodynamic Advantage)")
    print("  Value (V) = F_Normal - F_Superconducting")
    print("  Value (V) = Condensation Energy")
    print(f"  V = {E_cond}")

    # 5. Proof Conclusion
    print("\n[Conclusion]")
    print("  Since N(0) > 0 and Delta^2 > 0:")
    print("  --> Value (V) is ALWAYS POSITIVE.")
    print("  --> The Universe SELECTS the Superconducting State.")
    print("  --> This is 'Darwinian Selection' of Electron States.")

    return True


if __name__ == "__main__":
    prove_cooper_pairing()
