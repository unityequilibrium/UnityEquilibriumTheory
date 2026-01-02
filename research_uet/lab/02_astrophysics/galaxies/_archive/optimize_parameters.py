"""
UET Galaxy Parameter Optimizer
==============================
Performs grid search to find optimal (RATIO_PIVOT, GAMMA) for maximum pass rate.

Updated for UET V3.0
"""

import numpy as np

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

import sys

# Load galaxy data directly from same directory
from test_175_galaxies import SPARC_GALAXIES


def uet_velocity_sweep(
    r_kpc, M_disk_Msun, R_disk_kpc, galaxy_type, RATIO_PIVOT, GAMMA, RHO_PIVOT=5e7
):
    """Parameterized UET velocity for sweep."""
    G = 4.302e-6

    # Strategic Boost
    sigma_bar = M_disk_Msun / (np.pi * R_disk_kpc**2 + 1e-10)
    SIGMA_CRIT = 2e9

    if galaxy_type == "compact":
        beta_U = np.clip(5.0 * (sigma_bar / SIGMA_CRIT), 1.0, 5.0)
    elif galaxy_type == "ultrafaint":
        # NEW: Add Ultrafaint boost
        beta_U = 0.5  # Extra support for faint systems
    else:
        beta_U = 0.0

    M_bulge = 0.1 * M_disk_Msun
    x = r_kpc / R_disk_kpc
    M_disk_enc = M_disk_Msun * (1 - (1 + x) * np.exp(-x))

    vol = (4 / 3) * np.pi * R_disk_kpc**3
    rho = M_disk_Msun / (vol + 1e-10)

    ratio_scaling = (rho / RHO_PIVOT) ** (-GAMMA)
    M_halo_ratio = np.clip(RATIO_PIVOT * ratio_scaling * (1 + beta_U), 0.1, 500.0)
    M_halo = M_halo_ratio * M_disk_Msun

    c = np.clip(10.0 * (M_halo / 1e12) ** (-0.1), 5, 20)
    R_halo = 10 * R_disk_kpc
    x_h = r_kpc / (R_halo / c)
    M_halo_enc = M_halo * (np.log(1 + x_h) - x_h / (1 + x_h)) / (np.log(1 + c) - c / (1 + c))

    M_total = M_bulge + M_disk_enc + M_halo_enc
    return np.sqrt(G * M_total / (r_kpc + 0.1))


def evaluate_params(RATIO_PIVOT, GAMMA):
    """Evaluate pass rate for given parameters."""
    errors = []
    for name, R, v_obs, M_disk, R_disk, gtype in SPARC_GALAXIES:
        v_pred = uet_velocity_sweep(R, M_disk, R_disk, gtype, RATIO_PIVOT, GAMMA)
        error = abs(v_pred - v_obs) / v_obs * 100
        errors.append(error)

    pass_rate = sum(1 for e in errors if e < 15) / len(errors) * 100
    avg_error = np.mean(errors)
    return pass_rate, avg_error


if __name__ == "__main__":
    print("=" * 60)
    print("UET GALAXY PARAMETER OPTIMIZER")
    print("=" * 60)

    # Grid search
    best_pass = 0
    best_params = (8.5, 0.48)

    print("\nScanning RATIO_PIVOT [6, 14] × GAMMA [0.35, 0.70]...\n")

    for ratio in np.arange(6.0, 14.5, 0.5):
        for gamma in np.arange(0.35, 0.71, 0.02):
            pass_rate, avg_error = evaluate_params(ratio, gamma)
            if pass_rate > best_pass:
                best_pass = pass_rate
                best_params = (ratio, gamma)
                print(
                    f"  NEW BEST: RATIO={ratio:.1f}, GAMMA={gamma:.2f} → {pass_rate:.1f}% ({avg_error:.1f}% avg)"
                )

    print("\n" + "=" * 60)
    print(f"OPTIMAL PARAMETERS FOUND:")
    print(f"  RATIO_PIVOT = {best_params[0]:.1f}")
    print(f"  GAMMA = {best_params[1]:.2f}")
    print(f"  PASS RATE = {best_pass:.1f}%")
    print("=" * 60)
