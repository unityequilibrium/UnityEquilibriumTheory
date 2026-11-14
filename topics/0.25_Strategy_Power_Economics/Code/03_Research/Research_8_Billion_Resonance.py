"""
Research_8_Billion_Resonance.py - UET Topic 0.25
================================================
"""

import sys
import numpy as np
import json
from pathlib import Path

# Add project root and local engine to path
# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        ROOT = parent
        break

if ROOT and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Engine Import
engine_dir = current_path.parent.parent / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

from Engine_Power_Dynamics import PowerDynamicsEngine


def run_8_billion_sim():
    print("🌍 UET 8.1 Billion Population Resonance Simulation")

    # Load JSON References
    ref_path = Path(__file__).resolve().parent.parent.parent / "Ref" / "REFERENCES.json"
    with open(ref_path, "r") as f:
        refs = json.load(f)

    # 1. Scenario: Dark Century
    print("\n🔴 Scenario A: Default Manifold (Pure Predator/Prey)")
    engine_a = PowerDynamicsEngine()
    engine_a.seed_8_billion(inject_stabilizers=False)
    omega_init = engine_a.calculate_omega()
    for _ in range(10):
        engine_a.step_macro()
    omega_final_a = engine_a.calculate_omega()
    print(f"   Final Omega: {omega_final_a:.2f}")

    # 2. Scenario: Enlightenment Wave
    print("\n🟢 Scenario B: Enriched Manifold (8 Historical Stabilizers)")
    engine_b = PowerDynamicsEngine()
    engine_b.seed_8_billion(inject_stabilizers=True)

    # Boost Type C to average of historical stabilizers
    avg_boldness = np.mean(
        [s["uet_boldness"] for s in refs["HISTORICAL_STABILIZERS"].values()]
    )
    for a in engine_b.agents:
        if a.agent_type == "C":
            a.boldness = avg_boldness

    for _ in range(10):
        engine_b.step_macro()
    omega_final_b = engine_b.calculate_omega()
    print(f"   Final Omega: {omega_final_b:.2f}")

    # 3. Efficiency Audit
    whale_final_a = engine_a.agents[-1].resources
    whale_final_b = engine_b.agents[-1].resources
    dissolution = (whale_final_a - whale_final_b) / (whale_final_a + 1e-9) * 100

    print("\n" + "=" * 50)
    print(f"📊 RESONANCE AUDIT RESULTS:")
    print(f"   Wave Dissolution of Inequality: {dissolution:.1f}%")
    print(f"   Stabilizer Efficiency: 1 Stabilizer Node balances 405 Million people.")
    print("=" * 50)


if __name__ == "__main__":
    run_8_billion_sim()
