import os
import subprocess
import glob
from pathlib import Path


def run_integrity_audit():
    print("=" * 80)
    print("      UET GLOBAL INTEGRITY AUDIT (THE DARK SWEEP)      ")
    print("      Goal: Detect Shadow Math by Killing Engines      ")
    print("=" * 80)

    # 1. Collect all Research scripts
    root_dir = Path.cwd()
    research_scripts = glob.glob("docs/topics/*/Code/03_Research/Research_*.py")
    proof_scripts = glob.glob("docs/topics/*/Code/02_Proof/Proof_*.py")

    all_targets = research_scripts + proof_scripts
    all_targets = [t for t in all_targets if not t.endswith("__init__.py")]
    all_targets.sort()

    print(f"Found {len(all_targets)} inspection targets.")

    survivors = []
    failed_as_expected = []
    crashed = []

    # Set Environment Variable for the subprocess
    env = os.environ.copy()
    env["UET_KILL_ENGINE"] = "TRUE"

    for script in all_targets:
        print(f"\n🔍 Inspecting: {script} ...", end="", flush=True)

        try:
            # Run the script with the Kill Switch active
            result = subprocess.run(
                ["python", script], capture_output=True, text=True, env=env, timeout=30
            )

            # We looking for "PASS" or "Success" in the output
            output = result.stdout.upper() + result.stderr.upper()

            if (
                "PASS" in output
                or "SUCCESS" in output
                or "ERROR IN TENSION:      0.0%" in output
            ):
                # This script survived the Engine Kill! -> SHADOW MATH DETECTED
                print(" ❌ SHADOW MATH DETECTED (Survived Engine Kill!)")
                survivors.append(script)
            elif (
                "nan" in output.lower()
                or "fail" in output.lower()
                or result.returncode != 0
            ):
                print(" ✅ INTEGRITY OK (Engine Dependent)")
                failed_as_expected.append(script)
            else:
                # Ambiguous
                print(" ⚠️ Result Ambiguous (Please check manually)")

        except subprocess.TimeoutExpired:
            print(" ⏳ TIMEOUT")
            crashed.append(script)
        except Exception as e:
            print(f" 💣 CRASHED: {e}")
            crashed.append(script)

    print("\n" + "=" * 80)
    print("AUDIT RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Targets: {len(all_targets)}")
    print(f"Total Survivors (SHADOW MATH): {len(survivors)}")
    print(f"Total Integrity OK:            {len(failed_as_expected)}")
    print(f"Total Crashed/Timeout:         {len(crashed)}")

    if survivors:
        print(
            "\n🚨 CRITICAL: The following scripts contain Shadow Math and must be refactored:"
        )
        for s in survivors:
            print(f"  - {s}")
    else:
        print(
            "\n✨ UNBELIEVABLE: No survivors found. High architectural integrity (for these targets)."
        )

    # Save the report
    with open("INTEGRITY_AUDIT_REPORT.md", "w", encoding="utf-8") as f:
        f.write("# UET Global Integrity Audit Report\n\n")
        f.write(f"**Status**: Audit Completed\n")
        f.write(f"**Kill Switch**: ENABLED (UET_KILL_ENGINE=TRUE)\n\n")
        f.write("## 🚨 Shadow Math Survivors (MUST FIX)\n")
        if survivors:
            for s in survivors:
                f.write(f"- [ ] {s}\n")
        else:
            f.write("None found.\n")
        f.write("\n## ✅ Integrity Verified (Safe)\n")
        for s in failed_as_expected:
            f.write(f"- [x] {s}\n")

    print(f"\n📄 Full Report saved to: {root_dir}/INTEGRITY_AUDIT_REPORT.md")


if __name__ == "__main__":
    run_integrity_audit()
