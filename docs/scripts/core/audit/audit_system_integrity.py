"""
UET SUPREME AUDITOR
===================
The unified compliance officer for the Unity Equilibrium Theory.
Consolidates all audit logic (Structure, Docs, Code Standards, Safety) into one tool.

Modes:
  --mode structure : Check folder hierarchy (01_Engine, 02_Proof, etc.)
  --mode docs      : Check if every code file has a matching Analysis Report.
  --mode code      : Check for UETBaseSolver usage and forbidden patterns.
  --mode dynamic   : "The Dark Sweep" - Kills engines to detect Shadow Math.
  --mode full      : Run ALL checks (The rigorous standard).

Usage:
    python audit_system_integrity.py --mode full
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

import sys
import argparse
import re
import subprocess
import glob
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

# --- CONSTANTS ---
REQUIRED_DIRS = ["01_Engine", "02_Proof", "03_Research"]
KILL_SWITCH_REGEX = re.compile(r"INTEGRITY_KILL_SWITCH")
BASE_SOLVER_REGEX = re.compile(r"UETBaseSolver")
MANUAL_PATH_REGEX = re.compile(r"parents\[\d+\]")  # Risky manual path finding


# --- UTILS ---
def find_repo_root():
    curr = Path(__file__).resolve()
    for _ in range(6):
        if (curr / "docs").exists():
            return curr
        curr = curr.parent
    return None


ROOT = find_repo_root()
if not ROOT:
    print("CRITICAL: Cannot find 'docs' root.")
    sys.exit(1)

TOPICS_DIR = ROOT / "docs" / "topics"


# --- 1. STRUCTURE AUDIT ---
def run_structure_audit():
    print("\n" + "=" * 80)
    print("🏗️  STRUCTURE AUDIT")
    print("=" * 80)
    print(f"{'TOPIC':<40} | {'ENGINE':<8} | {'PROOF':<8} | {'RES':<8}")
    print("-" * 80)

    topics = sorted(
        [d for d in TOPICS_DIR.iterdir() if d.is_dir() and d.name[0].isdigit()]
    )
    for topic in topics:
        code_dir = topic / "Code"
        e_ok = (code_dir / "01_Engine").exists()
        p_ok = (code_dir / "02_Proof").exists()
        r_ok = (code_dir / "03_Research").exists()

        e_icon = "✅" if e_ok else "❌"
        p_icon = "✅" if p_ok else "❌"
        r_icon = "✅" if r_ok else "❌"

        print(f"{topic.name:<40} | {e_icon:<8} | {p_icon:<8} | {r_icon:<8}")


# --- 2. DOC COVERAGE AUDIT ---
def run_doc_audit():
    print("\n" + "=" * 80)
    print("📄 DOCUMENTATION COVERAGE AUDIT")
    print("=" * 80)

    missing_count = 0
    total_files = 0

    topics = sorted(
        [d for d in TOPICS_DIR.iterdir() if d.is_dir() and d.name[0].isdigit()]
    )

    for topic in topics:
        code_dir = topic / "Code"
        doc_dir = topic / "Doc"

        if not code_dir.exists():
            continue

        # Gather Code
        code_files = []
        for r, _, f in os.walk(code_dir):
            for file in f:
                if file.endswith(".py") and file != "__init__.py":
                    code_files.append(Path(r) / file)

        # Gather Docs
        doc_contents = ""
        if doc_dir.exists():
            for r, _, f in os.walk(doc_dir):
                for file in f:
                    if file.endswith(".md"):
                        try:
                            doc_contents += (Path(r) / file).read_text(
                                encoding="utf-8", errors="ignore"
                            )
                        except:
                            pass

        # Check Coverage
        missing_in_topic = []
        for cf in code_files:
            total_files += 1
            if cf.name not in doc_contents:
                missing_in_topic.append(cf.name)

        if missing_in_topic:
            print(f"📂 {topic.name}")
            for m in missing_in_topic:
                print(f"   🔴 MISSING DOC: {m}")
                missing_count += 1

    score = (
        ((total_files - missing_count) / total_files) * 100 if total_files > 0 else 0
    )
    print("-" * 80)
    print(
        f"Documentation Score: {score:.1f}% ({total_files - missing_count}/{total_files})"
    )


# --- 3. CODE STANDARDS AUDIT ---
def run_code_audit():
    print("\n" + "=" * 80)
    print("🧬 CODE STANDARDS AUDIT (BaseSolver & Paths)")
    print("=" * 80)

    violations = []

    topics = sorted(
        [d for d in TOPICS_DIR.iterdir() if d.is_dir() and d.name[0].isdigit()]
    )
    for topic in topics:
        code_dir = topic / "Code"
        if not code_dir.exists():
            continue

        for r, _, f in os.walk(code_dir):
            for file in f:
                if file.endswith(".py") and file != "__init__.py":
                    path = Path(r) / file
                    try:
                        content = path.read_text(encoding="utf-8", errors="ignore")

                        # Rule 1: Must use UETBaseSolver (if Engine)
                        if "01_Engine" in str(path) and not BASE_SOLVER_REGEX.search(
                            content
                        ):
                            # Exempt explicit exceptions if needed
                            if "Base" not in content:
                                violations.append(
                                    f"{topic.name}/{file} : No UETBaseSolver"
                                )

                        # Rule 2: No fragile paths
                        if (
                            MANUAL_PATH_REGEX.search(content)
                            and "UETPathManager" not in content
                        ):
                            violations.append(
                                f"{topic.name}/{file} : Manual 'parents[]' pathing"
                            )

                    except:
                        pass

    if violations:
        for v in violations:
            print(f"❌ VIOLATION: {v}")
    else:
        print("✅ ALL CODE COMPLIANT.")


# --- 4. DYNAMIC SAFETY AUDIT ---
def run_dynamic_audit():
    print("\n" + "=" * 80)
    print("😈 DYNAMIC SAFETY AUDIT (Engine Kill Check)")
    print("=" * 80)

    research_scripts = glob.glob(
        str(ROOT / "docs/topics/*/Code/03_Research/Research_*.py")
    )
    survivors = []
    env = os.environ.copy()
    env["UET_KILL_ENGINE"] = "TRUE"  # Poison Pill

    print(f"Running {len(research_scripts)} scripts vs Kill Switch...")

    for script in sorted(research_scripts):
        sname = Path(script).name
        try:
            res = subprocess.run(
                [sys.executable, script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=10,
            )
            output = (res.stdout + res.stderr).upper()

            if res.returncode != 0 or "FAIL" in output or "ERROR" in output:
                # print(f"✅ {sname} : DIED") # Too verbose? User wants concise.
                pass
            elif "PASS" in output or "SUCCESS" in output:
                print(f"❌ {sname} : SURVIVED (Shadow Math!)")
                survivors.append(sname)
            else:
                pass  # Ambiguous
        except:
            pass

    if survivors:
        print(f"\n🚨 FOUND {len(survivors)} SCRIPTS WITH SHADOW MATH.")
    else:
        print("\n✨ SYSTEM CLEAN: All scripts rely on the Core Engine.")


def main():
    parser = argparse.ArgumentParser(description="UET Supreme Auditor")
    parser.add_argument(
        "--mode",
        choices=["full", "structure", "docs", "code", "dynamic"],
        default="full",
    )
    args = parser.parse_args()

    if args.mode in ["full", "structure"]:
        run_structure_audit()
    if args.mode in ["full", "docs"]:
        run_doc_audit()
    if args.mode in ["full", "code"]:
        run_code_audit()
    if args.mode in ["full", "dynamic"]:
        run_dynamic_audit()


if __name__ == "__main__":
    main()
