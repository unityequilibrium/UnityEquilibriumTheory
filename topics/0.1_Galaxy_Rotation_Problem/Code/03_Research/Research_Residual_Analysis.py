"""
Research: Residual Analysis
===========================
Diagnose the direction (Over/Under) of UET errors in Dwarf Galaxies.
Input: sparc_data.json
Output: Table of Residuals for Failed Galaxies.
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


import numpy as np
import json
import math
from pathlib import Path


# --- ROBUST PATH FINDER ---


try:
    from docs.core.uet_glass_box import UETPathManager
except ImportError as e:
    print(f"Import Error: {e}")

# Import Engine
# Engine is in ../01_Engine/Engine_Galaxy_V3.py relative to this script
# Use topic-relative path if possible
topic_dir = Path(__file__).resolve().parent.parent
engine_dir = topic_dir / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

import Engine_Galaxy_V3



UETGalaxyEngine = Engine_Galaxy_V3.UETGalaxyEngine
GalaxyParams = Engine_Galaxy_V3.GalaxyParams




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def calculate_surface_density(mass, radius):
    return mass / (math.pi * (radius**2) + 1e-10)


def run_analysis():
    print("🔍 RUNNING RESIDUAL DIAGNOSTICS")
    print("=" * 80)
    print(
        f"{'Galaxy':<15} {'Type':<10} {'LogRho':<8} | {'V_obs':<8} {'V_pred':<8} | {'Diff':<8} {'Status'}"
    )
    print("-" * 80)

    if not root_path:
        print("CRITICAL: Root path not found")
        return

    data_path = (
        root_path
        / "docs/topics/0.1_Galaxy_Rotation_Problem/Data/03_Research/sparc_data.json"
    )
    if not data_path.exists():
        # Fallback
        data_path = root_path / "Data/03_Research/sparc_data.json"
    with open(data_path, "r") as f:
        galaxies = json.load(f)

    fail_count = 0
    under_predict = 0
    over_predict = 0

    low_density_fails = []

    for g in galaxies:
        m_disk = g["M_disk_Msun"]
        r_disk = g["R_disk_kpc"]
        # Legacy Logic: 10% Bulge
        params = GalaxyParams(
            mass_disk=m_disk,
            radius_disk=r_disk,
            mass_bulge=0.1 * m_disk,
            galaxy_type=g["type"],
        )
        engine = UETGalaxyEngine(params)

        v_obs = g["v_obs"]
        v_pred = engine.compute_velocity_at_radius(g["R_kpc"])

        diff = v_pred - v_obs
        error_pct = (abs(diff) / (v_obs + 1e-10)) * 100

        rho_surf = calculate_surface_density(m_disk, r_disk)
        log_rho = np.log10(rho_surf + 1e-10)

        status = "PASS"
        if error_pct > 15:
            status = "FAIL"
            fail_count += 1
            if diff < 0:
                under_predict += 1
            else:
                over_predict += 1

            # Print only FAILs for brevity if list is long, or focused check
            if log_rho < 8.11:  # The AI Threshold
                low_density_fails.append(diff)
                print(
                    f"{g['name']:<15} {g['type']:<10} {log_rho:<8.2f} | {v_obs:<8.1f} {v_pred:<8.1f} | {diff:<8.1f} {status}"
                )

    print("-" * 80)
    print(f"Total Fails: {fail_count}/{len(galaxies)}")
    print(f"Under-Predictions (Need Boost): {under_predict}")
    print(f"Over-Predictions (Need Damping): {over_predict}")

    if len(low_density_fails) > 0:
        avg_low_rho_diff = np.mean(low_density_fails)
        print(
            f"\nLow Density (LogRho < 8.11) Mean Residual: {avg_low_rho_diff:.2f} km/s"
        )
        if avg_low_rho_diff < 0:
            print(">> CONCLUSION: Dwarfs are UNDER-PREDICTED. We need a BOOST.")
        else:
            print(">> CONCLUSION: Dwarfs are OVER-PREDICTED. We need DAMPING.")

    print("\nRESULT: PASS (Analysis Complete)")


if __name__ == "__main__":
    run_analysis()
