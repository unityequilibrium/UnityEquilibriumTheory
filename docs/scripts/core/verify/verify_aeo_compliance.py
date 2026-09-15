
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
import json
import re

def audit_aeo():
    # Fix: Get absolute path relative to script location
    script_dir = str(_UET_REPO_ROOT / "docs" / "scripts" / "core")
    # The script is in docs/scripts/verify/, so topics is at ../../../topics
    base_dir = _UET_REPO_ROOT / "docs" / "topics"
    if not os.path.exists(base_dir):
        print(f"❌ Error: Cannot find topics directory at {base_dir}")
        return

    report = []
    
    # Get all topic directories
    topics = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d[0].isdigit()]
    topics.sort()

    print(f"Auditing {len(topics)} topics for AEO v2.0 compliance...\n")

    for topic in topics:
        readme_path = os.path.join(base_dir, topic, "README.md")
        status = {"topic": topic, "schema": "❌ MISSING", "digest": "❌ MISSING", "pass": False}
        
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Check for Schema.org (JSON-LD or Microdata)
                has_json_ld = '"@context": "https://schema.org"' in content
                has_microdata = 'itemtype="https://schema.org/' in content or 'itemtype="http://schema.org/' in content
                
                if has_json_ld or has_microdata:
                    status["schema"] = "✅ VALID"
                
                # Check for AI-Digest (EN/TH)
                if "> [!NOTE]" in content and "AI-Digest" in content:
                    status["digest"] = "✅ VALID"
                    
                if status["schema"] == "✅ VALID" and status["digest"] == "✅ VALID":
                    status["pass"] = True
        else:
            status["schema"] = "❌ NO README"
            status["digest"] = "❌ NO README"
            
        report.append(status)

    # Generate Formatted Report
    print(f"{'Topic ID':<45} | {'Schema.org':<12} | {'AI-Digest':<12}")
    print("-" * 75)
    for r in report:
        print(f"{r['topic']:<45} | {r['schema']:<12} | {r['digest']:<12}")

    passed_count = sum(1 for r in report if r["pass"])
    if len(topics) > 0:
        print(f"\nSummary: {passed_count}/{len(topics)} topics passed ({(passed_count/len(topics))*100:.1f}%)")
    else:
        print("\nSummary: No topics found to audit.")

if __name__ == "__main__":
    audit_aeo()
