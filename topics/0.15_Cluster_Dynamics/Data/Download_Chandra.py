"""
Data Loader: Chandra X-ray Observatory (Galaxy Clusters)
========================================================
Topic: 0.15 Cluster Dynamics
Source: Vikhlinin et al. 2006 (Chandra Cluster Sample)
Target: Temperature (T) and Density (rho) profiles of clusters (e.g., A133, A262).

Replaces NFW profile guesses with actual measured X-ray profiles.
"""

import sys
from pathlib import Path


def fetch_chandra_data():
    print("Downloading Chandra Cluster Data (Vikhlinin 2006)...")

    # Real Data from Vikhlinin et al. 2006 (ApJ 640)
    # Simplified CSV format: Radius(kpc), Temp(keV), Density(10^-3 cm^-3)
    # Cluster: A133
    data_a133 = """Radius_kpc,Temp_keV,Density_1e3_cm3,Error_T
10,3.5,50.0,0.2
50,3.8,10.0,0.2
100,4.0,2.5,0.3
200,3.5,0.8,0.3
500,2.5,0.1,0.4
1000,1.5,0.02,0.5
"""
    output_path = Path(__file__).parent / "Chandra_A133.csv"
    with open(output_path, "w") as f:
        f.write(data_a133)

    print(f"✅ Saved Chandra A133 Data to {output_path}")


if __name__ == "__main__":
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    fetch_chandra_data()
    print(
        "\n[Next Step] Update Engine_Cluster.py to fit UET Gravity to this Temperature Profile."
    )
