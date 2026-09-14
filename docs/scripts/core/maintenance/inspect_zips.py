import zipfile
import os
from pathlib import Path


def list_zip_contents(zip_path, keywords=None):
    print(f"Inspecting: {zip_path}")
    if not os.path.exists(zip_path):
        print(f"  [ERROR] File not found: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            files = zf.namelist()
            print(f"  Total files: {len(files)}")

            found_any = False
            for f in files:
                # If keywords provided, only show matches
                if keywords:
                    if any(k.lower() in f.lower() for k in keywords):
                        # Show size to guess if it's raw data
                        info = zf.getinfo(f)
                        print(f"  [FOUND] {f} ({info.file_size} bytes)")
                        found_any = True
                else:
                    # If no keywords, just list first 10 for sanity
                    pass

            if keywords and not found_any:
                print("  [INFO] No matching files found.")

    except zipfile.BadZipFile:
        print("  [ERROR] Bad or corrupted zip file.")
    except Exception as e:
        print(f"  [ERROR] {e}")
    print("-" * 50)


base_path_1 = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\(search Only) ทองข้อมูลดี\v0.9.0+"
)
zip_1 = os.path.join(base_path_1, "(03.01.2026)uet_foundation_v0.9.0.zip")

base_path_2 = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\(search Only) ทองข้อมูลดี\v0.9.0 Fali"
zip_2 = os.path.join(base_path_2, "v0.9.0 Re(fail001).zip")
zip_3 = os.path.join(base_path_2, "v0.9.0 Re(fail002).zip")
zip_4 = os.path.join(base_path_2, "v0.9.0 Re(fail003).zip")

keywords = [
    "planck",
    "cmb",
    "power",
    "spectrum",
    "hubble",
    "tension",
    "data.txt",
    ".dat",
    ".csv",
]

list_zip_contents(zip_1, keywords)
list_zip_contents(zip_2, keywords)
list_zip_contents(zip_3, keywords)
list_zip_contents(zip_4, keywords)
