"""
UET Cinematic Viz: Electroweak Symmetry Showcase (Topic 0.6)
===========================================================
Visualizes the Higgs Potential (Symmetry Breaking) and Mass Generation.
Cyan: The Photon Field
Magenta: The Heavy Boson Fields
Gold: The Higgs Vacuum Well
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

def generate_symmetry():
    print("🚀 Generating UET Electroweak Symmetry Viz (Showcase B)...")
    fig = plt.figure(figsize=(16, 8), facecolor=UET_BLACK)

    # --- 1. The Higgs Potential (The Mexican Hat) ---
    ax1 = fig.add_subplot(121, projection="3d", facecolor=UET_BLACK)
    r = np.linspace(0, 4, 100)
    theta = np.linspace(0, 2 * np.pi, 100)
    R, THETA = np.meshgrid(r, theta)
    X = R * np.cos(THETA)
    Y = R * np.sin(THETA)
    # V(phi) = -mu^2*phi^2 + lambda*phi^4
    Z = -3 * R**2 + 0.5 * R**4

    ax1.plot_surface(X, Y, Z, cmap="viridis", alpha=0.6, rstride=2, cstride=2)
    # The "Broken" vacuum state (A marble sitting in the valley)
    ax1.scatter(
        [2], [0], [-4], color=UET_GOLD, s=200, edgecolors="white", label="Broken Symmetry (v)"
    )

    ax1.set_title("The Higgs Potential: Origin of Mass", color=UET_GOLD, fontsize=14)
    ax1.axis("off")
    ax1.view_init(elev=30, azim=15)

    # --- 2. Mass Generation (The Field Split) ---
    ax2 = fig.add_subplot(122, projection="3d", facecolor=UET_BLACK)

    # Photon Field (A - massless)
    z_long = np.linspace(0, 10, 50)
    ax2.plot([0] * 50, [0] * 50, z_long, color=UET_CYAN, lw=1, alpha=0.5, label="Photon (0 GeV)")

    # W/Z Fields (Heavy - short range vortices)
    theta = np.linspace(0, 8 * np.pi, 100)
    z_short = np.linspace(0, 4, 100)
    ax2.plot(
        0.5 * np.cos(theta),
        0.5 * np.sin(theta),
        z_short,
        color=UET_MAGENTA,
        lw=3,
        alpha=0.9,
        label="W/Z Bosons (Heavy)",
    )
    # Glow for heavy field
    ax2.scatter([0], [0], [2], color=UET_MAGENTA, s=5000, alpha=0.05)

    ax2.set_title("Mass Generation: W vs Photon", color=UET_CYAN, fontsize=14)
    ax2.axis("off")
    ax2.view_init(elev=20, azim=45)

    plt.suptitle("UET Showcase B: Symmetry Breaking & Higgs Field", fontsize=20, color=UET_CYAN)
    plt.savefig(OUTPUT_DIR / "Cine_Electroweak_Symmetry.png", dpi=200, facecolor=UET_BLACK)
    plt.close()


if __name__ == "__main__":
    generate_symmetry()
