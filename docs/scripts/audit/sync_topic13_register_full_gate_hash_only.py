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
COMPONENT_REL = "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    register_path = ROOT / REGISTER_REL
    register = json.loads(register_path.read_text(encoding="utf-8-sig"))
    full = json.loads((ROOT / FULL_REL).read_text(encoding="utf-8-sig"))
    component = json.loads((ROOT / COMPONENT_REL).read_text(encoding="utf-8-sig"))
    entry = next(
        item
        for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    full_major = full["major_result"]
    full_fields = {
        "closure_level": full_major["closure_level"],
        "what_is_closed": full_major["what_is_closed"],
        "equation_or_mapping": full["equation_or_mapping"],
        "units": full["units"],
        "derivation_class": full["derivation_class"],
        "observable": full["observable"],
        "data_role": full["data_role"],
        "dependency_unlocked": full_major["dependency_unlocked"],
        "claim_boundary": full["claim_boundary"],
    }
    for field, value in full_fields.items():
        entry[field] = value
    entry["open_blockers"] = full_major["what_remains_open"]
    entry["resolved_blockers"] = full_major.get("resolved_blockers", [])
    entry["closure_summary"] = full_major.get("closure_summary", {})
    entry["verification_status"] = full["status"]
    entry["claim_promotion"] = False

    full_hash = digest(FULL_REL)
    evidence = next(item for item in entry["evidence_artifacts"] if item.get("path") == FULL_REL)
    evidence["sha256"] = full_hash
    component_evidence = {
        "path": COMPONENT_REL,
        "sha256": digest(COMPONENT_REL),
        "summary": {
            "status": component.get("status"),
            "major_result_id": component.get("major_result", {}).get("major_result_id"),
            "closure_level": component.get("major_result", {}).get("closure_level"),
            "physical_coefficient_evidence": component.get("physical_coefficient_evidence"),
            "full_core_unlock": component.get("full_core_unlock"),
        },
    }
    existing_component_evidence = next(
        (item for item in entry["evidence_artifacts"] if item.get("path") == COMPONENT_REL),
        None,
    )
    if existing_component_evidence is None:
        entry["evidence_artifacts"].append(component_evidence)
    else:
        existing_component_evidence.clear()
        existing_component_evidence.update(component_evidence)

    component_major = component["major_result"]
    component_entry = {
        "major_result_id": component_major["major_result_id"],
        "topic": component_major["topic"],
        "closure_level": component_major["closure_level"],
        "claim_promotion": False,
        "what_is_closed": component_major["what_is_closed"],
        "equation_or_mapping": component_major["equation_or_mapping"],
        "units": component_major["units"],
        "derivation_class": component_major["derivation_class"],
        "observable": component_major["observable"],
        "data_role": component_major["data_role"],
        "evidence_artifacts": [component_evidence],
        "verification_status": component.get("status"),
        "open_blockers": component_major["open_blockers"],
        "dependency_unlocked": component_major["dependency_unlocked"],
        "claim_boundary": component_major["claim_boundary"],
    }
    existing_component = next(
        (item for item in register["entries"] if item.get("major_result_id") == component_major["major_result_id"]),
        None,
    )
    if existing_component is None:
        register["entries"].append(component_entry)
    else:
        existing_component.clear()
        existing_component.update(component_entry)

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
    register["claim_promotion"] = False
    register_path.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency_path = ROOT / DEPENDENCY_REL
    dependency = json.loads(dependency_path.read_text(encoding="utf-8-sig"))
    register_hash = digest(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["register_sha256"] = register_hash
    partial.setdefault("closure_matrix", {})["sha256"] = matrix_hash
    partial["topic13_flat_thermodynamic_bridge_components"] = {
        "path": COMPONENT_REL,
        "sha256": digest(COMPONENT_REL),
        "summary": {
            "status": component.get("status"),
            "closure_level": component_major.get("closure_level"),
            "full_core_unlock": component.get("full_core_unlock"),
            "controlling_blocker": component.get("controlling_blocker"),
        },
        "full_core_unlock": False,
    }
    dependency_path.write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_TOPIC13_REGISTER_FULL_GATE_HASH_SYNC", "full_gate_sha256": full_hash, "register_sha256": register_hash, "component_major_result": component_major["major_result_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())