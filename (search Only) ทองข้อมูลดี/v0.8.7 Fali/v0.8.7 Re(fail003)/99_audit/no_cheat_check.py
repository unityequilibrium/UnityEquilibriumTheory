import os
import glob
import re

# --- CONFIG ---
BASE_DIR = r"c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.8.7"
STORY_DIR = os.path.join(BASE_DIR, "research_v3", "story_mode")


def scan_file(filepath):
    filename = os.path.basename(filepath)
    print(f"\n🔍 INSPECTING: {filename}")

    # FIXED: Explicit UTF-8 for Emojis
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    has_math = False
    has_data_load = False
    suspicious_lines = []

    for i, line in enumerate(lines):
        # 1. Check for Math (polyfit, curve_fit, std)
        if "np.polyfit" in line or "curve_fit" in line or "np.std" in line:
            print(f"   ✅ MATH FOUND (Line {i+1}): {line.strip()}")
            has_math = True

        # 2. Check for Data Loading (read_csv, open)
        if "pd.read_csv" in line or "open(" in line:
            print(f"   ✅ DATA LOAD (Line {i+1}): {line.strip()}")
            has_data_load = True

        # 3. Check for Hardcoded Results (Suspicious)
        # e.g., "k = 1.0" or "beta = 2" appearing at the start of a line
        if re.match(r"\s*[k|beta|gamma]\s*=\s*\d+\.?\d*", line):
            # Allow if it's inside a comment or print, but flag assignment
            if "if" not in line and "print" not in line:
                suspicious_lines.append((i + 1, line.strip()))

    if has_math and has_data_load:
        print("   ✅ VERDICT: SCRIPT IS CALCULATING, NOT FAKING.")
    else:
        print("   ⚠️ VERDICT: SCRIPT MIGHT BE SIMULATING OR INCOMPLETE.")

    if suspicious_lines:
        print("   ⚠️ CAUTION: Check these lines for hardcoding:")
        for ln, txt in suspicious_lines:
            print(f"      [L{ln}] {txt}")


def main():
    print("#######################################################")
    print("      👮 ANTI-CHEAT INSPECTOR (CODE AUDIT)")
    print("#######################################################")
    print("Scanning Story Mode Scripts for Hardcoded Values...")

    scripts = glob.glob(os.path.join(STORY_DIR, "*.py"))
    for script in scripts:
        if "finale" in script:
            continue
        scan_file(script)

    print("\n#######################################################")
    print("AUDIT COMPLETE.")


if __name__ == "__main__":
    main()
