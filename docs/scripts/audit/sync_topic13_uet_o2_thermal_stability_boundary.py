"""Integrate the thermal-only quadratic condensate stability boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_thermal_stability_boundary_audit.json"
MODULE_REL = "docs/core/uet_o2_thermal_stability_boundary.py"
OFFSHELL_REL = "docs/core/uet_o2_gaussian_offshell_background.py"
EOS_REL = "docs/core/uet_o2_finite_density_eos.py"
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
    expected = "PASS_ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY"
    if audit.get("status") != expected:
        raise SystemExit(f"thermal stability boundary audit is not passing: {audit.get('status')}")

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
        {"role": "analytic quadratic condensed stability boundary", "data_role": major["data_role"]},
    )
    offshell_evidence = evidence(OFFSHELL_REL, {"role": "off-shell O(2) Hessian and thermal determinant"})
    eos_evidence = evidence(EOS_REL, {"role": "declared condensed control and natural-unit EOS"})
    all_evidence = [audit_evidence, module_evidence, offshell_evidence, eos_evidence]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "analytic thermal-only quadratic stability boundary of the homogeneous condensed O(2) lane",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "the quadratic stability boundary is not a self-consistent finite-temperature stationary phase boundary",
    )
    transport = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport["uet_o2_thermal_stability_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "boundary_mode_witness": audit["boundary_mode_witness"],
        "above_boundary_mode_witness": audit["above_boundary_mode_witness"],
        "below_boundary_mode_witness": audit["below_boundary_mode_witness"],
        "convergence_records": audit["convergence_records"],
        "convergence_relative_errors": audit["convergence_relative_errors"],
        "self_consistent_finite_temperature_boundary": False,
        "interacting_self_energy_included": False,
        "vacuum_counterterm_included": False,
        "normal_two_fluid_completion": False,
        "physical_kubo_coefficient_included": False,
        "physical_si_mapping_included": False,
        "audit": audit_evidence,
        "implementation": module_evidence,
        "off_shell_hessian": offshell_evidence,
        "tree_eos": eos_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["uet_o2_thermal_stability_boundary"] = major["data_role"]
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
        "analytic condensed quadratic stability boundary with mode-sign witness below and above the boundary",
    )
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    for item in all_evidence:
        append_unique(full_entry.setdefault("evidence_artifacts", []), item)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_thermal_stability_boundary"] = audit_evidence
    partial["uet_o2_thermal_stability_boundary_controller"] = blocker
    partial["uet_o2_thermal_stability_boundary_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Thermal-Only Quadratic Condensed Stability Boundary (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-037` | `q=Z*mu^2-m_eff(Phi)^2`; `r_pi(A)=-q+lambda*A^2`; `A_boundary^2=q/lambda`; `r_sigma(A_boundary)=2*q` | `{AUDIT_REL}`; `{MODULE_REL}`; `{OFFSHELL_REL}`; `{EOS_REL}` | natural units; `A^2` and `q/lambda` are amplitude squared; Hessian entries are natural mass squared; no SI Phi map | declared O(2) tree-level Hessian plus thermal-only Gaussian mode witness; no interacting self-energy | analytic boundary, mode signs, below-boundary instability, one-sided thermal slope, and convergence pass; stationary finite-T backreaction remains open | closes the quadratic stability-domain boundary without calling it a phase transition or EOS closure | thermal determinant has a one-sided slope at the tree-level boundary; an interior finite-T stationary point requires self-energy/renormalized effective action | derive/source-lock thermal self-energy and solve the self-consistent stationary boundary before any phase-transition claim | 

This lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Thermal-Only Quadratic Condensed Stability Boundary"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared O(2) Hessian gives an analytic lower boundary `A_boundary^2=q/lambda` where `r_pi=0` and `r_sigma=2q`. The quadratic mode witness is nonnegative at and above this boundary and becomes negative below it. The thermal-only grand potential and one-sided slope at the boundary are finite and converged.

WHAT_REMAINS_OPEN: This is a quadratic stability boundary, not a self-consistent finite-temperature stationary phase boundary. Thermal self-energy, vacuum renormalization, condensate/two-fluid EOS, physical Kubo, microscopic SK/KMS/entropy, SI Phi mapping, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Thermal-only quadratic stability boundary lane only. No finite-temperature phase-transition, Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add the analytic boundary, mode-sign witnesses, one-sided thermal diagnostic, convergence record, and explicit non-promotion boundary; this sync links them into the full gate, closure register, dependency evidence, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
q = Z*mu^2 - m_eff(Phi)^2 > 0
r_pi(A) = -q + lambda*A^2
A_boundary^2 = q/lambda
r_sigma(A_boundary) = 2*q
```

VERIFICATION: `{audit["status"]}`; `r_pi=0`, `r_sigma=2q`, mode roots are nonnegative at/above the boundary and negative below it, thermal one-sided slope is resolved, and cutoff convergence passes. No clipping, fit, source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `{blocker}`. The boundary is not a finite-temperature stationary solution because the declared thermal determinant supplies a nonzero one-sided slope; closing that requires thermal self-energy or a renormalized effective action.

NEXT_ACTION: Derive or source-lock the finite-temperature self-energy needed for an interior stationary boundary, then close the condensate/normal two-fluid EOS and physical transport without promoting this stability boundary to a phase transition.

CLAIM_BOUNDARY: This is an action-derived natural-unit quadratic stability boundary and thermal-only diagnostic. It is not a self-consistent finite-temperature phase transition, EOS closure, transport result, SI calibration, external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Thermal-only quadratic condensed stability boundary"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

- Scope: close the analytic lower stability boundary of the homogeneous condensed O(2) quadratic Hessian and test its thermal-only mode domain.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; curvature identities, mode signs below/above the boundary, one-sided thermal slope, convergence, ontology, and holdout exclusion pass.
- Result closed: `T13_UET_O2_THERMAL_STABILITY_BOUNDARY` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the quadratic stable-domain boundary is explicit, while its finite-temperature stationary displacement still requires self-energy/renormalized action.
- Still open: vacuum renormalization, interacting self-energy, condensate/two-fluid EOS, physical Kubo, SK/KMS/entropy, SI map, alpha, source package, and Full Topic 13 closure.
- Next controller: derive or source-lock the thermal self-energy for a self-consistent stationary boundary; do not call the current boundary a phase transition.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""",
    )

    ledger_marker = "## Topic 13 Thermal-Only Quadratic Condensed Stability Boundary"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` thermal stability boundary lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added analytic stability-boundary module/audit and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; boundary curvatures, mode witnesses, thermal slope, convergence, and claim boundaries pass
- public-safety status: `partial`; no finite-T phase-transition, self-energy, transport, SI map, alpha, or external claim is made
- current claim boundary: `T13_UET_O2_THERMAL_STABILITY_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: derive/source-lock self-energy for a self-consistent finite-T stationary boundary
""",
    )

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_UET_O2_THERMAL_STABILITY_BOUNDARY",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
