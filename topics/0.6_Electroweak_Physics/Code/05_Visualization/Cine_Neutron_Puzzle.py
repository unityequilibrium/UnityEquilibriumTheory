"""
UET Cinematic Sim: Neutron Lifetime Puzzle (Topic 0.6)
======================================================
Visualizes the discrepancy between "Bottle" and "Beam" experiments.
Cyan: The Cold Neutrons (Bottle Method)
Magenta: The Flux of Decays (Beam Method)
Gold: The 9-second Discrepancy
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.6_Electroweak_Physics"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use("dark_background")
UET_CYAN = "#00e5ff"
UET_MAGENTA = "#ff00ff"
UET_GOLD = "#ffd700"
UET_BLACK = "#000000"




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_neutron_puzzle_sim():
    print("🚀 Simulating Neutron Lifetime Puzzle...")
    fig = plt.figure(figsize=(16, 8), facecolor=UET_BLACK)

    # 1. Visualization of the Two Methods
    ax1 = fig.add_subplot(121, projection="3d", facecolor=UET_BLACK)

    # Method A: The Bottle (UCN)
    # A cylinder of points
    z = np.linspace(-4, 0, 10)
    theta = np.linspace(0, 2 * np.pi, 20)
    Z, THETA = np.meshgrid(z, theta)
    X = 3 * np.cos(THETA)
    Y = 3 * np.sin(THETA)
    ax1.plot_wireframe(X, Y, Z, color=UET_CYAN, alpha=0.1, lw=0.5)
    ax1.scatter(
        np.random.uniform(-2, 2, 20),
        np.random.uniform(-2, 2, 20),
        np.random.uniform(-3, -1, 20),
        color=UET_CYAN,
        s=5,
        alpha=0.6,
        label="Bottle (Counting Survivors)",
    )

    # Method B: The Beam
    # A stream of points
    beam_z = np.linspace(2, 6, 20)
    ax1.plot([0] * 20, [0] * 20, beam_z, color=UET_MAGENTA, lw=10, alpha=0.1)  # Beam core
    ax1.scatter(
        np.random.normal(0, 0.2, 30),
        np.random.normal(0, 0.2, 30),
        np.random.uniform(3, 5, 30),
        color=UET_MAGENTA,
        s=5,
        alpha=0.8,
        label="Beam (Counting Decays)",
    )

    ax1.set_title("Experimental Methods", color=UET_GOLD, fontsize=14)
    ax1.axis("off")
    ax1.view_init(elev=20, azim=45)
    ax1.legend(loc="lower left", frameon=False)

    # 2. The Resulting Discrepancy Graph
    ax2 = fig.add_subplot(122, facecolor=UET_BLACK)

    tau_bottle = 878.4  # Seconds
    tau_beam = 887.7  # Seconds

    t = np.linspace(0, 3000, 500)
    survive_bottle = 100 * np.exp(-t / tau_bottle)
    survive_beam = 100 * np.exp(-t / tau_beam)

    ax2.plot(t, survive_bottle, color=UET_CYAN, lw=2, label=f"Bottle: τ = {tau_bottle}s")
    ax2.plot(t, survive_beam, color=UET_MAGENTA, lw=2, label=f"Beam: τ = {tau_beam}s")

    # Highlight the GAP
    idx = 150  # point to highlight
    ax2.annotate(
        "The 9-Second Mystery",
        xy=(t[idx], survive_beam[idx]),
        xytext=(t[idx] + 500, survive_beam[idx] + 10),
        color=UET_GOLD,
        arrowprops=dict(facecolor=UET_GOLD, shrink=0.05),
        fontsize=12,
    )

    ax2.set_title("The Lifetime Discrepancy", color=UET_GOLD, fontsize=14)
    ax2.set_xlabel("Time (s)", color="gray")
    ax2.set_ylabel("Survival Probability %", color="gray")
    ax2.legend(frameon=False)
    ax2.grid(alpha=0.1)

    plt.suptitle("UET Sim: Resolving the Neutron Lifetime Puzzle", fontsize=20, color=UET_CYAN)

    out_path = OUTPUT_DIR / "Sim_Neutron_Puzzle.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Neutron Simulation saved to: {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_neutron_puzzle_sim()
