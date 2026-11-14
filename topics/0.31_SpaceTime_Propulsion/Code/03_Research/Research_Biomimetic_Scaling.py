import numpy as np
import json
import os
from datetime import datetime

"""
🔬 RESEARCH: Biomimetic Scaling (Humpback Tubercle Gain)
Topic: 0.31_SpaceTime_Propulsion
Component: 03_Research
Standard: UET 5x4 Scientific Grid

This simulation compares:
1. Smooth Hull (Classical Aerospace)
2. Tubercle-Enhanced Hull (Whale-inspired) 
To show how "Bumpy" hulls improve lift/propulsion in Information Fluid.
"""

class BiomimeticSim:
    def __init__(self):
        self.phi_max = 1.0  # Coherence Flux
        self.viscosity_manifold = 0.05
        self.angles_of_attack = np.linspace(0, 30, 10)

    def calculate_efficiency(self, angle, tubercle_active=False):
        # Tubercle Effect: Maintains lift at higher angles of attack.
        # Classical: Stalls at 15 degrees.
        # Tubercle: Delays stall and creates vortex stabilization.
        
        stall_angle = 15.0 if not tubercle_active else 25.0
        base_lift = np.cos(np.deg2rad(angle)) * (1.0 if angle < stall_angle else 0.2)
        
        # UET Vortex Gain (Axiom 3)
        vortex_bonus = 0.15 * np.sin(np.deg2rad(angle)) if tubercle_active else 0.0
        
        efficiency = base_lift + vortex_bonus
        return efficiency

    def run(self):
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "topic": "0.31_SpaceTime_Propulsion",
                "category": "03_Research"
            },
            "scaling_test": []
        }

        for angle in self.angles_of_attack:
            eff_smooth = self.calculate_efficiency(angle, tubercle_active=False)
            eff_whale = self.calculate_efficiency(angle, tubercle_active=True)
            
            results["scaling_test"].append({
                "angle_degrees": float(angle),
                "efficiency_smooth": float(eff_smooth),
                "efficiency_whale": float(eff_whale),
                "gain_pct": float((eff_whale/eff_smooth - 1) * 100 if eff_smooth > 0 else 0)
            })

        return results

if __name__ == "__main__":
    sim = BiomimeticSim()
    output_data = sim.run()

    base_path = r"c:\Users\santa\Desktop\uet_harness\docs\topics\0.31_SpaceTime_Propulsion"
    result_path = os.path.join(base_path, "Result", "03_show_Result")
    os.makedirs(result_path, exist_ok=True)

    filename = "Res_Biomimetic_Scaling.json"
    with open(os.path.join(result_path, filename), "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Biomimetic Scaling Complete. Results saved to: {result_path}")
    print(f"🐋 Humpback Effect: Efficiency Gain at high angle = {output_data['scaling_test'][-1]['gain_pct']:.1f}%")
