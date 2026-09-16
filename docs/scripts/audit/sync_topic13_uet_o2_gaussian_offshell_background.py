"""Integrate the off-shell Gaussian O(2) background boundary lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_gaussian_offshell_background_audit.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_gaussian_offshell_background.py"
THERMAL_REL = "docs/core/02_equations/o2/uet_o2_condensate_gaussian_thermal.py"
SPECTRUM_REL = "docs/core/02_equations/o2/uet_o2_condensate_fluctuations.py"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
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
    expected = "PASS_ACTION_DERIVED_OFFSHELL_THERMAL_BACKREACTION_BOUNDARY"
    if audit.get("status") != expected:
        raise SystemExit(f"off-shell audit is not passing: {audit.get('status')}")

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
        {
            "role": "off-shell O(2) Hessian and thermal-only stable-domain boundary",
            "data_role": major["data_role"],
        },
    )
    thermal_evidence = evidence(
        THERMAL_REL,
        {"role": "fixed-background Gaussian thermal determinant boundary"},
    )
    spectrum_evidence = evidence(
        SPECTRUM_REL,
        {"role": "declared stationary O(2) quadratic mode roots"},
    )
    eos_evidence = evidence(
        EOS_REL,
        {"role": "tree-level condensate background and phase control"},
    )
    all_evidence = [
        audit_evidence,
        module_evidence,
        thermal_evidence,
        spectrum_evidence,
        eos_evidence,
    ]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "off-shell O(2) Gaussian Hessian and thermal-only stable-domain boundary at fixed Phi",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "a self-consistent finite-temperature phase boundary still requires a declared thermal self-energy or renormalized effective action",
    )
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    transport["uet_o2_gaussian_offshell_background_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "stationary_root_records": audit["stationary_root_records"],
        "convergence_records": audit["convergence_records"],
        "convergence_relative_errors": audit["convergence_relative_errors"],
        "audit": audit_evidence,
        "implementation": module_evidence,
        "fixed_background_gaussian": thermal_evidence,
        "stationary_spectrum": spectrum_evidence,
        "tree_level_eos": eos_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["uet_o2_gaussian_offshell_background_boundary"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["claim_promotion"] = False
    full["next_action"] = "Use the off-shell boundary to specify the missing thermal self-energy or renormalized effective action; then close normal Kubo/SK/KMS, entropy balance, and independent base-Phi SI calibration."
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    record = {
        key: major[key]
        for key in (
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
    record["evidence_artifacts"] = all_evidence
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item
        for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(
        item
        for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    append_unique(
        full_entry.setdefault("what_is_closed", []),
        "off-shell O(2) Gaussian Hessian recovery and thermal-only background stability boundary",
    )
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_gaussian_offshell_background_boundary"] = audit_evidence
    partial["uet_o2_gaussian_offshell_background_boundary_controller"] = blocker
    partial["uet_o2_gaussian_offshell_background_boundary_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Off-Shell Gaussian O(2) Thermal Background Boundary (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-033` | `Omega_tree(A)=0.5*(m_eff(Phi)^2-Z*mu^2)*A^2+0.25*lambda*A^4`; `r_sigma=-q+3*lambda*A^2`; `r_pi=-q+lambda*A^2`; `det=(y-k^2-r_sigma/Z)*(y-k^2-r_pi/Z)-4*mu^2*y` | `{AUDIT_REL}`; `{MODULE_REL}`; `{THERMAL_REL}`; `{SPECTRUM_REL}`; `{EOS_REL}` | natural units; `A,mu,T,omega,k` follow the declared O(2) action; grand potential is a natural thermodynamic density; no SI Phi map | off-shell Hessian of the declared conservative O(2) action plus thermal Bose determinant; no external coefficients | stationary-root recovery, stable-domain rejection, one-sided thermal tadpole, and quadrature convergence pass; renormalized finite-T phase boundary remains open | makes the thermal-background blocker measurable without treating fixed-background Gaussian pressure as a self-consistent EOS | tree-level stationary amplitude is not finite-T stationary under the thermal-only determinant; lower-amplitude side is unstable at the reference point | declare/derive thermal self-energy and vacuum renormalization, then solve a self-consistent finite-T phase boundary |

The audit uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared roles of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Off-Shell Gaussian O(2) Thermal Background Boundary"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The off-shell homogeneous O(2) Hessian was derived at
fixed `Phi`, and at `A^2=q/lambda` it recovers the existing radial/Goldstone
determinant. The thermal-only Gaussian potential is evaluated only where both
quadratic roots are positive. At the reference tree-level amplitude, the
one-sided stable-direction thermal slope is `{audit["reference"]["right_one_sided_slope"]:.12g}`, above the declared threshold `{audit["reference"]["tadpole_threshold"]:.12g}`.

WHAT_REMAINS_OPEN: The fixed tree-level amplitude is therefore not a
finite-temperature stationary point of the thermal-only Gaussian potential,
while the lower-amplitude side is unstable at the reference point. A valid
finite-temperature phase boundary requires a declared thermal self-energy or
renormalized effective action. Vacuum counterterms, normal two-fluid/Kubo,
SK/KMS, entropy production, SI Phi mapping, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Off-shell Gaussian thermal background boundary diagnostic
only. No Full Topic 13, Core, Gravity, constitutive transport, or external
validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add the off-shell curvatures,
mode roots, stable-domain audit, stationary determinant recovery, one-sided
thermal tadpole witness, and convergence record; this sync links them into the
full gate, closure register, dependency graph, formula audit, current report,
update log, and ledger.

EQUATION_OR_MAPPING:

```text
Omega_tree(A) = 0.5*(m_eff(Phi)^2 - Z*mu^2)*A^2 + 0.25*lambda*A^4
r_sigma = -q + 3*lambda*A^2
r_pi = -q + lambda*A^2
det(y) = (y-k^2-r_sigma/Z)*(y-k^2-r_pi/Z) - 4*mu^2*y
Omega_G(A,T) = T integral sum_a log(1-exp(-omega_a(A)/T)) d^3k/(2*pi)^3
```

VERIFICATION: `{audit["status"]}`; stationary roots recover the existing
determinant, the thermal-only stable-domain and quadrature checks pass, the
one-sided tadpole is nonzero, and the lower-amplitude witness is rejected as
unstable. No fit, source row, physical Kubo coefficient, or Xie 2026 holdout
is used.

CONTROLLING_BLOCKER: `{blocker}`. The full Topic 13 controller remains the
independent dimensional Phi/SI anchor or `alpha_Phi_K`; this lane additionally
makes the finite-temperature self-consistency requirement explicit.

NEXT_ACTION: Derive or explicitly source-lock the thermal self-energy and
vacuum renormalization needed for a self-consistent finite-temperature phase
boundary, then close normal Kubo/SK/KMS, entropy balance, and the independent
base-Phi SI anchor.

CLAIM_BOUNDARY: This is an action-derived off-shell Gaussian thermal boundary
diagnostic in natural units. It is not a renormalized finite-temperature UET
EOS, physical transport result, microscopic SK/KMS match, SI calibration,
external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Off-shell Gaussian O(2) thermal background boundary"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

- Scope: extend the declared O(2) quadratic determinant to a homogeneous off-shell amplitude and audit the thermal-only background boundary.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; stationary determinant recovery, stable-domain rejection, one-sided thermal tadpole, and quadrature convergence pass.
- Result closed: `T13_UET_O2_GAUSSIAN_OFFSHELL_BACKGROUND_BOUNDARY` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the tree-level amplitude is not finite-temperature stationary under the thermal-only determinant; a thermal self-energy or renormalized effective action is required.
- Still open: vacuum renormalization, interacting self-energy, normal two-fluid/Kubo, SK/KMS/entropy, SI Phi map, alpha, and Full Topic 13 closure.
- Next controller: declare/derive the missing thermal self-energy and renormalization contract before claiming a finite-temperature phase boundary.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""",
    )

    ledger_marker = "## Topic 13 Off-Shell Gaussian O(2) Thermal Background Boundary"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` off-shell O(2) background lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added off-shell Hessian/thermal-only boundary module and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; stationary determinant recovery, thermal stable-domain, one-sided tadpole, and convergence checks pass
- public-safety status: `partial`; no renormalized finite-T EOS, transport, SI map, alpha, or external claim is made
- current claim boundary: `T13_UET_O2_GAUSSIAN_OFFSHELL_BACKGROUND_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: derive/source-lock thermal self-energy and vacuum renormalization before a self-consistent phase-boundary claim
""",
    )

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_T13_UET_O2_GAUSSIAN_OFFSHELL_BACKGROUND_BOUNDARY",
                "major_result_id": major["major_result_id"],
                "closure_level": major["closure_level"],
                "full_topic13_status": full["status"],
                "full_core_unlock": False,
                "controlling_blocker": full["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
