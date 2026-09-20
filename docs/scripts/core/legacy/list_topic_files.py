
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

topics = [
    "0.9_Quantum_Nonlocality",
    "0.12_Vacuum_Energy_Casimir",
    "0.18_Neutrino_Mixing",
]
root = _UET_REPO_ROOT / "docs" / "topics"

for topic in topics:
    print(f"--- {topic} ---")
    topic_path = root / topic
    if topic_path.exists():
        for p in topic_path.rglob("*.py"):
            print(p)
