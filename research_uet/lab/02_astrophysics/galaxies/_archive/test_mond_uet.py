"""
MOND-UET Galaxy Rotation Test
==============================

Implements MOND (Modified Newtonian Dynamics) with UET interpretation.

MOND Core Equation:
    g × μ(g/a₀) = g_N

UET Interpretation:
    a₀ = β_CI × c × H₀ (from Holographic Bound)
    μ = Information Field response function

Reference: Milgrom (1983), McGaugh et al. (2016)

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
        UETParameters, SIGMA_CRIT, strategic_boost, potential_V, KAPPA_BEKENSTEIN
    )
except ImportError:
    pass  # Use local definitions if not available

import os

# Add parent directory for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from research_uet.theory.utility.universal_constants import c

# =============================================================================
# MOND CONSTANTS (with UET derivation)
# =============================================================================

# Hubble constant (1/s) ≈ 70 km/s/Mpc
H0 = 2.2e-18

# Holographic radius
R_H = c / H0  # ≈ 1.36e26 m

# CI Coupling factor (UET parameter, derived from MOND empirical fit)
BETA_CI = 0.18

# MOND acceleration scale (derived from Holographic Bound + CI coupling)
a0 = BETA_CI * c * H0  # ≈ 1.2e-10 m/s²


# G in astrophysical units: (km/s)² kpc / M_sun
G_astro = 4.302e-6

# Unit conversions
kpc_to_m = 3.086e19
Msun = 1.989e30

print(f"UET-Derived MOND Constants:")
print(f"  R_H (Holographic radius) = {R_H:.2e} m")
print(f"  β_CI (CI coupling) = {BETA_CI}")
print(f"  a₀ = β_CI × c × H₀ = {a0:.2e} m/s²")
print(f"  a₀ (literature) = 1.2e-10 m/s²")
print()


# =============================================================================
# MOND INTERPOLATION FUNCTIONS
# =============================================================================


def mu_simple(x):
    """Simple interpolating function: μ(x) = x / (1 + x)"""
    return x / (1 + x)


def mu_standard(x):
    """Standard interpolating function: μ(x) = x / √(1 + x²)"""
    return x / np.sqrt(1 + x**2)


def mond_acceleration(g_newton, mu_func=mu_simple):
    """
    Calculate MOND acceleration from Newtonian acceleration.

    MOND: g × μ(g/a₀) = g_N
    Solving for g: g = g_N / μ(g/a₀)

    This requires iteration since g appears on both sides.
    """
    # Convert a0 to (km/s)²/kpc for consistency
    # a0 in m/s² → (km/s)²/kpc
    # a0 [m/s²] × (1 km/1000 m)² × (kpc / 3.086e19 m) = a0 × 1e-6 / 3.086e19
    a0_astro = a0 * 1e-6 / kpc_to_m * 1e6  # Convert to (km/s)²/kpc
    # Actually simpler: a0 in (km/s)²/kpc = a0 [m/s²] × kpc_to_m / (1e3)²
    a0_astro = a0 * kpc_to_m / 1e6  # ≈ 3.7 (km/s)²/kpc

    # Iterative solution
    g = g_newton  # Initial guess
    for _ in range(20):
        x = g / a0_astro if a0_astro > 0 else 1e10
        mu_val = mu_func(x)
        g_new = g_newton / mu_val
        if abs(g_new - g) < 1e-6 * abs(g):
            break
        g = g_new

    return g


def mond_rotation_velocity(r_kpc, M_disk_Msun, R_disk_kpc, galaxy_type="spiral"):
    """
    Calculate rotation velocity using MOND.

    V² = r × g_MOND

    where g_MOND is solved from: g × μ(g/a₀) = g_N
    """
    # Enclosed mass (exponential disk)
    x = r_kpc / R_disk_kpc
    M_enc = M_disk_Msun * (1 - (1 + x) * np.exp(-x))

    # Add bulge (10% of disk)
    M_bulge = 0.1 * M_disk_Msun
    M_total_enc = M_enc + M_bulge

    # Newtonian acceleration
    r_safe = max(r_kpc, 0.1)
    g_newton = G_astro * M_total_enc / r_safe**2  # (km/s)²/kpc

    # MOND acceleration
    g_mond = mond_acceleration(g_newton)

    # Circular velocity: V² = r × g
    v_squared = r_safe * g_mond

    return np.sqrt(v_squared)


# =============================================================================
# SPARC DATA LOADING
# =============================================================================


def load_sparc_data():
    """Load SPARC galaxy data from test_175_galaxies.py."""
    try:
        from test_175_galaxies import SPARC_GALAXIES

        # Convert to dict format
        galaxies = []
        for gal in SPARC_GALAXIES:
            name, R_max, v_obs, M_disk, R_disk, gtype = gal
            galaxies.append(
                {
                    "name": name,
                    "type": gtype,
                    "M_disk": M_disk,
                    "R_disk": R_disk,
                    "R_max": R_max,
                    "V_obs": v_obs,
                }
            )
        return galaxies
    except ImportError:
        # Direct import as fallback
        try:
            import sys

            sys.path.insert(0, r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7")
            from test_175_galaxies import SPARC_GALAXIES

            galaxies = []
            for gal in SPARC_GALAXIES:
                name, R_max, v_obs, M_disk, R_disk, gtype = gal
                galaxies.append(
                    {
                        "name": name,
                        "type": gtype,
                        "M_disk": M_disk,
                        "R_disk": R_disk,
                        "R_max": R_max,
                        "V_obs": v_obs,
                    }
                )
            return galaxies
        except:
            pass

    # Last resort: use inline data
    print("Warning: Using inline SPARC data subset")
    return [
        {
            "name": "NGC2841",
            "type": "spiral",
            "M_disk": 1e11,
            "R_disk": 8,
            "R_max": 40,
            "V_obs": 300,
        },
        {
            "name": "NGC3198",
            "type": "spiral",
            "M_disk": 2e10,
            "R_disk": 5,
            "R_max": 30,
            "V_obs": 150,
        },
        {
            "name": "NGC2403",
            "type": "spiral",
            "M_disk": 1e10,
            "R_disk": 4,
            "R_max": 18,
            "V_obs": 130,
        },
        {"name": "UGC128", "type": "lsb", "M_disk": 5e9, "R_disk": 3, "R_max": 15, "V_obs": 130},
        {"name": "NGC300", "type": "lsb", "M_disk": 3e9, "R_disk": 3, "R_max": 12, "V_obs": 80},
        {"name": "IC2574", "type": "dwarf", "M_disk": 8e8, "R_disk": 3, "R_max": 12, "V_obs": 65},
        {
            "name": "DDO154",
            "type": "ultrafaint",
            "M_disk": 2e8,
            "R_disk": 2,
            "R_max": 8,
            "V_obs": 50,
        },
        {"name": "WLM", "type": "dwarf", "M_disk": 5e7, "R_disk": 1, "R_max": 2, "V_obs": 30},
    ]


# =============================================================================
# TEST FUNCTION
# =============================================================================


def test_mond_uet():
    """Test MOND-UET implementation against SPARC data."""
    print("=" * 70)
    print("🌌 MOND-UET GALAXY ROTATION TEST")
    print("=" * 70)
    print()
    print("MOND Equation: g × μ(g/a₀) = g_N")
    print(f"UET Derivation: a₀ = β_CI × c × H₀ = {a0:.2e} m/s²")
    print(f"CI Coupling: β_CI = {BETA_CI}")
    print()

    # Load data
    galaxies = load_sparc_data()
    print(f"Loaded {len(galaxies)} galaxies")
    print()

    # Test each galaxy
    results = {"pass": 0, "warn": 0, "fail": 0}
    type_results = {}
    errors = []

    for gal in galaxies:
        name = gal.get("name", "Unknown")
        gtype = gal.get("type", "spiral")
        M_disk = gal.get("M_disk", 1e10)
        R_disk = gal.get("R_disk", 3.0)
        V_obs = gal.get("V_obs", 100)

        R_max = gal.get("R_max", 2.0 * R_disk)

        # Calculate at R_max (where V_obs is measured)
        r_test = R_max
        V_mond = mond_rotation_velocity(r_test, M_disk, R_disk, gtype)

        # Error
        error = abs(V_mond - V_obs) / V_obs * 100
        errors.append(error)

        # Categorize
        if error < 15:
            results["pass"] += 1
            status = "✅"
        elif error < 25:
            results["warn"] += 1
            status = "⚠️"
        else:
            results["fail"] += 1
            status = "❌"

        # Track by type
        if gtype not in type_results:
            type_results[gtype] = {"pass": 0, "total": 0, "errors": []}
        type_results[gtype]["total"] += 1
        type_results[gtype]["errors"].append(error)
        if error < 15:
            type_results[gtype]["pass"] += 1

    # Summary
    print("=" * 70)
    print("RESULTS BY TYPE:")
    print("=" * 70)

    for gtype, data in sorted(type_results.items()):
        pass_rate = data["pass"] / data["total"] * 100 if data["total"] > 0 else 0
        avg_err = np.mean(data["errors"]) if data["errors"] else 0
        print(f"\n{gtype.upper()}:")
        print(f"  Count: {data['total']}")
        print(f"  Pass rate: {pass_rate:.0f}%")
        print(f"  Average error: {avg_err:.1f}%")

    # Overall
    total = results["pass"] + results["warn"] + results["fail"]
    pass_rate = results["pass"] / total * 100 if total > 0 else 0
    avg_error = np.mean(errors) if errors else 0
    median_error = np.median(errors) if errors else 0

    print()
    print("=" * 70)
    print(f"OVERALL SUMMARY: {total} Galaxies")
    print("=" * 70)
    print(f"  ✅ Passed (<15%):    {results['pass']} ({pass_rate:.0f}%)")
    print(f"  ⚠️ Warning (15-25%): {results['warn']} ({results['warn']/total*100:.0f}%)")
    print(f"  ❌ Failed (>25%):    {results['fail']} ({results['fail']/total*100:.0f}%)")
    print()
    print(f"  Average Error: {avg_error:.1f}%")
    print(f"  Median Error:  {median_error:.1f}%")
    print(f"  Pass Rate:     {pass_rate:.0f}%")
    print("=" * 70)

    if pass_rate >= 80:
        print("⭐⭐⭐⭐ EXCELLENT")
    elif pass_rate >= 70:
        print("⭐⭐⭐ GOOD")
    elif pass_rate >= 60:
        print("⭐⭐ ACCEPTABLE")
    else:
        print("⭐ NEEDS IMPROVEMENT")

    return pass_rate, avg_error


if __name__ == "__main__":
    test_mond_uet()
