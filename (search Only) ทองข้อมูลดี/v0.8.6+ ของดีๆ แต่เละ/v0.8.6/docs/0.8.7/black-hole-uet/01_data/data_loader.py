"""
CCBH Analysis Pipeline - Data Loader
=====================================
Load FITS catalogs (Shen 2011 DR7 or similar)
"""

import numpy as np
from pathlib import Path


def load_fits_catalog(filepath):
    """Load a FITS catalog and return essential columns."""
    try:
        from astropy.io import fits
        from astropy.table import Table
    except ImportError:
        print("ERROR: astropy not installed!")
        print("Run: pip install astropy")
        return None

    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        return None

    print(f"Loading {filepath.name}...")

    # Try different loading methods
    try:
        # Method 1: astropy Table (most flexible)
        table = Table.read(filepath)
        print(f"Loaded {len(table)} rows")
        return table
    except Exception as e:
        print(f"Table.read failed: {e}")

    try:
        # Method 2: Direct FITS access
        with fits.open(filepath) as hdul:
            print(f"HDU list: {[h.name for h in hdul]}")
            # Usually data is in extension 1
            data = hdul[1].data
            print(f"Loaded {len(data)} rows")
            return data
    except Exception as e:
        print(f"FITS open failed: {e}")
        return None


def extract_essential_columns(data, column_map=None):
    """
    Extract essential columns for CCBH analysis.

    Default column map for Shen 2011 DR7:
    - z: redshift
    - logMBH: log10(M_BH / M_sun)
    - logMBH_err: error on logMBH
    """
    if column_map is None:
        # Default for Shen 2011 DR7 catalog (VizieR + original)
        column_map = {
            "z": ["z", "Z", "REDSHIFT", "redshift"],
            "logMBH": ["logBH", "LOGBH_HB_VP06", "LOGBH_MGII_S11", "LOGBH", "logMBH", "LOG_MBH"],
            "logMBH_err": ["e_logBH", "ERR_LOGBH_HB_VP06", "ERR_LOGBH", "LOGBH_ERR", "e_logMBH"],
            "logLbol": ["logLbol", "LOGLBOL", "LOG_LBOL"],
        }

    result = {}
    available_cols = list(data.dtype.names) if hasattr(data, "dtype") else list(data.colnames)
    print(f"Available columns: {available_cols[:10]}... (showing first 10)")

    for key, possible_names in column_map.items():
        for name in possible_names:
            if name in available_cols:
                result[key] = np.array(data[name])
                print(f"  {key} <- {name}")
                break
        else:
            print(f"  {key} <- NOT FOUND (tried: {possible_names})")

    return result


def load_and_prepare(filepath):
    """One-stop function: load and prepare data for analysis."""
    data = load_fits_catalog(filepath)
    if data is None:
        return None

    extracted = extract_essential_columns(data)

    # Basic validation
    if "z" not in extracted or "logMBH" not in extracted:
        print("ERROR: Missing essential columns (z or logMBH)")
        return None

    print(f"\n=== Data Summary ===")
    print(f"  N objects: {len(extracted['z'])}")
    print(f"  z range: {np.nanmin(extracted['z']):.3f} - {np.nanmax(extracted['z']):.3f}")
    print(
        f"  logMBH range: {np.nanmin(extracted['logMBH']):.2f} - {np.nanmax(extracted['logMBH']):.2f}"
    )

    return extracted


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        data = load_and_prepare(sys.argv[1])
    else:
        print("Usage: python data_loader.py <catalog.fits>")
        print("\nTest with toy data:")
        print("  python toy_data_generator.py")
        print("  python data_loader.py toy_quasar_catalog.fits")
