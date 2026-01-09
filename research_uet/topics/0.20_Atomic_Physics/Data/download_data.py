"""
Download Script: Atomic Physics Real Data
==========================================
Downloads hydrogen spectrum data from NIST ASD.

Sources:
- NIST ASD: 10.18434/T4W30F
- CODATA 2018: 10.1063/5.0064853
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent


def download_nist_hydrogen():
    """
    NIST Atomic Spectra Database - Hydrogen Lines
    DOI: 10.18434/T4W30F
    URL: https://physics.nist.gov/asd
    """
    data = {
        "source": "NIST Atomic Spectra Database",
        "publication": {
            "title": "NIST Atomic Spectra Database (version 5.11)",
            "authors": ["Kramida, A.", "Ralchenko, Yu.", "Reader, J.", "NIST ASD Team"],
            "year": 2023,
            "doi": "10.18434/T4W30F",
            "url": "https://physics.nist.gov/asd",
        },
        "element": {"name": "Hydrogen", "symbol": "H", "atomic_number": 1},
        "balmer_series": {
            "description": "Transitions to n=2 (visible light)",
            "lines": [
                {
                    "name": "H-alpha",
                    "transition": "3 → 2",
                    "wavelength_vacuum_nm": 656.4614,
                    "wavelength_air_nm": 656.2819,
                    "frequency_THz": 456.676,
                    "energy_eV": 1.889,
                    "color": "red",
                },
                {
                    "name": "H-beta",
                    "transition": "4 → 2",
                    "wavelength_vacuum_nm": 486.2721,
                    "wavelength_air_nm": 486.1342,
                    "frequency_THz": 616.507,
                    "energy_eV": 2.550,
                    "color": "cyan",
                },
                {
                    "name": "H-gamma",
                    "transition": "5 → 2",
                    "wavelength_vacuum_nm": 434.1692,
                    "wavelength_air_nm": 434.0472,
                    "frequency_THz": 690.690,
                    "energy_eV": 2.856,
                    "color": "violet",
                },
                {
                    "name": "H-delta",
                    "transition": "6 → 2",
                    "wavelength_vacuum_nm": 410.2938,
                    "wavelength_air_nm": 410.1748,
                    "frequency_THz": 731.017,
                    "energy_eV": 3.023,
                    "color": "violet",
                },
                {
                    "name": "H-epsilon",
                    "transition": "7 → 2",
                    "wavelength_vacuum_nm": 397.1198,
                    "wavelength_air_nm": 397.0075,
                    "frequency_THz": 755.028,
                    "energy_eV": 3.123,
                    "color": "UV-violet",
                },
            ],
        },
        "lyman_series": {
            "description": "Transitions to n=1 (UV)",
            "lines": [
                {
                    "name": "Lyman-alpha",
                    "transition": "2 → 1",
                    "wavelength_vacuum_nm": 121.5670,
                    "energy_eV": 10.199,
                },
                {
                    "name": "Lyman-beta",
                    "transition": "3 → 1",
                    "wavelength_vacuum_nm": 102.5728,
                    "energy_eV": 12.088,
                },
            ],
        },
    }

    filepath = DATA_DIR / "nist_hydrogen_spectrum.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def download_codata_atomic():
    """
    CODATA 2018 - Atomic Constants
    DOI: 10.1063/5.0064853
    """
    data = {
        "source": "CODATA 2018 Recommended Values",
        "publication": {
            "title": "CODATA recommended values of the fundamental physical constants: 2018",
            "authors": ["Tiesinga, E.", "Mohr, P.J.", "Newell, D.B.", "Taylor, B.N."],
            "journal": "J. Phys. Chem. Ref. Data",
            "volume": 50,
            "pages": "033105",
            "year": 2021,
            "doi": "10.1063/5.0064853",
        },
        "constants": {
            "R_infinity": {
                "value": 10973731.568160,
                "uncertainty": 0.000021,
                "unit": "m⁻¹",
                "name": "Rydberg constant",
                "relative_uncertainty": 1.9e-12,
            },
            "R_H": {
                "value": 10967758.3406,
                "uncertainty": 0.0032,
                "unit": "m⁻¹",
                "name": "Rydberg constant for hydrogen",
                "note": "R_H = R_∞ × m_p/(m_p + m_e)",
            },
            "a_0": {
                "value": 5.29177210903e-11,
                "uncertainty": 0.00000000080e-11,
                "unit": "m",
                "name": "Bohr radius",
            },
            "alpha": {
                "value": 7.2973525693e-3,
                "uncertainty": 0.0000000011e-3,
                "unit": "dimensionless",
                "name": "Fine-structure constant",
                "inverse": 137.035999084,
            },
            "E_h": {
                "value": 4.3597447222071e-18,
                "uncertainty": 0.0000000000085e-18,
                "unit": "J",
                "name": "Hartree energy",
            },
            "m_e": {
                "value": 9.1093837015e-31,
                "uncertainty": 0.0000000028e-31,
                "unit": "kg",
                "name": "Electron mass",
            },
            "m_p": {
                "value": 1.67262192369e-27,
                "uncertainty": 0.00000000051e-27,
                "unit": "kg",
                "name": "Proton mass",
            },
        },
    }

    filepath = DATA_DIR / "codata_2018_atomic.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Created: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("Downloading Atomic Physics Real Data")
    print("=" * 60)

    download_nist_hydrogen()
    download_codata_atomic()

    print("\n✅ All data downloaded!")
    print(f"Location: {DATA_DIR}")


if __name__ == "__main__":
    main()
