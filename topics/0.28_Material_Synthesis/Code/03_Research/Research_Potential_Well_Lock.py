import numpy as np
import matplotlib.pyplot as plt


def energy_landscape(angle):
    """
    Simulates the energy potential of twisted bilayer graphene.
    The 'Magic Angle' (1.1) is a local energy minimum (a hole).
    """
    # Base energy (higher is unstable)
    base_energy = 10.0

    # The 'Magic Well' at 1.1 degrees
    magic_angle = 1.1
    well_depth = 8.0
    well_width = 0.05

    # Potential Well formula (Inverse Gaussian)
    well = well_depth * np.exp(-((angle - magic_angle) ** 2) / (2 * well_width**2))

    return base_energy - well


def simulate_vibration(initial_angle, noise_level, steps):
    """
    Simulates a graphene flake 'dancing' under acoustic vibration.
    """
    current_angle = initial_angle
    history = [current_angle]

    for _ in range(steps):
        # 1. Acoustic Kick (Random vibration)
        kick = np.random.normal(0, noise_level)
        new_angle = current_angle + kick

        # 2. Gravity-like pull (Energy minimization)
        # We want to move toward LOWER energy
        e_curr = energy_landscape(current_angle)
        e_new = energy_landscape(new_angle)

        if e_new < e_curr:
            # Always move to lower energy
            current_angle = new_angle
        else:
            # Probability to move to higher energy (thermal/acoustic jump)
            prob = np.exp(-(e_new - e_curr) / noise_level)
            if np.random.random() < prob:
                current_angle = new_angle

        history.append(current_angle)

    return history


def run_experiment():
    steps = 1000
    noise = 0.5  # High energy 'shaking'

    # Start at a 'Wrong' angle (e.g. 1.5 degrees)
    initial_pos = 1.5
    path = simulate_vibration(initial_pos, noise, steps)

    print("\n🕺 THE ATOMIC DANCE: Acoustic Alignment in Action")
    print("==================================================")
    print(f"Start Angle : {initial_pos:.2f}°")
    print(f"Final Angle : {path[-1]:.2f}°")
    print(f"Accuracy    : {(1.0 - abs(path[-1] - 1.1)/1.1)*100:.2f}%")

    # Visualization
    angles = np.linspace(0.5, 2.0, 500)
    energies = [energy_landscape(a) for a in angles]

    plt.figure(figsize=(12, 6))

    # Plot Energy Landscape
    plt.subplot(1, 2, 1)
    plt.plot(angles, energies, color="blue", label="Energy Potential")
    plt.scatter([1.1], [energy_landscape(1.1)], color="red", s=100, label="Magic Lock (1.1°)")
    plt.title("The 'Hole' in Reality (Energy Landscape)")
    plt.xlabel("Twist Angle")
    plt.ylabel("Potential Energy")
    plt.legend()

    # Plot The Path
    plt.subplot(1, 2, 2)
    plt.plot(path, color="magenta", alpha=0.6)
    plt.axhline(y=1.1, color="red", linestyle="--", label="1.1° Target")
    plt.title("The Flake's Path (Vibrating into Lock)")
    plt.xlabel("Time (Micro-steps)")
    plt.ylabel("Angle")
    plt.legend()

    plt.tight_layout()
    # Robust Path for Figures
    import os
    from pathlib import Path

    current_dir = Path(__file__).parent
    # Go up to topic root (Code/02_Proof -> Code -> TopicRoot)
    topic_root = current_dir.parent.parent

    # Standard: Result/02_Proof mirrors Code/02_Proof
    figures_dir = topic_root / "Result" / "02_Proof"
    figures_dir.mkdir(parents=True, exist_ok=True)

    save_path = figures_dir / "atomic_dance_sim.png"
    plt.savefig(str(save_path))

    print(f"\n✅ Simulation Complete. Plot saved as '{save_path.name}'")
    print("💡 ANALOGY: Like shaking a tray until the ball falls into the 1.1-degree slot.")


if __name__ == "__main__":
    run_experiment()
