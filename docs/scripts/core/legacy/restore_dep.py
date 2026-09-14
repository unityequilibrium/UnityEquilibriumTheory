import zipfile
import os
import shutil

zip_path = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\(search Only) ทองข้อมูลดี\v0.9.0+\04.01.2026.zip"
restore_dir = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\docs\topics\0.6_Electroweak_Physics\Code\experiments"
target_internal = "04.01.2026/data/01_particle_physics/w_mass_anomaly_data.py"
target_name = "w_mass_anomaly_data.py"

print(f"Restoring {target_name} to {restore_dir}...")

try:
    with zipfile.ZipFile(zip_path, "r") as z:
        source = z.open(target_internal)
        target_path = os.path.join(restore_dir, target_name)
        with open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)
        print("Success.")
except Exception as e:
    print(f"Error: {e}")
