"""Remove the obsolete broad package-absence wording from all Topic 13 entries."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
OLD = "ding_pbte_author_data_or_independent_reproduction_package_missing"
NEW = "ding_source_specific_C_src_and_mode_resolved_c_mu_not_available"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def replace(value: Any) -> Any:
    if isinstance(value, str):
        return NEW if value == OLD else value
    if isinstance(value, list):
        return [replace(item) for item in value]
    if isinstance(value, dict):
        return {key: replace(item) for key, item in value.items()}
    return value


def main() -> int:
    register = replace(load(REGISTER_REL))
    register["generated_at"] = date.today().isoformat()
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    dependency.setdefault("topic13_partial_evidence", {})["register_sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    remaining = OLD in json.dumps(register)
    print(json.dumps({
        "status": "PASS_TOPIC13_REGISTER_BLOCKER_WORDING_SYNC" if not remaining else "FAIL_TOPIC13_REGISTER_BLOCKER_WORDING_SYNC",
        "old_broad_blocker_present": remaining,
        "register_sha256": digest(REGISTER_REL),
    }, indent=2))
    return 0 if not remaining else 1


if __name__ == "__main__":
    raise SystemExit(main())
