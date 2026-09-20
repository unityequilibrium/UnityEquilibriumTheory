"""Integrate the scoped Phi-energy-anchor no-go into Topic 13 controls."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
NO_GO_REL = "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json"
UNITS_REL = "docs/core/07_artifacts/archive/uet_active_lane_units_observable_register.json"
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
    no_go = load(NO_GO_REL)
    if no_go.get("status") != "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR":
        raise SystemExit(f"no-go audit is not passing: {no_go.get('status')}")
    today = date.today().isoformat()

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(
        full["major_result"]["what_is_closed"],
        "scoped structural no-go for deriving e0 or numeric alpha_Phi_K from the current normalized Phi lane",
    )
    append_unique(
        full["major_result"]["what_remains_open"],
        "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
    )
    full.setdefault("verification_status", {})["phi_energy_anchor_identifiability"] = {
        "status": "PASS_SCOPED_NO_GO",
        "closure_level": "CLOSED_FOR_LANE",
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "target_or_holdout_used": False,
        "audit": evidence(
            NO_GO_REL,
            {
                "status": no_go["status"],
                "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
            },
        ),
        "claim_boundary": no_go["claim_boundary"],
    }
    append_unique(
        full.setdefault("evidence_artifacts", []),
        evidence(
            NO_GO_REL,
            {
                "status": no_go["status"],
                "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
            },
        ),
    )
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = (
        "Derive e0 and the base Phi-to-Delta_u_ph correspondence from a declared dimensionful action/free-energy origin, "
        "or obtain an independent measured energy-density/Phi-amplitude calibration; do not fit the anchor to TTG or read Xie 2026."
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(
        full_entry["what_is_closed"],
        "scoped structural no-go for deriving e0 or numeric alpha_Phi_K from the current normalized Phi lane",
    )
    append_unique(full_entry["open_blockers"], "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing")
    append_unique(
        full_entry["evidence_artifacts"],
        evidence(
            NO_GO_REL,
            {
                "status": no_go["status"],
                "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
            },
        ),
    )
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    if not any(item.get("major_result_id") == "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO" for item in register["entries"]):
        register["entries"].append({
            "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": no_go["major_result"]["what_is_closed"],
            "equation_or_mapping": no_go["major_result"]["equation_or_mapping"],
            "units": no_go["major_result"]["units"],
            "derivation_class": no_go["major_result"]["derivation_class"],
            "observable": no_go["major_result"]["observable"],
            "data_role": no_go["major_result"]["data_role"],
            "evidence_artifacts": [
                evidence(NO_GO_REL, {"status": no_go["status"]}),
                evidence(UNITS_REL, {"status": "normalized Phi lane declaration"}),
            ],
            "verification_status": no_go["status"],
            "open_blockers": no_go["major_result"]["open_blockers"],
            "dependency_unlocked": no_go["major_result"]["dependency_unlocked"],
            "claim_boundary": no_go["major_result"]["claim_boundary"],
        })
    register["next_major_result"] = {
        "major_result_id": "T13_DIMENSIONAL_PHI_ENERGY_ANCHOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "controlling_blocker": "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
        "source_route": "derive from a dimensionful action or obtain an independent energy/Phi calibration; no TTG fit",
    }
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["phi_energy_anchor_no_go"] = evidence(
        NO_GO_REL,
        {
            "status": no_go["status"],
            "full_core_unlock": False,
            "numeric_alpha_emitted": False,
        },
    )
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    log_marker = "### 2026-08-11 - Phi energy anchor identifiability no-go"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: test whether the current normalized Core `Phi` lane can identify a dimensionful `e0` or numeric `alpha_Phi_K` without an independent anchor.
- Added or changed: structural scale-witness audit/artifact, major-result register entry, Full Topic 13 evidence, dependency note, and this update-log record.
- Verified with: `{no_go['status']}`; normalized `Phi` rescaling, distinct alpha/e0 witnesses, Core unit declarations, open base mapping, and no-target/no-holdout checks all pass.
- Result closed: `T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO` is `CLOSED_FOR_LANE`; fitting `e0` or `alpha_Phi_K` from the normalized lane is explicitly rejected.
- Blocker narrowed: the next action is no longer an unconstrained search for a number; it is a declared dimensionful action/free-energy derivation or independent energy-density/Phi-amplitude calibration.
- Still open: actual `e0`, base `Phi -> Delta_u_ph`, independent `alpha_Phi_K`, Ding-specific `C_src`, and EOS/transport/KMS/entropy closure.
- Claim impact: no promotion. Full Topic 13 remains `PARTIAL / BLOCKED`, and Xie 2026 remains locked.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Phi Energy Anchor Identifiability No-Go"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` artifacts
- changed: added the normalized-Phi scale witness, no-go artifact, focused test, and full gate/register/dependency/update-log integration
- verification: `{no_go['status']}` plus focused Topic 13 source-lane regression; target and Xie 2026 holdout remain unused
- public-safety status: `partial`; this is an internal structural audit, not a numeric calibration
- current claim boundary: no-go is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: derive or independently source-lock the dimensionful Phi-energy anchor, without TTG fitting
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({
        "status": "PASS_INTEGRATED_PHI_ANCHOR_NO_GO",
        "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
        "closure_level": "CLOSED_FOR_LANE",
        "full_topic13_status": full["status"],
        "full_gate_sha256": digest(FULL_REL),
        "register_sha256": digest(REGISTER_REL),
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
