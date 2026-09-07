"""Integrate the natural-unit covariant action route boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-11.md"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def main() -> int:
    action = load(ACTION_REL)
    if action.get("status") != "PASS_NATURAL_UNIT_ROUTE_IDENTIFIED_SI_MAPPING_BLOCKED":
        raise SystemExit(f"action route audit is not passing: {action.get('status')}")
    today = date.today().isoformat()

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(
        full["major_result"]["what_is_closed"],
        "covariant natural-unit action route identified with explicit SI-anchor and covariant-Phi-to-normalized-Phi blockers",
    )
    route_projection = full.setdefault("verification_status", {}).setdefault(
        "covariant_action_si_anchor_route", {}
    )
    route_projection.update(
        {
            "status": "PASS_ROUTE_IDENTIFIED_SI_BLOCKED",
            "closure_level": "CLOSED_FOR_LANE",
            "numeric_e0_emitted": False,
            "numeric_alpha_Phi_K_emitted": False,
            "audit": evidence(
                ACTION_REL,
                {"status": action["status"], "major_result_id": "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE"},
            ),
            "claim_boundary": action["claim_boundary"],
            "major_result_id": action["major_result"]["major_result_id"],
            "data_role": action["major_result"]["data_role"],
            "checks": action.get("checks", route_projection.get("checks", {})),
            "controlling_blocker": action.get(
                "controlling_blocker", route_projection.get("controlling_blocker")
            ),
            "next_controller": action.get("next_controller", route_projection.get("next_controller")),
            "open_blockers": action["major_result"].get(
                "open_blockers", route_projection.get("open_blockers", [])
            ),
            "coefficient_provenance": action["major_result"].get(
                "coefficient_provenance", route_projection.get("coefficient_provenance", {})
            ),
        }
    )
    append_unique(full.setdefault("evidence_artifacts", []), evidence(ACTION_REL, {"status": action["status"], "data_role": "FORMULA_AND_DEPENDENCY_AUDIT_NOT_CALIBRATION"}))
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "covariant natural-unit action route identified with explicit SI-anchor and covariant-Phi-to-normalized-Phi blockers")
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE"}))
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    if not any(item.get("major_result_id") == "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE" for item in register["entries"]):
        register["entries"].append({
            "major_result_id": "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": action["major_result"]["what_is_closed"],
            "equation_or_mapping": action["major_result"]["equation_or_mapping"],
            "coefficient_provenance": action["major_result"].get("coefficient_provenance", {}),
            "units": action["major_result"]["units"],
            "derivation_class": action["major_result"]["derivation_class"],
            "observable": action["major_result"]["observable"],
            "data_role": action["major_result"]["data_role"],
            "evidence_artifacts": [evidence(ACTION_REL, {"status": action["status"]})],
            "verification_status": action["status"],
            "open_blockers": action["major_result"]["open_blockers"],
            "dependency_unlocked": action["major_result"]["dependency_unlocked"],
            "claim_boundary": action["major_result"]["claim_boundary"],
        })
    else:
        route_entry = next(
            item
            for item in register["entries"]
            if item.get("major_result_id") == "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE"
        )
        route_entry.update({
            "closure_level": action["major_result"]["closure_level"],
            "what_is_closed": action["major_result"]["what_is_closed"],
            "equation_or_mapping": action["major_result"]["equation_or_mapping"],
            "coefficient_provenance": action["major_result"].get("coefficient_provenance", {}),
            "units": action["major_result"]["units"],
            "derivation_class": action["major_result"]["derivation_class"],
            "observable": action["major_result"]["observable"],
            "data_role": action["major_result"]["data_role"],
            "verification_status": action["status"],
            "open_blockers": action["major_result"]["open_blockers"],
            "dependency_unlocked": action["major_result"]["dependency_unlocked"],
            "claim_boundary": action["major_result"]["claim_boundary"],
        })
        for item in route_entry.get("evidence_artifacts", []):
            if item.get("path") == ACTION_REL:
                item["sha256"] = digest(ACTION_REL)
    register["next_major_result"] = {
        "major_result_id": "T13_DIMENSIONAL_PHI_ENERGY_ANCHOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "controlling_blocker": "system_specific_SI_contract_and_covariant_Phi_to_normalized_Phi_map_missing",
        "source_route": "covariant action route is natural-unit only until field normalization and coefficient provenance are declared",
    }
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["covariant_action_si_anchor_route"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False})
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    log_marker = "### 2026-08-11 - Covariant action SI anchor route boundary"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: test whether the implemented covariant response action can currently provide an SI energy anchor for Topic 13.
- Added or changed: natural-unit action route audit, major-result register entry, Full Topic 13 evidence, dependency note, and this update-log record.
- Verified with: `{action['status']}`; natural-unit declarations, nonphysical default coefficient policy, open system-specific SI gate, and missing covariant-Phi-to-normalized-Phi map all match the source specification.
- Result closed: `T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE` is `CLOSED_FOR_LANE`; the covariant parent is identified as a conditional route, not an SI calibration.
- Still open: dimensionful field normalization, coefficient provenance, e0, base Phi-to-energy mapping, alpha_Phi_K, and full thermodynamic closure.
- Claim impact: no promotion; no natural-unit default was treated as a physical constant and Xie 2026 remains locked.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Covariant Action SI Anchor Route"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` action artifacts
- changed: added natural-unit/SI-anchor audit and synchronized Full Topic 13 result and dependency evidence
- verification: `{action['status']}` plus seven-test Topic 13 source/no-go/integration suite
- public-safety status: `partial`; no numeric SI anchor or calibration emitted
- current claim boundary: action route `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: define covariant field normalization and SI coefficient provenance before attempting e0
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({
        "status": "PASS_INTEGRATED_COVARIANT_ACTION_ROUTE",
        "major_result_id": "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE",
        "closure_level": "CLOSED_FOR_LANE",
        "full_topic13_status": full["status"],
        "full_gate_sha256": digest(FULL_REL),
        "register_sha256": digest(REGISTER_REL),
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
