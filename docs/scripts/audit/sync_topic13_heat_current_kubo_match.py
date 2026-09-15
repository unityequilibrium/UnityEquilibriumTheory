"""Integrate the state-matched heat-current Kubo lane into Topic 13 metadata."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_match_audit.json"
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


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def append_marker(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    action = load(ACTION_REL)
    expected_status = "PASS_ACTION_MATCHED_FINITE_CUTOFF_HEAT_CURRENT_KUBO_LANE"
    if action.get("status") != expected_status:
        raise SystemExit(f"heat-current Kubo lane is not passing: {action.get('status')}")
    major = action["major_result"]
    if major.get("major_result_id") != "T13_UET_O2_HEAT_CURRENT_KUBO_MATCH":
        raise SystemExit("heat-current Kubo major-result identity mismatch")
    today = date.today().isoformat()
    action_evidence = evidence(ACTION_REL, {"status": action["status"], "closure_level": major["closure_level"]})

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major["what_is_closed"],
        "state-matched finite-cutoff retarded heat-current response matches the covariant natural moment lane without SI or continuum promotion",
    )
    for blocker in major["open_blockers"]:
        append_unique(full_major["what_remains_open"], blocker)
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    transport["heat_current_kubo_match"] = {
        "major_result_id": major["major_result_id"],
        "status": action["status"],
        "closure_level": major["closure_level"],
        "finite_cutoff": action["state"]["finite_cutoff"],
        "kappa_natural": action["state"]["kappa_natural"],
        "dc_matrix_relative_residual": action["state"]["dc_matrix_relative_residual"],
        "dc_scalar_relative_residual": action["state"]["dc_scalar_relative_residual"],
        "retarded_heat_current_match_completed": action["state"]["retarded_heat_current_match_completed"],
        "physical_kubo_coefficient_emitted": action["state"]["physical_kubo_coefficient_emitted"],
        "audit": action_evidence,
        "open_blockers": major["open_blockers"],
        "claim_boundary": major["claim_boundary"],
    }
    transport.pop("uet_o2_heat_current_kubo_match", None)
    full["claim_promotion"] = False
    full["next_action"] = (
        "Complete the continuum and renormalized heat-current retarded match, then source-lock physical units and uncertainty; retain this natural finite-cutoff lane as non-SI."
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(
        full_entry["what_is_closed"],
        "state-matched finite-cutoff retarded heat-current response matches the covariant natural moment lane without SI or continuum promotion",
    )
    for blocker in major["open_blockers"]:
        append_unique(full_entry["open_blockers"], blocker)
    append_unique(full_entry["evidence_artifacts"], action_evidence)
    record = {
        field: major[field]
        for field in (
            "major_result_id",
            "topic",
            "closure_level",
            "what_is_closed",
            "equation_or_mapping",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "open_blockers",
            "dependency_unlocked",
            "claim_boundary",
        )
    }
    record["evidence_artifacts"] = [action_evidence]
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
    register_hash = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["register_sha256"] = register_hash
    partial["full_core_unlock"] = False
    partial.setdefault("lane_extensions", {})["heat_current_kubo_match"] = {
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "status": action["status"],
        "full_core_unlock": False,
        "audit": action_evidence,
    }
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    report_marker = "## State-Matched Heat-Current Kubo (T13-109)"
    append_marker(
        REPORT_REL,
        report_marker,
        f"""{report_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: The Landau-frame heat-current source, the shared finite-cutoff collision operator, the retarded heat-current matrix, and the zero-frequency match to the existing covariant `kappa_natural` response are consistent at one declared normal state.
WHAT_REMAINS_OPEN: Continuum limit, renormalized physical self-energy, physical/SI Kubo record, condensed two-fluid transport, dimensional Phi map, independent calibration, and Ding C_src remain open.
DEPENDENCY_UNLOCKED: State-matched finite-cutoff natural-unit heat-current Kubo lane only; no physical transport, SI, alpha, TTG, Core, or Full Topic 13 unlock.
STATUS: `{action['status']}`; physical closure remains `BLOCKED`.
WHAT_CHANGED: Added `{ACTION_REL}` and synchronized full gate, closure register, dependency evidence, report, update log, and ledger.
EQUATION_OR_MAPPING: `b_q^i=(E-h*q)(p^i/E)sqrt(w)`; `G_R^qq(omega)=b_q^T(L_cont-i*omega*I)^(-1)b_q`; `Re G_R^qq(0)=K_qq`.
VERIFICATION: DC matrix/scalar residuals are below `1e-10`; shared-state KMS/FDT, PSD, source projection, and entropy checks pass. No SI coefficient, fit, target data, or Xie 2026 holdout was used.
CONTROLLING_BLOCKER: `continuum_limit_and_physical_heat_Kubo_promotion_missing`.
NEXT_ACTION: Complete the continuum and renormalized heat-current match, then source-lock physical units and uncertainty without promoting this natural lane.
CLAIM_BOUNDARY: This is an action-matched finite-cutoff natural-unit heat-current lane, not a continuum-limit or SI transport coefficient and not Full Topic 13 closure.
""",
    )

    log_marker = "## 2026-08-17 - State-matched heat-current Kubo (T13-109)"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: The heat-current retarded response at finite cutoff matches the existing covariant natural moment response at the same state and operator.
WHAT_REMAINS_OPEN: Continuum/renormalized physical Kubo, condensed two-fluid completion, dimensional map, independent calibration, and Ding C_src.
DEPENDENCY_UNLOCKED: Heat-current matching lane only; no physical or downstream unlock.
STATUS: `{action['status']}` with physical closure `BLOCKED`.
WHAT_CHANGED: Added the heat-current matching module, verifier, artifact, regression test, and metadata sync.
EQUATION_OR_MAPPING: `Re G_R^qq(0)=K_qq=(b_q^perp)^T L_cont^+ b_q^perp`; KMS/FDT uses the same response.
VERIFICATION: State match, DC residual, KMS/FDT, PSD, conserved-source projection, no-fit, and holdout checks pass.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}`.
NEXT_ACTION: Complete continuum and renormalized matching before any physical/SI promotion.
CLAIM_BOUNDARY: No SI transport or Full Topic 13 closure is claimed.
""",
    )

    ledger_marker = "## Topic 13 State-Matched Heat-Current Kubo"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the state-matched heat-current Kubo module, verifier, artifact, test, and gate/register/dependency/report/log sync
- verification: `{action['status']}`; finite-cutoff natural units only, physical coefficient remains blocked, no holdout consumed
- public-safety status: `partial`
- current claim boundary: `{major['major_result_id']}` is `{major['closure_level']}`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated worktree changes were not edited
- next action: complete continuum and renormalized physical heat-current matching
""",
    )

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_HEAT_CURRENT_KUBO_MATCH",
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "full_gate_sha256": digest(FULL_REL),
        "register_sha256": digest(REGISTER_REL),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
