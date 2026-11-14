import json
import os
from datetime import datetime

"""
🔬 RESEARCH: Galactic Resource Ledger (GRL)
Topic: 0.31_SpaceTime_Propulsion
Component: 03_Research
Standard: UET 5x4 Scientific Grid

This simulation models the flow of "Imported Entropy" (Resources) 
from external solar systems to the Universal Ports.
"""

class GalacticLedger:
    def __init__(self):
        self.systems = {
            "Trappist-1": {"resource": "Plasma", "entropy_gain": 5000, "status": "Mining"},
            "Proxima-B": {"resource": "Graphene-Ore", "entropy_gain": 12000, "status": "Mining"},
            "Home-Solar": {"resource": "Biologicals", "entropy_gain": 0, "status": "Protected"}
        }
        self.port_efficiency = 0.98

    def process_trade(self):
        total_import = 0
        log = []
        
        for name, data in self.systems.items():
            if data["status"] == "Mining":
                received = data["entropy_gain"] * self.port_efficiency
                total_import += received
                log.append({
                    "origin": name,
                    "target": "Universal-Port-Alpha",
                    "resource": data["resource"],
                    "amount_units": received,
                    "loss_pct": (1 - self.port_efficiency) * 100
                })
        
        return total_import, log

    def run(self):
        total, trade_log = self.process_trade()
        
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "topic": "0.31_SpaceTime_Propulsion",
                "category": "03_Research"
            },
            "ledger_summary": {
                "total_imported_energy_units": total,
                "home_system_drain": 0.0,  # Eco-Ethics Goal
                "trade_events": trade_log
            }
        }
        return results

if __name__ == "__main__":
    ledger = GalacticLedger()
    output_data = ledger.run()

    base_path = r"c:\Users\santa\Desktop\uet_harness\docs\topics\0.31_SpaceTime_Propulsion"
    result_path = os.path.join(base_path, "Result", "03_show_Result")
    os.makedirs(result_path, exist_ok=True)

    filename = "Res_Galactic_Ledger.json"
    with open(os.path.join(result_path, filename), "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"✅ Galactic Ledger Updated. Total Imports: {output_data['ledger_summary']['total_imported_energy_units']} units.")
    print(f"🌍 Eco-Status: Home Solar System drain is 0.0%. System is SAFE.")
