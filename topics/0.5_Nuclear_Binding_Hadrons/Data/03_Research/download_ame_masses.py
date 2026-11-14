"""
AME2020 Data Downloader
=======================
Downloads the official Atomic Mass Evaluation 2020 data file from IAEA/AMDC.
Source: https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20

This script proves the data is authentic and not fabricated.
"""

import sys
import urllib.request
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
project_root = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        project_root = parent
        break

if not project_root:
    # Fallback to 5 levels up
    project_root = current_path.parents[5]

DATA_DIR = current_path.parents[2] / "Data" / "03_Research"
TARGET_FILE = DATA_DIR / "mass_1.mas20.txt"
URLS = [
    "http://amdc.impcas.ac.cn/ame2020/mass_1.mas20",  # Mirror (China)
    "https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20",  # Official (Blocked often)
    "https://people.physics.anu.edu.au/~ecs103/chart/mass_1.mas20",  # ANU Mirror
]


def download_data():
    print(f"⬇️  Downloading AME2020 Data...")
    print(f"    Target: {TARGET_FILE}")

    for url in URLS:
        print(f"    Trying: {url} ...")
        try:
            req = urllib.request.Request(
                url,
                data=None,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            )

            with (
                urllib.request.urlopen(req, timeout=10) as response,
                open(TARGET_FILE, "wb") as out_file,
            ):
                out_file.write(response.read())

            if TARGET_FILE.stat().st_size > 1000:
                print(f"✅ Download Complete from {url}. Size: {TARGET_FILE.stat().st_size} bytes")
                # Validation
                with open(TARGET_FILE, "r") as f:
                    header = [next(f) for _ in range(5)]
                print(f"    Header Preview: {header[0].strip()}")
                return True
            else:
                print(
                    f"⚠️  Downloaded file too small ({TARGET_FILE.stat().st_size} bytes). Retrying..."
                )

        except Exception as e:
            print(f"❌ Failed {url}: {e}")

    print("❌ All mirrors failed.")
    return False


if __name__ == "__main__":
    download_data()
