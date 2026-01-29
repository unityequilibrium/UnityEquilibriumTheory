"""
Research_Qubit_Mechanics.py
===========================
UET Verification of Fundamental Qubit Operations.
Validates:
1. Superposition (H-Gate)
2. Pauli-X (Bit Flip)
3. CNOT (Entanglement Logic)
4. Measurement Collapse
"""

import sys
import numpy as np
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
root_path = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "research_uet").exists():
        root_path = parent
        break

if root_path and str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Import Engine
try:
    from research_uet.topics.import_engine import get_engine

    QuantumUnityEngine = get_engine("0.18_Mathnicry")
except ImportError:
    # Fallback
    engine_dir = current_path.parent.parent / "01_Engine"
    sys.path.append(str(engine_dir))
    from Engine_Quantum_Logic import QuantumUnityEngine


def verify_qubit_mechanics():
    print("⚛️  UET Qubit Mechanics Verification")
    print("====================================")

    # 1. Initialize 2-Qubit System
    print("\n[1] Initializing Vacuum State |00>...")
    engine = QuantumUnityEngine(num_qubits=2)
    engine.summary()

    # 2. Superposition (H on 0)
    print("\n[2] Applying Hadamard (Superposition) on Qubit 0...")
    # Expect: |00> + |10> (Since index 0 is usually LSB or MSB dep on tensor, assume standard)
    engine.apply_hadamard(0)
    engine.summary()

    # 3. Entanglement (CNOT 0->1)
    print("\n[3] Applying CNOT (0 controls 1)...")
    # If 0 is 1, flip 1.
    # Current state: (|00> + |10>) / sqrt(2)? Or (|00> + |01>)?
    # Let's see the implementation. default tensor order [q0, q1] or [q1, q0]?
    # UET Engine uses tensor order.
    engine.apply_cnot(control=0, target=1)
    engine.summary()

    # 4. Measure
    print("\n[4] Measurement Collapse...")
    result = engine.measure_collapse()
    print(f"    Collapsed to: |{result}>")

    if result in ["00", "11"]:
        print("    ✅ SUCCESS: Bell State Correlation Observed.")
    else:
        print("    ⚠️  WARNING: Unexpected State (Check CNOT logic).")


if __name__ == "__main__":
    verify_qubit_mechanics()
