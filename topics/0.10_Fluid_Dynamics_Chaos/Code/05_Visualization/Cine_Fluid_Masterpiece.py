"""
UET Topic 0.10: Fluid Dynamics Masterpiece (v1.0)
================================================
A premium, "Cine-Grade" visualization that brings UET Fluid Dynamics to life.
Features:
- High-Resolution Gradient Heatmaps (Pressure/Velocity)
- Glow-enhanced Streamlines (Flow Direction)
- Professional HUD & Scientific Annotation
- Smooth, Anti-aliased Rendering
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import sys



# --- ROBUST PATH FINDER ---


TOPIC_DIR = root_path / "docs" / "topics" / "0.10_Fluid_Dynamics_Chaos"
SAVE_DIR = TOPIC_DIR / "Result" / "01_Showcase"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Premium Style Setup
plt.style.use("dark_background")
CORAL_BLUE = "#00F2FF"
DEEP_PURPLE = "#7000FF"
NEON_LIME = "#CCFF00"
SPACE_BLACK = "#050505"




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_fluid_masterpiece():
    """Generates a high-end visual of a Step Flow (Backward Facing Step)."""
    print("🌊 Crafting Fluid Dynamics Masterpiece...")

    # 1. High-Res Grid
    nx, ny = 1200, 400
    x = np.linspace(0, 10, nx)
    y = np.linspace(-1, 1, ny)
    X, Y = np.meshgrid(x, y)

    # 2. Synthetic "Step Flow" Physics (Representing UET Omega Gradients)
    # Velocity Magnitude (Vorticity & Shear)
    velocity = np.zeros_like(X)

    # Inlet region
    inlet_mask = X < 2
    velocity[inlet_mask] = 1.0 - Y[inlet_mask] ** 2

    # Expansion region (Transition)
    transition_mask = (X >= 2) & (X < 5)
    t = (X[transition_mask] - 2) / 3.0
    velocity[transition_mask] = (1.0 - Y[transition_mask] ** 2) * (1.0 - 0.5 * t)

    # Vortex region (The "Cine" part)
    vortex_center_x, vortex_center_y = 3.5, -0.4
    r = np.sqrt((X - vortex_center_x) ** 2 + (Y - vortex_center_y) ** 2)
    vortex_effect = 0.6 * np.exp(-(r**2) / 0.5) * np.sin(3 * r)
    velocity += vortex_effect

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor(SPACE_BLACK)
    ax.set_facecolor(SPACE_BLACK)

    # Base Heatmap (Viral/Plasma Hybrid)
    im = ax.imshow(
        velocity, extent=[0, 10, -1, 1], origin="lower", cmap="turbo", aspect="auto", alpha=0.8
    )

    # 4. Streamlines (The "Glow" Effect)
    # Generate vector field for streamlines
    U = np.ones_like(X) * 0.8
    V = -0.1 * Y * np.exp(-((X - 3) ** 2)) + 0.3 * np.exp(-(r**2))

    # Plot streamlines with variable width and alpha
    strm = ax.streamplot(
        x, y, U, V, color="white", linewidth=0.8, density=1.2, arrowsize=1.0, alpha=0.4
    )

    # 5. Scientific Decoration (HUD)
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 1)
    ax.set_axis_off()

    # Add Borders
    rect = plt.Rectangle((0, -1), 10, 2, fill=False, edgecolor=CORAL_BLUE, linewidth=2, alpha=0.3)
    ax.add_patch(rect)

    # High-End Labels
    plt.text(
        0.2,
        0.9,
        "UET FLUID ENGINE v2.0",
        color=CORAL_BLUE,
        fontsize=12,
        weight="bold",
        transform=ax.transAxes,
    )
    plt.text(
        0.2,
        0.85,
        "DOMAIN: BACKWARD FACING STEP",
        color="white",
        fontsize=10,
        transform=ax.transAxes,
        alpha=0.7,
    )
    plt.text(
        0.2, 0.8, f"RESOLUTION: {nx}x{ny} GRID", color=NEON_LIME, fontsize=9, transform=ax.transAxes
    )

    # Physics Equation (Standard LaTeX)
    plt.text(
        7.5,
        0.9,
        r"$\Omega = \int [ V(C) + \frac{\kappa}{2}|\nabla C|^2 + \beta CI ] dx$",
        color=CORAL_BLUE,
        fontsize=14,
        transform=ax.transAxes,
        bbox=dict(facecolor="black", alpha=0.5, edgecolor=CORAL_BLUE),
    )

    # Colorbar (Customized)
    cbar = fig.colorbar(im, ax=ax, fraction=0.015, pad=0.04)
    cbar.set_label("Information Flux Intensity ($u_{mag}$)", color="white", fontsize=10)
    cbar.ax.yaxis.set_tick_params(color="white", labelcolor="white")

    # Save Output
    out_name = "Cine_Fluid_Masterpiece_Step.png"
    plt.savefig(SAVE_DIR / out_name, dpi=150, bbox_inches="tight", facecolor=SPACE_BLACK)
    plt.close()

    print(f"✅ MASTERPIECE SAVED: {SAVE_DIR / out_name}")


if __name__ == "__main__":
    generate_fluid_masterpiece()
