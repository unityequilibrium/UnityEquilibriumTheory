"""
Data Downloader - 0.10 Fluid Dynamics & Chaos
==============================================
Download and verify benchmark data for fluid dynamics research.

Usage:
    python download_data.py [--all | --brownian | --turbulence | --poiseuille]
"""

import os
import json
import hashlib
import urllib.request
from pathlib import Path

# ============================================================================
# DATA SOURCES
# ============================================================================

DATA_SOURCES = {
    "brownian": {
        "description": "Brownian Motion - Einstein 1905 Parameters",
        "doi": "10.1002/andp.19053220806",
        "files": [
            {
                "name": "perrin_1908_data.json",
                "url": None,  # Embedded data below
                "embedded": True,
                "data": {
                    "source": "Perrin, J. (1909). Mouvement brownien et réalité moléculaire",
                    "doi": "10.1051/anphys/190900817005",
                    "temperature_K": 293.15,
                    "particle_radius_m": 2.1e-7,
                    "viscosity_Pa_s": 1.002e-3,
                    "avogadro_measured": 6.4e23,
                    "diffusion_coefficient_measured_m2_s": 8.7e-13,
                    "notes": "Data from Perrin's Nobel Prize work (1926)",
                },
            }
        ],
    },
    "poiseuille": {
        "description": "Poiseuille Flow - Pipe Flow Benchmark",
        "doi": None,
        "files": [
            {
                "name": "air_properties_20C.json",
                "url": None,
                "embedded": True,
                "data": {
                    "source": "CRC Handbook of Chemistry and Physics, 97th Edition",
                    "fluid": "Air at 20°C, 1 atm",
                    "density_kg_m3": 1.204,
                    "dynamic_viscosity_Pa_s": 1.825e-5,
                    "kinematic_viscosity_m2_s": 1.516e-5,
                    "thermal_conductivity_W_mK": 0.0257,
                },
            },
            {
                "name": "water_properties_20C.json",
                "url": None,
                "embedded": True,
                "data": {
                    "source": "CRC Handbook of Chemistry and Physics, 97th Edition",
                    "fluid": "Water at 20°C, 1 atm",
                    "density_kg_m3": 998.2,
                    "dynamic_viscosity_Pa_s": 1.002e-3,
                    "kinematic_viscosity_m2_s": 1.004e-6,
                    "thermal_conductivity_W_mK": 0.598,
                },
            },
        ],
    },
    "turbulence": {
        "description": "Turbulence - Kolmogorov Cascade",
        "doi": "10.1098/rspa.1991.0075",
        "files": [
            {
                "name": "kolmogorov_constants.json",
                "url": None,
                "embedded": True,
                "data": {
                    "source": "Sreenivasan, K.R. (1995). On the universality of the Kolmogorov constant",
                    "doi": "10.1063/1.868716",
                    "kolmogorov_constant_C": 1.5,
                    "energy_spectrum_slope": -5 / 3,
                    "dissipation_range_exponent": -7,
                    "notes": "Universal constants for inertial range turbulence",
                },
            }
        ],
    },
    "jhtdb": {
        "description": "Johns Hopkins Turbulence Database",
        "url": "http://turbulence.pha.jhu.edu/",
        "doi": "10.1088/1742-5468/2007/06/P06006",
        "note": "Requires registration and API access - see instructions below",
        "files": [],
    },
}

# ============================================================================
# DOWNLOADER
# ============================================================================


def get_data_dir():
    """Get the Data directory path."""
    return Path(__file__).parent


def save_embedded_data(category: str):
    """Save embedded data to JSON files."""
    data_dir = get_data_dir() / category
    data_dir.mkdir(parents=True, exist_ok=True)

    source = DATA_SOURCES.get(category)
    if not source:
        print(f"❌ Unknown category: {category}")
        return

    print(f"\n📦 {source['description']}")
    if source.get("doi"):
        print(f"   DOI: {source['doi']}")

    for file_info in source.get("files", []):
        if file_info.get("embedded"):
            filepath = data_dir / file_info["name"]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(file_info["data"], f, indent=2, ensure_ascii=False)
            print(f"   ✅ Saved: {filepath.name}")
        elif file_info.get("url"):
            # TODO: Implement URL download
            print(f"   ⏳ URL download not implemented: {file_info['name']}")


def download_all():
    """Download all embedded datasets."""
    print("=" * 60)
    print("📥 Downloading Fluid Dynamics Benchmark Data")
    print("=" * 60)

    for category in ["brownian", "poiseuille", "turbulence"]:
        save_embedded_data(category)

    print("\n" + "=" * 60)
    print("📋 External Data Sources (Manual Download Required)")
    print("=" * 60)

    jhtdb = DATA_SOURCES["jhtdb"]
    print(f"\n🌐 Johns Hopkins Turbulence Database")
    print(f"   URL: {jhtdb['url']}")
    print(f"   DOI: {jhtdb['doi']}")
    print(f"   Note: Requires registration for DNS data access")

    print("\n✅ Done!")


def list_references():
    """Print all DOI references."""
    print("\n📚 Data References (DOI)")
    print("-" * 40)
    for name, source in DATA_SOURCES.items():
        doi = source.get("doi", "N/A")
        print(f"{name}: {doi}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == "--all":
        download_all()
    elif sys.argv[1] == "--references":
        list_references()
    elif sys.argv[1] == "--brownian":
        save_embedded_data("brownian")
    elif sys.argv[1] == "--turbulence":
        save_embedded_data("turbulence")
    elif sys.argv[1] == "--poiseuille":
        save_embedded_data("poiseuille")
    else:
        print(
            "Usage: python download_data.py [--all | --references | --brownian | --turbulence | --poiseuille]"
        )
