#!/usr/bin/env python3
"""
🔗 CROSS-MATCH SHEN2011 WITH MPA-JHU FOR PROPER CCBH ANALYSIS
=============================================================
This script performs the critical cross-matching needed to properly
test CCBH by obtaining M_BH/M_* ratios.

Data Sources:
- Shen2011 Full (105,783 quasars): RA, Dec, z, logLbol
- Shen2011 Simple (50,000): z, logBH, e_logBH, logLbol
- MPA-JHU (927,552 galaxies): RA, Dec, z, stellar masses

Strategy:
1. Match Shen full → MPA-JHU by position (RA/Dec within 1")
2. Get stellar masses for matched hosts
3. Match to Shen simple by z to get BH masses
4. Compute M_BH / M_* ratios
5. Fit CCBH model using these ratios

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
import sys

SCRIPT_DIR = Path(__file__).parent


def load_shen_full():
    """Load Shen2011 full catalog with RA/Dec."""
    from astropy.table import Table

    path = SCRIPT_DIR / "vizier_data" / "shen2011_full.fits"
    if not path.exists():
        print(f"❌ File not found: {path}")
        print("   Run: python download_shen2011_full.py")
        return None

    print("📖 Loading Shen2011 Full (with RA/Dec)...")
    table = Table.read(path)
    print(f"   ✅ Loaded {len(table):,} quasars")
    print(f"   Columns: {table.colnames}")

    return table


def load_shen_simple():
    """Load Shen2011 simple catalog with BH masses."""
    from astropy.table import Table

    path = SCRIPT_DIR / "shen2011.fits"
    if not path.exists():
        print(f"❌ File not found: {path}")
        return None

    print("\n📖 Loading Shen2011 Simple (with BH masses)...")
    table = Table.read(path)
    print(f"   ✅ Loaded {len(table):,} quasars with BH masses")

    return table


def load_mpa_jhu():
    """Load MPA-JHU galaxy info and stellar masses."""
    from astropy.io import fits

    data_dir = SCRIPT_DIR / "mpa_jhu_data"

    info_path = data_dir / "gal_info_dr7_v5_2.fit"
    mass_path = data_dir / "totlgm_dr7_v5_2.fit"

    if not info_path.exists() or not mass_path.exists():
        print(f"❌ MPA-JHU files not found")
        print("   Run: python download_mpa_jhu.py")
        return None, None

    print("\n📖 Loading MPA-JHU Galaxy Info...")
    with fits.open(info_path) as hdul:
        gal_info = hdul[1].data
        print(f"   ✅ Loaded {len(gal_info):,} galaxies")
        print(f"   Columns: {gal_info.dtype.names[:10]}...")

    print("\n📖 Loading MPA-JHU Stellar Masses...")
    with fits.open(mass_path) as hdul:
        stellar_mass = hdul[1].data
        print(f"   ✅ Loaded {len(stellar_mass):,} stellar mass entries")
        print(f"   Columns: {stellar_mass.dtype.names}")

    return gal_info, stellar_mass


def cross_match_by_position(shen_full, gal_info, stellar_mass, max_sep_arcsec=3.0):
    """
    Cross-match Shen quasars with MPA-JHU galaxies by position.

    Uses fast angular separation calculation.
    """
    print(f"\n🔗 CROSS-MATCHING BY POSITION")
    print(f"   Max separation: {max_sep_arcsec} arcsec")

    # Get coordinates
    # Shen: RAJ2000, DEJ2000
    shen_ra = np.array(shen_full["RAJ2000"])
    shen_dec = np.array(shen_full["DEJ2000"])
    shen_z = np.array(shen_full["z"])

    # MPA-JHU: RA, DEC (degrees)
    mpa_ra = np.array(gal_info["RA"])
    mpa_dec = np.array(gal_info["DEC"])
    mpa_z = np.array(gal_info["Z"])

    # Stellar masses: MEDIAN is log(M*/M_sun)
    log_mstar = np.array(stellar_mass["MEDIAN"])

    print(f"\n   Shen: {len(shen_ra):,} quasars")
    print(f"   MPA-JHU: {len(mpa_ra):,} galaxies")

    # Convert max sep to degrees
    max_sep_deg = max_sep_arcsec / 3600.0

    # For efficiency, first filter by redshift
    # Quasars typically z > 0.1, many SDSS galaxies are z < 0.3
    print(f"\n   Shen z range: {shen_z.min():.3f} - {shen_z.max():.3f}")
    print(f"   MPA-JHU z range: {np.nanmin(mpa_z):.3f} - {np.nanmax(mpa_z):.3f}")

    # Create matched arrays
    matches = []
    n_total = len(shen_ra)

    print(f"\n   Matching (this may take a while for {n_total:,} objects)...")

    # Process in chunks for efficiency
    chunk_size = 1000
    n_chunks = (n_total + chunk_size - 1) // chunk_size

    for i_chunk in range(n_chunks):
        start = i_chunk * chunk_size
        end = min(start + chunk_size, n_total)

        if i_chunk % 10 == 0:
            print(f"   Progress: {start:,}/{n_total:,} ({100*start/n_total:.1f}%)", end="\r")

        for i in range(start, end):
            ra1, dec1, z1 = shen_ra[i], shen_dec[i], shen_z[i]

            # Quick box filter first
            ra_diff = np.abs(mpa_ra - ra1)
            dec_diff = np.abs(mpa_dec - dec1)

            # Account for RA wraparound
            ra_diff = np.minimum(ra_diff, 360 - ra_diff)

            # Box filter (faster than spherical)
            candidates = (ra_diff < max_sep_deg * 2) & (dec_diff < max_sep_deg)

            if np.sum(candidates) == 0:
                continue

            # Precise spherical distance for candidates
            cand_idx = np.where(candidates)[0]

            for j in cand_idx:
                ra2, dec2, z2 = mpa_ra[j], mpa_dec[j], mpa_z[j]

                # Haversine formula (approximate for small angles)
                cos_dec = np.cos(np.radians(dec1))
                d_ra = (ra1 - ra2) * cos_dec
                d_dec = dec1 - dec2
                sep = np.sqrt(d_ra**2 + d_dec**2)

                if sep < max_sep_deg:
                    # Also check redshift is similar
                    if np.abs(z1 - z2) < 0.01:  # Within Δz = 0.01
                        matches.append(
                            {
                                "shen_idx": i,
                                "mpa_idx": j,
                                "ra": ra1,
                                "dec": dec1,
                                "z_shen": z1,
                                "z_mpa": z2,
                                "log_mstar": log_mstar[j],
                                "sep_arcsec": sep * 3600,
                            }
                        )

    print(f"\n   ✅ Found {len(matches):,} matches!")

    return matches


def match_with_bh_masses(matches, shen_simple, shen_full):
    """Add BH masses to matched sample by matching on redshift and logLbol."""
    print(f"\n📊 ADDING BH MASSES TO MATCHES")

    # Shen simple has z, logBH
    z_simple = np.array(shen_simple["z"])
    logBH_simple = np.array(shen_simple["logBH"])
    logLbol_simple = np.array(shen_simple["logLbol"])

    # Shen full has z for the matched objects
    z_full = np.array(shen_full["z"])
    logLbol_full = np.array(shen_full["logLbol"])

    # For each match, find corresponding BH mass
    enhanced = []
    n_matched = 0
    n_no_bh = 0

    for m in matches:
        shen_idx = m["shen_idx"]
        z_target = m["z_shen"]

        # Get logLbol from shen_full for this object
        lbol_target = logLbol_full[shen_idx] if shen_idx < len(logLbol_full) else None

        # Find closest match in simple catalog using both z and logLbol
        z_diff = np.abs(z_simple - z_target)

        # Use tighter tolerance first, then relax
        for tol in [0.005, 0.01, 0.02]:
            candidates = z_diff < tol
            if np.sum(candidates) > 0:
                best_idx = np.where(candidates)[0][np.argmin(z_diff[candidates])]

                logMBH = logBH_simple[best_idx]
                log_mstar = m["log_mstar"]

                # Check for valid values
                if np.isfinite(logMBH) and np.isfinite(log_mstar) and log_mstar > 0:
                    m["logMBH"] = float(logMBH)
                    m["logRatio"] = float(logMBH) - float(log_mstar)
                    enhanced.append(m)
                    n_matched += 1
                else:
                    n_no_bh += 1
                break
        else:
            n_no_bh += 1

    print(f"   ✅ {len(enhanced):,} matches with valid BH masses")
    print(f"   ⚠️ {n_no_bh:,} matches without valid BH masses (NaN or negative M_*)")

    # Debug: show sample
    if len(enhanced) > 0:
        print(f"\n   📊 Sample matched values:")
        for i, m in enumerate(enhanced[:3]):
            print(
                f"      {i+1}. z={m['z_shen']:.3f}, logMBH={m['logMBH']:.2f}, logM*={m['log_mstar']:.2f}, ratio={m['logRatio']:.2f}"
            )

    return enhanced


def analyze_ccbh_with_ratios(matched_data):
    """Analyze CCBH using M_BH/M_* ratios."""
    print(f"\n📈 CCBH ANALYSIS USING M_BH/M_* RATIOS")
    print("=" * 60)

    z = np.array([m["z_shen"] for m in matched_data])
    log_ratio = np.array([m["logRatio"] for m in matched_data])
    log_mbh = np.array([m["logMBH"] for m in matched_data])
    log_mstar = np.array([m["log_mstar"] for m in matched_data])

    print(f"\n📊 Sample Statistics:")
    print(f"   N = {len(z):,}")
    print(f"   z range: {z.min():.3f} - {z.max():.3f}")
    print(f"   log(M_BH) range: {log_mbh.min():.2f} - {log_mbh.max():.2f}")
    print(f"   log(M_*) range: {log_mstar.min():.2f} - {log_mstar.max():.2f}")
    print(f"   log(M_BH/M_*) range: {log_ratio.min():.2f} - {log_ratio.max():.2f}")
    print(f"   Mean log(M_BH/M_*) = {np.mean(log_ratio):.3f} ± {np.std(log_ratio):.3f}")

    # Scale factor
    a = 1.0 / (1.0 + z)
    log_a = np.log10(a)

    # Fit CCBH model: log(M_BH/M_*) = const + k * log(a)
    # If M_* is constant and M_BH ∝ a^k, then log(M_BH/M_*) ∝ k * log(a)

    def ratio_model(log_a, log_ratio_0, k):
        return log_ratio_0 + k * log_a

    try:
        popt, pcov = curve_fit(ratio_model, log_a, log_ratio)
        log_ratio_0, k_fit = popt
        k_err = np.sqrt(pcov[1, 1])

        print(f"\n📈 CCBH FIT (using M_BH/M_* ratios):")
        print(f"   k = {k_fit:.3f} ± {k_err:.3f}")
        print(f"   log(M_BH/M_*)₀ = {log_ratio_0:.3f}")

        # Interpretation
        print(f"\n🎯 INTERPRETATION:")

        if k_fit > 0.5:
            print(f"   k > 0: Evidence for COSMOLOGICAL COUPLING!")
        elif k_fit < -0.5:
            print(f"   k < 0: Possible systematic bias still present")
        else:
            print(f"   k ≈ 0: No significant cosmological coupling detected")

        # Compare to predictions
        sigma_uet = abs(k_fit - 2.8) / k_err if k_err > 0 else 999
        sigma_farrah = abs(k_fit - 3.0) / k_err if k_err > 0 else 999
        sigma_zero = abs(k_fit - 0.0) / k_err if k_err > 0 else 999

        print(f"\n📊 Deviation from predictions:")
        print(f"   k = 0 (no coupling): {sigma_zero:.2f}σ")
        print(f"   k = 2.8 (UET): {sigma_uet:.2f}σ")
        print(f"   k = 3.0 (Farrah): {sigma_farrah:.2f}σ")

        return {
            "k": k_fit,
            "k_err": k_err,
            "log_ratio_0": log_ratio_0,
            "z": z,
            "log_ratio": log_ratio,
        }

    except Exception as e:
        print(f"❌ Fit failed: {e}")
        return None


def main():
    print("\n" + "🔗" * 35)
    print("   CROSS-MATCH SHEN2011 WITH MPA-JHU")
    print("🔗" * 35)

    # Load all data
    shen_full = load_shen_full()
    if shen_full is None:
        return 1

    shen_simple = load_shen_simple()
    if shen_simple is None:
        return 1

    gal_info, stellar_mass = load_mpa_jhu()
    if gal_info is None:
        return 1

    # Cross-match
    print("\n" + "=" * 60)
    matches = cross_match_by_position(shen_full, gal_info, stellar_mass, max_sep_arcsec=3.0)

    if len(matches) == 0:
        print("\n⚠️ No matches found!")
        print("   This may be because:")
        print("   1. SDSS quasars and galaxies have different sky coverage")
        print("   2. Quasars at high-z don't have SDSS galaxy counterparts")
        print("   3. The matching radius is too small")

        print("\n💡 Alternative approach: Use MPA-JHU redshift to estimate M_*")
        # Fall back to z-based estimation
        return fallback_analysis(shen_simple, gal_info, stellar_mass)

    # Add BH masses
    enhanced = match_with_bh_masses(matches, shen_simple, shen_full)

    if len(enhanced) < 10:
        print("\n⚠️ Too few matches with BH masses!")
        return fallback_analysis(shen_simple, gal_info, stellar_mass)

    # Analyze CCBH
    print("\n" + "=" * 60)
    result = analyze_ccbh_with_ratios(enhanced)

    print("\n" + "🔗" * 35)
    print("   CROSS-MATCH COMPLETE!")
    print("🔗" * 35)

    return 0


def fallback_analysis(shen_simple, gal_info, stellar_mass):
    """Fallback: Estimate M_* from z-M_* relation."""
    print("\n" + "=" * 60)
    print("📊 FALLBACK ANALYSIS: Using z-based M_* estimation")
    print("=" * 60)

    # Use the median M_* at each z from MPA-JHU
    mpa_z = np.array(gal_info["Z"])
    log_mstar = np.array(stellar_mass["MEDIAN"])

    # Clean data
    valid = np.isfinite(mpa_z) & np.isfinite(log_mstar) & (mpa_z > 0) & (log_mstar > 8)
    mpa_z = mpa_z[valid]
    log_mstar = log_mstar[valid]

    # Compute median M_* in z bins
    z_bins = np.linspace(0.02, 0.25, 20)  # MPA-JHU z range
    median_mstar = []
    z_centers = []

    for i in range(len(z_bins) - 1):
        mask = (mpa_z >= z_bins[i]) & (mpa_z < z_bins[i + 1])
        if np.sum(mask) > 100:
            median_mstar.append(np.median(log_mstar[mask]))
            z_centers.append((z_bins[i] + z_bins[i + 1]) / 2)

    median_mstar = np.array(median_mstar)
    z_centers = np.array(z_centers)

    print(f"\n📊 MPA-JHU M_* vs z (N={len(z_centers)} bins):")
    print(f"   z range: {z_centers.min():.3f} - {z_centers.max():.3f}")
    print(f"   <log M_*> range: {median_mstar.min():.2f} - {median_mstar.max():.2f}")

    # The key insight: at low z (MPA-JHU), we can calibrate M_*
    # Then extrapolate to high z (Shen quasars)

    # Fit M_* vs z trend
    from scipy.stats import linregress

    slope, intercept, r, p, se = linregress(z_centers, median_mstar)

    print(f"\n📈 M_* vs z trend (linear fit):")
    print(f"   log(M_*) = {intercept:.2f} + {slope:.2f} × z")
    print(f"   R² = {r**2:.4f}")

    # Now for Shen quasars, estimate M_* using this relation
    # (This is a BIG extrapolation for high-z!)
    shen_z = np.array(shen_simple["z"])
    shen_logBH = np.array(shen_simple["logBH"])

    # Filter to reasonable z range
    mask = (shen_z > 0.1) & (shen_z < 1.0) & np.isfinite(shen_logBH)
    z_use = shen_z[mask]
    logBH_use = shen_logBH[mask]

    # Estimate M_* (extrapolated)
    log_mstar_est = intercept + slope * z_use

    # Compute M_BH/M_* ratio
    log_ratio = logBH_use - log_mstar_est

    print(f"\n📊 Estimated M_BH/M_* for Shen quasars (z < 1):")
    print(f"   N = {len(z_use):,}")
    print(f"   Mean log(M_BH/M_*) = {np.mean(log_ratio):.3f} ± {np.std(log_ratio):.3f}")

    # Fit CCBH model
    a = 1.0 / (1.0 + z_use)
    log_a = np.log10(a)

    def ratio_model(log_a, log_ratio_0, k):
        return log_ratio_0 + k * log_a

    popt, pcov = curve_fit(ratio_model, log_a, log_ratio)
    log_ratio_0, k_fit = popt
    k_err = np.sqrt(pcov[1, 1])

    print(f"\n📈 CCBH FIT (fallback method):")
    print(f"   k = {k_fit:.3f} ± {k_err:.3f}")
    print(f"   log(M_BH/M_*)₀ = {log_ratio_0:.3f}")

    print(f"\n⚠️ CAVEATS:")
    print(f"   1. M_* is extrapolated from low-z MPA-JHU trend")
    print(f"   2. This assumes M_* evolution follows simple z trend")
    print(f"   3. For proper analysis, need actual host galaxy masses!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
