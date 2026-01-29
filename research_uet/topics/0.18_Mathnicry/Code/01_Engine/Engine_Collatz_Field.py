"""
Engine_Collatz_Field.py - UET Topic 0.18
========================================
A High-Performance Field Engine for the 3n+1 Manifold.
Treats numbers as Information Densities (Psi) flowing towards Unity.
"""

import numpy as np
import math

# Base Solver Import
try:
    from research_uet.core.uet_base_solver import UETBaseSolver
except ImportError:
    import sys

    # Fallback to relative if package fails
    from pathlib import Path

    current = Path(__file__).resolve()
    # Find root
    root = None
    for parent in [current] + list(current.parents):
        if (parent / "research_uet").exists():
            root = parent
            sys.path.insert(0, str(root))
            break
    from research_uet.core.uet_base_solver import UETBaseSolver


class CollatzFieldEngine(UETBaseSolver):
    def __init__(self, name="UET_Collatz_Field"):
        super().__init__(name=name)
        self.history = []

    def get_binary_entropy(self, n: int) -> float:
        """Calculates the Shannon Entropy of the bit-pattern of N."""
        bits = bin(n)[2:]
        counts = [bits.count("0"), bits.count("1")]
        total = len(bits)
        probs = [c / total for c in counts if c > 0]
        return -sum(p * np.log2(p) for p in probs)

        if n <= 1:
            return 0.0
        # Omega increases with scale but is modulated by entropy
        entropy = self.get_binary_entropy(n)
        potential = math.log2(n) * (1.0 + entropy)
        return float(potential)

    def calculate_omega(self, n: int) -> float:
        """
        The UET Potential (Omega) for a number N.
        Equilibrium (1) has Omega = 0.
        """
        if n <= 1:
            return 0.0
        entropy = self.get_binary_entropy(n)
        potential = math.log2(n) * (1.0 + entropy)
        return float(potential)

    def calculate_lyapunov_gradient(self, n: int) -> float:
        """
        Calculates the 'Cycle-Aware Energy Gradient'.
        If N is odd, we look at the expected result after the mandatory division.
        """
        if n <= 1:
            return 0.0

        omega_curr = self.calculate_omega(n)

        if n % 2 == 0:
            # Direct decay
            omega_next = self.calculate_omega(n // 2)
        else:
            # 3n+1 is ALWAYS followed by at least one division
            # We look at the potential of (3n+1)/2 as the atomic unit of odd-step evolution
            omega_next = self.calculate_omega((3 * n + 1) // 2)

        return omega_next - omega_curr

    def transform(self, n: int) -> int:
        """The 3n+1 Step."""
        if n % 2 == 0:
            return n // 2
        else:
            return 3 * n + 1

    def solve_trajectory(self, start_n: int, max_steps: int = 1000):
        """Runs the trajectory and logs the field potential at each step."""
        curr = start_n
        path = []

        for i in range(max_steps):
            omega = self.calculate_omega(curr)
            path.append({"n": curr, "omega": omega})

            if curr == 1:
                break
            curr = self.transform(curr)

        return path

    def summary(self, start_n: int):
        path = self.solve_trajectory(start_n)
        print(f"📉 UET Collatz Field Summary for N={start_n}:")
        print(f"   Steps to Unity: {len(path)-1}")
        print(f"   Peak Potential: {max(p['omega'] for p in path):.4f}")
        print(f"   Final State:   {path[-1]['n']} (Omega={path[-1]['omega']:.1f})")
        return path
