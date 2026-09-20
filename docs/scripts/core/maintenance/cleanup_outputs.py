
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
import os
import shutil
from pathlib import Path

# Config
ROOT = _UET_REPO_ROOT / "docs" / "topics"
VALID_PILLARS = ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]


def cleanup_results():
    print("🧹 STARTING RESULTS CLEANUP...")
    deleted_count = 0

    if not ROOT.exists():
        print("Root not found.")
        return

    # Iterate all topics
    for topic in ROOT.iterdir():
        if not topic.is_dir() or not topic.name.startswith("0."):
            continue

        result_dir = topic / "Result"
        if not result_dir.exists():
            continue

        print(f"Checking {topic.name}/Result...")

        # Check items in Result
        for item in result_dir.iterdir():
            if item.is_dir():
                # If it's NOT a valid pillar "01_Engine" etc. -> DELETE IT
                if item.name not in VALID_PILLARS:
                    # Double check it looks like a run folder (starts with digits usually)
                    # User complained about "17689..." timestamp folders.
                    print(f"  ❌ Deleting SPAM folder: {item.name}")
                    try:
                        shutil.rmtree(item)
                        deleted_count += 1
                    except Exception as e:
                        print(f"     Failed: {e}")
            else:
                # Delete loose files in Result (stats.csv, pngs)?
                # User images showed PNGs and CSVs loose in Research folders (ok) or Result (maybe ok).
                # But 'Result/' root should be clean.
                if item.name != "README.md":
                    print(f"  ❌ Deleting LOOSE file: {item.name}")
                    try:
                        os.remove(item)
                        deleted_count += 1
                    except Exception as e:
                        print(f"     Failed: {e}")

    print(f"✨ Cleanup Complete. Deleted {deleted_count} items.")


if __name__ == "__main__":
    cleanup_results()
