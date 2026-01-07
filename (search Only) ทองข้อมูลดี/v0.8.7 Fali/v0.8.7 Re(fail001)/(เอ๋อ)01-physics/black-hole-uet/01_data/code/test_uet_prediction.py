#!/usr/bin/env python3
"""
TEST UET PREDICTION: k ≈ 2.7-2.9 vs CCBH k = 3

This script:
1. Loads Shen 2011 data
2. Applies selection bias corrections (V/Vmax)
3. Fits CCBH model with different k values
4. Tests UET prediction (k ≈ 2.8) vs Farrah (k = 3)
5. Statistical comparison
6. Generates comprehensive plots

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
import sys

# Import our modules
from data_loader import load_and_prepare
from quality_cuts import apply_quality_cuts


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================


def test_uet_prediction(catalog_path, k_uet=2.8, k_farrah=3.0):
    """
    Test UET prediction k ≈ 2.8 against data

    Parameters:
    -----------
    catalog_path : str
        Path to Shen 2011 FITS catalog
    k_uet : float
        UET predicted value (default 2.8)
    k_farrah : float
        Farrah's value (default 3.0)
    """

    print("\n" + "=" * 80)
    print("TESTING UET PREDICTION: k ≈ 2.8 vs CCBH k = 3")
    print("=" * 80)

    # ========================================================================
    # STEP 1: LOAD & CLEAN DATA
    # ========================================================================

    print("\n" + "─" * 80)
    print("STEP 1: LOADING DATA")
    print("─" * 80)

    data = load_and_prepare(catalog_path)
    if data is None:
        print("ERROR: Could not load data!")
        return None

    clean_data = apply_quality_cuts(data)

    z = clean_data["z"]
    log_mbh = clean_data["logMBH"]

    print(f"\n✓ Proceeding with {len(z):,} high-quality quasars")

    # ========================================================================
    # STEP 2: APPLY V/VMAX CORRECTION
    # ========================================================================

    print("\n" + "─" * 80)
    print("STEP 2: APPLYING V/VMAX CORRECTION FOR SELECTION BIAS")
    print("─" * 80)

    # Compute V/Vmax weights
    # Simplified: assume flux limit corresponds to z_max for each object
    # More sophisticated: use actual SDSS selection function

    # For now, use luminosity-based weighting
    # Objects with higher luminosity are over-represented at high-z

    # Bin by redshift for V/Vmax correction
    z_bins = np.linspace(0.1, 5.0, 21)
    z_centers = (z_bins[:-1] + z_bins[1:]) / 2

    corrected_mbh = []
    corrected_z = []
    n_per_bin = []

    for i in range(len(z_bins) - 1):
        in_bin = (z >= z_bins[i]) & (z < z_bins[i + 1])
        n_in_bin = np.sum(in_bin)

        if n_in_bin >= 10:
            # Apply simple V/Vmax: weight by inverse of detection probability
            # Higher-z objects are harder to detect → upweight fainter ones
            mbh_in_bin = log_mbh[in_bin]

            # Simple model: detection probability ∝ L ∝ 10^(2.5*M)
            # Fainter objects (lower M) need higher weight
            weights = 10 ** (-0.5 * (mbh_in_bin - mbh_in_bin.min()))
            weights /= np.sum(weights)  # Normalize

            # Weighted mean (bias-corrected)
            mbh_corrected = np.average(mbh_in_bin, weights=weights)

            corrected_mbh.append(mbh_corrected)
            corrected_z.append(z_centers[i])
            n_per_bin.append(n_in_bin)

    corrected_mbh = np.array(corrected_mbh)
    corrected_z = np.array(corrected_z)
    n_per_bin = np.array(n_per_bin)

    print(f"\n✓ Bias correction applied to {len(corrected_z)} redshift bins")
    print(f"  Objects per bin: {n_per_bin.min():.0f} to {n_per_bin.max():.0f}")

    # ========================================================================
    # STEP 3: FIT CCBH MODEL - FREE k
    # ========================================================================

    print("\n" + "─" * 80)
    print("STEP 3: FITTING CCBH MODEL (FREE k)")
    print("─" * 80)

    a = 1.0 / (1.0 + corrected_z)
    log_a = np.log10(a)

    def ccbh_model(log_a, log_M0, k):
        return log_M0 + k * log_a

    # Fit with free k
    popt_free, pcov_free = curve_fit(ccbh_model, log_a, corrected_mbh)
    log_M0_free, k_free = popt_free
    log_M0_err_free, k_err_free = np.sqrt(np.diag(pcov_free))

    # R-squared
    residuals_free = corrected_mbh - ccbh_model(log_a, *popt_free)
    ss_res_free = np.sum(residuals_free**2)
    ss_tot = np.sum((corrected_mbh - np.mean(corrected_mbh)) ** 2)
    r2_free = 1 - (ss_res_free / ss_tot)

    print(f"\n✓ Free fit results:")
    print(f"  k_fit = {k_free:.3f} ± {k_err_free:.3f}")
    print(f"  log(M₀/M_☉) = {log_M0_free:.2f} ± {log_M0_err_free:.2f}")
    print(f"  R² = {r2_free:.4f}")

    # ========================================================================
    # STEP 4: TEST UET PREDICTION (k = 2.8)
    # ========================================================================

    print("\n" + "─" * 80)
    print("STEP 4: TESTING UET PREDICTION (k = 2.8)")
    print("─" * 80)

    # Fixed k = 2.8, fit only M0
    def ccbh_fixed_k(log_a, log_M0, k_fixed=k_uet):
        return log_M0 + k_fixed * log_a

    popt_uet, pcov_uet = curve_fit(lambda x, m0: ccbh_fixed_k(x, m0, k_uet), log_a, corrected_mbh)
    log_M0_uet = popt_uet[0]
    log_M0_err_uet = np.sqrt(pcov_uet[0, 0])

    # Chi-squared for UET model
    residuals_uet = corrected_mbh - ccbh_fixed_k(log_a, log_M0_uet, k_uet)
    ss_res_uet = np.sum(residuals_uet**2)
    r2_uet = 1 - (ss_res_uet / ss_tot)

    # Reduced chi-squared
    dof_uet = len(corrected_z) - 1  # 1 free parameter (M0)
    chi2_red_uet = ss_res_uet / dof_uet

    print(f"\n✓ UET model (k = {k_uet}):")
    print(f"  log(M₀/M_☉) = {log_M0_uet:.2f} ± {log_M0_err_uet:.2f}")
    print(f"  R² = {r2_uet:.4f}")
    print(f"  χ²/dof = {chi2_red_uet:.3f}")

    # ========================================================================
    # STEP 5: TEST FARRAH PREDICTION (k = 3.0)
    # ========================================================================

    print("\n" + "─" * 80)
    print("STEP 5: TESTING FARRAH PREDICTION (k = 3.0)")
    print("─" * 80)

    popt_farrah, pcov_farrah = curve_fit(
        lambda x, m0: ccbh_fixed_k(x, m0, k_farrah), log_a, corrected_mbh
    )
    log_M0_farrah = popt_farrah[0]
    log_M0_err_farrah = np.sqrt(pcov_farrah[0, 0])

    residuals_farrah = corrected_mbh - ccbh_fixed_k(log_a, log_M0_farrah, k_farrah)
    ss_res_farrah = np.sum(residuals_farrah**2)
    r2_farrah = 1 - (ss_res_farrah / ss_tot)

    dof_farrah = len(corrected_z) - 1
    chi2_red_farrah = ss_res_farrah / dof_farrah

    print(f"\n✓ Farrah model (k = {k_farrah}):")
    print(f"  log(M₀/M_☉) = {log_M0_farrah:.2f} ± {log_M0_err_farrah:.2f}")
    print(f"  R² = {r2_farrah:.4f}")
    print(f"  χ²/dof = {chi2_red_farrah:.3f}")

    # ========================================================================
    # STEP 6: STATISTICAL COMPARISON
    # ========================================================================

    print("\n" + "=" * 80)
    print("STATISTICAL COMPARISON")
    print("=" * 80)

    # Compare k_fit with k_uet and k_farrah
    sigma_from_uet = abs(k_free - k_uet) / k_err_free
    sigma_from_farrah = abs(k_free - k_farrah) / k_err_free

    print(f"\n1. Best-fit k vs predictions:")
    print(f"   k_fit = {k_free:.3f} ± {k_err_free:.3f}")
    print(f"   k_UET = {k_uet:.1f}")
    print(f"   k_Farrah = {k_farrah:.1f}")
    print(f"\n   Deviation from UET: {sigma_from_uet:.2f}σ")
    print(f"   Deviation from Farrah: {sigma_from_farrah:.2f}σ")

    # F-test: compare nested models
    # H0: k = k_uet, H1: k free
    F_uet = ((ss_res_uet - ss_res_free) / 1) / (ss_res_free / (len(corrected_z) - 2))
    p_uet = 1 - stats.f.cdf(F_uet, 1, len(corrected_z) - 2)

    F_farrah = ((ss_res_farrah - ss_res_free) / 1) / (ss_res_free / (len(corrected_z) - 2))
    p_farrah = 1 - stats.f.cdf(F_farrah, 1, len(corrected_z) - 2)

    print(f"\n2. F-test (is fixed k significantly worse than free k?):")
    print(f"   UET (k={k_uet}): F = {F_uet:.3f}, p = {p_uet:.4f}")
    print(f"   Farrah (k={k_farrah}): F = {F_farrah:.3f}, p = {p_farrah:.4f}")

    if p_uet > 0.05:
        print(f"   → UET model NOT significantly worse (p > 0.05) ✓")
    else:
        print(f"   → UET model significantly worse (p < 0.05) ✗")

    if p_farrah > 0.05:
        print(f"   → Farrah model NOT significantly worse (p > 0.05) ✓")
    else:
        print(f"   → Farrah model significantly worse (p < 0.05) ✗")

    # AIC comparison
    n = len(corrected_z)
    aic_free = 2 * 2 + n * np.log(ss_res_free / n)
    aic_uet = 2 * 1 + n * np.log(ss_res_uet / n)
    aic_farrah = 2 * 1 + n * np.log(ss_res_farrah / n)

    print(f"\n3. AIC comparison (lower is better):")
    print(f"   Free k: AIC = {aic_free:.2f}")
    print(f"   UET (k={k_uet}): AIC = {aic_uet:.2f} (Δ = {aic_uet - aic_free:+.2f})")
    print(f"   Farrah (k={k_farrah}): AIC = {aic_farrah:.2f} (Δ = {aic_farrah - aic_free:+.2f})")

    if aic_uet < aic_farrah:
        print(f"   → UET model PREFERRED over Farrah (ΔAIC = {aic_farrah - aic_uet:.2f})")
    else:
        print(f"   → Farrah model PREFERRED over UET (ΔAIC = {aic_uet - aic_farrah:.2f})")

    # ========================================================================
    # STEP 7: GENERATE PLOTS
    # ========================================================================

    print("\n" + "─" * 80)
    print("STEP 7: GENERATING PLOTS")
    print("─" * 80)

    # Create comprehensive plot
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # ---- Plot 1: Data + All Models ----
    ax1 = fig.add_subplot(gs[0, :])

    # Data points
    ax1.errorbar(
        corrected_z,
        corrected_mbh,
        fmt="o",
        markersize=8,
        capsize=5,
        color="black",
        label=f"Corrected data (N={len(corrected_z)})",
        alpha=0.7,
    )

    # Model predictions
    z_model = np.linspace(corrected_z.min(), corrected_z.max(), 100)
    a_model = 1.0 / (1.0 + z_model)
    log_a_model = np.log10(a_model)

    # Free fit
    mbh_free = ccbh_model(log_a_model, log_M0_free, k_free)
    ax1.plot(
        z_model,
        mbh_free,
        "b-",
        linewidth=3,
        alpha=0.8,
        label=f"Best fit: k = {k_free:.2f} ± {k_err_free:.2f}",
    )

    # UET prediction
    mbh_uet = ccbh_fixed_k(log_a_model, log_M0_uet, k_uet)
    ax1.plot(
        z_model,
        mbh_uet,
        "g--",
        linewidth=3,
        alpha=0.8,
        label=f"UET: k = {k_uet} (χ²/dof = {chi2_red_uet:.2f})",
    )

    # Farrah prediction
    mbh_farrah = ccbh_fixed_k(log_a_model, log_M0_farrah, k_farrah)
    ax1.plot(
        z_model,
        mbh_farrah,
        "r:",
        linewidth=3,
        alpha=0.8,
        label=f"Farrah: k = {k_farrah} (χ²/dof = {chi2_red_farrah:.2f})",
    )

    ax1.set_xlabel("Redshift z", fontsize=14)
    ax1.set_ylabel(r"log(M$_{BH}$ / M$_\odot$)", fontsize=14)
    ax1.set_title(
        "CCBH Model Comparison: UET vs Farrah vs Best Fit", fontsize=16, fontweight="bold"
    )
    ax1.legend(fontsize=11, loc="best")
    ax1.grid(alpha=0.3)

    # ---- Plot 2: Residuals Comparison ----
    ax2 = fig.add_subplot(gs[1, 0])

    ax2.errorbar(
        corrected_z,
        residuals_free,
        fmt="o",
        markersize=6,
        color="blue",
        alpha=0.6,
        label="Free fit",
    )
    ax2.errorbar(
        corrected_z,
        residuals_uet,
        fmt="s",
        markersize=6,
        color="green",
        alpha=0.6,
        label=f"UET (k={k_uet})",
    )
    ax2.errorbar(
        corrected_z,
        residuals_farrah,
        fmt="^",
        markersize=6,
        color="red",
        alpha=0.6,
        label=f"Farrah (k={k_farrah})",
    )

    ax2.axhline(0, color="black", linestyle="--", linewidth=2)
    ax2.set_xlabel("Redshift z", fontsize=12)
    ax2.set_ylabel("Residuals (dex)", fontsize=12)
    ax2.set_title("Model Residuals", fontsize=14, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.grid(alpha=0.3)

    # ---- Plot 3: Chi-squared Comparison ----
    ax3 = fig.add_subplot(gs[1, 1])

    models = ["Free k", f"UET\nk={k_uet}", f"Farrah\nk={k_farrah}"]
    chi2_values = [ss_res_free / (len(corrected_z) - 2), chi2_red_uet, chi2_red_farrah]
    colors_bar = ["blue", "green", "red"]

    bars = ax3.bar(models, chi2_values, color=colors_bar, alpha=0.7, edgecolor="black")
    ax3.set_ylabel("χ²/dof", fontsize=12)
    ax3.set_title("Model Quality Comparison", fontsize=14, fontweight="bold")
    ax3.axhline(1.0, color="gray", linestyle="--", linewidth=2, label="Perfect fit", alpha=0.5)
    ax3.legend(fontsize=10)
    ax3.grid(alpha=0.3, axis="y")

    # Add value labels on bars
    for bar, val in zip(bars, chi2_values):
        height = bar.get_height()
        ax3.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=11,
        )

    plt.tight_layout()
    plt.savefig("uet_prediction_test.png", dpi=200, bbox_inches="tight")
    print("✓ Saved: uet_prediction_test.png")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   Best-fit k = {k_free:.2f} ± {k_err_free:.2f}")
    print(f"   UET prediction k = {k_uet}")
    print(f"   Farrah prediction k = {k_farrah}")

    print(f"\n🎯 STATISTICAL COMPARISON:")

    if abs(k_free - k_uet) < abs(k_free - k_farrah):
        winner = "UET"
        print(f"   ✓ Data CLOSER to UET prediction!")
        print(f"     |k_fit - k_UET| = {abs(k_free - k_uet):.3f}")
        print(f"     |k_fit - k_Farrah| = {abs(k_free - k_farrah):.3f}")
    else:
        winner = "FARRAH"
        print(f"   ✓ Data CLOSER to Farrah prediction!")
        print(f"     |k_fit - k_Farrah| = {abs(k_free - k_farrah):.3f}")
        print(f"     |k_fit - k_UET| = {abs(k_free - k_uet):.3f}")

    if p_uet > 0.05 and p_farrah > 0.05:
        print(f"\n   ✓ Both models statistically acceptable (p > 0.05)")
        print(f"   → Cannot distinguish based on current data!")
    elif p_uet > 0.05 and p_farrah <= 0.05:
        print(f"\n   ✓ UET model acceptable, Farrah rejected!")
        print(f"   → UET WINS!")
    elif p_uet <= 0.05 and p_farrah > 0.05:
        print(f"\n   ✓ Farrah model acceptable, UET rejected!")
        print(f"   → FARRAH WINS!")
    else:
        print(f"\n   ✗ Both models rejected (p < 0.05)")
        print(f"   → Need better model or more data!")

    print(f"\n💡 INTERPRETATION:")
    if sigma_from_uet < 1 and sigma_from_farrah < 1:
        print(f"   Both UET and Farrah within 1σ of best fit")
        print(f"   → Current data cannot distinguish!")
        print(f"   → Need more data or better corrections!")
    elif sigma_from_uet < sigma_from_farrah:
        print(f"   UET ({sigma_from_uet:.1f}σ) closer than Farrah ({sigma_from_farrah:.1f}σ)")
        print(f"   → Weak evidence for UET!")
    else:
        print(f"   Farrah ({sigma_from_farrah:.1f}σ) closer than UET ({sigma_from_uet:.1f}σ)")
        print(f"   → Weak evidence for Farrah!")

    print(f"\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

    return {
        "k_free": k_free,
        "k_err": k_err_free,
        "k_uet": k_uet,
        "k_farrah": k_farrah,
        "chi2_free": ss_res_free / (len(corrected_z) - 2),
        "chi2_uet": chi2_red_uet,
        "chi2_farrah": chi2_red_farrah,
        "p_uet": p_uet,
        "p_farrah": p_farrah,
        "winner": winner,
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        catalog_path = sys.argv[1]
    else:
        catalog_path = "shen2011.fits"

    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "UET PREDICTION TEST - CCBH ANALYSIS" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")

    results = test_uet_prediction(catalog_path, k_uet=2.8, k_farrah=3.0)

    print(f"\n🎉 Ready to see results in: uet_prediction_test.png")
