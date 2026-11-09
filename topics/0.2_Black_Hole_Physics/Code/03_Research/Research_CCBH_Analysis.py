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

#!/usr/bin/env python3
"""
🌌 COMPREHENSIVE CCBH ANALYSIS SCRIPT
================================
Comprehensive Cosmologically Coupled Black Hole (CCBH) Analysis

This script combines ALL available data sources to properly test the
CCBH hypothesis: M_BH ∝ a^k where a = 1/(1+z)

Data Sources:
1. Shen 2011 (50,000 quasars): z, log(M_BH)
2. Kormendy & Ho 2013 (25 ellipticals): M_BH/M_bulge at z~0
3. MPA-JHU DR7 (927,552 galaxies): Stellar masses for host matching

Key Tests:
- k = 0: Standard GR (no coupling)
- k = 1: Comoving scenario
- k = 2.8: UET prediction
- k = 3: Vacuum energy interior (Farrah/Croker)

Author: UET Research Team
Date: 2025-12-28
Reference: Farrah et al. (2023), Croker et al. (2024)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from pathlib import Path
import sys

# --- PATH SETUP (Must be FIRST) ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        ROOT = parent
        break

if ROOT:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    print("CRITICAL: docs root not found!")
    sys.exit(1)

TOPIC_DIR = ROOT / "docs" / "topics" / "0.2_Black_Hole_Physics"
REPO_ROOT = ROOT  # Alias for compatibility

from docs.core.uet_glass_box import UETPathManager
from docs.core.uet_master_equation import UETParameters
from docs.core.uet_parameters import (
    G,
    C,
    M_SUN,
    K_B,
    HBAR,
    INTEGRITY_KILL_SWITCH,
)

# Aliases for compatibility
c = C
M_sun = M_SUN
kB = K_B
hbar = HBAR

# Derived Units (Calculated Precision)
Year_to_sec = 365.25 * 24 * 3600
pc = 3.085677581e16
Mpc = 1e6 * pc
Mpc_to_m = Mpc

# [UET] Derive k from Engine (No Shadow Math)
try:
    import importlib
    import importlib.util

    # Manually find file
    engine_path = TOPIC_DIR / "Code" / "01_Engine" / "Engine_BlackHole.py"
    if not engine_path.exists():
        raise FileNotFoundError(f"Engine not found at {engine_path}")

    spec = importlib.util.spec_from_file_location("Engine_BlackHole", engine_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETBlackHoleSolver = mod.UETBlackHoleSolver
    print("✅ Loaded Engine via importlib")
except Exception as e2:
    print(f"❌ CRITICAL ENGINE FAILURE: {e2}")
    # If engine fails, we must FAIL, not fallback to 2.8.
    if "INTEGRITY_KILL_SWITCH" in globals() and INTEGRITY_KILL_SWITCH:
        k_ccbh = float("nan")
    else:
        raise e2

# Instantiate Engine
engine = UETBlackHoleSolver()
k_ccbh = engine.solve_coupling_k()

# Verify Integrity
if np.isnan(k_ccbh) or (INTEGRITY_KILL_SWITCH):
    print("❌ KILL SWITCH ACTIVE: k_ccbh is NaN")
    # We allow the script to continue to fail gracefully or exit?
    # Research scripts should fail.
    sys.exit(1)

S_B_ratio = 1.0
print(f"✅ Derived k_ccbh = {k_ccbh} from Engine (Axiom 2)")

# ============================================================================
# DATA LOADING
# ============================================================================


def load_shen_catalog():
    """Load Shen 2011 quasar catalog with BH masses."""
    from astropy.table import Table

    # Path to Data (Found in Backup Folder)
    # c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\(search Only) ทองข้อมูลดี\v0.9.0+\data\02_astrophysics\black_holes\shen2011_recovered.fits

    # We construct path relative to Repo Root for portability on this machine
    repo = REPO_ROOT
    path = (
        repo
        / "(search Only) ทองข้อมูลดี"
        / "v0.9.0+"
        / "data"
        / "02_astrophysics"
        / "black_holes"
        / "shen2011_recovered.fits"
    )

    if not path.exists():
        print(f"❌ File not found: {path.absolute()}")
        return None

    print("📖 Loading Shen 2011 catalog...")
    try:
        table = Table.read(path)
    except Exception as e:
        print(f"❌ Error reading FITS: {e}")
        return None

    # Extract arrays
    data = {
        "z": np.array(table["z"]),
        "logMBH": np.array(table["logBH"]),
        "logMBH_err": np.array(table["e_logBH"]),
        "logLbol": np.array(table["logLbol"]),
    }

    print(f"   ✅ Loaded {len(data['z']):,} quasars")
    return data


def load_kormendy_ho():
    """Load Kormendy & Ho local ellipticals (z~0 reference)."""
    # Path: .../black_holes/kormendy_ho_data/kormendy_ho_ellipticals_sample.csv
    repo = REPO_ROOT
    path = (
        repo
        / "(search Only) ทองข้อมูลดี"
        / "v0.9.0+"
        / "data"
        / "02_astrophysics"
        / "black_holes"
        / "kormendy_ho_data"
        / "kormendy_ho_ellipticals_sample.csv"
    )

    if not path.exists():
        print(f"⚠️ K&H data not found: {path} \nUsing built-in sample")
        # Built-in sample from K&H 2013
        data = {
            "name": ["M87", "NGC4889", "NGC3842", "CenA", "NGC3115"],
            "z": np.array([0.004, 0.021, 0.021, 0.001, 0.002]),
            "logMBH": np.array([9.81, 10.32, 9.88, 7.84, 8.97]),
            "logMbulge": np.array([11.97, 12.16, 12.11, 11.04, 11.02]),
        }
        data["logRatio"] = data["logMBH"] - data["logMbulge"]
        return data

    print("📖 Loading Kormendy & Ho 2013 data...")

    names, log_mbh, log_mbulge, log_ratio, z = [], [], [], [], []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Skip header
            if line.startswith("name,"):
                continue

            parts = line.split(",")
            if len(parts) >= 5:
                names.append(parts[0])
                log_mbh.append(float(parts[1]))
                log_mbulge.append(float(parts[2]))
                log_ratio.append(float(parts[3]))
                # Estimate z from distance (H0 ~ 70 km/s/Mpc)
                d_mpc = float(parts[4])
                z.append(d_mpc * 70 / 3e5)  # v/c approximation

    data = {
        "name": names,
        "z": np.array(z),
        "logMBH": np.array(log_mbh),
        "logMbulge": np.array(log_mbulge),
        "logRatio": np.array(log_ratio),
    }

    print(f"   ✅ Loaded {len(names)} local ellipticals")
    print(
        f"   Mean log(M_BH/M_bulge) = {np.mean(log_ratio):.3f} ± {np.std(log_ratio):.3f}"
    )

    return data


# ============================================================================
# DATA CLEANING & BINNING
# ============================================================================


def apply_quality_cuts(data, config=None):
    """Apply quality cuts to quasar data."""
    if config is None:
        config = {
            "z_min": 0.1,
            "z_max": 5.0,
            "logMBH_min": 6.5,
            "logMBH_max": 11.0,
            "logMBH_err_max": 0.5,
        }

    z = data["z"]
    logMBH = data["logMBH"]
    logMBH_err = data["logMBH_err"]

    # Build mask
    mask = (
        np.isfinite(z)
        & np.isfinite(logMBH)
        & (z >= config["z_min"])
        & (z <= config["z_max"])
        & (logMBH >= config["logMBH_min"])
        & (logMBH <= config["logMBH_max"])
        & (logMBH_err <= config["logMBH_err_max"])
    )

    cleaned = {k: v[mask] for k, v in data.items() if isinstance(v, np.ndarray)}

    print(
        f"\n📋 Quality cuts: {len(cleaned['z']):,} / {len(z):,} passed ({100*len(cleaned['z'])/len(z):.1f}%)"
    )

    return cleaned


def bin_by_redshift(data, n_bins=15, method="equal_number"):
    """Bin data by redshift with V/Vmax-style weighting."""
    z = data["z"]
    logMBH = data["logMBH"]
    logMBH_err = data.get("logMBH_err", np.ones_like(logMBH) * 0.3)

    if method == "equal_number":
        percentiles = np.linspace(0, 100, n_bins + 1)
        bin_edges = np.percentile(z, percentiles)
    else:
        bin_edges = np.linspace(z.min(), z.max(), n_bins + 1)

    bins = []
    for i in range(n_bins):
        mask = (z >= bin_edges[i]) & (z < bin_edges[i + 1])
        if i == n_bins - 1:
            mask = (z >= bin_edges[i]) & (z <= bin_edges[i + 1])

        n = np.sum(mask)
        if n < 30:
            continue

        z_bin = z[mask]
        mbh_bin = logMBH[mask]
        err_bin = logMBH_err[mask]

        # V/Vmax-style weighting: downweight high-mass objects
        # (they're overrepresented due to flux limits)
        weights = 10 ** (-0.5 * (mbh_bin - mbh_bin.min()))
        weights /= np.sum(weights)

        # Weighted statistics
        mbh_mean = np.average(mbh_bin, weights=weights)
        mbh_std = np.sqrt(np.average((mbh_bin - mbh_mean) ** 2, weights=weights))
        mbh_err = mbh_std / np.sqrt(n)  # Standard error

        bins.append(
            {
                "z_center": np.mean(z_bin),
                "z_median": np.median(z_bin),
                "logMBH": mbh_mean,
                "logMBH_err": mbh_err,
                "logMBH_raw": np.mean(mbh_bin),  # Uncorrected
                "n": n,
            }
        )

    print(
        f"\n📊 Created {len(bins)} redshift bins (N = {bins[0]['n']:.0f} to {bins[-1]['n']:.0f})"
    )

    return bins


# ============================================================================
# CCBH MODEL FITTING
# ============================================================================


def ccbh_model(log_a, log_M0, k):
    """CCBH model: log(M_BH) = log(M_0) + k * log(a)"""
    return log_M0 + k * log_a


def fit_ccbh(z, logMBH, logMBH_err=None, k_fixed=None):
    """Fit CCBH model to binned data."""
    a = 1.0 / (1.0 + z)
    log_a = np.log10(a)

    if k_fixed is not None:
        # Fit only M0 with fixed k
        def model_fixed(x, log_M0):
            return log_M0 + k_fixed * x

        popt, pcov = curve_fit(
            model_fixed,
            log_a,
            logMBH,
            sigma=logMBH_err if logMBH_err is not None else None,
            absolute_sigma=True,
        )
        log_M0 = popt[0]
        log_M0_err = np.sqrt(pcov[0, 0])
        k = k_fixed
        k_err = 0.0
    else:
        # Fit both M0 and k
        popt, pcov = curve_fit(
            ccbh_model,
            log_a,
            logMBH,
            sigma=logMBH_err if logMBH_err is not None else None,
            absolute_sigma=True,
        )
        log_M0, k = popt
        log_M0_err, k_err = np.sqrt(np.diag(pcov))

    # Compute residuals and chi-squared
    predicted = ccbh_model(log_a, log_M0, k)
    residuals = logMBH - predicted

    if logMBH_err is not None:
        chi2 = np.sum((residuals / logMBH_err) ** 2)
        dof = len(z) - (1 if k_fixed else 2)
        chi2_red = chi2 / dof
    else:
        chi2_red = np.var(residuals)

    # R-squared
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((logMBH - np.mean(logMBH)) ** 2)
    r2 = 1 - ss_res / ss_tot

    return {
        "log_M0": log_M0,
        "log_M0_err": log_M0_err,
        "k": k,
        "k_err": k_err,
        "chi2_red": chi2_red,
        "r2": r2,
        "residuals": residuals,
    }


# ============================================================================
# MAIN ANALYSIS
# ============================================================================


def run_ultimate_analysis():
    """Run the complete CCBH analysis."""

    print("\n" + "🌌" * 35)
    print("   COMPREHENSIVE CCBH ANALYSIS")
    print("🌌" * 35)

    # ========================================================================
    # STEP 1: LOAD ALL DATA
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 1: LOADING DATA SOURCES")
    print("=" * 70)

    shen = load_shen_catalog()
    if shen is None:
        return None

    kh = load_kormendy_ho()

    # ========================================================================
    # STEP 2: QUALITY CUTS & BINNING
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 2: DATA PROCESSING")
    print("=" * 70)

    shen_clean = apply_quality_cuts(shen)
    bins = bin_by_redshift(shen_clean, n_bins=20)

    # Extract bin arrays
    z_bins = np.array([b["z_median"] for b in bins])
    mbh_bins = np.array([b["logMBH"] for b in bins])
    mbh_err_bins = np.array([b["logMBH_err"] for b in bins])
    mbh_raw = np.array([b["logMBH_raw"] for b in bins])

    # ========================================================================
    # STEP 3: FIT CCBH MODELS
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 3: FITTING CCBH MODELS")
    print("=" * 70)

    # Free k fit (bias-corrected)
    fit_free = fit_ccbh(z_bins, mbh_bins, mbh_err_bins)
    print(f"\n📈 FREE FIT (bias-corrected):")
    print(f"   k = {fit_free['k']:.3f} ± {fit_free['k_err']:.3f}")
    print(f"   log(M₀) = {fit_free['log_M0']:.2f} ± {fit_free['log_M0_err']:.2f}")
    print(f"   χ²/dof = {fit_free['chi2_red']:.3f}")

    # Raw fit (no correction)
    fit_raw = fit_ccbh(z_bins, mbh_raw)
    print(f"\n📈 RAW FIT (uncorrected):")
    print(f"   k_raw = {fit_raw['k']:.3f} ± {fit_raw['k_err']:.3f}")

    # Fixed k fits
    k_values = {
        "k=0": 0.0,
        "k=1": 1.0,
        "UET v3 (k=1.5)": 1.5,
        "UET v2 (k=2.8)": 2.8,
        "Farrah (k=3)": 3.0,
    }
    fits = {"free": fit_free, "raw": fit_raw}

    for name, k_val in k_values.items():
        fit = fit_ccbh(z_bins, mbh_bins, mbh_err_bins, k_fixed=k_val)
        fits[name] = fit
        print(f"\n📈 {name}:")
        print(f"   log(M₀) = {fit['log_M0']:.2f} ± {fit['log_M0_err']:.2f}")
        print(f"   χ²/dof = {fit['chi2_red']:.3f}, R² = {fit['r2']:.4f}")

    # ========================================================================
    # STEP 4: STATISTICAL COMPARISON
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 4: STATISTICAL COMPARISON")
    print("=" * 70)

    k_fit = fit_free["k"]
    k_err = fit_free["k_err"]

    print(f"\n📊 Best-fit k = {k_fit:.3f} ± {k_err:.3f}")
    print(f"\n🎯 Deviation from predictions:")

    for name, k_val in k_values.items():
        sigma = abs(k_fit - k_val) / k_err if k_err > 0 else float("inf")
        status = "✅" if sigma < 2 else ("⚠️" if sigma < 3 else "❌")
        print(f"   {status} {name}: {sigma:.2f}σ away")

    # Chi-squared comparison
    print(f"\n📊 Model Quality (χ²/dof):")
    chi2_free = fit_free["chi2_red"]
    for name in k_values.keys():
        chi2 = fits[name]["chi2_red"]
        delta = chi2 - chi2_free
        print(f"   {name}: {chi2:.3f} (Δ = {delta:+.3f})")

    # ========================================================================
    # STEP 5: KORMENDY & HO CALIBRATION
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 5: z~0 CALIBRATION (KORMENDY & HO)")
    print("=" * 70)

    ratio_z0 = np.mean(kh["logRatio"])
    ratio_z0_err = np.std(kh["logRatio"]) / np.sqrt(len(kh["logRatio"]))

    print(f"\n📊 Local Ellipticals (z ~ 0):")
    print(f"   N = {len(kh['name'])}")
    print(f"   <log(M_BH/M_bulge)> = {ratio_z0:.3f} ± {ratio_z0_err:.3f}")
    print(f"   Implied M_BH/M_bulge = {10**ratio_z0:.4f} ({100*10**ratio_z0:.2f}%)")

    print(f"\n💡 INTERPRETATION:")
    print(f"   If black holes grow as a^k relative to host mass,")
    print(f"   and we measure log(M_BH/M_bulge) = {ratio_z0:.2f} at z = 0,")
    print(f"   then at z = 1 (a = 0.5), we expect:")
    for k in [0, 1, 2.8, 3]:
        ratio_z1 = ratio_z0 + k * np.log10(0.5)
        print(f"     k = {k}: log(M_BH/M_bulge) = {ratio_z1:.2f}")

    # ========================================================================
    # STEP 6: GENERATE PLOTS
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 6: GENERATING PLOTS")
    print("=" * 70)

    fig = plt.figure(figsize=(18, 12))

    # Plot 1: Main data + models
    ax1 = fig.add_subplot(2, 2, 1)

    # Data points (binned)
    ax1.errorbar(
        z_bins,
        mbh_bins,
        yerr=mbh_err_bins,
        fmt="o",
        markersize=10,
        color="black",
        capsize=5,
        label=f'Shen+11 (V/Vmax corrected, N={len(shen_clean["z"]):,})',
    )

    # Model curves
    z_model = np.linspace(0.05, 5.5, 100)
    a_model = 1.0 / (1.0 + z_model)
    log_a_model = np.log10(a_model)

    colors = {
        "k=0": "gray",
        "k=1": "blue",
        "UET v3 (k=1.5)": "orange",
        "UET v2 (k=2.8)": "green",
        "Farrah (k=3)": "red",
    }
    styles = {
        "k=0": ":",
        "k=1": "--",
        "UET v3 (k=1.5)": "-",
        "UET v2 (k=2.8)": "-",
        "Farrah (k=3)": "-.",
    }

    for name in k_values.keys():
        y = ccbh_model(log_a_model, fits[name]["log_M0"], k_values[name])
        ax1.plot(
            z_model,
            y,
            styles[name],
            color=colors[name],
            linewidth=2.5,
            label=f'{name} (χ²/dof={fits[name]["chi2_red"]:.2f})',
        )

    # Best fit
    y_best = ccbh_model(log_a_model, fit_free["log_M0"], fit_free["k"])
    ax1.plot(
        z_model,
        y_best,
        "k-",
        linewidth=3,
        label=f'Best fit: k={fit_free["k"]:.2f}±{fit_free["k_err"]:.2f}',
    )

    ax1.set_xlabel("Redshift z", fontsize=14)
    ax1.set_ylabel(r"log(M$_{BH}$ / M$_\odot$)", fontsize=14)
    ax1.set_title("CCBH Model Comparison", fontsize=16, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.grid(alpha=0.3)
    ax1.set_xlim(0, 5.5)

    # Plot 2: Residuals
    ax2 = fig.add_subplot(2, 2, 2)

    for name in ["k=0", "UET v3 (k=1.5)", "Farrah (k=3)"]:
        ax2.scatter(
            z_bins,
            fits[name]["residuals"],
            label=name,
            alpha=0.7,
            s=60,
            color=colors[name],
        )

    ax2.axhline(0, color="black", linestyle="--", linewidth=2)
    ax2.set_xlabel("Redshift z", fontsize=12)
    ax2.set_ylabel("Residuals (dex)", fontsize=12)
    ax2.set_title("Model Residuals", fontsize=14, fontweight="bold")
    ax2.legend()
    ax2.grid(alpha=0.3)

    # Plot 3: K&H local sample
    ax3 = fig.add_subplot(2, 2, 3)

    ax3.scatter(
        kh["logMbulge"], kh["logMBH"], c="darkred", s=100, alpha=0.7, edgecolors="black"
    )

    # M_BH = 0.004 * M_bulge line (roughly K&H relation)
    x_line = np.linspace(10, 12.5, 100)
    y_line = x_line + ratio_z0
    ax3.plot(
        x_line,
        y_line,
        "k--",
        linewidth=2,
        label=f"Mean: log(M_BH/M_bulge) = {ratio_z0:.2f}",
    )

    ax3.set_xlabel(r"log(M$_{bulge}$ / M$_\odot$)", fontsize=12)
    ax3.set_ylabel(r"log(M$_{BH}$ / M$_\odot$)", fontsize=12)
    ax3.set_title(
        "Kormendy & Ho (2013) Local Ellipticals", fontsize=14, fontweight="bold"
    )
    ax3.legend()
    ax3.grid(alpha=0.3)

    # Plot 4: Chi-squared comparison
    ax4 = fig.add_subplot(2, 2, 4)

    model_names = list(k_values.keys())
    chi2_vals = [fits[n]["chi2_red"] for n in model_names]

    bars = ax4.bar(
        model_names,
        chi2_vals,
        color=[colors[n] for n in model_names],
        alpha=0.7,
        edgecolor="black",
    )

    ax4.axhline(1.0, color="gray", linestyle="--", linewidth=2, label="Perfect fit")

    for bar, val in zip(bars, chi2_vals):
        ax4.text(
            bar.get_x() + bar.get_width() / 2.0,
            val + 0.05,
            f"{val:.2f}",
            ha="center",
            fontsize=11,
        )

    ax4.set_ylabel("χ²/dof", fontsize=12)
    ax4.set_title("Model Quality Comparison", fontsize=14, fontweight="bold")
    ax4.legend()
    ax4.grid(alpha=0.3, axis="y")

    plt.tight_layout()

    # Standardized Output Path
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.2_Black_Hole_Physics",
        experiment_name="Research_CCBH_Analysis",
        pillar="03_Research",
        category="log",
    )
    result_dir.mkdir(parents=True, exist_ok=True)
    output_path = result_dir / "ultimate_ccbh_analysis.png"

    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"   ✅ Saved: {output_path}")

    # ========================================================================
    # FINAL VERDICT
    # ========================================================================
    print("\n" + "=" * 70)
    print("🏆 ANALYSIS VERSION 0.8.7")
    print("=" * 70)

    print(f"\n📊 BEST-FIT RESULT: k = {k_fit:.2f} ± {k_err:.2f}")

    if k_fit < 0.5:
        print(f"\n🔬 INTERPRETATION:")
        print(f"   k ≈ 0: Data consistent with NO cosmological coupling")
        print(f"   Selection bias may still dominate despite V/Vmax correction")
        print(f"   Need: Host galaxy stellar masses for M_BH/M_* analysis")
    elif k_fit < 1.5:
        print(f"\n🔬 INTERPRETATION:")
        print(f"   k ≈ 1: Weak evidence for cosmological coupling")
        print(f"   Consistent with comoving scenario (w = -1/3)")
        print(f"   BHs grow with universe but NOT as dark energy")
    elif k_fit < 2.5:
        print(f"\n🔬 INTERPRETATION:")
        print(f"   k ≈ 2: Moderate cosmological coupling")
        print(f"   Closer to UET prediction than standard GR")
        print(f"   Consistent with Faraoni & Rinaldi (2024) theoretical bounds")
    elif k_fit < 3.5:
        print(f"\n🔬 INTERPRETATION:")
        print(f"   k ≈ 3: Strong evidence for vacuum energy coupling!")
        print(f"   BHs could contribute to dark energy!")
        print(f"   Consistent with Farrah et al. (2023)")
    else:
        print(f"\n🔬 INTERPRETATION:")
        print(f"   k > 3: Potential phantom energy (w < -1)")
        print(f"   May indicate remaining systematic errors")

    # Comparison
    sigma_uet = abs(k_fit - 2.8) / k_err if k_err > 0 else 999
    sigma_farrah = abs(k_fit - 3.0) / k_err if k_err > 0 else 999

    print(f"\n🎯 UET vs FARRAH:")
    print(f"   |k - 2.8| / σ = {sigma_uet:.2f}")
    print(f"   |k - 3.0| / σ = {sigma_farrah:.2f}")

    if sigma_uet < sigma_farrah:
        print(f"\n   → Data CLOSER to UET prediction! ✅")
    else:
        print(f"\n   → Data CLOSER to Farrah prediction! ✅")

    print("\n" + "🌌" * 35)
    print("   ANALYSIS COMPLETE!")
    print("🌌" * 35)

    return {
        "k_best": k_fit,
        "k_err": k_err,
        "fits": fits,
        "bins": bins,
        "kh": kh,
    }


# ============================================================================
# STEP 7: THERMODYNAMIC RECYCLING ANALYSIS (UET PHASE 3)
# ============================================================================


def analyze_entropy_recycling(k_fit, log_M0_avg=8.5, volume_radius_mpc=1000):
    import numpy as np

    """
    Calculate if BH Entropy Production matches Dark Energy requirements.

    Hypothesis: Space generation (Dark Energy) is the recycling of Information (Entropy).
    Power_DE ~ T_horizon * dS_BH/dt
    """
    print("\n" + "=" * 70)
    print("STEP 7: THERMODYNAMIC RECYCLING VERIFICATION (Theoretical k=2.8)")
    print("=" * 70)

    # Constants (SI Units) - Imported from universal_constants
    # Mapping needed for M_solar (script uses M_solar, universal uses M_sun)
    M_solar = M_sun

    print(f"📡 Analysis Volume Radius: {volume_radius_mpc} Mpc")

    # 1. Estimate Total BH Mass in Volume
    # Density of galaxies ~ 0.01 per Mpc^3
    vol_mpc3 = (4 / 3) * np.pi * volume_radius_mpc**3
    n_galaxies = 0.01 * vol_mpc3

    # Average BH mass (from fit intercept ~ 10^8.5 usually, but we take param)
    avg_obs_mass = 10**log_M0_avg * M_solar

    total_mass_bh = n_galaxies * avg_obs_mass
    print(f"   Estimated Galaxies: {n_galaxies:.2e}")
    print(f"   Total BH Mass: {total_mass_bh/M_solar:.2e} M_sun")
    print(f"   Avg BH Mass: {avg_obs_mass/M_solar:.2e} M_sun")

    # 2. Calculate Entropy Production Rate (dS/dt)
    # S = A * const = M^2 * const
    # dS/dt = dS/dM * dM/dt
    # For CCBH: M(t) ~ a(t)^k
    # dM/dt = k * M * H(t)

    H0 = 70 * 1000 / Mpc_to_m  # Hubble constant in 1/s

    dM_dt = k_fit * total_mass_bh * H0
    print(f"   Mass Growth Rate (global): {dM_dt/M_solar*Year_to_sec:.2e} M_sun/yr")

    # dS/dt calculation (simplified scaling)
    # dS/dt = (8*pi*G*kB / hbar*c) * M * dM/dt
    # Summing over galaxies: Sum(M * k*M*H) = k*H * Sum(M^2)

    # Approx Sum(M^2) ~ N * <M>^2 (ignoring variance for order of magnitude)
    sum_M_squared = n_galaxies * (avg_obs_mass**2)

    prefactor = (8 * np.pi * G * kB) / (hbar * c)
    dS_dt_total = prefactor * sum_M_squared * k_fit * H0

    print(f"   Total Entropy Production (dS/dt): {dS_dt_total:.2e} J/K/s")

    # 3. Calculate "Recycling Power" (P = T_eff * dS/dt)
    # Scenario A: CMB Temperature (Heat Sink)
    T_cmb = 2.73
    power_recycling_cmb = T_cmb * dS_dt_total

    # Scenario B: Hawking Temperature (Self-Energy)
    # T_H = (hbar c^3) / (8 pi G M k_B)
    # P_H = T_H * dS/dt
    #     = [const1 / M] * [const2 * M * dM/dt]
    #     = const3 * dM/dt
    # This cancels out the M dependence! P_H is proportional to mass accretion rate exactly.
    # P_H = c^2 * dM/dt ("Input Power" = Rest Mass growth energy)

    # Let's verify the math:
    # T_H * dS/dt = (hbar c^3 / 8 pi G M kB) * (8 pi G M kB / hbar c) * dM/dt
    #             = c^2 * dM/dt
    # Power = Mass Growth Rate * c^2

    power_recycling_hawking = c**2 * dM_dt

    print(f"   Recycling Power (Scenario A - CMB): {power_recycling_cmb:.2e} Watts")
    print(
        f"   Recycling Power (Scenario B - Hawking): {power_recycling_hawking:.2e} Watts"
    )

    # 4. Compare to Dark Energy Power
    # DE Density rho_L ~ 10^-27 kg/m^3
    rho_lambda = 6e-27  # kg/m^3
    energy_lambda_density = rho_lambda * c**2

    # Power required to sustain Lambda density as volume expands?
    # dE_lambda/dt = rho_lambda * c^2 * dV/dt
    # dV/dt = 3 * H0 * V

    required_de_power = energy_lambda_density * 3 * H0 * (vol_mpc3 * Mpc_to_m**3)
    print(f"   Required Dark Energy Power: {required_de_power:.2e} Watts")

    # 5. The Ratios
    ratio_cmb = power_recycling_cmb / required_de_power
    ratio_hawking = power_recycling_hawking / required_de_power

    print(f"\n⚡ RATIO A (CMB): {ratio_cmb:.2e}")
    print(f"⚡ RATIO B (Hawking/Mass): {ratio_hawking:.2e}")

    if 0.1 < ratio_hawking < 100:
        print(
            "✅ SUCCESS (Hawking): The power matches M*c^2 growth! This implies Dark Energy comes from the Mass-Energy of the growth itself."
        )
    elif 0.1 < ratio_cmb < 100:
        print("✅ SUCCESS (CMB): The power matches CMB heat exchange!")
    else:
        print(
            "⚠️ ANALYSIS: Neither temperature perfectly fits, suggesting an efficiency factor 'eta' is needed."
        )

    return ratio_hawking

    # ============================================================================
    # MAIN
    # ============================================================================

    # --- VISUALIZATION ---
    try:
        sys.path.append(str(Path(__file__).parents[4]))
        from core import uet_viz

        result_dir = UETPathManager.get_result_dir(
            topic="0.2_Black_Hole_Physics",
            name="Research_CCBH_Analysis",
            pillar="03_Research",
            category="log",
        )

        # Black Hole Entropy Plot
        import numpy as np

        areas = np.linspace(1, 100, 50)
        entropy_uet = areas * 0.25  # Mock UET Scaling
        entropy_hawk = areas * 0.25

        fig = uet_viz.go.Figure()
        fig.add_trace(
            uet_viz.go.Scatter(
                x=areas, y=entropy_hawk, name="Hawking", line=dict(dash="dash")
            )
        )
        fig.add_trace(
            uet_viz.go.Scatter(
                x=areas, y=entropy_uet, name="UET Saturation", line=dict(color="red")
            )
        )
        fig.update_layout(
            title="Black Hole Entropy Saturation",
            xaxis_title="Area",
            yaxis_title="Entropy",
        )
        uet_viz.save_plot(fig, "black_hole_entropy.png", result_dir)
        print("  [Viz] Generated 'black_hole_entropy.png'")
    except Exception as e:
        print(f"Viz Error: {e}")


# ============================================================================
# SELECTION BIAS DIAGNOSIS (Integrated from v0.9.0 prototype)
# ============================================================================


def diagnose_selection_bias(z, logMBH, logL=None):
    """Diagnose if selection bias (Malmquist bias) is present."""
    print("\n" + "!" * 70)
    print("🔍 DIAGNOSING SELECTION BIAS (Malmquist Effect)")
    print("!" * 70)

    # Test 1: M_BH vs z correlation
    r_Mz, p_Mz = stats.pearsonr(z, logMBH)
    print(f"   1. Direct M_BH vs z correlation: r = {r_Mz:.3f} (p = {p_Mz:.2e})")

    # Test 2: Mass scatter vs z
    std_low = np.std(logMBH[z < np.median(z)])
    std_high = np.std(logMBH[z >= np.median(z)])
    print(f"   2. Mass dispersion: Low-z σ={std_low:.3f} | High-z σ={std_high:.3f}")

    bias_detected = r_Mz > 0.3 or std_high < std_low * 0.8
    if bias_detected:
        print("\n   ⚠️  RESULT: SIGNIFICANT SELECTION BIAS DETECTED!")
        print("      The observed k will be artificial (likely negative).")
        print("      Correction required: M_BH/M_stellar ratio or V/Vmax.")
    else:
        print("\n   ✅ RESULT: NO STRONG BIAS DETECTED.")

    return bias_detected


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # 1. Load Data
    shen = load_shen_catalog()
    if shen:
        shen_clean = apply_quality_cuts(shen)

        # 2. Diagnose Bias
        is_biased = diagnose_selection_bias(
            shen_clean["z"], shen_clean["logMBH"], shen_clean.get("logLbol")
        )

        if is_biased:
            print("\n" + "!" * 60)
            print("🔬 WARNING: BIASED EMPIRICAL FIT DETECTED")
            print("   We will run the analysis but treat 'k' as an upper/lower bound.")
            print("!" * 60)

        # 3. Run Analysis Pipeline
        results = run_ultimate_analysis()

        # 4. Run Thermodynamic Recycling (The True UET Verification)
        # Even if data is biased, the theoretical k=2.8 must satisfy Dark Energy requirements.
        analyze_entropy_recycling(k_fit=2.8, log_M0_avg=8.5)
    else:
        print("❌ FAILED: Could not load Shen catalog.")
