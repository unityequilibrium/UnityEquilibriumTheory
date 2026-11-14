"""
UET Cinematic Viz: Black Hole Physics (Topic 0.2)
================================================
Visualizes the Singularity Resolution and Event Horizon.
Cyan: The Event Horizon (Information Saturation)
Magenta: The Information-Potential Field (Repulsion)
Gold: The Stable Core (Resolved Singularity)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.2_Black_Hole_Physics"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use("dark_background")
UET_CYAN = "#00e5ff"  # Horizon
UET_MAGENTA = "#ff00ff"  # Entropy/Potential
UET_GOLD = "#ffd700"  # Resolved Core
UET_BLACK = "#000000"




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_cine_black_hole():
    print("🚀 Generating UET Cinematic Black Hole Viz...")

    fig = plt.figure(figsize=(12, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection="3d", facecolor=UET_BLACK)

    # 1. Spacetime Grid (The Distorted Manifold)
    x = np.linspace(-5, 5, 40)
    y = np.linspace(-5, 5, 40)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    # Schwarzschild-like potential + UET Core repulsion
    # Potential drops to negative infinity at r=0 in GR, but UET has a bounce
    Rs = 2.0
    Z_gravity = -Rs / (R + 0.1)
    # UET core repulsion (divergent at center but balances gravity)
    Z_uet = 0.5 * (Rs**2) / (R**2 + 0.05)
    Z_total = Z_gravity + Z_uet

    # Mask the center for aesthetics
    Z_total = np.clip(Z_total, -10, 5)

    # Plot the wireframe (Manifold)
    ax.plot_wireframe(X, Y, Z_total, color=UET_MAGENTA, alpha=0.1, lw=0.5)

    # 2. The Event Horizon (Sphere of Saturation)
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    # Rs = 2.0 in our display units
    horizon_x = Rs * np.outer(np.cos(u), np.sin(v))
    horizon_y = Rs * np.outer(np.sin(u), np.sin(v))
    horizon_z = Rs * np.outer(np.ones(np.size(u)), np.cos(v))

    # Offset Z to center on the potential well's throat
    horizon_z_offset = -1.5

    ax.plot_surface(
        horizon_x,
        horizon_y,
        horizon_z + horizon_z_offset,
        color=UET_CYAN,
        alpha=0.1,
        rstride=2,
        cstride=2,
        linewidth=0,
    )
    # Wireframe for horizon
    ax.plot_wireframe(
        horizon_x, horizon_y, horizon_z + horizon_z_offset, color=UET_CYAN, alpha=0.3, lw=0.5
    )

    # 3. The Resolved Core (The Golden Equilibrium)
    core_r = 0.4
    core_x = core_r * np.outer(np.cos(u), np.sin(v))
    core_y = core_r * np.outer(np.sin(u), np.sin(v))
    core_z = core_r * np.outer(np.ones(np.size(u)), np.cos(v))

    # Position at the bottom of the potential well
    core_z_pos = -2.5

    ax.plot_surface(
        core_x, core_y, core_z + core_z_pos, color=UET_GOLD, alpha=0.6, rstride=1, cstride=1
    )
    # Glow for core
    ax.scatter([0], [0], [core_z_pos], color=UET_GOLD, s=1000, alpha=0.1)
    ax.scatter([0], [0], [core_z_pos], color="white", s=50, alpha=0.8)

    # 4. Accretion Disk (Inspiraling Information)
    disk_theta = np.linspace(0, 10 * np.pi, 500)
    disk_r = np.linspace(Rs, 5, 500)
    disk_x = disk_r * np.cos(disk_theta)
    disk_y = disk_r * np.sin(disk_theta)
    disk_z = np.full_like(disk_x, -1.0)

    ax.plot(disk_x, disk_y, disk_z, color=UET_GOLD, alpha=0.2, lw=1)
    ax.scatter(disk_x[::5], disk_y[::5], disk_z[::5], color=UET_GOLD, s=2, alpha=0.4)

    # 5. Styling
    ax.set_title("UET Black Hole: Singularity Resolution", fontsize=20, color=UET_CYAN, pad=20)

    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.axis("off")

    # Orientation for dramatic view of the well
    ax.view_init(elev=35, azim=-45)

    # Legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color=UET_CYAN, lw=2, label="Event Horizon (Information Limit)"),
        Line2D(
            [0], [0], color=UET_GOLD, marker="o", ls="", label="Stable Core (Singularity Resolved)"
        ),
        Line2D([0], [0], color=UET_MAGENTA, lw=2, label="Information Potential Well"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", frameon=False, fontsize=10)

    out_path = OUTPUT_DIR / "Cine_BlackHole_Physics.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Black Hole Viz saved to: {out_path}")

    plt.close()


if __name__ == "__main__":
    generate_cine_black_hole()
