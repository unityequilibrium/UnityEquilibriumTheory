"""
UET Cinematic Viz: Electroweak Decay Showcase (Topic 0.6)
========================================================
Visualizes the Neutron Beta Decay process and Decay rates.
Cyan: Electron / Neutrino (Light particles)
Magenta: W Boson (The Mediator)
Gold: Proton / Neutron (The Hadrons)
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

def draw_sphere(ax, center, radius, color, alpha=0.7):
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 20)
    x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
    y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
    z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0)


def generate_decay():
    print("🚀 Generating UET Electroweak Decay Viz (Showcase A)...")
    fig = plt.figure(figsize=(16, 8), facecolor=UET_BLACK)

    # --- 1. Neutron Decay (3D Animation Frame) ---
    ax1 = fig.add_subplot(121, projection="3d", facecolor=UET_BLACK)

    # Neutron (Starting point)
    draw_sphere(ax1, [-4, 0, 0], 1.5, "gray", alpha=0.4)
    ax1.text(-4, 0, 2, "Neutron (n)", color="white", ha="center")

    # The Transition (W- Boson streak)
    t = np.linspace(0, 1, 50)
    ax1.plot(-4 + 6 * t, [0] * 50, np.sin(t * np.pi) * 2, color=UET_MAGENTA, lw=4, alpha=0.8)
    ax1.plot(
        -4 + 6 * t, [0] * 50, np.sin(t * np.pi) * 2, color=UET_MAGENTA, lw=12, alpha=0.1
    )  # Glow
    ax1.text(-1, 0, 2.5, "W- Boson", color=UET_MAGENTA, ha="center", fontsize=10)

    # Products: Proton (Gold), Electron (Cyan), Antineutrino (Faint Cyan)
    draw_sphere(ax1, [2, 1, 0], 1.5, UET_GOLD, alpha=0.8)
    ax1.text(2, 1, 2, "Proton (p)", color=UET_GOLD, ha="center")

    # Lepton Trajectories
    ax1.plot([2, 6], [1, 4], [0, 2], color=UET_CYAN, lw=2, alpha=0.9, label="Electron (e-)")
    ax1.plot([2, 5], [1, -5], [0, -3], color=UET_CYAN, lw=2, alpha=0.4, ls="--", label="Neutrino")

    ax1.set_title("Beta Decay: Nuclear Transformation", color=UET_MAGENTA, fontsize=14)
    ax1.view_init(elev=20, azim=-30)
    ax1.axis("off")

    # --- 2. Lifetime Statistics (Experimental Plot) ---
    ax2 = fig.add_subplot(122, facecolor=UET_BLACK)
    time = np.linspace(0, 5000, 200)
    n_count = 100 * np.exp(-time / 879.4)  # Neutron mean life ~879s
    ax2.plot(time, n_count, color=UET_CYAN, lw=2, label="Neutron Survival Rate")
    ax2.fill_between(time, n_count, color=UET_CYAN, alpha=0.1)

    ax2.set_title("Experimental Evidence: Neutron Lifetime (τ)", color=UET_GOLD, fontsize=14)
    ax2.set_xlabel("Time (seconds)", color="gray")
    ax2.set_ylabel("Probability of Survival", color="gray")
    ax2.grid(alpha=0.1)
    ax2.legend(frameon=False)

    plt.suptitle(
        "UET Showcase A: Special Weak-Force Decay Experiments", fontsize=20, color=UET_GOLD
    )
    plt.savefig(OUTPUT_DIR / "Cine_Electroweak_Decay.png", dpi=200, facecolor=UET_BLACK)
    plt.close()


if __name__ == "__main__":
    generate_decay()
