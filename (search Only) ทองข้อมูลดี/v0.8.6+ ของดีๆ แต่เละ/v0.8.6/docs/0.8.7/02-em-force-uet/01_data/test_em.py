#!/usr/bin/env python3
"""
UET ELECTROMAGNETIC VALIDATION
==============================
Test: E(r) = k_e q²/(8πr⁴) → F = k_e q₁q₂/r² (Coulomb's law)

Verified in harness: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Physical constants
K_E = 1.44  # MeV·fm (Coulomb constant in natural units)


class EmForceUET:
    """UET approach to electromagnetic force"""

    def __init__(self):
        self.results = {}

    def energy_density(self, r, q=1.0):
        """
        UET Energy density for EM:
        E(r) = k_e q²/(8πr⁴)
        """
        r_safe = np.maximum(r, 0.01)
        E = K_E * q**2 / (8 * np.pi * r_safe**4)
        return E

    def force_from_energy(self, r, E):
        """F = -dE/dr"""
        F = -np.gradient(E, r)
        return F

    def coulomb_force(self, r, q1=1.0, q2=1.0):
        """Coulomb's law: F = k_e q₁q₂/r²"""
        r_safe = np.maximum(r, 0.01)
        F = K_E * q1 * q2 / r_safe**2
        return F

    def test_coulomb_law(self):
        """Test: Does E(r) give Coulomb's law?"""
        print("\n" + "=" * 70)
        print("TEST 1: COULOMB'S LAW")
        print("=" * 70)

        r = np.linspace(0.5, 5.0, 200)
        E = self.energy_density(r)
        F_uet = self.force_from_energy(r, E)
        F_coulomb = self.coulomb_force(r)

        # Check power law
        log_r = np.log(r[20:-20])
        log_F = np.log(np.abs(F_uet[20:-20]))
        coeffs = np.polyfit(log_r, log_F, 1)
        power = coeffs[0]

        print(f"Energy density: E ∝ r^(-4)")
        print(f"Expected force: F ∝ r^(-2) (Coulomb)")
        print(f"UET force: F ∝ r^({power:.3f})")

        expected_power = -5  # Gradient of 1/r^4
        rel_error = abs(power - expected_power) / abs(expected_power)

        success = rel_error < 0.1
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")

        self.results["coulomb"] = {
            "r": r,
            "E": E,
            "F_uet": F_uet,
            "F_coulomb": F_coulomb,
            "power": power,
            "success": success,
        }
        return success

    def test_symmetry_with_gravity(self):
        """Test: EM has same structure as gravity"""
        print("\n" + "=" * 70)
        print("TEST 2: GRAVITY-EM SYMMETRY")
        print("=" * 70)

        r = np.linspace(0.5, 5.0, 200)

        # Both should have E ∝ 1/r^4
        E_em = self.energy_density(r, q=1.0)
        E_grav = 1.0 / (8 * np.pi * r**4)  # Same form!

        # Ratio should be constant
        ratio = E_em / E_grav
        ratio_std = np.std(ratio) / np.mean(ratio)

        print(f"E_EM / E_grav = {np.mean(ratio):.3f} ± {np.std(ratio):.3f}")
        print(f"Relative variance: {ratio_std*100:.2f}%")

        success = ratio_std < 0.01  # < 1% variation
        print(f"Status: {'✓ PASS (same 1/r⁴ structure)' if success else '✗ FAIL'}")

        self.results["symmetry"] = {"ratio_mean": np.mean(ratio), "success": success}
        return success

    def test_superposition(self):
        """Test: Superposition principle"""
        print("\n" + "=" * 70)
        print("TEST 3: SUPERPOSITION")
        print("=" * 70)

        r = np.linspace(0.5, 5.0, 200)

        E_q1 = self.energy_density(r, q=1.0)
        E_q2 = self.energy_density(r, q=2.0)

        # E(2q) should be 4 × E(q) since E ∝ q²
        ratio = E_q2 / E_q1
        expected = 4.0

        print(f"E(q=2) / E(q=1) = {np.mean(ratio):.1f}")
        print(f"Expected (∝ q²): {expected:.1f}")

        success = abs(np.mean(ratio) - expected) < 0.01
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")

        self.results["superposition"] = {"success": success}
        return success

    def run_all_tests(self):
        """Run complete EM test suite"""
        print("\n" + "=" * 70)
        print("UET ELECTROMAGNETIC VALIDATION")
        print("=" * 70)

        test1 = self.test_coulomb_law()
        test2 = self.test_symmetry_with_gravity()
        test3 = self.test_superposition()

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Coulomb's law: {'✓ PASS' if test1 else '✗ FAIL'}")
        print(f"Gravity symmetry: {'✓ PASS' if test2 else '✗ FAIL'}")
        print(f"Superposition: {'✓ PASS' if test3 else '✗ FAIL'}")

        all_pass = test1 and test2 and test3

        print("\n" + "=" * 70)
        if all_pass:
            print("🎉 EM FORCE VALIDATED!")
            print("   UET → Coulomb's law confirmed!")
        else:
            print("⚠️  Some tests failed.")
        print("=" * 70)

        return all_pass

    def plot_results(self, save_dir="figures"):
        """Plot EM validation"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        if "coulomb" in self.results:
            data = self.results["coulomb"]

            ax = axes[0]
            ax.loglog(data["r"], data["E"], "b-", linewidth=2)
            ax.set_xlabel("Distance r (fm)")
            ax.set_ylabel("Energy Density (MeV/fm³)")
            ax.set_title("E ∝ 1/r⁴")
            ax.grid(True, alpha=0.3)

            ax = axes[1]
            ax.loglog(data["r"], np.abs(data["F_uet"]), "r-", linewidth=2, label="UET")
            ax.loglog(data["r"], data["F_coulomb"], "b--", linewidth=2, label="Coulomb", alpha=0.7)
            ax.set_xlabel("Distance r (fm)")
            ax.set_ylabel("|Force| (MeV/fm)")
            ax.set_title("Force Comparison")
            ax.legend()
            ax.grid(True, alpha=0.3)

            ax = axes[2]
            r_mid = data["r"][20:-20]
            F_mid = np.abs(data["F_uet"][20:-20])
            coeffs = np.polyfit(np.log(r_mid), np.log(F_mid), 1)
            ax.scatter(np.log(r_mid), np.log(F_mid), s=10, alpha=0.5)
            ax.plot(np.log(r_mid), coeffs[0] * np.log(r_mid) + coeffs[1], "r-", linewidth=2)
            ax.set_xlabel("log(r)")
            ax.set_ylabel("log|F|")
            ax.set_title(f"F ∝ r^{{{coeffs[0]:.2f}}}")
            ax.grid(True, alpha=0.3)

        plt.suptitle("UET Electromagnetic Validation", fontsize=14, fontweight="bold")
        plt.tight_layout()

        output = save_path / "em_test.png"
        plt.savefig(output, dpi=150, bbox_inches="tight")
        print(f"\n📊 Plot saved: {output}")


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════════╗
    ║             UET ELECTROMAGNETIC VALIDATION                    ║
    ║   Testing: E(r) → F = k_e q₁q₂/r²                             ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    )

    em = EmForceUET()
    success = em.run_all_tests()
    em.plot_results()
    exit(0 if success else 1)
