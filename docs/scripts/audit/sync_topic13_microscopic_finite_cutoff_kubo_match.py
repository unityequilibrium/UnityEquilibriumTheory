"""Integrate the finite-cutoff microscopic Kubo matching lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_microscopic_finite_cutoff_kubo_match_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-17.md"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def append_marker(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def main() -> int:
    action = load(ACTION_REL)
    if action.get("status") != "PASS_ACTION_MATCHED_MICROSCOPIC_FINITE_CUTOFF_KUBO_LANE":
        raise SystemExit(f"microscopic Kubo lane is not passing: {action.get('status')}")
    major = action["major_result"]
    today = date.today().isoformat()

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major["what_is_closed"], "finite-cutoff action-matched contact-SK, Bethe-Salpeter, charged-current KMS/FDT, and entropy response lane is closed without SI or continuum promotion")
    for blocker in major["open_blockers"]:
        append_unique(full_major["what_remains_open"], blocker)
    transport = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport["microscopic_finite_cutoff_kubo_match"] = {
        "major_result_id": major["major_result_id"],
        "status": action["status"],
        "closure_level": major["closure_level"],
        "physical_closure_status": action["physical_closure_status"],
        "finite_cutoff": action["state"]["finite_cutoff"],
        "dc_response": action["state"]["dc_response"],
        "microscopic_bethe_salpeter_match_completed": action["state"]["microscopic_bethe_salpeter_match_completed"],
        "microscopic_sk_kms_match_completed": action["state"]["microscopic_sk_kms_match_completed"],
        "audit": evidence(ACTION_REL, {"status": action["status"], "closure_level": major["closure_level"]}),
        "open_blockers": major["open_blockers"],
        "claim_boundary": major["claim_boundary"],
    }
    full["claim_promotion"] = False
    full["next_action"] = "Complete the continuum and renormalized retarded self-energy match, then source-lock the dimensional Phi map and independent calibration; keep this finite-cutoff Kubo lane non-SI."
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "finite-cutoff action-matched contact-SK, Bethe-Salpeter, charged-current KMS/FDT, and entropy response lane is closed without SI or continuum promotion")
    for blocker in major["open_blockers"]:
        append_unique(full_entry["open_blockers"], blocker)
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": major["major_result_id"]}))
    record = {key: major[key] for key in ("major_result_id", "topic", "closure_level", "what_is_closed", "equation_or_mapping", "units", "derivation_class", "observable", "data_role", "evidence_artifacts", "verification_status", "open_blockers", "dependency_unlocked", "claim_boundary")}
    record["evidence_artifacts"] = [evidence(ACTION_REL, {"status": action["status"]})]
    existing = next((item for item in register["entries"] if item.get("major_result_id") == major["major_result_id"]), None)
    if existing is None:
        register["entries"].append(record)
    else:
        existing.clear()
        existing.update(record)
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["microscopic_finite_cutoff_kubo_match"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False, "closure_level": major["closure_level"]})
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    marker = "## Microscopic Finite-Cutoff Kubo Match (T13-108)"
    append_marker(REPORT_REL, marker, f"""{marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: The contact-SK quartic vertex, exact transition kernel, conservative finite-cutoff operator, charged retarded response, KMS/FDT ratios, and entropy witness are matched at one declared state.
WHAT_REMAINS_OPEN: Continuum limit, loop-renormalized off-shell self-energy, physical SI Kubo promotion, finite-temperature two-fluid completion, dimensional Phi map, independent alpha calibration, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Finite-cutoff microscopic Kubo matching lane only; no physical transport, Full Topic 13, Core, Gravity, or external-validation dependency is unlocked.
STATUS: `{action['status']}`; physical closure remains `BLOCKED`.
WHAT_CHANGED: Added `{ACTION_REL}` and synchronized the full gate, closure register, dependency evidence, this report, the update log, and the ledger.
EQUATION_OR_MAPPING: `G_R^JJ(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp`; `K_DC=Re G_R^JJ(0)` on the finite-cutoff natural-unit lane; `G^>/G^<=exp(beta*omega)`.
VERIFICATION: Contact cross-section, transition-rate, Bethe-Salpeter, KMS/FDT, Ward/conservation, PSD, and entropy checks pass. No physical SI coefficient, fit, target data, or Xie 2026 holdout was used.
CONTROLLING_BLOCKER: `continuum_limit_and_physical_kubo_promotion_missing`.
NEXT_ACTION: Complete the continuum and renormalized retarded self-energy match, then close the dimensional Phi map and independent calibration without promoting this finite-cutoff result.
CLAIM_BOUNDARY: This is an action-matched finite-cutoff natural-unit lane, not a continuum-limit or SI transport coefficient and not Full Topic 13 closure.
""")

    log_marker = "## 2026-08-17 - Microscopic finite-cutoff Kubo match (T13-108)"
    append_marker(LOG_REL, log_marker, f"""{log_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: Contact-SK, exact transition, conservative Bethe-Salpeter, charged-current KMS/FDT, and entropy matching at one finite cutoff.
WHAT_REMAINS_OPEN: Continuum/renormalized physical Kubo, finite-temperature two-fluid closure, dimensional Phi map, independent alpha calibration, and Ding C_src.
DEPENDENCY_UNLOCKED: Finite-cutoff microscopic lane only; no physical or downstream unlock.
STATUS: `{action['status']}` with physical closure `BLOCKED`.
WHAT_CHANGED: Added the matching implementation, verifier artifact, regression test, and synchronized metadata.
EQUATION_OR_MAPPING: `G_R^JJ=b_perp^T*(L-i*omega*I)^(-1)*b_perp`; KMS/FDT and entropy are evaluated from the same operator.
VERIFICATION: All matching checks pass; finite cutoff, natural units, no-fit, and holdout boundaries are explicit.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}`.
NEXT_ACTION: Complete continuum and renormalized retarded matching before physical promotion.
CLAIM_BOUNDARY: No SI transport or Full Topic 13 closure is claimed.
""")

    ledger_marker = "## Topic 13 Microscopic Finite-Cutoff Kubo Match"
    append_marker(LEDGER_REL, ledger_marker, f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the finite-cutoff matching module, audit artifact, test, and synchronized gate/register/dependency/report/log
- verification: `{action['status']}`; physical SI closure remains blocked and no holdout was consumed
- public-safety status: `partial`; natural-unit finite-cutoff lane only
- current claim boundary: `{major['major_result_id']}` is `{major['closure_level']}`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated changes were not edited
- next action: complete continuum and renormalized physical Kubo matching, then dimensional/source closure
""")

    print(json.dumps({"status": "PASS_INTEGRATED_T13_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH", "full_topic13_status": full["status"], "full_core_unlock": False, "full_gate_sha256": digest(FULL_REL), "register_sha256": digest(REGISTER_REL)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
