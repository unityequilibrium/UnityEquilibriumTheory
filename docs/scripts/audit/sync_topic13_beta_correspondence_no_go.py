"""Integrate the scoped action-beta to beta_T13 correspondence no-go."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_beta_action_normalized_correspondence_no_go.json"
MODULE_REL = "docs/core/02_equations/o2/uet_o2_beta_correspondence.py"
CURVATURE_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_normal_response_curvature_audit.json"
BETA_REL = "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json"
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
    expected = "PASS_SCOPED_NO_GO_ACTION_BETA_T13_CORRESPONDENCE"
    if audit.get("status") != expected:
        raise SystemExit(f"beta correspondence audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = audit["controlling_blocker"]
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })
    module_evidence = evidence(MODULE_REL, {"role": "scale-witness correspondence boundary"})
    curvature_evidence = evidence(CURVATURE_REL, {"role": "action-derived natural beta input"})
    beta_evidence = evidence(BETA_REL, {"role": "normalized beta_T13 candidate contract"})
    all_evidence = [audit_evidence, module_evidence, curvature_evidence, beta_evidence]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "scoped no-go for identifying action-derived natural beta with normalized beta_T13 without a declared scale map")
    append_unique(full_major.setdefault("what_remains_open", []), "declared field/free-energy/temperature normalization and source-backed beta_T13 coefficient are missing")
    bridge = full.setdefault("verification_status", {}).setdefault("non_circular_bridge", {})
    bridge["beta_action_normalized_correspondence_no_go"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "input_records": audit["input_records"],
        "scale_witnesses": audit["scale_witnesses"],
        "checks": audit["checks"],
        "audit": audit_evidence,
        "implementation": module_evidence,
        "action_curvature": curvature_evidence,
        "normalized_beta_contract": beta_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["beta_action_normalized_correspondence_no_go"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["claim_promotion"] = False
    full["next_action"] = "Declare the field/free-energy/natural-to-Kelvin scale map or obtain an independent source-backed beta_T13 coefficient; do not relabel the action-derived natural slope or use holdout fitting."
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
    append_unique(full_entry.setdefault("what_is_closed", []), "scoped action-beta to normalized beta_T13 correspondence no-go")
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["beta_action_normalized_correspondence_no_go"] = audit_evidence
    partial["beta_action_normalized_correspondence_no_go_controller"] = blocker
    partial["beta_action_normalized_correspondence_no_go_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Action-Beta to Normalized beta_T13 Correspondence No-Go (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-036` | `beta_action_natural=T*partial_T(partial_Phi^2 Omega_T)` versus `beta_T13=T0*(da_Phi/dT)|T0`; required `beta_T13=F(field_normalization,free_energy_scale,temperature_unit,beta_action_natural)` | `{AUDIT_REL}`; `{MODULE_REL}`; `{CURVATURE_REL}`; `{BETA_REL}` | action beta = natural mass dimension two; normalized beta = dimensionless local K-slope; `alpha_Phi_K` remains K per normalized Phi | action-derived curvature and declared candidate normalized functional have separate origins; scale map is not declared | scoped correspondence no-go passes with two distinct positive scale witnesses and no inferred physical coefficient | prevents relabeling an action slope as beta_T13 before field, energy, and Kelvin normalization are declared | scale witnesses could be mistaken for calibration if the map is silently chosen | derive/source-lock the missing scale map and beta coefficient independently of target fitting and Xie 2026 |

The no-go uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Action-Beta to Normalized beta_T13 Correspondence Boundary"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO`

WHAT_IS_ACTUALLY_CLOSED: The natural-unit normal-branch action slope and the
named normalized `beta_T13` contract are not numerically identifiable from
the current records. They have different units and derivation origins. Two
distinct positive field/free-energy/temperature scale completions preserve the
current normalized beta witness while leaving the physical correspondence
undefined. The no-go closes the structural question only.

WHAT_REMAINS_OPEN: A declared field normalization, free-energy density scale,
natural-to-Kelvin map, and source-backed `beta_T13` coefficient are missing.
The independent Phi/SI anchor, `alpha_Phi_K`, renormalized finite-temperature
action, transport, SK/KMS, and entropy closure are also open.

DEPENDENCY_UNLOCKED: Correspondence no-go only. No beta value, SI map,
physical transport, Full Topic 13, Core, Gravity, or external-validation
dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add explicit scale witnesses
and a unit/derivation comparison between the action-derived curvature and the
normalized beta contract; this sync links them into the bridge gate, register,
dependency graph, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
beta_action_natural = T * partial_T(partial_Phi^2 Omega_T)
beta_T13 = T0 * (da_Phi/dT)|T0
beta_T13 = F(field_normalization, free_energy_scale,
             temperature_unit, beta_action_natural)
```

VERIFICATION: `{audit["status"]}`; the action lane, normalized contract,
Phi-anchor no-go, distinct scale witnesses, and no-holdout checks pass. No
numeric beta, alpha, e0, Kelvin prediction, or target fit is emitted.

CONTROLLING_BLOCKER: `{blocker}`. The Full Topic 13 controller remains the
independent dimensional Phi/SI anchor or `alpha_Phi_K` route.

NEXT_ACTION: Derive or source-lock the missing scale map and beta coefficient
from an independent finite-temperature action or source, then test EOS,
transport, KMS, entropy, and dissipation without using Xie 2026.

CLAIM_BOUNDARY: This is a scoped structural correspondence no-go. It is not a
physical beta measurement, SI calibration, transport coefficient, external
validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Action-beta to normalized beta_T13 correspondence no-go"
    append_marker(LOG_REL, log_marker, f"""{log_marker}

- Scope: test whether the action-derived natural-unit normal response slope can be identified with the named normalized `beta_T13` contract.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key/placement repairs, bridge-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; unit/derivation comparison, two distinct positive scale witnesses, Phi-anchor linkage, and no-holdout checks pass.
- Result closed: `T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO` is `CLOSED_AS_NO_GO`.
- Blocker narrowed: a normalized beta correspondence requires an explicit field, free-energy, and natural-to-Kelvin scale map; the action slope is not relabeled as beta_T13.
- Still open: source-backed beta coefficient, Phi/SI anchor, alpha, renormalized finite-T action, EOS/transport/KMS/entropy, and Full Topic 13 closure.
- Next controller: derive/source-lock the missing scale map and coefficient independently of TTG target fitting and Xie 2026.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""")

    ledger_marker = "## Topic 13 Action-Beta to Normalized beta_T13 Correspondence No-Go"
    append_marker(LEDGER_REL, ledger_marker, f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` beta correspondence lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added scale-witness no-go and synchronized bridge gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; unit/derivation separation, distinct scale completions, and holdout exclusion pass
- public-safety status: `partial`; no physical beta, alpha, SI map, transport, or external claim is made
- current claim boundary: `T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO` is `CLOSED_AS_NO_GO`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: derive/source-lock the missing field/free-energy/Kelvin scale map and beta coefficient independently
""")

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
