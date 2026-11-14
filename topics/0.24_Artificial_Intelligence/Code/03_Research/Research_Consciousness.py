"""
Research_Consciousness.py
=========================
Topic: 0.24 Consciousness & Entropy
Hypothesis: "Consciousness is the act of maintaining Order (Low Entropy) against the flow of Time (High Entropy)."

Model:
1. Neural Field: A 2D Grid representing the brain's state.
2. Entropy (The Destroyer): Random noise added every step (Forgetting/Confusion).
3. Will (The Creator): A restorative force that reinforces the pattern (Attention).

Goal: Determine if "Natural Will" (Pattern Reinforcement) is required for "Self" to exist.
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


import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# --- ENVIRONMENT SETUP ---
script_path = Path(__file__).resolve()
project_root = script_path.parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from docs.core.uet_glass_box import UETPathManager


class ConsciousnessSimulator:
    def __init__(self, size=50):
        self.size = size
        self.field = np.zeros((size, size))
        self.entropy_rate = 0.1  # Rate of decay/noise

    def create_thought(self):
        """Injects a structured pattern (Gaussian) into the field."""
        x, y = np.meshgrid(np.arange(self.size), np.arange(self.size))
        center = self.size // 2
        sigma = 5.0
        # A simple "Idea" or "Self"
        pattern = np.exp(-((x - center) ** 2 + (y - center) ** 2) / (2 * sigma**2))
        self.field += pattern
        return pattern

    def step_entropy(self):
        """Apply the 2nd Law: Everything degrades."""
        # 1. Decay (Forgetting)
        self.field *= 0.95
        # 2. Noise (Confusion)
        noise = np.random.normal(0, 0.05, self.field.shape)
        self.field += noise

    def step_will(self, target_pattern, strength=0.0):
        """Apply Natural Will: The effort to remember/be."""
        # Reinforce the original pattern
        self.field += target_pattern * strength

    def measure_integrity(self, target_pattern):
        """How much of the 'Self' remains?"""
        # Correlation between current state and original 'Self'
        correlation = np.corrcoef(self.field.flatten(), target_pattern.flatten())[0, 1]
        return max(0, correlation)  # Clip negative correlations


def run_experiment():
    print("🧠 RESEARCH: CONSCIOUSNESS & ENTROPY")
    print("------------------------------------")
    print("Hypothesis: Existence requires active resistance (Will).")

    # Setup
    sim = ConsciousnessSimulator()
    original_self = sim.create_thought()

    print(f"Initial State: Organized Thought created.")

    # Simulation Loop
    steps = 50
    will_strengths = [0.0, 0.05, 0.10]  # No Will, Weak Will, Strong Will
    results = {}

    for strength in will_strengths:
        # Reset
        sim.field = original_self.copy()
        history = []

        for t in range(steps):
            sim.step_entropy()
            sim.step_will(original_self, strength)
            integrity = sim.measure_integrity(original_self)
            history.append(integrity)

        results[strength] = history
        final_state = "ALIVE" if history[-1] > 0.5 else "DEAD"
        print(
            f"Test (Will={strength:.2f}) -> Final Integrity: {history[-1]:.2f} [{final_state}]"
        )

    # Analysis
    print("\n🔍 ANALYSIS:")
    if results[0.0][-1] < 0.1 and results[0.10][-1] > 0.8:
        print("✅ SUCCESS: The 'Self' requires Will interaction.")
        print("   - Passive Existence (No Will) leads to disintegration (Death).")
        print("   - Active Existence (Will) maintains the Vortex of Self.")
        print(
            "   - This confirms 'Being is Becoming' (You must constantly BECOME to BE)."
        )

        # Plot
        result_dir = UETPathManager.get_result_dir(
            topic_id="0.24_Artificial_Intelligence",
            experiment_name="Research_Consciousness",
            pillar="03_Research",
            category="log",
        )
        plt.figure(figsize=(10, 6))
        for strength, history in results.items():
            label = f"Will Strength {strength}"
            if strength == 0.0:
                label += " (Passive)"
            if strength == 0.1:
                label += " (Active)"
            plt.plot(history, label=label, linewidth=2)

        plt.xlabel("Time (Steps)")
        plt.ylabel("Self-Integrity (Correlation)")
        plt.title("The Stability of Self: Entropy vs Will")
        plt.axhline(0.5, color="r", linestyle="--", label="Death Threshold")
        plt.legend()
        plt.savefig(result_dir / "Self_Stability.png")
        print(f"   Plot saved to: {result_dir}")

    else:
        print("❌ FAILURE: Entropy dynamics unclear.")


if __name__ == "__main__":
    run_experiment()
