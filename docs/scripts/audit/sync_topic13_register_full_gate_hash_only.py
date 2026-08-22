from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
MATRIX_REL = "docs/core/artifacts/t13_topic13_closure_matrix.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    register_path = ROOT / REGISTER_REL
    register = json.loads(register_path.read_text(encoding="utf-8-sig"))
    entry = next(
        item
        for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    full_hash = digest(FULL_REL)
    evidence = next(item for item in entry["evidence_artifacts"] if item.get("path") == FULL_REL)
    evidence["sha256"] = full_hash

    matrix_hash = digest(MATRIX_REL)
    matrix_entry = next(
        item
        for item in register["entries"]
        if item.get("major_result_id") == "T13_TOPIC13_CLOSURE_MATRIX"
    )
    matrix_evidence = next(
        item for item in matrix_entry["evidence_artifacts"] if item.get("path") == MATRIX_REL
    )
    matrix_evidence["sha256"] = matrix_hash
    entry.setdefault("closure_matrix", {})["sha256"] = matrix_hash
    register["generated_at"] = date.today().isoformat()
    register_path.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency_path = ROOT / DEPENDENCY_REL
    dependency = json.loads(dependency_path.read_text(encoding="utf-8-sig"))
    register_hash = digest(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = register_hash
    dependency.setdefault("topic13_partial_evidence", {})["register_sha256"] = register_hash
    dependency.setdefault("topic13_partial_evidence", {}).setdefault("closure_matrix", {})["sha256"] = matrix_hash
    dependency_path.write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_TOPIC13_REGISTER_FULL_GATE_HASH_SYNC", "full_gate_sha256": full_hash, "register_sha256": register_hash}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
