"""
Verify_Quantum_Logic.py
=======================
Grand Production Upscale: Verification of Topic 0.18.
Checks if UET Quantum Engine correctly handles Entanglement and Information Entropy.

Test Case: Bell State Generation |Phi+> = (|00> + |11>) / sqrt(2)
Target:
    1. Probabilities: P(00)=0.5, P(11)=0.5
    2. Von Neumann Entropy (Entanglement): S = 1.0 (Maximal for 2 qubits)
"""

import sys
from pathlib import Path
import numpy as np

# Path Fix
current_path = Path(__file__).resolve()
# Go up to 'research_uet' parent
root_path = current_path.parents[5]
sys.path.append(str(root_path))

# Local Import
engine_dir = current_path.parents[1] / "01_Engine"
sys.path.append(str(engine_dir))

from Engine_Quantum_Logic import UETQuantumSolver


def run_verification():
    print("🔮 UET QUANTUM LOGIC: PRODUCTION VERIFICATION")
    print("=============================================")
    print("Target: Bell State Entanglement Entropy (S=1.0)\n")

    # 1. Initialize 2 Qubits
    solver = UETQuantumSolver(num_qubits=2)

    # 2. Create Bell State
    print("  [1] Applying Hadamard on Qubit 0...")
    solver.apply_hadamard(target=0)

    print("  [2] Applying CNOT (Control 0, Target 1)...")
    solver.apply_cnot(control=0, target=1)

    # 3. Check Probabilities
    probs = np.abs(solver.state) ** 2
    p00 = probs[0]  # |00>
    p11 = probs[3]  # |11> (Index 3 is 11 binary)

    print(f"\n  [3] State Analysis")
    print(f"      P(|00>): {p00:.4f}")
    print(f"      P(|11>): {p11:.4f}")

    if abs(p00 - 0.5) < 0.001 and abs(p11 - 0.5) < 0.001:
        print("      ✅ Superposition Confirmed")
    else:
        print("      ❌ Superposition Failed")

    # 4. Check Entropy (Entanglement)
    entropy = solver.calculate_entropy(subsystem_size=1)
    print(f"\n  [4] Entanglement Entropy (Von Neumann)")
    print(f"      S_vn:    {entropy:.5f} bits")
    print(f"      Target:  1.00000 bits")

    if abs(entropy - 1.0) < 0.001:
        print("\n✅ STATUS: SUCCESS (Maximal Entanglement Verified)")
        print("   The UET Tensor Engine correctly models Non-Local Correlations.")
    else:
        print("\n❌ STATUS: FAILED (Entanglement missing)")


if __name__ == "__main__":
    run_verification()
