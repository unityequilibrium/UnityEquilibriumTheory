"""Integrate the bounded standard finite-temperature O(2) comparator."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from docs.core.core_paths import canonical_existing_path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_standard_o2_finite_temperature_comparator_audit.json"
MODULE_REL = "docs/core/02_equations/o2/standard_o2_finite_temperature_comparator.py"
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
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
    return hashlib.sha256(canonical_existing_path(ROOT / rel).read_bytes()).hexdigest()


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
    if audit.get("status") != "PASS_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR":
        raise SystemExit(f"standard O(2) comparator is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "finite_temperature_UET_effective_action_and_normal_two_fluid_sector_not_derived"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })
    module_evidence = evidence(MODULE_REL, {
        "data_role": major["data_role"],
        "status": "IMPLEMENTED_DETERMINISTIC_COMPARATOR",
    })
    eos_evidence = evidence(EOS_REL, {
        "status": "TREE_LEVEL_FINITE_DENSITY_O2_MEAN_FIELD_DERIVATION",
        "role": "effective_mass_input_only",
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "standard finite-temperature O(2) normal-branch pressure, charge, entropy, energy, and susceptibility comparator",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "finite-temperature UET effective action and condensate/normal two-fluid sector remain un-derived",
    )
    append_unique(full_major.setdefault("what_remains_open", []), "standard finite-temperature comparator does not supply physical UET Kubo coefficients")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["standard_o2_finite_temperature_normal_comparator"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "domain": audit["major_result"]["units"],
        "state": audit["state"],
        "finite_difference_checks": audit["finite_difference_checks"],
        "physical_uet_eos": False,
        "physical_kubo_coefficient_emitted": False,
        "alpha_Phi_K_emitted": False,
        "si_map_emitted": False,
        "R_gen_used_as_state": False,
        "audit": audit_evidence,
        "implementation": module_evidence,
        "effective_mass_input": eos_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    for item in (audit_evidence, module_evidence, eos_evidence):
        append_unique(full["evidence_artifacts"], item)
    full.setdefault("data_role", {})["standard_o2_finite_temperature_normal_comparator"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Derive or source-lock the finite-temperature UET effective action and normal sector, then acquire physical Kubo coefficients and an independent base-Phi SI anchor; keep the standard O(2) result as a comparator only."
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
    record["evidence_artifacts"] = [audit_evidence, module_evidence, eos_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [item for item in register.get("entries", []) if item.get("major_result_id") != major["major_result_id"]] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "standard finite-temperature O(2) normal-branch thermodynamic comparator is verified as a separate lane")
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
    partial["standard_o2_finite_temperature_normal_comparator"] = audit_evidence
    partial["standard_o2_finite_temperature_normal_comparator_controller"] = blocker
    partial["standard_o2_finite_temperature_normal_comparator_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Standard Finite-Temperature O(2) Normal Comparator (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-026` | `E_k=sqrt(k^2+m_eff(Phi)^2)`; `p_T=T integral [L(E_k-mu)+L(E_k+mu)]`; `n_T=partial p_T/partial mu`; `s_T=partial p_T/partial T`; `epsilon_T=-p_T+T s_T+mu n_T` | `{MODULE_REL}`; `{AUDIT_REL}`; `{EOS_REL}` | natural units; `T,mu,m_eff` = natural energy; `p_T,epsilon_T` = natural energy density; `n_T` = natural charge density; `chi_T` = charge-density per chemical-potential unit | standard free-complex-scalar grand-canonical thermodynamics, with UET `m_eff(Phi)` as an input only | standard comparator gate passes; finite-temperature UET action, condensate/normal sector, physical Kubo, SI map remain open | tests normal-domain positivity, charge/entropy derivatives, even/odd symmetries, and ontology separation | comparator can be mislabeled as UET finite-temperature closure or physical normal component | derive/source-lock UET finite-temperature action and two-fluid sector, then match Kubo/SI observables |

This comparator excludes zero-point and condensate terms and emits no
`alpha_Phi_K`, physical Kubo coefficient, SI scale, `C` relabeling, or `R_gen`
feedback.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Standard Finite-Temperature O(2) Normal Comparator"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A deterministic standard finite-temperature complex-
scalar normal-branch comparator is implemented using the declared UET
`m_eff(Phi)` as an input. Pressure, charge density, entropy density, energy
density, susceptibility, charge symmetry, and pressure-derivative identities
pass in the natural-unit comparator domain.

WHAT_REMAINS_OPEN: This does not derive a finite-temperature UET effective
action, condensate/normal two-fluid sector, physical Kubo coefficient, SI
`Phi` map, or `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Standard thermodynamic comparator lane only. Full Topic 13,
Core, Gravity, and physical constitutive transport remain blocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and its module/EOS hashes are linked into the full
Topic 13 gate, major-result register, dependency gate, formula audit, report,
update log, and work ledger.

EQUATION_OR_MAPPING:

```text
E_k = sqrt(k^2 + m_eff(Phi)^2)
p_T = T integral [L(E_k-mu) + L(E_k+mu)] d^3k/(2 pi)^3
n_T = partial p_T / partial mu
s_T = partial p_T / partial T
epsilon_T = -p_T + T*s_T + mu*n_T
```

VERIFICATION: Normal-branch domain, positivity, even/odd charge symmetry,
finite-difference pressure derivatives, and separation from `C`, `R_gen`,
`R_obs`, `alpha_Phi_K`, Kubo, and SI lanes pass. No target, holdout, or fit is
used.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Derive or source-lock the finite-temperature UET action and normal
sector, then match physical Kubo coefficients and the SI Phi observable map.

CLAIM_BOUNDARY: Standard QFT comparator only. Not a finite-temperature UET EOS,
not a two-fluid derivation, not physical transport, not `alpha_Phi_K`, and not
external validation.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Standard finite-temperature O(2) normal comparator"
    log_content = f"""{log_marker}

- Scope: add a standard finite-temperature normal-branch thermodynamic comparator without promoting it to UET finite-temperature closure.
- Added or changed: `{AUDIT_REL}`, `{MODULE_REL}`, comparator integration in the full gate/register/dependency gate, formula audit, current-state report, and ledger.
- Verified with: `{audit["status"]}`; pressure/charge/entropy/energy/susceptibility are finite and positive, charge parity and pressure derivatives pass, and no SI/Phi/Kubo claim is emitted.
- Result closed: `T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the remaining physical step is explicitly `{blocker}`; Kubo and SI anchor blockers remain separate.
- Still open: finite-temperature UET action, condensate/normal two-fluid sector, physical Kubo coefficient, SI Phi map, alpha_Phi_K, and Full Topic 13 closure.
- Next controller: derive/source-lock the UET finite-temperature sector; retain this output as a standard comparator only.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Standard Finite-Temperature O(2) Comparator"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` standard O(2) comparator and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the finite-temperature normal-branch comparator and synchronized Topic 13 full gate, register, dependency gate, formula audit, report, update log, and ledger
- verification: `{audit["status"]}`; thermodynamic derivative/symmetry checks pass and no UET SI/Kubo/alpha/holdout claim is emitted
- public-safety status: `partial`; standard comparator is not UET finite-temperature closure
- current claim boundary: `T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: derive/source-lock finite-temperature UET action and normal sector, then acquire physical Kubo and SI Phi evidence
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
