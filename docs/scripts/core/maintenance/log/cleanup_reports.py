#!/usr/bin/env python3
"""
Clean up temporary log reports
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

from pathlib import Path

maintenance_dir = _UET_REPO_ROOT / "docs" / "scripts" / "maintenance"

# Find all temporary report files
report_files = [
    "log_analysis_report.csv",
    "log_analysis_report.json",
    "log_health_report.json",
    "log_reset_report.json"
]

deleted_count = 0
for filename in report_files:
    file_path = maintenance_dir / filename
    if file_path.exists():
        file_path.unlink()
        print(f"Deleted: {filename}")
        deleted_count += 1

print(f"\nCleaned up {deleted_count} temporary report files")
