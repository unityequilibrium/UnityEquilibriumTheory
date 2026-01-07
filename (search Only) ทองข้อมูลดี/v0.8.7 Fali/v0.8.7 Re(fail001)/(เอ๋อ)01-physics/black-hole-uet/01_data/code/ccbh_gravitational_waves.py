#!/usr/bin/env python3
"""
🌊 CCBH ANALYSIS WITH LIGO/VIRGO GRAVITATIONAL WAVES
====================================================
Using GWTC-3 catalog (Third Gravitational-Wave Transient Catalog)
to test Cosmologically Coupled Black Holes hypothesis.

Why GW data is BETTER than optical:
1. No Malmquist bias - GWs are not flux-limited like light
2. Direct mass measurement from waveform
3. Redshift from luminosity distance
4. Clean sample - we KNOW these are black holes!

Data: GWTC-3 (~90 confident BBH mergers)
Source: LIGO/Virgo/KAGRA Collaboration

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from pathlib import Path
import json
import sys

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "gwtc_data"


# =============================================================================
# GWTC-3 EVENT DATA (from official release)
# =============================================================================

# Key BBH events from GWTC-3 with median values
# Format: (name, m1_source, m2_source, chirp_mass, z, d_L)
# m1, m2 in solar masses, z = redshift, d_L in Mpc

GWTC3_BBH_EVENTS = [
    # O1-O2 Events (confirmed BBH)
    ("GW150914", 35.6, 30.6, 28.6, 0.09, 440),
    ("GW151012", 23.2, 13.6, 15.2, 0.21, 1080),
    ("GW151226", 13.7, 7.7, 8.9, 0.09, 450),
    ("GW170104", 30.8, 20.0, 21.4, 0.20, 990),
    ("GW170608", 11.0, 7.6, 7.9, 0.07, 320),
    ("GW170729", 50.2, 34.0, 35.4, 0.48, 2840),
    ("GW170809", 35.0, 23.8, 24.9, 0.20, 1030),
    ("GW170814", 30.6, 25.2, 24.1, 0.12, 600),
    ("GW170818", 35.4, 26.7, 26.5, 0.21, 1060),
    ("GW170823", 39.5, 29.0, 29.2, 0.34, 1940),
    # O3a Events (selected BBH)
    ("GW190408_181802", 24.6, 18.4, 18.3, 0.29, 1540),
    ("GW190412", 30.1, 8.3, 13.3, 0.15, 740),
    ("GW190413_052954", 35.7, 24.0, 25.2, 0.36, 2060),
    ("GW190413_134308", 48.4, 34.4, 35.3, 0.54, 3390),
    ("GW190421_213856", 42.5, 32.5, 32.2, 0.47, 2790),
    ("GW190503_185404", 43.0, 29.4, 30.6, 0.35, 1990),
    ("GW190512_180714", 23.0, 12.6, 14.6, 0.26, 1370),
    ("GW190513_205428", 35.7, 18.0, 21.8, 0.33, 1880),
    ("GW190517_055101", 37.4, 25.3, 26.6, 0.45, 2620),
    ("GW190519_153544", 66.0, 40.5, 44.1, 0.55, 3470),
    ("GW190521", 85.0, 66.0, 64.0, 0.82, 5300),  # Famous one!
    ("GW190527_092055", 36.5, 22.6, 24.8, 0.40, 2320),
    ("GW190602_175927", 69.1, 47.8, 49.0, 0.67, 4200),
    ("GW190620_030421", 57.1, 36.2, 38.8, 0.51, 3120),
    ("GW190630_185205", 35.1, 23.6, 24.9, 0.23, 1210),
    ("GW190701_203306", 53.9, 40.8, 40.6, 0.49, 2970),
    ("GW190706_222641", 67.0, 38.2, 43.2, 0.57, 3620),
    ("GW190707_093326", 12.3, 8.5, 8.9, 0.11, 530),
    ("GW190708_232457", 17.8, 13.2, 13.3, 0.16, 790),
    ("GW190719_215514", 36.5, 25.2, 26.2, 0.44, 2560),
    ("GW190720_000836", 13.4, 7.8, 8.8, 0.13, 630),
    ("GW190727_060333", 38.0, 27.5, 28.1, 0.38, 2200),
    ("GW190728_064510", 12.3, 8.1, 8.7, 0.07, 330),
    ("GW190731_140936", 42.0, 27.4, 29.5, 0.47, 2780),
    ("GW190803_022701", 37.3, 27.2, 27.6, 0.38, 2230),
    ("GW190805_211137", 33.0, 23.2, 24.0, 0.35, 1990),
    ("GW190828_063405", 32.1, 26.2, 25.1, 0.21, 1070),
    ("GW190828_065509", 24.1, 9.8, 13.1, 0.24, 1240),
    ("GW190910_112807", 44.5, 33.1, 33.3, 0.47, 2760),
    ("GW190915_235702", 35.3, 24.4, 25.4, 0.28, 1510),
    ("GW190924_021846", 8.9, 5.8, 6.2, 0.06, 280),
    ("GW190929_012149", 80.8, 55.4, 57.0, 0.73, 4680),
    ("GW190930_133541", 12.4, 7.8, 8.5, 0.12, 600),
    # O3b Events (selected BBH)
    ("GW191103_012549", 11.9, 8.0, 8.4, 0.12, 580),
    ("GW191105_143521", 10.7, 7.3, 7.7, 0.09, 430),
    ("GW191109_010717", 65.0, 47.0, 47.4, 0.50, 3040),
    ("GW191127_050227", 29.8, 22.6, 22.5, 0.33, 1870),
    ("GW191129_134029", 10.7, 6.7, 7.3, 0.07, 320),
    ("GW191204_171526", 11.9, 8.2, 8.5, 0.10, 490),
    ("GW191215_223052", 24.0, 18.0, 18.0, 0.25, 1340),
    ("GW191216_213338", 12.1, 7.7, 8.3, 0.07, 340),
    ("GW191222_033537", 47.6, 29.4, 32.4, 0.37, 2140),
    ("GW200112_155838", 34.7, 27.6, 26.8, 0.26, 1390),
    ("GW200128_022011", 39.2, 26.1, 27.6, 0.31, 1730),
    ("GW200129_065458", 34.5, 28.8, 27.3, 0.28, 1520),
    ("GW200202_154313", 10.1, 7.3, 7.4, 0.08, 400),
    ("GW200208_130117", 37.9, 27.6, 28.1, 0.36, 2050),
    ("GW200209_085452", 35.6, 27.1, 26.8, 0.41, 2370),
    ("GW200216_220804", 61.0, 32.9, 38.3, 0.51, 3110),
    ("GW200219_094415", 37.5, 27.9, 28.0, 0.38, 2200),
    ("GW200224_222234", 40.0, 32.5, 31.3, 0.40, 2330),
    ("GW200225_060421", 19.3, 14.0, 14.2, 0.18, 890),
    ("GW200302_015811", 36.0, 27.4, 27.2, 0.35, 1990),
    ("GW200306_093714", 18.8, 12.6, 13.2, 0.20, 1010),
    ("GW200308_173609", 31.2, 24.9, 24.1, 0.34, 1910),
    ("GW200311_115853", 34.2, 27.6, 26.6, 0.28, 1500),
    ("GW200316_215756", 13.1, 7.8, 8.8, 0.11, 530),
    ("GW200322_091133", 36.9, 27.7, 27.7, 0.45, 2640),
]


def load_gwtc3_data():
    """Load GWTC-3 BBH events."""
    print("📖 Loading GWTC-3 BBH Events...")

    names = [e[0] for e in GWTC3_BBH_EVENTS]
    m1 = np.array([e[1] for e in GWTC3_BBH_EVENTS])
    m2 = np.array([e[2] for e in GWTC3_BBH_EVENTS])
    m_chirp = np.array([e[3] for e in GWTC3_BBH_EVENTS])
    z = np.array([e[4] for e in GWTC3_BBH_EVENTS])
    d_L = np.array([e[5] for e in GWTC3_BBH_EVENTS])

    # Total mass
    m_total = m1 + m2

    data = {
        "name": names,
        "m1": m1,
        "m2": m2,
        "m_total": m_total,
        "m_chirp": m_chirp,
        "z": z,
        "d_L": d_L,
    }

    print(f"   ✅ Loaded {len(names)} BBH merger events")
    print(f"   z range: {z.min():.2f} - {z.max():.2f}")
    print(f"   M_total range: {m_total.min():.1f} - {m_total.max():.1f} M☉")

    return data


def analyze_ccbh_gw(data):
    """Analyze CCBH hypothesis using GW data."""

    print("\n" + "=" * 60)
    print("📈 CCBH ANALYSIS - GRAVITATIONAL WAVE DATA")
    print("=" * 60)

    z = data["z"]
    m_total = data["m_total"]
    m1 = data["m1"]

    # Use primary mass (larger BH)
    log_m1 = np.log10(m1)

    # Scale factor
    a = 1.0 / (1.0 + z)
    log_a = np.log10(a)

    print(f"\n📊 SAMPLE STATISTICS:")
    print(f"   N = {len(z)}")
    print(f"   z range: {z.min():.2f} - {z.max():.2f}")
    print(f"   <z> = {np.mean(z):.2f} ± {np.std(z):.2f}")
    print(f"   M₁ range: {m1.min():.1f} - {m1.max():.1f} M☉")
    print(f"   <log M₁> = {np.mean(log_m1):.2f} ± {np.std(log_m1):.2f}")

    # CCBH model: log(M) = log(M_0) + k * log(a)
    def ccbh_model(log_a, log_M0, k):
        return log_M0 + k * log_a

    # Fit free k
    popt, pcov = curve_fit(ccbh_model, log_a, log_m1)
    log_M0, k_fit = popt
    log_M0_err, k_err = np.sqrt(np.diag(pcov))

    print(f"\n📈 CCBH FIT (free k):")
    print(f"   k = {k_fit:.3f} ± {k_err:.3f}")
    print(f"   log(M₀/M☉) = {log_M0:.2f} ± {log_M0_err:.2f}")

    # Compare to predictions
    sigma_zero = abs(k_fit - 0) / k_err
    sigma_uet = abs(k_fit - 2.8) / k_err
    sigma_farrah = abs(k_fit - 3.0) / k_err

    print(f"\n📊 DEVIATION FROM PREDICTIONS:")
    print(f"   k = 0 (no coupling): {sigma_zero:.2f}σ")
    print(f"   k = 2.8 (UET): {sigma_uet:.2f}σ")
    print(f"   k = 3.0 (Farrah): {sigma_farrah:.2f}σ")

    # Interpretation
    print(f"\n🎯 INTERPRETATION:")
    if abs(k_fit) < k_err:
        print(f"   k ≈ 0: Data consistent with NO cosmological coupling")
    elif k_fit > 0:
        print(f"   k > 0: Possible evidence for cosmological coupling!")
        if abs(k_fit - 2.8) < 2 * k_err:
            print(f"   → Consistent with UET prediction (k = 2.8)!")
    else:
        print(f"   k < 0: Selection effects or astrophysical evolution")

    # Note about GW mass evolution
    print(f"\n💡 IMPORTANT CAVEATS:")
    print(f"   1. GW BHs come from STELLAR evolution (not SMBHs)")
    print(f"   2. Mass range ~10-100 M☉ (very different from quasars)")
    print(f"   3. Higher z → earlier universe → younger stars")
    print(f"   4. Metallicity effects complicate interpretation")
    print(f"   5. CCBH hypothesis originally for SMBHs, not stellar BHs")

    return {
        "k": k_fit,
        "k_err": k_err,
        "log_M0": log_M0,
        "z": z,
        "log_m1": log_m1,
    }


def generate_plots(data, result):
    """Generate comprehensive plots."""

    print("\n📊 GENERATING PLOTS...")

    z = data["z"]
    m1 = data["m1"]
    m_total = data["m_total"]
    log_m1 = result["log_m1"]

    a = 1.0 / (1.0 + z)
    log_a = np.log10(a)

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # Plot 1: M1 vs z
    ax1 = axes[0, 0]
    ax1.scatter(z, m1, s=80, c="blue", alpha=0.6, edgecolors="black")
    ax1.set_xlabel("Redshift z", fontsize=12)
    ax1.set_ylabel(r"Primary Mass M$_1$ (M$_\odot$)", fontsize=12)
    ax1.set_title("GWTC-3: BH Primary Mass vs Redshift", fontsize=14)
    ax1.grid(alpha=0.3)

    # Highlight special events
    gw190521_idx = data["name"].index("GW190521")
    ax1.scatter(
        [z[gw190521_idx]],
        [m1[gw190521_idx]],
        s=200,
        c="red",
        marker="*",
        label="GW190521 (85 M☉)",
        zorder=10,
    )
    ax1.legend()

    # Plot 2: log(M1) vs log(a) with CCBH fits
    ax2 = axes[0, 1]
    ax2.scatter(log_a, log_m1, s=80, c="blue", alpha=0.6, edgecolors="black")

    # Model lines
    log_a_model = np.linspace(log_a.min() - 0.1, log_a.max() + 0.1, 100)

    for k, color, label in [
        (0, "gray", "k=0"),
        (result["k"], "blue", f'Best fit: k={result["k"]:.1f}'),
        (2.8, "green", "k=2.8 (UET)"),
        (3, "red", "k=3 (Farrah)"),
    ]:
        y = result["log_M0"] + k * log_a_model
        style = "-" if k == result["k"] else "--"
        ax2.plot(log_a_model, y, style, color=color, linewidth=2, label=label)

    ax2.set_xlabel("log(a) = log(1/(1+z))", fontsize=12)
    ax2.set_ylabel(r"log(M$_1$ / M$_\odot$)", fontsize=12)
    ax2.set_title("CCBH Test: log(M) vs log(a)", fontsize=14)
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Plot 3: Mass distribution
    ax3 = axes[1, 0]
    ax3.hist(m1, bins=20, color="blue", alpha=0.7, edgecolor="black")
    ax3.axvline(
        np.median(m1),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Median = {np.median(m1):.1f} M☉",
    )
    ax3.set_xlabel(r"Primary Mass M$_1$ (M$_\odot$)", fontsize=12)
    ax3.set_ylabel("Count", fontsize=12)
    ax3.set_title("Mass Distribution of GW Black Holes", fontsize=14)
    ax3.legend()
    ax3.grid(alpha=0.3)

    # Plot 4: z distribution
    ax4 = axes[1, 1]
    ax4.hist(z, bins=15, color="green", alpha=0.7, edgecolor="black")
    ax4.axvline(
        np.median(z),
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Median z = {np.median(z):.2f}",
    )
    ax4.set_xlabel("Redshift z", fontsize=12)
    ax4.set_ylabel("Count", fontsize=12)
    ax4.set_title("Redshift Distribution of GW Events", fontsize=14)
    ax4.legend()
    ax4.grid(alpha=0.3)

    plt.tight_layout()

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "ccbh_gravitational_waves.png"
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"   ✅ Saved: {output_path}")

    return output_path


def main():
    print("\n" + "🌊" * 35)
    print("   CCBH ANALYSIS - GRAVITATIONAL WAVES")
    print("🌊" * 35)

    # Load data
    data = load_gwtc3_data()

    # Analyze
    result = analyze_ccbh_gw(data)

    # Generate plots
    plot_path = generate_plots(data, result)

    # Final summary
    print("\n" + "=" * 60)
    print("🏆 FINAL SUMMARY")
    print("=" * 60)

    print(f"\n📊 GWTC-3 CCBH RESULT:")
    print(f"   k = {result['k']:.2f} ± {result['k_err']:.2f}")
    print(f"   log(M₀) = {result['log_M0']:.2f}")

    k = result["k"]
    k_err = result["k_err"]

    if abs(k) < 2 * k_err:
        verdict = "❓ INCONCLUSIVE - Cannot distinguish k=0 from k>0"
    elif k > 2 and k < 4:
        verdict = "✅ POSSIBLE SUPPORT for cosmological coupling!"
    elif k > 0:
        verdict = "⚠️ WEAK EVIDENCE for positive k"
    else:
        verdict = "❌ NO SUPPORT for CCBH (k < 0)"

    print(f"\n🎯 VERDICT: {verdict}")

    print(f"\n💡 KEY INSIGHT:")
    print(f"   GW black holes are STELLAR-mass (10-100 M☉)")
    print(f"   CCBH was proposed for SUPERmassive BHs (10⁶-10¹⁰ M☉)")
    print(f"   The physics may be different!")

    print("\n" + "🌊" * 35)
    print("   ANALYSIS COMPLETE!")
    print("🌊" * 35)

    return 0


if __name__ == "__main__":
    main()
