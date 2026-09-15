
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

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    print("Attempting to import docs.core.uet_matrix_engine...")
    import docs.core.uet_matrix_engine

    print("✅ Success: uet_matrix_engine imported.")
except Exception as e:
    print(f"❌ Failed: {e}")

try:
    print("Attempting to import docs.core.uet_base_solver...")
    from docs.core.uet_base_solver import UETBaseSolver

    print("✅ Success: UETBaseSolver imported.")
except Exception as e:
    print(f"❌ Failed: {e}")
