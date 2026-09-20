"""Integrate the Berut Figure 3 binary identity without promotion."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_berut_figure3_remote_binary_identity.json"
SOURCE_BOUNDARY_REL = "docs/core/07_artifacts/topic13/t13_berut_source_package_availability_boundary.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
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


def ref(relative: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def append_unique(values: list[Any], value: Any) -> None:
    if value not in values:
        values.append(value)


def append_marker(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    audit = load(AUDIT_REL)
    if audit.get("status") != "PASS_REMOTE_FIGURE3_BINARY_IDENTITY":
        raise SystemExit(f"unexpected binary-identity status: {audit.get('status')}")

    major = audit["major_result"]
    evidence = ref(
        AUDIT_REL,
        {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "closure_level": major["closure_level"],
            "source_sha256": audit["binary_identity"]["sha256"],
            "numeric_rows_emitted": 0,
            "full_core_unlock": False,
        },
    )

    source_boundary = load(SOURCE_BOUNDARY_REL)
    append_unique(
        source_boundary.setdefault("major_result", {}).setdefault("what_is_closed", []),
        "official publisher Figure 3 remote binary identity and embedded-raster inventory",
    )
    source_boundary["remote_binary_identity"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "binary_identity": audit["binary_identity"],
        "embedded_assets": audit["embedded_assets"],
        "audit": evidence,
        "full_core_unlock": False,
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(source_boundary.setdefault("evidence_artifacts", []), evidence)
    source_boundary["claim_promotion"] = False
    (ROOT / SOURCE_BOUNDARY_REL).write_text(
        json.dumps(source_boundary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    full = load(FULL_REL)
    append_unique(
        full.setdefault("major_result", {}).setdefault("what_is_closed", []),
        "official Berut Figure 3 remote binary identity and embedded-raster inventory",
    )
    for blocker in major["open_blockers"]:
        append_unique(full["major_result"].setdefault("what_remains_open", []), blocker)
    source_lane = full.setdefault("verification_status", {}).setdefault("source_package", {})
    source_lane["berut_figure3_remote_binary_identity"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "binary_identity": audit["binary_identity"],
        "embedded_asset_count": len(audit["embedded_assets"]),
        "audit": evidence,
        "full_core_unlock": False,
        "controlling_blocker": audit["controlling_blocker"],
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), evidence)
    full.setdefault("data_role", {})["berut_figure3_remote_binary_identity"] = major["data_role"]
    full["claim_promotion"] = False
    (ROOT / FULL_REL).write_text(
        json.dumps(full, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    register = load(REGISTER_REL)
    register["generated_at"] = date.today().isoformat()
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
    record["evidence_artifacts"] = [evidence]
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
        "official Berut Figure 3 remote binary identity and embedded-raster inventory",
    )
    for blocker in major["open_blockers"]:
        append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(
        json.dumps(register, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = date.today().isoformat()
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["berut_figure3_remote_binary_identity"] = evidence
    partial["berut_figure3_remote_binary_identity_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(
        json.dumps(dependency, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    marker = "## Berut Figure 3 Local Archive (2026-08-20)"
    section = f"""{marker}

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED: The official publisher Figure 3 route was
download-tested. Its remote binary identity is pinned by SHA-256, byte size,
OLE signature, retrieval date, and an explicit four-asset raster inventory.

WHAT_REMAINS_OPEN: No raster is accepted as a numeric row yet. Selected panel,
axis ticks and units, point or curve selection, digitization uncertainty,
preprocessing, and row identity remain open.

DEPENDENCY_UNLOCKED: Berut figure-acquisition route only. No numeric source,
alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: {audit["status"]}

WHAT_CHANGED: {AUDIT_REL} records the official article/download locators,
binary hash {audit["binary_identity"]["sha256"]}, size
{audit["binary_identity"]["bytes"]} bytes, and embedded raster inventory.
The binary is archived locally at the hash-linked raw path; no raw measurement table is implied.

EQUATION_OR_MAPPING: Figure 3 is a source-surface asset for the Berut
heat-versus-erasure-duration observable; no numeric Delta_Tq or alpha_Phi_K
mapping is emitted.

VERIFICATION: Binary identity and asset inventory checks pass; accepted numeric
rows emitted: 0; no fit, target data, calibration, or Xie 2026 holdout was used.

CONTROLLING_BLOCKER: {audit["controlling_blocker"]}

NEXT_ACTION: {audit["next_action"]}

CLAIM_BOUNDARY: Remote binary identity only. This is not a source-normalized
numeric row, uncertainty result, calibration, prediction, or external validation.
"""
    append_marker(REPORT_REL, marker, section)
    append_marker(FORMULA_REL, marker, section)
    append_marker(
        LOG_REL,
        "### 2026-08-20 - Berut Figure 3 local archive",
        (
            "### 2026-08-20 - Berut Figure 3 local archive\n\n"
            "- Scope: verify the official publisher Figure 3 binary route with the official binary archived for provenance.\n"
            f"- Added: {AUDIT_REL}, source-boundary/full-gate evidence, closure register, dependency evidence, formula audit, report, and update log.\n"
            f"- Verified: {audit['status']}; SHA-256 {audit['binary_identity']['sha256']}, {audit['binary_identity']['bytes']} bytes, OLE signature, and four embedded raster identities.\n"
            "- Result closed: T13_BERUT_FIGURE3_REMOTE_BINARY_IDENTITY is CLOSED_FOR_LANE.\n"
            f"- Blocker narrowed: {audit['controlling_blocker']} is now the active Berut controller; no numeric row was accepted.\n"
            "- Claim impact: no promotion; Full Topic 13 remains PARTIAL / BLOCKED.\n"
        ),
    )
    append_marker(
        MANIFEST_REL,
        marker,
        (
            f"{marker}\n\n"
            f"The official publisher Figure 3 route was download-tested on 2026-08-12. "
            f"The remote binary is hash-pinned as {audit['binary_identity']['sha256']} "
            f"with {audit['binary_identity']['bytes']} bytes and four embedded raster identities. "
            f"The binary is archived in the repository; no raw numeric row is accepted until "
            f"panel, axis, point, uncertainty, preprocessing, and row identity are recorded. "
            f"See {AUDIT_REL}.\n"
        ),
    )
    append_marker(
        LEDGER_REL,
        "## Topic 13 Berut Figure 3 Local Archive",
        (
            "## Topic 13 Berut Figure 3 Local Archive\n\n"
            "- area id: research-core (secondary: data-provenance)\n"
            "- workspace: docs/topics/0.13_Thermodynamic_Bridge Berut Figure 3 source route\n"
            f"- verification: {audit['status']}; hash {audit['binary_identity']['sha256']}, {audit['binary_identity']['bytes']} bytes, four embedded assets, no numeric rows\n"
            "- public-safety status: partial; binary identity is pinned and the official binary is archived; no raw numeric row is accepted\n"
            "- current claim boundary: T13_BERUT_FIGURE3_REMOTE_BINARY_IDENTITY is CLOSED_FOR_LANE; Full Topic 13 remains PARTIAL / BLOCKED\n"
            "- next action: obtain raw measurement uncertainty or a permissioned numeric table, and keep figure-derived rows out of calibration\n"
        ),
    )

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_BERUT_FIGURE3_BINARY_IDENTITY",
                "major_result_id": major["major_result_id"],
                "closure_level": major["closure_level"],
                "full_core_unlock": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

