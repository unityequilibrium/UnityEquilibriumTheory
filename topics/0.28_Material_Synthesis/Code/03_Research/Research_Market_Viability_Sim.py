import numpy as np


def calculate_market_viability():
    """
    Calculates the cost comparison between UET Perovskite and Traditional Rare-Earth Displays.
    """
    # Parameters for 1 Million Units (Price Tags)
    units = 1_000_000
    area_per_unit_sqm = 0.01  # 10cm x 10cm tag

    # Traditional (OLED/LCD using Rare Earths)
    rare_earth_cost_per_sqm = 80.0
    rare_earth_energy_kwh_per_sqm = 50.0  # High heat, Vacuum

    # UET (Perovskite LARP + Waste Graphene)
    uet_material_cost_per_sqm = 3.0  # Graphene from waste = nearly free
    uet_energy_kwh_per_sqm = 2.0  # Room Temp, No Vacuum

    electricity_price = 0.15  # $/kWh

    total_rare_earth = (
        units
        * area_per_unit_sqm
        * (rare_earth_cost_per_sqm + (rare_earth_energy_kwh_per_sqm * electricity_price))
    )
    total_uet = (
        units
        * area_per_unit_sqm
        * (uet_material_cost_per_sqm + (uet_energy_kwh_per_sqm * electricity_price))
    )

    saving_ratio = (total_rare_earth - total_uet) / total_rare_earth * 100

    print("\n📊 SCALE ANALYSIS: 1 Million Electronic Price Tags")
    print("===============================================")
    print(f"Traditional (Rare-Earth): ${total_rare_earth:,.2f}")
    print(f"UET (Smart Surface)   : ${total_uet:,.2f}")
    print(f"Total Savings         : ${total_rare_earth - total_uet:,.2f}")
    print(f"Efficiency Gain       : {saving_ratio:.1f}%")
    print("-----------------------------------------------")
    print("💡 STRATEGY: By using Graphene from waste, raw material cost drops by 95%.")
    print("💡 NO MINING: We rely on Recycle-Tin and Agriculture-Zero-Waste.")


if __name__ == "__main__":
    calculate_market_viability()
