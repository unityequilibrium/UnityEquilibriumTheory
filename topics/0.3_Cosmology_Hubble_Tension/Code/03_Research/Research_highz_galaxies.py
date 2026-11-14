"""
JWST High-Redshift Galaxy Dynamics Test (UET Prediction)
========================================================

Test the falsifiable prediction that a₀ scales with H(z):
    a₀(z) = BETA_CI * c * H(z)
Where:
    H(z) = H₀ * sqrt(Ω_m(1+z)³ + Ω_Λ)

This script compares rotation curves for the same galaxy parameters
at z=0 vs z=5 to show the expected 'UET Boost' in the early universe.

Updated for UET V3.0
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
import os
import sys
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH


# Setup local imports for Topic 0.3 and Topic 0.1
topic_path = root_path / "docs" / "topics" / "0.3_Cosmology_Hubble_Tension"
engine_path = topic_path / "Code" / "01_Engine"
galaxy_engine_path = (
    root_path / "docs" / "topics" / "0.1_Galaxy_Rotation_Problem" / "Code" / "01_Engine"
)

if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))
if str(galaxy_engine_path) not in sys.path:
    sys.path.insert(0, str(galaxy_engine_path))

try:
    from Engine_Cosmology import UETCosmologyEngine
    from Engine_Galaxy_V3 import UETGalaxyEngine, GalaxyParams
    from docs.core.uet_parameters import G_GALACTIC as G_astro
except ImportError as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


# Standardized UET Root Path
from docs import ROOT_PATH

root_path = ROOT_PATH


def simulate_highz_prediction(z_target=5.0):
    print(f"🚀 Simulating UET Predictions for Redshift z = {z_target}")
    print("-" * 50)

    # 1. Instantiate the Cosmology Engine to get H(z) info
    cosmo_engine = UETCosmologyEngine()
    a0_z0 = cosmo_engine.get_a0_at_redshift(0.0)
    a0_zh = cosmo_engine.get_a0_at_redshift(z_target)

    print(f"a0 (z=0): {a0_z0:.4f} (km/s)²/kpc")
    print(f"a0 (z={z_target}): {a0_zh:.4f} (km/s)²/kpc (Boost: {a0_zh/a0_z0:.2f}x)")

    # 2. Setup Galaxy Parameters (Generic LSB Disk)
    M_disk = 1e9  # M_sun
    R_disk = 3.0  # kpc
    R = np.linspace(0.1, 15, 100)

    # 3. Instantiate Galaxy Engine for z=0
    params_z0 = GalaxyParams(mass_disk=M_disk, radius_disk=R_disk, mass_bulge=0, redshift=0.0)
    engine_z0 = UETGalaxyEngine(params_z0)
    V_z0 = engine_z0.compute_curve(R)

    # 4. Instantiate Galaxy Engine for z_target
    params_zh = GalaxyParams(mass_disk=M_disk, radius_disk=R_disk, mass_bulge=0, redshift=z_target)
    engine_zh = UETGalaxyEngine(params_zh)
    V_zh = engine_zh.compute_curve(R)

    plt.figure(figsize=(10, 6))
    plt.plot(R, V_z0, "b-", label="z = 0 (Current Universe)")
    plt.plot(R, V_zh, "r--", label=f"z = {z_target} (JWST Era)")
    plt.fill_between(R, V_z0, V_zh, color="red", alpha=0.1, label="UET Evolutionary Boost")

    plt.title(f"UET Prediction: Evolution of Rotation Curves (a₀ ∝ H(z))")
    plt.xlabel("Radius (kpc)")
    plt.ylabel("Circular Velocity (km/s)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Updated to use UETPathManager for output
    try:
        from docs.core.uet_glass_box import UETPathManager

        output_dir = UETPathManager.get_result_dir(
            topic_id="0.3_Cosmology_Hubble_Tension",
            experiment_name="Research_highz_galaxies",
            pillar="03_Research",
            category="log",
        )
    except ImportError:
        # Fallback if running standalone without core
        output_dir = Path("Result")
        output_dir.mkdir(exist_ok=True)

    output_png = output_dir / "highz_evolution_prediction.png"
    plt.savefig(output_png)
    print(f"\nPrediction figure saved to {output_png}")
    print("Finding: UET predicts that high-z galaxies will show significantly higher ")
    print("rotation velocities for the same baryonic mass than local galaxies.")


if __name__ == "__main__":
    simulate_highz_prediction(z_target=5.0)
