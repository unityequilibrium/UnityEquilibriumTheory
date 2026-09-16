"""Integrate the Topic 13 physical Kubo provenance gate conservatively."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_physical_kubo_coefficient_provenance_audit.json"
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
    if audit.get("status") != "PASS_KUBO_PROVENANCE_GATE_OPEN_PHYSICAL_COEFFICIENT":
        raise SystemExit(f"Kubo provenance audit is not passing: {audit.get('status')}")
    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "physical_Kubo_coefficient_record_missing"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"].setdefault("what_is_closed", []), "physical Kubo coefficient provenance and acceptance gate is explicit")
    append_unique(full["major_result"].setdefault("what_remains_open", []), blocker)
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["physical_kubo_coefficient_provenance"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "numeric_transport_coefficient_emitted": False,
        "synthetic_controls_physical": False,
        "audit": audit_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), audit_evidence)
    full.setdefault("data_role", {})["physical_kubo_coefficient_provenance"] = "READINESS_GATE_ONLY_NO_COEFFICIENT_DATA"
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Acquire a state-matched physical Kubo coefficient record and an independent base-Phi SI anchor; rerun the transport and dimensional gates without promoting synthetic controls."
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
    record["evidence_artifacts"] = [audit_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [item for item in register.get("entries", []) if item.get("major_result_id") != major["major_result_id"]] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "physical Kubo coefficient provenance and acceptance gate is explicit")
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
    partial["physical_kubo_coefficient_provenance"] = audit_evidence
    partial["physical_kubo_coefficient_controller"] = blocker
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Physical Kubo Coefficient Provenance Gate (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-023` | `KuboCoefficientRecord -> constitutive coefficient` only when matched evidence passes | `{AUDIT_REL}`; `docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py` | value and coefficient units are source-specific; temperature, chemical potential, response state, correlator locator, source path, and hash are required | external/microscopic input required; no value supplied | provenance gate passes; physical coefficient remains open | separates readiness/formula sources from physical coefficient evidence and synthetic controls | a structural Kubo source or synthetic value can be misreported as a physical UET transport coefficient | acquire one state-matched coefficient record and rerun transport/state/unit checks |

The gate does not derive a coefficient from the conservative action and does
not use synthetic controls, TTG target data, or Xie 2026 as physical evidence.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Physical Kubo Coefficient Provenance Controller"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The required state-matched Kubo coefficient record
fields and evidence statuses are now machine-readable, and all existing
external transport records are classified as readiness/structure sources only.

WHAT_REMAINS_OPEN: No accepted physical coefficient record is present. The
transport verifier remains `physical_coefficient_evidence=BLOCKED_NOT_PROVIDED`;
finite-temperature normal response and curved 3+1 transport remain open.

DEPENDENCY_UNLOCKED: Kubo coefficient acceptance gate only. Full Topic 13 and
downstream Core/Gravity dependencies remain blocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` is linked into the Topic 13 transport gate,
major-result register, dependency gate, formula audit, report, and update log.

EQUATION_OR_MAPPING:

```text
KuboCoefficientRecord -> constitutive coefficient
```

VERIFICATION: Required value/unit/state/correlator/hash fields are checked;
synthetic controls are not promoted; no numeric coefficient, target curve, or
Xie 2026 holdout was used.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Acquire or microscopically derive one accepted state-matched
coefficient record, then rerun the transport verifier.

CLAIM_BOUNDARY: This closes a provenance gate only. It is not a physical
transport result, Kubo match, finite-temperature completion, alpha calibration,
or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Physical Kubo coefficient provenance gate"
    log_content = f"""{log_marker}

- Scope: audit the physical transport coefficient evidence boundary after the formal SK/KMS/entropy interface wave.
- Added or changed: `{AUDIT_REL}`, source-readiness inventory, transport integration sync, formula-audit record, Full Topic 13 gate/register/dependency evidence, and current-state report.
- Verified with: `{audit["status"]}`; required coefficient fields match the implementation, all five external records are structure/readiness only, and synthetic controls remain non-physical.
- Result closed: `T13_PHYSICAL_KUBO_COEFFICIENT_PROVENANCE_GATE` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the missing transport input is now explicit as `{blocker}` rather than an implicit default.
- Still open: physical coefficient value, finite-temperature normal component, curved 3+1 transport, base-Phi SI anchor, alpha_Phi_K, and full bridge closure.
- Next controller: acquire or microscopically derive one state-matched coefficient record; do not promote synthetic or formula-only sources.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Physical Kubo Provenance Gate"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` transport records
- changed: added the physical Kubo provenance audit and synchronized Topic 13 full gate, register, dependency gate, formula audit, report, and update log
- verification: `{audit["status"]}`; no physical coefficient value, synthetic promotion, target fit, or Xie 2026 access
- public-safety status: `partial`; readiness sources are not coefficient data
- current claim boundary: `T13_PHYSICAL_KUBO_COEFFICIENT_PROVENANCE_GATE` is `CLOSED_FOR_LANE`; physical transport remains blocked
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: acquire one accepted state-matched coefficient record and rerun the physical transport gate
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_PHYSICAL_KUBO_PROVENANCE_GATE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "full_topic13_status": full["status"],
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
