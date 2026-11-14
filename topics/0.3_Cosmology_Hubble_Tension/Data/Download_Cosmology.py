"""
Data Loader: Cosmic Chronometers & Hubble Data
==============================================
Topic: 0.3 Cosmology (Hubble Tension)
Source: Compilation of H(z) measurements (Moresco et al., Farooq et al.)
Target: H(z) vs z data points.

This replaces "hardcoded" Hubble tension values with actual observational data points
to fitting H0.
"""

import urllib.request
import sys
import pandas as pd
from io import StringIO
from pathlib import Path


def fetch_hz_data():
    print("Downloading Cosmic Chronometer H(z) Data...")

    # Using a stable mirror for H(z) compilation (commonly used in tutorials)
    # This dataset contains 30+ measurements of H(z) from differential ages.
    url = "https://raw.githubusercontent.com/carlosap87/Machine_Learning_Cosmology/master/data/Hz.csv"
    output_filename = "Hz_cc_data.csv"

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode("utf-8")

        # Validate it's CSV
        df = pd.read_csv(StringIO(data))
        if "z" not in df.columns or "Hz" not in df.columns:
            raise ValueError("Invalid CSV format")

        output_path = Path(__file__).parent / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)

        print(f"✅ Saved H(z) data to {output_path}")
        print(df.head())

    except Exception as e:
        print(f"❌ Failed to download Data: {e}")
        # Create a fallback small dataset if download fails (for reproducibility)
        print("   Creating fallback dataset based on Moresco et al. 2016...")
        fallback = """z,Hz,err
0.070,69.0,19.6
0.090,69.0,12.0
0.120,68.6,26.2
0.170,83.0,8.0
0.179,75.0,4.0
0.199,75.0,5.0
0.200,72.9,29.6
0.270,77.0,14.0
0.280,88.8,36.6
0.352,83.0,14.0
0.380,83.0,13.5
0.400,95.0,17.0
0.4004,77.0,10.2
0.4247,87.1,11.2
0.4497,92.8,12.9
0.470,89.0,50.0
0.4783,80.9,9.0
0.480,97.0,62.0
0.593,104.0,13.0
0.680,92.0,8.0
0.781,105.0,12.0
0.875,125.0,17.0
0.880,90.0,40.0
0.900,117.0,23.0
1.037,154.0,20.0
1.300,168.0,17.0
1.363,160.0,33.6
1.430,177.0,18.0
1.530,140.0,14.0
1.750,202.0,40.0
1.965,186.5,50.4
"""
        output_path = Path(__file__).parent / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(fallback)
        print("✅ Saved Fallback Data.")


if __name__ == "__main__":
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    fetch_hz_data()
    print("\n[Next Step] Update Engine_Hubble.py to fit H0 from this data.")
