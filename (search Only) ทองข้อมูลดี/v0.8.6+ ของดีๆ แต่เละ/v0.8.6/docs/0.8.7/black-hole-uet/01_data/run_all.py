#!/usr/bin/env python3
"""
CCBH Analysis Pipeline - Master Script
========================================

One command to rule them all!

Usage:
    python run_all.py <catalog.fits>

Example:
    python run_all.py toy_quasar_catalog.fits
    python run_all.py DR7_BH_cat_final.fits
"""

import sys
import os
from pathlib import Path

# Add this directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    print("=" * 70)
    print("   CCBH ANALYSIS PIPELINE - COSMOLOGICALLY COUPLED BLACK HOLES")
    print("=" * 70)
    print()

    # Check arguments
    if len(sys.argv) < 2:
        print("Usage: python run_all.py <catalog.fits>")
        print()
        print("Options:")
        print("  python run_all.py toy_quasar_catalog.fits   # Test with toy data")
        print("  python run_all.py DR7_BH_cat_final.fits     # Real Shen 2011 data")
        print()
        print("Generate toy data first:")
        print("  python toy_data_generator.py")
        return 1

    catalog_path = sys.argv[1]

    if not Path(catalog_path).exists():
        print(f"ERROR: File not found: {catalog_path}")
        print()
        print("If testing, first run: python toy_data_generator.py")
        return 1

    # Import modules
    print("[1/6] Loading modules...")
    try:
        import numpy as np
        from data_loader import load_and_prepare
        from quality_cuts import apply_quality_cuts, bin_by_redshift
        from ccbh_analysis import fit_ccbh_model, bootstrap_k_error, compare_with_farrah
        from visualize import (
            plot_raw_data,
            plot_ccbh_fit,
            plot_bootstrap_distribution,
            plot_comparison_summary,
        )

        print("      OK!")
    except ImportError as e:
        print(f"\nERROR: Missing module: {e}")
        print("\nInstall required packages:")
        print("  pip install numpy scipy matplotlib astropy")
        return 1

    # Step 1: Load data
    print()
    print("[2/6] Loading catalog...")
    data = load_and_prepare(catalog_path)
    if data is None:
        print("ERROR: Failed to load data")
        return 1

    # Step 2: Quality cuts
    print()
    print("[3/6] Applying quality cuts...")
    config = {
        "z_min": 0.3,
        "z_max": 4.0,
        "logMBH_min": 6.5,
        "logMBH_max": 10.5,
        "logMBH_err_max": 0.5,
        "remove_nan": True,
    }
    cleaned = apply_quality_cuts(data, config)

    # Plot raw data
    print()
    print("[4/6] Creating visualizations...")
    output_dir = Path(catalog_path).parent
    plot_raw_data(cleaned["z"], cleaned["logMBH"], output_path=str(output_dir / "raw_data.png"))

    # Step 3: Bin by redshift
    print()
    print("[5/6] Binning and fitting...")
    bins = bin_by_redshift(cleaned, n_bins=10, method="equal_number")

    # Extract arrays for fitting
    import numpy as np

    z_bin = np.array([b["z_median"] for b in bins])
    logMBH_bin = np.array([b["logMBH_median"] for b in bins])
    logMBH_err_bin = np.array([b["logMBH_std"] for b in bins]) / np.sqrt(
        [b["n_objects"] for b in bins]
    )

    # Fit the CCBH model
    fit_result = fit_ccbh_model(z_bin, logMBH_bin, logMBH_err_bin)

    print(f"\n=== FIT RESULT ===")
    print(f"  k = {fit_result['k_fit']:.3f} ± {fit_result['k_err']:.3f}")
    print(f"  log(M0) = {fit_result['logM0']:.2f}")
    print(f"  chi2/dof = {fit_result['chi2']:.1f}/{fit_result['ndof']}")

    # Plot fit
    plot_ccbh_fit(bins, fit_result, output_path=str(output_dir / "ccbh_fit.png"))

    # Bootstrap (optional, but useful)
    do_bootstrap = len(cleaned["z"]) < 50000  # Skip for large catalogs
    if do_bootstrap:
        bootstrap_result = bootstrap_k_error(cleaned["z"], cleaned["logMBH"], n_bootstrap=500)
        plot_bootstrap_distribution(
            bootstrap_result, output_path=str(output_dir / "bootstrap_k.png")
        )
        k_final = bootstrap_result["k_median"]
        k_final_err = (bootstrap_result["k_84"] - bootstrap_result["k_16"]) / 2
    else:
        k_final = fit_result["k_fit"]
        k_final_err = fit_result["k_err"]

    # Step 4: Compare with Farrah
    print()
    print("[6/6] Comparing with Farrah (2023)...")
    comparison = compare_with_farrah(k_final, k_final_err)
    plot_comparison_summary(comparison, output_path=str(output_dir / "comparison_summary.png"))

    # Final summary
    print("\n" + "=" * 70)
    print("                         ANALYSIS COMPLETE!")
    print("=" * 70)
    print(
        f"""
    RESULT:
    -------
    k = {k_final:.3f} ± {k_final_err:.3f}
    
    FARRAH (2023) PREDICTION:
    -------------------------
    k = 3.0 ± 0.5
    
    DIFFERENCE:
    -----------
    {comparison['sigma']:.1f}σ
    
    DECISION:
    ---------
    {comparison['decision']}
    
    OUTPUT FILES:
    -------------
    {output_dir}/raw_data.png
    {output_dir}/ccbh_fit.png
    {output_dir}/bootstrap_k.png
    {output_dir}/comparison_summary.png
    """
    )
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
