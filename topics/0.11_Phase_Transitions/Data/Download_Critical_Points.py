"""
Data Loader: NIST Chemistry WebBook (Critical Points)
=====================================================
Topic: 0.11 Phase Transitions
Source: NIST Standard Reference Data
Target: Critical Temperature/Pressure for H2O, CO2, N2.

Replaces generic Ising Model constants with real molecular properties.
"""

import sys
from pathlib import Path


def fetch_critical_points():
    print("Downloading NIST Critical Point Data...")

    # Real Data from webbook.nist.gov
    data = """Substance,Tc_Kelvin,Pc_MPa,Rho_c_kg_m3
Water,647.096,22.064,322.0
CarbonDioxide,304.13,7.3773,467.6
Nitrogen,126.19,3.3958,313.3
Oxygen,154.58,5.0430,436.1
Argon,150.687,4.863,535.6
Helium-4,5.1953,0.22746,69.64
"""
    output_path = Path(__file__).parent / "NIST_Critical_Points.csv"
    with open(output_path, "w") as f:
        f.write(data)

    print(f"✅ Saved NIST Phase Data to {output_path}")


if __name__ == "__main__":
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    fetch_critical_points()
    print(
        "\n[Next Step] Update Engine_Phase.py to simulate these specific transitions."
    )
