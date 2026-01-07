"""
CCBH Analysis Pipeline - Core Analysis
========================================
Fit the CCBH scaling relation: M_BH ∝ a^k

This is THE MONEY SCRIPT!
"""

import numpy as np
from scipy import optimize
from scipy import stats


def z_to_scale_factor(z):
    """Convert redshift z to scale factor a = 1/(1+z)."""
    return 1.0 / (1.0 + z)


def fit_ccbh_model(z_values, logMBH_values, logMBH_errors=None):
    """
    Fit the CCBH model: M ∝ a^k

    In log space: log(M) = log(M0) + k * log(a)

    Parameters
    ----------
    z_values : array
        Redshift values (median per bin)
    logMBH_values : array
        log10(M_BH) values (median per bin)
    logMBH_errors : array, optional
        Errors on logMBH (std per bin)

    Returns
    -------
    dict
        k_fit, k_err, M0, chi2, etc.
    """
    # Convert z to scale factor
    a_values = z_to_scale_factor(z_values)
    log_a = np.log10(a_values)

    # Weights (if errors provided)
    if logMBH_errors is not None and np.all(logMBH_errors > 0):
        weights = 1.0 / logMBH_errors**2
    else:
        weights = None

    # Linear regression: logMBH = logM0 + k * log(a)
    if weights is not None:
        # Weighted least squares
        def model(params):
            logM0, k = params
            return logM0 + k * log_a

        def chi2(params):
            residuals = logMBH_values - model(params)
            return np.sum(weights * residuals**2)

        result = optimize.minimize(chi2, [8.0, 3.0], method="Nelder-Mead")
        logM0, k_fit = result.x

        # Estimate errors from Hessian
        # Approximate with numerical derivatives
        eps = 1e-4
        hess = np.zeros((2, 2))
        for i in range(2):
            for j in range(2):
                params_pp = result.x.copy()
                params_pm = result.x.copy()
                params_mp = result.x.copy()
                params_mm = result.x.copy()
                params_pp[i] += eps
                params_pp[j] += eps
                params_pm[i] += eps
                params_pm[j] -= eps
                params_mp[i] -= eps
                params_mp[j] += eps
                params_mm[i] -= eps
                params_mm[j] -= eps
                hess[i, j] = (
                    chi2(params_pp) - chi2(params_pm) - chi2(params_mp) + chi2(params_mm)
                ) / (4 * eps**2)

        try:
            cov = np.linalg.inv(hess)
            k_err = np.sqrt(cov[1, 1])
        except:
            k_err = np.nan

        chi2_val = result.fun
    else:
        # Simple OLS
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_a, logMBH_values)
        k_fit = slope
        k_err = std_err
        logM0 = intercept
        chi2_val = np.sum((logMBH_values - (intercept + slope * log_a)) ** 2)

    # Convert logM0 to M0 in solar masses
    M0 = 10**logM0

    return {
        "k_fit": k_fit,
        "k_err": k_err,
        "logM0": logM0,
        "M0": M0,
        "chi2": chi2_val,
        "ndof": len(z_values) - 2,
        "a_values": a_values,
        "log_a": log_a,
        "logMBH_fit": logM0 + k_fit * log_a,
    }


def bootstrap_k_error(z_values, logMBH_values, logMBH_errors=None, n_bootstrap=1000):
    """
    Estimate k error using bootstrap resampling.

    Parameters
    ----------
    z_values : array
        Full (not binned) redshift array
    logMBH_values : array
        Full (not binned) logMBH array
    n_bootstrap : int
        Number of bootstrap samples

    Returns
    -------
    dict
        k_median, k_std, k_16, k_84 (1-sigma), k_samples
    """
    n_data = len(z_values)
    k_samples = []

    print(f"\nBootstrap resampling ({n_bootstrap} iterations)...")

    for i in range(n_bootstrap):
        # Random resample with replacement
        idx = np.random.choice(n_data, size=n_data, replace=True)
        z_boot = z_values[idx]
        logMBH_boot = logMBH_values[idx]

        # Quick linear regression
        a_boot = z_to_scale_factor(z_boot)
        log_a = np.log10(a_boot)

        # Bin the bootstrapped data
        n_bins = 10
        percentiles = np.linspace(0, 100, n_bins + 1)
        bin_edges = np.percentile(z_boot, percentiles)

        z_bin = []
        logMBH_bin = []
        for j in range(n_bins):
            mask = (z_boot >= bin_edges[j]) & (z_boot < bin_edges[j + 1])
            if j == n_bins - 1:
                mask = (z_boot >= bin_edges[j]) & (z_boot <= bin_edges[j + 1])
            if np.sum(mask) > 0:
                z_bin.append(np.median(z_boot[mask]))
                logMBH_bin.append(np.median(logMBH_boot[mask]))

        z_bin = np.array(z_bin)
        logMBH_bin = np.array(logMBH_bin)

        if len(z_bin) > 2:
            a_bin = z_to_scale_factor(z_bin)
            log_a_bin = np.log10(a_bin)
            slope, intercept, r, p, se = stats.linregress(log_a_bin, logMBH_bin)
            k_samples.append(slope)

        if (i + 1) % 200 == 0:
            print(f"  {i+1}/{n_bootstrap} done...")

    k_samples = np.array(k_samples)

    result = {
        "k_median": np.median(k_samples),
        "k_mean": np.mean(k_samples),
        "k_std": np.std(k_samples),
        "k_16": np.percentile(k_samples, 16),
        "k_84": np.percentile(k_samples, 84),
        "k_2.5": np.percentile(k_samples, 2.5),
        "k_97.5": np.percentile(k_samples, 97.5),
        "k_samples": k_samples,
    }

    print(f"\n=== Bootstrap Results ===")
    print(
        f"  k = {result['k_median']:.3f} +{result['k_84']-result['k_median']:.3f} -{result['k_median']-result['k_16']:.3f} (68% CI)"
    )
    print(
        f"  k = {result['k_median']:.3f} +{result['k_97.5']-result['k_median']:.3f} -{result['k_median']-result['k_2.5']:.3f} (95% CI)"
    )

    return result


def compare_with_farrah(k_fit, k_err):
    """
    Compare fitted k with Farrah et al. (2023) prediction.

    Farrah claims: k ≈ 3 for cosmological coupling
    """
    k_farrah = 3.0
    k_farrah_err = 0.5  # Approximate from paper

    # Significance of difference
    diff = abs(k_fit - k_farrah)
    combined_err = np.sqrt(k_err**2 + k_farrah_err**2)
    sigma = diff / combined_err

    print("\n" + "=" * 60)
    print("COMPARISON WITH FARRAH ET AL. (2023)")
    print("=" * 60)
    print(f"\n  Your result:   k = {k_fit:.3f} ± {k_err:.3f}")
    print(f"  Farrah (2023): k = {k_farrah:.1f} ± {k_farrah_err:.1f}")
    print(f"\n  Difference: {diff:.3f}")
    print(f"  Significance: {sigma:.1f}σ")

    print("\n" + "-" * 60)
    if sigma < 1:
        print("  INTERPRETATION: EXCELLENT AGREEMENT! 🎉")
        print("  Your data supports CCBH with cosmological coupling k~3")
        decision = "GO"
    elif sigma < 2:
        print("  INTERPRETATION: MARGINAL AGREEMENT")
        print("  Results are consistent within 2σ but tension exists")
        decision = "INVESTIGATE"
    elif sigma < 3:
        print("  INTERPRETATION: TENSION")
        print("  Data shows ~2-3σ tension with Farrah prediction")
        decision = "INTERESTING"
    else:
        print("  INTERPRETATION: DISAGREEMENT")
        print("  Data strongly disagrees with k~3 prediction")
        decision = "INVESTIGATE MORE"

    print("-" * 60)

    return {
        "k_fit": k_fit,
        "k_err": k_err,
        "k_farrah": k_farrah,
        "k_farrah_err": k_farrah_err,
        "difference": diff,
        "sigma": sigma,
        "decision": decision,
    }


if __name__ == "__main__":
    print("CCBH Analysis Module")
    print("\nThis is the core fitting code!")
    print("\nTo test, run:")
    print("  python toy_data_generator.py")
    print("  python run_all.py toy_quasar_catalog.fits")
