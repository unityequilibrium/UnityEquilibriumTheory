"""
UET Cinematic Viz: The Bell Bridge (Topic 0.9)
=============================================
Visualizes Quantum Entanglement as a topological bridge in the Information Field.
Cyan: Particle A Spin
Magenta: Particle B Spin
Gold: The Unity Field "Bridge"
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

def generate_bell_viz():
    print("🚀 Generating UET Bell Bridge Viz...")
    fig = plt.figure(figsize=(15, 10), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection="3d", facecolor=UET_BLACK)

    # 1. The Bridge (Unity Field)
    # A curved path connecting two distant points
    x = np.linspace(-10, 10, 500)
    y = 2 * np.sin(x / 3)
    z = 1 * np.cos(x / 2)

    # Draw glowing bridge
    ax.plot(x, y, z, color=UET_GOLD, lw=3, alpha=0.9, label="Unity Field Connectivity")
    ax.plot(x, y, z, color=UET_GOLD, lw=10, alpha=0.1)  # Glow

    # 2. Particles at the ends
    ax.scatter([-10], [y[0]], [z[0]], color=UET_CYAN, s=200, label="Entangled Particle A")
    ax.scatter([10], [y[-1]], [z[-1]], color=UET_MAGENTA, s=200, label="Entangled Particle B")

    # 3. Spin Vectors (Anti-correlated)
    ax.quiver(-10, y[0], z[0], 0, 0, 3, color=UET_CYAN, lw=3, arrow_length_ratio=0.3)
    ax.quiver(10, y[-1], z[-1], 0, 0, -3, color=UET_MAGENTA, lw=3, arrow_length_ratio=0.3)

    # 4. Phase Information Rings
    for i in [125, 250, 375]:
        theta = np.linspace(0, 2 * np.pi, 20)
        rx = 0.5 * np.cos(theta) + x[i]
        ry = 0.5 * np.sin(theta) + y[i]
        rz = z[i] + np.zeros_like(theta)
        ax.plot(rx, ry, rz, color=UET_GOLD, alpha=0.3, lw=1)

    # Styling
    ax.set_title(
        "UET Nonlocality: The Bell Bridge (Topological Entanglement)",
        fontsize=20,
        color=UET_GOLD,
        pad=20,
    )
    ax.text(0, 5, 0, "S ≈ 2√2 (Tsirelson Limit)", color=UET_GOLD, ha="center", fontsize=12)
    ax.axis("off")
    ax.view_init(elev=20, azim=-60)

    # Legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D(
            [0],
            [0],
            color=UET_CYAN,
            marker="o",
            linestyle="None",
            markersize=10,
            label="Particle A (Spin Up)",
        ),
        Line2D(
            [0],
            [0],
            color=UET_MAGENTA,
            marker="o",
            linestyle="None",
            markersize=10,
            label="Particle B (Spin Down)",
        ),
        Line2D([0], [0], color=UET_GOLD, lw=4, label="Quantum Information Bridge"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", frameon=False)

    out_path = OUTPUT_DIR / "Cine_Quantum_Bell.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Bell Bridge Viz saved to: {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_bell_viz()
