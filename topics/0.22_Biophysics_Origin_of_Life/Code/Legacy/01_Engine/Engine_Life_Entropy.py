"""
Engine: UET Biophysics (Origin of Life)
=======================================
Topic: 0.22 Biophysics
Folder: 01_Engine

Simulates Erwin Schrödinger's "Negative Entropy" concept.
Life maintains low entropy by exporting entropy to the environment.

Formula: dS_life/dt = -k_B * I (Information Flow) + dS_metabolism
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import sys
import numpy as np
from pathlib import Path

# --- ROBUST PATH FINDER ---


# Base Solver & Parameter Imports
try:
    from docs.core.uet_base_solver import UETBaseSolver
    from docs.core.uet_parameters import get_params
except ImportError:
    import sys
    from pathlib import Path

    current = Path(__file__).resolve()
    root = None
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists():
            root = parent
            sys.path.insert(0, str(root))
            break
    from docs.core.uet_base_solver import UETBaseSolver


class LifeEngine(UETBaseSolver):
    """
    Simulates a living system as an Information Processing Agent.
    """

    def __init__(self, params=None):
        # Axiomatic Scale: Biophysics
        super().__init__(name="Origin_of_Life_Entropy", topic="0.22_Biophysics", pillar="01_Engine", params=params)
        
        # Axiomatic Initialization
        self.entropy_internal = 1.0  # Normalized Baseline
        # Information Intake linked to Screening Beta (Axiom 2)
        self.information_intake = self.params.beta / self.params.I_max
        # Decay rate linked to Informational Loss (Phi - Axiom 1)
        self.decay_rate = self.params.phi_loss / self.params.I_max

    def step(self, t):
        """
        Evolution step: dS = Decay - Information_Processing
        """
        # 2nd Law: Entropy tends to increase
        self.entropy_internal += self.decay_rate

        # Life: Actively reduces entropy via information/energy intake
        # "It feeds on negative entropy" - Schrödinger
        self.entropy_internal -= self.information_intake

        # --- QUANTUM HARDENING (Landauer's Limit) ---
        # Minimum entropy is bounded by the Information Scale
        min_entropy = max(0.01, (1.0 - self.params.kappa))
        if self.entropy_internal < min_entropy:
            self.entropy_internal = min_entropy

        return self.entropy_internal


def run_life_simulation():
    print("=" * 60)
    print("⚙️  ENGINE: UET Biophysics (Origin of Life)")
    print("    Topic 0.22 - Schrödinger's Negative Entropy")
    print("=" * 60)

    life = LifeEngine()

    print(f"{'Time':<10} | {'Entropy (S)':<15} | {'State':<15}")
    print("-" * 50)

    # Simulate 10 steps
    for t in range(10):
        s = life.step(t)
        state = "Alive (Ordered)" if s < 0.8 else "Dead (Disordered)"
        print(f"{t:<10} | {s:<15.4f} | {state:<15}")

    print("-" * 50)

    # Compare with Non-Living Rock
    rock = LifeEngine()
    rock.information_intake = 0.0  # Rocks don't eat
    s_rock = rock.step(0)

    print(f"\nBenchmark:")
    print(f"  Living System S_final: {life.entropy_internal:.4f}")
    print(f"  Non-Living (Rock) S:   {s_rock:.4f} (Increasing)")

    if life.entropy_internal < s_rock:
        print("\n✅ PASS: Life successfully resists the 2nd Law via Information.")
        return True
    else:
        print("\n❌ FAIL: Life died.")
        return False


if __name__ == "__main__":
    run_life_simulation()
