"""Make the closure-register audit refresh its dependency hash pointer."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "docs/scripts/audit/audit_major_result_closure.py"


def main() -> int:
    text = TARGET.read_text(encoding="utf-8-sig")
    marker = '    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\\n", encoding="utf-8")\n'
    insertion = marker + '''    dependency_path = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"\n    if dependency_path.is_file():\n        dependency = load(dependency_path)\n        dependency["generated_at"] = date.today().isoformat()\n        dependency.setdefault("register", {})["path"] = rel(OUT)\n        dependency["register"]["sha256"] = sha256(OUT)\n        dependency_path.write_text(\n            json.dumps(dependency, indent=2, ensure_ascii=True) + "\\n",\n            encoding="utf-8",\n        )\n'''
    if 'dependency_path = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"' in text:
        print("MAJOR_RESULT_CLOSURE_DEPENDENCY_SYNC_ALREADY_PRESENT")
        return 0
    if marker not in text:
        raise SystemExit("closure-register output anchor not found")
    TARGET.write_text(text.replace(marker, insertion, 1), encoding="utf-8")
    print("PASS_REPAIRED_MAJOR_RESULT_CLOSURE_DEPENDENCY_SYNC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
