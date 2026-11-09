import json
import os
from pathlib import Path
from datetime import datetime

def generate_fusion_data():
    """
    Generates standard approximated data for fusion cross sections
    and Coulomb barriers based on standard physics references.
    """
    # Create the correct path based on UET standards (mirroring Code/03_Research)
    data_dir = Path(__file__).parent.parent.parent / "Data" / "03_Research"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = data_dir / "fusion_cross_sections.json"
    
    # Real-world approximate data (peak cross section and rough Coulomb barrier)
    # References: IAEA Nuclear Data Section / ENDF (Evaluated Nuclear Data File)
    data = {
        "_meta": {
            "source": "Approximations based on ENDF/B-VIII.0 and IAEA standard fusion data",
            "description": "Baseline fusion cross sections and Coulomb barriers for comparison with UET modifications.",
            "date_generated": datetime.now().strftime("%Y-%m-%d"),
            "units": {
                "barrier": "eV (electron-volts)",
                "peak_cross_section": "barns (1e-28 m^2)",
                "energy_released": "eV (electron-volts)"
            }
        },
        "reactions": {
            "D-T": {
                "name": "Deuterium-Tritium",
                "barrier_ev": 100000, 
                "peak_cross_section_barns": 5.0,
                "energy_released_ev": 17.6e6,
                "neutronic": True
            },
            "D-D": {
                "name": "Deuterium-Deuterium",
                "barrier_ev": 400000,
                "peak_cross_section_barns": 0.1,
                "energy_released_ev": 3.65e6,
                "neutronic": True
            },
            "p-B11": {
                "name": "Proton-Boron-11",
                "barrier_ev": 600000,
                "peak_cross_section_barns": 1.2,
                "energy_released_ev": 8.7e6,
                "neutronic": False
            }
        }
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print(f"Data successfully generated at: {file_path}")

if __name__ == "__main__":
    generate_fusion_data()
