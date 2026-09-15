"""Integrate the thermal one-loop UV boundary without promoting physics."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_uv_boundary_audit.json"
MODULE_REL = "docs/core/uet_o2_one_loop_normal_branch.py"
COMPARATOR_REL = "docs/core/standard_o2_finite_temperature_comparator.py"
BRANCH_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json"
CONVERGENCE_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_convergence_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-12.md"


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
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


def append_marker(rel: str, marker: str, content: str) -> None:
    path = ROOT / rel
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    audit = load(AUDIT_REL)
    if audit.get("status") != "PASS_THERMAL_UV_BOUNDARY":
        raise SystemExit(f"thermal UV boundary audit is not passing: {audit.get('status')}")
    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "vacuum_counterterm_and_renormalized_one_loop_response_not_closed"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })
    module_evidence = evidence(MODULE_REL, {
        "role": "thermal-only one-loop implementation with vacuum term excluded",
        "sha256_source_of_audit": audit["source_hashes"][MODULE_REL],
    })
    comparator_evidence = evidence(COMPARATOR_REL, {
        "role": "standard thermal integral and explicit zero-point exclusion",
        "sha256_source_of_audit": audit["source_hashes"][COMPARATOR_REL],
    })
    branch_evidence = evidence(BRANCH_REL, {
        "status": "PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE",
        "vacuum_counterterm_included": False,
    })
    convergence_evidence = evidence(CONVERGENCE_REL, {
        "status": "PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE",
        "reference": audit["reference"],
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "thermal-only one-loop UV tail and explicit vacuum-renormalization boundary")
    append_unique(full_major.setdefault("what_remains_open", []), "the UV boundary does not provide vacuum counterterms or a renormalized one-loop response")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["uet_o2_one_loop_uv_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "thermal_tail": audit["thermal_tail"],
        "vacuum_boundary": audit["vacuum_boundary"],
        "checks": audit["checks"],
        "audit": audit_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    append_unique(full["evidence_artifacts"], audit_evidence)
    full.setdefault("data_role", {})["uet_o2_one_loop_uv_boundary"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Acquire independent base-Phi SI calibration and physical Kubo evidence; retain the thermal-only UV boundary until a source-backed vacuum renormalization contract exists."
    full["claim_promotion"] = False
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    record = {key: major[key] for key in (
        "major_result_id", "topic", "closure_level", "what_is_closed",
        "equation_or_mapping", "units", "derivation_class", "observable",
        "data_role", "verification_status", "open_blockers",
        "dependency_unlocked", "claim_boundary",
    )}
    record["evidence_artifacts"] = [
        audit_evidence,
        module_evidence,
        comparator_evidence,
        branch_evidence,
        convergence_evidence,
    ]
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "thermal-only one-loop UV scope and explicit renormalization boundary")
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_one_loop_uv_boundary"] = audit_evidence
    partial["uet_o2_one_loop_uv_boundary_controller"] = blocker
    partial["uet_o2_one_loop_uv_boundary_max_relative_tail_bound"] = max(audit["thermal_tail"]["relative_to_reference"].values())
    partial["uet_o2_one_loop_uv_boundary_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## One-Loop Thermal UV Boundary (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-029` | `-log(1-exp(-x)) <= exp(-x)/(1-exp(-x))`; `I_0(Lambda) >= Lambda^4/(8 pi^2)`; `I_1(Lambda) >= (Lambda^2-m^2)/(4 sqrt(2) pi^2)` | `{AUDIT_REL}`; `{MODULE_REL}`; `{COMPARATOR_REL}` | natural-unit thermal observables and unweighted vacuum mode-integral diagnostics | analytic tail inequality and cutoff lower bounds; no counterterm constant supplied | thermal-only UV scope passes; vacuum renormalization remains open | prevents convergent thermal tails from being mistaken for a renormalized full one-loop action | omitted vacuum term could be silently treated as finite or renormalized | derive a source-backed counterterm/renormalization contract or retain the thermal-only boundary explicitly |

The audit closes the scope boundary, not the vacuum theory.  The thermal tail
is exponentially bounded on the normal branch; the omitted zero-point term has
recorded cutoff-growth lower bounds and is not used as a prediction.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## One-Loop Thermal UV Boundary"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The thermal-only one-loop normal branch has an explicit
UV scope boundary. Its Bose-log and occupation tails are analytically bounded
above on the declared normal branch, and the omitted vacuum/zero-point term is
separately recorded as a divergent, not-yet-renormalized contribution.

WHAT_REMAINS_OPEN: No vacuum counterterm, renormalized one-loop response,
interacting finite-temperature self-energy, condensate/two-fluid completion,
physical Kubo coefficient, SI Phi map, or `alpha_Phi_K` is supplied.

DEPENDENCY_UNLOCKED: Thermal-only UV scope control and a machine-readable
renormalization blocker. No physical transport, Full Topic 13, Core, or Gravity
dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` records the thermal tail bounds, vacuum cutoff-growth
boundary, source hashes, explicit exclusion policy, and holdout contract; this
sync links it into the full gate, register, dependency gate, formula audit,
update log, and ledger.

EQUATION_OR_MAPPING:

```text
-log(1-exp(-x)) <= exp(-x)/(1-exp(-x))
n_B(x) <= exp(-x)/(1-exp(-x))
I_0(Lambda) >= Lambda^4/(8 pi^2)
I_1(Lambda) >= (Lambda^2 - m_eff^2)/(4 sqrt(2) pi^2)
```

VERIFICATION: The maximum thermal-tail bound relative to the declared
reference outputs is `{max(audit["thermal_tail"]["relative_to_reference"].values()):.3e}`;
the convergence, branch, ontology, and holdout checks pass. The vacuum term is
not included and no renormalized action is claimed.

CONTROLLING_BLOCKER: `{blocker}`; the independent base-Phi SI anchor and
`alpha_Phi_K` remain the Full Topic 13 controller.

NEXT_ACTION: Acquire or derive a source-backed vacuum renormalization contract
without inventing counterterms, while separately pursuing physical Kubo and
independent base-Phi calibration evidence.

CLAIM_BOUNDARY: This closes only the thermal-only UV scope and blocker boundary.
It is not a renormalization proof, physical transport result, SI calibration,
external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - One-loop thermal UV boundary"
    log_content = f"""{log_marker}

- Scope: separate thermal-tail control from the omitted vacuum/zero-point renormalization layer.
- Added or changed: `{AUDIT_REL}`, thermal exponential-tail bounds, vacuum cutoff-growth diagnostics, full-gate/register/dependency integration, formula audit, report, and ledger.
- Verified with: `{audit["status"]}`; maximum relative thermal-tail bound `{max(audit["thermal_tail"]["relative_to_reference"].values()):.3e}`; no holdout or alpha fit.
- Result closed: `T13_UET_O2_ONE_LOOP_THERMAL_UV_BOUNDARY` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the thermal-only scope is controlled; `{blocker}` remains open and is not hidden by numerical convergence.
- Still open: counterterm/renormalized response, interacting finite-T sector, condensate/two-fluid sector, physical Kubo, SI Phi map, alpha, and Full Topic 13 closure.
- Next controller: obtain a source-backed renormalization contract or retain the boundary; independently acquire physical Kubo and base-Phi calibration evidence.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 One-Loop Thermal UV Boundary"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` O(2) one-loop thermal branch and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added thermal UV-boundary audit with exponential-tail bounds and explicit vacuum divergence boundary; synchronized full gate, register, dependency gate, formula audit, report, and update log
- verification: `{audit["status"]}`; maximum relative tail bound `{max(audit["thermal_tail"]["relative_to_reference"].values()):.3e}`; no counterterm or holdout claim
- public-safety status: `partial`; this is a scope/renormalization boundary, not a renormalized physical result
- current claim boundary: `T13_UET_O2_ONE_LOOP_THERMAL_UV_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: source-lock or derive renormalization without invented constants; acquire physical Kubo and independent base-Phi SI evidence
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_THERMAL_UV_BOUNDARY",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
