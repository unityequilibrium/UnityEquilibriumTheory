import os
import sys

# Dynamically add the Engine path to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
if engine_dir not in sys.path:
    sys.path.append(engine_dir)

from Engine_Flash_Joule import FlashJouleReactor


def run_proof():
    print("\n🏭 UET TOPIC 0.28: PROJECT 'SMOKESTACK GOLD'")
    print("==========================================")
    print("Scenario: Retrofitting a medium factory with FJH Units")

    # 1. Factory Parameters
    daily_waste_kg = 1000.0  # 1 Ton of Carbon-rich waste/day (Soot, Tires, Plastic)
    electricity_cost_kwh = 0.12  # $0.12 / kWh (Industrial Rate)

    # 2. Market Values
    # Waste Disposal Cost (We SAVE this money)
    disposal_cost_per_kg = 0.05  # Landfill fee

    # Graphene Value (Turbostratic / Bulk construction grade)
    # NOT the $100/g lab stuff. This is "Concrete Additive" grade.
    # Estimated Future Industrial Price: $50 / kg (Very conservative)
    graphene_value_kg = 50.0

    # 3. The Reactor Bank
    # We need to process 1000 kg in 24 hours
    batch_size_g = 1.0  # 1 gram per flash (Small scale FJH)
    # But we have many in parallel, or rapid fire.

    reactor = FlashJouleReactor(voltage_volts=350)

    print(f"📉 Input Waste: {daily_waste_kg:,.0f} kg")
    print(f"⚡ Electricity Price: ${electricity_cost_kwh}/kWh")
    print(f"💰 Graphene Target Price: ${graphene_value_kg}/kg")

    # 4. Simulation Loop (One Sample Batch)
    print("\n--- Running Optimization Test (Single Batch) ---")

    # Optimization sweep to find best pulse for this "Waste Type"
    best_efficiency = float("inf")
    best_pulse = 0
    final_yield_pct = 0

    pulses = [10, 30, 50, 80, 100, 150]  # ms duration

    for p in pulses:
        res = reactor.run_flash(sample_mass_g=batch_size_g, resistance_ohm=3.0, pulse_duration_ms=p)
        eff = res["efficiency_kj_g"]
        temp = res["peak_temp_k"]

        if res["success"]:
            if eff < best_efficiency:
                best_efficiency = eff
                best_pulse = p
                final_yield_pct = res["yield_percent"]

            print(
                f"  Pulse {p}ms: Temp {temp:.0f}K | Eff: {eff:.2f} kJ/g | Yield: {res['yield_percent']:.0f}% ✅"
            )
        else:
            print(f"  Pulse {p}ms: Temp {temp:.0f}K | ❌ Too Cold")

    print(f"\n🏆 Optimal Pulse Found: {best_pulse}ms ({best_efficiency:.2f} kJ/g)")

    # 5. Daily Production Calculation
    # Scale up Single Batch to 1 Ton
    total_yield_kg = daily_waste_kg * (final_yield_pct / 100.0)

    # Energy Calculation
    # kJ to kWh conversion: 1 kWh = 3600 kJ
    total_energy_kj = best_efficiency * (daily_waste_kg * 1000.0)  # kJ/g * g
    total_energy_kwh = total_energy_kj / 3600.0

    total_elec_cost = total_energy_kwh * electricity_cost_kwh
    total_disposal_saving = daily_waste_kg * disposal_cost_per_kg
    total_revenue = total_yield_kg * graphene_value_kg

    net_profit = total_revenue - total_elec_cost + total_disposal_saving

    print("\n📊 DAILY FACTORY BALANCE SHEET:")
    print("-" * 40)
    print(f"  Input Waste:      {daily_waste_kg:,.0f} kg")
    print(f"  Graphene Output:  {total_yield_kg:,.0f} kg (Yield: {final_yield_pct:.0f}%)")
    print(f"  Energy Consumed:  {total_energy_kwh:,.1f} kWh")
    print("-" * 40)
    print(f"  🔻 Electricity Cost:  -${total_elec_cost:,.2f}")
    print(f"  🔺 Disposal Saving:   +${total_disposal_saving:,.2f}")
    print(f"  💵 Graphene Revenue:  +${total_revenue:,.2f}")
    print("=" * 40)
    print(f"  📈 NET DAILY PROFIT:  +${net_profit:,.2f}")

    roi_msg = "FAILED"
    if net_profit > 0 and (total_revenue > total_elec_cost * 10):
        roi_msg = "✅ MASSIVE SUCCESS (10x Margin)"
        print(f"\nVeridct: {roi_msg}")
        print("Conclusion: Distributed Graphene Production is economically viable.")
    else:
        print("\nVerdict: ❌ FAIL. Electricity too expensive.")


if __name__ == "__main__":
    run_proof()
