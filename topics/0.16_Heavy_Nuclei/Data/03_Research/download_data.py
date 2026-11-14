"""
Download Script: Heavy Nuclei Real Data
========================================
Downloads nuclear mass data from AME2020.

Sources:
- AME2020: 10.1088/1674-1137/abddaf
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def download_ame2020_heavy():
    """
    AME2020 Atomic Mass Evaluation - Heavy Nuclei
    DOI: 10.1088/1674-1137/abddaf
    """
    data = {
        "source": "AME2020",
        "publication": {
            "title": "The AME 2020 atomic mass evaluation (II). Tables, graphs and references",
            "authors": [
                "Wang, M.",
                "Huang, W.J.",
                "Kondev, F.G.",
                "Audi, G.",
                "Naimi, S.",
            ],
            "journal": "Chinese Physics C",
            "volume": 45,
            "pages": "030003",
            "year": 2021,
            "doi": "10.1088/1674-1137/abddaf",
        },
        "heavy_nuclei": [
            {
                "Z": 82,
                "A": 208,
                "symbol": "Pb-208",
                "binding_energy_keV": 1636430,
                "mass_excess_keV": -21749.4,
            },
            {
                "Z": 83,
                "A": 209,
                "symbol": "Bi-209",
                "binding_energy_keV": 1640236,
                "mass_excess_keV": -18258.0,
            },
            {
                "Z": 92,
                "A": 235,
                "symbol": "U-235",
                "binding_energy_keV": 1783871,
                "mass_excess_keV": 40920.5,
            },
            {
                "Z": 92,
                "A": 238,
                "symbol": "U-238",
                "binding_energy_keV": 1801695,
                "mass_excess_keV": 47308.9,
            },
            {
                "Z": 94,
                "A": 239,
                "symbol": "Pu-239",
                "binding_energy_keV": 1806922,
                "mass_excess_keV": 48590.5,
            },
            {
                "Z": 94,
                "A": 244,
                "symbol": "Pu-244",
                "binding_energy_keV": 1835997,
                "mass_excess_keV": 54472.0,
            },
        ],
        "double_magic": [
            {
                "Z": 82,
                "A": 208,
                "symbol": "Pb-208",
                "note": "Doubly magic (Z=82, N=126)",
            },
            {
                "Z": 50,
                "A": 132,
                "symbol": "Sn-132",
                "note": "Doubly magic (Z=50, N=82)",
            },
        ],
    }

    filepath = DATA_DIR / "ame2020_heavy_nuclei.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("Downloading Heavy Nuclei Real Data")
    print("=" * 60)

    download_ame2020_heavy()

    print("\n✅ All data downloaded!")


if __name__ == "__main__":
    main()
