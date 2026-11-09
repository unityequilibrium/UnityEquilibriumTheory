import numpy as np
import matplotlib.pyplot as plt


def radiative_cooling_simulation():
    """
    Simulates the temperature drop of a water surface protected by
    a UET Radiative Cooling Membrane vs a standard surface.
    Outer space temperature T_space = 3K
    Atmospheric window = 8-13 microns
    """
    time = np.linspace(0, 12, 100)  # 12 hours (Day to Night transition)
    ambient_temp = 32 + 2 * np.sin(time / 4)  # Starts hot, cools slightly

    # Standard surface (Absorbs solar reflection, trapped by greenhouse)
    std_water_temp = ambient_temp + 1.5 * np.cos(time / 6)

    # UET Membrane (Emits IR directly to space via 8-13um window)
    # cooling_power ~ 100 W/m^2
    cooling_rate = 0.8  # degree per hour effective drop
    uet_water_temp = std_water_temp - (cooling_rate * time)

    # Limit cooling to a realistic floor (approx 10-15 degrees below ambient)
    uet_water_temp = np.maximum(uet_water_temp, std_water_temp - 12)

    plt.figure(figsize=(10, 6))
    plt.plot(time, std_water_temp, "r--", label="Standard Sea Surface (Heated by Sun/CO2)")
    plt.plot(time, uet_water_temp, "b-", label="UET Shielded Zone (Radiative Cooling to Space)")
    plt.fill_between(
        time,
        std_water_temp,
        uet_water_temp,
        color="cyan",
        alpha=0.2,
        label="Energy Dumped to Space",
    )

    plt.title("Radiative Cooling: Dumping Ocean Heat into Outer Space (3K)")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Temperature (°C)")
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

    save_path = figures_dir / "ocean_cooling_space_dump.png"
    plt.savefig(str(save_path))

    print(f"\n✅ Heat sink successfully diverted to the cosmic void.")


if __name__ == "__main__":
    radiative_cooling_simulation()
