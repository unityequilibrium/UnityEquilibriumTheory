"""
UET Paper Figure Collector
==========================
Harvests validation plots from all Research Topics and consolidates them
into the `paper/Figures` directory for publication (LaTeX).

Logic:
- Scans `topics/*/Result/*.png`
- Copies files to `docs/paper/Figures`
- Renames them to `Fig_{Topic}_{Name}.png`
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

import shutil
from pathlib import Path
import os

# scripts/Reporting -> scripts -> docs
current_file = Path(__file__).resolve()
ROOT_UET = _UET_REPO_ROOT / "docs"
TOPICS_DIR = ROOT_UET / "topics"
PAPER_FIG_DIR = ROOT_UET / "paper" / "Figures"


def collect_figures():
    print("========================================")
    print("📊 UET FIGURE HARVESTER")
    print("========================================")

    if not PAPER_FIG_DIR.exists():
        PAPER_FIG_DIR.mkdir(parents=True)
        print(f"Created {PAPER_FIG_DIR}")

    count = 0

    # 1. Iterate over Topics
    for topic in sorted(TOPICS_DIR.iterdir()):
        if not topic.is_dir() or not topic.name[0].isdigit():
            continue

        topic_num = topic.name.split("_")[0]  # e.g., "0.1"
        result_dir = topic / "Result"

        if not result_dir.exists():
            continue

        # 2. Find PNGs
        for png in result_dir.glob("*.png"):
            # Construct new name: Fig_0.1_galaxy_rotation.png
            clean_name = png.stem.replace(" ", "_").lower()
            new_name = f"Fig_{topic_num}_{clean_name}{png.suffix}"
            dest = PAPER_FIG_DIR / new_name

            # Copy
            try:
                shutil.copy2(png, dest)
                print(f"  [+] Copied: {new_name} (from {topic.name})")
                count += 1
            except Exception as e:
                print(f"  [!] Error copying {png.name}: {e}")

    print("----------------------------------------")
    print(f"✅ Harvest Complete. {count} figures ready in {PAPER_FIG_DIR.name}/")
    print("========================================")


if __name__ == "__main__":
    collect_figures()
