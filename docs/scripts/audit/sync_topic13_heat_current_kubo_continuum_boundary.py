"""Integrate the Topic 13 heat-current continuum boundary result."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_continuum_boundary_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-17.md"
LANE_ID = "T13_UET_O2_HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY"
ANCHOR_ID = "T13_UET_O2_HEAT_CURRENT_KUBO_MATCH"


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


def lane_record(major: dict[str, Any], action_evidence: dict[str, Any]) -> dict[str, Any]:
    record = {
        field: major.get(field)
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
    return record


def main() -> int:
    action = load(ACTION_REL)
    expected_status = "PASS_SCOPED_HEAT_CURRENT_KUBO_CONTINUUM_NO_GO"
    if action.get("status") != expected_status:
        raise SystemExit(f"heat-current continuum boundary is not passing: {action.get('status')}")
    major = action.get("major_result")
    if not isinstance(major, dict) or major.get("major_result_id") != LANE_ID:
        raise SystemExit("heat-current continuum boundary major-result identity mismatch")

    today = date.today().isoformat()
    action_evidence = evidence(
        ACTION_REL,
        {"status": action["status"], "closure_level": major["closure_level"]},
    )

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major["what_is_closed"],
        "the declared heat-current cutoff/order sequence is closed as a scoped continuum no-go without extrapolation",
    )
    for blocker in major["open_blockers"]:
        append_unique(full_major["what_remains_open"], blocker)
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    state = action["state"]
    transport["heat_current_kubo_continuum_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": action["status"],
        "closure_level": major["closure_level"],
        "cutoff_factors": state["cutoff_factors"],
        "cutoff_kappa_natural": state["cutoff_kappa_natural"],
        "cutoff_relative_changes": state["cutoff_relative_changes"],
        "acceptance_threshold": state["acceptance_threshold"],
        "cutoff_maximum_relative_change": state["cutoff_maximum_relative_change"],
        "baseline_to_refined_relative_change": state["baseline_to_refined_relative_change"],
        "continuum_limit_completed": action["continuum_limit_completed"],
        "physical_kubo_coefficient_emitted": action["physical_kubo_coefficient_emitted"],
        "controlling_blocker": action["controlling_blocker"],
        "next_controller": action["next_controller"],
        "audit": action_evidence,
        "open_blockers": major["open_blockers"],
        "claim_boundary": major["claim_boundary"],
    }
    transport.pop("uet_o2_heat_current_kubo_continuum_boundary", None)
    full["claim_promotion"] = False
    full["next_action"] = (
        "Replace or analytically control the declared heat-current cutoff/order dependence, rerun the unchanged 1e-2 convergence gate, then source-lock physical units and uncertainty without promoting the finite-cutoff lane."
    )
    (ROOT / FULL_REL).write_text(
        json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(
        item
        for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    append_unique(
        full_entry["what_is_closed"],
        "the declared heat-current cutoff/order sequence is closed as a scoped continuum no-go without extrapolation",
    )
    for blocker in major["open_blockers"]:
        append_unique(full_entry["open_blockers"], blocker)
    append_unique(full_entry["evidence_artifacts"], action_evidence)
    record = lane_record(major, action_evidence)
    existing = next(
        (item for item in register["entries"] if item.get("major_result_id") == LANE_ID),
        None,
    )
    if existing is None:
        anchor_index = next(
            index
            for index, item in enumerate(register["entries"])
            if item.get("major_result_id") == ANCHOR_ID
        )
        register["entries"].insert(anchor_index + 1, record)
    else:
        existing.clear()
        existing.update(record)
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    register.setdefault("topic13_lane_sync", {})["heat_current_kubo_continuum_boundary"] = {
        "major_result_id": LANE_ID,
        "lane_artifact": {"path": ACTION_REL, "sha256": digest(ACTION_REL)},
        "full_gate": {"path": FULL_REL, "sha256": digest(FULL_REL)},
        "full_core_unlock": False,
    }
    (ROOT / REGISTER_REL).write_text(
        json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )

    dependency = load(DEPENDENCY_REL)
    register_hash = digest(REGISTER_REL)
    dependency["generated_at"] = today
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["register_sha256"] = register_hash
    partial["full_core_unlock"] = False
    partial.setdefault("lane_extensions", {})["heat_current_kubo_continuum_boundary"] = {
        "major_result_id": LANE_ID,
        "closure_level": major["closure_level"],
        "status": action["status"],
        "full_core_unlock": False,
        "audit": action_evidence,
    }
    (ROOT / DEPENDENCY_REL).write_text(
        json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )

    report_marker = "## Heat-Current Kubo Continuum Boundary (T13-110)"
    append_marker(
        REPORT_REL,
        report_marker,
        f"""{report_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: The declared heat-current cutoff sequence and an independent radial/quadrature refinement both fail the existing continuum acceptance gate. This closes the boundary of the current finite-cutoff scheme, not the physical transport problem.
WHAT_REMAINS_OPEN: A regularized or analytically controlled continuum heat-current scheme, renormalized off-shell self-energy, physical Kubo record, finite-temperature condensed two-fluid completion, dimensional Phi map, independent calibration, and Ding C_src remain open.
DEPENDENCY_UNLOCKED: Scoped no-go for this heat-current discretization only; the finite-cutoff lane remains available, but no continuum, physical Kubo, SI, TTG, Core, or Full Topic 13 dependency is unlocked.
STATUS: `{action['status']}`; physical closure remains `BLOCKED`.
WHAT_CHANGED: Added `{ACTION_REL}` and synchronized the full gate, closure register, dependency evidence, report, update log, and ledger.
EQUATION_OR_MAPPING: `kappa_natural=(1/3)Tr[(b_q^perp)^T L_cont^+ b_q^perp]`; `r_i=abs(kappa_i-kappa_(i-1))/max(abs(kappa_(i-1)),1e-300)`; continuum admission requires `max(r_i)<=1e-2`.
VERIFICATION: Cutoff responses are `{state['cutoff_kappa_natural']}`; maximum adjacent relative change is `{state['cutoff_maximum_relative_change']:.6g}` and baseline-to-refined change is `{state['baseline_to_refined_relative_change']:.6g}`, both above `0.01`. No extrapolation, physical coefficient, fit, target data, or Xie 2026 holdout was used.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}`.
NEXT_ACTION: Replace or analytically control the declared cutoff/order dependence, rerun the unchanged convergence gate, and only then evaluate physical Kubo/SI admission.
CLAIM_BOUNDARY: This is a scoped no-go for the declared finite-cutoff heat-current discretization; it is not a mathematical no-go for all future schemes, not a physical Kubo coefficient, and not Full Topic 13 closure.
""",
    )

    log_marker = "## 2026-08-17 - Heat-current Kubo continuum boundary (T13-110)"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: The declared heat-current cutoff sequence and independent order refinement fail the unchanged `1e-2` continuum gate.
WHAT_REMAINS_OPEN: A controlled continuum scheme, renormalized physical Kubo, condensed two-fluid transport, dimensional map, independent calibration, and Ding C_src.
DEPENDENCY_UNLOCKED: Heat-current continuum boundary only; no physical or downstream unlock.
STATUS: `{action['status']}` with physical closure `BLOCKED`.
WHAT_CHANGED: Added the heat-current continuum boundary module, audit artifact, regression test, and metadata synchronization.
EQUATION_OR_MAPPING: `kappa_natural=(1/3)Tr[(b_q^perp)^T L_cont^+ b_q^perp]`; adjacent relative change gate remains `1e-2`.
VERIFICATION: Maximum cutoff change `{state['cutoff_maximum_relative_change']:.6g}` and independent refinement change `{state['baseline_to_refined_relative_change']:.6g}` both fail; no extrapolation, fit, target, or holdout access.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}`.
NEXT_ACTION: Replace or analytically control cutoff/order dependence and rerun the same gate before physical promotion.
CLAIM_BOUNDARY: Scoped scheme-level no-go only; no global continuum impossibility or Full Topic 13 closure is claimed.
""",
    )

    ledger_marker = "## Topic 13 Heat-Current Kubo Continuum Boundary"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the heat-current cutoff/order boundary module, verifier artifact, regression test, and gate/register/dependency/report/log sync
- verification: `{action['status']}`; max cutoff change `{state['cutoff_maximum_relative_change']:.6g}`, independent refinement change `{state['baseline_to_refined_relative_change']:.6g}`, threshold `0.01`
- public-safety status: `partial`; no continuum or physical coefficient promotion
- current claim boundary: `{LANE_ID}` is `{major['closure_level']}`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated worktree changes were not edited
- next action: replace or analytically control heat-current cutoff/order dependence and rerun the unchanged gate
""",
    )

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_T13_HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY",
                "major_result_id": LANE_ID,
                "full_topic13_status": full["status"],
                "full_core_unlock": False,
                "full_gate_sha256": digest(FULL_REL),
                "register_sha256": digest(REGISTER_REL),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
