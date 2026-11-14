import numpy as np
import json
import os
from datetime import datetime

"""
🔬 RESEARCH: Scenario Simulation - Debris Storm Response
Topic: 0.31_SpaceTime_Propulsion
Scenario: Massive Space Debris Influx (Total Solar System Stress Test)

This simulation models:
1. Debris Influx: 1,000,000 fragments entering at 50 km/s.
2. Industrial Stingray Swarm: Interception and recycling efficiency.
3. GCR Resilience: Integrity recovery over time.
4. Bio-Ring Integrity: Impact on Oxygen Domain.
"""

class DebrisStormScenario:
    def __init__(self):
        self.debris_count = 1000000.0
        self.stingray_fleet_size = 5000 # Number of Industrial Stingrays active
        self.gcr_base_integrity = 1.0
        self.bio_ring_baseline_o2 = 787500.0 # units/hr (from Res_Oxygen_Production)
        
    def simulate_storm(self):
        # 1. Interception
        # Capture efficiency depends on fleet size vs debris count
        capture_capacity = self.stingray_fleet_size * 150 # Each stingray captures 150 fragments/hr
        captured = min(self.debris_count, capture_capacity)
        remaining = self.debris_count - captured
        
        # 2. Damage from Remaining Debris
        # Each fragment reduces GCR integrity by a small factor
        damage = (remaining / 1000000.0) * 0.4 # Max 40% damage if all fragments hit
        integrity_post_storm = self.gcr_base_integrity - damage
        
        # 3. Recovery (Self-Healing)
        # GCR heals at 5% per hour
        integrity_final = min(1.0, integrity_post_storm + 0.1) # 2 hours of recovery
        
        # 4. Impact on Oxygen (Bio-Forest Damage)
        o2_loss_pct = damage * 1.2 # Bio-rings are more fragile than rails
        o2_output_final = self.bio_ring_baseline_o2 * (1.0 - o2_loss_pct)
        
        return {
            "captured_fragments": captured,
            "evaded_fragments": remaining,
            "gcr_integrity_post_impact": integrity_post_storm,
            "gcr_integrity_after_recovery": integrity_final,
            "o2_production_impacted": o2_output_final,
            "o2_production_loss_pct": o2_loss_pct * 100
        }

    def run(self):
        storm_results = self.simulate_storm()
        
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "scenario": "Massive Debris Storm",
                "severity": "High (1M fragments)"
            },
            "system_response": storm_results,
            "conclusion": "System CRITICAL" if storm_results["gcr_integrity_post_impact"] < 0.5 else "System RESILIENT"
        }
        return results

if __name__ == "__main__":
    scenario = DebrisStormScenario()
    output_data = scenario.run()

    base_path = r"c:\Users\santa\Desktop\uet_harness\docs\topics\0.31_SpaceTime_Propulsion"
    result_path = os.path.join(base_path, "Result", "03_show_Result")
    os.makedirs(result_path, exist_ok=True)

    filename = "Res_Scenario_Debris.json"
    with open(os.path.join(result_path, filename), "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Crisis Scenario Simulation Complete.")
    res = output_data['system_response']
    print(f"🧹 Intercepted: {res['captured_fragments']:.0f} units.")
    print(f"🛡️ Final GCR Integrity: {res['gcr_integrity_after_recovery']:.2f}")
    print(f"🌬️ Oxygen Loss: {res['o2_production_loss_pct']:.1f}%")
    print(f"🏁 Conclusion: {output_data['conclusion']}")
