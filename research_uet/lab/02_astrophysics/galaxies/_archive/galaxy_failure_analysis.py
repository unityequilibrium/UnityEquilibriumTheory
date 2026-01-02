"""
Galaxy Failure Analysis Script
================================
Deep analysis of why some galaxies fail UET prediction.

Updated for UET V3.0
"""


# Import from UET V3.0 Master Equation
import sys
from pathlib import Path
_root = Path(__file__).parent
while _root.name != "research_uet" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from research_uet.core.uet_master_equation import (
        UETParameters, SIGMA_CRIT, strategic_boost, potential_V, KAPPA_BEKENSTEIN
    )
except ImportError:
    pass  # Use local definitions if not available

import numpy as np

# Sample galaxies by type for analysis
GALAXIES_BY_TYPE = {
    "spiral": [
        ("NGC2841", 40, 300, 1e11, 8),
        ("NGC5055", 35, 200, 5e10, 6),
        ("NGC7331", 25, 240, 4e10, 5),
        ("NGC3198", 30, 150, 2e10, 5),
        ("NGC6503", 20, 115, 8e9, 3.5),
    ],
    "lsb": [
        ("UGC128", 15, 130, 5e9, 3),
        ("NGC300", 12, 80, 3e9, 3),
        ("F568-1", 12, 110, 4e9, 3),
    ],
    "dwarf": [
        ("IC2574", 12, 65, 8e8, 3),
        ("DDO170", 6, 55, 2e8, 1.5),
        ("NGC4214", 8, 70, 5e8, 2.5),
    ],
    "compact": [
        ("NGC4826", 12, 150, 1.5e10, 3),  # High v for R
        ("NGC6946", 15, 170, 2e10, 4),
        ("NGC4138", 15, 165, 1.5e10, 3),
    ],
}


def uet_prediction(r_kpc, M_disk, R_disk):
    """UET velocity prediction using Universal Density Law."""
    G = 4.302e-6

    # Disk contribution
    x = r_kpc / R_disk
    M_disk_enc = M_disk * (1 - (1 + x) * np.exp(-x))

    # Halo using UDL
    vol = (4 / 3) * np.pi * R_disk**3
    rho = M_disk / vol
    k = 54627.0
    M_halo_ratio = k / np.sqrt(rho)
    M_halo = M_halo_ratio * M_disk

    # NFW
    c = 10.0 * (M_halo / 1e12) ** (-0.1)
    c = np.clip(c, 5, 20)
    R_halo = 10 * R_disk
    x_h = r_kpc / (R_halo / c)
    M_halo_enc = M_halo * (np.log(1 + x_h) - x_h / (1 + x_h)) / (np.log(1 + c) - c / (1 + c))

    M_total = 0.1 * M_disk + M_disk_enc + M_halo_enc
    v = np.sqrt(G * M_total / (r_kpc + 0.1))
    return v


def analyze_all_types():
    print("=" * 70)
    print("GALAXY FAILURE ANALYSIS BY TYPE")
    print("=" * 70)

    results_by_type = {}

    for gtype, galaxies in GALAXIES_BY_TYPE.items():
        print(f"\n{'='*50}")
        print(f"TYPE: {gtype.upper()}")
        print("=" * 50)

        print(f"{'Galaxy':<12} {'v_obs':<8} {'v_UET':<8} {'Error%':<8} {'Status':<8}")
        print("-" * 50)

        errors = []
        pass_count = 0

        for name, R, v_obs, M_disk, R_disk in galaxies:
            v_uet = uet_prediction(R, M_disk, R_disk)
            error = abs(v_uet - v_obs) / v_obs * 100
            errors.append(error)

            status = "PASS" if error < 20 else "FAIL"
            if status == "PASS":
                pass_count += 1

            print(f"{name:<12} {v_obs:<8.0f} {v_uet:<8.1f} {error:<8.1f} {status:<8}")

        pass_rate = pass_count / len(galaxies) * 100
        avg_error = np.mean(errors)

        results_by_type[gtype] = {
            "pass_rate": pass_rate,
            "avg_error": avg_error,
            "count": len(galaxies),
        }

        print("-" * 50)
        print(f"Pass Rate: {pass_rate:.0f}%, Avg Error: {avg_error:.1f}%")

    print("\n" + "=" * 70)
    print("SUMMARY BY GALAXY TYPE")
    print("=" * 70)
    print(f"{'Type':<12} {'Pass Rate':<12} {'Avg Error':<12} {'Issue':<30}")
    print("-" * 70)

    for gtype, res in results_by_type.items():
        if res["pass_rate"] < 70:
            issue = "PROBLEM - needs investigation"
        elif res["avg_error"] > 20:
            issue = "High error variance"
        else:
            issue = "OK"

        print(
            f"{gtype:<12} {res['pass_rate']:.0f}%{'':<8} {res['avg_error']:.1f}%{'':<8} {issue:<30}"
        )

    print("\n" + "=" * 70)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 70)

    print(
        """
PROBLEM AREAS IDENTIFIED:

1. COMPACT GALAXIES (High v, small R)
   - UET under-predicts velocity
   - Issue: NFW concentration may be wrong for compact galaxies
   - Fix: Need steeper inner profile or higher c
   
2. DWARF GALAXIES (Low mass)
   - UET may over/under-predict depending on cored vs cuspy
   - Issue: NFW is cuspy, but dwarfs often have cores
   - Fix: Use DC14 or cored profile (already tried in v6)
   
3. LSB GALAXIES (Low surface brightness)
   - Large spread in errors
   - Issue: High dark matter fraction but low baryon density
   - Fix: UDL formula may need LSB-specific calibration
   
ROOT CAUSES:
- NFW profile assumes cuspy center (bad for dwarfs/LSB)
- Universal k=54627 may not fit all scales
- Missing baryonic feedback effects
    """
    )

    return results_by_type


if __name__ == "__main__":
    analyze_all_types()
