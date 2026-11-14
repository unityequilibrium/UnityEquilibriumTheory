import os
import requests
import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


from docs.core.uet_glass_box import UETPathManager

# URLs for Planck 2018 TT Power Spectrum (Binned)
URLS = [
    "https://lambda.gsfc.nasa.gov/data/Planck/release_3/ancillary-data/cosmoparams/COM_PowerSpect_CMB-TT-binned_R3.01.txt",
    "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/COM_PowerSpect_CMB-TT-binned_R3.01.txt",
]


def download_data():
    # Setup paths
    current_dir = Path(__file__).resolve().parent
    target_dir = current_dir.parents[1] / "Data" / "03_Research"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "planck_tt_spectrum_2018.txt"
    print(f"Target: {target_file}")

    for url in URLS:
        print(f"Attempting download from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ Download successful! Size: {len(response.text)} bytes")
            return True
        except Exception as e:
            print(f"❌ Failed to download from {url}: {e}")
            continue
    return False


if __name__ == "__main__":
    success = download_data()
    sys.exit(0 if success else 1)
