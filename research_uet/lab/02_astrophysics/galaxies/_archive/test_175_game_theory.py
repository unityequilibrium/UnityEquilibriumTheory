"""
UET + Game Theory Integration Test (SPARC 175)
==============================================
Testing the "United Equation" where Game Theory (Efficiency) is combined
with Field Dynamics.

Hypothesis (TUNED BOOST MODE):
- Previous Tests:
  - Base V3: Compact Error ~20% (Undershoot).
  - Penalty Mode: Compact Error ~35% (Massive Undershoot).
  - Strong Boost: Compact Error ~50% (Overshoot).

- Conclusion: Compact Galaxies need a MODERATE Boost.
  High Conflict (Density) forces the system to *conserve* Vacuum Pressure
  more efficiently than the standard decay law predicts.

- Strategic Term: Additive Boost to prevent Ratio from dropping too low.

New Term:
   M_halo_ratio = Base_Scaling + Strategic_Boost(rho)
"""

import numpy as np
import sys
import os

# Import Data from existing database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from test_175_galaxies import SPARC_GALAXIES
except ImportError:
    SPARC_GALAXIES = []


def uet_game_theory_velocity(r_kpc, M_disk_Msun, R_disk_kpc, galaxy_type):
    G = 4.302e-6

    # === 1. Standard Physics (Field Dynamics) ===
    RHO_PIVOT = 5e7
    RATIO_PIVOT = 8.5
    GAMMA = 0.48

    # Calculate Density (The Conflict Level)
    vol = (4 / 3) * np.pi * R_disk_kpc**3
    rho = M_disk_Msun / (vol + 1e-10)

    # Base Scaling (Entropy Drag) - Decay with density
    base_ratio = RATIO_PIVOT * (rho / RHO_PIVOT) ** (-GAMMA)

    # === 2. Game Theory (Strategic Term / NEA) ===
    # Axiom 6: High Density = Strategic Optimization
    # Instead of letting the support decay completely (as per GAMMA),
    # the system "locks in" a minimum support level to handle the stress.

    STRATEGIC_THRESHOLD = 5e7  # Start boosting earlier
    ALPHA_STRATEGY = 0.5  # Moderate Boost strength (relative to Pivot)

    # Sigmoid Activation
    strategic_boost = 0
    if rho > STRATEGIC_THRESHOLD:
        activation = 1 / (1 + np.exp(-(rho - STRATEGIC_THRESHOLD) / (STRATEGIC_THRESHOLD)))
        # Boost scaled by base ratio to be proportional? No, additive floor.
        strategic_boost = RATIO_PIVOT * ALPHA_STRATEGY * activation

    # Combined Equation (ADDING Boost)
    M_halo_ratio = base_ratio + strategic_boost

    # Limits
    M_halo_ratio = max(M_halo_ratio, 0.1)
    M_halo_ratio = min(M_halo_ratio, 500.0)

    # === 3. Resultant Force ===
    M_halo = M_halo_ratio * M_disk_Msun

    # Halo Concentration
    c = 10.0 * (M_halo / 1e12) ** (-0.1)
    c = np.clip(c, 5, 20)

    M_bulge = 0.1 * M_disk_Msun
    x = r_kpc / R_disk_kpc
    M_disk_enc = M_disk_Msun * (1 - (1 + x) * np.exp(-x))

    R_halo = 10 * R_disk_kpc
    x_h = r_kpc / (R_halo / c)
    M_halo_enc = M_halo * (np.log(1 + x_h) - x_h / (1 + x_h)) / (np.log(1 + c) - c / (1 + c))

    M_total = M_bulge + M_disk_enc + M_halo_enc
    v_circ = np.sqrt(G * M_total / (r_kpc + 0.1))

    return v_circ


def run_test():
    print("=" * 70)
    print("🌌 UET + GAME THEORY INTEGRATION TEST (MODERATE BOOST)")
    print("   Hypothesis: Moderate Efficiency Boost for Compacts")
    print("=" * 70)

    if not SPARC_GALAXIES:
        return

    results = []
    for name, R, v_obs, M_disk, R_disk, gtype in SPARC_GALAXIES:
        v_uet = uet_game_theory_velocity(R, M_disk, R_disk, gtype)
        error = abs(v_uet - v_obs) / v_obs * 100
        signed = (v_uet - v_obs) / v_obs * 100
        results.append({"name": name, "error": error, "signed": signed, "type": gtype})

    # Summary by type
    print("\nRESULTS BY TYPE (With Strategic Boost):")
    print("-" * 40)

    by_type = {}
    for r in results:
        t = r["type"]
        if t not in by_type:
            by_type[t] = {"errors": [], "signed": [], "passed": 0, "total": 0}
        by_type[t]["errors"].append(r["error"])
        by_type[t]["signed"].append(r["signed"])
        by_type[t]["total"] += 1
        if r["error"] < 15:
            by_type[t]["passed"] += 1

    for t in ["spiral", "lsb", "dwarf", "ultrafaint", "compact"]:
        if t in by_type:
            data = by_type[t]
            rate = 100 * data["passed"] / data["total"]
            avg_sign = np.mean(data["signed"])
            print(
                f"{t.upper():<12}: {rate:.0f}% Pass (Avg Err: {np.mean(data['errors']):.1f}%, Bias: {avg_sign:+.1f}%)"
            )

    # Overall
    passed = sum(1 for r in results if r["error"] < 15)
    print("=" * 70)
    print(f"OVERALL PASS RATE: {100*passed/len(results):.0f}% ({passed}/{len(results)})")
    print("=" * 70)


if __name__ == "__main__":
    run_test()
