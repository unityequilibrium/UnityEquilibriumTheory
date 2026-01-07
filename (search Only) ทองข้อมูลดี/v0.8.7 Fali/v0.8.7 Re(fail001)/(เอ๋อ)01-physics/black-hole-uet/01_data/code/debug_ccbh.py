#!/usr/bin/env python3
"""
🔥 CCBH DEBUG SCRIPT - Step by Step
====================================
This script tests each step of the CCBH analysis independently.
Prints verbose output at every stage to identify exactly WHERE things break.

Usage:
    python debug_ccbh.py
    python debug_ccbh.py shen2011.fits
    python debug_ccbh.py --step 2   # Run only step 2
"""

import sys
from pathlib import Path

# === CONFIGURATION ===
SCRIPT_DIR = Path(__file__).parent
DEFAULT_FITS = SCRIPT_DIR / "shen2011.fits"


def print_header(step_num, title):
    """Print a big visible header."""
    print("\n" + "=" * 70)
    print(f"🔬 STEP {step_num}: {title}")
    print("=" * 70)


def print_success(msg):
    print(f"✅ SUCCESS: {msg}")


def print_error(msg):
    print(f"❌ ERROR: {msg}")


def print_warning(msg):
    print(f"⚠️ WARNING: {msg}")


# ============================================================================
# STEP 1: Check Dependencies
# ============================================================================
def step1_check_dependencies():
    print_header(1, "CHECKING DEPENDENCIES")

    all_ok = True

    # NumPy
    try:
        import numpy as np

        print_success(f"numpy {np.__version__}")
    except ImportError:
        print_error("numpy not installed! Run: pip install numpy")
        all_ok = False

    # Astropy (critical for FITS)
    try:
        import astropy

        print_success(f"astropy {astropy.__version__}")
    except ImportError:
        print_error("astropy not installed! Run: pip install astropy")
        all_ok = False

    # SciPy
    try:
        import scipy

        print_success(f"scipy {scipy.__version__}")
    except ImportError:
        print_warning("scipy not installed (optional but recommended)")

    # Matplotlib
    try:
        import matplotlib

        print_success(f"matplotlib {matplotlib.__version__}")
    except ImportError:
        print_warning("matplotlib not installed (needed for plots)")

    return all_ok


# ============================================================================
# STEP 2: Check File Exists
# ============================================================================
def step2_check_file(filepath):
    print_header(2, "CHECKING FILE")

    filepath = Path(filepath)
    print(f"Looking for: {filepath}")
    print(f"Absolute path: {filepath.absolute()}")

    if filepath.exists():
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print_success(f"File exists! Size: {size_mb:.2f} MB")
        return True
    else:
        print_error(f"File NOT found: {filepath}")
        print("\n📂 Files in current directory:")
        for f in SCRIPT_DIR.glob("*.fits"):
            print(f"   - {f.name}")
        return False


# ============================================================================
# STEP 3: Load FITS File
# ============================================================================
def step3_load_fits(filepath):
    print_header(3, "LOADING FITS FILE")

    try:
        from astropy.io import fits
        from astropy.table import Table
    except ImportError:
        print_error("astropy not imported!")
        return None

    filepath = Path(filepath)

    # Try Table.read first
    try:
        print("Trying: Table.read()...")
        table = Table.read(filepath)
        print_success(f"Loaded {len(table)} rows using Table.read()")
        print(f"\n📋 Column names ({len(table.colnames)} total):")
        for i, col in enumerate(table.colnames):
            print(f"   {i+1:3d}. {col}")
        return table
    except Exception as e:
        print_warning(f"Table.read failed: {e}")

    # Try fits.open
    try:
        print("\nTrying: fits.open()...")
        with fits.open(filepath) as hdul:
            print(f"HDU list: {[h.name for h in hdul]}")
            data = hdul[1].data
            print_success(f"Loaded {len(data)} rows using fits.open()")
            print(f"\n📋 Column names ({len(data.dtype.names)} total):")
            for i, col in enumerate(data.dtype.names):
                print(f"   {i+1:3d}. {col}")
            return data
    except Exception as e:
        print_error(f"fits.open failed: {e}")
        return None


# ============================================================================
# STEP 4: Extract Essential Columns
# ============================================================================
def step4_extract_columns(data):
    print_header(4, "EXTRACTING ESSENTIAL COLUMNS")

    import numpy as np

    # Get column names
    if hasattr(data, "colnames"):
        cols = data.colnames
    elif hasattr(data, "dtype"):
        cols = list(data.dtype.names)
    else:
        print_error("Cannot determine column names!")
        return None

    # Define what we're looking for
    search_map = {
        "z (redshift)": ["z", "Z", "REDSHIFT", "redshift"],
        "logMBH (BH mass)": [
            "logBH",
            "LOGBH_HB_VP06",
            "LOGBH_MGII_S11",
            "LOGBH",
            "logMBH",
            "LOG_MBH",
            "logMBH_HB",
        ],
        "logMBH_err": ["e_logBH", "ERR_LOGBH_HB_VP06", "ERR_LOGBH", "LOGBH_ERR", "e_logMBH"],
        "logLbol": ["logLbol", "LOGLBOL", "LOG_LBOL", "Lbol"],
    }

    result = {}
    for key, possible in search_map.items():
        found = False
        for name in possible:
            if name in cols:
                arr = np.array(data[name])
                result[key.split(" ")[0]] = arr
                print_success(
                    f"{key} <- '{name}' (min={np.nanmin(arr):.2f}, max={np.nanmax(arr):.2f})"
                )
                found = True
                break
        if not found:
            print_warning(f"{key} NOT FOUND (tried: {possible})")

    # Check critical columns
    if "z" not in result:
        print_error("CRITICAL: 'z' (redshift) column not found!")
        print("\n🔍 Looking for columns containing 'z' or 'red':")
        for c in cols:
            if "z" in c.lower() or "red" in c.lower():
                print(f"   - {c}")
        return None

    if "logMBH" not in result:
        print_error("CRITICAL: 'logMBH' (black hole mass) column not found!")
        print("\n🔍 Looking for columns containing 'bh' or 'mass':")
        for c in cols:
            if "bh" in c.lower() or "mass" in c.lower():
                print(f"   - {c}")
        return None

    return result


# ============================================================================
# STEP 5: Check Data Quality
# ============================================================================
def step5_check_quality(data):
    print_header(5, "CHECKING DATA QUALITY")

    import numpy as np

    z = data["z"]
    logMBH = data["logMBH"]

    print(f"\n📊 REDSHIFT (z):")
    print(f"   Total objects: {len(z)}")
    print(f"   Range: {np.nanmin(z):.3f} - {np.nanmax(z):.3f}")
    print(f"   NaN count: {np.sum(np.isnan(z))}")
    print(f"   Negative/Zero: {np.sum(z <= 0)}")

    print(f"\n📊 BLACK HOLE MASS (logMBH):")
    print(f"   Total objects: {len(logMBH)}")
    print(f"   Range: {np.nanmin(logMBH):.2f} - {np.nanmax(logMBH):.2f}")
    print(f"   NaN count: {np.sum(np.isnan(logMBH))}")
    print(f"   < 6.0 (too small): {np.sum(logMBH < 6.0)}")
    print(f"   > 11.0 (too big): {np.sum(logMBH > 11.0)}")

    # Valid data count
    valid = np.isfinite(z) & np.isfinite(logMBH) & (z > 0) & (logMBH > 6) & (logMBH < 11)
    print(f"\n✅ VALID OBJECTS: {np.sum(valid)} / {len(z)} ({100*np.sum(valid)/len(z):.1f}%)")

    return np.sum(valid) > 100


# ============================================================================
# STEP 6: Quick k Estimation
# ============================================================================
def step6_quick_k(data):
    print_header(6, "QUICK k ESTIMATION")

    import numpy as np

    z = data["z"]
    logMBH = data["logMBH"]

    # Clean data
    valid = (
        np.isfinite(z) & np.isfinite(logMBH) & (z > 0.1) & (z < 5.0) & (logMBH > 6) & (logMBH < 11)
    )
    z_clean = z[valid]
    logMBH_clean = logMBH[valid]

    print(f"Using {len(z_clean)} valid objects")

    # Scale factor: a = 1/(1+z)
    a = 1.0 / (1.0 + z_clean)
    log_a = np.log10(a)

    # Simple linear regression: logMBH = const + k * log(a)
    # k = slope of logMBH vs log(a)
    from numpy.polynomial import polynomial as P

    coef = np.polyfit(log_a, logMBH_clean, 1)
    k_raw = coef[0]
    intercept = coef[1]

    print(f"\n📈 RAW LINEAR FIT (no bias correction):")
    print(f"   k_raw = {k_raw:.3f}")
    print(f"   intercept = {intercept:.2f}")

    # Expected results
    print(f"\n📌 INTERPRETATION:")
    print(f"   k = 0: No cosmological coupling (Standard GR)")
    print(f"   k = 1: Comoving scenario")
    print(f"   k = 3: Vacuum energy interior (Dark energy!)")

    if k_raw < 0.5:
        print_warning(
            f"k_raw = {k_raw:.2f} → Likely consistent with k=0 (selection bias dominates)"
        )
    elif k_raw < 1.5:
        print_success(f"k_raw = {k_raw:.2f} → Consistent with k≈1 (some coupling)")
    elif k_raw < 2.5:
        print_success(f"k_raw = {k_raw:.2f} → Potentially interesting! Needs bias correction.")
    else:
        print_warning(f"k_raw = {k_raw:.2f} → Very high! May indicate data issues or strong bias.")

    return k_raw


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "🔥" * 35)
    print("    CCBH DEBUG SCRIPT - Step by Step")
    print("🔥" * 35)

    # Parse args
    fits_file = DEFAULT_FITS
    if len(sys.argv) > 1:
        if not sys.argv[1].startswith("--"):
            fits_file = Path(sys.argv[1])

    print(f"\n📂 Input file: {fits_file}")

    # Run all steps
    results = {}

    # Step 1
    ok = step1_check_dependencies()
    results["step1"] = ok
    if not ok:
        print("\n❌ STOPPED: Missing dependencies. Install them and retry.")
        return 1

    # Step 2
    ok = step2_check_file(fits_file)
    results["step2"] = ok
    if not ok:
        print("\n❌ STOPPED: File not found.")
        return 1

    # Step 3
    raw_data = step3_load_fits(fits_file)
    results["step3"] = raw_data is not None
    if raw_data is None:
        print("\n❌ STOPPED: Could not load FITS file.")
        return 1

    # Step 4
    data = step4_extract_columns(raw_data)
    results["step4"] = data is not None
    if data is None:
        print("\n❌ STOPPED: Could not extract required columns.")
        return 1

    # Step 5
    ok = step5_check_quality(data)
    results["step5"] = ok
    if not ok:
        print_warning("Data quality issues detected, but continuing...")

    # Step 6
    k = step6_quick_k(data)
    results["step6"] = k is not None

    # Summary
    print("\n" + "=" * 70)
    print("📋 DEBUG SUMMARY")
    print("=" * 70)
    for step, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {step}: {status}")

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 ALL STEPS PASSED! Ready for full analysis.")
        print("\nNext step: python test_uet_prediction.py")
        return 0
    else:
        print("\n⚠️ Some steps failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
