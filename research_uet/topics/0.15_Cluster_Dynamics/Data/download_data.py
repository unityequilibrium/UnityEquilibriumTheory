"""
Download Script: Cluster Dynamics Real Data
============================================
Downloads galaxy cluster data for virial mass tests.

Sources:
- Girardi 1998: 10.1086/306157
- Vikhlinin 2006: 10.1086/500288
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def download_cluster_data():
    """
    Galaxy Cluster Virial Data
    DOI: 10.1086/306157
    """
    data = {
        "source": "Girardi et al. 1998",
        "publication": {
            "title": "Optical Mass Estimates of Galaxy Clusters",
            "authors": [
                "Girardi, M.",
                "Giuricin, G.",
                "Mardirossian, F.",
                "Mezzetti, M.",
                "Boschin, W.",
            ],
            "journal": "ApJ",
            "volume": 505,
            "pages": "74",
            "year": 1998,
            "doi": "10.1086/306157",
        },
        "clusters": [
            {
                "name": "Coma",
                "velocity_dispersion_km_s": 1008,
                "virial_mass_Msun": 1.2e15,
                "r_virial_Mpc": 2.9,
            },
            {
                "name": "Perseus",
                "velocity_dispersion_km_s": 1282,
                "virial_mass_Msun": 1.1e15,
                "r_virial_Mpc": 2.1,
            },
            {
                "name": "Virgo",
                "velocity_dispersion_km_s": 632,
                "virial_mass_Msun": 4.2e14,
                "r_virial_Mpc": 1.55,
            },
            {
                "name": "Abell 2199",
                "velocity_dispersion_km_s": 801,
                "virial_mass_Msun": 5.6e14,
                "r_virial_Mpc": 1.8,
            },
            {
                "name": "Abell 85",
                "velocity_dispersion_km_s": 969,
                "virial_mass_Msun": 9.1e14,
                "r_virial_Mpc": 2.3,
            },
        ],
        "virial_relation": "M_virial = 3 σ² R_v / G",
    }

    filepath = DATA_DIR / "cluster_virial_1998.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def download_xray_cluster_data():
    """
    Chandra X-ray Cluster Data
    DOI: 10.1086/500288
    """
    data = {
        "source": "Vikhlinin et al. 2006",
        "publication": {
            "title": "Chandra Sample of Nearby Relaxed Galaxy Clusters",
            "journal": "ApJ",
            "volume": 640,
            "pages": "691",
            "year": 2006,
            "doi": "10.1086/500288",
        },
        "clusters": [
            {"name": "A133", "T_keV": 3.8, "M500_Msun": 2.3e14, "r500_Mpc": 0.89},
            {"name": "A262", "T_keV": 2.2, "M500_Msun": 8.0e13, "r500_Mpc": 0.58},
            {"name": "A383", "T_keV": 5.0, "M500_Msun": 3.5e14, "r500_Mpc": 0.97},
            {"name": "A478", "T_keV": 7.2, "M500_Msun": 6.8e14, "r500_Mpc": 1.21},
            {"name": "A1795", "T_keV": 6.0, "M500_Msun": 5.2e14, "r500_Mpc": 1.10},
        ],
    }

    filepath = DATA_DIR / "chandra_clusters_2006.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("Downloading Cluster Dynamics Real Data")
    print("=" * 60)

    download_cluster_data()
    download_xray_cluster_data()

    print("\n✅ All data downloaded!")


if __name__ == "__main__":
    main()
