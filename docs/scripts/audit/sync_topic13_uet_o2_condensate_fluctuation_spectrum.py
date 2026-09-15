"""Integrate the fixed-Phi tree-level condensate fluctuation spectrum."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_fluctuation_spectrum_audit.json"
MODULE_REL = "docs/core/uet_o2_condensate_fluctuations.py"
EOS_REL = "docs/core/uet_o2_finite_density_eos.py"
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
    if audit.get("status") != "PASS_T0_QUADRATIC_FLUCTUATION_SPECTRUM":
        raise SystemExit(f"quadratic spectrum audit is not passing: {audit.get('status')}")
    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "finite_temperature_normal_component_and_interacting_self_energy_not_derived"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })
    module_evidence = evidence(MODULE_REL, {
        "role": "fixed-Phi tree-level condensate fluctuation determinant",
        "data_role": major["data_role"],
    })
    eos_evidence = evidence(EOS_REL, {
        "role": "independent tree-level EOS sound-speed reference",
        "sound_speed_sq": audit["reference"]["eos_sound_speed_sq"],
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "fixed-Phi tree-level radial/Goldstone determinant and low-k sound-speed match")
    append_unique(full_major.setdefault("what_remains_open", []), "quadratic T=0 spectrum does not derive finite-temperature self-energy or normal transport")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["uet_o2_condensate_fluctuation_spectrum"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "reference": audit["reference"],
        "mode_records": audit["mode_records"],
        "determinant_residual_max_abs": audit["determinant_residual_max_abs"],
        "audit": audit_evidence,
        "implementation": module_evidence,
        "eos_reference": eos_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    append_unique(full["evidence_artifacts"], audit_evidence)
    full.setdefault("data_role", {})["uet_o2_condensate_fluctuation_spectrum"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Use the verified T=0 spectrum as a boundary condition only; derive/source-lock finite-temperature self-energy and normal response while pursuing physical Kubo and independent base-Phi SI evidence."
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
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "fixed-Phi T=0 radial/Goldstone spectrum with determinant and EOS slope checks")
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
    partial["uet_o2_condensate_fluctuation_spectrum"] = audit_evidence
    partial["uet_o2_condensate_fluctuation_spectrum_controller"] = blocker
    partial["uet_o2_condensate_fluctuation_spectrum_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## T=0 Condensate Fluctuation Spectrum (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-031` | `det M=(omega^2-k^2)(omega^2-k^2-2q/Z)-4 mu^2 omega^2=0`; `omega_+-^2=k^2+q/Z+2mu^2 +- sqrt((q/Z+2mu^2)^2+4mu^2 k^2)` | `{AUDIT_REL}`; `{MODULE_REL}`; `{EOS_REL}` | natural units; `omega,k,mu` = energy; `Phi` fixed response input; no SI map | quadratic expansion of the declared O(2) action at fixed Phi | determinant roots and low-k EOS matching pass; finite-T self-energy and transport remain open | checks the action spectrum independently of synthetic Kubo controls | T=0 roots can be misread as a normal-fluid or finite-T transport derivation | source-lock/derive finite-T self-energy and normal response; retain SI and renormalization blockers |

The low branch is a Goldstone mode only in the declared condensed T=0 lane;
the high branch is the mixed radial/phase mode and is not a separate physical
particle claim.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## T=0 Condensate Fluctuation Spectrum"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: At fixed `Phi`, the declared O(2) action gives a
tree-level quadratic radial/phase determinant around the condensed background.
Both roots are non-negative over the declared wavenumber sweep, the
zero-momentum low root is Goldstone, the determinant residual is at most
`{audit["determinant_residual_max_abs"]:.3e}`, and the low-k slope agrees with
the independent EOS sound speed.

WHAT_REMAINS_OPEN: Finite-temperature self-energy, normal component, dissipative
transport, physical Kubo coefficients, vacuum renormalization, SI `Phi` map,
`alpha_Phi_K`, and external validation remain open.

DEPENDENCY_UNLOCKED: Fixed-Phi natural-unit T=0 spectrum only. No finite-
temperature normal, physical transport, Full Topic 13, Core, or Gravity unlock.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add and verify the fixed-Phi
quadratic determinant; this sync links the result into the full gate, register,
dependency gate, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
det M = (omega^2-k^2)(omega^2-k^2-2q/Z) - 4*mu^2*omega^2
omega_+-^2 = k^2 + q/Z + 2*mu^2
               +- sqrt((q/Z + 2*mu^2)^2 + 4*mu^2*k^2)
lim(k->0) omega_-^2/k^2 = c_s^2
```

VERIFICATION: Determinant residual max is `{audit["determinant_residual_max_abs"]:.3e}`;
low-k Goldstone slope is `{audit["reference"]["low_k_goldstone_slope"]:.6f}` versus
EOS `c_s^2={audit["reference"]["eos_sound_speed_sq"]:.6f}`. `Phi` is held fixed;
no target, holdout, alpha fit, or physical Kubo value is used.

CONTROLLING_BLOCKER: `{blocker}`; Full Topic 13 still controls on the independent
dimensional `Phi`/SI anchor or `alpha_Phi_K`.

NEXT_ACTION: Match this boundary to a declared finite-temperature effective
action without inventing self-energy terms, then acquire state-matched physical
Kubo evidence and independent base-Phi calibration.

CLAIM_BOUNDARY: This is a fixed-Phi natural-unit T=0 tree-level spectrum. It is
not a finite-temperature two-fluid theory, renormalized loop result, physical
transport validation, SI calibration, external validation, or Full Topic 13
closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - T=0 condensate fluctuation spectrum"
    log_content = f"""{log_marker}

- Scope: derive and verify the fixed-Phi tree-level radial/Goldstone quadratic determinant around the condensed O(2) background.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, source hashes, full-gate/register/dependency integration, formula audit, report, update log, and ledger.
- Verified with: `{audit["status"]}`; determinant residual `{audit["determinant_residual_max_abs"]:.3e}` and low-k slope/EOS sound-speed agreement.
- Result closed: `T13_UET_O2_CONDENSATE_FLUCTUATION_SPECTRUM` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the T=0 spectrum is independently bounded; finite-T self-energy and normal response are not inferred from it.
- Still open: finite-T normal component, interacting self-energy, physical Kubo, SI Phi map, alpha, vacuum renormalization, and Full Topic 13 closure.
- Next controller: derive/source-lock finite-T self-energy and normal response; retain the spectrum as a boundary condition only.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 T=0 Condensate Fluctuation Spectrum"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` fixed-Phi O(2) condensate fluctuation lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added quadratic radial/Goldstone spectrum module and audit; synchronized full gate, register, dependency gate, formula audit, report, and update log
- verification: `{audit["status"]}`; determinant residual `{audit["determinant_residual_max_abs"]:.3e}`; low-k EOS match passes
- public-safety status: `partial`; spectrum is T=0 tree-level evidence, not finite-temperature transport
- current claim boundary: `T13_UET_O2_CONDENSATE_FLUCTUATION_SPECTRUM` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: derive/source-lock finite-T self-energy and normal response; acquire physical Kubo and independent base-Phi SI evidence
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_T0_QUADRATIC_FLUCTUATION_SPECTRUM",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
