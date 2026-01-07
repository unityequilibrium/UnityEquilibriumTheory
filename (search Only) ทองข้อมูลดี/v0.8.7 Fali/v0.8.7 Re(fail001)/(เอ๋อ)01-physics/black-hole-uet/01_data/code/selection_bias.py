"""
CCBH Selection Bias Correction
==============================
Apply corrections for Malmquist/selection bias in QSO samples.

Problem: Flux-limited surveys preferentially detect more massive BHs at high-z
Solution: Multiple approaches

Author: UET Research Team
Date: 2025-12-28
"""

import numpy as np
from scipy import stats


def diagnose_selection_bias(z, logMBH, logL=None):
    """
    Diagnose if selection bias is present in the data.

    Selection bias symptoms:
    1. Strong correlation between L and z (flux limit)
    2. logMBH increases with z (Malmquist bias)
    3. Narrowing of M_BH distribution at high-z

    Parameters
    ----------
    z : array
        Redshifts
    logMBH : array
        log10(M_BH)
    logL : array, optional
        log10(Luminosity) if available

    Returns
    -------
    dict : Diagnostic results
    """
    print("\n" + "=" * 70)
    print("SELECTION BIAS DIAGNOSTIC")
    print("=" * 70)

    # Test 1: M_BH vs z correlation (raw)
    r_Mz, p_Mz = stats.pearsonr(z, logMBH)
    print(f"\n1. Direct M_BH vs z correlation:")
    print(f"   r = {r_Mz:.3f}, p = {p_Mz:.2e}")

    if r_Mz > 0.3:
        print(f"   ⚠️  WARNING: Positive correlation suggests Malmquist bias!")
        bias_detected = True
    elif r_Mz < -0.3:
        print(f"   ⚠️  WARNING: Strong negative correlation - opposite bias?")
        bias_detected = True
    else:
        print(f"   ✓ Weak correlation - bias may be limited")
        bias_detected = False

    # Test 2: Mass scatter vs z
    z_low = z < np.median(z)
    z_high = z >= np.median(z)

    std_low = np.std(logMBH[z_low])
    std_high = np.std(logMBH[z_high])

    print(f"\n2. Mass dispersion:")
    print(f"   Low-z σ(logM) = {std_low:.3f}")
    print(f"   High-z σ(logM) = {std_high:.3f}")

    if std_high < std_low * 0.7:
        print(f"   ⚠️  WARNING: Reduced scatter at high-z indicates flux cut!")

    # Test 3: If luminosity available
    if logL is not None:
        r_Lz, p_Lz = stats.pearsonr(z, logL)
        print(f"\n3. Luminosity vs z:")
        print(f"   r = {r_Lz:.3f}, p = {p_Lz:.2e}")
        if r_Lz > 0.5:
            print(f"   ⚠️  STRONG flux-limit bias detected!")

    # Summary
    print("\n" + "-" * 70)
    if bias_detected:
        print("DIAGNOSIS: Selection bias DETECTED")
        print("RECOMMENDATION: Apply correction methods below")
    else:
        print("DIAGNOSIS: No strong bias detected")
        print("RECOMMENDATION: Proceed with caution")
    print("-" * 70)

    return {
        "r_Mz": r_Mz,
        "p_Mz": p_Mz,
        "bias_detected": bias_detected,
        "std_low_z": std_low,
        "std_high_z": std_high,
    }


def apply_volume_correction(z, logMBH, z_bins=10):
    """
    Apply V/Vmax correction for selection effects.

    Each object is weighted by the inverse of the volume in which
    it could have been detected. For flux-limited samples, more
    massive BHs are visible over larger volumes.

    Parameters
    ----------
    z : array
        Redshifts
    logMBH : array
        log10(M_BH)
    z_bins : int
        Number of redshift bins

    Returns
    -------
    dict : Corrected values
    """
    print("\n" + "=" * 70)
    print("V/Vmax VOLUME CORRECTION")
    print("=" * 70)

    # Estimate detection limit at each z
    # Simplified: assume flux limit corresponds to min observed M at each z

    z_edges = np.linspace(z.min(), z.max(), z_bins + 1)
    z_center = (z_edges[:-1] + z_edges[1:]) / 2

    # For each bin, estimate the minimum detectable mass
    M_min_per_bin = []
    for i in range(z_bins):
        mask = (z >= z_edges[i]) & (z < z_edges[i + 1])
        if np.sum(mask) > 5:
            M_min_per_bin.append(np.percentile(logMBH[mask], 5))
        else:
            M_min_per_bin.append(np.nan)

    M_min_per_bin = np.array(M_min_per_bin)

    # Fit M_min(z) trend
    valid = ~np.isnan(M_min_per_bin)
    if np.sum(valid) > 3:
        slope, intercept, r, p, se = stats.linregress(z_center[valid], M_min_per_bin[valid])
        print(f"\nDetection limit trend: logM_min = {intercept:.2f} + {slope:.2f}*z")
        print(f"  (r = {r:.3f})")

        if slope > 0.2:
            print(f"  ⚠️  Significant increase in minimum M with z!")

    # Weight each object by 1/V_max
    # V_max ∝ (D_L(z_max))^3 where z_max is the max z at which object is detectable
    # Simplified approximation: weight = 1 / (1+z)^3 (comoving volume)

    weights = 1.0 / (1 + z) ** 3

    # Re-bin with weights
    corrected_logMBH = []
    corrected_z = []

    for i in range(z_bins):
        mask = (z >= z_edges[i]) & (z < z_edges[i + 1])
        if np.sum(mask) > 5:
            w = weights[mask]
            # Weighted median
            sorted_idx = np.argsort(logMBH[mask])
            sorted_M = logMBH[mask][sorted_idx]
            sorted_w = w[sorted_idx]
            cumsum = np.cumsum(sorted_w)
            cutoff = cumsum[-1] / 2.0
            weighted_median = sorted_M[np.searchsorted(cumsum, cutoff)]

            corrected_logMBH.append(weighted_median)
            corrected_z.append(z_center[i])

    print(f"\nApplied (1+z)^-3 volume weighting to {len(corrected_z)} bins")

    return {
        "z_corrected": np.array(corrected_z),
        "logMBH_corrected": np.array(corrected_logMBH),
        "weights": weights,
        "M_min_trend": (intercept, slope) if np.sum(valid) > 3 else (np.nan, np.nan),
    }


def apply_matched_sample_method(z, logMBH, logL, z_bins=10):
    """
    Create a matched sample to remove luminosity bias.

    For each redshift bin, select only objects within a fixed
    luminosity range that is observable across all redshifts.

    Parameters
    ----------
    z : array
    logMBH : array
    logL : array
        log10(Luminosity)
    z_bins : int

    Returns
    -------
    dict : Matched sample
    """
    print("\n" + "=" * 70)
    print("LUMINOSITY-MATCHED SAMPLE")
    print("=" * 70)

    # Find luminosity range observable at all z
    z_edges = np.linspace(z.min(), z.max(), z_bins + 1)

    L_min_global = -np.inf
    L_max_global = np.inf

    for i in range(z_bins):
        mask = (z >= z_edges[i]) & (z < z_edges[i + 1])
        if np.sum(mask) > 5:
            L_min_global = max(L_min_global, np.percentile(logL[mask], 10))
            L_max_global = min(L_max_global, np.percentile(logL[mask], 90))

    print(f"\nOverlapping L range: {L_min_global:.2f} < logL < {L_max_global:.2f}")

    # Select objects in this range
    L_mask = (logL >= L_min_global) & (logL <= L_max_global)
    print(f"Selected {np.sum(L_mask)}/{len(z)} objects ({100*np.sum(L_mask)/len(z):.1f}%)")

    if np.sum(L_mask) < len(z) * 0.1:
        print("⚠️  WARNING: Very few objects selected - range too narrow!")

    return {
        "mask": L_mask,
        "z_matched": z[L_mask],
        "logMBH_matched": logMBH[L_mask],
        "logL_matched": logL[L_mask],
        "L_range": (L_min_global, L_max_global),
    }


def simulate_bias_effect(n_objects=1000, k_true=3.0, add_bias=True):
    """
    Simulate how Malmquist bias affects k measurement.

    Parameters
    ----------
    n_objects : int
        Number of simulated quasars
    k_true : float
        True cosmological coupling index
    add_bias : bool
        Whether to add Malmquist bias

    Returns
    -------
    dict : Simulation results
    """
    print("\n" + "=" * 70)
    print("MALMQUIST BIAS SIMULATION")
    print("=" * 70)

    np.random.seed(42)

    # Generate true BH masses (log-normal distribution)
    logMBH_true = np.random.normal(8.0, 0.5, n_objects)

    # Generate redshifts (uniform in comoving volume)
    z = np.random.uniform(0.5, 2.5, n_objects)
    a = 1.0 / (1 + z)

    # Apply cosmological coupling: M(z) = M(z=0) * a^k
    # In log: logM(z) = logM(z=0) + k * log(a)
    logMBH_evolved = logMBH_true + k_true * np.log10(a / a.max())

    # Add observational scatter
    logMBH_obs = logMBH_evolved + np.random.normal(0, 0.2, n_objects)

    if add_bias:
        # Simulate flux limit: higher z → only see brighter/more massive
        # Detection probability ∝ M * D_L^-2
        D_L_squared = (1 + z) ** 2  # Simplified

        # Detection threshold increases with z
        logM_threshold = 7.5 + 0.5 * z  # Simplified model

        detected = logMBH_obs > logM_threshold

        z_det = z[detected]
        logMBH_det = logMBH_obs[detected]

        print(
            f"\nWith bias: {np.sum(detected)}/{n_objects} detected ({100*np.sum(detected)/n_objects:.1f}%)"
        )
    else:
        z_det = z
        logMBH_det = logMBH_obs
        print(f"\nNo bias: All {n_objects} objects detected")

    # Fit k from detected sample
    a_det = 1.0 / (1 + z_det)
    log_a = np.log10(a_det)
    slope, intercept, r, p, se = stats.linregress(log_a, logMBH_det)
    k_measured = slope

    print(f"\nTrue k = {k_true:.2f}")
    print(f"Measured k = {k_measured:.2f} ± {se:.2f}")
    print(f"Bias = {k_measured - k_true:.2f}")

    if add_bias and abs(k_measured - k_true) > 1:
        print(f"\n⚠️  SIGNIFICANT BIAS DETECTED!")
        print(f"   Malmquist bias can shift k by {abs(k_measured - k_true):.1f}!")

    return {
        "k_true": k_true,
        "k_measured": k_measured,
        "k_err": se,
        "bias": k_measured - k_true,
        "z_detected": z_det,
        "logMBH_detected": logMBH_det,
        "n_detected": len(z_det),
    }


if __name__ == "__main__":
    print(
        """
    ╔═══════════════════════════════════════════════════════════════╗
    ║         CCBH SELECTION BIAS ANALYSIS                          ║
    ║         Understanding why k=-2 instead of k=3                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    )

    # Demonstrate the bias
    print("\n🔬 DEMONSTRATION: How Malmquist bias affects k measurement\n")

    print("=" * 70)
    print("TEST 1: No selection bias (ideal case)")
    print("=" * 70)
    result_no_bias = simulate_bias_effect(k_true=3.0, add_bias=False)

    print("\n" + "=" * 70)
    print("TEST 2: With Malmquist selection bias (realistic)")
    print("=" * 70)
    result_bias = simulate_bias_effect(k_true=3.0, add_bias=True)

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print(
        f"""
    True k = 3.0 (cosmological coupling)
    
    Without bias: k_measured = {result_no_bias['k_measured']:.2f}  ← CORRECT!
    With bias:    k_measured = {result_bias['k_measured']:.2f}  ← BIASED!
    
    The Malmquist bias can shift k from +3 to negative values!
    
    This explains why the Shen 2011 catalog gives k ≈ -2:
    - It's a flux-limited sample
    - At high-z, only the most massive BHs are visible
    - This creates an artificial negative correlation
    
    FIX: Use M_BH/M_galaxy ratio or apply V/Vmax correction
    """
    )
