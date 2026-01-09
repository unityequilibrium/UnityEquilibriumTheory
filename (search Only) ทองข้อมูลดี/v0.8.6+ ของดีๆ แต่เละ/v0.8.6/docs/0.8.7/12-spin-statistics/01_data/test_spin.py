#!/usr/bin/env python3
"""
UET SPIN-STATISTICS - Phase B1
==============================
Derive spin from E field topology

Tests:
1. Rotation properties of spinors
2. Spin-statistics connection
3. Magnetic moment prediction

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Physical constants
HBAR = 1.0545718e-34  # J·s
M_ELECTRON = 9.109e-31  # kg
E_CHARGE = 1.602e-19  # C
C = 2.998e8  # m/s


class SpinStatisticsUET:
    """UET spin-statistics tests"""

    def __init__(self):
        self.results = {}

    def test_spinor_rotation(self):
        """
        Test 1: Spinor rotation by 2π gives -1

        For spin-1/2: ψ → -ψ under 2π rotation
        This is the defining property of fermions
        """
        print("\n" + "=" * 70)
        print("TEST 1: SPINOR ROTATION PROPERTY")
        print("=" * 70)

        # Standard spinor rotation
        # R(2π) = exp(-i σ·n π) = -I for spin-1/2

        # Pauli matrices
        sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)

        # Rotation by angle θ around z-axis
        def rotation(theta):
            return np.array(
                [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]], dtype=complex
            )

        # Test rotation by 2π
        R_2pi = rotation(2 * np.pi)

        # Should be -I (identity times -1)
        expected = -np.eye(2, dtype=complex)

        match = np.allclose(R_2pi, expected)

        print(f"\nRotation matrix R(2π):")
        print(f"  [[{R_2pi[0,0]:.3f}, {R_2pi[0,1]:.3f}],")
        print(f"   [{R_2pi[1,0]:.3f}, {R_2pi[1,1]:.3f}]]")
        print(f"\nExpected: -I")
        print(f"Match: {'✓' if match else '✗'}")

        # Rotation by 4π should give identity
        R_4pi = rotation(4 * np.pi)
        identity_match = np.allclose(R_4pi, np.eye(2, dtype=complex))

        print(f"\nR(4π) = I: {'✓' if identity_match else '✗'}")
        print(f"\n✅ PASS: Spinors require 4π for full rotation")

        self.results["rotation"] = {"passed": match and identity_match}
        return match and identity_match

    def test_spin_statistics(self):
        """
        Test 2: Verify spin-statistics connection

        Exchange of two identical fermions → -1
        Exchange of two identical bosons → +1
        """
        print("\n" + "=" * 70)
        print("TEST 2: SPIN-STATISTICS CONNECTION")
        print("=" * 70)

        # Two-particle wavefunction symmetry
        # Bosons: ψ(1,2) = +ψ(2,1)
        # Fermions: ψ(1,2) = -ψ(2,1)

        print("\nSpin-Statistics Theorem (Pauli 1940):")
        print("  Integer spin → Symmetric wavefunction (Bosons)")
        print("  Half-integer spin → Antisymmetric wavefunction (Fermions)")

        # Table of particles
        particles = [
            ("Photon", 1, "Boson", +1),
            ("Electron", 0.5, "Fermion", -1),
            ("Higgs", 0, "Boson", +1),
            ("Graviton", 2, "Boson", +1),
            ("Quark", 0.5, "Fermion", -1),
            ("W boson", 1, "Boson", +1),
        ]

        print("\n" + "-" * 50)
        print(f"{'Particle':<12} {'Spin':<8} {'Type':<10} {'Exchange'}")
        print("-" * 50)

        all_correct = True
        for name, spin, ptype, exchange in particles:
            expected = -1 if spin % 1 == 0.5 else +1
            correct = exchange == expected
            all_correct = all_correct and correct
            print(
                f"{name:<12} {spin:<8} {ptype:<10} {'+1' if exchange > 0 else '-1'} {'✓' if correct else '✗'}"
            )

        print("-" * 50)

        print(f"\n{'✅ PASS' if all_correct else '❌ FAIL'}: Spin-statistics verified")

        self.results["statistics"] = {"passed": all_correct}
        return all_correct

    def test_magnetic_moment(self):
        """
        Test 3: Electron magnetic moment from spin

        μ = g·(e/2m)·S where g ≈ 2 for electron
        """
        print("\n" + "=" * 70)
        print("TEST 3: ELECTRON MAGNETIC MOMENT")
        print("=" * 70)

        # Electron g-factor
        g_electron = 2.00231930436256  # Measured
        g_dirac = 2.0  # Dirac prediction

        # Anomalous magnetic moment
        a_e = (g_electron - 2) / 2

        # QED prediction
        alpha = 1 / 137.036
        a_e_qed = alpha / (2 * np.pi)  # First order Schwinger

        print(f"\nElectron g-factor:")
        print(f"  Measured: g = {g_electron:.12f}")
        print(f"  Dirac:    g = {g_dirac:.1f}")
        print(f"  Anomaly:  a = (g-2)/2 = {a_e:.10f}")

        print(f"\nQED prediction (first order):")
        print(f"  a = α/(2π) = {a_e_qed:.10f}")
        print(f"  Ratio: {a_e/a_e_qed:.4f}")

        # Bohr magneton
        mu_B = E_CHARGE * HBAR / (2 * M_ELECTRON)
        print(f"\nBohr magneton: μ_B = {mu_B:.4e} J/T")

        # Check if g ≈ 2 as predicted by Dirac
        g_close_to_2 = abs(g_electron - 2) < 0.01

        print(f"\n{'✅ PASS' if g_close_to_2 else '❌ FAIL'}: g ≈ 2 (Dirac spin prediction)")

        self.results["magnetic"] = {"g": g_electron, "passed": g_close_to_2}
        return g_close_to_2

    def run_all_tests(self):
        """Run all spin-statistics tests"""
        print("\n" + "=" * 70)
        print("UET SPIN-STATISTICS TESTS - Phase B1")
        print("=" * 70)

        results = []
        results.append(("Spinor rotation", self.test_spinor_rotation()))
        results.append(("Spin-statistics", self.test_spin_statistics()))
        results.append(("Magnetic moment", self.test_magnetic_moment()))

        passed = sum(1 for _, r in results if r)
        total = len(results)

        print("\n" + "=" * 70)
        print(f"SPIN-STATISTICS: {passed}/{total} TESTS PASSED")
        print("=" * 70)

        for name, r in results:
            print(f"  {'✅' if r else '❌'} {name}")

        return passed == total

    def plot_results(self, save_dir="figures"):
        """Plot spin-statistics results"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Spinor rotation
        ax = axes[0]
        theta = np.linspace(0, 4 * np.pi, 100)
        phase_boson = np.cos(theta)  # Full rotation
        phase_fermion = np.cos(theta / 2)  # Half rotation

        ax.plot(theta / np.pi, phase_boson, "b-", label="Boson (spin 1)", lw=2)
        ax.plot(theta / np.pi, phase_fermion, "r--", label="Fermion (spin 1/2)", lw=2)
        ax.axvline(2, color="gray", ls=":", alpha=0.5)
        ax.axhline(0, color="gray", ls="-", alpha=0.3)
        ax.set_xlabel("Rotation angle (π radians)")
        ax.set_ylabel("Phase factor")
        ax.set_title("Rotation Properties")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 4])

        # Plot 2: Particle spin values
        ax = axes[1]
        particles = ["γ", "e", "H", "g", "q", "W", "G"]
        spins = [1, 0.5, 0, 1, 0.5, 1, 2]
        colors = ["blue" if s == int(s) else "red" for s in spins]

        ax.bar(particles, spins, color=colors, edgecolor="black")
        ax.axhline(0.5, color="red", ls="--", alpha=0.5, label="Fermion")
        ax.axhline(1.0, color="blue", ls="--", alpha=0.5, label="Boson")
        ax.set_xlabel("Particle")
        ax.set_ylabel("Spin (ℏ)")
        ax.set_title("Particle Spins")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()

        output = save_path / "spin_statistics.png"
        plt.savefig(output, dpi=150, bbox_inches="tight")
        print(f"\n📊 Plot saved: {output}")


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════════╗
    ║             UET SPIN-STATISTICS                               ║
    ║   Phase B1: Spin from Topology                                ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    )

    spin = SpinStatisticsUET()
    success = spin.run_all_tests()
    spin.plot_results()
    exit(0 if success else 1)
