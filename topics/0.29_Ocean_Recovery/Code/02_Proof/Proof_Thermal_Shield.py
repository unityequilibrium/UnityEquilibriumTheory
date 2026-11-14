import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add Engine directory to sys.path to handle numbered folders (e.g. 0.29)
script_dir = os.path.dirname(os.path.abspath(__file__))
engine_dir = os.path.abspath(os.path.join(script_dir, "../01_Engine"))
sys.path.append(engine_dir)

from Engine_Ocean_Cooling import OceanHeatSink

# For standard path references if needed
# from docs.core.uet_glass_box import UETPathManager


def run_proof():
    print("\n🔬 UET TOPIC 0.29: OCEAN COOLING PROOF")
    print("======================================")

    # 1. Setup Simulation
    # Simulate a "Heat Wave" event over 48 hours
    hours = 48
    steps_per_hour = 60  # Minute resolution
    total_steps = hours * steps_per_hour

    # Create the Heat Sink (1m3 volume)
    # Ground Temp = 26 C
    # Deep Sand Bed coupling
    sink = OceanHeatSink(volume_m3=1.0, wall_thickness_m=0.2)

    # 2. Generate Ambient Data (The Threat)
    # Sinusoidal wave oscillating between 29C (Day) and 34C (Peak Heat Wave)
    # Normal bleaching threshold is ~30.5C
    time_points = np.linspace(0, hours, total_steps)
    ambient_temps = 31.5 + 2.5 * np.sin(2 * np.pi * time_points / 24)

    internal_temps = []

    print(f"🌊 Simulating {hours} Hours of Heat Wave...")
    print(f"🔥 Ambient Peak: {max(ambient_temps):.2f} C")
    print(f"❄️ Ground Temp: {sink.ground_temp:.2f} C")

    # 3. Run Physics Engine
    for i in range(total_steps):
        current_ambient = ambient_temps[i]
        # Engine update (dt = 60s)
        t_internal = sink.update(current_ambient, dt_seconds=60)
        internal_temps.append(t_internal)

    # 4. Analyze Results
    internal_temps = np.array(internal_temps)

    # Metrics
    max_internal = max(internal_temps)
    cooling_delta = max(ambient_temps) - max_internal
    avg_delta = np.mean(ambient_temps) - np.mean(internal_temps)

    print("\n📊 RESULTS:")
    print(f"Max Internal Temp: {max_internal:.2f} C")
    print(f"Cooling Protection: -{cooling_delta:.2f} C (Peak Reduction)")
    print(f"Average Cooling:    -{avg_delta:.2f} C")

    # 5. Visualize
    # Path logic
    script_dir = os.path.dirname(os.path.abspath(__file__))
    topic_root = os.path.dirname(os.path.dirname(script_dir))
    result_dir = os.path.join(topic_root, "Result", "02_Proof")
    os.makedirs(result_dir, exist_ok=True)

    plt.figure(figsize=(12, 6))
    plt.plot(time_points, ambient_temps, "r--", label="Ambient Water (Heat Wave)", alpha=0.7)
    plt.plot(time_points, internal_temps, "b-", label="Inside Structure (Sanctuary)", linewidth=2)
    plt.axhline(y=30.5, color="orange", linestyle=":", label="Bleaching Threshold (30.5C)")

    plt.fill_between(
        time_points,
        internal_temps,
        ambient_temps,
        color="blue",
        alpha=0.1,
        label="Thermal Shielding",
    )

    plt.title(f"Thermal Inertia Shielding: Peak Reduction -{cooling_delta:.2f}°C")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = os.path.join(result_dir, "Res_Cooling_Performance.png")
    plt.savefig(output_path)
    print(f"📈 Plot saved to: {output_path}")
    plt.close()

    # 6. Conclusion
    if cooling_delta > 1.5 and max_internal < 31.0:
        print("✅ PROOF PASSED: Structure maintains safe sanctuary.")
    elif cooling_delta > 0.5:
        print("⚠️ PROOF PARTIAL: Cooling works but insufficient magnitude.")
    else:
        print("❌ PROOF FAILED: Structure cannot resist heat wave.")


if __name__ == "__main__":
    run_proof()
