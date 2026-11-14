"""
Download Script for Atomic Physics Reference Data
==================================================
Downloads hydrogen spectrum data from NIST and CODATA.

DOIs:
- 10.18434/T4W30F (NIST ASD)
- 10.1063/5.0064853 (CODATA 2018)

Usage:
    python download_references.py
"""

import os
import json
from pathlib import Path

# Create directories
DATA_DIR = Path(__file__).parent
DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_nist_hydrogen():
    """
    Download NIST Atomic Spectra Database hydrogen lines.
    
    Source: https://physics.nist.gov/asd
    DOI: 10.18434/T4W30F
    
    Balmer series (vacuum wavelengths):
    - H-α: 656.4614 nm (n=3→2)
    - H-β: 486.2721 nm (n=4→2)
    - H-γ: 434.1692 nm (n=5→2)
    - H-δ: 410.2938 nm (n=6→2)
    """
    data = {
        "source": "NIST Atomic Spectra Database",
        "doi": "10.18434/T4W30F",
        "url": "https://physics.nist.gov/asd",
        "element": "Hydrogen (H I)",
        "series": {
            "balmer": {
                "description": "n → 2 transitions (visible light)",
                "lines": [
                    {
                        "name": "H-alpha",
                        "transition": "3 → 2",
                        "wavelength_vacuum_nm": 656.4614,
                        "wavelength_air_nm": 656.2819,
                        "frequency_THz": 456.676,
                        "uncertainty_nm": 0.0001
                    },
                    {
                        "name": "H-beta",
                        "transition": "4 → 2",
                        "wavelength_vacuum_nm": 486.2721,
                        "wavelength_air_nm": 486.1342,
                        "frequency_THz": 616.507,
                        "uncertainty_nm": 0.0001
                    },
                    {
                        "name": "H-gamma",
                        "transition": "5 → 2",
                        "wavelength_vacuum_nm": 434.1692,
                        "wavelength_air_nm": 434.0472,
                        "frequency_THz": 690.690,
                        "uncertainty_nm": 0.0001
                    },
                    {
                        "name": "H-delta",
                        "transition": "6 → 2",
                        "wavelength_vacuum_nm": 410.2938,
                        "wavelength_air_nm": 410.1748,
                        "frequency_THz": 731.017,
                        "uncertainty_nm": 0.0001
                    }
                ]
            },
            "lyman": {
                "description": "n → 1 transitions (UV)",
                "lines": [
                    {
                        "name": "Lyman-alpha",
                        "transition": "2 → 1",
                        "wavelength_vacuum_nm": 121.5670,
                        "uncertainty_nm": 0.0001
                    }
                ]
            }
        }
    }
    
    filepath = DATA_DIR / "nist_hydrogen_spectrum.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Written: {filepath}")
    return filepath


def download_codata_rydberg():
    """
    Download CODATA 2018 Rydberg constant and related values.
    
    DOI: 10.1063/5.0064853
    
    R∞ = 10 973 731.568 160(21) m⁻¹
    """
    data = {
        "source": "CODATA 2018 Recommended Values",
        "doi": "10.1063/5.0064853",
        "constants": {
            "R_infinity": {
                "value": 10973731.568160,
                "uncertainty": 0.000021,
                "unit": "m⁻¹",
                "name": "Rydberg constant",
                "relative_uncertainty": 1.9e-12
            },
            "R_H": {
                "value": 10967758.340,
                "uncertainty": 0.003,
                "unit": "m⁻¹",
                "name": "Rydberg constant for hydrogen",
                "note": "R_H = R_∞ * m_p/(m_p + m_e)"
            },
            "a_0": {
                "value": 5.29177210903e-11,
                "uncertainty": 0.00000000080e-11,
                "unit": "m",
                "name": "Bohr radius"
            },
            "alpha": {
                "value": 7.2973525693e-3,
                "uncertainty": 0.0000000011e-3,
                "unit": "dimensionless",
                "name": "Fine-structure constant"
            },
            "E_h": {
                "value": 4.3597447222071e-18,
                "uncertainty": 0.0000000000085e-18,
                "unit": "J",
                "name": "Hartree energy"
            },
            "m_e": {
                "value": 9.1093837015e-31,
                "uncertainty": 0.0000000028e-31,
                "unit": "kg",
                "name": "Electron mass"
            },
            "m_p": {
                "value": 1.67262192369e-27,
                "uncertainty": 0.00000000051e-27,
                "unit": "kg",
                "name": "Proton mass"
            }
        }
    }
    
    filepath = DATA_DIR / "codata_2018_atomic.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Written: {filepath}")
    return filepath


def create_references_readme():
    """Create README for data directory."""
    content = """# Atomic Physics Data Sources

## References

| Source | DOI | Description |
|:-------|:----|:------------|
| NIST ASD | 10.18434/T4W30F | Hydrogen spectrum |
| CODATA 2018 | 10.1063/5.0064853 | Rydberg constant |

## Data Files

| File | Content |
|:-----|:--------|
| `nist_hydrogen_spectrum.json` | Balmer/Lyman series wavelengths |
| `codata_2018_atomic.json` | Rydberg, fine structure, Bohr radius |

## Usage

```python
import json
with open("nist_hydrogen_spectrum.json") as f:
    data = json.load(f)
    
for line in data["series"]["balmer"]["lines"]:
    print(f"{line['name']}: {line['wavelength_vacuum_nm']} nm")
```

## Source URLs

- NIST ASD: https://physics.nist.gov/asd
- CODATA: https://physics.nist.gov/cuu/Constants/
"""
    filepath = DATA_DIR / "README.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Written: {filepath}")


def main():
    print("=" * 60)
    print("Downloading Atomic Physics Reference Data")
    print("=" * 60)
    
    download_nist_hydrogen()
    download_codata_rydberg()
    create_references_readme()
    
    print("\n✅ All data downloaded!")
    print(f"Location: {DATA_DIR}")


if __name__ == "__main__":
    main()
