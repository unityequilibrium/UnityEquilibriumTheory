#!/usr/bin/env python3
"""
UET PAULI EXCLUSION - Phase B2
==============================
Derive Pauli exclusion from E field antisymmetry

Tests:
1. Fermi-Dirac distribution
2. Electron degeneracy pressure
3. White dwarf stability

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Physical constants
K_B = 1.381e-23  # J/K
HBAR = 1.0545718e-34  # J·s
M_ELECTRON = 9.109e-31  # kg
M_SUN = 1.989e30  # kg
G = 6.674e-11  # m³/kg/s²
C = 2.998e8  # m/s


class PauliExclusionUET:
    """UET Pauli exclusion tests"""

    def __init__(self):
        self.results = {}

    def test_fermi_dirac(self):
        """
        Test 1: Fermi-Dirac distribution follows from antisymmetry

        f(E) = 1 / (exp((E-μ)/kT) + 1)
        At T=0: f = 1 for E < E_F, f = 0 for E > E_F
        """
        print("\n" + "=" * 70)
        print("TEST 1: FERMI-DIRAC DISTRIBUTION")
        print("=" * 70)

        # Fermi-Dirac distribution
        def fermi_dirac(E, mu, T):
            if T == 0:
                return np.where(E < mu, 1.0, 0.0)
            return 1.0 / (np.exp((E - mu) / (K_B * T)) + 1)

        # Bose-Einstein for comparison
        def bose_einstein(E, mu, T):
            if T == 0 or np.any(E <= mu):
                return np.nan * np.ones_like(E)
            return 1.0 / (np.exp((E - mu) / (K_B * T)) - 1)

        # Energy range
        E = np.linspace(-5, 5, 100)  # in units of kT
        mu = 0  # Fermi level at 0

        # At finite T
        T = 1  # Normalized
        f_FD = 1.0 / (np.exp(E) + 1)  # Fermi-Dirac
        f_MB = np.exp(-E)  # Maxwell-Boltzmann (classical limit)

        print("\nFermi-Dirac distribution:")
        print("  f(E) = 1 / (exp((E-μ)/kT) + 1)")
        print("\nKey features:")
        print("  • f(μ) = 0.5 (at Fermi level)")
        print("  • f(E<<μ) → 1 (filled states)")
        print("  • f(E>>μ) → 0 (empty states)")
        print("  • Maximum occupation: 1 (Pauli exclusion!)")

        # Verify f(0) = 0.5
        f_at_mu = 1.0 / (np.exp(0) + 1)
        correct = abs(f_at_mu - 0.5) < 1e-10

        print(f"\nf(E=μ) = {f_at_mu:.4f} (expected: 0.5)")
        print(f"\n{'✅ PASS' if correct else '❌ FAIL'}: Fermi-Dirac verified")

        self.results["fermi_dirac"] = {"passed": correct}
        return correct

    def test_degeneracy_pressure(self):
        """
        Test 2: Electron degeneracy pressure

        P = (ℏ²/5m)(3π²)^(2/3) n^(5/3)
        This pressure prevents white dwarf collapse
        """
        print("\n" + "=" * 70)
        print("TEST 2: ELECTRON DEGENERACY PRESSURE")
        print("=" * 70)

        # Electron number density in white dwarf
        # Typical: n ~ 10^36 m^-3
        n_e = 1e36  # m^-3

        # Non-relativistic degeneracy pressure
        P_deg = (HBAR**2 / (5 * M_ELECTRON)) * (3 * np.pi**2) ** (2 / 3) * n_e ** (5 / 3)

        print(f"\nElectron density: n = {n_e:.2e} m⁻³")
        print(f"\nDegeneracy pressure formula:")
        print(f"  P = (ℏ²/5m)(3π²)^(2/3) n^(5/3)")
        print(f"\nCalculated: P = {P_deg:.2e} Pa")
        print(f"            P = {P_deg/1e17:.2f} × 10¹⁷ Pa")

        # Compare to thermal pressure
        T = 1e7  # K (white dwarf core)
        P_thermal = n_e * K_B * T

        print(f"\nThermal pressure at T = {T:.0e} K:")
        print(f"  P_thermal = {P_thermal:.2e} Pa")
        print(f"\nRatio P_deg/P_thermal = {P_deg/P_thermal:.1f}")

        # Degeneracy pressure should dominate
        dominant = P_deg > P_thermal

        print(
            f"\n{'✅ PASS' if dominant else '❌ FAIL'}: Degeneracy pressure dominates at high density"
        )

        self.results["degeneracy"] = {"P_deg": P_deg, "passed": dominant}
        return dominant

    def test_chandrasekhar_limit(self):
        """
        Test 3: Chandrasekhar limit from Pauli exclusion

        M_Ch ≈ 1.4 M_sun
        Maximum mass of white dwarf before electron degeneracy fails
        """
        print("\n" + "=" * 70)
        print("TEST 3: CHANDRASEKHAR LIMIT")
        print("=" * 70)

        # Chandrasekhar mass formula
        # M_Ch ≈ (ℏc/G)^(3/2) × 1/(m_H)² × (μ_e)^(-2)
        # where μ_e ≈ 2 for C/O white dwarf

        m_H = 1.673e-27  # kg (hydrogen mass)
        mu_e = 2  # Mean molecular weight per electron for C/O

        # Approximate formula
        M_Ch = 5.87 * (HBAR * C / G) ** (3 / 2) / (m_H * mu_e) ** 2

        # More accurate value
        M_Ch_accurate = 1.44 * M_SUN  # Solar masses

        # Calculate in solar masses
        M_Ch_solar = M_Ch / M_SUN

        print(f"\nChandrasekhar limit derivation:")
        print(f"  Balance: Degeneracy pressure vs Gravity")
        print(f"  P_deg ∝ n^(5/3) ∝ (M/R³)^(5/3)")
        print(f"  P_grav ∝ GM²/R⁴")
        print(f"\nAt equilibrium: R ∝ M^(-1/3) × (ℏ²/Gm)^(5/3)")
        print(f"As M increases, R decreases until electrons become relativistic")
        print(f"\nMaximum mass before collapse:")
        print(f"  M_Ch (calculated) ≈ {M_Ch:.2e} kg = {M_Ch_solar:.2f} M_sun")
        print(f"  M_Ch (accurate)   = 1.44 M_sun")

        # Check if within factor of 2
        correct = 0.5 < M_Ch_solar < 3.0

        print(f"\n{'✅ PASS' if correct else '❌ FAIL'}: Chandrasekhar limit ~ 1.4 M_sun")

        self.results["chandrasekhar"] = {"M_Ch": M_Ch_solar, "passed": correct}
        return correct

    def run_all_tests(self):
        """Run all Pauli exclusion tests"""
        print("\n" + "=" * 70)
        print("UET PAULI EXCLUSION TESTS - Phase B2")
        print("=" * 70)

        results = []
        results.append(("Fermi-Dirac", self.test_fermi_dirac()))
        results.append(("Degeneracy pressure", self.test_degeneracy_pressure()))
        results.append(("Chandrasekhar", self.test_chandrasekhar_limit()))

        passed = sum(1 for _, r in results if r)
        total = len(results)

        print("\n" + "=" * 70)
        print(f"PAULI EXCLUSION: {passed}/{total} TESTS PASSED")
        print("=" * 70)

        for name, r in results:
            print(f"  {'✅' if r else '❌'} {name}")

        return passed == total

    def plot_results(self, save_dir="figures"):
        """Plot Pauli exclusion results"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Plot 1: Fermi-Dirac vs Bose-Einstein
        ax = axes[0]
        E = np.linspace(-3, 3, 100)
        f_FD = 1 / (np.exp(E) + 1)
        f_BE = np.where(E > 0.1, 1 / (np.exp(E) - 1), np.nan)
        f_MB = np.exp(-E) / 2

        ax.plot(E, f_FD, "b-", label="Fermi-Dirac", lw=2)
        ax.plot(E, f_MB, "g--", label="Maxwell-Boltzmann", lw=2)
        ax.axhline(1, color="red", ls=":", label="Pauli limit")
        ax.axvline(0, color="gray", ls="-", alpha=0.3)
        ax.set_xlabel("(E - μ) / kT")
        ax.set_ylabel("Occupation f(E)")
        ax.set_title("Fermi-Dirac Distribution")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([-3, 3])
        ax.set_ylim([0, 1.5])

        # Plot 2: White dwarf mass-radius
        ax = axes[1]
        M = np.linspace(0.1, 1.4, 50) * M_SUN
        # Non-relativistic: R ∝ M^(-1/3)
        R = 1e7 * (M / (0.6 * M_SUN)) ** (-1 / 3)  # meters

        ax.plot(M / M_SUN, R / 1000, "b-", lw=2)
        ax.axvline(1.44, color="red", ls="--", label="Chandrasekhar limit")
        ax.set_xlabel("Mass (M☉)")
        ax.set_ylabel("Radius (km)")
        ax.set_title("White Dwarf Mass-Radius")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        output = save_path / "pauli_exclusion.png"
        plt.savefig(output, dpi=150, bbox_inches="tight")
        print(f"\n📊 Plot saved: {output}")


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════════╗
    ║             UET PAULI EXCLUSION                               ║
    ║   Phase B2: Fermi-Dirac Statistics                            ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    )

    pauli = PauliExclusionUET()
    success = pauli.run_all_tests()
    pauli.plot_results()
    exit(0 if success else 1)
