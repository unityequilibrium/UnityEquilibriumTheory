"""Synchronize the Topic 13 covariant field-normalization no-go into gates."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
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
    expected = "PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION"
    if action.get("status") != expected:
        raise SystemExit(f"field-normalization audit is not passing: {action.get('status')}")
    today = date.today().isoformat()
    controller = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    controller_detail = "physical_field_normalization_observable_and_SI_coefficient_provenance_or_independent_alpha_calibration_missing"
    next_action = "Source-lock a covariant field residue or response-observable amplitude with a system-specific SI coefficient/energy-density contract, or provide an independent non-TTG alpha_Phi_K calibration record; then derive base Phi-to-Phi_E without Xie 2026."

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"]["what_is_closed"], "covariant scalar field-rescaling redundancy is explicit; canonical field normalization cannot supply a physical SI anchor")
    full.setdefault("verification_status", {})["covariant_field_normalization_no_go"] = {
        "status": "PASS_SCOPED_NO_GO",
        "closure_level": "CLOSED_FOR_LANE",
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "audit": evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]}),
        "claim_boundary": action["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), evidence(ACTION_REL, {"status": action["status"], "data_role": action["major_result"]["data_role"]}))
    append_unique(full["major_result"]["what_remains_open"], controller)
    full["controlling_blocker"] = controller
    full["controlling_blocker_detail"] = controller_detail
    full["next_action"] = next_action
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "covariant scalar field-rescaling redundancy is explicit; canonical field normalization cannot supply a physical SI anchor")
    append_unique(full_entry["open_blockers"], controller)
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]}))
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    entry = next((item for item in register["entries"] if item.get("major_result_id") == action["major_result"]["major_result_id"]), None)
    if entry is None:
        register["entries"].append({
            "major_result_id": action["major_result"]["major_result_id"],
            "topic": action["major_result"]["topic"],
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": action["major_result"]["what_is_closed"],
            "equation_or_mapping": action["major_result"]["equation_or_mapping"],
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
    register["next_major_result"] = {
        "major_result_id": "T13_PHYSICAL_FIELD_NORMALIZATION_SI_ANCHOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "controlling_blocker": controller,
        "source_route": "the physical field normalization must be fixed by a source-locked observable residue/amplitude and SI contract, or bypassed only by an independent non-TTG alpha calibration",
    }
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["covariant_field_normalization_no_go"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False})
    partial["reason"] = "Lane-level no-gos and comparators make the missing physical normalization explicit; they do not supply e0, alpha_Phi_K, or full thermodynamic closure."
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    log_marker = "### 2026-08-11 - Covariant field-normalization identifiability no-go"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8-sig")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: determine whether the current natural-unit covariant response scalar can identify the physical field scale needed by Topic 13.
- Added or changed: field-rescaling witness, machine-readable no-go artifact, formula-audit record, Full Topic 13 gate evidence, register/dependency records, and regression tests.
- Verified with: `{action['status']}`; potential, kinetic term, curvature factor, and conditional normalized coordinate are invariant under the declared field rescaling. No target or Xie 2026 data is read.
- Result closed: `T13_COVARIANT_FIELD_NORMALIZATION_IDENTIFIABILITY_NO_GO` is `CLOSED_FOR_LANE`; canonicalizing the action does not yield a physical SI normalization.
- Still open: physical field residue or observable amplitude, system-specific SI coefficient/energy-density contract, base `Phi -> Phi_E`, `e0`, independent `alpha_Phi_K`, and full thermodynamic closure.
- Claim impact: no promotion. The Full Topic 13 gate remains `PARTIAL/BLOCKED` and no numerical calibration is emitted.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8-sig") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Covariant Field-Normalization No-Go"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` action artifacts
- changed: added the covariant field-rescaling no-go, formula record, tests, and synchronized gates/register/dependency state
- verification: `{action['status']}`; focused regression coverage is required before this wave is treated as complete
- public-safety status: `partial`; no field scale, `e0`, `alpha_Phi_K`, prediction, or holdout result was emitted
- current claim boundary: field-normalization no-go `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: source-lock the physical field normalization and SI coefficient contract, or acquire an independent non-TTG alpha calibration record
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({"status": "PASS_INTEGRATED_COVARIANT_FIELD_NORMALIZATION_NO_GO", "major_result_id": action["major_result"]["major_result_id"], "closure_level": "CLOSED_FOR_LANE", "full_topic13_status": full["status"], "full_gate_sha256": digest(FULL_REL), "register_sha256": digest(REGISTER_REL), "dependency_unlock": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
