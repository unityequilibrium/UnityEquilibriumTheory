"""
Research_Galaxy_Curve_Social.py
-------------------------------
Topic: 0.1 Galaxy Rotation Problem
Purpose: Generate a "Viral-Ready" visualization comparing Standard Physics vs UET.
Style: Dark Mode / Neon for Social Media (FB/X/TikTok).

Logic:
1. Simulate a standard Spiral Galaxy (Mass ~ 5e10 Solar Masses).
2. Compute Newtonian Velocity (Red Line - Falls off).
3. Compute UET Velocity (Green Line - Flat/Stable).
4. Annotate with clear, non-academic text.
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER ---


try:
    # Import the Engine directly for accurate physics
    sys.path.append(
        str(
            root_path
            / "docs"
            / "topics"
            / "0.1_Galaxy_Rotation_Problem"
            / "Code"
            / "01_Engine"
        )
    )
    from Engine_Galaxy_V3 import UETGalaxyEngine, GalaxyParams
    from docs.core.uet_glass_box import UETPathManager
except ImportError as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


# Standardized UET Root Path


def generate_social_plot():
    print("🎨 Generating Social Media Visual: Galaxy Rotation...")

    # 1. Define Representsative Galaxy (Standard Spiral like Milky Way/Andromeda)
    # Using SPARC-like parameters
    mass_disk = 5.0e10  # Solar Masses
    radius_disk = 3.5  # kpc (Scale Length)
    # No Bulge for simplicity to show pure disk effect, or small bulge
    mass_bulge = 0.5e10

    params = GalaxyParams(
        mass_disk=mass_disk, radius_disk=radius_disk, mass_bulge=mass_bulge, galaxy_type="spiral"
    )

    engine = UETGalaxyEngine(params)

    # 2. Compute Curves
    radii = np.linspace(0.5, 25, 100)  # 0 to 25 kpc
    v_newton = []
    v_uet = []

    for r in radii:
        # Standard Newton: only baryonic mass, no dark matter
        # V^2 = GM/r
        # We need the cumulative mass at radius r
        # Approximation for disk: M(r) = M_total * (1 - exp(-r/Rd) * (1 + r/Rd))
        # This is strictly exponential disk mass profile
        y = r / radius_disk
        mass_enclosed_disk = mass_disk * (1 - np.exp(-y) * (1 + y))
        mass_enclosed = mass_enclosed_disk + mass_bulge  # Simplified point bulge

        v_sq_newton = (4.30e-6 * mass_enclosed) / r  # G in units for km/s, kpc, Msun
        v_n = np.sqrt(abs(v_sq_newton))
        v_newton.append(v_n)

        # UET Calculation
        v_u = engine.compute_velocity_at_radius(r)
        v_uet.append(v_u)

    # 3. Plotting (Dark Mode)
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Neon Colors
    color_fail = "#ef476f"  # Neon Red
    color_pass = "#06d6a0"  # Neon Green
    color_text = "#ffffff"

    # Plot Lines
    ax.plot(
        radii,
        v_newton,
        color=color_fail,
        linestyle="--",
        linewidth=2,
        label="Standard Physics (Newton)\nNeeds 'Dark Matter' to fix",
    )
    ax.plot(
        radii,
        v_uet,
        color=color_pass,
        linewidth=4,
        label="UET (Information Field)\nMatches Reality Naturally",
    )

    # Shade the gap (The "Dark Matter" Illusion)
    ax.fill_between(radii, v_newton, v_uet, color="gray", alpha=0.1, label="The 'Dark Matter' Gap")

    # Annotations
    ax.set_title(
        "THE GALAXY ROTATION PROBLEM", fontsize=16, color=color_text, weight="bold", pad=20
    )
    ax.set_xlabel("Distance from Center (kpc)", fontsize=12, color="gray")
    ax.set_ylabel("Rotation Speed (km/s)", fontsize=12, color="gray")

    # Callout Arrows
    # Point at the drop
    ax.annotate(
        "Standard Math FAILS here\n(Galaxy flies apart)",
        xy=(15, v_newton[60]),
        xytext=(15, v_newton[60] - 50),
        arrowprops=dict(facecolor=color_fail, shrink=0.05),
        color=color_fail,
        fontsize=10,
        ha="center",
    )

    # Point at the stability
    ax.annotate(
        "UET Holds it Together\n(Fluid Equilibrium)",
        xy=(20, v_uet[80]),
        xytext=(15, v_uet[80] + 40),
        arrowprops=dict(facecolor=color_pass, shrink=0.05),
        color=color_pass,
        fontsize=10,
        ha="center",
        weight="bold",
    )

    # Grid and Spines
    ax.grid(True, alpha=0.1, color="gray", linestyle=":")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("gray")
    ax.spines["left"].set_color("gray")

    ax.legend(fontsize=10, loc="lower right")

    # Save
    # Save to Standardized Showcase via Engine Logic
    output_dir = UETPathManager.get_result_dir(
        topic_id="0.1", experiment_name="Social_Curve", category="showcase"
    )
    output_path = output_dir / "Research_Galaxy_Curve_Social.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Image Saved to Showcase: {output_path}")
    return True


if __name__ == "__main__":
    generate_social_plot()
