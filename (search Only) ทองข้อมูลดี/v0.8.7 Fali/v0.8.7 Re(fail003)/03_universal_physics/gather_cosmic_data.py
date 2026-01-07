import os
import shutil
import glob

# --- CONFIG ---
SOURCE_ROOT = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research"
DEST_DIR = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\03_universal_physics\data"
)
os.makedirs(DEST_DIR, exist_ok=True)

# Keyword map to find specific files in the deep nest
TARGETS = {
    "gw150914_strain.csv": "Gravitational_Waves",
    "beta_decay.csv": "Weak_Force_Beta",
    "particle_masses.csv": "Particle_Mass_Spectrum",
    "planck_2018.csv": "CMB_Power_Spectrum",
    "black_hole_sample.csv": "Black_Hole_Sample",
    "orbital_data.csv": "Orbital_Mechanics",
    "climate_data.csv": "Thermodynamics_Climate",
    "qcd_potential.csv": "Strong_Force_QCD",
    "coulomb_data.csv": "Electromagnetism",
}


def gather_data():
    print(f"--- GATHERING COSMIC DATA ---")
    found_count = 0

    # Brute force walk to find files matching targets
    for root, dirs, files in os.walk(SOURCE_ROOT):
        for file in files:
            if file in TARGETS:
                src_path = os.path.join(root, file)
                new_name = TARGETS[file] + ".csv"
                dst_path = os.path.join(DEST_DIR, new_name)

                print(f"Found {file} -> {new_name}")
                shutil.copy2(src_path, dst_path)
                found_count += 1

    print(f"--- GATHER COMPLETED. Found {found_count}/{len(TARGETS)} datasets ---")


if __name__ == "__main__":
    gather_data()
