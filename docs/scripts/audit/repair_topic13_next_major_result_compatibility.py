from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    register_path = ROOT / REGISTER_REL
    register = json.loads(register_path.read_text(encoding="utf-8-sig"))
    if register.get("next_major_result") != "T13_FULL_THERMODYNAMIC_BRIDGE":
        register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
        register_path.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency_path = ROOT / DEPENDENCY_REL
    dependency = json.loads(dependency_path.read_text(encoding="utf-8-sig"))
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    dependency.setdefault("topic13_partial_evidence", {})["register_sha256"] = digest(REGISTER_REL)
    dependency_path.write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_TOPIC13_REGISTER_COMPATIBILITY_REPAIRED", "register_sha256": digest(REGISTER_REL)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
