"""
Proof_Bell_State_Fidelity.py - UET Topic 0.18
=============================================
Verifies the creation of a Bell State (|00> + |11>) using
the QuantumUnityEngine.
Calculates the statistical fidelity over 1000 measurements.
"""

import sys
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

# Engine Path
engine_path = current_path.parents[1] / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from Engine_Quantum_Logic import QuantumUnityEngine


def verify_bell_state(samples=1000):
    print(f"🔬 Verifying Bell State Fidelity ({samples} samples)...")

    # 3. Measure (Correct Physics: Re-prepare state for each shot)
    results = []

    print("   [Running 1000 Independent Trials...]")
    for _ in range(samples):
        # A. Initialize Fresh Engine (Reset Unity Field)
        engine = QuantumUnityEngine(num_qubits=2)

        # B. Apply Hadamard to Qubit 0
        engine.apply_hadamard(0)

        # C. Apply CNOT (Control: 0, Target: 1)
        engine.apply_cnot(0, 1)

        # D. Measure & Collapse
        results.append(tuple(map(int, list(engine.measure_collapse()))))

    # Analyze
    counts = {(0, 0): 0, (0, 1): 0, (1, 0): 0, (1, 1): 0}
    for r in results:
        counts[r] += 1

    # Ideal Bell State: 50% |00>, 50% |11>
    fidelity = (counts[(0, 0)] + counts[(1, 1)]) / samples

    print("\n--- Measurement Statistics ---")
    print(f" |00>: {counts[(0,0)]} ({counts[(0,0)]/samples*100:.1f}%)")
    print(f" |11>: {counts[(1,1)]} ({counts[(1,1)]/samples*100:.1f}%)")
    print(f" Errors (|01>, |10>): {counts[(0,1)] + counts[(1,0)]}")
    print(f" Final Fidelity: {fidelity:.4f}")

    # Save Results
    import json

    result_data = {
        "Topic": "0.18_Quantum_Computing",
        "Category": "02_Proof",
        "Test": "Bell_State_Fidelity",
        "Samples": samples,
        "Counts": {str(k): v for k, v in counts.items()},
        "Fidelity": fidelity,
        "Status": "PASS" if fidelity > 0.95 else "FAIL",
    }

    output_path = (
        Path(__file__).parent.parent.parent
        / "Result"
        / "02_Proof"
        / "02_Proof_Bell_State_Stats.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result_data, f, indent=4)
    print(f"📁 Result saved to: {output_path.name}")

    if fidelity > 0.95:
        print("\n✅ SUCCESS: Quantum Unity Fidelity Verified!")
    else:
        print("\n❌ FAILURE: Fidelity too low.")


if __name__ == "__main__":
    verify_bell_state()
