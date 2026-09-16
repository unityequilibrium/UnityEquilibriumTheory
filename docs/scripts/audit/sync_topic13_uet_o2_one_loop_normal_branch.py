"""Integrate the action-derived one-loop normal branch conservatively."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
MASS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
ACTION_REL = "docs/core/02_equations/covariant/uet_covariant_matter.py"
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
    if audit.get("status") != "PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE":
        raise SystemExit(f"one-loop normal branch audit is not passing: {audit.get('status')}")

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
        "data_role": major["data_role"],
        "status": "ACTION_DERIVED_THERMAL_NORMAL_BRANCH",
    })
    mass_evidence = evidence(MASS_REL, {
        "status": "TREE_LEVEL_FINITE_DENSITY_O2_MEAN_FIELD_DERIVATION",
        "role": "effective_mass_map",
    })
    action_evidence = evidence(ACTION_REL, {
        "status": "CANDIDATE_O2_SCALAR_ACTION_WITH_RECIPROCAL_RESPONSE_COUPLING",
        "role": "conservative_action_origin",
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "action-derived one-loop thermal normal-background determinant and Phi response derivative")
    append_unique(full_major.setdefault("what_remains_open", []), "vacuum counterterm/interacting finite-temperature completion remains open")
    append_unique(full_major.setdefault("what_remains_open", []), "condensate Goldstone and normal two-fluid completion remains open")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["uet_o2_one_loop_normal_branch"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "state": audit["state"],
        "finite_difference_checks": audit["finite_difference_checks"],
        "vacuum_counterterm_included": False,
        "condensate_contribution_included": False,
        "normal_two_fluid_completion": False,
        "physical_kubo_coefficient_emitted": False,
        "alpha_Phi_K_emitted": False,
        "si_map_emitted": False,
        "R_gen_used_as_state": False,
        "audit": audit_evidence,
        "implementation": module_evidence,
        "effective_mass_map": mass_evidence,
        "action_origin": action_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    for item in (audit_evidence, module_evidence, mass_evidence, action_evidence):
        append_unique(full["evidence_artifacts"], item)
    full.setdefault("data_role", {})["uet_o2_one_loop_normal_branch"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Close the thermal one-loop vacuum/renormalization contract or retain the thermal-only scope; then derive the condensate/two-fluid sector and match physical Kubo/SI Phi observables."
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
    record["evidence_artifacts"] = [audit_evidence, module_evidence, mass_evidence, action_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [item for item in register.get("entries", []) if item.get("major_result_id") != major["major_result_id"]] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "action-derived one-loop normal-background thermal determinant and Phi response derivative")
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
    partial["uet_o2_one_loop_normal_branch"] = audit_evidence
    partial["uet_o2_one_loop_normal_branch_controller"] = blocker
    partial["uet_o2_one_loop_normal_branch_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Action-Derived O(2) One-Loop Normal Branch (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-027` | `Omega_N^(1,T)=T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))]`; `E_k=sqrt(k^2+m_eff(Phi)^2)`; `partial p_N/partial Phi=-(partial m_eff^2/partial Phi)(1/2) integral[(n_-+n_+)/E_k]` | `{MODULE_REL}`; `{AUDIT_REL}`; `{MASS_REL}`; `{ACTION_REL}` | natural units; `T,mu,m_eff` = energy; `p,Omega,epsilon` = energy density; `n` = charge density; `s` = entropy density; response derivative = action-energy density per natural Phi unit | thermal one-loop determinant from the declared conservative O(2) action mass map; no vacuum counterterm | normal-background action-derived lane passes; renormalization, condensate/two-fluid, Kubo, SK/KMS, SI remain open | verifies action mass derivative, thermodynamic derivatives, positivity, and exclusion boundary | thermal determinant can be overread as full finite-temperature UET EOS or physical transport | close renormalization and interacting finite-T action, then derive condensate/normal sector and match Kubo/SI observables |

This lane uses no `R_gen` state/feedback and emits no physical Kubo value,
`alpha_Phi_K`, or SI observable map.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Action-Derived O(2) One-Loop Normal Branch"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The thermal one-loop determinant on the homogeneous
normal background `A=0` is derived from the declared action mass map
`m_eff(Phi)`. The response derivative, charge/temperature derivatives,
positivity, and energy identity pass in natural units.

WHAT_REMAINS_OPEN: Vacuum counterterm/renormalization and interacting thermal
self-energy are not closed. The condensate/Goldstone/normal two-fluid sector,
physical Kubo coefficient, SK/KMS matching, SI Phi map, and `alpha_Phi_K` remain
open.

DEPENDENCY_UNLOCKED: Action-derived normal-background lane only. No full finite-
temperature UET EOS, physical transport, Full Topic 13, Core, or Gravity unlock.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and hashes of the action, mass map, and one-loop
implementation are linked into the full gate, register, dependency gate,
formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
E_k = sqrt(k^2 + m_eff(Phi)^2)
Omega_N^(1,T) = T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))] d^3k/(2 pi)^3
partial p_N/partial Phi = -(partial m_eff^2/partial Phi) * 1/2 integral[(n_-+n_+)/E_k] d^3k/(2 pi)^3
```

VERIFICATION: Action mass derivative, pressure derivatives with respect to Phi,
mu, and T, positivity, energy identity, normal-domain condition, and explicit
vacuum/condensate/two-fluid exclusion all pass. No fit, target, holdout,
physical Kubo value, or SI alpha is used.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Close or explicitly bound the vacuum/renormalization layer, then
derive the condensate/two-fluid sector and match physical Kubo/SI Phi
observables.

CLAIM_BOUNDARY: This is an action-derived thermal normal-background lane only.
It is not a renormalized full finite-temperature UET action, two-fluid
derivation, physical transport, SI calibration, external validation, or Full
Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Action-derived O(2) one-loop normal branch"
    log_content = f"""{log_marker}

- Scope: derive the finite-temperature normal-background thermal determinant from the declared O(2) action mass map, without claiming a full two-fluid closure.
- Added or changed: `{AUDIT_REL}`, `{MODULE_REL}`, action/mass-map hashes, full-gate integration, major-result register, dependency evidence, formula audit, report, and ledger.
- Verified with: `{audit["status"]}`; `dp/dPhi`, `dp/dmu=n`, `dp/dT=s`, energy identity, positivity, normal-domain condition, and explicit exclusion boundaries pass.
- Result closed: `T13_UET_O2_ONE_LOOP_NORMAL_BRANCH` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the derived branch stops at `{blocker}`; condensate/two-fluid, Kubo, SK/KMS, SI anchor, and alpha remain separate blockers.
- Still open: vacuum/renormalized interacting completion, condensate/normal sector, physical Kubo, SI Phi map, alpha_Phi_K, and Full Topic 13 closure.
- Next controller: close the renormalization/interaction boundary or keep it explicit, then derive the remaining finite-temperature sector.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Action-Derived O(2) One-Loop Normal Branch"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` O(2) action/thermal branch and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the action-derived one-loop normal branch and synchronized Topic 13 full gate, register, dependency gate, formula audit, report, update log, and ledger
- verification: `{audit["status"]}`; thermodynamic derivatives, action response derivative, positivity, and excluded-physics boundaries pass
- public-safety status: `partial`; branch is not a renormalized full finite-temperature UET closure
- current claim boundary: `T13_UET_O2_ONE_LOOP_NORMAL_BRANCH` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: address vacuum/interaction boundary, condensate/two-fluid completion, physical Kubo, and SI Phi mapping
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
