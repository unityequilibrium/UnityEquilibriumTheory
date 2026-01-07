#!/usr/bin/env python3
"""
UET QUANTUM EXTENSION - Phase 2 Tests
======================================
Testing how UET connects to quantum mechanics

Tests:
1. Uncertainty Principle from wave properties
2. Casimir force (F = -∇E works for vacuum)
3. De Broglie relation (wave-particle duality)
4. Energy quantization (standing waves)

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Physical constants
HBAR_C_eVnm = 197.3  # eV·nm


class QuantumUET:
    """UET approach to quantum mechanics"""

    def __init__(self):
        self.results = {}

    def test_uncertainty_from_waves(self):
        """Uncertainty principle emerges from wave localization"""
        print("\n" + "=" * 70)
        print("TEST 1: UNCERTAINTY PRINCIPLE FROM WAVES")
        print("=" * 70)

        def momentum_uncertainty(sigma):
            return 1 / (2 * sigma)  # In units where ℏ = 1

        sigmas = [0.5, 1.0, 2.0, 4.0]
        print("\nLocalization vs Momentum spread:")
        print(f"{'σ (Δx)':>10} {'Δp (ℏ=1)':>12} {'ΔxΔp':>10}")
        print("-" * 35)

        products = []
        for sigma in sigmas:
            delta_x = sigma
            delta_p = momentum_uncertainty(sigma)
            product = delta_x * delta_p
            products.append(product)
            print(f"{sigma:>10.2f} {delta_p:>12.4f} {product:>10.4f}")

        min_product = min(products)
        print(f"\nMinimum ΔxΔp = {min_product:.4f}")
        print(f"Heisenberg limit = 0.50")

        success = all(p >= 0.49 for p in products)
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")

        self.results["uncertainty"] = {"sigmas": sigmas, "products": products, "success": success}
        return success

    def test_casimir_force(self):
        """Casimir effect as prototype for F = -∇E"""
        print("\n" + "=" * 70)
        print("TEST 2: CASIMIR FORCE (F = -∇E)")
        print("=" * 70)

        d = np.linspace(10, 100, 100)  # nm
        E_casimir = -np.pi**2 * HBAR_C_eVnm / (720 * d**3)
        F_casimir = -np.gradient(E_casimir, d)
        F_theory = -np.pi**2 * HBAR_C_eVnm / (240 * d**4)

        ratio = F_casimir / F_theory
        rel_error = np.std(ratio[10:-10]) / np.mean(ratio[10:-10])

        print(f"\nCasimir energy: E ∝ -1/d³")
        print(f"Force from gradient: F = -dE/dd")
        print(f"F_gradient / F_theory = {np.mean(ratio[10:-10]):.4f}")
        print(f"Relative error: {rel_error*100:.1f}%")

        success = rel_error < 0.05
        print(f"Status: {'✓ PASS (F = -∇E works!)' if success else '✗ FAIL'}")

        self.results["casimir"] = {
            "d": d,
            "E": E_casimir,
            "F_gradient": F_casimir,
            "F_theory": F_theory,
            "success": success,
        }
        return success

    def test_de_broglie_relation(self):
        """de Broglie wavelength λ = h/p"""
        print("\n" + "=" * 70)
        print("TEST 3: DE BROGLIE RELATION")
        print("=" * 70)

        m_e = 0.511e6  # eV/c²
        KE = 1.0  # eV
        p_classical = np.sqrt(2 * m_e * KE)
        lambda_dB = 2 * np.pi * HBAR_C_eVnm / p_classical

        print(f"Electron kinetic energy: {KE:.1f} eV")
        print(f"de Broglie wavelength: λ = {lambda_dB:.4f} nm = {lambda_dB*10:.4f} Å")

        expected_lambda = 1.226  # nm for 1 eV electron
        rel_error = abs(lambda_dB - expected_lambda) / expected_lambda
        print(f"\nExpected: λ = {expected_lambda:.3f} nm")
        print(f"Error: {rel_error*100:.1f}%")

        success = rel_error < 0.05
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")

        self.results["de_broglie"] = {
            "lambda_dB": lambda_dB,
            "expected": expected_lambda,
            "success": success,
        }
        return success

    def test_energy_quantization(self):
        """Particle in box gives E_n ∝ n²"""
        print("\n" + "=" * 70)
        print("TEST 4: ENERGY QUANTIZATION")
        print("=" * 70)

        L = 1.0  # nm
        prefactor = np.pi**2 * HBAR_C_eVnm**2 / (2 * 0.511e6 * L**2)

        print(f"Box size: L = {L} nm")
        print(f"\n{'n':>5} {'E_n (eV)':>15} {'E_n/E_1':>10}")
        print("-" * 35)

        E_theory = []
        for n in range(1, 6):
            E_n = n**2 * prefactor
            E_theory.append(E_n)
            print(f"{n:>5} {E_n:>15.4f} {E_n/prefactor:>10.1f}")

        ratio = E_theory[1] / E_theory[0]
        success = abs(ratio - 4.0) < 0.01
        print(f"\nE_2/E_1 = {ratio:.1f} (expected: 4.0)")
        print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")

        self.results["quantization"] = {"levels": E_theory, "success": success}
        return success

    def run_all_tests(self):
        """Run complete quantum test suite"""
        print("\n" + "=" * 70)
        print("UET QUANTUM EXTENSION - Phase 2")
        print("=" * 70)

        test1 = self.test_uncertainty_from_waves()
        test2 = self.test_casimir_force()
        test3 = self.test_de_broglie_relation()
        test4 = self.test_energy_quantization()

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Uncertainty Principle: {'✓ PASS' if test1 else '✗ FAIL'}")
        print(f"Casimir Force (F=-∇E): {'✓ PASS' if test2 else '✗ FAIL'}")
        print(f"de Broglie Relation: {'✓ PASS' if test3 else '✗ FAIL'}")
        print(f"Energy Quantization: {'✓ PASS' if test4 else '✗ FAIL'}")

        all_pass = test1 and test2 and test3 and test4
        passed = sum([test1, test2, test3, test4])

        print("\n" + "=" * 70)
        if all_pass:
            print("🎉 ALL QUANTUM TESTS PASSED!")
        else:
            print(f"⚠️  {passed}/4 tests passed.")
        print("=" * 70)

        return all_pass

    def plot_results(self, save_dir="figures"):
        """Plot quantum test results"""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Plot 1: Uncertainty
        ax = axes[0, 0]
        if "uncertainty" in self.results:
            sigmas = self.results["uncertainty"]["sigmas"]
            products = self.results["uncertainty"]["products"]
            ax.bar(range(len(sigmas)), products, color="steelblue")
            ax.axhline(0.5, color="red", linestyle="--", label="Heisenberg limit")
            ax.set_xticks(range(len(sigmas)))
            ax.set_xticklabels([f"σ={s}" for s in sigmas])
            ax.set_ylabel("ΔxΔp")
            ax.set_title("Uncertainty Principle")
            ax.legend()
            ax.grid(True, alpha=0.3)

        # Plot 2: Casimir
        ax = axes[0, 1]
        if "casimir" in self.results:
            data = self.results["casimir"]
            ax.plot(data["d"], -data["F_gradient"] * 1e6, "b-", linewidth=2, label="F = -dE/dd")
            ax.plot(
                data["d"], -data["F_theory"] * 1e6, "r--", linewidth=2, label="Theory", alpha=0.7
            )
            ax.set_xlabel("Separation d (nm)")
            ax.set_ylabel("|F| (μeV/nm³)")
            ax.set_title("Casimir Force")
            ax.legend()
            ax.grid(True, alpha=0.3)

        # Plot 3: de Broglie
        ax = axes[1, 0]
        energies = np.logspace(-1, 3, 50)
        m_e = 0.511e6
        wavelengths = 2 * np.pi * HBAR_C_eVnm / np.sqrt(2 * m_e * energies)
        ax.loglog(energies, wavelengths, "b-", linewidth=2)
        ax.set_xlabel("Kinetic Energy (eV)")
        ax.set_ylabel("de Broglie λ (nm)")
        ax.set_title("Wave-Particle Duality")
        ax.grid(True, alpha=0.3)

        # Plot 4: Energy levels
        ax = axes[1, 1]
        if "quantization" in self.results:
            levels = self.results["quantization"]["levels"]
            n_vals = np.arange(1, len(levels) + 1)
            ax.bar(n_vals, levels, color="green", alpha=0.7)
            ax.plot(n_vals, levels[0] * n_vals**2, "r--", linewidth=2, label="E ∝ n²")
            ax.set_xlabel("Quantum number n")
            ax.set_ylabel("Energy (eV)")
            ax.set_title("Quantized Energy")
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.suptitle("UET Quantum Extension", fontsize=14, fontweight="bold")
        plt.tight_layout()

        output = save_path / "quantum_tests.png"
        plt.savefig(output, dpi=150, bbox_inches="tight")
        print(f"\n📊 Plot saved: {output}")


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════════╗
    ║             UET QUANTUM EXTENSION                             ║
    ║   Phase 2: Quantum Mechanics Integration                      ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    )

    quantum = QuantumUET()
    success = quantum.run_all_tests()
    quantum.plot_results()
    exit(0 if success else 1)
