"""Integrate one-loop numerical convergence without promoting physics."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_convergence_audit.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
COMPARATOR_REL = "docs/core/02_equations/o2/standard_o2_finite_temperature_comparator.py"
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
    if audit.get("status") != "PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE":
        raise SystemExit(f"one-loop convergence audit is not passing: {audit.get('status')}")
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
        "cutoff_factor": audit["reference"]["cutoff_factor"],
        "quadrature_order": audit["reference"]["quadrature_order"],
    })
    comparator_evidence = evidence(COMPARATOR_REL, {
        "cutoff_control": "explicit cutoff_factor",
        "role": "thermal integral implementation",
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "numerical cutoff and quadrature convergence of the action-derived one-loop normal branch")
    append_unique(full_major.setdefault("what_remains_open", []), "one-loop convergence does not close vacuum renormalization or interacting finite-temperature response")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["uet_o2_one_loop_convergence"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "drift": audit["drift"],
        "policy": audit["policy"],
        "audit": audit_evidence,
        "implementation": module_evidence,
        "comparator": comparator_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    for item in (audit_evidence, module_evidence, comparator_evidence):
        append_unique(full["evidence_artifacts"], item)
    full.setdefault("data_role", {})["uet_o2_one_loop_convergence"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Close the thermal one-loop vacuum/renormalization contract or retain the thermal-only scope; then derive interacting finite-temperature and condensate/two-fluid sectors and match physical Kubo/SI Phi observables."
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
    record["evidence_artifacts"] = [audit_evidence, module_evidence, comparator_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [item for item in register.get("entries", []) if item.get("major_result_id") != major["major_result_id"]] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "numerical convergence policy and reference baseline for the action-derived one-loop normal branch")
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
    partial["uet_o2_one_loop_convergence"] = audit_evidence
    partial["uet_o2_one_loop_convergence_controller"] = blocker
    partial["uet_o2_one_loop_convergence_reference"] = audit["reference"]
    partial["uet_o2_one_loop_convergence_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## One-Loop Normal Branch Convergence (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-028` | `p in [0, 70 max(T,m_eff,|mu|)]`, Gauss-Legendre `N=256`, maximum plateau drift `<=1e-8` | `{AUDIT_REL}`; `{MODULE_REL}`; `{COMPARATOR_REL}` | cutoff and momentum are natural units; declared thermodynamic outputs retain one-loop natural-unit contracts | deterministic numerical convergence policy for the thermal-only integral | convergence gate passes with reference `cutoff_factor=70`, `N=256`; vacuum/interaction physics remains open | prevents cutoff/order artifacts from being read as thermal response | low-order quadrature can drift at high cutoff; vacuum counterterm is not represented | keep reference baseline fixed and separately close renormalization/interacting finite-T response |

The convergence result is numerical evidence for the declared thermal-only
branch. It is not a renormalization proof or a physical transport coefficient.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## One-Loop Normal Branch Convergence"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The action-derived thermal-only one-loop normal branch
has a reproducible numerical plateau. The locked reference is
`cutoff_factor=70`, `quadrature_order=256`; the maximum plateau drift across
cutoffs `30,40,50,70,100` and orders `96,128,192,256` is below `1e-8` for all
declared outputs.

WHAT_REMAINS_OPEN: The convergence result does not close vacuum counterterms,
renormalization, interacting thermal self-energy, condensate/two-fluid physics,
Kubo transport, SK/KMS matching, SI Phi mapping, or `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Numerical stability of the action-derived normal branch
only. No physical thermal, transport, Full Topic 13, Core, or Gravity unlock.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` adds explicit cutoff/order sweeps and is linked into
the full gate, register, dependency gate, formula audit, report, update log,
and ledger.

EQUATION_OR_MAPPING:

```text
cutoff = 70 * max(T, m_eff, |mu|)
quadrature_order = 256
max relative plateau drift <= 1e-8
```

VERIFICATION: Plateau max drift is `{max(audit["drift"]["plateau_max_relative_drift"].values()):.3e}`;
cutoff-tail drift is `{max(audit["drift"]["cutoff_tail_relative_drift_order_192"].values()):.3e}`;
order drift is `{max(audit["drift"]["quadrature_order_relative_drift_cutoff_70"].values()):.3e}`.
Low-order high-cutoff cases are excluded from the reference. No target,
holdout, alpha fit, or synthetic replacement is used.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Close or explicitly bound the one-loop vacuum/renormalization
layer, then derive the interacting finite-temperature and condensate/two-fluid
sectors before physical transport matching.

CLAIM_BOUNDARY: Numerical convergence of the declared thermal-only integral
only. Not a renormalization proof, physical transport result, SI calibration,
external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - One-loop normal branch convergence"
    log_content = f"""{log_marker}

- Scope: verify cutoff and quadrature convergence of the action-derived thermal-only one-loop normal branch.
- Added or changed: `{AUDIT_REL}`, explicit `cutoff_factor`, convergence integration in the full gate/register/dependency gate, formula audit, report, and ledger.
- Verified with: `{audit["status"]}`; reference `cutoff_factor=70`, `quadrature_order=256`, plateau max drift below `1e-8` across declared outputs.
- Result closed: `T13_UET_O2_ONE_LOOP_CONVERGENCE` is `CLOSED_FOR_LANE`.
- Blocker narrowed: numerical stability is closed; `{blocker}` remains the controller for the one-loop physics boundary.
- Still open: vacuum/renormalization, interacting finite-T response, condensate/two-fluid sector, physical Kubo, SI Phi map, alpha_Phi_K, and Full Topic 13 closure.
- Next controller: close/bound renormalization and derive the remaining finite-T action sector.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 One-Loop Normal Branch Convergence"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` thermal one-loop normal branch and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added cutoff/quadrature convergence audit and synchronized Topic 13 full gate, register, dependency gate, formula audit, report, update log, and ledger
- verification: `{audit["status"]}`; reference `cutoff_factor=70`, `N=256`, plateau drift below `1e-8`; low-order drift is disclosed
- public-safety status: `partial`; convergence does not supply renormalization or physical transport
- current claim boundary: `T13_UET_O2_ONE_LOOP_CONVERGENCE` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: close/bound vacuum renormalization and derive interacting finite-T/condensate sector
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_ACTION_DERIVED_ONE_LOOP_CONVERGENCE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
