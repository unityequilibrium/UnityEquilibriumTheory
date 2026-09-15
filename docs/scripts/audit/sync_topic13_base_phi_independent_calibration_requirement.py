"""Integrate the open base-Phi calibration requirement into Topic 13 records."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json"
PROTOCOL_REL = "docs/topics/0.13_Thermodynamic_Bridge/BASE_PHI_INDEPENDENT_CALIBRATION_PROTOCOL.md"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-11.md"


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
    action = load(ACTION_REL)
    if action.get("status") != "PASS_OPEN_CALIBRATION_REQUIREMENT":
        raise SystemExit(f"calibration requirement audit is not passing: {action.get('status')}")

    today = date.today().isoformat()
    major = action["major_result"]
    blocker = action["controlling_blocker"]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major["what_is_closed"], "independent base-Phi calibration acceptance contract is machine-readable")
    append_unique(full_major["what_remains_open"], blocker)
    append_unique(full_major["what_remains_open"], "base_Phi_to_Phi_E_mapping_not_derived")
    full.setdefault("verification_status", {})["base_phi_independent_calibration_requirement"] = {
        "status": "OPEN_REQUIREMENT",
        "closure_level": "OPEN",
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "required_record_fields": action["required_record_fields"],
        "audit": evidence(ACTION_REL, {"status": action["status"], "major_result_id": major["major_result_id"]}),
        "controlling_blocker": blocker,
        "claim_boundary": action["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), evidence(ACTION_REL, {"status": action["status"], "data_role": major["data_role"]}))
    full["next_action"] = "Use the machine-readable base-Phi calibration protocol to obtain a permitted independent paired record; then derive base Phi-to-Phi_E and alpha_Phi_K without TTG residuals or Xie 2026."
    full["claim_promotion"] = False
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "independent base-Phi calibration acceptance contract is machine-readable")
    append_unique(full_entry["open_blockers"], blocker)
    append_unique(full_entry["open_blockers"], "base_Phi_to_Phi_E_mapping_not_derived")
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": major["major_result_id"]}))
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)

    requirement_entry = next((item for item in register["entries"] if item.get("major_result_id") == major["major_result_id"]), None)
    record = {key: major[key] for key in ("major_result_id", "topic", "closure_level", "what_is_closed", "equation_or_mapping", "units", "derivation_class", "observable", "data_role", "evidence_artifacts", "verification_status", "open_blockers", "dependency_unlocked", "claim_boundary")}
    record["evidence_artifacts"] = [evidence(ACTION_REL, {"status": action["status"]})]
    if requirement_entry is None:
        register["entries"].append(record)
    else:
        requirement_entry.clear()
        requirement_entry.update(record)
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["base_phi_independent_calibration_requirement"] = evidence(
        ACTION_REL,
        {"status": action["status"], "full_core_unlock": False, "closure_level": "OPEN"},
    )
    partial["base_phi_calibration_controller"] = blocker
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Base-Phi Independent Calibration Requirement (2026-08-11)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-020` | `Phi_E = Delta_u/e0`; `Phi_E = s_material Phi_base`; `alpha_Phi_K = (e0/c_v) s_material` | `{ACTION_REL}`; `{PROTOCOL_REL}` | `Delta_u,e0` = J m^-3; `c_v` = J m^-3 K^-1; `Phi_E,Phi_base,s_material` = dimensionless; `alpha_Phi_K` = K per normalized base Phi | protocol-defined calibration bridge; no numerical constant supplied | open requirement, not a derivation or calibration | defines the minimum independent paired record needed before a base-Phi SI observable map can be considered | a named Phi_E coordinate or a TTG residual can be mistaken for a base-Phi calibration | obtain the paired record with locator, units, uncertainty, preprocessing, row identity, hash, and independence statement; then rerun the locked calibration audit |

The protocol is an acceptance contract only. It does not identify base `Phi`
with `Phi_E`, temperature, heat flux, entropy, or `R_gen`, and it emits no
numeric `alpha_Phi_K`."""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Base-Phi Calibration Controller"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `OPEN`

WHAT_IS_ACTUALLY_CLOSED: The admissible independent calibration route is now a
machine-readable acceptance contract with required provenance, units,
uncertainty, row identity, and holdout restrictions.

WHAT_REMAINS_OPEN: No paired base-`Phi` amplitude and SI observable record is
available. The named `Phi_E` reference lane remains separate from base `Phi`.

DEPENDENCY_UNLOCKED: None. Full Topic 13, Core curved 3+1, and Gravity remain
blocked by this and the remaining thermodynamic closure gates.

STATUS: `OPEN_INDEPENDENT_BASE_PHI_CALIBRATION_REQUIRED`

WHAT_CHANGED: `{ACTION_REL}` is linked into the full gate, major-result
register, dependency gate, and formula audit.

EQUATION_OR_MAPPING:

```text
Phi_E = Delta_u / e0
Phi_E = s_material * Phi_base
alpha_Phi_K = (e0 / c_v) * s_material
Delta_Tq = alpha_Phi_K * Delta_Phi_base
```

VERIFICATION: The contract audit passes its required-field and forbidden-input
checks. No source rows, TTG residuals, numeric target curve, parameter fit, or
Xie 2026 holdout was consumed.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Obtain a permitted independent paired base-`Phi`/SI record or a
derived base-`Phi` to `Phi_E` map, then run the preregistered calibration without
post-inspection tuning.

CLAIM_BOUNDARY: This is a protocol result, not a calibration result. It emits
no numerical `alpha_Phi_K`, prediction, external validation, or full Topic 13
closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-11 - Base-Phi independent calibration requirement"
    log_content = f"""{log_marker}

- Scope: narrow the controlling dimensional/calibration blocker without selecting a base-Phi scale.
- Wave type: gate pass / claim-boundary pass.
- Added or changed: `{ACTION_REL}`, a Topic 13 integration sync, a formula-audit entry, and linked full-gate/register/dependency/report records.
- Verified with: `PASS_OPEN_CALIBRATION_REQUIREMENT`; required paired-source fields and forbidden TTG/Xie/tuning inputs are explicit.
- Result: the calibration acceptance route is machine-readable at `OPEN`; no alpha value was produced.
- Blocker narrowed: the vague dimensional-anchor gap is now `independent_paired_base_Phi_amplitude_and_SI_observable_record_missing`.
- Still open: base-Phi to Phi_E mapping, e0/c_v calibration inputs, alpha_Phi_K, and EOS/transport/KMS/entropy closure.
- Next controller: obtain a permitted paired record or derive the base-Phi map independently; do not use Phi_E coordinate normalization as base-Phi calibration.
- Claim impact: no promotion; Xie 2026 remains metadata-only and untouched.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Base-Phi Calibration Requirement"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` calibration records
- changed: added the open calibration requirement artifact, integration sync, formula record, report section, and update-log entry
- verification: `PASS_OPEN_CALIBRATION_REQUIREMENT`; no source rows, fit, target curve, numeric alpha, or Xie 2026 holdout was consumed
- public-safety status: `partial`; the route is machine-readable but the physical base-Phi calibration is absent
- current claim boundary: `T13_BASE_PHI_INDEPENDENT_CALIBRATION_REQUIREMENT` is `OPEN`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: obtain a permitted paired base-Phi/SI record or derive the base-Phi-to-Phi_E map independently
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_OPEN_BASE_PHI_CALIBRATION_REQUIREMENT",
        "major_result_id": major["major_result_id"],
        "closure_level": "OPEN",
        "full_topic13_status": full["status"],
        "full_gate_sha256": digest(FULL_REL),
        "register_sha256": digest(REGISTER_REL),
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
