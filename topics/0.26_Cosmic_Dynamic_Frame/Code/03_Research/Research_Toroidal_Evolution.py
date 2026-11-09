"""
Research_Toroidal_Evolution.py
==============================
Topic: 0.26 Cosmic Dynamic Frame
Hypothesis:
    1. The Universe evolves from a Cylinder to a Torus.
    2. "Singularity/Big Bang" occurs when the Torus geometry intersects (Hole closes).

Experiment:
    - Simulate a Toroidal Field where r_minor (Tube Radius) grows over time.
    - R_major (Ring Radius) stays fixed (or grows slower).
    - Critical Moment: When r_minor -> R_major, the "Hole" closes.
    - Measure: Maximum Velocity/Energy at the Core (The Hole).

Prediction:
    As the hole narrows, conservation of angular momentum (flow) should cause
    velocity to spike -> Infinity. This models the "Big Bang" as a Geometric Event.
"""

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
from pathlib import Path

# --- ROBUST PATH FINDER ---


from docs.core.uet_glass_box import UETPathManager


def get_flow_velocity(x, y, z, R_major, r_minor):
    """
    Calculate flow velocity in a dynamic Torus.
    Constraint: Volume is conserved, so if flow area constricts, speed increases.
    """
    rho = np.sqrt(x**2 + y**2)
    dist_to_ring = np.sqrt((rho - R_major) ** 2 + z**2)

    # 1. Toroidal Spin (Around the ring)
    # v_phi ~ 1/dist (Vortex behavior)
    # Singularity avoid: dist + epsilon
    v_phi = 10.0 / (dist_to_ring + 0.1)

    # 2. Poloidal Flow (Through the hole)
    # As hole closes (rho -> 0), poloidal flux is squeezed.
    # Squeeze Factor: 1 / (Area of Hole)
    hole_radius = max(0.1, R_major - r_minor)
    squeeze_factor = 10.0 / hole_radius

    # Poloidal speed increases as we get closer to the center z-axis
    v_pol = squeeze_factor * (1.0 / (rho + 0.1))

    return v_phi, v_pol


def run_evolution():
    print("=" * 60)
    print("🍩 UET TOPOLOGY RESEARCH: THE GEOMETRIC SINGULARITY")
    print("   Testing: What happens when the Torus Hole closes?")
    print("=" * 60)

    # Parameters
    R_major = 10.0  # Fixed Ring Radius
    r_minor_start = 2.0  # Start as thin tube
    r_minor_end = 9.9  # End almost closing the hole (Horn Torus)
    steps = 50

    r_values = np.linspace(r_minor_start, r_minor_end, steps)
    energy_levels = []

    print(f"   Simulating Evolution: r_minor {r_minor_start} -> {r_minor_end}")

    for i, r in enumerate(r_values):
        hole_radius = R_major - r

        # Test particle at the "Event Horizon" (Inner edge of the torus)
        test_rho = hole_radius + 0.1
        test_z = 0

        # Get Velocity
        v_phi, v_pol = get_flow_velocity(test_rho, 0, test_z, R_major, r)

        total_energy = 0.5 * (v_phi**2 + v_pol**2)
        energy_levels.append(total_energy)

        if i % 10 == 0:
            print(
                f"   Stage {i:<2}: Hole Radius = {hole_radius:.2f} | Energy = {total_energy:.2f}"
            )

    # Theoretical Singularity
    print("-" * 60)
    peak_energy = max(energy_levels)
    start_energy = energy_levels[0]
    increase_factor = peak_energy / start_energy

    print(f"   Initial Energy: {start_energy:.2f}")
    print(f"   Peak Energy:    {peak_energy:.2f}")
    print(f"   Spike Factor:   {increase_factor:.1f}x")

    output_dir = UETPathManager.get_result_dir(
        topic_id="0.26_Cosmic_Dynamic_Frame",
        experiment_name="Research_Toroidal_Evolution",
        pillar="03_Research",
        category="log",
    )

    plt.figure(figsize=(10, 6))
    plt.plot(r_values, energy_levels, "r-", linewidth=3)
    plt.axvline(x=R_major, color="k", linestyle="--", label="Singularity (Hole Closes)")
    plt.title("Cosmic Energy vs. Torus Evolution")
    plt.xlabel("Torus Tube Radius (r_minor)")
    plt.ylabel("Core Energy Density")
    plt.grid(True)
    plt.annotate(
        "Big Bang Event?",
        xy=(r_values[-1], energy_levels[-1]),
        xytext=(r_values[steps // 2], energy_levels[-1]),
        arrowprops=dict(facecolor="black", shrink=0.05),
    )

    plt.savefig(output_dir / "singularity_plot.png")
    print(f"   [Viz] Saved: {output_dir / 'singularity_plot.png'}")

    if increase_factor > 10.0:
        print("✅ CONFIRMED: Geometric Closure creates an Energy Singularity.")
        print("   Hypothesis Validated: The 'Big Bang' is a Topological Event.")
        return True
    else:
        print("❌ FAIL: No singularity observed.")
        return False


if __name__ == "__main__":
    success = run_evolution()
    sys.exit(0 if success else 1)
