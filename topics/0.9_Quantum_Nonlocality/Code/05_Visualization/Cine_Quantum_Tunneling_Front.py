"""
UET Cinematic Viz: DNA Proton Tunneling (Topic 0.9) - ENHANCED VIEW
===================================================================
Visualizes Quantum Tunneling in biological scales as Information Decay.
Front-on view for better clarity as requested by the user.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.9_Quantum_Nonlocality"
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

def generate_tunneling_viz_front():
    print("🚀 Generating UET DNA Tunneling Viz (Front View)...")
    fig = plt.figure(figsize=(15, 10), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection="3d", facecolor=UET_BLACK)

    # 1. DNA Double Helix (Schematic - Straightened for Front View)
    z_helix = np.linspace(-5, 5, 500)
    theta = z_helix
    r = 3
    # Helix tracks
    ax.plot(r * np.cos(theta), r * np.sin(theta), z_helix, color=UET_GOLD, lw=4, alpha=0.2)
    ax.plot(
        r * np.cos(theta + np.pi),
        r * np.sin(theta + np.pi),
        z_helix,
        color=UET_GOLD,
        lw=4,
        alpha=0.2,
    )

    # 2. THE TUNNELING FOCUS (Front-on perspective)
    # We focus on the X-Z plane effectively

    # The Barrier (Magenta) - Potential energy wall
    x_bar = np.linspace(-2, 2, 100)
    # Potential hump V(x)
    z_bar = 2 * np.exp(-(x_bar**2) / 0.2)
    # Plot as a ribbon/wall
    for y_off in np.linspace(-0.5, 0.5, 5):
        ax.plot(x_bar, np.zeros_like(x_bar) + y_off, z_bar, color=UET_MAGENTA, lw=2, alpha=0.6)

    # Wave-function (Cyan)
    # Incoming Wave
    x_in = np.linspace(-5, -1, 100)
    z_in = 0.8 * np.sin(15 * x_in) * np.exp(-((x_in + 3) ** 2) / 2)
    ax.plot(x_in, np.zeros_like(x_in), z_in, color=UET_CYAN, lw=3, alpha=0.9)

    # Tunnelled Wave (Lower amplitude)
    x_out = np.linspace(1, 5, 100)
    z_out = 0.2 * np.sin(15 * x_out) * np.exp(-((x_out - 3) ** 2) / 2)
    ax.plot(x_out, np.zeros_like(x_out), z_out, color=UET_CYAN, lw=2, alpha=0.7)

    # The "Ghostly" Proton Pulse
    # Represented as glowing particles blinking through
    ax.scatter([-3, 3], [0, 0], [0, 0], color=UET_CYAN, s=300, alpha=0.4, edgecolors="white")
    ax.scatter(
        [0],
        [0],
        [1.5],
        color=UET_MAGENTA,
        s=100,
        alpha=0.8,
        marker="X",
        label="Information Barrier",
    )

    # Labels & Info
    ax.text(-3, 0, 2, "Stable H-Bond", color=UET_CYAN, ha="center", fontweight="bold")
    ax.text(3, 0, 2, "Quantum Leak (Mutation)", color=UET_MAGENTA, ha="center", fontweight="bold")
    ax.text(0, 0, 3.5, "Barrier: 0.4 eV", color=UET_GOLD, ha="center")

    # Styling
    ax.set_title(
        "UET Field Mechanics: DNA Proton Tunneling (Structural Leak)",
        fontsize=22,
        color=UET_CYAN,
        pad=20,
    )
    ax.set_xlabel("Informational Coordinate (x)")
    ax.set_zlabel("Unity Intensity (Ω)")

    # Adjust camera for strictly front-on (X-Z plane)
    ax.view_init(elev=0, azim=-90)
    ax.axis("off")

    # Legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color=UET_CYAN, lw=3, label="Proton Information Wave (σ)"),
        Line2D([0], [0], color=UET_MAGENTA, lw=2, label="Potential Barrier (H-Bond Energy)"),
        Line2D([0], [0], color=UET_GOLD, lw=4, alpha=0.3, label="DNA Scaffold (Unity Grid)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", frameon=False)

    out_path = OUTPUT_DIR / "Cine_Quantum_Tunneling_Front.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ DNA Tunneling Front Viz saved to: {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_tunneling_viz_front()
