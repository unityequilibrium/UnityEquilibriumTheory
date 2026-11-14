"""
UET Cinematic Viz: Grand Unification (Topic 0.0)
================================================
Visualizes the "Grand Convergence" of fundamental forces.
Cyan: Electroweak/Strong (Quantum)
Magenta: Gravity (Macro/Geometry)
Gold: The UET Unity Core
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.0_Grand_Unification"
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

def generate_cine_unification():
    print("🚀 Generating UET Cinematic Grand Unification Viz...")
    
    fig = plt.figure(figsize=(12, 12), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # 1. Quantum Field (The Micro Spiral)
    t = np.linspace(0, 10, 500)
    q_x = 0.5 * t * np.cos(4 * t)
    q_y = 0.5 * t * np.sin(4 * t)
    q_z = t
    
    # 2. Gravity Field (The Macro Curve)
    g_x = -0.8 * t * np.cos(t)
    g_y = -0.8 * t * np.sin(t)
    g_z = t
    
    # 3. The Unity Path (The Convergence)
    u_x = np.linspace(2, 0, 500)
    u_y = np.linspace(-2, 0, 500)
    u_z = np.linspace(15, 0, 500)
    
    # Rendering with GLOW
    # Quantum Field
    ax.plot(q_x, q_y, q_z, color=UET_CYAN, alpha=0.1, lw=10)
    ax.plot(q_x, q_y, q_z, color=UET_CYAN, alpha=0.5, lw=2, label="Quantum Field")
    
    # Gravity Field
    ax.plot(g_x, g_y, g_z, color=UET_MAGENTA, alpha=0.1, lw=10)
    ax.plot(g_x, g_y, g_z, color=UET_MAGENTA, alpha=0.5, lw=2, label="Gravity Field")
    
    # The Core Convergence
    ax.plot(u_x, u_y, u_z, color=UET_GOLD, alpha=0.1, lw=15)
    ax.plot(u_x, u_y, u_z, color=UET_GOLD, alpha=0.8, lw=3, label="UET Unity Core")
    
    # Core Pulsar
    ax.scatter([0], [0], [0], color=UET_GOLD, s=1000, alpha=0.1)
    ax.scatter([0], [0], [0], color="white", s=100, alpha=0.6)
    
    # 4. Background Manifold (The "Sand Dune" Surface)
    x = np.linspace(-10, 10, 30)
    y = np.linspace(-10, 10, 30)
    X, Y = np.meshgrid(x, y)
    Z = 2 * np.sin(np.sqrt(X**2 + Y**2) / 2) # Fluctuating manifold
    ax.plot_wireframe(X, Y, Z, color=UET_MAGENTA, alpha=0.03, lw=0.5)

    # 5. Styling
    ax.set_title("UET Grand Unification: The Convergence of Forces", fontsize=18, color=UET_GOLD, pad=20)
    
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)
    ax.axis('off')
    
    ax.view_init(elev=20, azim=30)
    ax.legend(loc='lower left', frameon=False)
    
    out_path = OUTPUT_DIR / "Cine_Grand_Unification.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Cinematic Unification Viz saved to: {out_path}")
    
    plt.close()

if __name__ == "__main__":
    generate_unification_plot = generate_cine_unification # Alias
    generate_cine_unification()
