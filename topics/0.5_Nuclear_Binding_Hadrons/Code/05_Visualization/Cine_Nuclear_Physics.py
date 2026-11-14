"""
UET Cinematic Viz: Nuclear & Hadron Physics (Topic 0.5)
======================================================
Visualizes the Nuclear "Valley of Stability" and Proton Structure.
Cyan: The Valley of Stability Surface
Gold: The Stable Nuclei (The Backbone)
Magenta: Quark Confinement (Y-Strings)
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
plt.style.use('dark_background')
UET_CYAN = "#00e5ff"    # Stability Surface
UET_MAGENTA = "#ff00ff" # Confinement (Quarks)
UET_GOLD = "#ffd700"    # Stable Nuclei
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_cine_nuclear():
    print("🚀 Generating UET Cinematic Nuclear & Hadron Viz...")
    
    fig = plt.figure(figsize=(15, 10), facecolor=UET_BLACK)
    
    # --- SUBPLOT 1: The Valley of Stability (Macro View) ---
    ax1 = fig.add_subplot(121, projection='3d', facecolor=UET_BLACK)
    
    # Z (Protons), N (Neutrons)
    z_vals = np.linspace(1, 100, 50)
    n_vals = np.linspace(1, 150, 50)
    Z_grid, N_grid = np.meshgrid(z_vals, n_vals)
    A_grid = Z_grid + N_grid
    
    # Semi-Empirical Mass Formula (Simplified for Viz)
    # B/A approx a_vol - a_surf/A^1/3 - a_coul*Z^2/A^4/3 - a_asym*(N-Z)^2/A^2
    B_per_A = 15.7 - 17.8/(A_grid**(1/3)) - 0.71*(Z_grid**2)/(A_grid**(4/3)) - 23.7*((N_grid-Z_grid)**2)/(A_grid**2)
    B_per_A = np.clip(B_per_A, 0, 9) # Binding energy is positive
    
    # Plot the stability surface
    surf = ax1.plot_surface(Z_grid, N_grid, B_per_A, cmap='magma', alpha=0.6, 
                           antialiased=True, rstride=2, cstride=2)
    ax1.plot_wireframe(Z_grid, N_grid, B_per_A, color=UET_CYAN, alpha=0.1, lw=0.5)

    # Highlight the "Backbone of Truth" (Stable Nuclei)
    # Approx N = Z for light, N = 1.5Z for heavy
    stable_z = np.linspace(1, 100, 20)
    stable_n = stable_z * (1 + (stable_z/200)) # Simple empirical fit
    # Calculate B/A for stable line
    stable_a = stable_z + stable_n
    stable_b = 15.7 - 17.8/(stable_a**(1/3)) - 0.71*(stable_z**2)/(stable_a**(4/3)) - 23.7*((stable_n-stable_z)**2)/(stable_a**2)
    
    ax1.plot(stable_z, stable_n, stable_b, color=UET_GOLD, lw=4, alpha=0.9, label="Valley of Stability")
    ax1.plot(stable_z, stable_n, stable_b, color=UET_GOLD, lw=10, alpha=0.2) # Glow
    
    ax1.set_title("The Nuclear Landscape", color=UET_GOLD, fontsize=16)
    ax1.set_xlabel("Protons (Z)", color=UET_CYAN)
    ax1.set_ylabel("Neutrons (N)", color=UET_CYAN)
    ax1.set_zlabel("Binding Energy (B/A)", color=UET_GOLD)
    ax1.view_init(elev=35, azim=-140)
    ax1.grid(False)

    # --- SUBPLOT 2: The Proton Structure (Micro View) ---
    ax2 = fig.add_subplot(122, projection='3d', facecolor=UET_BLACK)
    
    # 3 Quarks (U, U, D)
    # Position them in a triangle
    quark_pos = np.array([
        [1, 0, 0],    # U1
        [-0.5, 0.86, 0], # U2
        [-0.5, -0.86, 0] # D
    ])
    
    quark_colors = [UET_CYAN, UET_CYAN, UET_MAGENTA]
    quark_labels = ["Up", "Up", "Down"]
    
    # Draw Gluon "Y-Strings" (Confinement)
    # Center point (Neutral Information Hub)
    center = np.array([0, 0, 0])
    for i in range(3):
        # Line from center to quark
        ax2.plot([center[0], quark_pos[i, 0]], [center[1], quark_pos[i, 1]], [center[2], quark_pos[i, 2]], 
                 color=UET_MAGENTA, lw=3, alpha=0.8, ls='--')
        # Glow
        ax2.plot([center[0], quark_pos[i, 0]], [center[1], quark_pos[i, 1]], [center[2], quark_pos[i, 2]], 
                 color=UET_MAGENTA, lw=12, alpha=0.1)
        
        # Draw the Quark sphere
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        sphere_r = 0.3
        sx = quark_pos[i, 0] + sphere_r * np.outer(np.cos(u), np.sin(v))
        sy = quark_pos[i, 1] + sphere_r * np.outer(np.sin(u), np.sin(v))
        sz = quark_pos[i, 2] + sphere_r * np.outer(np.ones(np.size(u)), np.cos(v))
        ax2.plot_surface(sx, sy, sz, color=quark_colors[i], alpha=0.7)
        ax2.text(quark_pos[i, 0], quark_pos[i, 1], quark_pos[i, 2] + 0.5, quark_labels[i], 
                 color='white', ha='center', fontsize=10, fontweight='bold')

    # Add Information Cloud (The Proton bag)
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    bag_r = 1.8
    bx = bag_r * np.outer(np.cos(u), np.sin(v))
    by = bag_r * np.outer(np.sin(u), np.sin(v))
    bz = bag_r * np.outer(np.ones(np.size(u)), np.cos(v))
    ax2.plot_wireframe(bx, by, bz, color=UET_CYAN, alpha=0.03, lw=0.5)

    ax2.set_title("Inside the Proton (uud)", color=UET_CYAN, fontsize=16)
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)
    ax2.set_zlim(-2, 2)
    ax2.axis('off')
    ax2.view_init(elev=20, azim=45)

    plt.suptitle("UET Nuclear & Hadron Physics: The Bind of Truth", fontsize=22, color=UET_GOLD, y=0.95)
    plt.tight_layout()
    
    out_path = OUTPUT_DIR / "Cine_Nuclear_Physics.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Nuclear Viz saved to: {out_path}")
    
    plt.close()

if __name__ == "__main__":
    generate_cine_nuclear()
