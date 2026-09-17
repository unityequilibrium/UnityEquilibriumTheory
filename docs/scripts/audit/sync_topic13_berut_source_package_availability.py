"""Integrate the scoped Berut source-boundary result without promotion."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_berut_source_package_availability_boundary.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FOUNDATION_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermodynamic_bridge_foundation_claim_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MANIFEST_REL = "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-20.md"


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
    if audit.get("status") != "PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY":
        raise SystemExit(f"unexpected Berut audit status: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    audit_evidence = evidence(
        AUDIT_REL,
        {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "closure_level": major["closure_level"],
            "numeric_rows_emitted": audit["numeric_rows_emitted"],
            "full_core_unlock": False,
        },
    )

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "Berut source-surface classification and non-calibration boundary")
    for blocker in major["open_blockers"]:
        append_unique(full_major.setdefault("what_remains_open", []), blocker)
    source_lane = full.setdefault("verification_status", {}).setdefault("source_package", {})
    source_lane["berut_source_package_availability_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "source_surface": audit["source_surface"],
        "local_source_inventory": audit["local_source_inventory"],
        "checks": audit["verification_status"],
        "audit": audit_evidence,
        "full_core_unlock": False,
        "controlling_blocker": audit["controlling_blocker"],
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), audit_evidence)
    full.setdefault("data_role", {})["berut_source_package_availability"] = major["data_role"]
    full["berut_source_acquisition_controller"] = audit["controlling_blocker"]
    full["berut_source_next_action"] = audit["next_action"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["claim_promotion"] = False
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
    record["evidence_artifacts"] = [audit_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", []) if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "Berut source-surface classification and non-calibration boundary")
    for blocker in major["open_blockers"]:
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
    partial["berut_source_package_availability_boundary"] = audit_evidence
    partial["berut_source_package_controller"] = audit["controlling_blocker"]
    partial["berut_source_package_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    foundation = load(FOUNDATION_REL)
    foundation["status"] = "FOUNDATION_WARN"
    for export in foundation.get("blocked_foundation_exports", []):
        if export.get("export_id") == "T13_EXPORT_SOURCE_NORMALIZED_LANDAUER_DATASET":
            blockers = export.setdefault("blockers", [])
            append_unique(blockers, audit["controlling_blocker"])
            append_unique(blockers, "Berut Figure 3 binary is archived and figure-derived rows are hash-linked; raw numeric measurement uncertainty remains open")
    for row in foundation.get("row_controller_summary", []):
        if row.get("row_id") == "berut_2012_summary_300K":
            row["source_closure_status"] = "official_figure_binary_archived_figure_derived_rows_raw_numeric_open"
            row["next_controller"] = audit["controlling_blocker"]
            row["first_missing_requirement"] = "permissioned raw numeric package or source-grade measurement uncertainty for the Figure 3 rows"
    foundation["berut_source_boundary_artifact"] = audit_evidence
    (ROOT / FOUNDATION_REL).write_text(json.dumps(foundation, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    marker = "## Berut Source Package Availability Boundary (2026-08-20)"
    section = f"""{marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The Berut working copies in the current checkout are
classified as topic-derived summaries, not raw experimental rows. The captured
publisher surface is recorded as a Figure 3/PPT acquisition route, while the
absence of a local raw or separately exposed source-data package is explicit.

WHAT_REMAINS_OPEN: The official Figure 3 binary/hash, selected panel and axis
mapping, numeric transcription, row identity, preprocessing, and uncertainty
package remain open. No Berut numeric row is eligible for calibration.

DEPENDENCY_UNLOCKED: Berut source-acquisition decision only. No Full Topic 13,
Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` records the source identity, publisher locator,
current local inventory, source-surface scope, and non-calibration policy.

EQUATION_OR_MAPPING: `E_min = k_B T ln(2)` remains an imported standard
constraint. No numeric `Delta_Tq = alpha_Phi_K * Delta_Phi` mapping is emitted.

VERIFICATION: All source identity, summary-role, no-raw-file, surface-scope,
holdout, no-fit, and no-calibration checks pass; accepted numeric rows emitted:
`0`.

CONTROLLING_BLOCKER: `{audit["controlling_blocker"]}`

NEXT_ACTION: {audit["next_action"]}

CLAIM_BOUNDARY: This is a provenance and acquisition boundary, not a closed
Berut numeric row, uncertainty result, `alpha_Phi_K`, UET bridge, or external
validation.
"""
    append_marker(REPORT_REL, marker, section)
    append_marker(FORMULA_REL, marker, section)
    append_marker(LOG_REL, "### 2026-08-12 - Berut source package availability boundary", f"""### 2026-08-12 - Berut source package availability boundary

- Scope: reconcile the Berut source surface with files actually present in the current checkout.
- Added or changed: `{AUDIT_REL}`, the full-gate source-package lane, closure register, dependency evidence, foundation claim gate, formula audit, report, manifest note, update log, and ledger entry.
- Verified with: `{audit["status"]}`; source identity, publisher locator, summary-only role, archived-figure status, no-fit, no-calibration, and holdout checks.
- Result closed: `T13_BERUT_SOURCE_PACKAGE_AVAILABILITY_BOUNDARY` is `CLOSED_FOR_LANE`.
- Blocker narrowed: `{audit["controlling_blocker"]}` now controls the Berut row; the official Figure 3 binary and figure-derived comparison route are archived; raw numeric uncertainty remains open.
- Still open: numeric package, selected-panel ticks/points, preprocessing, uncertainty, `alpha_Phi_K`, and Full Topic 13 closure.
- Next controller: obtain a permissioned raw numeric package or source-grade measurement uncertainty; keep Figure 3c rows outside alpha calibration.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""")
    append_marker(MANIFEST_REL, marker, f"""{marker}

The current checkout audit records the Nature Figure 3/PPT route as a publisher
locator, but no official binary, raw table, or separately exposed source-data
package is stored locally. The two Berut JSON copies remain topic-derived
summary rows and are not calibration-eligible. See `{AUDIT_REL}` for the
source-surface scope, hashes, and next acquisition controller.
""")
    append_marker(LEDGER_REL, "## Topic 13 Berut Source Package Availability Boundary", f"""## Topic 13 Berut Source Package Availability Boundary

- area id: `research-core` (secondary: `data-provenance`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` Berut/Landauer source lane
- changed: added source-surface availability artifact and synchronized full gate, register, dependency gate, foundation claim gate, formula audit, report, manifest, and update log
- verification: `{audit["status"]}`; accepted numeric rows `0`, no fit, no calibration, no Xie holdout
- public-safety status: `partial`; official figure binary is archived, but raw/permissioned numeric measurement uncertainty is not available
- current claim boundary: `T13_BERUT_SOURCE_PACKAGE_AVAILABILITY_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated topic changes were not edited
- next action: archive the permitted Figure 3/numeric source package and complete row-level provenance before calibration use
""")

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_BERUT_SOURCE_BOUNDARY",
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
