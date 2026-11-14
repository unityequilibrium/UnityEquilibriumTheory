import os
import sys

# Link to Engine
script_dir = os.path.dirname(os.path.abspath(__file__))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
if engine_dir not in sys.path:
    sys.path.append(engine_dir)

from Engine_Mycelial_Network import MycelialNetwork, BioEntity


def run_simulation():
    print("\n🌳 EXPERIMENT: Natural Forest vs. UET Urban Ecosystem")
    print("=====================================================")

    # 1. Setup Environments
    years = 15

    # A. Wild Forest (Control)
    wild_tree = BioEntity("TREE", age=0)

    # B. UET Ecosystem (Test)
    uet_network = MycelialNetwork(transfer_efficiency=0.9)
    uet_tree = BioEntity("TREE", age=0)
    waste_station = BioEntity("WASTE_STATION")

    uet_network.add_node(uet_tree)
    uet_network.add_node(waste_station)

    # Concrete Threshold (from previous experiment)
    concrete_threshold_N = 436000  # Strength at Year 9

    print(
        f"\n{'Year':<5} | {'Wild Biomass':<15} | {'UET Biomass':<15} | {'Diff (x)':<10} | {'Status'}"
    )
    print("-" * 75)

    crossing_year_uet = None
    crossing_year_wild = None

    for year in range(1, years + 1):
        # --- Simulate Wild ---
        wild_tree.grow_natural(genetic_factor=1.0)

        # --- Simulate UET ---
        # 1. Human Waste Input (Trash -> Nutrients)
        waste_station.waste_input = 2000  # High nutrient load from city trash
        # 2. Mycelial Transfer
        uet_network.distribute_nutrients()
        # 3. Genetic Growth
        uet_tree.grow_natural(genetic_factor=1.3)  # 30% GMO boost

        # Calculate Strength (Approximation: Strength ~ Biomass * 5000)
        wild_strength = wild_tree.biomass * 5000
        uet_strength = uet_tree.biomass * 5000

        ratio = uet_strength / wild_strength

        marker = ""
        if uet_strength > concrete_threshold_N:
            marker = "✅ UET READY"
            if crossing_year_uet is None:
                crossing_year_uet = year

        if wild_strength > concrete_threshold_N:
            if crossing_year_wild is None:
                crossing_year_wild = year

        print(
            f"{year:<5} | {wild_tree.biomass:<15.1f} | {uet_tree.biomass:<15.1f} | {ratio:<10.1f} | {marker}"
        )

    print("-" * 75)
    print(f"\n🚀 RESULTS:")
    print(f"Wild Tree Crossing Point: Year {crossing_year_wild if crossing_year_wild else '> 15'}")
    print(f"UET Tree Crossing Point:  Year {crossing_year_uet}")

    if crossing_year_uet and crossing_year_uet <= 5:
        print("\n🏆 MISSION ACCOMPLISHED: The 'Fast-Growth' strategy works.")
        print("We can replace concrete in < 5 Years using Waste+Fungi+GMO.")
    else:
        print("\n⚠️  Too Slow: Need more nutrients or better genetics.")


if __name__ == "__main__":
    run_simulation()
