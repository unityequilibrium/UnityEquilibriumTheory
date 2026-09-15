
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
import os

# Setup Path
current_dir = str(_UET_REPO_ROOT / "docs" / "scripts" / "core")
project_root = str(_UET_REPO_ROOT)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project Root: {project_root}")
print(f"Sys Path: {sys.path[:3]}")

try:
    print("Attempting to import docs...")
    import docs

    print(f"Success: {docs}")

    print("Attempting to import docs.core...")
    import docs.core

    print(f"Success: {docs.core}")

    print("Attempting to import docs.core.uet_parameters...")
    import docs.core.uet_parameters as p

    print(f"Success module: {p}")
    print(f"Has UETParameters? {'UETParameters' in dir(p)}")

    from docs.core.uet_parameters import UETParameters

    print(f"Success class: {UETParameters}")

except Exception as e:
    print(f"FAIL: {e}")
    import traceback

    traceback.print_exc()
