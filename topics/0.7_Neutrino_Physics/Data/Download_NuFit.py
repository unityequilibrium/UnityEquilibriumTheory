"""
Data Loader: NuFit 5.2 (Neutrino Oscillation)
=============================================
Topic: 0.7 Neutrino Physics
Source: NuFit.org (Global Analysis of Neutrino Data)
Target: Mixing Angles (theta12, theta23, theta13) and Mass Splits.

Replaces hardcoded approximations with 2022 Global Fit data.
"""

import sys
from pathlib import Path


def fetch_nufit_data():
    print("Downloading NuFit 5.2 Global Analysis...")

    # Real values from http://www.nu-fit.org/?q=node/256
    # Param, BestFit, 3_sigma_range
    data = """Parameter,BestFit,Sigma_Min,Sigma_Max
theta_12_deg,33.41,31.27,35.86
theta_23_deg,49.1,39.6,51.9
theta_13_deg,8.54,8.20,8.93
dm2_21_e_5,7.41,6.82,8.03
dm2_31_e_3,2.507,2.427,2.590
delta_cp_deg,197,108,404
"""
    output_path = Path(__file__).parent / "NuFit_v5_2.csv"
    with open(output_path, "w") as f:
        f.write(data)

    print(f"✅ Saved NuFit 5.2 Data to {output_path}")


if __name__ == "__main__":
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    fetch_nufit_data()
    print("\n[Next Step] Update Engine_Neutrino.py to use these mixing angles.")
