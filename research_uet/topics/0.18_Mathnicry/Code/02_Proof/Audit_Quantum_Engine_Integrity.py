"""
Audit_Quantum_Engine_Integrity.py - UET Topic 0.18
==================================================
Strict audit using UET Glass Box and Bug Hunter.
Checks if the Quantum Engine maintains "Truth" (G0-G4 Gates).
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

root = ROOT  # Alias for legacy code compatibility

# Engine Import
engine_dir = current_path.parent.parent / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

from research_uet.core.uet_glass_box import UETMetricLogger
from research_uet.core.uet_bug_hunter import UETBugHunter
from Engine_Quantum_Logic import QuantumUnityEngine


def run_glass_box_audit():
    print(f"🛡️ Starting UET Glass Box Audit for Quantum Computing (Topic 0.18)")
    print(f"  Root: {root}")

    # 1. Setup Logger & Hunter
    # Important: Point output to the standard Topic Result folder
    logger = UETMetricLogger(
        simulation_name="Quantum_Integrity_Audit",
        output_dir=str(
            Path(__file__).resolve().parent.parent.parent / "Result" / "02_Proof"
        ),
        flat_mode=True,
    )
    hunter = UETBugHunter(topic="0.18_Quantum")

    # 2. Initialize Engine with Logger
    num_qubits = 10
    engine = QuantumUnityEngine(num_qubits=num_qubits, logger=logger)

    print(f"  Initialized {num_qubits}-Qubit Engine.")

    # 3. Execute Operations with Monitoring
    # Phase 1: High-Energy Superposition
    print("  Executing Phase 1: Superposition (H-Gates)...")
    for i in range(num_qubits):
        engine.apply_hadamard(i)

        # Calculate Unity Omega (Total field resonance)
        # For a normalized Wavefunction, sum(probs) = 1.0 (The True Equilibrium)
        omega = float(np.sum(np.abs(engine.state) ** 2))

        # Log to Glass Box
        logger.log_step(step=i, time_val=float(i), omega=omega, field_c=engine.state)

        # Audit with Bug Hunter
        failures = hunter.audit_step({"omega": omega})
        if failures:
            print(f"  ⚠️ integrity Warning at Step {i}: {failures}")

    # Phase 2: Entanglement (CNOT Gates)
    print("  Executing Phase 2: Entanglement (CNOT-Gates)...")
    for i in range(num_qubits - 1):
        engine.apply_cnot(i, i + 1)
        omega = float(np.sum(np.abs(engine.state) ** 2))
        logger.log_step(
            step=num_qubits + i,
            time_val=float(num_qubits + i),
            omega=omega,
            field_c=engine.state,
        )

    # Phase 3: P vs NP Scaling Logic (Search)
    print("  Executing Phase 3: Resonance Search (Oracle + Diffuser)...")
    target_idx = 42
    # Oracle
    engine.state[target_idx] *= -1
    # Diffuser
    mean_amp = np.mean(engine.state)
    engine.state = 2 * mean_amp - engine.state

    omega = float(np.sum(np.abs(engine.state) ** 2))
    logger.log_step(step=20, time_val=20.0, omega=omega, field_c=engine.state)

    # 4. Final Report
    print("\n--- Audit Summary ---")
    report_path = logger.save_report()
    integrity_summary = hunter.generate_final_report(logger.step_count, 0)
    print(f"  Integrity: {integrity_summary}")
    print(f"  Glass Box Ledger: {report_path}")


if __name__ == "__main__":
    run_glass_box_audit()
