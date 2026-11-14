"""
🌌 UET Unified Galaxy-Black Hole Evolution Simulation
=====================================================
Hypothesis: Black Holes act as the "Informational Seed" (Anchor) for early galaxies.
Mechanisms:
1. CCBH Coupling: M_BH scales with Hubble expansion M_BH ∝ a^k (k ≈ 3.0).
2. Informational Glue: a₀ (acceleration scale) scales with H(z).
3. Co-evolution: Black hole growth creates a potential well that anchors baryonic matter.

Topic: 0.26_Cosmic_Dynamic_Frame
Author: Antigravity (UET Assistant)
Date: 2026-02-14
V1.1 (Moved & Refined)
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


import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# --- ENVIRONMENT SETUP ---
try:
    from docs import ROOT_PATH
except ImportError:
    # If not installed, find relative to this file
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        if (parent / "docs").exists():
            sys.path.insert(0, str(parent))
            from docs import ROOT_PATH

            break

# Injection of topic engine paths for robust imports
topic_03 = (
    ROOT_PATH / "docs" / "topics" / "0.3_Cosmology_Hubble_Tension" / "Code" / "01_Engine"
)
topic_02 = ROOT_PATH / "docs" / "topics" / "0.2_Black_Hole_Physics" / "Code" / "01_Engine"

for p in [topic_03, topic_02]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from Engine_Cosmology import UETCosmologyEngine
    from Engine_BlackHole import UETBlackHoleEngine
    from docs.core.uet_glass_box import UETPathManager
except ImportError as e:
    print(f"❌ SETUP ERROR: {e}")
    sys.exit(1)


def run_gvbh_unified_sim():
    print("🚀 Starting Unified Galaxy-Black Hole evolution simulation in Topic 0.26...")

    # Engines
    cosmo = UETCosmologyEngine()
    bh_engine = UETBlackHoleEngine()

    # Redshift range (from early universe to today)
    z_range = np.linspace(0, 15, 100)
    a = 1.0 / (1.0 + z_range)

    # 1. Calculate Black Hole Evolution (CCBH)
    k = bh_engine.solve_coupling_k()
    M_BH_init = 1e6  # Starting seed mass in M_sun

    # Define M_init at z=15 (start of reionization/seed era)
    a_start = 1.0 / (1.0 + 15)
    M_BH_z = [M_BH_init * ((1.0 / (1.0 + z)) / a_start) ** k for z in z_range]

    # 2. Calculate Informational Glue (a0 boost)
    a0_z = [cosmo.get_a0_at_redshift(z) for z in z_range]

    # 3. Model Galaxy Mass "Anchoring" Potential
    M_G_baseline = np.array(M_BH_z) * 1000  # Standard 1000x scaling

    # UET Effect: More mass anchored per unit BH seed in high-z due to a0 boost
    a0_0 = cosmo.get_a0_at_redshift(0)
    efficiency_boost = np.array(a0_z) / a0_0

    # Scaling factor for anchoring efficiency (empirical UET v0.8.7 model)
    M_G_uet = M_G_baseline * (efficiency_boost**0.5)

    # --- PLOTTING ---
    fig, ax1 = plt.subplots(figsize=(12, 7))

    color = "tab:red"
    ax1.set_xlabel("Redshift (z)")
    ax1.set_ylabel("Black Hole Mass (M_sun)", color=color)
    ax1.plot(z_range, M_BH_z, color=color, linewidth=2, label=f"BH Mass (CCBH k={k})")
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_yscale("log")
    ax1.invert_xaxis()  # High z on left

    ax2 = ax1.twinx()
    color = "tab:blue"
    ax2.set_ylabel("Galaxy Mass (M_sun)", color=color)
    ax2.plot(z_range, M_G_uet, color=color, linewidth=3, label="Galaxy Mass (UET Anchored)")
    ax2.plot(
        z_range,
        M_G_baseline,
        color="gray",
        linestyle="--",
        alpha=0.5,
        label="Baseline (No a0 Boost)",
    )
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.set_yscale("log")

    plt.title("UET Unified Evolution: Black Hole Seed vs Galaxy Anchoring", fontsize=14)
    fig.tight_layout()

    # Legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # Save Results to Topic 0.26 Result Dir
    try:
        output_dir = UETPathManager.get_result_dir(
            topic_id="0.26_Cosmic_Dynamic_Frame",
            experiment_name="Research_GvB_Evolution",
            pillar="03_Research",
            category="log",
        )
    except:
        output_dir = (
            ROOT_PATH
            / "docs"
            / "topics"
            / "0.26_Cosmic_Dynamic_Frame"
            / "Result"
            / "03_Research"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

    output_png = output_dir / "gvbh_unified_evolution.png"
    plt.savefig(output_png)

    print(f"✅ Simulation Complete. Figure saved to: {output_png}")
    print(f"📊 Summary at z=10:")
    idx_10 = np.abs(z_range - 10).argmin()
    print(f"   BH Mass: {M_BH_z[idx_10]:.2e} M_sun")
    print(f"   Galaxy Mass (UET): {M_G_uet[idx_10]:.2e} M_sun")
    print(f"   Efficiency Boost: {efficiency_boost[idx_10]:.2f}x")


if __name__ == "__main__":
    run_gvbh_unified_sim()
