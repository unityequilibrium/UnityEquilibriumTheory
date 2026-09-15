"""Repair register and dependency hashes after the mp-48 gate integration."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
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


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def replace_recursive(value: Any) -> Any:
    if isinstance(value, str):
        return NEW if value == OLD else value
    if isinstance(value, list):
        return [replace_recursive(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_recursive(item) for key, item in value.items()}
    return value


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def main() -> int:
    today = date.today().isoformat()
    register = load(REGISTER_REL)
    index = next(i for i, item in enumerate(register["entries"]) if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    entry = replace_recursive(register["entries"][index])
    append_unique(
        entry["what_is_closed"],
        "independent mp-48 harmonic graphite heat-capacity comparator with provenance, volumetric conversion, and epistemic envelope",
    )
    append_unique(entry["open_blockers"], NEW)
    entry.setdefault("data_role", {})["independent_heat_capacity_source"] = "CLOSED_FOR_LANE_COMPARATOR_NOT_CALIBRATION"
    evidence_items = entry.setdefault("evidence_artifacts", [])
    for item in evidence_items:
        if item.get("path") == FULL_REL:
            item["sha256"] = sha256(FULL_REL)
    for rel, summary in (
        (AUDIT_REL, {"status": "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE", "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION"}),
        (PACKAGE_REL, {"status": "SOURCE_LOCKED_INDEPENDENT_HARMONIC_CV_COMPARATOR", "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION"}),
    ):
        item = {"path": rel, "sha256": sha256(rel), "summary": summary}
        if not any(existing.get("path") == rel for existing in evidence_items):
            evidence_items.append(item)
    register["entries"][index] = entry
    register["generated_at"] = today
    register["next_major_result"] = {
        "major_result_id": "T13_DIMENSIONAL_PHI_ENERGY_ANCHOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "controlling_blocker": "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
        "source_route": "mp-48 independent c_v comparator is available but is not a Phi calibration",
    }
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    dependency.setdefault("register", {})["sha256"] = sha256(REGISTER_REL)
    dependency.setdefault("topic13_partial_evidence", {})["register_sha256"] = sha256(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS_REGISTER_LINKAGE_REPAIRED",
        "register_sha256": sha256(REGISTER_REL),
        "full_gate_sha256": sha256(FULL_REL),
        "dependency_register_sha256": dependency["register"]["sha256"],
        "mp48_present": any("mp-48" in str(item) for item in entry["what_is_closed"]),
        "old_broad_blocker_present": OLD in json.dumps(entry),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
