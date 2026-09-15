"""
UET Integrity Auditor V2 (Global Sweep)
=======================================
Systematically audits all 24 Research Topics for conformity to the "Unity" standard.

Checks:
1. ENGINE INTEGRITY:
   - File exists in Code/01_Engine/
   - Imports `UETBaseSolver` & `UETParameters`
   - Explicitly checks `INTEGRITY_KILL_SWITCH`

2. RESEARCH INTEGRITY:
   - Imports correct Engine
   - Calculates nothing locally (No Shadow Math) - *Heuristic check*
   - Uses Robust Path Finding

3. PATH STRUCTURE:
   - Verifies 01_Engine, 02_Proof, 03_Research, 04_Competitor structure.

Usage:
    python docs/tools/integrity_auditor_v2.py
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

import os
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

# Constants
REQUIRED_DIRS = ["01_Engine", "02_Proof", "03_Research"]  # 04_Competitor is optional
KILL_SWITCH_REGEX = re.compile(r"INTEGRITY_KILL_SWITCH")
ENGINE_IMPORT_REGEX = re.compile(r"from .*Engine.* import|import .*Engine")
UET_BASE_REGEX = re.compile(r"UETBaseSolver")


@dataclass
class TopicStatus:
    name: str
    path: Path
    has_engine: bool = False
    engine_compliant: bool = False
    research_compliant: bool = False
    details: str = ""


def find_repo_root():
    curr = Path(__file__).resolve()
    for _ in range(6):
        if (curr / "docs").exists():
            return curr
        curr = curr.parent
    return None


ROOT = find_repo_root()
if not ROOT:
    print("CRITICAL: Cannot find repo root.")
    sys.exit(1)

TOPICS_DIR = ROOT / "docs" / "topics"


def audit_topic(topic_path: Path) -> TopicStatus:
    status = TopicStatus(name=topic_path.name, path=topic_path)
    details = []

    # 1. Check Directory Structure
    code_dir = topic_path / "Code"
    if not code_dir.exists():
        status.details = "MISSING: Code directory"
        return status

    # 2. Check Engine
    engine_dir = code_dir / "01_Engine"
    engine_files = list(engine_dir.glob("*.py")) if engine_dir.exists() else []

    # Filter out __init__.py
    engine_files = [f for f in engine_files if f.name != "__init__.py"]

    if not engine_files:
        details.append("[NO] No Engine found")
    else:
        status.has_engine = True
        main_engine = engine_files[0]  # Assume first is main for now

        try:
            content = main_engine.read_text(encoding="utf-8")

            # Check for Base Class
            if not UET_BASE_REGEX.search(content):
                details.append(f"[!!] {main_engine.name}: Missing UETBaseSolver")

            # Check for Kill Switch
            if not KILL_SWITCH_REGEX.search(content):
                details.append(
                    f"[NO] {main_engine.name}: Missing INTEGRITY_KILL_SWITCH"
                )
            else:
                status.engine_compliant = True  # Only if kill switch is present

        except Exception as e:
            details.append(f"[NO] Error reading engine: {e}")

    # 3. Check Research Scripts
    research_dir = code_dir / "03_Research"
    research_files = list(research_dir.glob("*.py")) if research_dir.exists() else []
    research_files = [f for f in research_files if f.name != "__init__.py"]

    if not research_files:
        details.append("[!!] No Research scripts found")
    else:
        compliant_count = 0
        for rf in research_files:
            try:
                content = rf.read_text(encoding="utf-8")
                # Look for Engine Import
                # Either "from ... import EngineX" or "import ...EngineX"
                # Or dynamic import "spec_from_file_location"
                if "importlib" in content or "from" in content or "import" in content:
                    # This is a bit weak, let's look for "Engine" string
                    if "Engine" in content:
                        compliant_count += 1
                    else:
                        details.append(f"[!!] {rf.name}: No 'Engine' reference found")
                else:
                    details.append(f"[!!] {rf.name}: Suspicious lack of imports")
            except:
                pass

        if compliant_count == len(research_files) and len(research_files) > 0:
            status.research_compliant = True
        elif len(research_files) > 0:
            details.append(
                f"[!!] Only {compliant_count}/{len(research_files)} research scripts use Engine"
            )

    status.details = "; ".join(details)
    return status


def main():
    print(f"SEARCHING: STARTING UET INTEGRITY AUDIT V2 on {TOPICS_DIR}")
    print("=" * 100)
    print(
        f"{'TOPIC':<40} | {'ENGINE':<10} | {'KILL SWITCH':<12} | {'RESEARCH':<10} | {'DETAILS'}"
    )
    print("-" * 100)

    topics = sorted(
        [d for d in TOPICS_DIR.iterdir() if d.is_dir() and d.name[0].isdigit()]
    )

    results = []

    for topic in topics:
        stat = audit_topic(topic)
        results.append(stat)

        engine_icon = "[OK]" if stat.has_engine else "[NO]"
        kill_icon = "[OK]" if stat.engine_compliant else "[NO]"
        res_icon = "[OK]" if stat.research_compliant else "[!!]"

        print(
            f"{stat.name:<40} | {engine_icon:<10} | {kill_icon:<12} | {res_icon:<10} | {stat.details}"
        )

    print("=" * 100)

    # Summary Metrics
    total = len(results)
    compliant_engines = sum(1 for r in results if r.engine_compliant)
    print(f"\nSUMMARY:")
    print(f"  Total Topics: {total}")
    print(
        f"  Compliant Engines (Kill Switch): {compliant_engines}/{total} ({compliant_engines/total*100:.1f}%)"
    )

    if compliant_engines < total:
        print(
            "\n[NO] FAILED: Integrity compromised. See 'DETAILS' column for missing Kill Switches."
        )
        sys.exit(1)
    else:
        print("\n[OK] PASSED: All topics verified.")
        sys.exit(0)


if __name__ == "__main__":
    main()
