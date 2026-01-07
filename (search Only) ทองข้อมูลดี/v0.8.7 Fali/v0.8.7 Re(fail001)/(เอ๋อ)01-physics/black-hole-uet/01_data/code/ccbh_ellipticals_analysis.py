#!/usr/bin/env python3
"""
🏛️ CCBH ANALYSIS WITH ELLIPTICAL GALAXIES
==========================================
This is the PROPER way to test CCBH - using elliptical galaxies
that have NO active accretion!

Why Ellipticals?
- No gas → No accretion → BH can't grow from eating
- No major mergers → BH can't grow from collisions
- IF BH mass still grows with time → MUST be cosmological coupling!

Data: Kormendy & Ho (2013) - 25 local ellipticals with M_BH and M_bulge

Comparison with Farrah et al. (2023):
- They used elliptical galaxies at z~0 and z~0.7
- Found that M_BH/M_* ratio changes with z
- Implies k ≈ 3 (vacuum energy coupling)

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def load_kormendy_ho():
    """Load Kormendy & Ho local ellipticals."""
    path = SCRIPT_DIR / "kormendy_ho_data" / "kormendy_ho_ellipticals_sample.csv"

    if not path.exists():
        print(f"❌ File not found: {path}")
        return None

    print("📖 Loading Kormendy & Ho (2013) Ellipticals...")

    names, log_mbh, log_mbulge, log_ratio, distances = [], [], [], [], []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("name,"):
                continue

            parts = line.split(",")
            if len(parts) >= 5:
                names.append(parts[0])
                log_mbh.append(float(parts[1]))
                log_mbulge.append(float(parts[2]))
                log_ratio.append(float(parts[3]))
                distances.append(float(parts[4]))

    # Convert distance to redshift (H0 = 70 km/s/Mpc)
    distances = np.array(distances)
    z = distances * 70 / 3e5  # v/c approximation

    data = {
        "name": names,
        "z": z,
        "logMBH": np.array(log_mbh),
        "logMbulge": np.array(log_mbulge),
        "logRatio": np.array(log_ratio),
        "distance_Mpc": distances,
    }

    print(f"   ✅ Loaded {len(names)} elliptical galaxies")

    return data


def analyze_ccbh_ellipticals(data):
    """Analyze CCBH using elliptical galaxy sample."""

    print("\n" + "=" * 60)
    print("📈 CCBH ANALYSIS - ELLIPTICAL GALAXIES")
    print("=" * 60)

    z = data["z"]
    log_ratio = data["logRatio"]
    log_mbh = data["logMBH"]
    log_mbulge = data["logMbulge"]

    print(f"\n📊 SAMPLE STATISTICS:")
    print(f"   N = {len(z)}")
    print(f"   z range: {z.min():.4f} - {z.max():.4f}")
    print(f"   Mean z: {np.mean(z):.4f}")
    print(f"   log(M_BH) range: {log_mbh.min():.2f} - {log_mbh.max():.2f}")
    print(f"   log(M_bulge) range: {log_mbulge.min():.2f} - {log_mbulge.max():.2f}")
    print(f"   Mean log(M_BH/M_bulge) = {np.mean(log_ratio):.3f} ± {np.std(log_ratio):.3f}")

    # Key insight: All these galaxies are at z ~ 0
    # So we can only get the z=0 calibration point!

    print(f"\n💡 KEY INSIGHT:")
    print(f"   All K&H galaxies are LOCAL (z < 0.03)")
    print(f"   This gives us the z~0 reference point only!")
    print(f"")
    print(f"   To test CCBH, Farrah et al. compared:")
    print(f"   - Ellipticals at z ~ 0 (like our K&H sample)")
    print(f"   - Ellipticals at z ~ 0.7 (from SDSS/BOSS)")
    print(f"")
    print(f"   We only have the z ~ 0 sample here!")

    # What can we do?
    # 1. Check if M_BH/M_bulge ratio has any trend with z
    # 2. Extrapolate what we'd expect at higher z

    print(f"\n📈 FITTING M_BH vs M_BULGE RELATION:")

    # Fit M_BH vs M_bulge relation
    slope, intercept, r, p, se = stats.linregress(log_mbulge, log_mbh)

    print(f"   log(M_BH) = {intercept:.2f} + {slope:.2f} × log(M_bulge)")
    print(f"   R² = {r**2:.4f}")
    print(f"   p-value = {p:.2e}")

    # The classic M_BH - M_bulge relation: M_BH ≈ 0.002 × M_bulge
    # log(M_BH) = log(M_bulge) + log(0.002) = log(M_bulge) - 2.7

    mean_ratio = np.mean(log_ratio)

    print(f"\n🎯 z~0 CALIBRATION FOR CCBH:")
    print(f"   <log(M_BH/M_bulge)>₀ = {mean_ratio:.3f}")
    print(f"   Implied M_BH/M_bulge ratio = {10**mean_ratio:.4f}")
    print(f"   (i.e., BH is ~{100*10**mean_ratio:.2f}% of bulge mass)")

    # What would we expect at higher z?
    print(f"\n📊 EXPECTED log(M_BH/M_bulge) AT HIGHER z:")
    print(f"   If BH mass grows as a^k (CCBH hypothesis):")
    print(f"   log(M_BH/M_bulge) = {mean_ratio:.2f} + k × log(a)")
    print()

    z_test = [0.0, 0.5, 1.0, 2.0]
    for z_t in z_test:
        a_t = 1.0 / (1.0 + z_t)
        log_a = np.log10(a_t)
        print(f"   z = {z_t:.1f} (a = {a_t:.3f}):")
        for k in [0, 1, 2.8, 3]:
            ratio_pred = mean_ratio + k * log_a
            print(f"      k = {k}: log(M_BH/M_bulge) = {ratio_pred:.2f}")
        print()

    # Generate plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: M_BH vs M_bulge
    ax1 = axes[0]
    ax1.scatter(log_mbulge, log_mbh, s=100, c=z, cmap="viridis", edgecolors="black", alpha=0.8)

    # Fit line
    x_line = np.linspace(log_mbulge.min() - 0.5, log_mbulge.max() + 0.5, 100)
    y_line = intercept + slope * x_line
    ax1.plot(x_line, y_line, "r--", linewidth=2, label=f"Fit: slope = {slope:.2f}")

    # 1:1 line (M_BH = M_bulge)
    ax1.plot(x_line, x_line, "k:", linewidth=1, alpha=0.5, label="M_BH = M_bulge")

    ax1.set_xlabel(r"log(M$_{bulge}$ / M$_\odot$)", fontsize=12)
    ax1.set_ylabel(r"log(M$_{BH}$ / M$_\odot$)", fontsize=12)
    ax1.set_title("Kormendy & Ho (2013): M_BH vs M_bulge", fontsize=14)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(z.min(), z.max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax1)
    cbar.set_label("Redshift z", fontsize=10)

    # Plot 2: CCBH predictions
    ax2 = axes[1]

    z_model = np.linspace(0, 2, 100)
    a_model = 1.0 / (1.0 + z_model)
    log_a_model = np.log10(a_model)

    colors = {
        "k=0 (Standard)": "gray",
        "k=1 (Comoving)": "blue",
        "k=2.8 (UET)": "green",
        "k=3 (Farrah)": "red",
    }

    for name, k in [
        ("k=0 (Standard)", 0),
        ("k=1 (Comoving)", 1),
        ("k=2.8 (UET)", 2.8),
        ("k=3 (Farrah)", 3),
    ]:
        ratio_pred = mean_ratio + k * log_a_model
        ax2.plot(z_model, ratio_pred, linewidth=2.5, label=name, color=colors[name])

    # Mark our data point at z~0
    ax2.scatter(
        [np.mean(z)],
        [mean_ratio],
        s=200,
        c="gold",
        marker="*",
        edgecolors="black",
        zorder=10,
        label=f"K&H z~0: {mean_ratio:.2f}",
    )

    ax2.set_xlabel("Redshift z", fontsize=12)
    ax2.set_ylabel(r"log(M$_{BH}$/M$_{bulge}$)", fontsize=12)
    ax2.set_title("CCBH Predictions: M_BH/M_bulge vs z", fontsize=14)
    ax2.legend(loc="lower left")
    ax2.grid(alpha=0.3)
    ax2.set_xlim(0, 2)

    plt.tight_layout()
    output_path = SCRIPT_DIR / "ccbh_ellipticals_analysis.png"
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"   ✅ Saved: {output_path}")

    return {
        "mean_ratio_z0": mean_ratio,
        "std_ratio_z0": np.std(log_ratio),
        "slope": slope,
        "intercept": intercept,
    }


def main():
    print("\n" + "🏛️" * 35)
    print("   CCBH ANALYSIS - ELLIPTICAL GALAXIES")
    print("🏛️" * 35)

    data = load_kormendy_ho()
    if data is None:
        return 1

    result = analyze_ccbh_ellipticals(data)

    print("\n" + "=" * 60)
    print("🏆 FINAL SUMMARY")
    print("=" * 60)

    print(f"\n📊 z~0 CALIBRATION:")
    print(f"   <log(M_BH/M_bulge)>₀ = {result['mean_ratio_z0']:.3f} ± {result['std_ratio_z0']:.3f}")

    print(f"\n💡 WHAT THIS MEANS FOR CCBH:")
    print(f"   1. We have established the z~0 baseline")
    print(f"   2. To TEST CCBH, we need ellipticals at z > 0")
    print(f"   3. Farrah found M_BH/M_bulge INCREASES at lower z")
    print(f"   4. This implies k ≈ 3 (cosmological coupling)")

    print(f"\n🎯 UET PREDICTION (k = 2.8):")
    print(
        f"   At z = 0.7, expect log(M_BH/M_bulge) = {result['mean_ratio_z0'] + 2.8 * np.log10(1/1.7):.2f}"
    )
    print(
        f"   At z = 1.0, expect log(M_BH/M_bulge) = {result['mean_ratio_z0'] + 2.8 * np.log10(0.5):.2f}"
    )

    print(f"\n📝 CONCLUSION:")
    print(f"   Our Kormendy & Ho sample provides the z~0 anchor point.")
    print(f"   To complete the CCBH test, we need high-z ellipticals!")
    print(f"   This is exactly what Farrah et al. did with SDSS/BOSS.")

    print("\n" + "🏛️" * 35)
    print("   ANALYSIS COMPLETE!")
    print("🏛️" * 35)

    return 0


if __name__ == "__main__":
    main()
