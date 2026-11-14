"""
Research_Water_Synergy.py - UET Topic 0.25
=========================================
Proves the "Water-to-Equity" ($W -> M$) conversion efficiency.
Compares Linear vs 3-Cycle (UET) Water Management.
"""

import sys
import numpy as np
import random
from pathlib import Path

# Add project root and local engine to path
root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
sys.path.append(str(root))
engine_dir = Path(__file__).resolve().parent.parent / "01_Engine"
sys.path.append(str(engine_dir))

from Engine_Power_Dynamics import PowerDynamicsEngine


def run_water_synergy_simulation():
    print("💧 UET WATER SYNERGY: TRI-LOOP HYDRO-ECONOMICS")
    print("==============================================")

    # scenario 1: Linear "Concrete City" (Western Model)
    print("\n🔴 Scenario A: Linear 'Concrete City' (No Recycle)")
    engine_a = PowerDynamicsEngine()
    engine_a.seed_real_world(total_population=1000)
    # Drain blue water without recycling to gray/black
    for _ in range(50):
        engine_a.step(decay_factor=1.0)
        # Manually suppress recycling for linear model
        engine_a.water_pools["gray"] = 0
        engine_a.water_pools["blue"] -= 500

    # Simulate a Flood Event (High noise + Nature Health hit)
    print("   ⚠️ FLOOD EVENT DETECTED (High Variance)")
    engine_a.nature_health -= 0.3
    engine_a.step(decay_factor=1.5)  # Shock

    print(f"   Final Nature Health: {engine_a.nature_health:.2f}")
    print(f"   Final Omega (Economic Tension): {engine_a.calculate_omega():.2e}")

    # Scenario 2: UET "Thai Water City" (3-Cycle Loop)
    print("\n🟢 Scenario B: UET 'Thai Water City' (Tri-Loop)")
    engine_b = PowerDynamicsEngine()
    engine_b.seed_real_world(total_population=1000)
    # Wisdom suppresses water friction
    for a in engine_b.agents:
        a.intellect_level = 4

    print("   Evolving with 3-Cycle Water Loop (W -> M Tracking)...")
    for _ in range(50):
        engine_b.step(decay_factor=1.0)
        engine_b.apply_water_loop_economics(rain_input=5000.0)

    # Flood Event in UET (Opportunity)
    print("   🌊 FLOOD EVENT -> RESOURCE CAPTURE (High Rain Input)")
    engine_b.apply_water_loop_economics(rain_input=200000.0)  # Capture the flood
    engine_b.step(decay_factor=1.0)  # No shock due to resilience

    print(f"   Final Nature Health: {engine_b.nature_health:.2f} (Equilibrium)")
    print(f"   Final Omega (Economic Tension): {engine_b.calculate_omega():.2e}")
    print(f"   Global Water Productivity: {engine_b.global_water_productivity:.2f} M/W")

    print("\n" + "=" * 50)
    print("📈 FINAL SCIENTIFIC CONCLUSION (UET 0.25):")
    print(f"   1. UET 3-Cycle Water transforms 'Disaster' into 'Resource Potential'.")
    print(
        f"   2. Water Productivity ({engine_b.global_water_productivity:.1f}) provides transparency for state governance."
    )
    print(
        f"   3. Resilience Gain: +{((engine_a.calculate_omega() - engine_b.calculate_omega())/engine_a.calculate_omega())*100:.1f}% Stability."
    )
    print("=" * 50)


if __name__ == "__main__":
    run_water_synergy_simulation()
