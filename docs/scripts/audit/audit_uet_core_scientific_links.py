"""Audit the scientific-link chain for organization-assigned core records.

This is a link audit, not a physics verifier.  It reports whether a file has a
canonical equation-family contract, formula IDs, units, verifiers, artifacts,
and claim metadata.  Missing links keep the result blocked; organization
ownership never promotes scientific evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
ARTIFACTS = CORE / "artifacts"
REGISTRY_PATH = ARTIFACTS / "uet_research_organization_registry.json"
MIGRATION_PATH = ARTIFACTS / "uet_core_file_migration_map.json"
POLICY_PATH = CORE / "00_governance" / "uet_research_organization_policy.json"
FAMILY_CONTRACT_PATH = ARTIFACTS / "uet_core_equation_family_contract.json"
CORRESPONDENCE_PATH = ARTIFACTS / "uet_equation_correspondence_registry.json"
FOUNDATION_GATE_PATH = ARTIFACTS / "uet_foundation_dependency_gate.json"
OUTPUT_PATH = ARTIFACTS / "uet_core_scientific_link_audit.json"

GENERATOR_ID = "docs/scripts/audit/audit_uet_core_scientific_links.py"
REQUIRED_LINK_FIELDS = (
    "formula_ids",
    "unit_lane",
    "verifier_paths",
    "artifact_paths",
    "claim_ceiling",
)


class DuplicateKeyError(ValueError):
    """Raised for an exact duplicate JSON key."""


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path, *, detect_case_collisions: bool = False) -> tuple[Any, list[str], list[list[str]]]:
    errors: list[str] = []
    collisions: set[tuple[str, ...]] = set()
    if not path.exists():
        return None, [f"missing file: {path.relative_to(ROOT).as_posix()}"], []

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        folded: dict[str, str] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateKeyError(f"duplicate JSON key: {key}")
            if detect_case_collisions:
                key_folded = key.casefold()
                previous = folded.get(key_folded)
                if previous is not None and previous != key:
                    collisions.add(tuple(sorted((previous, key))))
                folded[key_folded] = key
            result[key] = value
        return result

    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle, object_pairs_hook=pairs_hook if detect_case_collisions else _strict_pairs)
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"invalid JSON {path.relative_to(ROOT).as_posix()}: {exc}")
        return None, errors, []
    return value, errors, [list(item) for item in sorted(collisions)]


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def nonempty(value: Any) -> bool:
    if isinstance(value, (list, dict, str)):
        return bool(value)
    return value is not None


def build() -> dict[str, Any]:
    registry, registry_errors, registry_collisions = load_json(REGISTRY_PATH)
    migration, migration_errors, migration_collisions = load_json(MIGRATION_PATH)
    policy, policy_errors, policy_collisions = load_json(POLICY_PATH)
    family_contract, family_errors, family_collisions = load_json(FAMILY_CONTRACT_PATH)
    correspondence, correspondence_errors, correspondence_collisions = load_json(
        CORRESPONDENCE_PATH, detect_case_collisions=True
    )
    foundation_gate, foundation_errors, foundation_collisions = load_json(FOUNDATION_GATE_PATH)

    errors = (
        registry_errors
        + migration_errors
        + policy_errors
        + family_errors
        + correspondence_errors
        + foundation_errors
    )
    all_collisions = {
        tuple(item)
        for group in (
            registry_collisions,
            migration_collisions,
            policy_collisions,
            family_collisions,
            correspondence_collisions,
            foundation_collisions,
        )
        for item in group
    }

    files = registry.get("files", []) if isinstance(registry, dict) else []
    assigned = [item for item in files if item.get("organization_disposition")]
    rules = {
        rule.get("disposition_id"): rule
        for rule in (policy.get("review_disposition_rules", []) if isinstance(policy, dict) else [])
        if rule.get("disposition_id")
    }
    families = {
        family.get("family_id"): family
        for family in (family_contract.get("families", []) if isinstance(family_contract, dict) else [])
        if family.get("family_id")
    }

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in assigned:
        by_family[str(item.get("equation_family_or_lane"))].append(item)

    family_rows: list[dict[str, Any]] = []
    file_rows: list[dict[str, Any]] = []
    missing_contract_count = 0
    missing_field_counts: Counter[str] = Counter()
    records_with_fields: Counter[str] = Counter()
    source_path_missing_count = 0

    for family_id in sorted(by_family):
        records = sorted(by_family[family_id], key=lambda item: item.get("path", ""))
        rule_ids = sorted({str(item.get("organization_disposition")) for item in records})
        rule = rules.get(rule_ids[0]) if len(rule_ids) == 1 else None
        contract = families.get(family_id)
        contract_exists = isinstance(contract, dict)
        if not contract_exists:
            missing_contract_count += len(records)

        field_counts: dict[str, int] = {}
        missing_fields: set[str] = set()
        for field in REQUIRED_LINK_FIELDS:
            count = sum(nonempty(item.get(field)) for item in records)
            field_counts[field] = count
            records_with_fields[field] += count
            if count != len(records):
                missing_fields.add(field)
                missing_field_counts[field] += len(records) - count

        if not contract_exists:
            link_status = "BLOCKED_NO_CANONICAL_FAMILY_CONTRACT"
        elif missing_fields:
            link_status = "BLOCKED_LINK_FIELDS_INCOMPLETE"
        else:
            link_status = "LINKED_PENDING_VERIFICATION"

        contract_evidence_paths = list(contract.get("evidence_paths", [])) if contract_exists else []
        contract_evidence_exists = all((ROOT / path).exists() for path in contract_evidence_paths)
        family_row = {
            "family_or_lane": family_id,
            "organization_dispositions": rule_ids,
            "owner_ids": sorted({item.get("owner_id") for item in records}),
            "room_ids": sorted({item.get("room_id") for item in records}),
            "record_count": len(records),
            "record_paths": [item.get("path") for item in records],
            "canonical_family_contract_id": family_id if contract_exists else None,
            "canonical_family_contract_status": "FOUND" if contract_exists else "MISSING",
            "contract_evidence_paths": contract_evidence_paths,
            "contract_evidence_paths_exist": contract_evidence_exists,
            "record_link_field_counts": field_counts,
            "missing_link_fields": sorted(missing_fields),
            "link_status": link_status,
            "unit_lane_from_contract": contract.get("unit_lane") if contract_exists else None,
            "claim_ceiling_from_contract": contract.get("claim_ceiling") if contract_exists else None,
            "next_action": (
                rule.get("next_action")
                if rule
                else "manual_family_scope_review"
            ),
            "claim_boundary": "link audit only; no equation or physical claim promotion",
        }
        family_rows.append(family_row)

        for item in records:
            path = str(item.get("path", ""))
            source_exists = (ROOT / path).exists()
            if not source_exists:
                source_path_missing_count += 1
            file_rows.append(
                {
                    "path": path,
                    "organization_disposition": item.get("organization_disposition"),
                    "family_or_lane": family_id,
                    "owner_id": item.get("owner_id"),
                    "room_id": item.get("room_id"),
                    "organization_status": item.get("organization_status"),
                    "evidence_status": item.get("evidence_status"),
                    "source_exists": source_exists,
                    "formula_ids_present": nonempty(item.get("formula_ids")),
                    "unit_lane_present": nonempty(item.get("unit_lane")),
                    "verifier_paths_present": nonempty(item.get("verifier_paths")),
                    "artifact_paths_present": nonempty(item.get("artifact_paths")),
                    "claim_ceiling_present": nonempty(item.get("claim_ceiling")),
                    "family_link_status": link_status,
                    "next_action": item.get("next_action"),
                }
            )

    assigned_paths = sorted(str(item.get("path")) for item in assigned)
    audited_paths = sorted(row["path"] for row in file_rows)
    physical_move_not_performed = isinstance(migration, dict) and migration.get("physical_move_performed") is False
    foundation_blocked = isinstance(foundation_gate, dict) and foundation_gate.get("status") == "BLOCKED"
    all_blocked = all(item.get("evidence_status") == "BLOCKED" for item in assigned)
    checks = [
        {
            "check_id": "assigned_records_are_all_audited",
            "status": "PASS" if assigned_paths == audited_paths else "FAIL",
            "observed": len(audited_paths),
            "expected": len(assigned_paths),
        },
        {
            "check_id": "assigned_source_paths_exist",
            "status": "PASS" if source_path_missing_count == 0 else "FAIL",
            "observed": source_path_missing_count,
            "expected": 0,
        },
        {
            "check_id": "organization_does_not_promote_evidence",
            "status": "PASS" if all_blocked else "FAIL",
            "observed": sum(item.get("evidence_status") != "BLOCKED" for item in assigned),
            "expected": 0,
        },
        {
            "check_id": "foundation_gate_remains_blocked",
            "status": "PASS" if foundation_blocked else "FAIL",
            "observed": foundation_gate.get("status") if isinstance(foundation_gate, dict) else None,
            "expected": "BLOCKED",
        },
        {
            "check_id": "physical_move_not_performed",
            "status": "PASS" if physical_move_not_performed else "FAIL",
            "observed": migration.get("physical_move_performed") if isinstance(migration, dict) else None,
            "expected": False,
        },
        {
            "check_id": "correspondence_registry_exact_json",
            "status": "PASS" if not correspondence_errors else "FAIL",
            "observed": correspondence_errors,
            "expected": [],
        },
        {
            "check_id": "case_insensitive_metadata_key_lint",
            "status": "REVIEW_REQUIRED" if all_collisions else "PASS",
            "observed": [list(item) for item in sorted(all_collisions)],
            "expected": [],
        },
    ]

    link_blocked = missing_contract_count > 0 or bool(missing_field_counts) or bool(errors)
    audit_status = "BLOCKED_OPEN_SCIENTIFIC_LINKS" if link_blocked else "PASS_WITH_REVIEW_REQUIRED" if all_collisions else "PASS"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_scientific_link_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR_ID,
        "audit_status": audit_status,
        "controlling_blocker": (
            "scientific_link_input_errors"
            if errors
            else "pending_families_have_no_canonical_formula_unit_verifier_artifact_chain"
            if link_blocked
            else "case_insensitive_metadata_key_review"
            if all_collisions
            else None
        ),
        "scope": {
            "organization_registry_file_count": len(files),
            "assigned_review_record_count": len(assigned),
            "family_or_lane_count": len(family_rows),
            "physical_move_performed": not physical_move_not_performed,
        },
        "summary": {
            "assigned_records": len(assigned),
            "audited_records": len(file_rows),
            "canonical_family_contract_matches": sum(
                row["canonical_family_contract_status"] == "FOUND" for row in family_rows
            ),
            "families_without_canonical_contract": sum(
                row["canonical_family_contract_status"] == "MISSING" for row in family_rows
            ),
            "records_without_canonical_contract": missing_contract_count,
            "records_with_formula_ids": records_with_fields["formula_ids"],
            "records_with_unit_lane": records_with_fields["unit_lane"],
            "records_with_verifier_paths": records_with_fields["verifier_paths"],
            "records_with_artifact_paths": records_with_fields["artifact_paths"],
            "records_with_claim_ceiling": records_with_fields["claim_ceiling"],
            "missing_link_field_counts": dict(sorted(missing_field_counts.items())),
            "missing_source_path_count": source_path_missing_count,
            "case_insensitive_key_collision_count": len(all_collisions),
        },
        "checks": checks,
        "families": family_rows,
        "records": file_rows,
        "input_errors": errors,
        "case_insensitive_key_collisions": [list(item) for item in sorted(all_collisions)],
        "inputs": {
            "organization_registry": {"path": repo_path(REGISTRY_PATH), "sha256": sha256_file(REGISTRY_PATH)},
            "migration_map": {"path": repo_path(MIGRATION_PATH), "sha256": sha256_file(MIGRATION_PATH)},
            "organization_policy": {"path": repo_path(POLICY_PATH), "sha256": sha256_file(POLICY_PATH)},
            "family_contract": {"path": repo_path(FAMILY_CONTRACT_PATH), "sha256": sha256_file(FAMILY_CONTRACT_PATH)},
            "correspondence_registry": {"path": repo_path(CORRESPONDENCE_PATH), "sha256": sha256_file(CORRESPONDENCE_PATH)},
            "foundation_gate": {"path": repo_path(FOUNDATION_GATE_PATH), "sha256": sha256_file(FOUNDATION_GATE_PATH)},
        },
        "interpretation": [
            "An organization disposition routes ownership; it does not create a scientific link.",
            "A missing family contract or link field blocks promotion even when the source module exists.",
            "The correspondence registry is exact-JSON valid; case-insensitive key collisions are reported as a compatibility lint.",
            "This artifact does not verify formulas, units, observables, or empirical claims.",
        ],
        "claim_boundary": "organization/scientific-link audit only; no equation, physical, or empirical claim is promoted",
        "next_controller": "create canonical family-link records, beginning with foundation/matter-space and covariant families, then populate formula IDs, unit lanes, verifier paths, artifact paths, and claim ceilings",
    }


def without_generated_at(payload: dict[str, Any]) -> dict[str, Any]:
    copied = json.loads(json.dumps(payload))
    copied.pop("generated_at", None)
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare the existing artifact without writing")
    parser.add_argument("--no-write", action="store_true", help="print the summary without writing")
    args = parser.parse_args()
    result = build()
    if args.check:
        if not OUTPUT_PATH.exists():
            print(json.dumps({"status": "DRIFT", "mismatches": [repo_path(OUTPUT_PATH)]}, ensure_ascii=False))
            return 1
        actual, errors, _ = load_json(OUTPUT_PATH)
        mismatch = bool(errors) or without_generated_at(actual) != without_generated_at(result)
        print(json.dumps({"status": "DRIFT" if mismatch else "PASS", "mismatches": [repo_path(OUTPUT_PATH)] if mismatch else []}, ensure_ascii=False))
        return 1 if mismatch else 0
    if not args.no_write:
        OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "audit_status": result["audit_status"],
                "assigned_records": result["summary"]["assigned_records"],
                "families": result["summary"]["canonical_family_contract_matches"],
                "families_without_contract": result["summary"]["families_without_canonical_contract"],
                "records_without_contract": result["summary"]["records_without_canonical_contract"],
                "case_insensitive_key_collisions": result["summary"]["case_insensitive_key_collision_count"],
                "controlling_blocker": result["controlling_blocker"],
                "output": repo_path(OUTPUT_PATH),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
