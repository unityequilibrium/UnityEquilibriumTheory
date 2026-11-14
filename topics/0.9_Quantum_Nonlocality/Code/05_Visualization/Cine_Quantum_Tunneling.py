"""
UET Cinematic Viz: DNA Proton Tunneling (Topic 0.9)
===================================================
Visualizes Quantum Tunneling in biological scales as Information Decay.
Cyan: Proton Wave-function
Gold: DNA Helix Backbone
Magenta: Potential Barrier (Information Gap)
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

def generate_tunneling_viz():
    print("🚀 Generating UET DNA Tunneling Viz...")
    fig = plt.figure(figsize=(15, 10), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection="3d", facecolor=UET_BLACK)

    # 1. DNA Double Helix (Schematic)
    z = np.linspace(0, 15, 500)
    theta = 2 * z
    r = 3
    # Helix 1
    x1, y1 = r * np.cos(theta), r * np.sin(theta)
    # Helix 2 (180 deg shifted)
    x2, y2 = r * np.cos(theta + np.pi), r * np.sin(theta + np.pi)

    ax.plot(x1, y1, z, color=UET_GOLD, lw=4, alpha=0.3)
    ax.plot(x2, y2, z, color=UET_GOLD, lw=4, alpha=0.3)

    # 2. Base Pairs (Steps)
    for i in range(0, 500, 50):
        ax.plot([x1[i], x2[i]], [y1[i], y2[i]], [z[i], z[i]], color=UET_GOLD, alpha=0.2, lw=1)

    # 3. THE TUNNELING EVENT (Zoom-in at z=7.5)
    center_z = 7.5
    # The barrier (Magenta)
    bx = np.linspace(-1, 1, 20)
    by = np.zeros_like(bx)
    bz = center_z + np.exp(-(bx**2) / 0.1) * 2  # Potential hump
    ax.plot(bx, by, bz, color=UET_MAGENTA, lw=3, label="Potential Barrier (H-Bond)")

    # The Proton Wave-function (Cyan)
    # Reflected part
    wx_left = np.linspace(-4, -1, 50)
    wz_left = center_z + 0.5 * np.sin(10 * wx_left)
    ax.plot(wx_left, np.zeros_like(wx_left), wz_left, color=UET_CYAN, lw=2, alpha=0.8)
    # Transmitted part (Lower amplitude)
    wx_right = np.linspace(1, 4, 50)
    wz_right = center_z + 0.15 * np.sin(10 * wx_right)
    ax.plot(wx_right, np.zeros_like(wx_right), wz_right, color=UET_CYAN, lw=2, alpha=0.8)

    # The "Ghostly" Tunneling particle
    ax.scatter([-1.5, 1.5], [0, 0], [center_z, center_z], color=UET_CYAN, s=50, alpha=0.5)

    # Styling
    ax.set_title("UET Field Mechanics: DNA Proton Tunneling", fontsize=20, color=UET_CYAN, pad=20)
    ax.text(
        0,
        -5,
        center_z + 1,
        "Information Leak (L) → Mutation Risk",
        color=UET_MAGENTA,
        ha="center",
        fontsize=12,
    )
    ax.axis("off")
    ax.view_init(elev=25, azim=15)

    # Legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color=UET_GOLD, lw=4, label="DNA Information Scaffold"),
        Line2D([0], [0], color=UET_CYAN, lw=2, label="Proton Wave (Informational Flow)"),
        Line2D([0], [0], color=UET_MAGENTA, lw=3, label="H-Bond Potential Barrier"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", frameon=False)

    out_path = OUTPUT_DIR / "Cine_Quantum_Tunneling.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ DNA Tunneling Viz saved to: {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_tunneling_viz()
