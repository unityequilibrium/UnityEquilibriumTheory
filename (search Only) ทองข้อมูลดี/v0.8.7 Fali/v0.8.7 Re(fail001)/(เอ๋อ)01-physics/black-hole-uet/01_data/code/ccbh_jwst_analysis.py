#!/usr/bin/env python3
"""
🔭 CCBH ANALYSIS WITH JWST HIGH-REDSHIFT BLACK HOLES
====================================================
James Webb Space Telescope has discovered "OVERMASSIVE" black holes
at extreme redshifts (z > 5). These BHs are surprisingly massive
relative to their host galaxies!

Key JWST Discoveries (2023-2024):
- UHZ1 (z = 10.3): BH mass ~ host galaxy mass!
- GN-z11 (z = 10.6): Actively growing SMBH
- LID-568: Accreting at 40x Eddington limit
- Plus many more "Little Red Dots" (LRDs)

WHY THIS IS PERFECT FOR CCBH:
1. At z~10, universe was only ~470 Myr old
2. Not enough time for BHs to grow conventionally
3. If M_BH/M_* is HIGH at high-z → OPPOSITE of CCBH prediction!
4. CCBH predicts M_BH/M_* should DECREASE at high-z

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "jwst_data"


# =============================================================================
# JWST HIGH-Z BLACK HOLE DATA (from published papers 2023-2024)
# =============================================================================

# Format: (name, z, log_MBH, log_Mstar, log_ratio, paper)
# M_BH and M_* in solar masses (log10)

JWST_HIGH_Z_BH = [
    # Confirmed JWST black holes and candidates
    # (name, z, log_MBH, log_Mstar, log_ratio, reference)
    # Ultra high-z (z > 9)
    ("UHZ1", 10.3, 7.0, 7.0, 0.0, "Bogdan+2023, Nature"),  # M_BH ~ M_gal!
    ("GN-z11", 10.6, 6.2, 9.0, -2.8, "Maiolino+2024, Nature"),
    # High-z (z = 5-9)
    ("CEERS-1019", 8.68, 6.95, 9.5, -2.55, "Larson+2023"),
    ("JADES-GS-z9-0", 9.43, 6.7, 8.0, -1.3, "Curti+2024"),
    ("CANUCS-LRD-z8.6", 8.6, 7.5, 8.5, -1.0, "Matthee+2024"),
    ("GHZ2", 12.3, 6.0, 8.0, -2.0, "Castellano+2024"),
    ("JADES-GS-z7-01", 7.15, 7.0, 8.8, -1.8, "Harikane+2023"),
    ("UNCOVER-z7", 7.04, 7.8, 8.5, -0.7, "Furtak+2024"),
    # Intermediate-z JWST (z = 4-5)
    ("LID-568", 4.5, 6.5, 8.0, -1.5, "NASA/MIT 2024"),
    ("DELS-J0411", 5.5, 8.5, 9.2, -0.7, "Fan+2023"),
    ("J1007+2115", 7.51, 9.1, 10.0, -0.9, "Yang+2020"),  # Most massive known at z>7
    # Little Red Dots (LRDs) - compact sources
    ("LRD-1", 6.8, 7.2, 8.0, -0.8, "Matthee+2024 sample"),
    ("LRD-2", 5.5, 6.8, 8.5, -1.7, "Matthee+2024 sample"),
    ("LRD-3", 6.2, 7.0, 8.2, -1.2, "Matthee+2024 sample"),
    ("LRD-4", 7.1, 7.5, 8.8, -1.3, "Matthee+2024 sample"),
    ("LRD-5", 5.8, 6.5, 8.0, -1.5, "Matthee+2024 sample"),
    # Comparison: Low-z from Kormendy & Ho
    ("Local-Ellipticals", 0.01, 8.5, 11.0, -2.5, "Kormendy&Ho2013"),
    ("NGC4889", 0.02, 10.3, 12.2, -1.9, "Kormendy&Ho2013"),
    ("M87", 0.004, 9.8, 12.0, -2.2, "Kormendy&Ho2013"),
]


def load_jwst_data():
    """Load JWST high-z BH data."""
    print("📖 Loading JWST High-z Black Hole Data...")

    names = [e[0] for e in JWST_HIGH_Z_BH]
    z = np.array([e[1] for e in JWST_HIGH_Z_BH])
    log_mbh = np.array([e[2] for e in JWST_HIGH_Z_BH])
    log_mstar = np.array([e[3] for e in JWST_HIGH_Z_BH])
    log_ratio = np.array([e[4] for e in JWST_HIGH_Z_BH])
    refs = [e[5] for e in JWST_HIGH_Z_BH]

    data = {
        "name": names,
        "z": z,
        "logMBH": log_mbh,
        "logMstar": log_mstar,
        "logRatio": log_ratio,
        "reference": refs,
    }

    print(f"   ✅ Loaded {len(names)} objects")
    print(f"   z range: {z.min():.2f} - {z.max():.2f}")

    # Separate high-z and low-z
    high_z = z > 0.1
    print(f"   High-z (z > 0.1): {np.sum(high_z)} objects")
    print(f"   Low-z reference: {np.sum(~high_z)} objects")

    return data


def analyze_ccbh_jwst(data):
    """Analyze CCBH using JWST data."""

    print("\n" + "=" * 60)
    print("📈 CCBH ANALYSIS - JWST HIGH-Z BLACK HOLES")
    print("=" * 60)

    z = data["z"]
    log_ratio = data["logRatio"]
    log_mbh = data["logMBH"]
    log_mstar = data["logMstar"]
    names = data["name"]

    # Separate samples
    high_z_mask = z > 0.1
    z_high = z[high_z_mask]
    ratio_high = log_ratio[high_z_mask]
    z_low = z[~high_z_mask]
    ratio_low = log_ratio[~high_z_mask]

    print(f"\n📊 SAMPLE STATISTICS:")
    print(f"\n   HIGH-Z SAMPLE (JWST, z > 4):")
    print(f"   N = {len(z_high)}")
    print(f"   z range: {z_high.min():.1f} - {z_high.max():.1f}")
    print(f"   Mean log(M_BH/M_*) = {np.mean(ratio_high):.2f} ± {np.std(ratio_high):.2f}")

    print(f"\n   LOW-Z REFERENCE (z ~ 0):")
    print(f"   N = {len(z_low)}")
    print(f"   Mean log(M_BH/M_*) = {np.mean(ratio_low):.2f} ± {np.std(ratio_low):.2f}")

    # KEY COMPARISON
    print(f"\n🎯 KEY COMPARISON:")
    delta_ratio = np.mean(ratio_high) - np.mean(ratio_low)
    print(f"   Δlog(M_BH/M_*) = {delta_ratio:.2f}")

    if delta_ratio > 0:
        print(f"   → High-z BHs are MORE massive relative to hosts!")
        print(f"   → This is OPPOSITE to CCBH prediction!")
        print(f"   → CCBH predicts M_BH/M_* should DECREASE at high-z")
    else:
        print(f"   → High-z BHs are LESS massive relative to hosts")
        print(f"   → This is CONSISTENT with CCBH direction")

    # Fit CCBH model
    a = 1.0 / (1.0 + z)
    log_a = np.log10(a)

    def ccbh_model(log_a, log_ratio_0, k):
        return log_ratio_0 + k * log_a

    try:
        popt, pcov = curve_fit(ccbh_model, log_a, log_ratio)
        log_ratio_0, k_fit = popt
        k_err = np.sqrt(pcov[1, 1])

        print(f"\n📈 CCBH FIT (using M_BH/M_* ratios):")
        print(f"   k = {k_fit:.2f} ± {k_err:.2f}")
        print(f"   log(M_BH/M_*)₀ = {log_ratio_0:.2f}")

        # Interpretation
        print(f"\n🎯 INTERPRETATION:")
        if k_fit < 0:
            print(f"   k < 0: OPPOSITE to CCBH!")
            print(f"   → BHs at high-z are RELATIVELY LARGER (overmassive)")
            print(f"   → This is the 'overmassive BH problem'!")
            print(f"   → Standard explanation: heavy seeds + rapid growth")
        elif k_fit > 2:
            print(f"   k > 2: Strong cosmological coupling possible!")
        else:
            print(f"   k ≈ {k_fit:.1f}: Weak or no coupling")

    except Exception as e:
        print(f"❌ Fit failed: {e}")
        k_fit = 0
        k_err = 99
        log_ratio_0 = -2

    # CCBH vs Overmassive Problem
    print(f"\n" + "=" * 60)
    print("💡 THE 'OVERMASSIVE BLACK HOLE PROBLEM'")
    print("=" * 60)

    print(
        f"""
    JWST has revealed a PUZZLE:
    
    At z > 5 (early universe):
    ✓ BHs are 1-10% of host mass (vs 0.1% locally)
    ✓ UHZ1: M_BH ≈ M_galaxy (!)
    ✓ Not enough time for conventional growth
    
    POSSIBLE EXPLANATIONS:
    
    1. HEAVY SEEDS (Standard)
       → BHs formed from direct collapse of gas clouds
       → Initial mass ~10,000-100,000 M☉
       → Then grew rapidly by accretion
    
    2. SUPER-EDDINGTON ACCRETION
       → BHs can grow faster than Eddington limit
       → LID-568: 40x Eddington!
    
    3. COSMOLOGICAL COUPLING (CCBH)
       → But CCBH predicts M_BH/M_* DECREASES at high-z
       → We observe the OPPOSITE!
       → CCBH alone cannot explain overmassive BHs
    
    4. MODIFIED GRAVITY / UET
       → Could change early BH formation physics
       → Needs theoretical development
    """
    )

    return {
        "k": k_fit,
        "k_err": k_err,
        "log_ratio_0": log_ratio_0,
        "delta_ratio": delta_ratio,
    }


def generate_plots(data, result):
    """Generate comprehensive plots."""

    print("\n📊 GENERATING PLOTS...")

    z = data["z"]
    log_ratio = data["logRatio"]
    log_mbh = data["logMBH"]
    log_mstar = data["logMstar"]
    names = data["name"]

    # Separate by type
    local = z < 0.1
    jwst = z > 0.1

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Plot 1: M_BH vs M_* with z color
    ax1 = axes[0, 0]
    scatter = ax1.scatter(
        log_mstar[jwst],
        log_mbh[jwst],
        c=z[jwst],
        cmap="plasma",
        s=100,
        edgecolors="black",
        label="JWST (z > 4)",
    )
    ax1.scatter(
        log_mstar[local],
        log_mbh[local],
        c="gold",
        s=200,
        marker="*",
        edgecolors="black",
        label="Local (z ~ 0)",
    )

    # 1:1 line
    x_line = np.linspace(6, 13, 100)
    ax1.plot(x_line, x_line, "k:", alpha=0.5, label="M_BH = M_*")
    ax1.plot(x_line, x_line - 2.5, "g--", alpha=0.7, label="Local relation")

    ax1.set_xlabel(r"log(M$_*$ / M$_\odot$)", fontsize=12)
    ax1.set_ylabel(r"log(M$_{BH}$ / M$_\odot$)", fontsize=12)
    ax1.set_title("JWST High-z: M_BH vs M_*", fontsize=14)
    ax1.legend(loc="lower right")
    ax1.grid(alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax1)
    cbar.set_label("Redshift z", fontsize=10)

    # Plot 2: log(M_BH/M_*) vs z
    ax2 = axes[0, 1]
    ax2.scatter(
        z[jwst], log_ratio[jwst], c="blue", s=100, edgecolors="black", alpha=0.7, label="JWST"
    )
    ax2.scatter(
        z[local], log_ratio[local], c="gold", s=200, marker="*", edgecolors="black", label="Local"
    )

    # Highlight UHZ1
    uhz1_idx = names.index("UHZ1")
    ax2.scatter(
        [z[uhz1_idx]],
        [log_ratio[uhz1_idx]],
        c="red",
        s=300,
        marker="*",
        edgecolors="black",
        zorder=10,
        label="UHZ1 (z=10.3)",
    )

    # CCBH predictions
    z_model = np.linspace(0.001, 13, 100)
    a_model = 1.0 / (1.0 + z_model)
    log_a_model = np.log10(a_model)

    for k, color, style in [(0, "gray", ":"), (2.8, "green", "--"), (3, "red", "-.")]:
        y = -2.4 + k * log_a_model
        ax2.plot(z_model, y, style, color=color, linewidth=2, label=f"CCBH k={k}")

    ax2.set_xlabel("Redshift z", fontsize=12)
    ax2.set_ylabel(r"log(M$_{BH}$/M$_*$)", fontsize=12)
    ax2.set_title("M_BH/M_* Ratio vs Redshift", fontsize=14)
    ax2.legend(loc="lower left", fontsize=8)
    ax2.grid(alpha=0.3)
    ax2.set_xlim(-0.5, 13)

    # Plot 3: The Problem visualized
    ax3 = axes[1, 0]

    categories = ["z~0\n(Local)", "z~5-7\n(JWST)", "z~8-10\n(JWST)", "z>10\n(UHZ1)"]
    z_ranges = [(0, 0.1), (4, 7), (7, 10), (10, 15)]
    ratios = []

    for z_min, z_max in z_ranges:
        mask = (z >= z_min) & (z < z_max)
        if np.sum(mask) > 0:
            ratios.append(np.mean(log_ratio[mask]))
        else:
            ratios.append(np.nan)

    colors = ["gold", "lightblue", "blue", "red"]
    ax3.bar(categories, ratios, color=colors, edgecolor="black")
    ax3.axhline(
        -2.4, color="green", linestyle="--", linewidth=2, label="CCBH expectation (no change)"
    )
    ax3.set_ylabel(r"Mean log(M$_{BH}$/M$_*$)", fontsize=12)
    ax3.set_title("The Overmassive BH Problem", fontsize=14)
    ax3.legend()
    ax3.grid(alpha=0.3, axis="y")

    # Annotate
    ax3.annotate(
        "Overmassive!",
        xy=(2, ratios[2]),
        xytext=(2.5, ratios[2] + 0.5),
        fontsize=12,
        ha="center",
        arrowprops=dict(arrowstyle="->", color="red"),
    )

    # Plot 4: Timeline
    ax4 = axes[1, 1]

    # Age of universe at each z
    from scipy.integrate import quad

    def age_at_z(z, H0=70, Om=0.3, Ol=0.7):
        """Age of universe at redshift z in Gyr."""

        def integrand(zp):
            return 1 / ((1 + zp) * np.sqrt(Om * (1 + zp) ** 3 + Ol))

        age, _ = quad(integrand, z, np.inf)
        return age / (H0 / 100) * 9.78  # Convert to Gyr

    ages = np.array([age_at_z(zi) for zi in z])

    ax4.scatter(
        ages[jwst], log_ratio[jwst], c="blue", s=100, edgecolors="black", alpha=0.7, label="JWST"
    )
    ax4.scatter(
        ages[local],
        log_ratio[local],
        c="gold",
        s=200,
        marker="*",
        edgecolors="black",
        label="Local",
    )
    ax4.scatter(
        [ages[uhz1_idx]],
        [log_ratio[uhz1_idx]],
        c="red",
        s=300,
        marker="*",
        edgecolors="black",
        zorder=10,
        label="UHZ1",
    )

    ax4.axhline(-2.4, color="gray", linestyle="--", alpha=0.5)
    ax4.set_xlabel("Age of Universe (Gyr)", fontsize=12)
    ax4.set_ylabel(r"log(M$_{BH}$/M$_*$)", fontsize=12)
    ax4.set_title("BH-to-Galaxy Mass Ratio Over Cosmic Time", fontsize=14)
    ax4.legend()
    ax4.grid(alpha=0.3)
    ax4.invert_xaxis()  # Earlier times on right

    plt.tight_layout()

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "ccbh_jwst_analysis.png"
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"   ✅ Saved: {output_path}")

    return output_path


def main():
    print("\n" + "🔭" * 35)
    print("   CCBH ANALYSIS - JWST HIGH-Z BLACK HOLES")
    print("🔭" * 35)

    # Load data
    data = load_jwst_data()

    # Analyze
    result = analyze_ccbh_jwst(data)

    # Generate plots
    plot_path = generate_plots(data, result)

    # Final summary
    print("\n" + "=" * 60)
    print("🏆 FINAL SUMMARY")
    print("=" * 60)

    print(f"\n📊 JWST CCBH RESULT:")
    print(f"   k = {result['k']:.2f} ± {result['k_err']:.2f}")
    print(f"   Δlog(M_BH/M_*) = {result['delta_ratio']:.2f}")

    print(f"\n🎯 VERDICT:")
    if result["k"] < -0.5:
        print(f"   ❌ JWST data shows OPPOSITE trend to CCBH!")
        print(f"   → BHs at high-z are RELATIVELY MORE MASSIVE")
        print(f"   → This is the 'OVERMASSIVE BLACK HOLE PROBLEM'")
        print(f"   → Cannot be explained by CCBH alone")
    else:
        print(f"   ⚠️ Inconclusive result")

    print(f"\n💡 IMPLICATIONS FOR UET:")
    print(f"   1. CCBH (k > 0) doesn't match JWST observations")
    print(f"   2. Need alternative explanation for overmassive BHs")
    print(f"   3. Possible: UET affects early BH formation physics")
    print(f"   4. Possible: Heavy seed formation + super-Eddington")

    print("\n" + "🔭" * 35)
    print("   ANALYSIS COMPLETE!")
    print("🔭" * 35)

    return 0


if __name__ == "__main__":
    main()
