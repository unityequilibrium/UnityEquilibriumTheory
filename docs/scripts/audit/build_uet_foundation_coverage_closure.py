"""Build a deterministic coverage closure for F0/F2 review.

Every discovered code surface and formula-audit row receives an explicit owner or
quarantine status.  This does not make an open correspondence row physical; it
only prevents inventory omissions from hiding inside a broad blocker.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CODE_PATH = ROOT / "docs/core/07_artifacts/archive/uet_code_surface_inventory.json"
FORMULA_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"
FAMILY_PATH = ROOT / "docs/core/07_artifacts/archive/uet_core_equation_family_contract.json"
REGISTRY_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
OUT = ROOT / "docs/core/07_artifacts/gates/uet_foundation_coverage_closure.json"


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def family_owners(family_contract: dict[str, Any]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for family in family_contract.get("families", []):
        family_id = family.get("family_id")
        for path in family.get("module_paths", []):
            if family_id and path:
                owners[path] = family_id
    return owners


def build() -> dict[str, Any]:
    code = load(CODE_PATH)
    formulas = load(FORMULA_PATH)
    families = load(FAMILY_PATH)
    registry = load(REGISTRY_PATH)
    owners = family_owners(families)
    registry_ids = {entry.get("equation_id") for entry in registry.get("entries", [])}

    code_records: list[dict[str, Any]] = []
    code_status_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for record in code.get("records", []):
        path = record.get("path", "")
        family_id = owners.get(path)
        if family_id:
            coverage_status = "ASSIGNED_TO_DECLARED_FAMILY"
            quarantine_reason = None
        else:
            family_id = "quarantine.unregistered_or_support_surface"
            coverage_status = "EXPLICITLY_QUARANTINED"
            quarantine_reason = "surface is outside the current declared core family contract; it cannot create an independent physical claim"
        code_status_counts[coverage_status] += 1
        family_counts[family_id] += 1
        code_records.append(
            {
                "surface_id": record.get("surface_id"),
                "path": path,
                "line": record.get("line"),
                "kind": record.get("kind"),
                "owner_family": family_id,
                "coverage_status": coverage_status,
                "quarantine_reason": quarantine_reason,
                "ontology_status": record.get("ontology_status", "OPEN"),
                "unit_status": record.get("unit_status", "OPEN"),
                "derivation_status": record.get("derivation_status", "OPEN"),
                "observable_status": "REQUIRES_FAMILY_GATE" if coverage_status == "ASSIGNED_TO_DECLARED_FAMILY" else "NOT_A_PHYSICAL_CLAIM",
            }
        )

    formula_records: list[dict[str, Any]] = []
    formula_status_counts: Counter[str] = Counter()
    correspondence_counts: Counter[str] = Counter()
    for record in formulas.get("records", []):
        formula_id = record.get("formula_id")
        if formula_id in registry_ids:
            registry_link = "CENTRAL_REGISTRY_LINKED"
        else:
            registry_link = "TOPIC_ROW_NOT_YET_IN_CENTRAL_REGISTRY"
        correspondence = record.get("correspondence_status", "OPEN_CORRESPONDENCE_REVIEW")
        formula_status = record.get("evidence_class", "REVIEW_REQUIRED")
        formula_status_counts[formula_status] += 1
        correspondence_counts[correspondence] += 1
        formula_records.append(
            {
                "formula_id": formula_id,
                "topic_id": record.get("topic_id"),
                "source": record.get("source"),
                "equation_class": record.get("equation_class"),
                "evidence_class": formula_status,
                "registry_link_status": registry_link,
                "correspondence_status": correspondence,
                "derivation_status": record.get("proof_status"),
                "unit_declaration": record.get("variables_and_units"),
                "observable_status": "OPEN_UNLESS_EXPLICITLY_MAPPED",
                "claim_status": "NO_PROMOTION_FROM_INVENTORY",
            }
        )

    unlinked_files = code.get("summary", {}).get("unlinked_core_files", [])
    parse_errors = formulas.get("parse_errors", [])
    explicit_exclusions = [
        {
            "scope": "README/METHOD prose equations not parsed by the formula-table scanner",
            "status": "EXPLICITLY_EXCLUDED_FROM_AUTOMATIC_EQUATION_INVENTORY",
            "reason": "prose is not treated as a machine-verified equation; it remains subject to manual formula audit before promotion",
        },
        {
            "scope": "topic formula rows whose standard counterpart or observable map is open",
            "status": "INVENTORIED_BUT_NOT_CLOSED",
            "reason": "inventory coverage does not imply correspondence or derivation",
        },
        {
            "scope": "unregistered core/support Python modules",
            "status": "EXPLICITLY_QUARANTINED",
            "reason": "unowned formula-like surfaces cannot create an independent physical equation family",
        },
    ]
    all_code_covered = len(code_records) == code.get("coverage", {}).get("candidate_surface_count", -1)
    all_formula_covered = len(formula_records) == formulas.get("coverage", {}).get("parsed_formula_row_count", -1)
    status = "PASS_WITH_EXPLICIT_QUARANTINES" if all_code_covered and all_formula_covered and not parse_errors else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_foundation_coverage_closure",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS" if status != "BLOCKED" else "PASS_WITH_DISCLOSED_GAPS",
        "coverage_gate_status": status,
        "purpose": "F0 inventory closure and F2/F4 review coverage; not a physical validation artifact",
        "coverage": {
            "code_surface_count": len(code_records),
            "formula_row_count": len(formula_records),
            "declared_family_count": len(families.get("families", [])),
            "central_registry_entry_count": len(registry.get("entries", [])),
            "unlinked_core_file_count": len(unlinked_files),
            "parse_error_count": len(parse_errors),
            "all_code_surfaces_assigned_or_quarantined": all_code_covered,
            "all_formula_rows_inventoried": all_formula_covered,
        },
        "summary": {
            "code_status_counts": dict(sorted(code_status_counts.items())),
            "owner_family_counts": dict(sorted(family_counts.items())),
            "formula_evidence_counts": dict(sorted(formula_status_counts.items())),
            "formula_correspondence_counts": dict(sorted(correspondence_counts.items())),
        },
        "code_surfaces": code_records,
        "formula_rows": formula_records,
        "unlinked_core_files": unlinked_files,
        "explicit_exclusions": explicit_exclusions,
        "open_physics_gates": {
            "F1_ontology": "family assignment does not close lane-specific physical identity",
            "F2_correspondence": "topic rows and unregistered families still require standard counterpart and observable review",
            "F3_units": "inventory unit text is not dimensional closure",
            "F4_derivation": "proof-status text is not a derivation",
            "F7_observable": "observable_status remains open unless a measurement operator is separately recorded",
        },
        "next_controller": "use this coverage closure as the input to a full correspondence/unit/observable matrix; do not promote any row from inventory alone",
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
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={result['audit_status']}")
        print(f"coverage_gate_status={result['coverage_gate_status']}")
        print(f"code_surface_count={result['coverage']['code_surface_count']}")
        print(f"formula_row_count={result['coverage']['formula_row_count']}")
        print(f"unlinked_core_file_count={result['coverage']['unlinked_core_file_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
