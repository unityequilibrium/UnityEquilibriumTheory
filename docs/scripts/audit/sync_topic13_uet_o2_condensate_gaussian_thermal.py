"""Integrate the fixed-background Gaussian finite-temperature O(2) lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_gaussian_thermal_audit.json"
MODULE_REL = "docs/core/uet_o2_condensate_gaussian_thermal.py"
SPECTRUM_REL = "docs/core/uet_o2_condensate_fluctuations.py"
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
    expected = "PASS_ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE"
    if audit.get("status") != expected:
        raise SystemExit(f"Gaussian thermal audit is not passing: {audit.get('status')}")

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
            "role": "fixed-tree-level-background Gaussian thermal determinant",
            "data_role": major["data_role"],
        },
    )
    spectrum_evidence = evidence(
        SPECTRUM_REL,
        {"role": "declared O(2) quadratic mode roots"},
    )
    eos_evidence = evidence(
        EOS_REL,
        {"role": "tree-level condensate background and phase control"},
    )

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "fixed-background Gaussian finite-temperature determinant of the two O(2) condensate quasiparticle branches",
    )
    append_unique(full_major.setdefault("what_remains_open", []), blocker)
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "thermal background backreaction and self-consistent finite-temperature phase boundary remain open",
    )
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    transport["uet_o2_condensate_gaussian_finite_t_lane"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "mode_records": audit["mode_records"],
        "convergence_records": audit["convergence_records"],
        "convergence_relative_errors": audit["convergence_relative_errors"],
        "finite_difference_checks": audit["finite_difference_checks"],
        "fixed_tree_level_background": True,
        "thermal_background_backreaction_included": False,
        "vacuum_counterterm_included": False,
        "interacting_self_energy_included": False,
        "normal_two_fluid_completion": False,
        "physical_kubo_coefficient_included": False,
        "audit": audit_evidence,
        "implementation": module_evidence,
        "quadratic_spectrum": spectrum_evidence,
        "tree_level_eos": eos_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in (audit_evidence, module_evidence, spectrum_evidence, eos_evidence):
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["uet_o2_condensate_gaussian_finite_t_lane"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["claim_promotion"] = False
    full["next_action"] = "Derive a self-consistent finite-temperature background/effective potential or retain the Gaussian fixed-background boundary; then close normal Kubo/SK/KMS, entropy balance, and independent base-Phi SI calibration."
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
    record["evidence_artifacts"] = [
        audit_evidence,
        module_evidence,
        spectrum_evidence,
        eos_evidence,
    ]
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
        "fixed-background Gaussian finite-temperature O(2) quasiparticle determinant with thermodynamic derivative and convergence checks",
    )
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["uet_o2_condensate_gaussian_finite_t_lane"] = audit_evidence
    partial["uet_o2_condensate_gaussian_finite_t_lane_controller"] = blocker
    partial["uet_o2_condensate_gaussian_finite_t_lane_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Fixed-Background Gaussian Finite-Temperature O(2) Lane (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-032` | `omega_+-^2=k^2+q/Z+2mu^2 +- sqrt((q/Z+2mu^2)^2+4mu^2 k^2)`; `Omega_G=T integral sum_a log(1-exp(-omega_a/T))`; `p_G=-Omega_G`; `epsilon_G=-p_G+T*s_G+mu*n_G` | `{AUDIT_REL}`; `{MODULE_REL}`; `{SPECTRUM_REL}`; `{EOS_REL}` | natural units; `T,mu,omega,k` = energy; `p,s,epsilon` = natural densities; `Phi` fixed action input; no SI map | quadratic O(2) action spectrum plus Gaussian thermal Bose determinant; no external source coefficients | fixed-background finite-T pressure, derivatives, positivity, mode roots, and convergence pass; background backreaction, renormalization, self-energy, transport, and SI remain open | establishes a finite-T action-derived quasiparticle lane without using the standard-fluid comparator as UET transport | Gaussian determinant can be overread as a self-consistent finite-T EOS or two-fluid closure | derive thermal background backreaction/self-consistent phase boundary and match physical normal/Kubo/SK/KMS sectors |

The lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026
holdout. It keeps `C`, `Phi`, `R_gen`, and `R_obs` in their declared roles.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Fixed-Background Gaussian Finite-Temperature O(2) Lane"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared O(2) quadratic radial/Goldstone roots
were used to derive a natural-unit Gaussian Bose determinant on a fixed
tree-level condensed background. Pressure, entropy, generalized chemical
potential response, Phi response derivative, energy identity, mode positivity,
and quadrature/cutoff convergence pass.

WHAT_REMAINS_OPEN: The thermal background is not re-minimized, so the
self-consistent finite-temperature phase boundary and thermal backreaction are
open. Vacuum renormalization, interacting self-energy, normal two-fluid
current, physical Kubo coefficient, microscopic SK/KMS, entropy production,
SI Phi mapping, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Fixed-background Gaussian finite-temperature quasiparticle
lane only. No physical two-fluid, Full Topic 13, Core, Gravity, or external
validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` records the action-derived mode-root, thermal
determinant, finite-difference, convergence, units, ontology, and exclusion
checks; this sync links it into the full gate, register, dependency graph,
formula audit, current report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
q = Z*mu^2 - m_eff(Phi)^2 > 0
omega_+-^2 = k^2 + q/Z + 2*mu^2
               +- sqrt((q/Z + 2*mu^2)^2 + 4*mu^2*k^2)
Omega_G = T integral sum_a log(1-exp(-omega_a/T)) d^3k/(2*pi)^3
p_G = -Omega_G
epsilon_G = -p_G + T*s_G + mu*n_G
```

VERIFICATION: `{audit["status"]}`; pressure, entropy, charge-response,
Phi-response and energy identity checks pass; mode roots are non-negative;
reference quadrature/cutoff convergence is within the declared tolerance. No
source row, target curve, fit, physical Kubo coefficient, or Xie 2026 holdout
is used.

CONTROLLING_BLOCKER: `{blocker}`. The full Topic 13 controller remains the
independent dimensional Phi/SI anchor or `alpha_Phi_K`.

NEXT_ACTION: Derive or source-lock a self-consistent finite-temperature
background/effective potential, then close the normal Kubo/SK/KMS and entropy
sectors while independently obtaining the base-Phi SI anchor.

CLAIM_BOUNDARY: This is an action-derived fixed-background Gaussian
finite-temperature lane in natural units. It is not a self-consistent UET EOS,
finite-temperature two-fluid theory, renormalized loop action, physical
transport result, microscopic SK/KMS match, SI calibration, external
validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Fixed-background Gaussian finite-temperature O(2) lane"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

- Scope: derive the Gaussian thermal Bose determinant of the two O(2) quadratic condensate branches on a fixed tree-level background.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; mode positivity, pressure/entropy/mu/Phi derivatives, energy identity, and quadrature/cutoff convergence pass.
- Result closed: `T13_UET_O2_CONDENSATE_GAUSSIAN_FINITE_T_LANE` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the fixed-background Gaussian thermal determinant is now explicit; thermal background backreaction and self-consistent phase boundary remain open.
- Still open: renormalization, interacting self-energy, normal two-fluid/Kubo, SK/KMS/entropy, SI Phi map, alpha, and Full Topic 13 closure.
- Next controller: derive the self-consistent finite-temperature background or retain this boundary, then close physical normal-sector evidence.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""",
    )

    ledger_marker = "## Topic 13 Fixed-Background Gaussian Finite-Temperature O(2) Lane"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` O(2) Gaussian thermal lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the fixed-background Gaussian finite-T module/audit and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; mode roots, thermodynamic derivatives, energy identity, convergence, and exclusion boundaries pass
- public-safety status: `partial`; no self-consistent finite-T EOS, transport, SI map, or alpha is claimed
- current claim boundary: `T13_UET_O2_CONDENSATE_GAUSSIAN_FINITE_T_LANE` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: close thermal background backreaction/self-consistent phase boundary and physical normal/Kubo evidence
""",
    )

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_T13_UET_O2_CONDENSATE_GAUSSIAN_FINITE_T_LANE",
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
