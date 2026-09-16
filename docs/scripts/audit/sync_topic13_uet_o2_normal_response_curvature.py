"""Integrate the action-derived normal response-curvature lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_normal_response_curvature_audit.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_normal_response_curvature.py"
ONE_LOOP_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
RESPONSE_REL = "docs/core/02_equations/covariant/uet_covariant_response.py"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-12.md"


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
    audit = load(AUDIT_REL)
    expected = "PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE"
    if audit.get("status") != expected:
        raise SystemExit(f"normal response curvature audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = audit["controlling_blocker"]
    audit_evidence = evidence(
        AUDIT_REL,
        {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "closure_level": major["closure_level"],
            "full_core_unlock": False,
        },
    )
    module_evidence = evidence(
        MODULE_REL,
        {"role": "action-derived natural-unit normal thermal response curvature", "data_role": major["data_role"]},
    )
    one_loop_evidence = evidence(ONE_LOOP_REL, {"role": "thermal normal one-loop determinant"})
    response_evidence = evidence(RESPONSE_REL, {"role": "declared response potential and Hessian"})
    all_evidence = [audit_evidence, module_evidence, one_loop_evidence, response_evidence]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "action-derived natural-unit normal-branch Phi response curvature and temperature slope with finite-difference and convergence verification",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "natural-unit response curvature is not a normalized beta_T13 or an SI Phi-to-thermal observable map",
    )
    transport = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport["uet_o2_normal_response_curvature_lane"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "finite_difference_checks": audit["finite_difference_checks"],
        "convergence_records": audit["convergence_records"],
        "convergence_relative_errors": audit["convergence_relative_errors"],
        "units": major["units"],
        "audit": audit_evidence,
        "implementation": module_evidence,
        "normal_one_loop": one_loop_evidence,
        "response_sector": response_evidence,
        "vacuum_counterterm_included": False,
        "condensate_contribution_included": False,
        "physical_beta_t13_identified": False,
        "physical_si_mapping_included": False,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["uet_o2_normal_response_curvature_lane"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["claim_promotion"] = False
    full["next_action"] = "Use the natural-unit curvature as an action-derived input only; declare a separate normalized beta functional or independent source-backed coefficient, then close renormalization, normal/two-fluid transport, KMS/entropy, SI Phi mapping, and alpha."
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    record = {key: major[key] for key in (
        "major_result_id", "topic", "closure_level", "what_is_closed",
        "equation_or_mapping", "units", "derivation_class", "observable",
        "data_role", "verification_status", "open_blockers",
        "dependency_unlocked", "claim_boundary",
    )}
    record["evidence_artifacts"] = all_evidence
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "action-derived natural-unit normal Phi response curvature and temperature slope")
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_normal_response_curvature_lane"] = audit_evidence
    partial["uet_o2_normal_response_curvature_lane_controller"] = blocker
    partial["uet_o2_normal_response_curvature_lane_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Action-Derived Normal Thermal Response Curvature (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-035` | `m_eff(Phi)^2=m^2-epsilon_nc*h*(Phi-Phi_*)`; `kappa_Phi^T=(partial_Phi m_eff^2)^2*partial_(m_eff^2)s_M`; `beta_action_natural=T*partial_T kappa_Phi^T`; `kappa_Phi=epsilon_nc*U''(Phi)+kappa_Phi^T` | `{AUDIT_REL}`; `{MODULE_REL}`; `{ONE_LOOP_REL}`; `{RESPONSE_REL}` | natural units; `Phi` has action-field mass dimension one; `kappa_Phi` has mass dimension two; `beta_action_natural` has mass dimension two; normalized `beta_T13` and SI `alpha_Phi_K` are not identified | declared covariant response map plus thermal one-loop normal determinant; no external calibration and no vacuum counterterm | action-derived normal-branch curvature, analytic derivatives, finite differences, and convergence pass; renormalization, SI, beta correspondence, and physical transport remain open | closes the natural-unit response-curvature lane without relabeling it as normalized beta or a thermal observable | the natural-unit slope could be mistaken for `beta_T13` or an SI coefficient if field normalization and observable mapping are not supplied | provide a declared normalized beta functional or independent source-backed coefficient, then close renormalization and SI Phi mapping |

The lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Action-Derived Normal Thermal Response Curvature"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared normal O(2) one-loop thermal determinant
was differentiated through the declared `m_eff(Phi)` action map. The natural-
unit Phi response curvature, its temperature derivative, the bare response
potential Hessian contribution, finite differences, and quadrature convergence
are recorded. This closes a derivation lane, not the physical thermal bridge.

WHAT_REMAINS_OPEN: The result has natural-unit field normalization and has no
vacuum counterterm, condensate contribution, finite-temperature two-fluid
completion, physical Kubo coefficient, normalized `beta_T13` correspondence,
SI Phi map, or independent `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Action-derived natural-unit normal response curvature
only. No normalized beta, SI observable, physical transport, Full Topic 13,
Core, Gravity, or external-validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add the action-derived response
curvature, temperature slope, finite-difference checks, convergence records,
units, and explicit non-identification rules; this sync links them into the
full gate, closure register, dependency graph, formula audit, current report,
update log, and ledger.

EQUATION_OR_MAPPING:

```text
m_eff(Phi)^2 = m^2 - epsilon_nc*h*(Phi-Phi_*)
kappa_Phi^T = (partial_Phi m_eff^2)^2 * partial_(m_eff^2) s_M
beta_action_natural = T * partial_T kappa_Phi^T
kappa_Phi = epsilon_nc*U''(Phi) + kappa_Phi^T
```

VERIFICATION: `{audit["status"]}`; analytic curvature, temperature slope,
total curvature, finite-difference agreement, and convergence checks pass.
The contract confirms natural units and confirms that physical beta, SI map,
vacuum renormalization, condensate, and Kubo sectors are not emitted. No fit,
source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `{blocker}` for this lane. The Full Topic 13 controller
remains the independent dimensional Phi/SI anchor or `alpha_Phi_K` route.

NEXT_ACTION: Match the action-derived natural-unit curvature to a separately
declared normalized finite-temperature functional or independent source-backed
coefficient without renaming it `beta_T13`; then close renormalization,
normal/two-fluid transport, KMS/entropy, SI Phi mapping, and alpha.

CLAIM_BOUNDARY: This is an action-derived natural-unit normal response
curvature and temperature-slope lane. It is not `beta_T13`, a physical thermal
observable, a renormalized finite-temperature action, a physical transport
coefficient, an SI calibration, external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Action-derived normal thermal response curvature"
    append_marker(LOG_REL, log_marker, f"""{log_marker}

- Scope: derive and audit the natural-unit normal-branch Phi response curvature and temperature slope from the declared O(2) action map.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; analytic versus finite-difference curvature/slope, total-curvature check, quadrature convergence, ontology, and no-holdout checks pass.
- Result closed: `T13_UET_O2_NORMAL_RESPONSE_CURVATURE_LANE` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the natural-unit response derivative is explicit, but its correspondence to normalized `beta_T13`, physical transport, and SI thermal observable remains unestablished.
- Still open: vacuum renormalization, condensate/normal two-fluid completion, Kubo/SK/KMS/entropy, SI Phi map, alpha, and Full Topic 13 closure.
- Next controller: establish a non-circular normalized-beta correspondence or source-backed coefficient without using Xie 2026 or fitting the target curve.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""")

    ledger_marker = "## Topic 13 Action-Derived Normal Thermal Response Curvature"
    append_marker(LEDGER_REL, ledger_marker, f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` normal response-curvature lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added action-derived normal curvature/slope audit and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; finite differences, convergence, units, ontology, and holdout exclusion pass
- public-safety status: `partial`; no normalized beta, SI map, physical Kubo, alpha, or external claim is made
- current claim boundary: `T13_UET_O2_NORMAL_RESPONSE_CURVATURE_LANE` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: close the normalized-beta correspondence and independent Phi/SI anchor without using holdout data
""")

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_UET_O2_NORMAL_RESPONSE_CURVATURE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
