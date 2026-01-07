#!/usr/bin/env python3
"""
🔍 QUERY SHEN 2011 BLACK HOLE MASSES FROM VIZIER
================================================
The main Shen catalog has multiple tables. We need the one with BH masses.

VizieR Tables:
- J/ApJS/194/45/catalog - Main catalog (positions, z, Lbol)
- J/ApJS/194/45/table2 - Quasar properties including BH masses

Usage:
    python query_shen_bh_masses.py
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "vizier_data"


def query_all_shen_tables():
    """Query all available tables in J/ApJS/194/45."""
    from astroquery.vizier import Vizier

    print("🔍 Querying ALL tables in J/ApJS/194/45...")

    # Configure Vizier
    Vizier.ROW_LIMIT = 10  # Just get sample first

    try:
        catalogs = Vizier.get_catalogs("J/ApJS/194/45")

        print(f"\n📋 Found {len(catalogs)} table(s):")
        for i, cat in enumerate(catalogs):
            name = cat.meta.get("name", "Unknown")
            desc = cat.meta.get("description", "")[:60]
            print(f"\n   {i+1}. {name}")
            print(f"      Rows: {len(cat)} (sample)")
            print(f"      Columns: {cat.colnames}")
            if desc:
                print(f"      Description: {desc}...")

        return catalogs

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def download_bh_masses():
    """Download the table with BH masses."""
    from astroquery.vizier import Vizier

    # Try to get the properties table with BH masses
    # VizieR catalog structure for Shen 2011:
    # - table1 or catalog = main table
    # - table2 = full properties including Hbeta, MgII, CIV derived BH masses

    print("\n📥 Attempting to download BH mass table...")

    Vizier.ROW_LIMIT = -1  # All rows
    Vizier.TIMEOUT = 600  # 10 minutes

    # Try different table specifications
    table_specs = [
        "J/ApJS/194/45/table2",  # Properties table
        "J/ApJS/194/45/qso",  # QSO table
        "J/ApJS/194/45/props",  # Properties
    ]

    for spec in table_specs:
        print(f"\n   Trying: {spec}")
        try:
            result = Vizier.get_catalogs(spec)
            if result and len(result) > 0:
                table = result[0]
                print(f"   ✅ Got {len(table)} rows!")
                print(f"   Columns: {table.colnames[:15]}...")

                # Check for BH mass columns
                bh_cols = [c for c in table.colnames if "bh" in c.lower() or "mass" in c.lower()]
                if bh_cols:
                    print(f"   🎯 BH-related columns: {bh_cols}")

                return table
        except Exception as e:
            print(f"   ❌ {e}")

    return None


def merge_with_existing():
    """Merge with already downloaded Shen2011 full catalog."""
    from astropy.table import Table
    import numpy as np

    # Load existing catalog
    main_path = OUTPUT_DIR / "shen2011_full.fits"
    bh_path = SCRIPT_DIR / "shen2011.fits"  # Our original simplified version with BH masses!

    print("\n📊 Checking existing files...")

    if main_path.exists():
        main = Table.read(main_path)
        print(f"   Main catalog: {len(main)} rows")
        print(f"   Columns: {main.colnames}")

    if bh_path.exists():
        bh = Table.read(bh_path)
        print(f"\n   BH catalog (original): {len(bh)} rows")
        print(f"   Columns: {bh.colnames}")

        # This has logBH! We can use this directly
        if "logBH" in bh.colnames or "logBH" in [c.upper() for c in bh.colnames]:
            print("\n   🎯 FOUND: Our original shen2011.fits HAS logBH!")
            print("   We can use this directly for CCBH analysis!")
            return bh

    return None


def main():
    print("\n" + "🔍" * 35)
    print("   QUERY SHEN 2011 BH MASSES")
    print("🔍" * 35)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # First, check what we already have
    result = merge_with_existing()

    if result is not None:
        print("\n" + "=" * 60)
        print("📋 SOLUTION FOUND!")
        print("=" * 60)
        print("\n✅ Our original shen2011.fits already has the BH masses!")
        print("   The new shen2011_full.fits has RA/Dec coordinates.")
        print("\n💡 STRATEGY:")
        print("   1. Use shen2011.fits for z and logBH")
        print("   2. Use shen2011_full.fits for RA/Dec (if cross-matching needed)")
        print("   3. Merge by matching on z or SDSS name")
        return 0

    # Query available tables
    print("\n" + "-" * 60)
    catalogs = query_all_shen_tables()

    # Try to download BH masses
    print("\n" + "-" * 60)
    bh_table = download_bh_masses()

    if bh_table is not None:
        # Save
        output_path = OUTPUT_DIR / "shen2011_bh_masses.fits"
        bh_table.write(output_path, format="fits", overwrite=True)
        print(f"\n✅ Saved: {output_path}")
    else:
        print("\n⚠️ Could not download BH mass table directly.")
        print("   But our original shen2011.fits has the data we need!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
