"""
CCBH Analysis Pipeline - Quality Cuts
======================================
Apply quality cuts to clean the quasar sample
"""

import numpy as np


def apply_quality_cuts(data, config=None):
    """
    Apply quality cuts to the data.

    Parameters
    ----------
    data : dict
        Dictionary with keys: z, logMBH, logMBH_err, etc.
    config : dict, optional
        Quality cut configuration

    Returns
    -------
    dict
        Cleaned data with same structure
    """
    if config is None:
        config = {
            "z_min": 0.1,
            "z_max": 5.0,
            "logMBH_min": 6.0,
            "logMBH_max": 11.0,
            "logMBH_err_max": 0.5,
            "remove_nan": True,
        }

    print("\n=== Applying Quality Cuts ===")
    n_initial = len(data["z"])

    # Start with all True
    mask = np.ones(n_initial, dtype=bool)

    # Remove NaN values
    if config.get("remove_nan", True):
        nan_mask = np.isfinite(data["z"]) & np.isfinite(data["logMBH"])
        n_nan = np.sum(~nan_mask)
        mask &= nan_mask
        print(f"  Remove NaN: {n_nan} objects removed")

    # Redshift cuts
    z_min = config.get("z_min", 0.1)
    z_max = config.get("z_max", 5.0)
    z_mask = (data["z"] >= z_min) & (data["z"] <= z_max)
    n_z = np.sum(mask & ~z_mask)
    mask &= z_mask
    print(f"  z in [{z_min}, {z_max}]: {n_z} objects removed")

    # Mass cuts
    logMBH_min = config.get("logMBH_min", 6.0)
    logMBH_max = config.get("logMBH_max", 11.0)
    m_mask = (data["logMBH"] >= logMBH_min) & (data["logMBH"] <= logMBH_max)
    n_m = np.sum(mask & ~m_mask)
    mask &= m_mask
    print(f"  logMBH in [{logMBH_min}, {logMBH_max}]: {n_m} objects removed")

    # Error cuts (if available)
    if "logMBH_err" in data and data["logMBH_err"] is not None:
        err_max = config.get("logMBH_err_max", 0.5)
        err_mask = data["logMBH_err"] <= err_max
        n_err = np.sum(mask & ~err_mask)
        mask &= err_mask
        print(f"  logMBH_err <= {err_max}: {n_err} objects removed")

    # Apply mask to all columns
    cleaned = {}
    for key, arr in data.items():
        if arr is not None:
            cleaned[key] = arr[mask]

    n_final = len(cleaned["z"])
    print(f"\n  Initial: {n_initial} objects")
    print(f"  Final:   {n_final} objects")
    print(f"  Kept:    {100*n_final/n_initial:.1f}%")

    return cleaned


def bin_by_redshift(data, n_bins=10, method="equal_number"):
    """
    Bin data by redshift.

    Parameters
    ----------
    data : dict
        Cleaned data dictionary
    n_bins : int
        Number of redshift bins
    method : str
        'equal_number' or 'equal_width'

    Returns
    -------
    list of dict
        Each dict contains binned data and statistics
    """
    z = data["z"]
    logMBH = data["logMBH"]

    if method == "equal_number":
        # Equal number per bin
        percentiles = np.linspace(0, 100, n_bins + 1)
        bin_edges = np.percentile(z, percentiles)
    else:
        # Equal width
        bin_edges = np.linspace(z.min(), z.max(), n_bins + 1)

    bins = []
    for i in range(n_bins):
        mask = (z >= bin_edges[i]) & (z < bin_edges[i + 1])
        if i == n_bins - 1:
            mask = (z >= bin_edges[i]) & (z <= bin_edges[i + 1])

        if np.sum(mask) > 0:
            bin_data = {
                "z_min": bin_edges[i],
                "z_max": bin_edges[i + 1],
                "z_median": np.median(z[mask]),
                "z_mean": np.mean(z[mask]),
                "logMBH_median": np.median(logMBH[mask]),
                "logMBH_mean": np.mean(logMBH[mask]),
                "logMBH_std": np.std(logMBH[mask]),
                "n_objects": np.sum(mask),
            }
            bins.append(bin_data)

    print(f"\n=== Binning Summary ===")
    print(f"  Method: {method}")
    print(f"  N bins: {len(bins)}")
    for i, b in enumerate(bins):
        print(
            f"    Bin {i+1}: z=[{b['z_min']:.2f}, {b['z_max']:.2f}], N={b['n_objects']}, <logMBH>={b['logMBH_median']:.2f}"
        )

    return bins


if __name__ == "__main__":
    print("Quality Cuts Module")
    print("Usage: Import in your analysis script")
    print("\nExample:")
    print("  from quality_cuts import apply_quality_cuts, bin_by_redshift")
    print("  cleaned = apply_quality_cuts(data)")
    print("  bins = bin_by_redshift(cleaned, n_bins=10)")
