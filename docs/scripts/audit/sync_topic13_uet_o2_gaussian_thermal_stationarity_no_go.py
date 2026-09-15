"""Integrate the scoped thermal Gaussian condensate stationarity no-go."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_gaussian_thermal_stationarity_no_go.json"
MODULE_REL = "docs/core/uet_o2_gaussian_thermal_stationarity_no_go.py"
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
    expected = "PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY"
    if audit.get("status") != expected:
        raise SystemExit(f"thermal Gaussian stationarity no-go audit is not passing: {audit.get('status')}")

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
    module_evidence = evidence(MODULE_REL, {"role": "analytic thermal Gaussian stationarity no-go", "data_role": major["data_role"]})
    offshell_evidence = evidence(OFFSHELL_REL, {"role": "off-shell O(2) mode roots and thermal determinant"})
    eos_evidence = evidence(EOS_REL, {"role": "declared tree-level condensed control"})
    all_evidence = [audit_evidence, module_evidence, offshell_evidence, eos_evidence]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "scoped no-go for a thermal-only Gaussian stationary condensate within the stable domain x=A^2>=q/lambda",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "the no-go does not constrain a renormalized/interacting finite-temperature branch with self-energy",
    )
    transport = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport["uet_o2_gaussian_thermal_stationarity_no_go"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "formal_no_go_closure": audit["formal_no_go_closure"],
        "reference": audit["reference"],
        "representative_records": audit["representative_records"],
        "finite_difference_records": audit["finite_difference_records"],
        "convergence_records": audit["convergence_records"],
        "convergence_relative_errors": audit["convergence_relative_errors"],
        "vacuum_counterterm_included": False,
        "interacting_self_energy_included": False,
        "renormalized_interacting_branch_required": True,
        "audit": audit_evidence,
        "implementation": module_evidence,
        "off_shell_hessian": offshell_evidence,
        "tree_eos": eos_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["uet_o2_gaussian_thermal_stationarity_no_go"] = major["data_role"]
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
        "thermal-only Gaussian condensate stationarity no-go in the declared stable domain",
    )
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    for item in all_evidence:
        append_unique(full_entry.setdefault("evidence_artifacts", []), item)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_gaussian_thermal_stationarity_no_go"] = audit_evidence
    partial["uet_o2_gaussian_thermal_stationarity_no_go_controller"] = blocker
    partial["uet_o2_gaussian_thermal_stationarity_no_go_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Thermal Gaussian Condensate Stationarity No-Go (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-038` | `x=A^2`; `x>=q/lambda`; `partial_x Omega_tree=0.5*(-q+lambda*x)>=0`; `partial_x omega_+-^2>0`; `partial_x omega_-^2>0`; `partial_x Omega_G>0` for stable Bose modes | `{AUDIT_REL}`; `{MODULE_REL}`; `{OFFSHELL_REL}`; `{EOS_REL}` | natural units; `x` is amplitude squared; `Omega` is natural density; no SI Phi map | declared tree O(2) potential and stable Gaussian determinant; no vacuum/interacting self-energy | scoped analytic no-go plus mode-derivative and finite-difference witnesses pass; conclusion explicitly limited to current branch | closes the thermal-only stationarity question as a no-go and forces a named renormalized/interacting branch for any finite-T stationary claim | a vacuum counterterm or interacting self-energy can alter the derivative and is not ruled out | derive/source-lock the named renormalized interacting branch before phase-boundary promotion | 

The no-go uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Thermal Gaussian Condensate Stationarity No-Go"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO`

WHAT_IS_ACTUALLY_CLOSED: In the declared tree plus stable thermal Gaussian branch, let `x=A^2`. The stable domain is `x>=q/lambda`; the tree derivative is nonnegative, both quadratic mode roots increase with `x`, and each stable Bose determinant term increases with `x`. Therefore the combined thermal-only potential has no stationary condensate in that domain. Analytic margins, finite-difference derivative signs, and cutoff convergence are recorded.

WHAT_REMAINS_OPEN: This no-go is scoped. Vacuum counterterms, interacting finite-temperature self-energy, and a renormalized effective action may define a different branch and are not ruled out. EOS/two-fluid, physical Kubo, SK/KMS/entropy, SI Phi mapping, alpha, source package, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: No-go for the current thermal-only Gaussian branch only. A named renormalized/interacting branch is required; no Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add the algebraic no-go, analytic mode-root derivatives, finite-difference sign witnesses, and convergence record; this sync links them into the full gate, closure register, dependency evidence, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
x = A^2
x >= q/lambda
partial_x Omega_tree = 0.5*(-q + lambda*x) >= 0
partial_x omega_+^2 > 0, partial_x omega_-^2 > 0
partial_x [T log(1-exp(-omega/T))] > 0
=> partial_x Omega_tree+Omega_G > 0
```

VERIFICATION: `{audit["status"]}`; analytic discriminant margin is positive, mode-root derivatives are positive over the declared witness, thermal and combined finite-difference derivatives are positive, and potential convergence passes. No clipping, fit, source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `{blocker}`. The no-go excludes only a stationary point of the current thermal-only Gaussian domain; any finite-temperature stationary phase claim now requires the named renormalized/interacting branch.

NEXT_ACTION: Derive or source-lock the finite-temperature self-energy and renormalized effective action for the named branch, then test whether a stationary solution exists before discussing phase transition or two-fluid closure.

CLAIM_BOUNDARY: This is a scoped structural no-go for the current tree plus stable thermal Gaussian branch. It is not a no-go for interacting finite-temperature UET, a physical phase-transition proof, EOS closure, transport result, SI calibration, external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Thermal Gaussian condensate stationarity no-go"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

- Scope: test whether the tree plus stable thermal Gaussian condensate branch admits a stationary point in `x=A^2`.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; tree derivative, analytic mode-root derivative/margin, finite-difference signs, convergence, ontology, and holdout exclusion pass.
- Result closed: `T13_UET_O2_GAUSSIAN_THERMAL_STATIONARITY_NO_GO` is `CLOSED_AS_NO_GO`.
- Blocker narrowed: the current thermal-only Gaussian branch has no stationary condensate in its stable domain; a named renormalized/interacting branch is now required for any finite-T stationary claim.
- Still open: vacuum renormalization, self-energy, condensate/two-fluid EOS, physical Kubo, SK/KMS/entropy, SI map, alpha, source package, and Full Topic 13 closure.
- Next controller: derive/source-lock the named renormalized interacting branch and rerun stationarity before phase-transition promotion.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""",
    )

    ledger_marker = "## Topic 13 Thermal Gaussian Condensate Stationarity No-Go"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` thermal Gaussian stationarity lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added scoped analytic no-go, derivative witnesses, and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; analytic margin, mode derivatives, finite-difference signs, convergence, and claim boundaries pass
- public-safety status: `partial`; no interacting phase transition, EOS, transport, SI map, alpha, or external claim is made
- current claim boundary: `T13_UET_O2_GAUSSIAN_THERMAL_STATIONARITY_NO_GO` is `CLOSED_AS_NO_GO`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: derive/source-lock the named renormalized interacting branch before any finite-T stationary claim
""",
    )

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_UET_O2_GAUSSIAN_THERMAL_STATIONARITY_NO_GO",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
