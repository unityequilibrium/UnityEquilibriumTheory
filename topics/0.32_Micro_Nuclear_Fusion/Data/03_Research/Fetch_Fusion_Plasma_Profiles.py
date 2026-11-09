"""
Fetch_Fusion_Plasma_Profiles.py - Topic 0.32
============================================
Prepares plasma confinement benchmarks for UET vs. ITER comparison.
Axiom 4: Semi-open Exchange. 
Plasma must exchange energy with the 'In-field' (Confinement) 
without losing it to the 'Ex-field' (Radiation/Turbulence).
"""

import json
from pathlib import Path

# --- FUSION BENCHMARKS (LAWSON CRITERION) ---
# Derived from JET 2022 (Nature) and ITER Baseline
FUSION_DATA = {
    "_meta": {
        "source": "JET Collaboration / IAEA ITER Project",
        "description": "Triple product (n * T * tau) benchmarks for Q=1 and Q=10.",
        "date_acquired": "2026-03-29"
    },
    "benchmarks": [
        {
            "id": "JET_Nature_2022",
            "name": "JET D-T Record (59 MJ)",
            "temp_kev": 10.0,
            "density_m3": 4e19,
            "confinement_time_s": 5.0,
            "q_factor": 0.33,
            "mechanism": "Magnetic Confinement (Tokamak)"
        },
        {
            "id": "ITER_Target",
            "name": "ITER Q=10 Goal",
            "temp_kev": 15.0,
            "density_m3": 1e20,
            "confinement_time_s": 400.0,
            "q_factor": 10.0,
            "mechanism": "Magnetic Confinement (Tokamak)"
        },
        {
            "id": "NIF_Ignition",
            "name": "NIF Inertial Ignition",
            "temp_kev": 5.0,
            "density_m3": 1e31,
            "confinement_time_s": 1e-10,
            "q_factor": 1.5,
            "mechanism": "Inertial Confinement (Laser)"
        }
    ]
}

def prepare_data():
    current_dir = Path(__file__).parent
    output_file = current_dir / "fusion_benchmarks.json"
    
    print(f"📥 Preparing Fusion Plasma Benchmarks at {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(FUSION_DATA, f, indent=4)
        
    print("✅ Fusion Data Ready.")

if __name__ == "__main__":
    prepare_data()
