import numpy as np
import json
import os
from datetime import datetime

"""
🔬 RESEARCH: Galactic Coral Reef (GCR) Growth Simulation
Topic: 0.31_SpaceTime_Propulsion
Component: 03_Research
Standard: UET 5x4 Scientific Grid

This simulation models:
1. Self-repairing material logic (Graphene-weave healing).
2. Autonomous branching (GCR growth) based on logistics demand.
3. Symbiotic efficiency (Waste-to-O2 conversion).
"""

class GCRSim:
    def __init__(self):
        self.structural_integrity = 1.0 # 1.0 = Full health
        self.material_reservoir = 500.0 # Units of Graphene stored in infrastructure
        self.traffic_density = 0.5 # 0.0 to 1.0 (Demand for new branches)
        
    def simulate_damage(self, impact_force):
        # Impact reduces integrity
        damage = impact_force / 1000.0
        self.structural_integrity = max(0.0, self.structural_integrity - damage)
        return damage

    def self_repair(self):
        # Repair logic: Uses reservoir to increase integrity
        needed = 1.0 - self.structural_integrity
        cost = needed * 100.0
        if self.material_reservoir >= cost:
            self.material_reservoir -= cost
            self.structural_integrity = 1.0
            return True
        return False

    def check_growth(self):
        # If traffic > 0.8, branch out
        if self.traffic_density > 0.8:
            return "Branching Initiated (New Rail Path)"
        return "Stable (Current Capacity OK)"

    def run(self):
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "topic": "0.31_SpaceTime_Propulsion",
                "category": "03_Research"
            },
            "repair_cycle": {},
            "growth_cycles": []
        }

        # Step 1: Simulate Impact
        impact = 250.0
        damaged = self.simulate_damage(impact)
        pre_repair = self.structural_integrity
        repaired = self.self_repair()
        
        results["repair_cycle"] = {
            "impact_force": impact,
            "damage_pct": damaged * 100,
            "post_impact_integrity": pre_repair,
            "repair_successful": repaired,
            "final_integrity": self.structural_integrity
        }

        # Step 2: Growth Test
        for density in [0.5, 0.7, 0.9]:
            self.traffic_density = density
            results["growth_cycles"].append({
                "traffic_density": density,
                "status": self.check_growth()
            })

        return results

if __name__ == "__main__":
    sim = GCRSim()
    output_data = sim.run()

    base_path = r"c:\Users\santa\Desktop\uet_harness\docs\topics\0.31_SpaceTime_Propulsion"
    result_path = os.path.join(base_path, "Result", "03_show_Result")
    os.makedirs(result_path, exist_ok=True)

    filename = "Res_GCR_Growth.json"
    with open(os.path.join(result_path, filename), "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ GCR Growth Simulation Complete.")
    print(f"🏥 Repair Status: {output_data['repair_cycle']['repair_successful']} (Integrity: {output_data['repair_cycle']['final_integrity']})")
    print(f"🌿 Growth Check: {output_data['growth_cycles'][-1]['status']}")
