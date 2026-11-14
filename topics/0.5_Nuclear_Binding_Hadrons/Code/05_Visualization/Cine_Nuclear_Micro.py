"""
UET Cinematic Viz: Nuclear Micro Showcase (Topic 0.5)
=====================================================
1. Proton Structure
2. QCD Running Coupling
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.5_Nuclear_Binding_Hadrons"
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


def generate_micro():
    print("🚀 Generating UET Nuclear Micro Viz (Showcase B)...")
    fig = plt.figure(figsize=(16, 8), facecolor=UET_BLACK)

    # 1. Proton Structure
    ax1 = fig.add_subplot(121, projection="3d", facecolor=UET_BLACK)
    quark_pos = np.array([[1, 0, 0], [-0.5, 0.86, 0], [-0.5, -0.86, 0]])
    for i in range(3):
        color = UET_CYAN if i < 2 else UET_MAGENTA
        draw_sphere(ax1, quark_pos[i], 0.35, color)
        ax1.plot(
            [0, quark_pos[i, 0]],
            [0, quark_pos[i, 1]],
            [0, quark_pos[i, 2]],
            color=UET_MAGENTA,
            lw=2,
            alpha=0.6,
        )
    ax1.set_title("Hadron: Quark Confinement (uud)", color=UET_CYAN, fontsize=14)
    ax1.axis("off")
    ax1.view_init(elev=20, azim=45)

    # 2. QCD Running Coupling
    ax2 = fig.add_subplot(122, facecolor=UET_BLACK)
    Q = np.geomspace(0.5, 100, 200)
    alpha_uet = (1 / (0.6 * np.log(Q**2 / 0.2**2))) * (1 - 0.2 * np.exp(-Q / 2))
    ax2.plot(Q, alpha_uet, color=UET_CYAN, lw=2, label="UET Prediction")
    ax2.set_xscale("log")
    ax2.set_title("QCD Bridge: Information Binding", color=UET_MAGENTA, fontsize=14)
    ax2.grid(alpha=0.1)
    ax2.legend(frameon=False)

    plt.suptitle("UET Showcase B: Hadron Structure & QCD Bridge", fontsize=20, color=UET_MAGENTA)
    plt.savefig(OUTPUT_DIR / "Cine_Nuclear_Micro.png", dpi=200, facecolor=UET_BLACK)
    plt.close()


if __name__ == "__main__":
    generate_micro()
