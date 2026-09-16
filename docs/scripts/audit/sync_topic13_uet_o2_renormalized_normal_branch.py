"""Integrate the declared renormalized normal one-loop scheme lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_renormalized_normal_branch_audit.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_renormalized_normal_branch.py"
NORMAL_REL = "docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py"
CURVATURE_REL = "docs/core/02_equations/o2/uet_o2_normal_response_curvature.py"
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
    expected = "PASS_ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME"
    if audit.get("status") != expected:
        raise SystemExit(f"renormalized normal audit is not passing: {audit.get('status')}")

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
        {"role": "declared mass-squared Taylor-subtracted normal one-loop scheme", "data_role": major["data_role"]},
    )
    normal_evidence = evidence(NORMAL_REL, {"role": "thermal normal one-loop determinant"})
    curvature_evidence = evidence(CURVATURE_REL, {"role": "action-derived thermal response curvature"})
    all_evidence = [audit_evidence, module_evidence, normal_evidence, curvature_evidence]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "declared mass-squared Taylor-subtraction scheme for the normal one-loop vacuum plus thermal determinant",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "interacting finite-temperature self-energy and microscopic renormalization matching remain open",
    )
    transport = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport["uet_o2_renormalized_normal_one_loop_lane"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "finite_difference_checks": audit["finite_difference_checks"],
        "convergence_records": audit["convergence_records"],
        "convergence_relative_errors": audit["convergence_relative_errors"],
        "numerical_stability_note": audit["numerical_stability_note"],
        "vacuum_subtraction_order": 2,
        "reference_point": "Phi=Phi_*",
        "interacting_self_energy_included": False,
        "condensate_contribution_included": False,
        "normal_two_fluid_completion": False,
        "physical_kubo_coefficient_included": False,
        "physical_si_mapping_included": False,
        "audit": audit_evidence,
        "implementation": module_evidence,
        "thermal_normal_branch": normal_evidence,
        "response_curvature": curvature_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["uet_o2_renormalized_normal_one_loop_lane"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
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
    record["evidence_artifacts"] = all_evidence
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(
        full_entry.setdefault("what_is_closed", []),
        "declared natural-unit renormalized normal one-loop scheme with cutoff and thermodynamic checks",
    )
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    for item in all_evidence:
        append_unique(full_entry.setdefault("evidence_artifacts", []), item)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_renormalized_normal_one_loop_lane"] = audit_evidence
    partial["uet_o2_renormalized_normal_one_loop_lane_controller"] = blocker
    partial["uet_o2_renormalized_normal_one_loop_lane_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Renormalized Normal One-Loop Scheme Lane (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-036` | `V_vac^R(x)=integral[E(x)-E(x0)-(x-x0)E'(x0)-1/2*(x-x0)^2 E''(x0)] d^3k/(2*pi)^3`; `Omega_R=V_vac^R+Omega_N^(1,T)`; `kappa_Phi^R=epsilon_nc U''+kappa_Phi^T+(partial_Phi m_eff^2)^2 partial_x^2 V_vac^R` | `{AUDIT_REL}`; `{MODULE_REL}`; `{NORMAL_REL}`; `{CURVATURE_REL}` | natural units; `x=m_eff^2`; vacuum potential is natural energy density; response curvature has natural mass dimension two; no SI alpha | declared mass-squared Taylor subtraction at `Phi_*`; no external counterterm measurement | reference conditions, mass-derivative finite difference, response curvature, convergence, and thermodynamic identities pass; microscopic matching remains open | closes a reproducible normal-branch subtraction scheme without claiming unique physical renormalization | subtracted potential is cancellation-sensitive and the scheme is not matched to interacting finite-T self-energy or physical data | derive finite-T self-energy/counterterm matching and then connect to physical Kubo, SK/KMS, entropy, SI map, and alpha | 

This lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Renormalized Normal One-Loop Scheme Lane"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A declared mass-squared Taylor-subtraction scheme through second order at `Phi_*` now produces a finite natural-unit normal-branch vacuum plus thermal one-loop state. Reference conditions, response curvature, cutoff convergence, and pressure/entropy/charge/energy identities are recorded.

WHAT_REMAINS_OPEN: This is not a unique microscopic renormalization, interacting finite-temperature self-energy, condensate/two-fluid EOS, physical Kubo coefficient, microscopic SK/KMS match, entropy-production closure, SI Phi map, or independent `alpha_Phi_K` calibration.

DEPENDENCY_UNLOCKED: Renormalized normal one-loop scheme lane only. No Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add the declared subtraction scheme, mass-derivative and response checks, convergence record, and thermodynamic identity audit; this sync links them to the full gate, closure register, dependency evidence, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
x = m_eff(Phi)^2
V_vac^R(x) = integral [E(x)-E(x0)-(x-x0)E'(x0)-1/2*(x-x0)^2 E''(x0)] d^3k/(2*pi)^3
Omega_R = V_vac^R + Omega_N^(1,T)
kappa_Phi^R = epsilon_nc U''(Phi) + kappa_Phi^T + (partial_Phi m_eff^2)^2 partial_x^2 V_vac^R
```

VERIFICATION: `{audit["status"]}`; reference renormalization conditions, mass-derivative finite difference, response curvature, convergence, thermodynamic derivatives, natural units, ontology, and holdout exclusion pass. Numerical cancellation sensitivity is explicitly recorded rather than hidden.

CONTROLLING_BLOCKER: `{blocker}` for this lane. Full Topic 13 remains controlled by the independent dimensional Phi/SI anchor, source package, beta bridge, EOS/transport/KMS/entropy completion, and `alpha_Phi_K` calibration.

NEXT_ACTION: Match the finite-temperature action beyond the declared free normal determinant, then close physical Kubo/SK/KMS/entropy and the independent Phi-to-thermal observable map without using Xie 2026 or fitting `alpha_Phi_K`.

CLAIM_BOUNDARY: This is an action-derived natural-unit subtraction scheme for one normal O(2) lane. It is not a unique physical renormalization, external validation, SI calibration, transport coefficient, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Renormalized normal one-loop scheme lane"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

- Scope: close the declared mass-squared Taylor-subtraction scheme for the normal one-loop vacuum plus thermal determinant.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; reference conditions, derivative checks, convergence, thermodynamic identities, ontology, and holdout policy pass.
- Result closed: `T13_UET_O2_RENORMALIZED_NORMAL_ONE_LOOP_LANE` is `CLOSED_FOR_LANE`.
- Blocker narrowed: a reproducible subtraction scheme exists; interacting finite-T self-energy and microscopic scheme matching remain open.
- Still open: condensate/two-fluid EOS, physical Kubo, SK/KMS/entropy, SI Phi map, source package, alpha, and Full Topic 13 closure.
- Next controller: extend the renormalized action with finite-T self-energy matching or record a scoped no-go before physical transport promotion.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""",
    )

    ledger_marker = "## Topic 13 Renormalized Normal One-Loop Scheme Lane"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` renormalized normal one-loop lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the subtraction-scheme module/audit and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; reference conditions, derivative checks, convergence, thermodynamic identities, and claim boundaries pass
- public-safety status: `partial`; no unique physical renormalization, Kubo, SI map, alpha, or external claim is made
- current claim boundary: `T13_UET_O2_RENORMALIZED_NORMAL_ONE_LOOP_LANE` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: close finite-T self-energy matching and physical transport/SI dependencies without holdout use
""",
    )

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_UET_O2_RENORMALIZED_NORMAL_ONE_LOOP_LANE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
