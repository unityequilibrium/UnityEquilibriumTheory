"""
Proof_Social_Stability.py - UET Topic 0.25
==========================================
Refined Proof: Compares inequality (Omega) evolution.
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
import random
from pathlib import Path

# Fix depth for docs
root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.append(str(root))
engine_dir = Path(__file__).resolve().parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

from docs.core.uet_glass_box import UETMetricLogger
from Engine_Power_Dynamics import PowerDynamicsEngine, StrategicAgent


def run_stability_comparison():
    print("⚖️ UET Stability Proof (Refined): Predator/Prey Dynamics")

    # World 1: Inequality (Predators vs Prey)
    print("\n🌍 World 1: The Predator World (Type D + Type A)")
    logger_d = UETMetricLogger("Social_Stability", topic_id="0.25", category="log")
    engine_d = PowerDynamicsEngine(nx=100, logger=logger_d)
    engine_d.seed_real_world()  # Properly populates self.agents[100]
    # Reset to flat baseline for controlled proof
    engine_d.C = np.ones((1, 100))
    engine_d.sync_from_field()

    for i in range(100):
        t = "D" if i < 20 else "A"  # 20 Predators
        p = engine_d.TYPE_PROFILES[t]
        engine_d.agents[i].agent_type = t
        engine_d.agents[i].boldness = p["boldness"]
        engine_d.agents[i].resources = 1.0

    for _ in range(50):
        engine_d.step()
    omega_final_d = engine_d.calculate_omega()
    logger_d.save_report()

    # World 2: Stability (Stabilizers vs Prey)
    print("\n🌍 World 2: The Stabilizer World (Type C + Type A)")
    logger_c = UETMetricLogger(
        simulation_name="World_Stabilizer",
        topic_id="0.25",
        category="log",
        flat_mode=True,
    )
    engine_c = PowerDynamicsEngine(nx=100, logger=logger_c)
    engine_c.seed_real_world()
    engine_c.C = np.ones((1, 100))
    engine_c.sync_from_field()

    for i in range(100):
        t = "C" if i < 20 else "A"  # 20 Stabilizers
        p = engine_c.TYPE_PROFILES[t]
        engine_c.agents[i].agent_type = t
        engine_c.agents[i].boldness = p["boldness"]
        engine_c.agents[i].resources = 1.0

    for _ in range(50):
        engine_c.step()
    omega_final_c = engine_c.calculate_omega()
    logger_c.save_report()

    print("\n" + "=" * 40)
    print(f"📊 Predator World Omega (Inequality): {omega_final_d:.4f}")
    print(f"📊 Stabilizer World Omega (Stability): {omega_final_c:.4f}")

    if omega_final_c < omega_final_d:
        print(
            "\n✅ PROOF SUCCESS: Type C agents effectively redistribute tension to minimize Omega."
        )
        print(
            "💡 UET Insight: Inequality is a high-cost manifold distortion. Altruism is a physical optimizer."
        )
    else:
        print("\n❌ PROOF FAILURE: Check boldness/selfishness parameters.")


if __name__ == "__main__":
    run_stability_comparison()
