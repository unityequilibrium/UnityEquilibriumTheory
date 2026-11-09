"""
Data Loader: Muon g-2 Anomaly
=============================
Topic: 0.8 Muon g-2
Source: Fermilab (FNAL) / Brookhaven (BNL)
Target: Anomalous magnetic moment a_mu (Experiment vs Standard Model).

Replaces theoretical placeholder with the famous 4.2 sigma tension data.
"""

import sys
from pathlib import Path


def fetch_muon_g2_data():
    print("Downloading Muon g-2 Data (FNAL 2023)...")

    # Values from PRL 131, 161802 (2023)
    # a_mu (Exp) = 116 592 059 (22) x 10^-11
    # a_mu (SM)  = 116 591 810 (43) x 10^-11 (White Paper 2020)

    csv_content = """Source,Value_e11,Uncertainty_e11,Year
Standard_Model_WP,116591810,43,2020
BNL_Experiment,116592089,63,2006
FNAL_Run1,116592040,54,2021
FNAL_Run23,116592055,24,2023
World_Average_Exp,116592059,22,2023
"""
    output_path = Path(__file__).parent / "Muon_g2_Values.csv"
    with open(output_path, "w") as f:
        f.write(csv_content)

    print(f"✅ Saved Muon g-2 Data to {output_path}")


if __name__ == "__main__":
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)
    fetch_muon_g2_data()
    print(
        "\n[Next Step] Update Engine_Muon_g2.py to calculate UET prediction vs this gap."
    )
