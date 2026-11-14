"""
UET Cinematic Viz: Muon g-2 Anomaly (Topic 0.8)
==============================================
Visualizes the Muon Magnetic Precession and the UET Information Boost.
Cyan: The Muon Spin Direction
Magenta: The Excess "Anomalous" Field
Gold: The Muon Path / Storage Ring
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.8_Muon_g2_Anomaly"
OUTPUT_DIR = TOPIC_DIR / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Aesthetics
plt.style.use('dark_background')
UET_CYAN = "#00e5ff"    # Spin
UET_MAGENTA = "#ff00ff" # Anomaly
UET_GOLD = "#ffd700"    # Path
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_muon_viz():
    print("🚀 Generating UET Muon g-2 Cinematic Viz...")
    
    fig = plt.figure(figsize=(15, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # 1. The Storage Ring (Path)
    theta = np.linspace(0, 10 * np.pi, 1000)
    r_ring = 10
    height = 2
    # Muon Spiraling Path (A few orbits)
    x = r_ring * np.cos(theta)
    y = r_ring * np.sin(theta)
    z = (theta / (10*np.pi)) * height
    
    ax.plot(x, y, z, color=UET_GOLD, lw=2, alpha=0.5, label="Muon Storage Trajectory")
    
    # 2. Spin Precession (The Wobble)
    # Every 100 points, draw a spin vector
    for i in range(0, 1000, 100):
        # Basis vector
        pos = np.array([x[i], y[i], z[i]])
        # Precession angle (Anomaly makes it lag behind the velocity vector)
        # g-factor determines how fast spin rotates vs velocity
        # Anomaly a_mu is the difference
        precession_angle = 0.5 * theta[i] 
        spin_v = np.array([np.cos(precession_angle), np.sin(precession_angle), 0.5]) * 2
        
        ax.quiver(pos[0], pos[1], pos[2], spin_v[0], spin_v[1], spin_v[2], 
                  color=UET_CYAN, arrow_length_ratio=0.3, lw=2, alpha=0.9)
        
        # 3. Vacuum Loops (The Anomaly Source)
        # Small loops around the muon
        loop_phi = np.linspace(0, 2*np.pi, 20)
        lx = pos[0] + 0.5 * np.cos(loop_phi)
        ly = pos[1] + 0.5 * np.sin(loop_phi)
        lz = pos[2] + 0.2 * np.sin(loop_phi * 2)
        ax.plot(lx, ly, lz, color=UET_MAGENTA, alpha=0.4, lw=1)

    # 4. The UET Field (Wireframe background)
    xg, yg = np.meshgrid(np.linspace(-15, 15, 10), np.linspace(-15, 15, 10))
    zg = -5 + 0.1 * (xg**2 + yg**2) / 10
    ax.plot_wireframe(xg, yg, zg, color=UET_MAGENTA, alpha=0.05, lw=0.5)

    # Annotations
    ax.text(0, 0, 5, "Magnetic Moment: g-2", color=UET_GOLD, ha='center', fontsize=15, fontweight='bold')
    ax.text(10, 0, 3, "Δa_μ ≈ 2.51e-9", color=UET_MAGENTA, ha='center', fontsize=12)
    ax.text(-10, 0, 3, "Spin Precession (ω_a)", color=UET_CYAN, ha='center', fontsize=12)

    # Styling
    ax.set_title("UET Muon g-2: Information Coupling in the Quantum Vacuum", fontsize=20, color=UET_CYAN, pad=20)
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-5, 8)
    ax.axis('off')
    ax.view_init(elev=30, azim=45)
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=UET_GOLD, lw=2, label='Muon Trajectory'),
        Line2D([0], [0], color=UET_CYAN, marker='>', markersize=10, label='Spin Vector (Precession)'),
        Line2D([0], [0], color=UET_MAGENTA, lw=1, ls='--', label='Vacuum Info Loops (g-2 Burst)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=False)
    
    out_path = OUTPUT_DIR / "Cine_Muon_Anomaly.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Muon g-2 Cinematic Viz saved to: {out_path}")
    plt.close()

if __name__ == "__main__":
    generate_muon_viz()
