import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Create path to Engine
script_dir = os.path.dirname(os.path.abspath(__file__))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
sys.path.append(engine_dir)

from Engine_Ocean_Power import OceanGenerator


def run_proof():
    print("\n🔬 UET TOPIC 0.29: FREE ENERGY PROOF")
    print("====================================")

    # 1. Setup Generator
    # 10 Wh Battery (Like a large power bank cell)
    gen = OceanGenerator(battery_capacity_wh=10.0)

    # 2. Simulation Parameters (24 Hours)
    hours = 24
    dt = 60  # seconds
    steps = hours * 60

    # Input Data (From Research 1 Findings)
    # Delta T averages 1.7 C, fluctuating slightly
    # Flow velocity averages 0.5 m/s (Updraft from chimney effect)

    time_points = []
    battery_levels = []
    power_ins = []

    print(f"⚡ Simulating {hours} Hours of Autonomous Operation...")
    print(f"   Delta T Input: ~1.7 °C")
    print(f"   Flow Input:    ~0.5 m/s")

    # 3. Time Stepping
    for i in range(steps):
        t_hour = i / 60.0

        # Inputs with slight noise/variation
        delta_t = 1.7 + 0.2 * np.sin(t_hour)
        flow_v = 0.5 + 0.1 * np.cos(t_hour * 2)

        # Engine Update
        status = gen.update(delta_t, flow_v, dt_seconds=dt)

        time_points.append(t_hour)
        battery_levels.append(status["Battery_Pct"])
        power_ins.append(status["P_Total_In"])

    # 4. Analysis
    avg_power = np.mean(power_ins)
    min_battery = min(battery_levels)
    final_battery = battery_levels[-1]

    print("\n📊 RESULTS:")
    print(f"Average Power Gen: {avg_power*1000:.1f} mW")
    print(f"Minimum Battery:   {min_battery:.1f}%")
    print(f"Final Battery:     {final_battery:.1f}%")

    # 5. Visualize
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    os.makedirs(result_dir, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = "tab:blue"
    ax1.set_xlabel("Time (Hours)")
    ax1.set_ylabel("Battery Level (%)", color=color)
    ax1.plot(time_points, battery_levels, color=color, linewidth=2, label="Battery Status")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_ylim(0, 100)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = "tab:orange"
    ax2.set_ylabel(
        "Power Generation (Watts)", color=color
    )  # we already handled the x-label with ax1
    ax2.plot(time_points, power_ins, color=color, linestyle="--", alpha=0.5, label="Power In")
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title(f"Energy Autonomy Check: Avg Generation {avg_power*1000:.0f} mW")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    output_path = os.path.join(result_dir, "Res_Energy_Budget.png")
    plt.savefig(output_path)
    print(f"📈 Plot saved to: {output_path}")
    plt.close()

    # 6. Pass/Fail
    if min_battery > 20.0 and avg_power > 0.1:
        print("✅ PROOF PASSED: System is self-sufficient.")
    else:
        print("❌ PROOF FAILED: Battery drained or insufficient power.")


if __name__ == "__main__":
    run_proof()
