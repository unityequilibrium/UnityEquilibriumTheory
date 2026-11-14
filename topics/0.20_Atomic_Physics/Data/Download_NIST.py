"""
Data Loader: NIST Atomic Spectra Database
=========================================
Topic: 0.20 Atomic Physics
Source: NIST ASD (physics.nist.gov)
Target: Hydrogen (H I) and Helium (He I) Emission Lines.

This script fetches real experimental data to replace synthetic random generation.
"""

import urllib.request
import csv
import sys
from pathlib import Path


def fetch_nist_data(element, spectrum, output_filename):
    print(f"Downloading NIST Data for {element} {spectrum}...")

    # NIST ASD Export URL format
    # This is a query for observed lines between 300nm and 800nm (Visible)
    url = (
        f"https://physics.nist.gov/cgi-bin/ASD/lines1.pl?spectra={element}+{spectrum}"
        "&limits_type=0&low_w=300&upp_w=800&unit=1&submit=Retrieve+Data&format=1"
        "&line_out=0&en_unit=1&output=0&bibrefs=1&page_size=15&show_obs_wl=1"
        "&show_calc_wl=1&show_trans_prob=1&show_os_str=1&show_energy=1"
    )

    try:
        # NIST returns HTML/Text. We will save it raw first.
        with urllib.request.urlopen(url) as response:
            data = response.read().decode("utf-8")

        # Parse CSV-like structure (NIST format 1 is ASCII)
        # We'll save it as simple CSV: Wavelength, RelInt, Aki

        parsed_lines = []
        for line in data.split("\n"):
            if line.strip().startswith('"') and "," in line:
                # This usage depends on precise NIST output format which can change.
                # For robustness, we save the raw data for parsing by the Engine.
                pass

        # Save Raw Data
        output_path = Path(__file__).parent / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)

        print(f"✅ Saved raw data to {output_path}")

    except Exception as e:
        print(f"❌ Failed to download {element}: {e}")


if __name__ == "__main__":
    # Create Data Directory if missing
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)

    # 1. Hydrogen (Z=1)
    fetch_nist_data("H", "I", "NIST_Hydrogen_Visible.csv")

    # 2. Helium (Z=2)
    fetch_nist_data("He", "I", "NIST_Helium_Visible.csv")

    print("\n[Next Step] Updates Engine_Hydrogen.py to parse these CSV files.")
