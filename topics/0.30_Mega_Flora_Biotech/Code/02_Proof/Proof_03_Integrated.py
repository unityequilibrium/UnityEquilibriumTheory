import os
import sys

import json

# Link to Engine
script_dir = os.path.dirname(os.path.abspath(__file__))
result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
sys.path.append(engine_dir)

if not os.path.exists(result_dir):
    os.makedirs(result_dir)

from Engine_Full_Ecosystem_Integration import YggdrasilEcoAdapter, MycelialNetwork
from Engine_Mycelial_Network import BioEntity  # Waste Station


def run_integrated_proof():
    log_file = os.path.join(result_dir, "Res_Integrated_Loop.txt")
    with open(log_file, "w", encoding="utf-8") as f:

        def log_print(msg):
            print(msg)
            f.write(str(msg) + "\n")

        log_print("\n🌳 UET PROOF 03: THE COMPLETE YGGDRASIL ECOSYSTEM")
        log_print("=================================================")
        log_print("Objective: Speed + Stability (Adaptive Growth with Infinite Food)")

        # 1. Setup
        years = 20
        network = MycelialNetwork(transfer_efficiency=0.9)

        # The Star: Adapted Yggdrasil
        yggdrasil = YggdrasilEcoAdapter(growth_rate=1.2)
        network.add_node(yggdrasil)

        # The Support: Waste Station
        waste_station = BioEntity("WASTE_STATION")
        network.add_node(waste_station)

        # Concrete Threshold
        concrete_start = 500000.0

        log_print(
            f"\n{'Year':<5} | {'Height (m)':<12} | {'Girth (cm)':<12} | {'Stress %':<10} | {'Strength (N)':<15} | {'Status'}"
        )
        log_print("-" * 85)

        crossing_year = None

        for year in range(1, years + 1):
            # A. Feed the System (City Waste)
            waste_station.waste_input = 2000  # Massive input

            # B. Network Transfer (The "Cheat")
            network.distribute_nutrients()

            # C. Tree Growth (The "Balance")
            # The tree now has massive 'biomass_kg' from the network
            # It must decide how to use it (Height vs Girth)
            stats = yggdrasil.grow_one_year(year)

            # D. Concrete Decay
            concrete_current = concrete_start * ((1 - 0.015) ** year)

            # E. Comparison
            strength_n = stats["integrity_score"]
            status = "Grow..."
            if strength_n > concrete_current:
                status = "✅ STRONGER"
                if crossing_year is None:
                    crossing_year = year

            log_print(
                f"{year:<5} | {stats['height_m']:<12} | {stats['diameter_cm']:<12} | {stats['stress_ratio']:<10} | {strength_n:,.0f}{'':<10} | {status}"
            )

        log_print("-" * 85)
        log_print(f"Final Crossing Point: Year {crossing_year}")

        if crossing_year and crossing_year <= 5:
            log_print("\n🏆 VERDICT: PERFECT SYNERGY.")
            log_print("The Tree used the extra food to grow THICK fast (Stress Control).")
            log_print("It overtook Concrete in < 5 Years while staying Stable.")
        else:
            log_print("\n⚠️ VERDICT: Fast but maybe Unstable?")


if __name__ == "__main__":
    run_integrated_proof()
