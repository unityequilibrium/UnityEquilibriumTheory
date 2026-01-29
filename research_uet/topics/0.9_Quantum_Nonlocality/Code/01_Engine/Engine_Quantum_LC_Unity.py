"""
Engine_Quantum_LC_Unity.py - UET Topic 0.9
==========================================
Simulates a Quantum LC Circuit (the basis of superconducting qubits)
using the Unity Equilibrium Theory.

UET Physics:
- Charge (Q) = Manifold Displacement (Spatial stretch).
- Flux (Phi) = Manifold Momentum (Phase velocity).
- Hamiltonian (H) = Total Unity Energy = (Phase_Vel^2 / 2L) + (Displacement^2 / 2C).
- Quantization = The Discrete Lattice restricts energy levels to harmonic modes.
"""

import numpy as np

# Base Solver Import
try:
    from research_uet.core.uet_base_solver import UETBaseSolver
except ImportError:
    import sys
    from pathlib import Path

    current = Path(__file__).resolve()
    root = None
    for parent in [current] + list(current.parents):
        if (parent / "research_uet").exists():
            root = parent
            sys.path.insert(0, str(root))
            break
    from research_uet.core.uet_base_solver import UETBaseSolver


class QuantumLCUnity(UETBaseSolver):
    def __init__(self, L=1.0, C=1.0, hbar=1.0):
        super().__init__(name="Quantum_LC_Reactor")
        self.L = L  # Inductance (Unity Inertia)
        self.C = C  # Capacitance (Unity Elasticity)
        self.hbar = hbar

        # Characteristic frequency (Manifold resonance frequency)
        self.omega = 1.0 / np.sqrt(L * C)

        # Zero-point fluctuations
        self.phi_zp = np.sqrt(hbar * L * self.omega / 2)
        self.q_zp = np.sqrt(hbar * C * self.omega / 2)

        print(f"⚡ Quantum LC Manifold Reactor Initialized")
        print(f"   Frequency (Omega): {self.omega:.4f}")
        print(f"   Zero-point Flux:   {self.phi_zp:.4f}")
        print(f"   Zero-point Charge: {self.q_zp:.4f}")

    def get_eigenenergy(self, n):
        """Returns the energy level n in the Unity Lattice."""
        return self.hbar * self.omega * (n + 0.5)

    def simulate_wavefunction(self, n=0, phi_range=(-5, 5), points=500):
        """
        Simulates the Manifold Displacement (Phi) for the n-th energy level.
        This represents the probability density of the Unity Field.
        """
        phi_vals = np.linspace(phi_range[0], phi_range[1], points)

        # Hermite-Gaussian modes (Standard Harmonic Oscillator)
        from scipy.special import hermite
        from math import factorial

        coeff = (1.0 / np.sqrt(2**n * factorial(n))) * (self.omega / (np.pi * self.hbar)) ** (1 / 4)
        xi = np.sqrt(self.omega / self.hbar) * phi_vals
        psi_n = coeff * np.exp(-(xi**2) / 2) * hermite(n)(xi)

        return phi_vals, psi_n


if __name__ == "__main__":
    lc = QuantumLCUnity(L=1e-9, C=1e-12)  # Realistic nH and pF

    # Save Results
    import json
    from pathlib import Path

    result_data = {
        "Topic": "0.9_Quantum_Nonlocality",
        "Category": "01_Engine",
        "Component": "Quantum_LC_Unity",
        "Parameters": {"L": lc.L, "C": lc.C, "Omega": lc.omega},
        "ZeroPoint": {"Phi_ZP": lc.phi_zp, "Q_ZP": lc.q_zp},
        "Energy_Levels": [lc.get_eigenenergy(n) for n in range(10)],
    }
    output_path = (
        Path(__file__).parent.parent.parent
        / "Result"
        / "01_Engine"
        / "01_Engine_Quantum_LC_Summary.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result_data, f, indent=4)
    print(f"📁 Result saved to: {output_path.name}")

    print("\n--- Energy Levels (Unity Harmonic Modes) ---")
    for n in range(5):
        print(f" Mode |{n}>: {lc.get_eigenenergy(n):.4e} J")
