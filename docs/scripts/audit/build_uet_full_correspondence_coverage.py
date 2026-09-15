"""Build a row-complete but claim-conservative correspondence coverage artifact."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
FORMULA_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"
REGISTRY_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
ACTIVE_CONTRACT_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_active_correspondence_contract.json"
OUTPUT = ROOT / "docs/core/07_artifacts/correspondence/uet_full_correspondence_coverage.json"


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def registry_index(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry.get("equation_id"): entry for entry in registry.get("entries", []) if entry.get("equation_id")}


def counterpart_status(status: str) -> str:
    if status == "STANDARD_COUNTERPART_NOT_UET_DERIVATION":
        return "DECLARED_STANDARD_COUNTERPART_NOT_UET_DERIVATION"
    if status == "LEGACY_OR_COMPARATOR":
        return "LEGACY_OR_COMPARATOR"
    if status in {"UET_BRIDGE_OPEN", "OPEN_CORRESPONDENCE_REVIEW"}:
        return "OPEN_MANUAL_CORRESPONDENCE_REVIEW"
    return "UNCLASSIFIED_CORRESPONDENCE_REVIEW"


def build() -> dict[str, Any]:
    formulas = load(FORMULA_PATH)
    registry = load(REGISTRY_PATH)
    active_contract = load(ACTIVE_CONTRACT_PATH)
    active_index = {row.get("formula_id"): row for row in active_contract.get("rows", [])}
    index = registry_index(registry)
    rows: list[dict[str, Any]] = []
    correspondence_counts: Counter[str] = Counter()
    unit_counts: Counter[str] = Counter()
    observable_counts: Counter[str] = Counter()
    linked_count = 0
    open_count = 0

    for source in formulas.get("records", []):
        formula_id = source.get("formula_id")
        entry = index.get(formula_id)
        active = active_index.get(formula_id)
        declared_status = source.get("correspondence_status", "OPEN_CORRESPONDENCE_REVIEW")
        if active:
            map_status = active.get("status", "OPEN_UET_CANDIDATE_MAPPING")
            standard_counterpart = active.get("standard_counterpart")
            observable_mapping = {"status": active.get("observable_status", "OPEN_UNRESOLVED"), "operator": active.get("observable_operator") }
            unit_lane = active.get("unit_lane", "UNRESOLVED_FROM_ACTIVE_CONTRACT")
            derivation_class = active.get("derivation_class", "UNDECLARED")
        elif entry:
            linked_count += 1
            map_status = counterpart_status(declared_status)
            standard_counterpart = entry.get("standard_physics_counterpart")
            observable_mapping = entry.get("observable_mapping", {})
            unit_lane = entry.get("unit_lane", "UNDECLARED")
            derivation_class = entry.get("mathematical_role", "UNDECLARED")
        else:
            map_status = counterpart_status(declared_status)
            standard_counterpart = "UNRESOLVED—manual standard-physics correspondence required"
            observable_mapping = {"status": "OPEN_UNRESOLVED"}
            unit_lane = "UNRESOLVED_FROM_TOPIC_ROW"
            derivation_class = source.get("proof_status", "UNDECLARED")
        if "OPEN" in map_status or "UNRESOLVED" in map_status:
            open_count += 1
        observable_status = observable_mapping.get("status", "OPEN_UNRESOLVED") if isinstance(observable_mapping, dict) else "OPEN_UNRESOLVED"
        correspondence_counts[map_status] += 1
        unit_counts[unit_lane] += 1
        observable_counts[observable_status] += 1
        rows.append(
            {
                "formula_id": formula_id,
                "topic_id": source.get("topic_id"),
                "relation": source.get("relation"),
                "source": source.get("source"),
                "evidence_class": source.get("evidence_class"),
                "registry_link_status": "ACTIVE_CONTRACT_LINKED" if active else ("CENTRAL_REGISTRY_LINKED" if entry else "TOPIC_ROW_NOT_IN_CENTRAL_REGISTRY"),
                "standard_counterpart_status": map_status,
                "standard_counterpart": standard_counterpart,
                "unit_lane": unit_lane,
                "derivation_class_or_status": derivation_class,
                "observable_mapping": observable_mapping,
                "observable_status": observable_status,
                "symmetry_conservation_status": "OPEN_UNLESS_SEPARATELY_VERIFIED",
                "limiting_case_status": "OPEN_UNLESS_SEPARATELY_VERIFIED",
                "claim_ceiling": "inventory/correspondence review only; no promotion from this artifact",
                "next_action": "close standard counterpart, units, derivation origin and measurement operator in the lane-specific package",
            }
        )

    registry_rows: list[dict[str, Any]] = []
    formula_ids = {row.get("formula_id") for row in formulas.get("records", [])}
    for entry in registry.get("entries", []):
        equation_id = entry.get("equation_id")
        registry_rows.append(
            {
                "equation_id": equation_id,
                "topic_inventory_link_status": "LINKED_TO_TOPIC_ROW" if equation_id in formula_ids else "CORE_OR_ADDENDUM_ONLY",
                "classification": entry.get("classification"),
                "standard_counterpart": entry.get("standard_physics_counterpart"),
                "unit_lane": entry.get("unit_lane"),
                "observable_status": (entry.get("observable_mapping") or {}).get("status", "OPEN_UNRESOLVED"),
                "derivation_status": entry.get("mathematical_role"),
                "claim_boundary": entry.get("claim_boundary"),
            }
        )

    all_rows_covered = len(rows) == formulas.get("coverage", {}).get("parsed_formula_row_count", -1)
    return {
        "schema_version": "1.0",
        "artifact": "uet_full_correspondence_coverage",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS_WITH_OPEN_ROWS" if all_rows_covered else "FAIL",
        "matrix_status": "BLOCKED_OPEN_CORRESPONDENCE_ROWS" if all_rows_covered and open_count else "BLOCKED_INCOMPLETE_INVENTORY",
        "purpose": "row-complete F2 correspondence coverage; not a derivation or physical validation",
        "coverage": {
            "topic_formula_row_count": len(rows),
            "topic_formula_rows_expected": formulas.get("coverage", {}).get("parsed_formula_row_count"),
            "all_topic_rows_covered": all_rows_covered,
            "central_registry_entry_count": len(registry_rows),
            "central_registry_linked_topic_rows": linked_count,
            "open_correspondence_row_count": open_count,
        },
        "summary": {
            "standard_counterpart_status_counts": dict(sorted(correspondence_counts.items())),
            "unit_lane_counts": dict(sorted(unit_counts.items())),
            "observable_status_counts": dict(sorted(observable_counts.items())),
        },
        "rows": rows,
        "registry_rows": registry_rows,
        "interpretation": [
            "Coverage means every discovered row has an explicit record; it does not mean every row has a closed physical counterpart.",
            "A standard counterpart is not evidence that UET derived that relation.",
            "An open observable or unit field blocks data claims for that row.",
        ],
        "next_controller": "close the active lane rows with a standard counterpart, dimensional contract and measurement operator before any real-data promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        result = build()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={result['audit_status']}")
        print(f"matrix_status={result['matrix_status']}")
        print(f"topic_formula_row_count={result['coverage']['topic_formula_row_count']}")
        print(f"open_correspondence_row_count={result['coverage']['open_correspondence_row_count']}")
    return 0 if result["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
