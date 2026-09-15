"""Synchronize the dependency gate pointer after rebuilding the result register."""

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
    dependency_path = ROOT / DEPENDENCY_REL
    dependency = json.loads(dependency_path.read_text(encoding="utf-8-sig"))
    register_hash = digest(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = register_hash
    dependency["register"]["path"] = REGISTER_REL
    dependency_path.write_text(
        json.dumps(dependency, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS_SYNCHRONIZED_MAJOR_RESULT_DEPENDENCY_REGISTER_HASH",
        "register": REGISTER_REL,
        "register_sha256": register_hash,
        "dependency": DEPENDENCY_REL,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
