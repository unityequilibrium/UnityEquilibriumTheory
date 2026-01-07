import os
import shutil

# --- CONFIG ---
SOURCE_ROOT = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research"
# Consolidated into Universal Physics Folder for the Grand Unified Test
DEST_DIR = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_v3\03_universal_physics\data"
)

TARGETS = {
    "hrv_stress.csv": "Biology_HRV",
    "social_polarization.csv": "Sociology_Polarization",
    "karate_club.txt": "Network_Karate",
    "email_enron.txt": "Network_Enron",
    "ca_hepth.txt": "Network_Citation",
    "facebook_combined.txt": "Network_Social_FB",
}


def gather_complex_systems():
    print("--- GATHERING COMPLEX SYSTEMS DATA ---")
    found_count = 0

    for root, dirs, files in os.walk(SOURCE_ROOT):
        for file in files:
            if file in TARGETS:
                src = os.path.join(root, file)
                dst = os.path.join(DEST_DIR, TARGETS[file] + os.path.splitext(file)[1])
                print(f"Found {file} -> {os.path.basename(dst)}")
                shutil.copy2(src, dst)
                found_count += 1

    print(f"--- FOUND {found_count}/{len(TARGETS)} DATASETS ---")


if __name__ == "__main__":
    gather_complex_systems()
