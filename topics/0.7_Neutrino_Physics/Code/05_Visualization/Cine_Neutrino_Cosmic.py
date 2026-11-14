"""
UET Cinematic Viz: Cosmic Neutrino Scaling (Topic 0.7)
======================================================
Visualizes the Universal Scaling Law: M ∝ 1/sqrt(rho).
Links Neutrino Mass generation to Galaxy Dark Matter Halos.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.7_Neutrino_Physics"
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

def generate_cosmic_viz():
    print("🚀 Generating UET Cosmic Neutrino Viz...")
    fig = plt.figure(figsize=(18, 9), facecolor=UET_BLACK)
    
    # --- 1. THE NEUTRINO SCALE (Micro) ---
    ax1 = fig.add_subplot(121, projection='3d', facecolor=UET_BLACK)
    
    # Visualize a Neutrino mass-generation "well"
    r = np.linspace(0.1, 5, 50)
    theta = np.linspace(0, 2*np.pi, 50)
    R, THETA = np.meshgrid(r, theta)
    X = R * np.cos(THETA)
    Y = R * np.sin(THETA)
    # Inverse sqrt(rho) potential shape
    Z = -1 / np.sqrt(R)
    
    ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.6)
    ax1.plot_wireframe(X, Y, Z, color=UET_CYAN, alpha=0.1, lw=0.5)
    # The "Ghostly" particle in the center
    ax1.scatter([0], [0], [-5], color=UET_CYAN, s=10, alpha=0.8, label="Neutrino Mass Scale")
    
    ax1.set_title("MICRO: Neutrino Mass Potential", color=UET_CYAN, fontsize=14)
    ax1.axis('off')

    # --- 2. THE GALAXY SCALE (Macro) ---
    ax2 = fig.add_subplot(122, projection='3d', facecolor=UET_BLACK)
    
    # Visualize a Galaxy Dark Matter Halo
    galaxy_r = np.linspace(0.1, 25, 50)
    G_R, G_THETA = np.meshgrid(galaxy_r, theta)
    GX = G_R * np.cos(G_THETA)
    GY = G_R * np.sin(G_THETA)
    # Same inverse sqrt scaling!
    GZ = -2 * np.sqrt(G_R) # Scaling the inverse
    
    ax2.plot_surface(GX, GY, GZ, cmap='magma', alpha=0.4)
    # The Galaxy disk in the center
    ax2.scatter(np.random.normal(0, 5, 200), np.random.normal(0, 5, 200), np.random.normal(0, 0.5, 200), 
                color=UET_GOLD, s=1, alpha=0.6, label="Baryonic Galaxy")
    
    ax2.set_title("MACRO: Dark Matter Halo (Ω-Field)", color=UET_MAGENTA, fontsize=14)
    ax2.axis('off')

    plt.suptitle("UET Universal Law: M ∝ ρ^(-0.5)\nUnifying Neutrinos and Galaxies", fontsize=22, color=UET_GOLD)
    
    out_path = OUTPUT_DIR / "Cine_Neutrino_Cosmic.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cosmic Neutrino Viz saved to: {out_path}")
    plt.close()

if __name__ == "__main__":
    generate_cosmic_viz()
