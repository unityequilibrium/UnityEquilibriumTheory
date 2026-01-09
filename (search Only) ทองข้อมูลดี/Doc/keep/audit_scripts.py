"""
Audit all test scripts for:
1. Real data usage (vs synthetic)
2. New equation version usage
"""

import os
from pathlib import Path

LAB_DIR = Path(__file__).parent / "lab"

# Keywords that indicate real data
REAL_DATA_KEYWORDS = [
    "SPARC",
    "PDG",
    "CODATA",
    "LIGO",
    "EHT",
    "Planck",
    "Berut",
    "Lamoreaux",
    "Mohideen",
    "Hensen",
    "Aspect",
    "experimental",
    "measured",
    "observed",
]

# Keywords that indicate synthetic data
SYNTHETIC_KEYWORDS = ["synthetic", "generated", "random", "simulated", "mock"]

# Keywords for new equation
NEW_EQUATION_KEYWORDS = [
    "omega_functional_complete",
    "strategic_boost",
    "natural_will",
    "semi_open_exchange",
    "layer_coherence",
]


def check_file(filepath: Path) -> dict:
    """Check a single file for data and equation usage."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except:
        return {"error": "Could not read file"}

    result = {
        "real_data": [],
        "synthetic_data": [],
        "new_equation": [],
        "uses_real": False,
        "uses_new_eq": False,
    }

    for kw in REAL_DATA_KEYWORDS:
        if kw.lower() in content.lower():
            result["real_data"].append(kw)
            result["uses_real"] = True

    for kw in SYNTHETIC_KEYWORDS:
        if kw.lower() in content.lower():
            result["synthetic_data"].append(kw)

    for kw in NEW_EQUATION_KEYWORDS:
        if kw in content:
            result["new_equation"].append(kw)
            result["uses_new_eq"] = True

    return result


def audit_directory(dir_path: Path, depth: int = 0) -> dict:
    """Audit all Python files in a directory."""
    results = {}

    for item in sorted(dir_path.iterdir()):
        if item.name.startswith("_") or item.name.startswith("."):
            continue

        if item.is_dir():
            sub_results = audit_directory(item, depth + 1)
            results.update(sub_results)
        elif item.suffix == ".py":
            rel_path = item.relative_to(LAB_DIR.parent)
            results[str(rel_path)] = check_file(item)

    return results


def main():
    print("=" * 70)
    print("UET SCRIPT AUDIT - Real Data & Equation Version Check")
    print("=" * 70)

    if not LAB_DIR.exists():
        print(f"ERROR: Lab directory not found: {LAB_DIR}")
        return

    results = audit_directory(LAB_DIR)

    # Categorize
    real_data_scripts = []
    synthetic_scripts = []
    new_eq_scripts = []
    old_eq_scripts = []

    for path, info in results.items():
        if "error" in info:
            continue

        if info["uses_real"]:
            real_data_scripts.append((path, info["real_data"]))
        else:
            synthetic_scripts.append(path)

        if info["uses_new_eq"]:
            new_eq_scripts.append((path, info["new_equation"]))
        else:
            old_eq_scripts.append(path)

    # Print summary
    print(f"\nTotal Python files: {len(results)}")

    print(f"\n{'=' * 70}")
    print("REAL DATA USAGE")
    print("=" * 70)
    print(f"✅ Uses real data: {len(real_data_scripts)}")
    for path, keywords in real_data_scripts[:10]:
        print(f"   {path}: {keywords[:3]}")
    if len(real_data_scripts) > 10:
        print(f"   ... and {len(real_data_scripts) - 10} more")

    print(f"\n⚠️ May use synthetic: {len(synthetic_scripts)}")
    for path in synthetic_scripts[:5]:
        print(f"   {path}")
    if len(synthetic_scripts) > 5:
        print(f"   ... and {len(synthetic_scripts) - 5} more")

    print(f"\n{'=' * 70}")
    print("EQUATION VERSION")
    print("=" * 70)
    print(f"✅ Uses NEW equation (V3.0): {len(new_eq_scripts)}")
    for path, keywords in new_eq_scripts[:5]:
        print(f"   {path}: {keywords[:2]}")

    print(f"\n⚠️ Uses OLD equation: {len(old_eq_scripts)}")
    print("   (These need updating to use omega_functional_complete)")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    real_pct = len(real_data_scripts) / len(results) * 100 if results else 0
    new_pct = len(new_eq_scripts) / len(results) * 100 if results else 0
    print(f"Real data coverage: {real_pct:.1f}%")
    print(f"New equation coverage: {new_pct:.1f}%")

    if real_pct < 50:
        print("\n⚠️ MANY SCRIPTS MAY USE SYNTHETIC DATA - REVIEW NEEDED")
    if new_pct < 10:
        print("\n⚠️ MOST SCRIPTS USE OLD EQUATION - UPDATE NEEDED")


if __name__ == "__main__":
    main()
