"""Integrate the Topic 13 transport/KMS/entropy status boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_transport_kms_entropy_status_boundary_audit.json"
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
    if action.get("status") != "PASS_SCOPED_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY":
        raise SystemExit(f"transport status boundary is not passing: {action.get('status')}")
    major = action["major_result"]
    today = date.today().isoformat()

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major["what_is_closed"], "transport/KMS/entropy structural and formal status boundary with physical closure kept blocked")
    for blocker in major["open_blockers"]:
        append_unique(full_major["what_remains_open"], blocker)
    transport_gate = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport_gate["transport_kms_entropy_status_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": action["status"],
        "closure_level": major["closure_level"],
        "structural_lane_status": "PASS",
        "physical_closure_status": action["physical_closure_status"],
        "controlling_blocker": action["controlling_blocker"],
        "open_blockers": major["open_blockers"],
        "audit": evidence(ACTION_REL, {"status": action["status"], "closure_level": major["closure_level"]}),
        "claim_boundary": major["claim_boundary"],
    }
    full["claim_promotion"] = False
    full["next_action"] = "Acquire a state-matched physical Kubo record or microscopic interacting SK match, then close the finite-temperature normal sector and dimensional Phi-to-thermal map; retain the formal lanes as nonphysical evidence."
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "transport/KMS/entropy structural and formal status boundary with physical closure kept blocked")
    for blocker in major["open_blockers"]:
        append_unique(full_entry["open_blockers"], blocker)
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": major["major_result_id"]}))
    entry = next((item for item in register["entries"] if item.get("major_result_id") == major["major_result_id"]), None)
    record = {key: major[key] for key in ("major_result_id", "topic", "closure_level", "what_is_closed", "equation_or_mapping", "units", "derivation_class", "observable", "data_role", "evidence_artifacts", "verification_status", "open_blockers", "dependency_unlocked", "claim_boundary")}
    record["evidence_artifacts"] = [evidence(ACTION_REL, {"status": action["status"]})]
    if entry is None:
        register["entries"].append(record)
    else:
        entry.clear()
        entry.update(record)
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["transport_kms_entropy_status_boundary"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False, "closure_level": major["closure_level"]})
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    report_marker = "## Transport/KMS/Entropy Status Boundary (T13-107)"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`

WHAT_IS_ACTUALLY_CLOSED: The conservative-action identifiability question is
closed as a scoped no-go. The formal local/open-system SK/KMS/FDT interfaces,
natural-unit covariant heat-flux and entropy-current balance, and physical
Kubo admission schema are separately verified. These are named lanes, not a
physical transport result.

WHAT_REMAINS_OPEN: `physical_Kubo_coefficient_record_missing`,
`finite_temperature_normal_component_not_derived`,
`microscopic_interacting_SK_match_missing`,
`dimensional_Phi_to_thermal_observable_map_missing`, and
`curved_3p1_transport_solver_missing` remain open.

DEPENDENCY_UNLOCKED: Structural/formal transport, KMS, entropy, and heat-flux
lanes only. No physical transport, Full Topic 13, Core, Gravity, or external
validation dependency is unlocked.

STATUS: `{action['status']}`; physical closure remains `BLOCKED`.

WHAT_CHANGED: Added `{ACTION_REL}` and synchronized the full gate, closure
register, dependency evidence, this report, the update log, and the ledger.

EQUATION_OR_MAPPING: `J_diss^A=-L^(AB)X_B`; `nabla_mu J_S^mu=X_A L^(AB)X_B>=0`;
`N(omega)=coth(beta_th omega/2)*2 Im D_R`; `q^mu=kappa_natural*X_T^mu`.

VERIFICATION: Structural no-go, formal SK/KMS/FDT, open-system positivity,
natural-unit covariant entropy balance, and physical-coefficient admission
checks pass. No physical coefficient, fit, target tuning, or locked holdout
was used.

CONTROLLING_BLOCKER: `{action['controlling_blocker']}` for this lane.

NEXT_ACTION: Acquire a state-matched physical Kubo record or microscopic
interacting SK/influence-functional match, then close the finite-temperature
normal sector and dimensional Phi-to-thermal map.

CLAIM_BOUNDARY: This is a scoped status boundary and formal-lane result. It is
not a physical Kubo measurement, complete two-fluid transport theory, SI Phi
calibration, TTG prediction, external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "## 2026-08-17 - Transport/KMS/entropy status boundary (T13-107)"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: Structural conservative-action no-go, formal SK/KMS/FDT lanes, natural-unit covariant entropy/heat-flux balance, and physical Kubo admission boundary.
WHAT_REMAINS_OPEN: Physical Kubo record, finite-temperature normal sector, microscopic interacting SK match, dimensional Phi map, and curved 3+1 transport.
DEPENDENCY_UNLOCKED: Structural/formal lane only; no physical transport or downstream dependency unlock.
STATUS: `{action['status']}` with physical closure `BLOCKED`.
WHAT_CHANGED: Added the machine-readable status-boundary artifact and synchronized gate/register/dependency/report.
EQUATION_OR_MAPPING: `J_diss^A=-L^(AB)X_B`; `nabla_mu J_S^mu>=0`; KMS/FDT and covariant heat-flux balance remain formal/natural-unit lanes.
VERIFICATION: All boundary checks pass; no fit, target data, physical coefficient, or Xie 2026 holdout was consumed.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}`.
NEXT_ACTION: Obtain matched physical Kubo or microscopic SK evidence and complete the remaining physical dependencies.
CLAIM_BOUNDARY: No promotion to physical transport or Full Topic 13 closure.
""",
    )

    ledger_marker = "## Topic 13 Transport/KMS/Entropy Status Boundary"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added `{ACTION_REL}` and synchronized full gate, closure register, dependency evidence, report, and update log
- verification: `{action['status']}`; physical coefficient remains blocked and no holdout was consumed
- public-safety status: `partial`; formal/structural lanes only
- current claim boundary: `{major['major_result_id']}` is `{major['closure_level']}`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated changes were not edited
- next action: acquire state-matched physical Kubo or microscopic SK evidence
""",
    )

    print(json.dumps({"status": "PASS_INTEGRATED_T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY", "full_topic13_status": full["status"], "full_core_unlock": False, "full_gate_sha256": digest(FULL_REL), "register_sha256": digest(REGISTER_REL)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
