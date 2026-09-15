
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


def migrate_all_topics():
    root_dir = _UET_REPO_ROOT / "docs" / "topics"
    print("🚀 STARTING BIG CLEAN: ALL TOPICS MIGRATION (V2.1)")
    print("==================================================")

    # Standard subfolders for Data
    pillars = ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]

    topics = sorted([d for d in root_dir.iterdir() if d.is_dir() and d.name[0].isdigit()])

    for topic in topics:
        print(f"🔧 Processing: {topic.name}")

        # --- 1. RESULT MIGRATION ---
        result_dir = topic / "Result"
        result_dir.mkdir(exist_ok=True)

        (result_dir / "01_Showcase").mkdir(exist_ok=True)
        (result_dir / "02_Figures").mkdir(exist_ok=True)
        logs_dir = result_dir / "_Logs"
        logs_dir.mkdir(exist_ok=True)

        # Move timestamped/run logs
        for item in result_dir.iterdir():
            if item.is_dir() and item.name not in [
                "01_Showcase",
                "02_Figures",
                "_Logs",
                "figures",
                "_Archive",
            ]:
                # Assume it's a log folder if it starts with digit or has 'run'
                if item.name[0].isdigit() or "run" in item.name.lower():
                    try:
                        shutil.move(str(item), str(logs_dir / item.name))
                    except Exception as e:
                        print(f"   ⚠️ Could not move {item.name}: {e}")

        # --- 2. REF MIGRATION (Flatten) ---
        ref_dir = topic / "Ref"
        if ref_dir.exists():
            (ref_dir / "PDF_Downloads").mkdir(exist_ok=True)

            # Walk and Flatten PDFs
            for r, d, f in os.walk(ref_dir):
                for file in f:
                    if file.lower().endswith(".pdf"):
                        src = Path(r) / file
                        dst = ref_dir / "PDF_Downloads" / file
                        if src.parent != dst:  # Don't move if already there
                            try:
                                shutil.move(str(src), str(dst))
                                print(f"   📄 Flattened PDF: {file}")
                            except:
                                pass

            # Handle Data_Source LEAK (Move to Data/03_Research)
            data_source_legacy = ref_dir / "Data_Source"
            if data_source_legacy.exists():
                data_target = topic / "Data" / "03_Research"
                data_target.mkdir(parents=True, exist_ok=True)

                for item in data_source_legacy.iterdir():
                    try:
                        shutil.move(str(item), str(data_target / item.name))
                        print(f"   💾 Moved Data_Source content to Data/03_Research: {item.name}")
                    except:
                        pass
                try:
                    data_source_legacy.rmdir()
                except:
                    pass

            # Remove empty legacy folders in Ref
            for p in pillars:
                legacy = ref_dir / p
                if legacy.exists() and not any(legacy.iterdir()):
                    legacy.rmdir()

        # --- 3. DATA MIGRATION (Ensure 5x4) ---
        data_dir = topic / "Data"
        data_dir.mkdir(exist_ok=True)
        for p in pillars:
            (data_dir / p).mkdir(exist_ok=True)

    print("\n✅ BIG CLEAN COMPLETE.")


if __name__ == "__main__":
    migrate_all_topics()
