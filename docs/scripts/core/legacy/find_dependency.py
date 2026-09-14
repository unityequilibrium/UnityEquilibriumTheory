import zipfile
import os

zip_dir = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\(search Only) ทองข้อมูลดี\v0.9.0+"
)
target_file = "w_mass_anomaly_data.py"
files = ["lab 02.01.2026.zip", "03.01.2026.zip", "04.01.2026.zip"]

print(f"Searching for {target_file} in archives...\n")

found = False
for f in files:
    path = os.path.join(zip_dir, f)
    if not os.path.exists(path):
        continue

    try:
        with zipfile.ZipFile(path, "r") as z:
            for name in z.namelist():
                if target_file in name:
                    print(f"FOUND in {f}: {name}")
                    found = True
    except Exception as e:
        print(f"Error reading {f}: {e}")

if not found:
    print("File not found in inspected archives.")
