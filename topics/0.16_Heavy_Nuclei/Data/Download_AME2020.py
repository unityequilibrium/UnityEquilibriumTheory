"""
Data Loader: AME2020 (Atomic Mass Evaluation)
=============================================
Topic: 0.16 Heavy Nuclei / 0.5 Nuclear Binding
Source: IMPCAS / IAEA
Target: Binding Energies for all known isotopes.

This replaces the "Liquid Drop Model" estimates with real measured mass defects.
"""

import urllib.request
import sys
from pathlib import Path


def fetch_ame2020():
    print("Downloading AME2020 Mass Evaluation Data...")

    # URL for mass.mas2020.txt (Official ASCII format)
    # Source: https://www-nds.iaea.org/amdc/ame2020/mass.mas20.txt
    url = "https://www-nds.iaea.org/amdc/ame2020/mass.mas20.txt"
    output_filename = "AME2020_mass.txt"

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode("utf-8")

        # Header skipping is handled by the Engine usually, but let's save the whole file
        output_path = Path(__file__).parent / output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)

        print(f"✅ Saved AME2020 data to {output_path}")
        print(f"   Size: {len(data)/1024:.2f} KB")

    except Exception as e:
        print(f"❌ Failed to download AME2020: {e}")


if __name__ == "__main__":
    # Create Data Directory
    Path(__file__).parent.mkdir(parents=True, exist_ok=True)

    fetch_ame2020()

    print(
        "\n[Next Step] Update Engine_Fission_Solver.py to read real binding energies."
    )
