"""Synchronize the Topic 13 matter-coupling normalization no-go."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"

RESULT_ID = "T13_COVARIANT_MATTER_COUPLING_NORMALIZATION_IDENTIFIABILITY_NO_GO"
LANE_KEY = "covariant_matter_coupling_normalization_no_go"
CONTROLLER = "physical_field_normalization_and_interaction_coefficient_provenance_missing"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def lane_record(action: dict[str, Any]) -> dict[str, Any]:
    major = action["major_result"]
    record = {
        key: value
        for key, value in action.items()
        if key not in {"schema_version", "artifact", "generated_at", "major_result", "evidence_artifacts"}
    }
    record.update(
        {
            "major_result_id": major["major_result_id"],
            "status": action["status"],
            "closure_level": major["closure_level"],
            "data_role": major["data_role"],
            "audit": evidence(
                ACTION_REL,
                {
                    "status": action["status"],
                    "major_result_id": major["major_result_id"],
                    "closure_level": major["closure_level"],
                },
            ),
            "controlling_blocker": action["controlling_blocker"],
            "open_blockers": major["open_blockers"],
            "claim_boundary": major["claim_boundary"],
        }
    )
    return record


def sync_full_gate(action: dict[str, Any]) -> None:
    full = load(FULL_REL)
    full["generated_at"] = date.today().isoformat()
    full.setdefault("verification_status", {}).setdefault("dimensional_observable_map", {})[
        LANE_KEY
    ] = lane_record(action)
    full["verification_status"].setdefault("eos_transport_kms_entropy", {}).pop(LANE_KEY, None)
    append_unique(
        full["major_result"]["what_is_closed"],
        "the covariant response-matter interaction rescaling no-go is explicit; the natural response coupling cannot supply a physical Phi/SI anchor",
    )
    append_unique(
        full.setdefault("evidence_artifacts", []),
        evidence(ACTION_REL, {"status": action["status"], "data_role": action["major_result"]["data_role"]}),
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sync_register(action: dict[str, Any]) -> None:
    register = load(REGISTER_REL)
    register["generated_at"] = date.today().isoformat()
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(
        full_entry["what_is_closed"],
        "the covariant response-matter interaction rescaling no-go is explicit; the natural response coupling cannot supply a physical Phi/SI anchor",
    )
    append_unique(full_entry["open_blockers"], CONTROLLER)
    append_unique(
        full_entry["evidence_artifacts"],
        evidence(ACTION_REL, {"status": action["status"], "major_result_id": RESULT_ID}),
    )
    entry = next((item for item in register["entries"] if item.get("major_result_id") == RESULT_ID), None)
    if entry is None:
        major = action["major_result"]
        register["entries"].append(
            {
                "major_result_id": RESULT_ID,
                "topic": major["topic"],
                "closure_level": major["closure_level"],
                "what_is_closed": major["what_is_closed"],
                "equation_or_mapping": major["equation_or_mapping"],
                "units": major["units"],
                "derivation_class": major["derivation_class"],
                "observable": major["observable"],
                "data_role": major["data_role"],
                "evidence_artifacts": [evidence(ACTION_REL, {"status": action["status"]})],
                "verification_status": action["status"],
                "open_blockers": major["open_blockers"],
                "dependency_unlocked": major["dependency_unlocked"],
                "claim_boundary": major["claim_boundary"],
            }
        )
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def sync_dependency(action: dict[str, Any]) -> None:
    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = date.today().isoformat()
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial[LANE_KEY] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False})
    partial["reason"] = (
        "The covariant matter-coupling no-go makes the missing physical response normalization explicit; "
        "it does not supply e0, alpha_Phi_K, Ding C_src, physical Kubo coefficients, or full closure."
    )
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    action = load(ACTION_REL)
    expected = "PASS_SCOPED_NO_GO_COVARIANT_MATTER_COUPLING_NORMALIZATION"
    if action.get("status") != expected:
        raise SystemExit(f"coupling-normalization audit is not passing: {action.get('status')}")
    sync_full_gate(action)
    sync_register(action)
    sync_dependency(action)
    print(json.dumps({"status": action["status"], "major_result_id": RESULT_ID, "lane": LANE_KEY}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
