
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
from pathlib import Path
import shutil

# Robust Path: scripts/Maintenance -> docs
current_file = Path(__file__).resolve()
root = _UET_REPO_ROOT / "docs" / "topics"


def fix_paths():
    if not root.exists():
        print(f"Root not found: {root}")
        return

    # 1. Update Scripts
    for path in root.rglob("test_*.py"):
        try:
            content = path.read_text(encoding="utf-8")
            if 'parents[1] / "Result"' in content:
                new_content = content.replace(
                    'parents[1] / "Result"', 'parents[2] / "Result"'
                )
                path.write_text(new_content, encoding="utf-8")
                print(f"Fixed path in {path.name}")
        except Exception as e:
            print(f"Error reading {path}: {e}")

    # 2. Move Files
    for code_res in root.rglob("Code/Result"):
        if code_res.is_dir():
            # Target is Topic/Result
            # Code/Result -> Code -> Topic -> Result
            topic_res = code_res.parents[1] / "Result"
            topic_res.mkdir(parents=True, exist_ok=True)

            for item in code_res.iterdir():
                if item.is_file():
                    target = topic_res / item.name
                    shutil.move(str(item), str(target))
                    print(f"Moved {item.name} to {topic_res}")

            # Remove empty Code/Result
            try:
                code_res.rmdir()
                print(f"Removed empty {code_res}")
            except:
                pass


if __name__ == "__main__":
    fix_paths()
