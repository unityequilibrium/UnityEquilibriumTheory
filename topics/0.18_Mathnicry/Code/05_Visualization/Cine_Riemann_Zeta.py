"""
UET Cinematic Viz: Riemann Hypothesis (Topic 0.18)
==================================================
Aesthetic Restoration of the "Complex Spiral" look.
Matches the user's reference image for ζ(s).
Uses custom "Glow" effects in Matplotlib.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
import mpmath



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.18_Mathnicry"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use('dark_background')
UET_CYAN = "#00e5ff"
UET_MAGENTA = "#ff00ff"
UET_GOLD = "#ffd700"
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_cine_riemann():
    print("🚀 Generating UET Cinematic Riemann Zeta Viz...")
    
    # 1. Setup Data: Scanning zeta(1/2 + it)
    t = np.linspace(0, 40, 1000)
    complex_points = [0.5 + 1j * val for val in t]
    
    # Use mpmath for high precision
    mpmath.mp.dps = 20
    zeta_vals = [complex(mpmath.zeta(s)) for s in complex_points]
    
    x = [z.real for z in zeta_vals]
    y = [z.imag for z in zeta_vals]
    z = t # Time/Height axis
    
    fig = plt.figure(figsize=(12, 16), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # 2. Rendering Layers (The GLOW effect)
    # Layer 1: Wide blurred glow
    ax.plot(x, y, z, color=UET_CYAN, alpha=0.1, lw=10, zorder=1)
    # Layer 2: Medium halo
    ax.plot(x, y, z, color=UET_CYAN, alpha=0.3, lw=4, zorder=2)
    # Layer 3: Core bright line
    ax.plot(x, y, z, color="white", alpha=0.8, lw=1.5, zorder=3)
    
    # 3. Features: The Critical Line (Geometry of Truth)
    # Draw a vertical spine at (0,0, t)
    ax.plot([0, 0], [0, 0], [0, 40], color=UET_GOLD, alpha=0.4, ls='--', lw=1, label="The Zero Hub")
    
    # Mark the Zeros (Equilibrium Sinks)
    # Known zeros at approx 14.13, 21.02, 25.01, 30.42, 32.93, 37.58
    zeros_t = [14.13, 21.02, 25.01, 30.42, 32.93, 37.58]
    for z_t in zeros_t:
        ax.scatter([0], [0], [z_t], color=UET_GOLD, s=150, alpha=0.9, edgecolors='white', marker='o', zorder=5)
        # Add labels for sinks
        ax.text(0.2, 0.2, z_t, f"Zero @ {z_t}", color=UET_GOLD, fontsize=8)

    # 4. Projections (Shadow Fields)
    # Projection on the bottom (Re vs Im plot)
    ax.plot(x, y, np.zeros_like(z)-2, color=UET_MAGENTA, alpha=0.2, lw=1)
    
    # 5. Styling & Labels
    ax.set_title("$\mathbb{R}$iemann Hypothesis: Geometric Sink Analysis", fontsize=20, color=UET_GOLD, pad=20)
    
    # Remove axis panes
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    
    # Set limits and hide axis
    ax.set_xlim(-2, 3)
    ax.set_ylim(-2.5, 2.5)
    ax.set_zlim(0, 42)
    
    # Floating axis labels
    ax.set_xlabel("$\mathbb{R}eal$ (Re)", color=UET_CYAN)
    ax.set_ylabel("$\mathbb{I}maginary$ (Im)", color=UET_CYAN)
    ax.set_zlabel("$t$ (Height)", color=UET_GOLD)
    
    # 6. Orientation (Dramatic Angle)
    ax.view_init(elev=25, azim=-45)
    
    # Dark Mode Polish
    plt.tight_layout()
    
    out_path = OUTPUT_DIR / "Cine_Riemann_Zeta_Showcase.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Viz saved to: {out_path}")
    
    # Optional: Save a sequence for GIF (simulate animation)
    print("📸 Creating multi-angle sequence...")
    for i, angle in enumerate(range(-45, 15, 20)):
        ax.view_init(elev=25, azim=angle)
        plt.savefig(OUTPUT_DIR / f"Cine_Riemann_Frame_{i}.png", dpi=100)
    
    plt.close()

if __name__ == "__main__":
    generate_cine_riemann()
