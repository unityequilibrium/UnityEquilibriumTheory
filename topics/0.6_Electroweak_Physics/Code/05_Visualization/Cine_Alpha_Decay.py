"""
UET Cinematic Sim: Alpha Decay Tunneling (Topic 0.6)
===================================================
Visualizes the Quantum Tunneling process and the Geiger-Nuttall Law.
Cyan: The Alpha Particle Wave Function
Magenta: The Potential Barrier V(r)
Gold: The Escaped Particle
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

def generate_alpha_sim():
    print("🚀 Simulating Alpha Decay Tunneling...")
    fig = plt.figure(figsize=(12, 10), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection="3d", facecolor=UET_BLACK)

    # 1. The Potential Barrier Landscape
    radius = np.linspace(0.1, 10, 100)
    theta = np.linspace(0, 2 * np.pi, 50)
    R, THETA = np.meshgrid(radius, theta)
    X = R * np.cos(THETA)
    Y = R * np.sin(THETA)

    # Potential: Strong attractive well + Coulomb barrier
    # V(r) = -V0 (r < R0) + Z1*Z2*e^2/r (r > R0)
    R0 = 2.0
    V_nuclear = -40 * (R <= R0)
    V_coulomb = (20 / R) * (R > R0)
    Z = V_nuclear + V_coulomb

    ax.plot_surface(X, Y, Z, cmap="plasma", alpha=0.3, rstride=2, cstride=2)
    ax.plot_wireframe(X, Y, Z, color=UET_MAGENTA, alpha=0.1, lw=0.5)

    # 2. The Wave Function (Psi) inside the well
    r_well = np.linspace(0, R0, 50)
    theta_w = np.linspace(0, 2 * np.pi, 50)
    RW, TW = np.meshgrid(r_well, theta_w)
    XW = RW * np.cos(TW)
    YW = RW * np.sin(TW)
    ZW = 5 * np.cos(np.pi * RW / R0) - 40  # Wave standing inside
    ax.plot_surface(XW, YW, ZW, color=UET_CYAN, alpha=0.6)

    # 3. The Escaping Particle (The Tunneling Event)
    # A glowing sphere outside the barrier
    ax.scatter(
        [6], [0], [5], color=UET_GOLD, s=500, edgecolors="white", label="Escaped Alpha Particle"
    )
    # Tail (The path taken)
    path_r = np.linspace(2, 6, 20)
    ax.plot(path_r, [0] * 20, (20 / path_r), color=UET_GOLD, lw=3, alpha=0.5, ls="--")

    # Styling
    ax.set_title("UET Sim: Alpha Decay Tunneling (WKB Approximation)", fontsize=18, color=UET_GOLD)
    ax.set_zlim(-50, 25)
    ax.axis("off")
    ax.view_init(elev=25, azim=-45)

    # Annotations
    ax.text(0, 0, -45, "Nuclear Well", color=UET_CYAN, ha="center", fontsize=10)
    ax.text(0, 0, 15, "Coulomb Barrier", color=UET_MAGENTA, ha="center", fontsize=10)

    out_path = OUTPUT_DIR / "Sim_Alpha_Decay.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Alpha Simulation saved to: {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_alpha_sim()
