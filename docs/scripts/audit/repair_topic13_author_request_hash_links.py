"""Refresh Topic 13 register/dependency hashes after request-wave integration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    full_rel = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
    full_hash = digest(FULL)
    entry = next(
        item for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    changed = False
    for item in entry.get("evidence_artifacts", []):
        if item.get("path") == full_rel and item.get("sha256") != full_hash:
            item["sha256"] = full_hash
            changed = True
    if changed:
        REGISTER.write_text(
            json.dumps(register, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    dependency = json.loads(DEPENDENCY.read_text(encoding="utf-8-sig"))
    register_hash = digest(REGISTER)
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["register_sha256"] = register_hash
    DEPENDENCY.write_text(
        json.dumps(dependency, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "PASS_TOPIC13_HASH_LINK_REPAIR",
        "full_gate_hash": full_hash,
        "register_hash": register_hash,
        "register_entry_updated": changed,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
