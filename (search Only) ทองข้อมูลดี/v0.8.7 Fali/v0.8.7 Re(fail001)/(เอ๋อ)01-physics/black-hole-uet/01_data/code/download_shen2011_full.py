#!/usr/bin/env python3
"""
🌟 DOWNLOAD FULL SHEN 2011 CATALOG FROM VIZIER
==============================================
Downloads the complete SDSS DR7 Quasar Catalog (Shen et al. 2011)
with all 105,783 quasars including RA, Dec, z, BH masses, etc.

VizieR Catalog: J/ApJS/194/45

Usage:
    python download_shen2011_full.py
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "vizier_data"


def download_via_astroquery():
    """Download using astroquery (preferred method)."""
    try:
        from astroquery.vizier import Vizier
        import astropy.units as u
    except ImportError:
        print("❌ astroquery not installed!")
        print("   Run: pip install astroquery")
        return None

    print("📥 Downloading full Shen 2011 catalog from VizieR...")
    print("   Catalog: J/ApJS/194/45")
    print("   Expected: 105,783 quasars")

    # Configure Vizier to get all rows and all columns
    Vizier.ROW_LIMIT = -1  # No limit
    Vizier.TIMEOUT = 300  # 5 minutes

    try:
        # Query the main quasar table
        print("\n🔍 Querying VizieR (this may take 1-2 minutes)...")
        catalogs = Vizier.get_catalogs("J/ApJS/194/45")

        print(f"\n📋 Found {len(catalogs)} table(s)")
        for i, cat in enumerate(catalogs):
            print(f"   {i+1}. {cat.meta.get('name', 'Unknown')}: {len(cat)} rows")

        # The main table is usually the largest one
        main_table = max(catalogs, key=len)
        print(f"\n✅ Main table: {len(main_table)} rows, {len(main_table.colnames)} columns")
        print(f"   Columns: {main_table.colnames[:10]}...")

        return main_table

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def download_via_tap():
    """Alternative: Download using TAP service."""
    try:
        from astroquery.utils.tap.core import TapPlus
    except ImportError:
        print("❌ astroquery not installed!")
        return None

    print("📥 Downloading via TAP service...")

    try:
        tap = TapPlus(url="https://tapvizier.cds.unistra.fr/TAPVizieR/tap")

        query = """
        SELECT TOP 200000 *
        FROM "J/ApJS/194/45/table2"
        """

        print("   Executing ADQL query...")
        job = tap.launch_job(query)
        result = job.get_results()

        print(f"✅ Got {len(result)} rows")
        return result

    except Exception as e:
        print(f"❌ TAP Error: {e}")
        return None


def download_via_url():
    """Fallback: Direct FTP download."""
    import urllib.request
    import gzip

    # VizieR FTP location
    base_url = "https://cdsarc.cds.unistra.fr/ftp/J/ApJS/194/45/"
    files = ["table2.dat.gz", "ReadMe"]

    print("📥 Downloading via FTP (fallback method)...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    for filename in files:
        url = base_url + filename
        output_path = OUTPUT_DIR / filename

        print(f"   Downloading: {filename}")
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (UET Research)"}
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                with open(output_path, "wb") as f:
                    f.write(response.read())
            print(f"   ✅ Saved: {output_path.name}")

            # Decompress if .gz
            if filename.endswith(".gz"):
                dat_path = OUTPUT_DIR / filename.replace(".gz", "")
                with gzip.open(output_path, "rb") as f_in:
                    with open(dat_path, "wb") as f_out:
                        f_out.write(f_in.read())
                print(f"   ✅ Decompressed: {dat_path.name}")

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return None

    return OUTPUT_DIR / "table2.dat"


def save_fits(table, filename):
    """Save table as FITS file."""
    output_path = OUTPUT_DIR / filename
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n💾 Saving as FITS: {output_path}")
    table.write(output_path, format="fits", overwrite=True)
    print(f"   ✅ Saved: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    return output_path


def main():
    print("\n" + "🌟" * 35)
    print("   DOWNLOAD FULL SHEN 2011 CATALOG")
    print("🌟" * 35)

    # Try astroquery first
    result = download_via_astroquery()

    if result is None:
        print("\n⚠️ astroquery failed, trying TAP...")
        result = download_via_tap()

    if result is None:
        print("\n⚠️ TAP failed, trying direct FTP...")
        dat_path = download_via_url()
        if dat_path:
            print(f"\n✅ Downloaded raw data to: {dat_path}")
            print("   Note: This is ASCII format, needs parsing")
        return 1

    # Save as FITS
    fits_path = save_fits(result, "shen2011_full.fits")

    # Summary
    print("\n" + "=" * 60)
    print("📋 DOWNLOAD COMPLETE")
    print("=" * 60)
    print(f"   Total quasars: {len(result)}")
    print(f"   Columns: {len(result.colnames)}")
    print(f"   Output: {fits_path}")

    # Show key columns
    key_cols = ["RAJ2000", "DEJ2000", "z", "logBH", "e_logBH", "logLbol"]
    print(f"\n📊 Key columns available:")
    for col in key_cols:
        if col in result.colnames:
            print(f"   ✅ {col}")
        else:
            # Try variations
            found = [c for c in result.colnames if col.lower() in c.lower()]
            if found:
                print(f"   ✅ {found[0]} (similar to {col})")
            else:
                print(f"   ❌ {col} (not found)")

    print("\n💡 NEXT STEP:")
    print("   Update cross_match_catalogs.py to use this file!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
