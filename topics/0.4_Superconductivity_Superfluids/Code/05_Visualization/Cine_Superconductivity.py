"""
UET Cinematic Viz: Superconductivity (Topic 0.4)
================================================
Visualizes the Meissner Effect and Quantum Vortices.
Cyan: The Superconducting Field (Condensate)
Gold: Magnetic Field Lines (Expelled)
Magenta: Quantum Vortices (Information Pinning)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.4_Superconductivity_Superfluids"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use('dark_background')
UET_CYAN = "#00e5ff"    # Superconductor
UET_MAGENTA = "#ff00ff" # Vortices
UET_GOLD = "#ffd700"    # Magnetic Field
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_cine_supercond():
    print("🚀 Generating UET Cinematic Superconductivity Viz...")
    
    fig = plt.figure(figsize=(12, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # 1. The Superconducting Base (A circular disk)
    theta = np.linspace(0, 2*np.pi, 100)
    r = np.linspace(0, 5, 20)
    T, R = np.meshgrid(theta, r)
    X = R * np.cos(T)
    Y = R * np.sin(T)
    Z = -0.5 * np.exp(-(R**2)/10) # Slight curvature
    
    ax.plot_surface(X, Y, Z, color=UET_CYAN, alpha=0.3, rstride=1, cstride=1, linewidth=0)
    # Wireframe for structure
    ax.plot_wireframe(X, Y, Z, color=UET_CYAN, alpha=0.1, lw=0.5)
    
    # 2. The Floating Magnet (Golden Sphere/Cube)
    # Positioned at Z=4
    mag_x = 0
    mag_y = 0
    mag_z = 5
    ax.scatter([mag_x], [mag_y], [mag_z], color=UET_GOLD, s=1500, alpha=0.8, edgecolors='white')
    ax.scatter([mag_x], [mag_y], [mag_z], color="white", s=2000, alpha=0.1) # Glow
    
    # 3. Magnetic Field Lines (Expelled - The Meissner Effect)
    # Lines originate from the magnet but bend AWAY from the disk
    for angle in np.linspace(0, 2*np.pi, 12):
        # Parametric curve for a field line bending around the disk
        s = np.linspace(0, 1, 100)
        # Radial displacement
        r_off = 3 * s + 0.5
        # Vertical displacement bending outward
        line_x = r_off * np.cos(angle)
        line_y = r_off * np.sin(angle)
        line_z = mag_z - (mag_z + 2) * s * (1 - np.exp(-r_off/2))
        
        ax.plot(line_x, line_y, line_z, color=UET_GOLD, alpha=0.4, lw=1.5)
        # Glow layer
        ax.plot(line_x, line_y, line_z, color=UET_GOLD, alpha=0.05, lw=10)

    # 4. Quantum Vortices (Pinning)
    # Tornado-like spirals in the center of the disk
    vortex_centers = [(1.5, 1.5), (-1.8, 0.5), (0.5, -2.0)]
    for vx, vy in vortex_centers:
        vz = np.linspace(-0.5, 2, 50)
        v_angle = np.linspace(0, 4*np.pi, 50)
        v_r = 0.2 * (1 - vz/3)
        ax.plot(vx + v_r * np.cos(v_angle), vy + v_r * np.sin(v_angle), vz, 
                color=UET_MAGENTA, alpha=0.8, lw=2)
        # Core Glow
        ax.scatter([vx], [vy], [0], color=UET_MAGENTA, s=50, alpha=0.5)

    # 5. Information Particles (Frictionless Flow)
    # Moving particles around a vortex
    for _ in range(20):
        p_r = np.random.uniform(2, 4)
        p_angle = np.random.uniform(0, 2*np.pi)
        px = p_r * np.cos(p_angle)
        py = p_r * np.sin(p_angle)
        pz = -0.4
        ax.scatter([px], [py], [pz], color="white", s=2, alpha=0.5)
        # Add a trail
        trail_angle = np.linspace(p_angle, p_angle + 0.5, 10)
        ax.plot(p_r * np.cos(trail_angle), p_r * np.sin(trail_angle), [pz]*10, 
                color=UET_CYAN, alpha=0.3, lw=1)

    # Styling
    ax.set_title("UET Superconductivity: Magnetic Field Expulsion", fontsize=18, color=UET_GOLD, pad=20)
    
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.axis('off')
    
    ax.view_init(elev=25, azim=45)
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='white', label='Magnet (Source)', markerfacecolor=UET_GOLD, markersize=10, ls=''),
        Line2D([0], [0], color=UET_GOLD, lw=2, label='Expelled Magnetic Flux'),
        Line2D([0], [0], color=UET_CYAN, lw=4, label='Superconducting Condensate'),
        Line2D([0], [0], color=UET_MAGENTA, lw=2, label='Quantum Vortices (Pinning)')
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=False, fontsize=10)
    
    out_path = OUTPUT_DIR / "Cine_Superconductivity.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Supercond Viz saved to: {out_path}")
    
    plt.close()

if __name__ == "__main__":
    generate_cine_supercond()
