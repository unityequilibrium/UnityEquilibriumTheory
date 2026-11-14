"""
UET Cinematic Viz: Quantum Research Suite (Topic 0.9)
=====================================================
A the complete overview of Topic 0.9 research scripts.
1. Bell Inequality (The S-Value Violation)
2. Qubit Mechanics (T1 Relaxation)
3. Double Slit (Wave Pattern)
4. DNA Tunneling (Frontal View)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup Paths
TOPIC_DIR = root_path / "docs" / "topics" / "0.9_Quantum_Nonlocality"
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

def generate_research_suite():
    print("🚀 Generating UET Quantum Research Suite...")
    fig = plt.figure(figsize=(20, 15), facecolor=UET_BLACK)

    # --- 1. BELL VIOLATION (Top Left) ---
    ax1 = fig.add_subplot(221, projection="3d", facecolor=UET_BLACK)
    theta = np.linspace(0, 2 * np.pi, 100)
    # Correlation curve wrapped on a cylinder
    z_bell = -np.cos(2 * theta)
    ax1.plot(np.cos(theta), np.sin(theta), z_bell, color=UET_CYAN, lw=3)
    ax1.text(0, 0, 1.5, "Bell S ≈ 2.828", color=UET_CYAN, ha="center", fontweight="bold")
    ax1.set_title("Research: Bell Inequality", color=UET_CYAN)
    ax1.axis("off")

    # --- 2. QUBIT DECAY (Top Right) ---
    ax2 = fig.add_subplot(222, facecolor=UET_BLACK)
    t = np.linspace(0, 10, 100)
    y_decay = np.exp(-t / 3)
    ax2.plot(t, y_decay, color=UET_MAGENTA, lw=3)
    ax2.fill_between(t, y_decay, color=UET_MAGENTA, alpha=0.1)
    ax2.set_title("Research: Qubit T1 Relaxation", color=UET_MAGENTA)
    ax2.set_xlabel("Time (μs)")
    ax2.set_ylabel("Fidelity")

    # --- 3. DOUBLE SLIT (Bottom Left) ---
    ax3 = fig.add_subplot(223, facecolor=UET_BLACK)
    x = np.linspace(-10, 10, 500)
    intensity = (np.cos(x) ** 2) * (np.sinc(x / 5) ** 2)
    ax3.plot(x, intensity, color=UET_GOLD, lw=2)
    ax3.set_title("Research: Double Slit Interference", color=UET_GOLD)
    ax3.axis("off")

    # --- 4. DNA TUNNELING FRONT-ON (Bottom Right) ---
    ax4 = fig.add_subplot(224, projection="3d", facecolor=UET_BLACK)
    # Simplified Front View
    x_bar = np.linspace(-2, 2, 50)
    z_bar = 2 * np.exp(-(x_bar**2) / 0.5)
    ax4.plot(x_bar, np.zeros_like(x_bar), z_bar, color=UET_MAGENTA, lw=3)
    # Pulse
    ax4.scatter([-1.5, 1.5], [0, 0], [0, 0], color=UET_CYAN, s=100)
    ax4.set_title("Research: DNA Proton Tunneling", color=UET_CYAN)
    ax4.view_init(elev=0, azim=-90)
    ax4.axis("off")

    plt.suptitle(
        "UET Topic 0.9: Quantum Research Overview\n'Make the Invisible, Visible'",
        fontsize=24,
        color=UET_GOLD,
    )

    out_path = OUTPUT_DIR / "Cine_Quantum_Research_Suite.png"
    plt.savefig(out_path, dpi=200, facecolor=UET_BLACK)
    print(f"✅ Quantum Research Suite saved to: {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_research_suite()
