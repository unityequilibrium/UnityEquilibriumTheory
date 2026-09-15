"""Synchronize the Topic 13 causal branch-selection major result."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
CURRENT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
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


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def main() -> int:
    action = load(ACTION_REL)
    expected = "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH"
    if action.get("status") != expected:
        raise SystemExit(f"causal branch-selection audit is not passing: {action.get('status')}")
    today = date.today().isoformat()

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"]["what_is_closed"], "scoped conserved-gradient no-go plus named coupled flux-telegraph causal branch selection")
    full.setdefault("verification_status", {})["causal_branch_selection"] = {
        "status": "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH",
        "closure_level": "CLOSED_FOR_LANE",
        "baseline_full_candidate_pass": False,
        "baseline_replaced": False,
        "audit": evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]}),
        "claim_boundary": action["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), evidence(ACTION_REL, {"status": action["status"], "data_role": action["major_result"]["data_role"]}))
    # Keep the named-lane controller nested in verification_status. The full
    # result already exposes the dimensional-map blocker that owns this
    # dependency, so copying the lane wording into what_remains_open would
    # double-count the same unresolved requirement.
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "scoped conserved-gradient no-go plus named coupled flux-telegraph causal branch selection")
    append_unique(full_entry["open_blockers"], action["controlling_blocker"])
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]}))
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)

    flux_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_CAUSAL_FLUX_TELEGRAPH_BRANCH")
    obsolete = {"full coupled Phi integration", "full-candidate leakage rerun"}
    flux_entry["open_blockers"] = [item for item in flux_entry["open_blockers"] if item not in obsolete]
    for blocker in (
        "original kappa_C>0 conserved-gradient baseline remains blocked by scoped no-go",
        "selected branch remains normalized and has no dimensional thermal mapping",
        "full Topic 13 bridge components remain open",
    ):
        append_unique(flux_entry["open_blockers"], blocker)
    flux_entry["dependency_unlocked"] = "coupled C/Phi lane is verified separately; no SI or full Topic 13 dependency unlock"

    result_id = action["major_result"]["major_result_id"]
    if not any(item.get("major_result_id") == result_id for item in register["entries"]):
        register["entries"].append({
            "major_result_id": result_id,
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
    else:
        existing_entry = next(item for item in register["entries"] if item.get("major_result_id") == result_id)
        existing_entry["closure_level"] = action["major_result"]["closure_level"]
        existing_entry["what_is_closed"] = action["major_result"]["what_is_closed"]
        existing_entry["equation_or_mapping"] = action["major_result"]["equation_or_mapping"]
        existing_entry["units"] = action["major_result"]["units"]
        existing_entry["derivation_class"] = action["major_result"]["derivation_class"]
        existing_entry["observable"] = action["major_result"]["observable"]
        existing_entry["data_role"] = action["major_result"]["data_role"]
        existing_entry["verification_status"] = action["status"]
        existing_entry["open_blockers"] = action["major_result"]["open_blockers"]
        existing_entry["dependency_unlocked"] = action["major_result"]["dependency_unlocked"]
        existing_entry["claim_boundary"] = action["major_result"]["claim_boundary"]
        existing_entry["evidence_artifacts"] = [evidence(ACTION_REL, {"status": action["status"]})]
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["causal_branch_selection"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False, "baseline_replaced": False})
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    current_marker = "## 2026-08-11 Causal Branch Selection Update"
    current_path = ROOT / CURRENT_REL
    current = current_path.read_text(encoding="utf-8-sig")
    if current_marker not in current:
        current += f"""

{current_marker}

MAJOR_RESULT_CLOSURE: `T13_CAUSAL_THERMAL_BRANCH_SELECTION` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The original conserved-gradient baseline is a scoped high-k no-go, while the named coupled conserved-flux/C-Phi branch passes the locked compact-support, arrival, ledger, convergence, and anti-manipulation gates.

WHAT_REMAINS_OPEN: The selected causal branch is normalized; the SI `Phi` scale, source package, `alpha_Phi_K`, bridge, EOS, transport, SK/KMS, entropy, and balance requirements remain open.

DEPENDENCY_UNLOCKED: Normalized causal input only; no full Topic 13 or downstream Core dependency.

STATUS: `PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH` for branch selection; Full Topic 13 remains `PARTIAL/BLOCKED`.

WHAT_CHANGED: Linked the baseline no-go and the passing named branches as one major-result record and removed the obsolete standalone-flux note that said coupled integration was still pending.

EQUATION_OR_MAPPING: `C_t + partial_x J_C = 0`; `tau_C J_C_t + J_C = -M_C partial_x(mu_C)`; `tau_Phi Phi_tt + Phi_t + M_Phi mu_Phi = 0` in the named normalized branch.

VERIFICATION: The original baseline remains above `1e-6`; the selected coupled lane has zero measured pre-arrival leakage, nonzero arrivals, energy residual below `1e-6`, no clipping, no cone padding, no parameter fit, and no Xie 2026 access.

CONTROLLING_BLOCKER: `selected_causal_branch_is_normalized_and_dimensional_thermal_bridge_remains_open`.

NEXT_ACTION: Independently close the dimensional and thermodynamic bridge without relabeling the failed baseline.

CLAIM_BOUNDARY: No SI thermal mapping, external validation, covariant completion, or global closure follows from the named branch.
"""
        current_path.write_text(current, encoding="utf-8")

    log_marker = "### 2026-08-11 - Causal branch selection closure"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8-sig")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: consolidate the declared conserved-C no-go and passing named flux/C-Phi branch into one major causal decision.
- Added or changed: causal branch-selection audit, major-result record, full-gate/dependency evidence, current-state note, tests, and a correction to the flux branch's obsolete pending-coupling wording.
- Verified with: `{action['status']}`; the baseline still fails its locked `1e-6` leakage threshold, while the coupled branch passes compact support, arrival, mass, energy, convergence, no-clipping, no-padding, no-fit, and holdout checks.
- Result closed: `T13_CAUSAL_THERMAL_BRANCH_SELECTION` is `CLOSED_FOR_LANE`.
- Still open: dimensional Phi/energy mapping, source and independent alpha records, non-circular bridge, EOS, transport, SK/KMS, entropy, and balance closure.
- Claim impact: no promotion and no substitution. The full Topic 13 result remains `PARTIAL/BLOCKED`.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8-sig") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Causal Branch Selection"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` causal artifacts
- changed: consolidated the preserved conserved-C no-go with the passing named flux/C-Phi causal branch; corrected stale flux-branch dependency wording
- verification: `{action['status']}`; focused branch-selection tests are required before this wave is complete
- public-safety status: `partial`; named branch is normalized/internal and no SI mapping or external data claim was added
- current claim boundary: causal selection `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: close physical field normalization or independent alpha, then the remaining thermodynamic bridge components
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({"status": "PASS_INTEGRATED_T13_CAUSAL_BRANCH_SELECTION", "major_result_id": result_id, "closure_level": "CLOSED_FOR_LANE", "full_topic13_status": full["status"], "full_gate_sha256": digest(FULL_REL), "register_sha256": digest(REGISTER_REL), "dependency_unlock": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
