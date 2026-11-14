"""
UET Cinematic Viz: Hubble Tension (Topic 0.3)
=============================================
Visualizes the divergence between Early (Global) and Late (Local) Universe expansion.
Cyan: Local Expansion (Measured by JWST/SH0ES)
Magenta: Global Expansion (Measured by Planck/CMB)
Gold: The UET Transition Curve
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.3_Cosmology_Hubble_Tension"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use('dark_background')
UET_CYAN = "#00e5ff"    # Local (SH0ES)
UET_MAGENTA = "#ff00ff" # Global (Planck)
UET_GOLD = "#ffd700"    # UET Prediction
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_cine_hubble():
    print("🚀 Generating UET Cinematic Hubble Tension Viz...")
    
    fig = plt.figure(figsize=(12, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # 1. Redshift (Z) axis - logarithmic-ish to show detail at both ends
    z = np.linspace(0, 5, 200)
    
    # Standard Cosmology H(z) mockup
    h0_planck = 67.4
    h0_shoes = 73.0
    
    # Global Curve (Planck Baseline)
    h_global = h0_planck * np.sqrt(0.3 * (1 + z)**3 + 0.7)
    
    # Local Divergence (What we see locally)
    # In UET, the local expansion is boosted by beta = sqrt(alpha_em) approx 0.085
    beta = 0.085
    h_local = h_global * (1 + beta * np.exp(-z/1.5)) # Divergence fades at high z
    
    # 2. Rendering the Curves in 3D
    # The X-axis represents Time (Z), Y represents Scale, Z represents Expansion Rate
    
    # Global Curve (Magenta - Light from the finish)
    ax.plot(z, np.zeros_like(z), h_global, color=UET_MAGENTA, alpha=0.9, lw=2, label="Early Universe (Planck)")
    ax.plot(z, np.zeros_like(z), h_global, color=UET_MAGENTA, alpha=0.1, lw=10) # Glow
    
    # Local Data Points (Cyan - Modern measurements)
    ax.plot(z[:50], np.zeros_like(z[:50]), h_local[:50], color=UET_CYAN, alpha=0.9, lw=2, label="Late Universe (SH0ES/JWST)")
    ax.plot(z[:50], np.zeros_like(z[:50]), h_local[:50], color=UET_CYAN, alpha=0.2, lw=10) # Glow
    
    # 3. The Galactic Web (Visual Background)
    # Random stars/galaxies following the expansion
    np.random.seed(42)
    for _ in range(30):
        rand_z = np.random.uniform(0, 5)
        rand_y = np.random.uniform(-10, 10)
        h_val = h0_planck * np.sqrt(0.3 * (1 + rand_z)**3 + 0.7)
        if rand_z < 1.0:
            h_val *= (1 + beta)
            color = UET_CYAN
        else:
            color = UET_MAGENTA
            
        ax.scatter([rand_z], [rand_y], [h_val], color=color, s=5, alpha=0.3)
        
    # 4. The Manifold Grid (The Expanding Space)
    xx, yy = np.meshgrid(np.linspace(0, 5, 20), np.linspace(-15, 15, 20))
    # Grid depth represents the potential well of expansion
    zz_grid = h0_planck * np.sqrt(0.3 * (1 + xx)**3 + 0.7)
    ax.plot_wireframe(xx, yy, zz_grid, color=UET_GOLD, alpha=0.05, lw=0.5)

    # 5. Styling
    ax.set_title("UET Hubble Tension: Resolving the Cosmic Discrepancy", fontsize=18, color=UET_CYAN, pad=20)
    
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.axis('off')
    
    ax.view_init(elev=30, azim=-120)
    ax.legend(loc='upper left', frameon=False, fontsize=10)
    
    out_path = OUTPUT_DIR / "Cine_Hubble_Tension.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Hubble Viz saved to: {out_path}")
    
    plt.close()

if __name__ == "__main__":
    generate_cine_hubble()
