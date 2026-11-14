import numpy as np
import matplotlib.pyplot as plt


def simulate_cleanup(total_pollution_kg, cycles):
    """
    Simulates the cleanup of an ocean zone.
    Macro-Robot: Good at large debris (80% capture), bad at microplastics (5% capture).
    UET-Hybrid: Macro-Robot + Graphene Aerogel Filter (99% microplastic capture).
    """
    # Assumption: 70% of plastic by count are microplastics (<5mm)
    macro_debris = total_pollution_kg * 0.3
    micro_debris = total_pollution_kg * 0.7

    # 1. Standard Robot Results
    robot_macro_remain = macro_debris * (0.2**cycles)  # 80% per cycle
    robot_micro_remain = micro_debris * (0.95**cycles)  # 5% per cycle
    total_robot_remain = robot_macro_remain + robot_micro_remain

    # 2. UET Hybrid (Robot + Graphene Sponge)
    hybrid_macro_remain = macro_debris * (0.2**cycles)
    hybrid_micro_remain = micro_debris * (0.01**cycles)  # 99% per cycle
    total_hybrid_remain = hybrid_macro_remain + hybrid_micro_remain

    return total_robot_remain, total_hybrid_remain


def run_remediation_demo():
    poll_kg = 1000  # 1 Ton of pollution
    cycles = np.arange(1, 6)

    robot_data = []
    hybrid_data = []

    for c in cycles:
        r, h = simulate_cleanup(poll_kg, c)
        robot_data.append(r)
        hybrid_data.append(h)

    print("\n🌊 OCEAN CLEANUP SIMULATION: Macro vs Micro")
    print("==========================================")
    print(f"Cycle 3 Results:")
    print(f"Standard Robot Remainder : {robot_data[2]:.2f} kg (Mostly Microplastics)")
    print(f"UET Hybrid Remainder     : {hybrid_data[2]:.2f} kg (Near Total Cleanup)")

    plt.figure(figsize=(10, 6))
    plt.plot(cycles, robot_data, "r--o", label="Standard Solar Robot (Large Debris only)")
    plt.plot(cycles, hybrid_data, "g-s", label="UET Hybrid (Robot + Graphene Sponge)")
    plt.axhline(y=10, color="gray", linestyle=":", label="Bio-Safety Threshold")
    plt.title("Ocean Remediation: Mass of Pollution Remaining over Time")
    plt.xlabel("Cleanup Cycles (passes over area)")
    plt.ylabel("Pollution Remaining (kg)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Robust Path for Figures
    import os
    from pathlib import Path

    current_dir = Path(__file__).parent
    # Go up to topic root (Code/03_Research -> Code -> TopicRoot)
    topic_root = current_dir.parent.parent

    # Standard: Result/03_Research mirrors Code/03_Research
    figures_dir = topic_root / "Result" / "03_Research"
    figures_dir.mkdir(parents=True, exist_ok=True)

    save_path = figures_dir / "ocean_remediation_plot.png"
    plt.savefig(str(save_path))

    print(f"\n✅ Simulation Complete. Plot saved as '{save_path.name}'")
    print(
        "💡 CONCLUSION: Standard robots collect large debris; Graphene Filters capture micro-toxins."
    )


if __name__ == "__main__":
    run_remediation_demo()
