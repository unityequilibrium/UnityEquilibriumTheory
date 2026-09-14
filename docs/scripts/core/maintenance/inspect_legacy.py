import zipfile
import os
from pathlib import Path

TARGET_DIR = (
    r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0\(search Only) ทองข้อมูลดี\v0.9.0+"
)
ZIPS = ["02.01.2026.zip", "03.01.2026.zip", "lab 02.01.2026.zip"]


def analyze_zip(zip_name):
    zip_path = os.path.join(TARGET_DIR, zip_name)
    print(f"\n📦 Analyzing: {zip_name}")
    print("=" * 50)

    if not os.path.exists(zip_path):
        print(f"❌ File not found: {zip_path}")
        return

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            file_list = z.namelist()
            print(f"Total Files: {len(file_list)}")

            # Analyze Structure
            dirs = set()
            py_files = 0
            md_files = 0

            print("\n📂 Top Level Structure:")
            for f in file_list:
                parts = f.split("/")
                if len(parts) > 1:
                    dirs.add(parts[0])

                if f.endswith(".py"):
                    py_files += 1
                if f.endswith(".md"):
                    md_files += 1

            for d in sorted(list(dirs))[:10]:  # First 10 dirs
                print(f"  - {d}/")
            if len(dirs) > 10:
                print("  ... (and more)")

            print(f"\n📄 Stats: {py_files} Python files, {md_files} Markdown files.")

            # Look for "Lost Knowledge" keywords
            keywords = [
                "solution",
                "galaxy",
                "solver",
                "analysis",
                "dark",
                "matter",
                "result",
            ]
            print("\n🔍 Interesting Files (Sample):")
            count = 0
            for f in file_list:
                lower = f.lower()
                if any(k in lower for k in keywords) and not lower.endswith("/"):
                    print(f"  - {f}")
                    count += 1
                    if count >= 10:
                        break

    except Exception as e:
        print(f"❌ Error reading zip: {e}")


if __name__ == "__main__":
    for z in ZIPS:
        analyze_zip(z)
