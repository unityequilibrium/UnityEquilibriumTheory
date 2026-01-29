import os
import shutil
from pathlib import Path

# Configuration
SOURCE_ROOT = Path(r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_uet\topics")
DEST_DIR = Path(r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_uet\paper\Figures")

# Ensure destination exists
DEST_DIR.mkdir(parents=True, exist_ok=True)

print(f"🌾 Harvesting figures from: {SOURCE_ROOT}")
print(f"📦 Depositing into: {DEST_DIR}")

count = 0

# Walk through all directories
for root, dirs, files in os.walk(SOURCE_ROOT):
    for file in files:
        if file.lower().endswith(".png"):
            source_path = Path(root) / file

            # Identify Topic from path (e.g., "0.7_Neutrino_Physics")
            topic_folder = None
            for part in source_path.parts:
                if part[0].isdigit() and "_" in part:  # Simple heuristic for "0.X_Name"
                    topic_folder = part
                    break

            # Map Topic to Chapter
            target_subfolder = "Unsorted"
            if topic_folder:
                prefix = topic_folder.split("_")[0]  # "0.7"

                # MAPPING TABLE
                if prefix == "0.0":
                    target_subfolder = "Ch02_MasterEq"
                elif prefix == "0.19":
                    target_subfolder = "Ch04_Gravity"
                elif prefix == "0.1":
                    target_subfolder = "Ch05_Galactic"
                elif prefix == "0.3":
                    target_subfolder = "Ch06_Cosmology"
                elif prefix == "0.15":
                    target_subfolder = "Ch07_Clusters"
                elif prefix == "0.2":
                    target_subfolder = "Ch08_BlackHoles"
                elif prefix == "0.9":
                    target_subfolder = "Ch09_Quantum"
                elif prefix == "0.17":
                    target_subfolder = "Ch10_MassGen"
                elif prefix in ["0.6"]:
                    target_subfolder = "Ch10_StandardModel"
                elif prefix in ["0.20", "0.5", "0.16"]:
                    target_subfolder = "Ch11_Nuclear"
                elif prefix == "0.7":
                    target_subfolder = "Ch12_Neutrinos"
                elif prefix in ["0.8", "0.12"]:
                    target_subfolder = "Ch13_Precision"
                elif prefix == "0.4":
                    target_subfolder = "Ch14_NewPhysics"
                elif prefix == "0.18":
                    target_subfolder = "Ch15_Primes"
                elif prefix == "0.21":
                    target_subfolder = "Ch16_Topology"
                elif prefix == "0.13":
                    target_subfolder = "Ch17_Thermo"
                elif prefix == "0.14":
                    target_subfolder = "Ch06_Complex"  # Keep legacy
                elif prefix == "0.22":
                    target_subfolder = "Ch18_Life"
                elif prefix == "0.24":
                    target_subfolder = "Ch19_AI"
                elif prefix == "0.25":
                    target_subfolder = "Ch20_Econ"
                elif prefix == "0.26":
                    target_subfolder = "Ch21_Social"
                elif prefix == "0.23":
                    target_subfolder = "Ch22_Scale"

            # Create subfolder
            final_dest_dir = DEST_DIR / target_subfolder
            final_dest_dir.mkdir(exist_ok=True)

            # Copy
            dest_path = final_dest_dir / file
            try:
                shutil.copy2(source_path, dest_path)
                print(f"  [+] {topic_folder} -> {target_subfolder}/{file}")
                count += 1
            except Exception as e:
                print(f"  [!] Failed {file}: {e}")

print(f"✅ Harvest Complete. {count} figures collected and sorted.")
