import numpy as np
import matplotlib.pyplot as plt
import os


def run_proof():
    print("\n🔬 UET TOPIC 0.29: THE $10M INVESTMENT CHALLENGE")
    print("=============================================")

    # 1. Investment Parameters
    investment_budget = 10_000_000  # $10 Million USD

    # 2. Cost Models (Per Hectare - 10,000 m2)
    # Forest: Cheap, basic planting
    cost_forest_ha = 3_000.0  # $3,000 / ha (High quality restoration)

    # UET Ocean: Industrial Engineering (High CapEx)
    # Estimate: $50 per m2 unit * 5,000 units (50% coverage density)
    cost_ocean_ha = 250_000.0  # $250,000 / ha (Industrial scale pricing)

    # 3. Output Models (Per Hectare / Year)
    # Oxygen: Gross Production (The "Factory" metric)
    o2_forest_ton_yr = 11.0  # ~30 g/m2/day * 10,000 * 365 / 1e6
    o2_ocean_ton_yr = 63.0  # ~172 g/m2/day * 10,000 * 365 / 1e6 (5.8x factor)

    # Economics: Ecosystem Services (Tourism, Fish, Protection)
    econ_forest_yr = 2_500.0  # $2,500 / ha / year
    econ_ocean_yr = 80_000.0  # $80,000 / ha / year (High value coral services)

    # 4. Initial "Purchase" (How much can we buy?)
    area_forest = investment_budget / cost_forest_ha
    area_ocean = investment_budget / cost_ocean_ha

    print(f"💰 Budget: ${investment_budget/1e6:.0f} Million")
    print(f"🌳 Forest Acquired: {area_forest:.1f} Hectares (Massive Area)")
    print(f"W Ocean Acquired:  {area_ocean:.1f} Hectares (Targeted Spot)")

    # 5. Simulation (50 Years)
    years = 50
    time = np.arange(years + 1)

    # Cumulative Utility
    cum_o2_forest = []
    cum_o2_ocean = []

    cum_val_forest = []
    cum_val_ocean = []

    current_o2_f = 0
    current_o2_o = 0
    current_val_f = 0
    current_val_o = 0

    # Growth factors
    # Forests take 20 years to reach peak output
    # Corals take 5-10 years to overgrow structure

    for y in time:
        # Growth Curve (Sigmoid)
        maturity_f = 1 / (1 + np.exp(-0.2 * (y - 10)))  # Peak at 20
        maturity_o = 1 / (1 + np.exp(-0.5 * (y - 5)))  # Peak at 10

        # Yearly Output
        year_o2_f = area_forest * o2_forest_ton_yr * maturity_f
        year_o2_o = area_ocean * o2_ocean_ton_yr * maturity_o

        year_val_f = area_forest * econ_forest_yr * maturity_f
        year_val_o = area_ocean * econ_ocean_yr * maturity_o

        # Cumulative
        current_o2_f += year_o2_f
        current_o2_o += year_o2_o
        cum_o2_forest.append(current_o2_f)
        cum_o2_ocean.append(current_o2_o)

        current_val_f += year_val_f
        current_val_o += year_val_o
        cum_val_forest.append(current_val_f)
        cum_val_ocean.append(current_val_o)

    # 6. Analysis
    print("\n📊 50-YEAR RETURN ON INVESTMENT:")
    print(f"Oxygen Produced (Forest): {cum_o2_forest[-1]:.0f} Tons")
    print(
        f"Oxygen Produced (Ocean):  {cum_o2_ocean[-1]:.0f} Tons ratio: {cum_o2_ocean[-1]/cum_o2_forest[-1]:.2f}x"
    )

    print(f"Economic Value Generated (Forest): ${cum_val_forest[-1]/1e6:.1f} M")
    print(
        f"Economic Value Generated (Ocean):  ${cum_val_ocean[-1]/1e6:.1f} M ratio: {cum_val_ocean[-1]/cum_val_forest[-1]:.2f}x"
    )

    # 7. Visualize
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    os.makedirs(result_dir, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Oxygen
    ax1.plot(time, cum_o2_forest, "g--", label=f"Forest ({area_forest:.0f} ha)")
    ax1.plot(time, cum_o2_ocean, "b-", linewidth=3, label=f"UET Ocean ({area_ocean:.0f} ha)")
    ax1.set_title("Cumulative Oxygen Production (50 Years)")
    ax1.set_ylabel("Tons of O2")
    ax1.set_xlabel("Year")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Plot 2: Money (Ecosystem Value)
    ax2.plot(time, [investment_budget / 1e6] * len(time), "k:", label="Initial Investment")
    ax2.plot(time, np.array(cum_val_forest) / 1e6, "g--", label="Forest Value")
    ax2.plot(time, np.array(cum_val_ocean) / 1e6, "b-", linewidth=3, label="Ocean Value")
    ax2.set_title("Cumulative Economic Value Generated ($M)")
    ax2.set_ylabel("Million USD")
    ax2.set_xlabel("Year")
    ax2.legend()
    ax2.grid(alpha=0.3)

    output_path = os.path.join(result_dir, "Res_Economic_Scale.png")
    plt.savefig(output_path)
    print(f"📈 Plot saved to: {output_path}")
    plt.close()

    # Verdict
    # Even with much smaller area, does Ocean win on Value?
    if cum_val_ocean[-1] > cum_val_forest[-1]:
        print("✅ PROOF PASSED: Ocean Restoration beats Forest in Economic ROI.")
    else:
        print("❌ PROOF FAILED: Forest is still better due to massive area.")


if __name__ == "__main__":
    run_proof()
