import shutil
import os
from pathlib import Path

# Source with non-ASCII characters
SOURCE_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\(search Only) ทองข้อมูลดี\Fali\Re(fail003)\03_universal_physics\data"

# Destination in active lab
DEST_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7\research_uet\data\03_universal"


def port_data():
    print(f"Copying from: {SOURCE_DIR}")
    print(f"To: {DEST_DIR}")

    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)

    try:
        shutil.copytree(SOURCE_DIR, DEST_DIR)
        print("✅ Data transfer complete.")
        # List files to verify
        print("Files:")
        for f in os.listdir(DEST_DIR):
            print(f" - {f}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    port_data()
