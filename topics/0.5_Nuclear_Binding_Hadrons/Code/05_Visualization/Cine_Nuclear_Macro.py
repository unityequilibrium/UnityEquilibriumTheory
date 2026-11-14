"""
UET Cinematic Viz: Nuclear Macro Showcase (Topic 0.5)
=====================================================
1. Valley of Stability
2. Light Nuclei Geometry (He-4)
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


def generate_macro():
    print("🚀 Generating UET Nuclear Macro Viz (Showcase A)...")
    fig = plt.figure(figsize=(16, 8), facecolor=UET_BLACK)

    # 1. Valley of Stability
    ax1 = fig.add_subplot(121, projection="3d", facecolor=UET_BLACK)
    z_vals = np.linspace(1, 100, 50)
    n_vals = np.linspace(1, 150, 50)
    Z_grid, N_grid = np.meshgrid(z_vals, n_vals)
    A_grid = Z_grid + N_grid
    B_per_A = (
        15.7
        - 17.8 / (A_grid ** (1 / 3))
        - 0.71 * (Z_grid**2) / (A_grid ** (4 / 3))
        - 23.7 * ((N_grid - Z_grid) ** 2) / (A_grid**2)
    )
    B_per_A = np.clip(B_per_A, 0, 9)
    ax1.plot_surface(Z_grid, N_grid, B_per_A, cmap="magma", alpha=0.6)
    ax1.set_title("Nuclear Landscape: Valley of Stability", color=UET_GOLD, fontsize=14)
    ax1.view_init(elev=35, azim=-140)
    ax1.axis("off")

    # 2. Light Nuclei (He-4)
    ax2 = fig.add_subplot(122, projection="3d", facecolor=UET_BLACK)
    s = 1.0
    alpha_pos = np.array([[s, s, s], [s, -s, -s], [-s, s, -s], [-s, -s, s]])
    for i in range(4):
        color = UET_GOLD if i < 2 else "white"
        draw_sphere(ax2, alpha_pos[i], 0.8, color, alpha=0.5)
    ax2.set_title("Light Nuclei: Axiomatic Geometry (He-4)", color=UET_CYAN, fontsize=14)
    ax2.view_init(elev=30, azim=60)
    ax2.axis("off")

    plt.suptitle("UET Showcase A: Nuclear Stability & Macro-Geometry", fontsize=20, color=UET_GOLD)
    plt.savefig(OUTPUT_DIR / "Cine_Nuclear_Macro.png", dpi=200, facecolor=UET_BLACK)
    plt.close()


if __name__ == "__main__":
    generate_macro()
