"""
UET Figure Coverage Auditor
===========================
Analyzes the "Visual Gap" between Research Code and Generated Results.

User Input: "We ran ~260 tests, but only got 94 images. Why?"

Objective:
1. Identify all `Research_*.py` scripts (The "Intention").
2. Detect if they adhere to the Visualization Standard (contain `plt.savefig`).
3. Count actual PNGs in `Result/`.
4. Report "Silent scripts" that claim to research but show nothing.
"""

# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP

import sys
from pathlib import Path
import re

# Setup paths
current_file = Path(__file__).resolve()
# audit_figure_coverage.py -> Audit/ -> scripts/ -> docs/
RESEARCH_UET_DIR = _UET_REPO_ROOT / "docs"
TOPICS_DIR = RESEARCH_UET_DIR / "topics"


def audit_coverage():
    print("==================================================")
    print("🔍 UET VISUAL COVERAGE AUDIT")
    print("==================================================")
    print(f"Scanning: {TOPICS_DIR}\n")

    total_scripts = 0
    plotting_scripts = 0
    total_images = 0
    silent_scripts = []

    # Prepare Table Rows
    rows = []

    for topic in sorted(TOPICS_DIR.iterdir()):
        if not topic.is_dir() or not topic.name[0].isdigit():
            continue

        # Paths
        code_dir = topic / "Code" / "03_Research"
        result_dir = topic / "Result"

        # 1. Count Images
        images = list(result_dir.glob("*.png")) if result_dir.exists() else []
        image_count = len(images)
        total_images += image_count

        # 2. Analyze Scripts
        scripts = list(code_dir.glob("Research_*.py")) if code_dir.exists() else []

        topic_plotting_potential = 0
        topic_silent = []

        for script in scripts:
            total_scripts += 1
            try:
                content = script.read_text(encoding="utf-8")
                # Simple heuristic: Does it import matplotlib or savefig?
                if "matplotlib" in content or "plt.savefig" in content:
                    plotting_scripts += 1
                    topic_plotting_potential += 1

                    # Heuristic check: Did this topic produce *any* images?
                    # Ideally we match script name to image, but UET naming isn't perfectly 1:1 yet.
                    if image_count == 0:
                        topic_silent.append(script.name)
            except:
                pass

        if topic_silent:
            silent_scripts.extend([f"{topic.name}/{s}" for s in topic_silent])

        # Add Row
        rows.append(
            f"| {topic.name:<35} | {len(scripts):<7} | {topic_plotting_potential:<10} | {image_count:<7} |"
        )

    # Print Report
    print(f"| {'TOPIC':<35} |cripts | Potential | Images |")
    print(f"|{'-'*37}|{'-'*9}|{'-'*12}|{'-'*9}|")
    for row in rows:
        print(row)
    print(f"|{'-'*69}|")

    print("\n📊 SUMMARY STATS")
    print(f"  - Total Research Scripts:      {total_scripts}")
    print(
        f"  - Scripts with Plot Logic:     {plotting_scripts} ({plotting_scripts/total_scripts*100:.1f}%)"
    )
    print(f"  - Total Images Found:          {total_images}")
    print(
        f"  - Images per Plot-Script:      {total_images/plotting_scripts if plotting_scripts else 0:.2f}"
    )

    print("\n🔇 SILENT SCRIPT ALERT (Scripts with `plt` but NO images in Topic Result)")
    if silent_scripts:
        for s in silent_scripts:
            print(f"  [!] {s}")
    else:
        print("  (None - All plotting topics have at least one image)")

    print("\n--------------------------------------------------")
    print("💡 INSIGHT:")
    if total_images < total_scripts:
        print(
            f"You have {total_scripts} research scripts, but only {plotting_scripts} are designed to output images."
        )
        print(
            f"The discrepancy ({total_scripts - plotting_scripts} scripts) is because many scripts are pure numerical/text validators."
        )
        print("This is normal, but check the 'Silent Script' list above for broken visualizations.")
    print("==================================================")


if __name__ == "__main__":
    audit_coverage()
