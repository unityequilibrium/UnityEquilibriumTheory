"""
Research_Grover_Search_UET.py - UET Topic 0.18
==============================================
Implements Grover's Search Algorithm using the QuantumUnityEngine.
Goal: Find a 'Hidden Marked State' in a database of N elements using only sqrt(N) steps.

UET Interpretation:
- The "Marked State" is a point of destructive interference in the Unity Field.
- The "Diffuser" is a global phase inversion that pulls the rest of the manifold's
  energy into that target point (Resonance Amplification).
"""

import sys
import numpy as np
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "research_uet").exists():
        ROOT = parent
        break

if ROOT and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Engine Import
engine_dir = current_path.parent.parent / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))
from Engine_Quantum_Logic import QuantumUnityEngine


class GroverUETExperiment:
    def __init__(self, num_qubits=3, target_idx=5):
        self.num_qubits = num_qubits
        self.n = 2**num_qubits
        self.target_idx = target_idx
        self.engine = QuantumUnityEngine(num_qubits)

        print(f"🚀 Initializing Grover Search for {self.n} states...")
        print(
            f"🎯 Target Index: {target_idx} (|{format(target_idx, f'0{num_qubits}b')}>)"
        )

    def apply_oracle(self):
        """
        Grover Oracle: Flips the phase of the target state.
        Optimized: Direct index negation (No matrix overhead).
        """
        self.engine.state[self.target_idx] *= -1

    def apply_diffuser(self):
        """
        Grover Diffuser (Inversion about Mean):
        Optimized: D|v> = 2<s|v>|s> - |v> (No RAM crashes).
        Note: <s|v> is the mean of all amplitudes times sqrt(N).
        """
        mean_amp = np.mean(self.engine.state)
        # Apply inversion: v' = 2*mean - v
        self.engine.state = 2 * mean_amp - self.engine.state

    def run(self):
        # 1. Initialize Superposition (Put Unity Field into uniform vibration)
        for i in range(self.num_qubits):
            self.engine.apply_hadamard(i)

        # 2. Iterations (Optimal steps ~ pi/4 * sqrt(N))
        iterations = int(np.pi / 4 * np.sqrt(self.n))
        print(f"🔄 Running {iterations} iterations of Oracle + Diffuser...")

        for i in range(iterations):
            self.apply_oracle()
            self.apply_diffuser()

            # Check current energy concentration (Optional)
            probs = np.abs(self.engine.state) ** 2
            target_prob = probs[self.target_idx]
            print(f"  Iter {i+1}: Resonance at target = {target_prob:.4f}")

        # 3. Final Result
        print("\n--- Final Unity Field Profile ---")
        self.engine.summary()

        # 4. Success Check
        res = self.engine.measure_collapse()
        res_idx = int("".join(map(str, res)), 2)
        print(
            f"\n🔍 Measured Result: |{format(res_idx, f'0{self.num_qubits}b')}> (Index: {res_idx})"
        )

        if res_idx == self.target_idx:
            print("✨ SUCCESS: Unity Field converged on the correct solution!")
        else:
            print("⚠️ FAILURE: Convergence failed.")


if __name__ == "__main__":
    # Test with 4 qubits (16 states), looking for index 13
    exp = GroverUETExperiment(num_qubits=4, target_idx=13)
    exp.run()
