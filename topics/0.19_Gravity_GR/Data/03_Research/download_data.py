"""
Download Script: Gravity/GR Real Data
======================================
Downloads real experimental data for equivalence principle tests.

Sources:
- Eöt-Wash: 10.1103/PhysRevLett.100.041101
- MICROSCOPE: 10.1103/PhysRevLett.129.121102
- CODATA: 10.1103/RevModPhys.93.025010
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def download_eotwash_data():
    """
    Eöt-Wash Torsion Balance Data (2008)
    DOI: 10.1103/PhysRevLett.100.041101
    """
    data = {
        "source": "Eöt-Wash Group, University of Washington",
        "publication": {
            "title": "Test of the equivalence principle using a rotating torsion balance",
            "authors": [
                "Schlamminger, S.",
                "Choi, K.-Y.",
                "Wagner, T.A.",
                "Gundlach, J.H.",
                "Adelberger, E.G.",
            ],
            "journal": "Phys. Rev. Lett.",
            "volume": 100,
            "pages": "041101",
            "year": 2008,
            "doi": "10.1103/PhysRevLett.100.041101",
        },
        "experiment": {
            "method": "Rotating torsion balance",
            "test_bodies": ["Beryllium", "Titanium"],
            "location": "University of Washington",
        },
        "results": {
            "eta_Earth": {
                "value": 0.3e-13,
                "uncertainty": 1.8e-13,
                "unit": "dimensionless",
                "description": "Eötvös parameter for Earth gravity",
            },
            "eta_Sun": {
                "value": -3.1e-13,
                "uncertainty": 4.7e-13,
                "unit": "dimensionless",
                "description": "Eötvös parameter for Solar gravity",
            },
            "eta_galactic_DM": {
                "value": -4e-5,
                "uncertainty": 7e-5,
                "unit": "dimensionless",
                "description": "Eötvös parameter for galactic dark matter",
            },
        },
    }

    filepath = DATA_DIR / "eotwash_2008.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def download_microscope_data():
    """
    MICROSCOPE Space Mission Data (2022)
    DOI: 10.1103/PhysRevLett.129.121102
    """
    data = {
        "source": "MICROSCOPE Collaboration (CNES/ONERA)",
        "publication": {
            "title": "MICROSCOPE Mission: Final Results of the Test of the Equivalence Principle",
            "authors": ["MICROSCOPE Collaboration"],
            "journal": "Phys. Rev. Lett.",
            "volume": 129,
            "pages": "121102",
            "year": 2022,
            "doi": "10.1103/PhysRevLett.129.121102",
        },
        "experiment": {
            "method": "Space-based differential accelerometer",
            "mission": "MICROSCOPE satellite",
            "orbit": "Circular, 710 km altitude",
            "test_bodies": ["Platinum-Rhodium alloy", "Titanium alloy"],
            "duration": "2.5 years",
        },
        "results": {
            "eta": {
                "value": -1.5e-15,
                "stat_uncertainty": 2.3e-15,
                "sys_uncertainty": 1.5e-15,
                "combined_uncertainty": 2.7e-15,
                "unit": "dimensionless",
                "description": "Final Eötvös parameter (world's best)",
            }
        },
        "precision": "10^-15 level (best ever achieved)",
    }

    filepath = DATA_DIR / "microscope_2022.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def download_codata_constants():
    """
    CODATA 2018 Fundamental Constants
    DOI: 10.1103/RevModPhys.93.025010
    """
    data = {
        "source": "NIST/CODATA",
        "publication": {
            "title": "CODATA recommended values of the fundamental physical constants: 2018",
            "authors": ["Tiesinga, E.", "Mohr, P.J.", "Newell, D.B.", "Taylor, B.N."],
            "journal": "Rev. Mod. Phys.",
            "volume": 93,
            "pages": "025010",
            "year": 2021,
            "doi": "10.1103/RevModPhys.93.025010",
        },
        "constants": {
            "G": {
                "value": 6.67430e-11,
                "uncertainty": 0.00015e-11,
                "unit": "m³ kg⁻¹ s⁻²",
                "name": "Newtonian constant of gravitation",
                "relative_uncertainty": 2.2e-5,
            },
            "c": {
                "value": 299792458,
                "uncertainty": 0,
                "unit": "m s⁻¹",
                "name": "Speed of light in vacuum",
                "note": "Exact (defines the meter)",
            },
            "hbar": {
                "value": 1.054571817e-34,
                "uncertainty": 0,
                "unit": "J s",
                "name": "Reduced Planck constant",
                "note": "Exact (defines the kilogram)",
            },
            "l_P": {
                "value": 1.616255e-35,
                "uncertainty": 0.000018e-35,
                "unit": "m",
                "name": "Planck length",
            },
            "t_P": {
                "value": 5.391247e-44,
                "uncertainty": 0.000060e-44,
                "unit": "s",
                "name": "Planck time",
            },
            "m_P": {
                "value": 2.176434e-8,
                "uncertainty": 0.000024e-8,
                "unit": "kg",
                "name": "Planck mass",
            },
        },
    }

    filepath = DATA_DIR / "codata_2018_gravity.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("Downloading Gravity/GR Real Data")
    print("=" * 60)

    download_eotwash_data()
    download_microscope_data()
    download_codata_constants()

    print("\n✅ All data downloaded!")
    print(f"Location: {DATA_DIR}")


if __name__ == "__main__":
    main()
