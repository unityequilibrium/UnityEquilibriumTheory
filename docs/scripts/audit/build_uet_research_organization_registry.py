"""Build the UET organization registry and migration view.

This is an organization-control generator.  It does not change equation status,
physics claims, imports, or file locations.  The existing core-file manifest,
equation-family contract, and foundation gate remain the authoritative inputs
for their respective domains.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
ARTIFACTS = CORE / "07_artifacts"
POLICY_PATH = CORE / "00_governance" / "uet_research_organization_policy.json"
MANIFEST_PATH = ARTIFACTS / "provenance" / "uet_core_file_manifest.json"
FAMILY_CONTRACT_PATH = ARTIFACTS / "archive" / "uet_core_equation_family_contract.json"
FOUNDATION_GATE_PATH = ARTIFACTS / "gates" / "uet_foundation_dependency_gate.json"
REGISTRY_PATH = ARTIFACTS / "gates" / "uet_research_organization_registry.json"
MIGRATION_PATH = ARTIFACTS / "archive" / "uet_core_file_migration_map.json"
AUDIT_PATH = ARTIFACTS / "gates" / "uet_core_organization_audit.json"
INDEX_PATH = CORE / "00_governance" / "CORE_RESEARCH_ORGANIZATION_INDEX.md"

REQUIRED_FILE_FIELDS = (
    "asset_id",
    "path",
    "file_kind",
    "logical_area",
    "owner_id",
    "room_id",
    "equation_family_or_lane",
    "organization_status",
    "evidence_status",
    "status_source",
    "generated_or_source",
    "formula_ids",
    "verifier_paths",
    "artifact_paths",
    "upstream_dependencies",
    "downstream_dependencies",
    "sha256",
    "migration_state",
    "next_action",
)

VALID_EVIDENCE_STATUSES = {
    "LEGACY",
    "COMPARATOR",
    "CANDIDATE",
    "INTERNAL",
    "SIMULATION_ONLY",
    "EXTERNAL_COMPARISON",
    "BLOCKED",
}

OWNER_BY_AREA = {
    "00_governance": "ORG",
    "01_contracts": "FOUNDATION",
    "02_equations": "EQUATION",
    "03_lanes": "LANE",
    "04_proofs": "EVIDENCE",
    "05_tests": "EVIDENCE",
    "06_data": "DATA",
    "07_artifacts": "EVIDENCE",
    "08_history": "ORG",
    "99_review": "ORG",
}

UPSTREAM_BY_OWNER = {
    "ORG": [],
    "FOUNDATION": ["ORG"],
    "EQUATION": ["FOUNDATION"],
    "LANE": ["FOUNDATION", "EQUATION", "DATA"],
    "EVIDENCE": ["FOUNDATION", "EQUATION", "LANE"],
    "DATA": ["ORG"],
}

DOWNSTREAM_BY_OWNER = {
    "ORG": ["FOUNDATION", "DATA"],
    "FOUNDATION": ["EQUATION", "LANE", "EVIDENCE"],
    "EQUATION": ["LANE", "EVIDENCE"],
    "LANE": ["EVIDENCE"],
    "EVIDENCE": [],
    "DATA": ["LANE"],
}


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize_path(value: str) -> str:
    return value.replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def stable_asset_id(path: str) -> str:
    digest = hashlib.sha256(normalize_path(path).encode("utf-8")).hexdigest()[:12]
    return f"UET-CORE-FILE-{digest.upper()}"


def family_maps(contract: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_module: dict[str, dict[str, Any]] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for family in contract.get("families", []):
        family_id = str(family.get("family_id", ""))
        if family_id:
            by_id[family_id] = family
        for module_path in family.get("module_paths", []):
            by_module[normalize_path(str(module_path))] = family
    return by_module, by_id


def family_for(record: dict[str, Any], by_module: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    family = by_module.get(normalize_path(str(record.get("path", ""))))
    if family:
        return family
    owner = str(record.get("owner_family_or_lane") or "")
    if owner.startswith("core."):
        return {"family_id": owner, "claim_ceiling": "review required"}
    return None


def effective_record(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    path = normalize_path(str(result.get("path", "")))
    if path == "docs/core/00_governance/uet_research_organization_policy.json":
        result.update(
            file_kind="governance_policy",
            logical_area="00_governance",
            owner_family_or_lane="core_governance",
            registry_link_status="SOURCE_POLICY",
            status_source=path,
            generated_or_source="source",
            review_action="keep_as_governance_source",
        )
    return result


def room_for(path: str, logical_area: str) -> str:
    lower = normalize_path(path).lower()
    if logical_area in {"00_governance", "08_history", "99_review"}:
        return "ROOM_CORE_ORGANIZATION"
    if logical_area == "03_lanes":
        if any(token in lower for token in ("t13", "thermal", "he4", "topic13", "o2")):
            return "ROOM_TOPIC_013"
        if any(token in lower for token in ("phase", "structure_factor", "spinodal", "0_11", "topic11")):
            return "ROOM_TOPIC_011"
    return "ROOM_CORE_FOUNDATION"


def owner_for(logical_area: str) -> str:
    return OWNER_BY_AREA.get(logical_area, "ORG")


def evidence_status(record: dict[str, Any], family: dict[str, Any] | None) -> str:
    if record.get("registry_link_status") == "REVIEW_REQUIRED":
        return "BLOCKED"
    if record.get("file_kind") in {"unassigned_python_surface", "review_required", "lane_specific_module"}:
        return "BLOCKED"
    if family:
        ceiling = str(family.get("claim_ceiling", "")).lower()
        if "legacy comparator" in ceiling:
            return "COMPARATOR"
        if "candidate" in ceiling:
            return "CANDIDATE"
        if "diagnostic" in ceiling or "utility" in ceiling:
            return "INTERNAL"
    if record.get("file_kind") in {
        "generated_artifact",
        "verifier_or_regression_test",
        "proof_or_derivation_runner",
        "governance_policy",
        "navigation_and_legacy_boundary",
        "update_log",
    }:
        return "INTERNAL"
    if record.get("generated_or_source") == "generated":
        return "INTERNAL"
    return "BLOCKED"


def organization_status(record: dict[str, Any]) -> str:
    if record.get("registry_link_status") == "REVIEW_REQUIRED":
        return "UNASSIGNED"
    if record.get("file_kind") in {"unassigned_python_surface", "review_required", "lane_specific_module"}:
        return "UNASSIGNED"
    return "ASSIGNED"


def family_group(family_id: str) -> str:
    lower = family_id.lower()
    if "legacy" in lower:
        return "legacy"
    if "matter_space" in lower or "trace" in lower or "hyperbolic" in lower:
        return "matter_space"
    if "covariant" in lower or "curved" in lower or "gr" in lower:
        return "covariant"
    if "o2" in lower:
        return "o2"
    if "lorentz" in lower or "noether" in lower:
        return "lorentz_noether"
    return "review"


def test_group(path: str) -> str:
    lower = path.lower()
    if "artifact" in lower or "schema" in lower:
        return "artifact"
    if "converg" in lower or "numerical" in lower or "causal" in lower:
        return "numerical"
    if "equation" in lower or "formula" in lower or "deriv" in lower:
        return "equation"
    return "regression"


def canonical_artifact_target(name: str) -> str:
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from docs.core.core_paths import canonical_artifact_path

    return repo_path(canonical_artifact_path(name))

def target_path(record: dict[str, Any], family: dict[str, Any] | None, room_id: str) -> str:
    path = normalize_path(str(record["path"]))
    name = Path(path).name
    area = str(record.get("logical_area", "99_review"))
    family_id = str((family or {}).get("family_id") or record.get("owner_family_or_lane") or "review_required")

    if record.get("file_kind") == "generated_artifact":
        return canonical_artifact_target(name)

    if area == "00_governance":
        return f"docs/core/00_governance/{name}"
    if area == "01_contracts":
        return f"docs/core/01_contracts/{name}"
    if area == "02_equations":
        return f"docs/core/02_equations/{family_group(family_id)}/{name}"
    if area == "03_lanes":
        if room_id == "ROOM_TOPIC_013":
            subdir = "topic13_support" if name.lower().startswith("t13") else "thermal"
        elif room_id == "ROOM_TOPIC_011":
            subdir = "phase_transition"
        else:
            subdir = "review"
        return f"docs/core/03_lanes/{subdir}/{name}"
    if area == "04_proofs":
        return f"docs/core/04_proofs/{name}"
    if area == "05_tests":
        return f"docs/core/05_tests/{test_group(path)}/{name}"
    if area == "06_data":
        if record.get("file_kind") == "declared_input_data":
            subdir = "source_packages" if name.lower().endswith((".csv", ".tsv", ".parquet", ".npz")) else "manifests"
        else:
            subdir = "derived_inputs"
        return f"docs/core/06_data/{subdir}/{name}"
    if area == "07_artifacts":
        domain = str(record.get("owner_family_or_lane") or "")
        subdir = "topic13" if "topic13" in domain.lower() or name.lower().startswith(("t13_", "thermal_", "he4_")) else "verification"
        return f"docs/core/07_artifacts/{subdir}/{name}"
    if area == "08_history":
        lower = name.lower()
        subdir = "update_logs" if "update_log" in lower else "legacy" if "legacy" in lower else "research_notes"
        return f"docs/core/08_history/{subdir}/{name}"
    return f"docs/core/99_review/{name}"


def migration_state(current_path: str, planned_path: str) -> str:
    current = normalize_path(current_path)
    planned = normalize_path(planned_path)
    if current == planned:
        return "MIGRATED"
    if current.startswith(("docs/core/artifacts/", "docs/core/data/", "docs/core/test/", "docs/core/02_Proof/")):
        return "COMPATIBILITY_PATH_RETAINED"
    return "NOT_STARTED"


def next_action(record: dict[str, Any], family: dict[str, Any] | None) -> str:
    if record.get("registry_link_status") == "REVIEW_REQUIRED":
        return "assign_owner_family_or_quarantine"
    if record.get("generated_or_source") == "generated":
        return "retain_path_and_link_generator"
    if family:
        return "link_formula_verifier_artifact_and_migration_target"
    if record.get("file_kind") == "governance_policy":
        return "keep_as_organization_source_policy"
    return "link_registry_status_and_owner"


def related_tests(path: str, test_paths: list[Path]) -> list[str]:
    normalized = normalize_path(path)
    stem = Path(normalized).stem
    matches: list[str] = []
    for test_path in test_paths:
        try:
            content = test_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if normalized in content or stem in content:
            matches.append(repo_path(test_path))
    return sorted(matches)


def build_file_record(
    source_record: dict[str, Any],
    by_module: dict[str, dict[str, Any]],
    test_paths: list[Path],
) -> dict[str, Any]:
    record = effective_record(source_record)
    path = normalize_path(str(record["path"]))
    logical_area = str(record.get("logical_area", "99_review"))
    owner_id = owner_for(logical_area)
    room_id = room_for(path, logical_area)
    family = family_for(record, by_module)
    family_id = str((family or {}).get("family_id") or record.get("owner_family_or_lane") or "review_required")
    planned_path = target_path(record, family, room_id)
    artifacts = [normalize_path(str(item)) for item in (family or {}).get("evidence_paths", [])]
    if record.get("file_kind") == "generated_artifact":
        artifacts = [path]
    linked_tests = related_tests(path, test_paths) if record.get("file_kind") in {"equation_module", "lane_specific_module", "support_or_adapter_module"} else []
    family_verifiers = [
        normalize_path(str(item))
        for item in (family or {}).get("verifier_paths", [])
    ]
    verifier_paths = sorted(set(linked_tests + family_verifiers))
    formula_ids = [
        str(item)
        for item in (family or {}).get("formula_ids", [])
        if str(item)
    ]
    organization = organization_status(record)
    evidence = evidence_status(record, family)
    status_source = str(record.get("status_source") or "")
    if status_source == "MANIFEST_CLASSIFICATION_ONLY":
        status_source = "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
    return {
        "asset_id": stable_asset_id(path),
        "path": path,
        "file_kind": record.get("file_kind"),
        "logical_area": logical_area,
        "owner_id": owner_id,
        "room_id": room_id,
        "equation_family_or_lane": family_id or None,
        "organization_status": organization,
        "evidence_status": evidence,
        "status_source": status_source,
        "generated_or_source": record.get("generated_or_source", "source"),
        "formula_ids": formula_ids,
        "verifier_paths": verifier_paths,
        "artifact_paths": artifacts,
        "upstream_dependencies": UPSTREAM_BY_OWNER.get(owner_id, []),
        "downstream_dependencies": DOWNSTREAM_BY_OWNER.get(owner_id, []),
        "sha256": record.get("sha256"),
        "migration_state": migration_state(path, planned_path),
        "next_action": next_action(record, family),
        "target_physical_path": planned_path,
        "registry_link_status": record.get("registry_link_status"),
        "review_action": record.get("review_action"),
        "unit_lane": (family or {}).get("unit_lane"),
        "derivation_class": (family or {}).get("derivation_class"),
        "claim_ceiling": (family or {}).get("claim_ceiling"),
        "import_reference_count": None,
        "link_reference_count": None,
        "reference_scan_status": "DEFERRED_TO_MIGRATION_WAVE",
    }


def build_registry(policy: dict[str, Any], manifest: dict[str, Any], contract: dict[str, Any], gate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    by_module, _ = family_maps(contract)
    source_records = manifest.get("files", [])
    test_paths = [CORE / Path(item["path"]) for item in source_records if item.get("file_kind") == "verifier_or_regression_test"]
    files = [build_file_record(item, by_module, test_paths) for item in source_records]
    files.sort(key=lambda item: item["path"])

    review_files = [item for item in files if item["organization_status"] == "UNASSIGNED"]
    required_failures = [
        item
        for item in files
        if any(item.get(field) is None for field in REQUIRED_FILE_FIELDS)
    ]
    duplicate_ids = [asset_id for asset_id, count in Counter(item["asset_id"] for item in files).items() if count > 1]
    owners = {item["owner_id"] for item in files}
    declared_owners = {item["owner_id"] for item in policy.get("owners", [])}
    rooms = {item["room_id"] for item in files}
    declared_rooms = {item["room_id"] for item in policy.get("rooms", [])}
    areas = {item["logical_area"] for item in files}
    declared_areas = set(policy.get("logical_areas", {}))

    checks = [
        {
            "check_id": "all_required_file_fields",
            "status": "PASS" if not required_failures else "FAIL",
            "observed": len(required_failures),
            "expected": 0,
        },
        {
            "check_id": "unique_asset_ids",
            "status": "PASS" if not duplicate_ids else "FAIL",
            "observed": len(duplicate_ids),
            "expected": 0,
        },
        {
            "check_id": "declared_owner_references",
            "status": "PASS" if owners <= declared_owners else "FAIL",
            "observed": sorted(owners - declared_owners),
            "expected": [],
        },
        {
            "check_id": "declared_room_references",
            "status": "PASS" if rooms <= declared_rooms else "FAIL",
            "observed": sorted(rooms - declared_rooms),
            "expected": [],
        },
        {
            "check_id": "declared_logical_areas",
            "status": "PASS" if areas <= declared_areas else "FAIL",
            "observed": sorted(areas - declared_areas),
            "expected": [],
        },
        {
            "check_id": "review_queue_is_explicit",
            "status": "PASS" if all(item["next_action"] for item in review_files) else "FAIL",
            "observed": len(review_files),
            "expected": "every review item has next_action",
        },
        {
            "check_id": "foundation_status_not_promoted",
            "status": "PASS" if gate.get("status") == "BLOCKED" else "REVIEW_REQUIRED",
            "observed": gate.get("status"),
            "expected": "BLOCKED",
        },
    ]
    hard_fail = any(check["status"] == "FAIL" for check in checks)
    audit_status = "FAIL" if hard_fail else "PASS_WITH_REVIEW_REQUIRED" if review_files else "PASS"
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    counts = Counter(item["file_kind"] for item in files)
    owner_counts = Counter(item["owner_id"] for item in files)
    area_counts = Counter(item["logical_area"] for item in files)
    evidence_counts = Counter(item["evidence_status"] for item in files)
    migration_counts = Counter(item["migration_state"] for item in files)

    registry = {
        "schema_version": "1.0",
        "registry_id": policy.get("registry_id", "UET-RESEARCH-ORGANIZATION"),
        "artifact": "uet_research_organization_registry",
        "generated_at": generated_at,
        "generator": "docs/scripts/audit/build_uet_research_organization_registry.py",
        "status": audit_status,
        "controlling_blocker": "organization_assignment_and_migration_queue_open" if review_files else None,
        "scientific_foundation_status": {
            "status": gate.get("status"),
            "audit_status": gate.get("audit_status"),
            "blocker": gate.get("blocker"),
            "source": repo_path(FOUNDATION_GATE_PATH),
        },
        "source_policy": repo_path(POLICY_PATH),
        "source_artifacts": [repo_path(MANIFEST_PATH), repo_path(FAMILY_CONTRACT_PATH), repo_path(FOUNDATION_GATE_PATH)],
        "counts": dict(sorted(counts.items())),
        "owner_counts": dict(sorted(owner_counts.items())),
        "logical_area_counts": dict(sorted(area_counts.items())),
        "evidence_status_counts": dict(sorted(evidence_counts.items())),
        "migration_state_counts": dict(sorted(migration_counts.items())),
        "review_queue_count": len(review_files),
        "owners": policy.get("owners", []),
        "rooms": policy.get("rooms", []),
        "logical_areas": policy.get("logical_areas", {}),
        "dependency_edges": policy.get("dependency_edges", []),
        "parallel_policy": policy.get("parallel_policy", {}),
        "files": files,
        "rules": {
            "one_file_one_owner": True,
            "one_file_one_primary_logical_area": True,
            "organization_status_does_not_promote_physics": True,
            "generated_artifacts_are_not_hand_edited": True,
        },
    }

    migration = {
        "schema_version": "1.0",
        "artifact": "uet_core_file_migration_map",
        "generated_at": generated_at,
        "generator": "docs/scripts/audit/build_uet_research_organization_registry.py",
        "status": audit_status,
        "controlling_blocker": "organization_assignment_and_migration_queue_open" if review_files else None,
        "physical_move_performed": False,
        "preconditions": [
            "owner and logical area assigned",
            "import scan passes",
            "link scan passes",
            "compatibility tests pass",
            "generator paths are updated",
        ],
        "files": [
            {
                "asset_id": item["asset_id"],
                "current_path": item["path"],
                "target_path": item["target_physical_path"],
                "owner_id": item["owner_id"],
                "room_id": item["room_id"],
                "organization_status": item["organization_status"],
                "migration_state": item["migration_state"],
                "import_reference_count": item["import_reference_count"],
                "link_reference_count": item["link_reference_count"],
                "reference_scan_status": item["reference_scan_status"],
                "compatibility_plan": "retain_current_path_until_import_link_and_test_gates_pass",
                "next_action": item["next_action"],
            }
            for item in files
        ],
    }

    audit = {
        "schema_version": "1.0",
        "artifact": "uet_core_organization_audit",
        "generated_at": generated_at,
        "generator": "docs/scripts/audit/build_uet_research_organization_registry.py",
        "status": audit_status,
        "controlling_blocker": "organization_assignment_and_migration_queue_open" if review_files else None,
        "scope": {
            "manifest_file_count": len(files),
            "review_queue_count": len(review_files),
            "foundation_status": gate.get("status"),
        },
        "checks": checks,
        "unassigned_paths": [item["path"] for item in review_files],
        "duplicate_asset_ids": duplicate_ids,
        "source_policy": repo_path(POLICY_PATH),
        "source_manifest": repo_path(MANIFEST_PATH),
        "claim_boundary": "organization pass does not promote any physics or application claim",
    }

    index_lines = [
        "# Core Research Organization Index",
        "",
        "> Generated by `docs/scripts/audit/build_uet_research_organization_registry.py`. Do not hand-edit.",
        "",
        f"Generated at: `{generated_at}`",
        f"Organization registry: [`{REGISTRY_PATH.name}`](../artifacts/{REGISTRY_PATH.name})",
        f"Migration map: [`{MIGRATION_PATH.name}`](../artifacts/{MIGRATION_PATH.name})",
        f"Audit: [`{AUDIT_PATH.name}`](../artifacts/{AUDIT_PATH.name})",
        "",
        "## Current state",
        "",
        f"- Organization status: **{audit_status}**",
        f"- Files indexed: **{len(files)}**",
        f"- Review queue: **{len(review_files)}**",
        f"- Foundation gate: **{gate.get('status')}**",
        "- Physical migration: **not performed**",
        "",
        "## Owner counts",
        "",
        "| Owner | Files |",
        "| :-- | --: |",
    ]
    index_lines.extend(f"| `{key}` | {value} |" for key, value in sorted(owner_counts.items()))
    index_lines += ["", "## Logical areas", "", "| Area | Files |", "| :-- | --: |"]
    index_lines.extend(f"| `{key}` | {value} |" for key, value in sorted(area_counts.items()))
    index_lines += [
        "",
        "## Operating rule",
        "",
        "`request → owner → lane → blocker → inputs → verifier → artifact → handoff`",
        "",
        "The registry is an organization view. Scientific status remains controlled by the foundation gate and linked evidence artifacts.",
        "",
        "## First review queue",
        "",
    ]
    index_lines.extend(f"- `{item['path']}` → `{item['next_action']}`" for item in review_files[:100])
    if len(review_files) > 100:
        index_lines.append(f"- … {len(review_files) - 100} more paths are listed in the migration map")
    index_lines.append("")
    return registry, migration, audit, "\n".join(index_lines)


def canonical_without_timestamp(payload: dict[str, Any]) -> dict[str, Any]:
    copied = json.loads(json.dumps(payload))
    copied.pop("generated_at", None)
    return copied


def canonical_index(text: str) -> str:
    return re.sub(r"Generated at: `[^`]+`", "Generated at: `<timestamp>`", text)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare existing outputs without writing")
    args = parser.parse_args()

    source = ROOT / "docs" / "scripts" / "audit" / "reconcile_uet_core_registry_v4.py"
    spec = importlib.util.spec_from_file_location("uet_core_registry_reconcile", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load canonical generator: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outputs = module.build()
    registry = outputs["registry"]
    migration = outputs["migration"]
    audit = outputs["audit"]
    index = outputs["organization_index"]

    outputs = {
        REGISTRY_PATH: registry,
        MIGRATION_PATH: migration,
        AUDIT_PATH: audit,
    }
    if args.check:
        mismatches: list[str] = []
        for path, expected in outputs.items():
            if not path.exists():
                mismatches.append(repo_path(path))
                continue
            actual = load_json(path)
            if canonical_without_timestamp(actual) != canonical_without_timestamp(expected):
                mismatches.append(repo_path(path))
        if not INDEX_PATH.exists() or canonical_index(INDEX_PATH.read_text(encoding="utf-8")) != canonical_index(index):
            mismatches.append(repo_path(INDEX_PATH))
        print(json.dumps({"status": "PASS" if not mismatches else "DRIFT", "mismatches": mismatches}, ensure_ascii=False))
        return 0 if not mismatches else 1

    for path, payload in outputs.items():
        write_json(path, payload)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(index, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": audit["status"],
                "registry": repo_path(REGISTRY_PATH),
                "migration_map": repo_path(MIGRATION_PATH),
                "audit": repo_path(AUDIT_PATH),
                "index": repo_path(INDEX_PATH),
                "indexed_files": len(registry["files"]),
                "review_queue_count": registry["review_queue_count"],
                "foundation_status": registry.get("scientific_foundation_status", {}).get("status"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
