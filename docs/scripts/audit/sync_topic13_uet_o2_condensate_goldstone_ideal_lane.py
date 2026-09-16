"""Integrate the T=0 condensate/Goldstone ideal-lane result conservatively."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_goldstone_ideal_lane_audit.json"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
MATTER_REL = "docs/core/02_equations/covariant/uet_covariant_matter.py"
TRANSPORT_REL = "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py"
RESPONSE_REL = "docs/core/02_equations/covariant/uet_covariant_response.py"
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
    if audit.get("status") != "PASS_T0_CONDENSATE_GOLDSTONE_IDEAL_LANE":
        raise SystemExit(f"condensate/Goldstone audit is not passing: {audit.get('status')}")
    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "finite_temperature_normal_component_and_physical_Kubo_coefficient_missing"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })
    source_evidence = [
        evidence(EOS_REL, {"role": "tree-level finite-density O(2) EOS"}),
        evidence(MATTER_REL, {"role": "covariant O(2) action and Noether current"}),
        evidence(TRANSPORT_REL, {"role": "T=0 ideal constitutive and Goldstone interface"}),
        evidence(RESPONSE_REL, {"role": "declared response ontology and action input"}),
    ]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "T=0 tree-level O(2) condensate, Goldstone, Noether-current, and ideal stress mapping")
    append_unique(full_major.setdefault("what_remains_open", []), "the condensate/Goldstone result does not close the finite-temperature normal component or physical Kubo transport")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["uet_o2_condensate_goldstone_ideal_lane"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "finite_difference_checks": audit["finite_difference_checks"],
        "noether_checks": audit["noether_checks"],
        "synthetic_mode_control": audit["synthetic_mode_control"],
        "boundary": audit["boundary"],
        "audit": audit_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    append_unique(full["evidence_artifacts"], audit_evidence)
    full.setdefault("data_role", {})["uet_o2_condensate_goldstone_ideal_lane"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Keep the T=0 ideal condensate lane separate; acquire finite-temperature normal-sector and physical Kubo evidence while independently closing the base-Phi SI anchor and one-loop renormalization boundary."
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
    record["evidence_artifacts"] = [audit_evidence] + source_evidence
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "T=0 tree-level condensate/Goldstone ideal lane with covariant Noether mapping")
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
    partial["uet_o2_condensate_goldstone_ideal_lane"] = audit_evidence
    partial["uet_o2_condensate_goldstone_ideal_lane_controller"] = blocker
    partial["uet_o2_condensate_goldstone_ideal_lane_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## T=0 Condensate and Goldstone Ideal Lane (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-030` | `q=Z mu^2-m_eff^2`; `A^2=q/lambda`; `p=q^2/(4 lambda)`; `N^mu=(Z q/lambda) xi^mu`; `omega_G=+-c_s k` | `{AUDIT_REL}`; `{EOS_REL}`; `{MATTER_REL}`; `{TRANSPORT_REL}` | natural units; `mu,m_eff,xi` = energy; `p` = energy density; O(2) charge/current = natural Noether units; `Phi` remains action response input | declared tree-level O(2) action and covariant phase reduction; no SI anchor or physical Kubo value supplied | T=0 ideal condensate/Goldstone lane passes; finite-T normal and dissipative physics remain open | separates tree-level ideal response from normal component and transport evidence | ideal condensate result can be mislabeled as a full finite-temperature two-fluid theory or physical Kubo closure | derive/source-lock the finite-temperature normal sector and acquire state-matched physical Kubo records; retain SI Phi and renormalization blockers |

Synthetic Kubo controls are used only to exercise the existing linear-mode
control path.  They are not physical transport evidence.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## T=0 Condensate and Goldstone Ideal Lane"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared natural-unit O(2) action closes a
tree-level condensed branch at `T=0`: stationarity, amplitude, pressure, signed
Noether charge, susceptibility, sound speed, canonical Legendre relation,
Josephson phase relation, covariant ideal current/stress, and the tree-level
Goldstone frequency relation are verified together.

WHAT_REMAINS_OPEN: The finite-temperature normal component, interacting
self-energy, two-fluid completion, physical Kubo coefficient, SK/KMS physical
matching, SI `Phi` map, `alpha_Phi_K`, vacuum renormalization, and curved 3+1
remain open. Synthetic Kubo values were used only as a simulation control.

DEPENDENCY_UNLOCKED: T=0 tree-level condensate/Goldstone ideal lane only. No
physical transport, Full Topic 13, Core, or Gravity dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` verifies and records the existing EOS, covariant
Noether current, ideal stress, Josephson, and Goldstone interfaces, then this
sync links the result into the full gate, register, dependency gate, formula
audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
q = Z*mu^2 - m_eff(Phi)^2 > 0
A^2 = q/lambda
p = q^2/(4*lambda)
N^mu = (Z*q/lambda)*xi^mu
T^mu nu = f_s*xi^mu*xi^nu + p*g^mu nu
omega_G = +-c_s*k
```

VERIFICATION: The condensed branch, stationarity, thermodynamic derivatives,
Noether conservation, Josephson relation, current/stress mapping, Goldstone
frequency, finite-temperature rejection boundary, ontology separation, and
holdout policy all pass. No physical coefficient, target fit, or Xie 2026
numeric data is used.

CONTROLLING_BLOCKER: `{blocker}` for this lane; the Full Topic 13 controller
remains the independent dimensional `Phi`/SI anchor or `alpha_Phi_K`.

NEXT_ACTION: Derive or source-lock the finite-temperature normal sector and
state-matched physical Kubo coefficients without turning the synthetic control
into data; keep the SI Phi and renormalization blockers explicit.

CLAIM_BOUNDARY: This is a natural-unit tree-level T=0 ideal lane. It is not a
finite-temperature two-fluid derivation, physical transport validation,
renormalized one-loop theory, SI calibration, external validation, or Full
Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - T=0 condensate and Goldstone ideal lane"
    log_content = f"""{log_marker}

- Scope: audit the existing tree-level condensed O(2) EOS, covariant ideal current/stress, Noether identity, Josephson relation, and Goldstone mode without claiming finite-temperature two-fluid closure.
- Added or changed: `{AUDIT_REL}`, source hashes, full-gate/register/dependency integration, formula audit, report, update log, and ledger.
- Verified with: `{audit["status"]}`; condensed branch `q={audit["reference"]["condensate_control"]}`, `c_s^2={audit["reference"]["sound_speed_sq"]}`, and all declared checks pass.
- Result closed: `T13_UET_O2_CONDENSATE_GOLDSTONE_IDEAL_LANE` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the T=0 ideal lane is separated from the still-open finite-temperature normal and physical Kubo sectors.
- Still open: normal component, interacting finite-T self-energy, physical Kubo, SI Phi map, alpha, vacuum renormalization, curved 3+1, and Full Topic 13 closure.
- Next controller: derive/source-lock the finite-temperature normal sector and physical coefficient record; do not promote synthetic mode controls.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 T=0 Condensate and Goldstone Ideal Lane"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` O(2) finite-density/ideal superfluid lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added condensate/Goldstone/Noether ideal-lane audit and synchronized full gate, register, dependency gate, formula audit, report, and update log
- verification: `{audit["status"]}`; stationarity, derivatives, current/stress mapping, Josephson, Goldstone, and boundary checks pass
- public-safety status: `partial`; T=0 ideal result is not finite-temperature physical transport
- current claim boundary: `T13_UET_O2_CONDENSATE_GOLDSTONE_IDEAL_LANE` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: derive/source-lock finite-temperature normal response and acquire physical Kubo evidence while retaining SI Phi and renormalization blockers
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_T0_CONDENSATE_GOLDSTONE_IDEAL_LANE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
