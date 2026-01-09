"""
CCBH Analysis Pipeline - Toy Data Generator
=============================================
Create synthetic quasar catalog for testing the pipeline
"""

import numpy as np
from pathlib import Path


def generate_toy_quasars(
    n_quasars=10000, k_true=3.0, z_min=0.3, z_max=4.0, logM0=8.5, scatter=0.3, seed=42
):
    """
    Generate toy quasar catalog with known k coupling.

    Model: log(M_BH) = logM0 + k * log(a) + noise

    Parameters
    ----------
    n_quasars : int
        Number of quasars to generate
    k_true : float
        True coupling parameter (default 3.0 = Farrah prediction)
    z_min, z_max : float
        Redshift range
    logM0 : float
        log10(M_BH) at a=1 (z=0)
    scatter : float
        Gaussian scatter in logMBH (dex)
    seed : int
        Random seed for reproducibility

    Returns
    -------
    dict
        z, logMBH, logMBH_err arrays
    """
    np.random.seed(seed)

    print(f"\n=== Generating Toy Quasar Catalog ===")
    print(f"  N quasars: {n_quasars}")
    print(f"  True k: {k_true}")
    print(f"  z range: [{z_min}, {z_max}]")
    print(f"  log(M0): {logM0}")
    print(f"  Scatter: {scatter} dex")

    # Generate uniform in log(1+z) for more even distribution
    log1pz = np.random.uniform(np.log10(1 + z_min), np.log10(1 + z_max), n_quasars)
    z = 10**log1pz - 1

    # Scale factor
    a = 1.0 / (1.0 + z)
    log_a = np.log10(a)

    # True relation with scatter
    noise = np.random.normal(0, scatter, n_quasars)
    logMBH = logM0 + k_true * log_a + noise

    # Simulate measurement errors (larger for fainter = higher z)
    logMBH_err = 0.1 + 0.05 * z  # Simple model

    print(f"\n  Generated!")
    print(f"  z range: {z.min():.2f} - {z.max():.2f}")
    print(f"  logMBH range: {logMBH.min():.2f} - {logMBH.max():.2f}")

    return {
        "z": z,
        "logMBH": logMBH,
        "logMBH_err": logMBH_err,
        "k_true": k_true,
        "logM0_true": logM0,
    }


def save_to_fits(data, output_path="toy_quasar_catalog.fits"):
    """Save toy data to FITS file."""
    try:
        from astropy.table import Table
    except ImportError:
        print("ERROR: astropy not installed!")
        print("Saving to CSV instead...")
        save_to_csv(data, output_path.replace(".fits", ".csv"))
        return

    table = Table()
    table["Z"] = data["z"]
    table["LOGBH_HB_VP06"] = data["logMBH"]  # Match Shen 2011 column name
    table["ERR_LOGBH_HB_VP06"] = data["logMBH_err"]

    # Add metadata
    table.meta["K_TRUE"] = data["k_true"]
    table.meta["LOGM0_TRUE"] = data["logM0_true"]
    table.meta["COMMENT"] = "Toy catalog for testing CCBH pipeline"

    table.write(output_path, format="fits", overwrite=True)
    print(f"\nSaved: {output_path}")


def save_to_csv(data, output_path="toy_quasar_catalog.csv"):
    """Save toy data to CSV file (fallback if no astropy)."""
    import csv

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Z", "LOGBH_HB_VP06", "ERR_LOGBH_HB_VP06"])
        for i in range(len(data["z"])):
            writer.writerow([data["z"][i], data["logMBH"][i], data["logMBH_err"][i]])

    print(f"\nSaved: {output_path}")


def main():
    """Generate toy catalog for testing."""
    print("=" * 60)
    print("TOY QUASAR CATALOG GENERATOR")
    print("=" * 60)

    # Generate with k=3 (Farrah prediction)
    data = generate_toy_quasars(
        n_quasars=10000, k_true=3.0, z_min=0.3, z_max=4.0, logM0=8.5, scatter=0.3, seed=42
    )

    # Save
    output_dir = Path(__file__).parent
    fits_path = output_dir / "toy_quasar_catalog.fits"

    save_to_fits(data, str(fits_path))

    print("\n" + "=" * 60)
    print("NEXT STEP:")
    print("  python run_all.py toy_quasar_catalog.fits")
    print("\nExpected result: k_fit ≈ 3.0 (within errors)")
    print("=" * 60)

    return data


if __name__ == "__main__":
    main()
