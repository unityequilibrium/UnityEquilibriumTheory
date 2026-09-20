"""Sync the named Phi_E reference-normalization result into Topic 13 gates."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ACTION = "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json"
FULL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict) -> dict:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def unique(items: list, item: object) -> None:
    if item not in items:
        items.append(item)


def main() -> int:
    action = load(ACTION)
    if action["status"] != "PASS_NAMED_PHI_E_REFERENCE_NORMALIZATION":
        raise SystemExit("Phi_E reference audit is not passing")
    today = date.today().isoformat()
    full = load(FULL)
    full["generated_at"] = today
    unique(full["major_result"]["what_is_closed"], "source-backed reference normalization for named Phi_E energy-response coordinate")
    unique(full["major_result"]["what_remains_open"], "base_Phi_to_Phi_E_mapping_and_independent_base_alpha_Phi_K_missing")
    full.setdefault("verification_status", {})["phi_e_reference_normalization"] = {"status": action["status"], "closure_level": "CLOSED_FOR_LANE", "numeric_base_alpha_Phi_K_emitted": False, "parameter_fitting_performed": False, "target_data_used": False, "xie_2026_accessed": False, "audit": evidence(ACTION, {"status": action["status"]}), "claim_boundary": action["claim_boundary"]}
    unique(full.setdefault("evidence_artifacts", []), evidence(ACTION, {"status": action["status"], "data_role": action["major_result"]["data_role"]}))
    (ROOT / FULL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item["major_result_id"] == "T13_FULL_THERMODYNAMIC_BRIDGE")
    unique(full_entry["what_is_closed"], "source-backed reference normalization for named Phi_E energy-response coordinate")
    unique(full_entry["open_blockers"], action["controlling_blocker"])
    unique(full_entry["evidence_artifacts"], evidence(ACTION, {"status": action["status"]}))
    for item in full_entry["evidence_artifacts"]:
        if item["path"] == FULL:
            item["sha256"] = digest(FULL)
    existing = next((item for item in register["entries"] if item["major_result_id"] == action["major_result"]["major_result_id"]), None)
    record = {key: action["major_result"][key] for key in ("major_result_id", "topic", "closure_level", "what_is_closed", "equation_or_mapping", "units", "derivation_class", "observable", "data_role", "verification_status", "open_blockers", "dependency_unlocked", "claim_boundary")}
    record["evidence_artifacts"] = [evidence(ACTION, {"status": action["status"]})]
    if existing is None:
        register["entries"].append(record)
    else:
        existing.clear(); existing.update(record)
    (ROOT / REGISTER).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dep = load(DEPENDENCY)
    dep["generated_at"] = today
    partial = dep.setdefault("topic13_partial_evidence", {})
    partial["phi_e_reference_normalization"] = evidence(ACTION, {"status": action["status"], "full_core_unlock": False})
    partial["register_sha256"] = digest(REGISTER)
    dep.setdefault("register", {})["sha256"] = digest(REGISTER)
    (ROOT / DEPENDENCY).write_text(json.dumps(dep, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_INTEGRATED_T13_PHI_E_REFERENCE_NORMALIZATION", "full_status": full["status"], "register_sha256": digest(REGISTER)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
