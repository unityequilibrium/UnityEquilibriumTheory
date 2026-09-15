"""Attach the Ding 2022 source-mapping audit to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
AUDIT = ROOT / "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    audit_path = rel(AUDIT)
    audit_hash = sha256(AUDIT)
    source = gate["verification_status"]["source_package"]
    normalized_source_ready = bool(audit.get("checks", {}).get("permitted_figure_numeric_route_ready"))
    raw_author_source_ready = bool(audit.get("checks", {}).get("raw_author_numeric_source_present"))
    source_ready = raw_author_source_ready
    blocker = audit.get("controlling_blocker") or (
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    )
    source["status"] = audit.get("status")
    source["source_status"] = (
        "FIGURE_DERIVED_PERMITTED_WITH_CLOSED_MAPPING"
        if normalized_source_ready
        else "RAW_AUTHOR_NUMERIC_SOURCE_OPEN"
    )
    raw_author_numeric_source_present = bool(
        audit["checks"].get("raw_author_numeric_source_present")
    )
    # A permitted figure route is usable for normalized comparison,
    # but it is not the raw author numeric package required by the
    # Full Topic 13 source gate.
    source["figure_derived_numeric_route_ready"] = normalized_source_ready
    source["source_ready_for_full_closure"] = raw_author_numeric_source_present
    source["provisional_source_present"] = not raw_author_source_ready
    source["normalized_comparison_route_ready"] = normalized_source_ready
    source["raw_author_numeric_source_present"] = raw_author_numeric_source_present
    source["numeric_fitting_allowed"] = False
    source["source_mapping_audit_status"] = audit.get("status")
    source["source_mapping_audit_artifact"] = {
        "path": audit_path,
        "sha256": audit_hash,
    }
    source["controlling_blocker"] = blocker

    old_source_blockers = {
        "ttg_numeric_source_package_is_provisional",
        "ding_2022_figure_series_mapping_unresolved_or_raw_source_permission_missing",
    }
    remains = gate["major_result"].setdefault("what_remains_open", [])
    remains[:] = [item for item in remains if item not in old_source_blockers]
    if normalized_source_ready:
        closed_source_result = (
            "permitted Ding 2022 figure-derived normalized source with closed printed-legend mapping"
        )
        closed = gate["major_result"].setdefault("what_is_closed", [])
        if closed_source_result not in closed:
            closed.append(closed_source_result)
        provisional_blocker = "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
        if provisional_blocker not in remains:
            remains.insert(0, provisional_blocker)
        blocker = provisional_blocker
        gate["next_action"] = (
            "Acquire Ding raw-author or accepted independently reproduced PBTE C_src(T) rows with "
            "units and uncertainty, then derive alpha_Phi_K or create an independent calibration "
            "record using training/calibration data only; do not read or tune on Xie 2026."
        )
    else:
        remains.insert(0, blocker)
        gate["next_action"] = (
            "Capture a permitted numeric TTG route or close the Ding 2022 color-to-grating-period "
            "mapping from a source-backed locator; then close independent alpha_Phi_K calibration "
            "without reading Xie 2026."
        )
    gate["controlling_blocker"] = blocker
    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != audit_path]
    evidence.append(
        {
            "path": audit_path,
            "sha256": audit_hash,
            "summary": {
                "status": audit.get("status"),
                "controlling_blocker": audit.get("controlling_blocker"),
                "source_route_ready_for_full_closure": source_ready,
        "normalized_comparison_route_ready": normalized_source_ready,
        "raw_author_numeric_source_present": raw_author_source_ready,
                "raw_author_numeric_source_present": audit["checks"].get(
                    "raw_author_numeric_source_present"
                ),
                "permitted_figure_numeric_route_ready": audit["checks"].get(
                    "permitted_figure_numeric_route_ready"
                ),
                "color_to_period_mapping_closed": audit["checks"].get(
                    "color_to_period_mapping_closed"
                ),
            },
        }
    )
    gate["claim_promotion"] = False
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": gate["status"],
        "controlling_blocker": gate["controlling_blocker"],
        "source_mapping_status": audit.get("status"),
        "source_route_ready_for_full_closure": source_ready,
        "artifact": audit_path,
    }, indent=2))
    return 0 if audit.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
