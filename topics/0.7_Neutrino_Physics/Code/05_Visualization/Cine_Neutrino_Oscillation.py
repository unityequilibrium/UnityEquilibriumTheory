"""
UET Cinematic Viz: Neutrino Oscillation (Topic 0.7)
===================================================
Visualizes 3-flavor oscillation (PMNS) as a color-shifting wave.
Cyan: Electron Neutrino
Magenta: Muon Neutrino
Gold: Tau Neutrino
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
UET_CYAN = "#00e5ff"    # nu_e
UET_MAGENTA = "#ff00ff" # nu_mu
UET_GOLD = "#ffd700"    # nu_tau
UET_BLACK = "#000000"



# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_oscillation_viz():
    print("🚀 Generating UET Neutrino Oscillation Viz...")
    fig = plt.figure(figsize=(15, 10), facecolor=UET_BLACK)
    ax = fig.add_subplot(111, projection='3d', facecolor=UET_BLACK)
    
    # 1. The Path (Neutrino propagation)
    z = np.linspace(0, 20, 1000)
    
    # 3-Flavor Probabilities (Simplified for Viz)
    # L/E phase
    phase = 0.5 * z
    p_e = np.cos(phase)**2 * 0.8 + 0.1
    p_mu = np.sin(phase)**2 * 0.7 + 0.1
    p_tau = 1.0 - p_e - p_mu
    
    # Map probabilities to RGB colors
    colors = np.zeros((len(z), 3))
    # nu_e (Cyan) -> [0, 1, 1]
    # nu_mu (Magenta) -> [1, 0, 1]
    # nu_tau (Gold) -> [1, 0.8, 0]
    
    for i in range(len(z)):
        c = p_e[i]*np.array([0, 0.9, 1.0]) + \
            p_mu[i]*np.array([1.0, 0, 1.0]) + \
            p_tau[i]*np.array([1.0, 0.8, 0])
        colors[i] = np.clip(c, 0, 1)

    # Drawing the Wave Function (A spiral)
    r = 2.0
    freq = 2.0
    x = r * np.cos(freq * z)
    y = r * np.sin(freq * z)
    
    # Plotting segment by segment for color variation
    for i in range(len(z)-1):
        ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], color=colors[i], lw=3, alpha=0.8)
        # Glow
        ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], color=colors[i], lw=10, alpha=0.05)

    # 2. Add Flavor Labels
    ax.text(x[0], y[0], z[0]-1, "ν_e Source", color=UET_CYAN, ha='center', fontsize=12, fontweight='bold')
    
    # Mixing Angle Indicators (Theoretical Symmetries)
    ax.text(5, 5, 2, "θ₁₂ ≈ 30° (π/6)", color=UET_CYAN, alpha=0.5)
    ax.text(-5, 5, 10, "θ₂₃ ≈ 45° (Maximal)", color=UET_MAGENTA, alpha=0.5)
    
    # Styling
    ax.set_title("UET Neutrino: The Flavor Dance (PMNS Interference)", fontsize=18, color=UET_GOLD, pad=20)
    ax.set_box_aspect([1, 1, 3])
    ax.axis('off')
    ax.view_init(elev=15, azim=45)
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=UET_CYAN, lw=4, label='ν_e (Electron)'),
        Line2D([0], [0], color=UET_MAGENTA, lw=4, label='ν_μ (Muon)'),
        Line2D([0], [0], color=UET_GOLD, lw=4, label='ν_τ (Tau)')
    ]
    ax.legend(handles=legend_elements, loc='lower left', frameon=False)
    
    out_path = OUTPUT_DIR / "Cine_Neutrino_Oscillation.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Neutrino Oscillation Viz saved to: {out_path}")
    plt.close()

if __name__ == "__main__":
    generate_oscillation_viz()
