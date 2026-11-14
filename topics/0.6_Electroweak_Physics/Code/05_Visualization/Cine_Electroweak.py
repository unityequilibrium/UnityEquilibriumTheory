"""
UET Cinematic Viz: Electroweak Physics (Topic 0.6)
=================================================
Visualizes the Weinberg Angle (Mixing) and Symmetry Breaking.
Cyan: The Photon Field (A) - Long Range
Magenta: The W/Z Boson Fields - Short Range "Heavy"
Gold: The Unified Electroweak Force
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
plt.style.use('dark_background')
UET_CYAN = "#00e5ff"    # EM
UET_MAGENTA = "#ff00ff" # Weak
UET_GOLD = "#ffd700"    # Unified
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_cine_electroweak():
    print("🚀 Generating UET Cinematic Electroweak Viz...")
    
    fig = plt.figure(figsize=(12, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # --- 1. THE MIXING AXES (Weinberg Angle) ---
    theta_w = 28.7 * np.pi / 180 # Standard Weinberg Angle approx 28.7 degrees
    
    # Drawing the Axes
    length = 10
    # Unified Axis
    ax.plot([0, 0], [0, 0], [0, length], color=UET_GOLD, lw=4, alpha=0.8, label="Unified Field")
    ax.plot([0, 0], [0, 0], [0, length], color=UET_GOLD, lw=12, alpha=0.1) # Glow

    # EM Plane (Photon) - Rotated by theta_w
    ax.plot([0, length*np.sin(theta_w)], [0, length*np.cos(theta_w)], [0, 0], 
            color=UET_CYAN, lw=3, alpha=0.9, label="Photon (EM)")
    
    # Weak Plane (Z Boson) - Orthogonal to EM plane in the mixing space
    ax.plot([0, length*np.cos(theta_w)], [0, -length*np.sin(theta_w)], [0, 0], 
            color=UET_MAGENTA, lw=3, alpha=0.9, label="Z Boson (Weak)")

    # --- 2. FIELD DIVERGENCE (Particles) ---
    # Photon: Straight long-range beam
    ax.plot(np.linspace(0, 8, 50), np.linspace(0, 8, 50), [0]*50, color=UET_CYAN, alpha=0.3, lw=1)
    
    # W/Z Bosons: Short-range "Heavy" vortices
    for _ in range(5):
        vx = np.random.uniform(-4, 4)
        vy = np.random.uniform(-4, 4)
        vz = np.linspace(0, 2, 20)
        v_angle = np.linspace(0, 4*np.pi, 20)
        v_r = 0.5 * (1 - vz/2)
        ax.plot(vx + v_r*np.cos(v_angle), vy + v_r*np.sin(v_angle), vz, 
                color=UET_MAGENTA, alpha=0.5, lw=1)

    # --- 3. THE HIGGS VACUUM (Grid) ---
    xx, yy = np.meshgrid(np.linspace(-10, 10, 20), np.linspace(-10, 10, 20))
    # Subsurface grid with a "Heavy" potential well in the center
    zz = -2 * np.exp(-(xx**2 + yy**2)/20)
    ax.plot_wireframe(xx, yy, zz, color=UET_GOLD, alpha=0.05, lw=0.5)

    # --- 4. DATA TEXT ---
    ax.text(0, 0, length + 0.5, "SU(2) x U(1)", color=UET_GOLD, ha='center', fontsize=12, fontweight='bold')
    ax.text(length*np.sin(theta_w), length*np.cos(theta_w), 0.5, "sin²θ_W ≈ 0.231", color=UET_CYAN, ha='center', fontsize=10)

    # Styling
    ax.set_title("UET Electroweak: Geometric Field Mixing", fontsize=18, color=UET_CYAN, pad=20)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.axis('off')
    
    ax.view_init(elev=25, azim=-60)
    ax.legend(loc='lower left', frameon=False, fontsize=10)
    
    out_path = OUTPUT_DIR / "Cine_Electroweak.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Electroweak Viz saved to: {out_path}")
    
    plt.close()

if __name__ == "__main__":
    generate_cine_electroweak()
