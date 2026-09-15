"""Audit derivation-origin and evidence class for every registered UET relation.

This audit closes bookkeeping about where a relation comes from without promoting a
relation-level derivation into a physical theory or empirical validation claim.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
OUT_PATH = ROOT / "docs/core/07_artifacts/verification/uet_derivation_origin_audit.json"

REQUIRED_FIELDS = {
    "equation_id",
    "classification",
    "mathematical_role",
    "source_or_origin",
    "assumptions",
    "limiting_cases",
    "implementation_paths",
    "verifier_paths",
    "evidence_class",
    "proof_status",
    "claim_boundary",
    "failure_mode",
    "next_hardening_step",
}


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path.relative_to(ROOT)}")
    return value


def _origin_family(entry: dict[str, Any]) -> str:
    evidence = str(entry.get("evidence_class", "")).upper()
    proof = str(entry.get("proof_status", "")).lower()
    classification = str(entry.get("classification", "")).lower()
    if evidence == "LEGACY" or "legacy" in classification:
        return "LEGACY_OR_COMPARATOR"
    if "CONCEPTUAL" in evidence or "conceptual" in proof:
        return "CONCEPTUAL_CANDIDATE"
    if "CANDIDATE" in evidence or "candidate" in classification:
        return "CANDIDATE_WITH_LOCAL_CHECKS"
    if "CHECKED" in evidence or "checked" in proof:
        return "STANDARD_OR_INTERNAL_COMPARATOR"
    if "CONTRACT" in evidence or "contract" in classification or "contract" in proof:
        return "CONTRACT_OR_MAPPING"
    if proof == "derived" or "derived" in proof:
        return "DECLARED_RELATION_DERIVATION"
    if "DIAGNOSTIC" in evidence or "heuristic" in proof or "open" in proof:
        return "HEURISTIC_OR_DIAGNOSTIC"
    return "UNCLASSIFIED_OPEN"


def _derivation_readiness(entry: dict[str, Any], family: str) -> str:
    if family == "DECLARED_RELATION_DERIVATION":
        return "RELATION_DERIVATION_DECLARED_PHYSICAL_CLOSURE_OPEN"
    if family == "STANDARD_OR_INTERNAL_COMPARATOR":
        return "COMPARATOR_CHECKED_UET_DERIVATION_OPEN"
    if family == "CANDIDATE_WITH_LOCAL_CHECKS":
        return "CANDIDATE_LOCAL_CHECKS_PHYSICAL_CLOSURE_OPEN"
    if family == "LEGACY_OR_COMPARATOR":
        return "LEGACY_ORIGIN_RETAINED_NOT_PROMOTABLE"
    if family in {"CONCEPTUAL_CANDIDATE", "HEURISTIC_OR_DIAGNOSTIC"}:
        return "OPEN_HEURISTIC_OR_CONCEPTUAL_ORIGIN"
    if family == "CONTRACT_OR_MAPPING":
        return "OPEN_CONTRACT_MAPPING_NO_DERIVATION"
    return "UNCLASSIFIED_REQUIRES_REVIEW"


def build_report(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    if registry is None:
        if not REGISTRY_PATH.exists():
            errors.append(f"missing registry: {REGISTRY_PATH.relative_to(ROOT)}")
            registry = {}
        else:
            try:
                registry = _load(REGISTRY_PATH)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(str(exc))
                registry = {}

    entries = registry.get("entries", []) if isinstance(registry, dict) else []
    if not isinstance(entries, list) or not entries:
        errors.append("registry entries must be a non-empty list")
        entries = []

    seen: set[str] = set()
    audit_entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    open_entries = 0
    declared_derivations = 0
    comparator_checked = 0
    physical_promotions = 0

    for index, entry in enumerate(entries):
        prefix = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = sorted(REQUIRED_FIELDS - set(entry))
        errors.extend(f"{prefix} missing {field}" for field in missing)
        equation_id = entry.get("equation_id")
        if not isinstance(equation_id, str) or not equation_id:
            errors.append(f"{prefix}.equation_id must be non-empty")
            equation_id = f"<missing:{index}>"
        elif equation_id in seen:
            errors.append(f"duplicate equation_id: {equation_id}")
        else:
            seen.add(equation_id)

        source = entry.get("source_or_origin")
        proof = entry.get("proof_status")
        if not isinstance(source, str) or not source.strip():
            errors.append(f"{prefix}.source_or_origin must be non-empty")
        if not isinstance(proof, str) or not proof.strip():
            errors.append(f"{prefix}.proof_status must be non-empty")

        family = _origin_family(entry)
        readiness = _derivation_readiness(entry, family)
        counts[family] = counts.get(family, 0) + 1
        if family == "DECLARED_RELATION_DERIVATION":
            declared_derivations += 1
        if family == "STANDARD_OR_INTERNAL_COMPARATOR":
            comparator_checked += 1
        if family not in {"DECLARED_RELATION_DERIVATION", "STANDARD_OR_INTERNAL_COMPARATOR"}:
            open_entries += 1
        physical_promotions += int(readiness.endswith("PHYSICAL_CLOSURE_CLOSED"))

        audit_entries.append(
            {
                "equation_id": equation_id,
                "classification": entry.get("classification"),
                "origin_family": family,
                "derivation_readiness": readiness,
                "source_or_origin": source,
                "evidence_class": entry.get("evidence_class"),
                "proof_status": proof,
                "mathematical_role": entry.get("mathematical_role"),
                "claim_boundary": entry.get("claim_boundary"),
                "physical_closure": False,
                "physical_promotion_allowed": False,
            }
        )

    audit_status = "PASS" if not errors else "FAIL"
    status = "PASS_WITH_DECLARED_OPEN_ORIGINS" if audit_status == "PASS" else "BLOCKED_INVALID_ORIGIN_AUDIT"
    return {
        "schema_version": "1.0",
        "artifact": "uet_derivation_origin_audit",
        "generated_at": date.today().isoformat(),
        "audit_status": audit_status,
        "status": status,
        "purpose": "classify relation origins and preserve the boundary between derivation, comparison, heuristic and physical closure",
        "registry": str(REGISTRY_PATH.relative_to(ROOT)).replace("\\", "/"),
        "metrics": {
            "registry_entry_count": len(audit_entries),
            "origin_family_counts": counts,
            "declared_relation_derivations": declared_derivations,
            "comparator_checked_relations": comparator_checked,
            "open_or_candidate_relations": open_entries,
            "physical_promotions_allowed": physical_promotions,
        },
        "entries": audit_entries,
        "gates": {
            "every_registry_row_has_origin_and_proof_label": not errors,
            "derived_is_distinguished_from_comparator": True,
            "heuristic_and_conceptual_rows_remain_open": open_entries > 0,
            "no_physical_promotion_from_relation_audit": physical_promotions == 0,
        },
        "errors": errors,
        "claim_boundary": "relation-level derivation bookkeeping only; no empirical, SI, universal-C, mass, particle, GR or cosmology promotion",
        "next_controller": "manually close assumptions, limiting cases and physical correspondence for open rows; retain comparator and heuristic rows as non-derivational",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.no_write:
        OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"status={report['status']}")
        print(f"registry_entry_count={report['metrics']['registry_entry_count']}")
        print(f"open_or_candidate_relations={report['metrics']['open_or_candidate_relations']}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())