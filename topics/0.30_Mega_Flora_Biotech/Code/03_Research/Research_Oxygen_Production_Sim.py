import json
import os
from datetime import datetime

"""
🔬 RESEARCH: Solar Oxygen Production Scaling
Topic: 0.31_SpaceTime_Propulsion (Integration with 0.30)
Component: 03_Research
Standard: UET 5x4 Scientific Grid

This simulation models:
1. Oxygen output of Mega Flora Bio-Rings.
2. Acceleration gain from Acoustic Metabolic Hacking.
3. CO2 -> O2 conversion efficiency in a closed galactic loop.
"""

class OxygenSim:
    def __init__(self):
        # Constants from Topic 0.30 and 0.31
        self.o2_production_baseline = 100.0  # units/km^3/hr
        self.metabolic_hacking_gain = 0.575 # +57.5% from acoustic resonance
        self.industrial_co2_output = 50000.0 # units/hr (Aggregated solar-industrial output)
        
        # Scaling Parameters
        self.ring_segment_km = 1000.0 # Length of a standard Bio-Ring segment

    def calculate_production(self, segments):
        total_vol = segments * 10.0 # 10 km^3 per segment cross-section
        baseline_o2 = total_vol * self.o2_production_baseline
        boosted_o2 = baseline_o2 * (1.0 + self.metabolic_hacking_gain)
        return boosted_o2

    def run(self):
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "topic": "0.31_SpaceTime_Propulsion",
                "category": "03_Research"
            },
            "production_scaling": []
        }

        # Scale from 1 to 100 segments
        for seg in [1, 10, 50, 100, 500]:
            total_o2 = self.calculate_production(seg)
            net_balance = total_o2 - self.industrial_co2_output
            
            results["production_scaling"].append({
                "segments": seg,
                "total_km": seg * self.ring_segment_km,
                "o2_units_hr": total_o2,
                "net_carbon_balance_hr": net_balance,
                "sustainability_status": "Positive" if net_balance > 0 else "Negative"
            })

        return results

if __name__ == "__main__":
    sim = OxygenSim()
    output_data = sim.run()

    base_path = r"c:\Users\santa\Desktop\uet_harness\docs\topics\0.31_SpaceTime_Propulsion"
    result_path = os.path.join(base_path, "Result", "03_show_Result")
    os.makedirs(result_path, exist_ok=True)

    filename = "Res_Oxygen_Production.json"
    with open(os.path.join(result_path, filename), "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Oxygen Scaling Simulation Complete.")
    latest = output_data['production_scaling'][-1]
    print(f"🌬️ 500k km Bio-Ring produces {latest['o2_units_hr']:.1f} units of O2/hr.")
    print(f"🌏 Net Balance: {latest['net_carbon_balance_hr']:.1f} (Industrial Surplus). Status: {latest['sustainability_status']}")
