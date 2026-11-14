"""
📥 Download SPARC Galaxy Data
=============================
Downloads rotation curve data from SPARC database.

Source: http://astroweb.cwru.edu/SPARC/
DOI: 10.3847/0004-6256/152/6/157
Reference: Lelli, McGaugh, Schombert (2016)

This script downloads:
1. Galaxy properties table (SPARC_Lelli2016c.mrt)
2. Individual rotation curve files (*_rotmod.dat)
"""

import os
import urllib.request
from pathlib import Path

# SPARC data URLs
SPARC_BASE = "http://astroweb.cwru.edu/SPARC/"
SPARC_TABLE = "SPARC_Lelli2016c.mrt"

# Sample galaxies to download (full curves)
SAMPLE_GALAXIES = [
    "NGC2403",
    "NGC2841",
    "NGC3198",
    "NGC5055",
    "NGC6503",
    "NGC7331",
    "DDO154",
    "DDO170",
    "IC2574",
    "UGC128",
]


def download_file(url: str, dest: Path) -> bool:
    """Download file from URL to destination."""
    try:
        print(f"  Downloading: {url}")
        urllib.request.urlretrieve(url, dest)
        print(f"  ✅ Saved: {dest.name}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def main():
    print("=" * 60)
    print("SPARC DATA DOWNLOADER")
    print("=" * 60)
    print()
    print("Source: Lelli, McGaugh, Schombert (2016)")
    print("DOI: 10.3847/0004-6256/152/6/157")
    print("URL: http://astroweb.cwru.edu/SPARC/")
    print()

    # Output directory
    output_dir = Path(__file__).parent
    print(f"Output: {output_dir}")
    print()

    # Download main table
    print("[1] Galaxy Properties Table")
    print("-" * 40)
    table_url = SPARC_BASE + SPARC_TABLE
    table_dest = output_dir / SPARC_TABLE
    download_file(table_url, table_dest)
    print()

    # Download rotation curves
    print("[2] Rotation Curve Files")
    print("-" * 40)
    success = 0
    for galaxy in SAMPLE_GALAXIES:
        filename = f"{galaxy}_rotmod.dat"
        url = SPARC_BASE + "rotmods/" + filename
        dest = output_dir / filename
        if download_file(url, dest):
            success += 1

    print()
    print("=" * 60)
    print(f"SUMMARY: Downloaded {success}/{len(SAMPLE_GALAXIES)} rotation curves")
    print("=" * 60)

    # Verify
    print()
    print("Files in directory:")
    for f in output_dir.glob("*.dat"):
        print(f"  {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
