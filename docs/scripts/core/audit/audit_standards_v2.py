
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
import time
from pathlib import Path
import sys


def audit_project():
    root = _UET_REPO_ROOT / "docs" / "topics"
    print(f"🔍 STARTING UET STANDARDS AUDIT (V2.1)")
    print(f"Target: {root}")
    print("-" * 60)
    print(f"{'TOPIC':<35} | {'RESULT (Showcase)':<20} | {'REF (Flat)':<15} | {'DATA (5x4)':<15}")
    print("-" * 60)

    topics = sorted([d for d in root.iterdir() if d.is_dir() and d.name[0].isdigit()])

    audit_log = []

    for topic in topics:
        status_result = "❌ OLD"
        status_ref = "❌ NESTED"
        status_data = "❓ UNKNOWN"

        # 1. Check Result Standard (Looking for 01_Showcase)
        result_dir = topic / "Result"
        if (result_dir / "01_Showcase").exists() and (result_dir / "_Logs").exists():
            status_result = "✅ V2.1"
        elif not result_dir.exists():
            status_result = "⚠️ MISSING"

        # 2. Check Reference Standard (Should NOT have 01_Engine etc, should be flat or empty)
        ref_dir = topic / "Ref"
        if ref_dir.exists():
            subdirs = [x.name for x in ref_dir.iterdir() if x.is_dir()]
            legacy_dirs = ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]
            if any(x in subdirs for x in legacy_dirs):
                status_ref = "❌ NESTED (Legacy)"
            else:
                status_ref = "✅ FLAT"
        else:
            status_ref = "⚠️ MISSING"

        # 3. Check Data Standard (Should HAVE 01_Engine etc if not empty)
        data_dir = topic / "Data"
        if data_dir.exists():
            subdirs = [x.name for x in data_dir.iterdir() if x.is_dir()]
            legacy_dirs = ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]
            if any(x in subdirs for x in legacy_dirs):
                status_data = "✅ 5x4 Grid"
            elif not list(data_dir.iterdir()):
                status_data = "⚪ EMPTY"
            else:
                status_data = "❌ CHAOS (Flat?)"
        else:
            status_data = "⚠️ MISSING"

        print(f"{topic.name:<35} | {status_result:<20} | {status_ref:<15} | {status_data:<15}")

        # Collect violations for summary
        if "❌" in status_result or "❌" in status_ref or "❌" in status_data:
            audit_log.append(topic.name)

    print("-" * 60)
    print(f"🚨 FOUND INTENSIVE WORK NEEDED IN {len(audit_log)} TOPICS.")
    print("Violations detected in:")
    for t in audit_log:
        print(f" - {t}")


if __name__ == "__main__":
    audit_project()
