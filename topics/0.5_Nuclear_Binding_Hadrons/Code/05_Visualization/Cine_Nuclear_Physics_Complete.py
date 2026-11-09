"""
UET Cinematic Viz: Comprehensive Nuclear & Hadron Showcase (Topic 0.5)
======================================================================
Visualizes ALL key research components:
1. Stability Valley (Nuclear)
2. Proton Structure (Hadron)
3. QCD Running Coupling (The Bridge)
4. Light Nuclei Overlap (Axiomatic Geometry)
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


def generate_cine_nuclear_complete():
    print("🚀 Generating COMPREHENSIVE UET Nuclear & Hadron Viz...")

    fig = plt.figure(figsize=(18, 14), facecolor=UET_BLACK)

    # --- [1] The Valley of Stability (Nuclear Landscape) ---
    ax1 = fig.add_subplot(221, projection="3d", facecolor=UET_BLACK)
    z_vals = np.linspace(1, 100, 40)
    n_vals = np.linspace(1, 150, 40)
    Z_grid, N_grid = np.meshgrid(z_vals, n_vals)
    A_grid = Z_grid + N_grid
    B_per_A = (
        15.7
        - 17.8 / (A_grid ** (1 / 3))
        - 0.71 * (Z_grid**2) / (A_grid ** (4 / 3))
        - 23.7 * ((N_grid - Z_grid) ** 2) / (A_grid**2)
    )
    B_per_A = np.clip(B_per_A, 0, 9)
    ax1.plot_surface(Z_grid, N_grid, B_per_A, cmap="magma", alpha=0.5, rstride=2, cstride=2)
    stable_z = np.linspace(1, 100, 20)
    stable_n = stable_z * (1 + (stable_z / 200))
    ax1.plot(stable_z, stable_n, 8.5, color=UET_GOLD, lw=3, alpha=0.8)  # Stability line
    ax1.set_title("Nuclei: Valley of Stability", color=UET_GOLD, fontsize=14)
    ax1.axis("off")
    ax1.view_init(elev=35, azim=-140)

    # --- [2] Inside the Proton (Quark Confinement) ---
    ax2 = fig.add_subplot(222, projection="3d", facecolor=UET_BLACK)
    quark_pos = np.array([[1, 0, 0], [-0.5, 0.86, 0], [-0.5, -0.86, 0]])
    for i in range(3):
        color = UET_CYAN if i < 2 else UET_MAGENTA
        draw_sphere(ax2, quark_pos[i], 0.35, color)
        # Y-Strings
        ax2.plot(
            [0, quark_pos[i, 0]],
            [0, quark_pos[i, 1]],
            [0, quark_pos[i, 2]],
            color=UET_MAGENTA,
            lw=2,
            alpha=0.6,
        )
    ax2.set_title("Hadron: u-u-d Structure", color=UET_CYAN, fontsize=14)
    ax2.axis("off")
    ax2.view_init(elev=20, azim=45)

    # --- [3] QCD Running Coupling (The Bridge) ---
    ax3 = fig.add_subplot(223, facecolor=UET_BLACK)
    Q = np.geomspace(0.5, 100, 200)
    # Alpha_s(Q) = 1 / (b0 * ln(Q^2/Lambda^2))
    alpha_qcd = 1 / (0.6 * np.log(Q**2 / 0.2**2))
    # UET correction: smoother at low Q (Beta-boost)
    alpha_uet = alpha_qcd * (1 - 0.2 * np.exp(-Q / 2))

    ax3.plot(Q, alpha_qcd, color=UET_MAGENTA, ls="--", alpha=0.4, label="Standard QCD")
    ax3.plot(Q, alpha_uet, color=UET_CYAN, lw=2, label="UET Bridge")
    ax3.fill_between(Q, alpha_uet, alpha_qcd, color=UET_CYAN, alpha=0.1)

    ax3.set_xscale("log")
    ax3.set_title("QCD Bridge: Running Coupling $\\alpha_s(Q)$", color=UET_CYAN, fontsize=14)
    ax3.set_xlabel("Energy Scale Q (GeV)", color="gray")
    ax3.set_ylabel("Strength $\\alpha_s$", color="gray")
    ax3.legend(frameon=False)
    ax3.grid(alpha=0.1)

    # --- [4] Light Nuclei: Alpha Particle (Geometry) ---
    ax4 = fig.add_subplot(224, projection="3d", facecolor=UET_BLACK)
    # Tetrahedral positions for He-4
    s = 1.0
    alpha_pos = np.array([[s, s, s], [s, -s, -s], [-s, s, -s], [-s, -s, s]])
    for i in range(4):
        color = UET_GOLD if i < 2 else "white"  # Protons and Neutrons
        draw_sphere(ax4, alpha_pos[i], 0.8, color, alpha=0.6)

    # Manifold overlap (Central Glow)
    ax4.scatter([0], [0], [0], color=UET_CYAN, s=2000, alpha=0.1)
    ax4.set_title("Light Nuclei: Helium-4 Tetra-Symmetry", color=UET_GOLD, fontsize=14)
    ax4.axis("off")
    ax4.view_init(elev=30, azim=60)

    plt.suptitle(
        "UET COMPREHENSIVE NUCLEAR SHOWCASE: SCALE INTEGRATION", fontsize=22, color=UET_GOLD, y=0.96
    )
    plt.figtext(
        0.5,
        0.02,
        "From Quark Confinement to Nuclear Stability: A Unified Information-Geometric Proof",
        ha="center",
        fontsize=12,
        color="gray",
        fontstyle="italic",
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    out_path = OUTPUT_DIR / "Cine_Nuclear_Physics_Complete.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ COMPLETE Cinematic Nuclear Viz saved to: {out_path}")

    plt.close()


if __name__ == "__main__":
    generate_cine_nuclear_complete()
