#!/usr/bin/env python3
"""
🌌 MPA-JHU DR7 STELLAR MASS CATALOG DOWNLOADER
==============================================
Downloads the galaxy stellar mass catalog from MPA-Garching
for use in CCBH bias correction.

Files:
- totlgm_dr7_v5_2.fit.gz: Total stellar masses (927,552 galaxies)
- fiblgm_dr7_v5_2.fit.gz: Fiber stellar masses

Reference: Kauffmann et al. (2003), Salim et al. (2007)

Usage:
    python download_mpa_jhu.py
"""

import os
import sys
import urllib.request
import gzip
import shutil
from pathlib import Path

# Base URL
BASE_URL = "https://wwwmpa.mpa-garching.mpg.de/SDSS/DR7/Data/"

# Files to download
FILES = {
    "totlgm_dr7_v5_2.fit.gz": "Total stellar masses (927,552 galaxies)",
    "fiblgm_dr7_v5_2.fit.gz": "Fiber stellar masses",
    "gal_info_dr7_v5_2.fit.gz": "Galaxy info (RA, Dec, z, etc.)",
}

# Output directory
OUTPUT_DIR = Path(__file__).parent / "mpa_jhu_data"


def download_file(url, output_path):
    """Download a file with progress."""
    print(f"📥 Downloading: {url}")
    print(f"   → {output_path}")

    try:
        # Create request with user agent
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (UET Research)"})

        with urllib.request.urlopen(request, timeout=60) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            chunk_size = 1024 * 1024  # 1 MB
            downloaded = 0

            with open(output_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        pct = 100 * downloaded / total_size
                        print(f"   Progress: {pct:.1f}% ({downloaded/1024/1024:.1f} MB)", end="\r")

        print(f"\n   ✅ Downloaded: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True

    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False


def decompress_gz(gz_path, output_path):
    """Decompress a .gz file."""
    print(f"📦 Decompressing: {gz_path.name} → {output_path.name}")

    try:
        with gzip.open(gz_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"   ✅ Decompressed: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False


def verify_fits(filepath):
    """Verify FITS file can be read."""
    try:
        from astropy.io import fits

        with fits.open(filepath) as hdul:
            print(f"   📋 HDUs: {[h.name for h in hdul]}")
            if len(hdul) > 1:
                print(f"   📊 Rows: {len(hdul[1].data)}")
                print(f"   📋 Columns: {list(hdul[1].columns.names)[:5]}...")
        return True
    except Exception as e:
        print(f"   ⚠️ Could not verify: {e}")
        return False


def main():
    print("\n" + "🌌" * 35)
    print("   MPA-JHU DR7 STELLAR MASS CATALOG DOWNLOADER")
    print("🌌" * 35)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\n📂 Output directory: {OUTPUT_DIR}")

    # Download files
    success = []
    for filename, description in FILES.items():
        print(f"\n{'='*60}")
        print(f"📄 {filename}")
        print(f"   {description}")
        print("=" * 60)

        url = BASE_URL + filename
        gz_path = OUTPUT_DIR / filename
        fit_path = OUTPUT_DIR / filename.replace(".gz", "")

        # Check if already exists
        if fit_path.exists():
            print(f"   ℹ️ Already exists: {fit_path.name}")
            print(f"   Size: {fit_path.stat().st_size / 1024 / 1024:.1f} MB")
            verify_fits(fit_path)
            success.append(filename)
            continue

        # Download
        if not gz_path.exists():
            if not download_file(url, gz_path):
                continue

        # Decompress
        if not decompress_gz(gz_path, fit_path):
            continue

        # Verify
        verify_fits(fit_path)
        success.append(filename)

    # Summary
    print("\n" + "=" * 60)
    print("📋 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"   Downloaded: {len(success)}/{len(FILES)} files")

    if len(success) == len(FILES):
        print("\n✅ ALL FILES READY!")
        print("\n📂 Files in output directory:")
        for f in OUTPUT_DIR.glob("*.fit"):
            print(f"   - {f.name} ({f.stat().st_size/1024/1024:.1f} MB)")

        print("\n💡 NEXT STEP:")
        print("   Run: python cross_match_catalogs.py")
        return 0
    else:
        print("\n⚠️ Some files failed to download.")
        print("   Try again or download manually from:")
        print(f"   {BASE_URL}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
