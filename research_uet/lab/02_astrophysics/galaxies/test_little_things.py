"""
🌌 LITTLE THINGS Dwarf Galaxy Test
====================================
Testing UET + DC14 model against LITTLE THINGS dwarf galaxies.

Compares:
1. UET v3 (NFW-based)
2. UET v5 (DC14 cored profile)
3. Observed velocities

Uses high-resolution data from Oh et al. (2015).

Updated for UET V3.0
"""

import numpy as np
import sys

# Import from UET V3.0 Master Equation
import sys
from pathlib import Path

_root = Path(__file__).parent
while _root.name != "research_uet" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from research_uet.core.uet_master_equation import (
        UETParameters,
        SIGMA_CRIT,
        strategic_boost,
        potential_V,
        KAPPA_BEKENSTEIN,
    )
except ImportError:
    pass  # Use local definitions if not available

import os

# Add data paths - go up to research_uet then into data
_data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "02_astrophysics")
sys.path.insert(0, os.path.abspath(_data_path))

try:
    from little_things_data import LITTLE_THINGS_GALAXIES, save_data
    from di_cintio_profile import dc14_rotation_velocity, dc14_concentration, dc14_profile_params

    DC14_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    DC14_AVAILABLE = False


def uet_velocity_nfw(r, M_disk, R_disk, galaxy_type="dwarf"):
    """
    UET v3 velocity with NFW halo (baseline).
    Same as test_175_galaxies.py
    """
    G = 4.302e-6  # kpc (km/s)^2 / Msun

    # Universal Density Law
    vol = (4 / 3) * np.pi * R_disk**3
    rho = M_disk / (vol + 1e-10)
    k = 54627.0
    M_halo_ratio = k / np.sqrt(rho)
    M_halo_ratio = max(M_halo_ratio, 0.1)
    M_halo = M_halo_ratio * M_disk

    # NFW concentration
    c = 10.0 * (M_halo / 1e12) ** (-0.1)
    c = np.clip(c, 5, 20)

    R_halo = 10 * R_disk
    r_s = R_halo / c
    x = r / r_s
    M_halo_enc = M_halo * (np.log(1 + x) - x / (1 + x)) / (np.log(1 + c) - c / (1 + c))

    # Disk
    x_disk = r / R_disk
    M_disk_enc = M_disk * (1 - (1 + x_disk) * np.exp(-x_disk))

    M_total = M_disk_enc + M_halo_enc
    V = np.sqrt(G * M_total / (r + 0.01))

    return V


def uet_velocity_v6(r, M_star, R_disk, galaxy_type="dwarf"):
    """
    UET v6 velocity with MASS-DEPENDENT k constant.

    Fixes the dwarf galaxy underprediction by using higher k for low-mass galaxies.
    Based on abundance matching: dwarfs have higher M_halo/M_star ratios.
    """
    G = 4.302e-6

    # Universal Density Law with MASS-DEPENDENT k
    vol = (4 / 3) * np.pi * R_disk**3
    rho = M_star / (vol + 1e-10)

    # Mass-dependent k calibration
    # Higher k for lower mass = more DM dominated
    if M_star < 1e7:  # Ultra-faint
        k = 200000.0
    elif M_star < 1e8:  # Small dwarf
        k = 150000.0
    elif M_star < 1e9:  # Dwarf
        k = 100000.0
    else:  # Spiral-like
        k = 54627.0

    M_halo_ratio = k / np.sqrt(rho)
    M_halo_ratio = max(M_halo_ratio, 0.1)
    M_halo = M_halo_ratio * M_star

    # NFW concentration
    c = 10.0 * (M_halo / 1e12) ** (-0.1)
    c = np.clip(c, 5, 25)

    R_halo = 10 * R_disk
    r_s = R_halo / c
    x = r / r_s
    M_halo_enc = M_halo * (np.log(1 + x) - x / (1 + x)) / (np.log(1 + c) - c / (1 + c))

    # Disk
    x_disk = r / R_disk
    M_disk_enc = M_star * (1 - (1 + x_disk) * np.exp(-x_disk))

    M_total = M_disk_enc + M_halo_enc
    V = np.sqrt(G * M_total / (r + 0.01))

    return V


def run_test():
    """Run LITTLE THINGS test comparing UET v3 vs v5 (DC14)."""
    print("=" * 70)
    print("🌌 LITTLE THINGS DWARF GALAXY TEST")
    print("    UET v3 (NFW) vs UET v6 (Mass-dependent k)")
    print("=" * 70)
    print()

    if not DC14_AVAILABLE:
        print("❌ DC14 model not available. Check imports.")
        return None, None

    # Save data if needed
    save_data()

    galaxies = LITTLE_THINGS_GALAXIES["galaxies"]
    print(f"Source: {LITTLE_THINGS_GALAXIES['source']}")
    print(f"Total galaxies: {len(galaxies)}")
    print()

    results_v3 = []
    results_v6 = []

    print(
        f"{'Name':<12} {'V_obs':<8} {'V_v3':<8} {'V_v5':<8} {'Err_v3':<10} {'Err_v5':<10} {'Better':<8}"
    )
    print("-" * 70)

    for g in galaxies:
        name = g["name"]
        V_obs = g["V_last"]
        M_star = g["M_star"]
        R_disk = g["R_d"]
        R_last = g["R_last"]

        # UET v3 (NFW)
        V_v3 = uet_velocity_nfw(R_last, M_star, R_disk, "dwarf")
        err_v3 = abs(V_v3 - V_obs) / V_obs * 100

        # UET v6 (Mass-dependent k)
        V_v6 = uet_velocity_v6(R_last, M_star, R_disk, "dwarf")
        err_v6 = abs(V_v6 - V_obs) / V_obs * 100

        # Which is better?
        if err_v6 < err_v3:
            better = "✅ v6"
        elif err_v3 < err_v6:
            better = "v3"
        else:
            better = "="

        print(
            f"{name:<12} {V_obs:<8.0f} {V_v3:<8.1f} {V_v6:<8.1f} {err_v3:<10.1f} {err_v6:<10.1f} {better:<8}"
        )

        results_v3.append({"name": name, "V_obs": V_obs, "V_pred": V_v3, "error": err_v3})
        results_v6.append({"name": name, "V_obs": V_obs, "V_pred": V_v6, "error": err_v6})

    # Summary
    avg_err_v3 = np.mean([r["error"] for r in results_v3])
    avg_err_v6 = np.mean([r["error"] for r in results_v6])

    pass_v3 = sum(1 for r in results_v3 if r["error"] < 15)
    pass_v6 = sum(1 for r in results_v6 if r["error"] < 15)

    v6_wins = sum(1 for r3, r6 in zip(results_v3, results_v6) if r6["error"] < r3["error"])

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"                    UET v3 (NFW)    UET v6 (k recal)")
    print(f"  Average Error:    {avg_err_v3:.1f}%           {avg_err_v6:.1f}%")
    print(
        f"  Pass Rate (<15%): {100*pass_v3/len(galaxies):.0f}%            {100*pass_v6/len(galaxies):.0f}%"
    )
    print()
    print(f"  v6 wins on {v6_wins}/{len(galaxies)} galaxies ({100*v6_wins/len(galaxies):.0f}%)")
    print()

    if avg_err_v6 < avg_err_v3:
        improvement = (avg_err_v3 - avg_err_v6) / avg_err_v3 * 100
        print(f"⭐ v6 IMPROVES ERROR BY {improvement:.1f}%!")
    else:
        print("⚠️ v6 did not improve overall error")

    print()

    return results_v3, results_v6


if __name__ == "__main__":
    results_v3, results_v6 = run_test()
