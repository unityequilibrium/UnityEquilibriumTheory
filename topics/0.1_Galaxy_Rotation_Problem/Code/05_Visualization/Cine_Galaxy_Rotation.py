"""
UET Cinematic Viz: Galaxy Rotation Problem (Topic 0.1)
======================================================
Visualizes the Galaxy Rotation Curve in a high-end 3D style.
Shows the "Omega Field" flux and why the velocity stays flat.
Matches the UET Cinematic Standard.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.1_Galaxy_Rotation_Problem"
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

def generate_cine_galaxy():
    print("🌌 Generating UET Cinematic Galaxy Rotation Viz...")

    # 1. Physics Logic (SPARC-like mockup)
    # R (radius in kpc)
    r = np.linspace(0.1, 30, 100)

    # Newtonian Velocity (Drops off like 1/sqrt(r))
    v_newton = 200 * np.exp(-r / 10) + 50 / np.sqrt(r)
    v_newton = np.clip(v_newton, 0, 250)

    # UET Velocity (Stays flat due to Omega gradient)
    v_uet = 200 * (1 - np.exp(-r / 5)) + 150  # Mocking the MOND/UET flatness
    v_uet = np.clip(v_uet, 0, 230)

    # 3D Spiral Mesh for the background
    angle = np.linspace(0, 10 * np.pi, 1000)
    spiral_r = np.linspace(0, 30, 1000)
    spiral_x = spiral_r * np.cos(angle)
    spiral_y = spiral_r * np.sin(angle)
    spiral_z = np.zeros_like(spiral_r)

    fig = plt.figure(figsize=(12, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection="3d", facecolor=UET_BLACK)

    # 2. Rendering Layers

    # Layer 1: The Galaxy Disk (Glow)
    ax.plot(spiral_x, spiral_y, spiral_z, color=UET_CYAN, alpha=0.1, lw=5)
    ax.scatter(spiral_x[::10], spiral_y[::10], spiral_z[::10], color="white", s=1, alpha=0.3)

    # Layer 2: The Core (Glow)
    ax.scatter([0], [0], [0], color="white", s=500, alpha=0.1)
    ax.scatter([0], [0], [0], color=UET_GOLD, s=100, alpha=0.8)

    # 3. The Rotation Curve (3D Projection)
    # We project the curve into the Z-axis
    # Newtonian Curve (Red/Magenta - The "Failing" Theory)
    ax.plot(
        r, np.zeros_like(r), v_newton, color=UET_MAGENTA, lw=2, alpha=0.6, label="Newtonian Falloff"
    )
    ax.plot(r, np.zeros_like(r), v_newton, color=UET_MAGENTA, lw=8, alpha=0.1)  # Glow

    # UET Curve (Cyan/Gold - The "Winning" Theory)
    ax.plot(r, np.zeros_like(r), v_uet, color=UET_CYAN, lw=2, alpha=0.9, label="UET Flat Rotation")
    ax.plot(r, np.zeros_like(r), v_uet, color=UET_CYAN, lw=10, alpha=0.2)  # Glow

    # Connection lines (Rays)
    for i in range(0, len(r), 10):
        ax.plot([r[i], r[i]], [0, 0], [0, v_uet[i]], color=UET_CYAN, alpha=0.3, ls=":")

    # 4. Omega Field (The Sauce)
    # Draw a faint field mesh around the galaxy
    # This represents the information energy curvature
    xx, yy = np.meshgrid(np.linspace(-30, 30, 20), np.linspace(-30, 30, 20))
    # Omega field density (Higher at center)
    zz_omega = 400 / (np.sqrt(xx**2 + yy**2) + 10)
    ax.plot_wireframe(xx, yy, zz_omega, color=UET_GOLD, alpha=0.05, lw=0.5)

    # 5. Styling
    ax.set_title("UET Galaxy Dynamics: The Information Flux", fontsize=18, color=UET_CYAN, pad=20)

    # Clean up
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.axis("off")  # Pure Cinematic look

    # Orientation
    ax.view_init(elev=35, azim=-60)

    # Legend
    ax.legend(loc="upper right", frameon=False, fontsize=10)

    out_path = OUTPUT_DIR / "Cine_Galaxy_Rotation.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Galaxy Viz saved to: {out_path}")

    plt.close()


if __name__ == "__main__":
    generate_cine_galaxy()
