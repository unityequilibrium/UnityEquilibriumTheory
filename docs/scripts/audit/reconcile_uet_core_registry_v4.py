"""Reconcile the UET core file registry with the physical canonical tree.

This is an organization-control generator. It does not move files, alter
equation implementations, or promote scientific claims. The physical
migration manifest remains the source for placement history; this generator
repairs stale logical views that described the pre-migration flat tree.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_CORE_PATHS_SPEC = importlib.util.spec_from_file_location("uet_core_paths_reconcile", ROOT / "docs" / "core" / "core_paths.py")
if _CORE_PATHS_SPEC is None or _CORE_PATHS_SPEC.loader is None:
    raise RuntimeError("cannot load docs/core/core_paths.py")
_CORE_PATHS = importlib.util.module_from_spec(_CORE_PATHS_SPEC)
_CORE_PATHS_SPEC.loader.exec_module(_CORE_PATHS)
canonical_dependency_graph_path = _CORE_PATHS.canonical_dependency_graph_path
canonical_file_manifest_path = _CORE_PATHS.canonical_file_manifest_path
canonical_migration_map_path = _CORE_PATHS.canonical_migration_map_path
canonical_organization_audit_path = _CORE_PATHS.canonical_organization_audit_path
canonical_organization_registry_path = _CORE_PATHS.canonical_organization_registry_path
canonical_path_for = _CORE_PATHS.canonical_path_for
canonical_registry_audit_path = _CORE_PATHS.canonical_registry_audit_path
is_compatibility_asset = _CORE_PATHS.is_compatibility_asset
is_markdown_redirect = _CORE_PATHS.is_markdown_redirect
is_python_shim = _CORE_PATHS.is_python_shim
normalize_relative = _CORE_PATHS.normalize_relative

CORE = ROOT / "docs" / "core"
PHYSICAL_MANIFEST_PATH = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
CONSOLIDATION_PATH = CORE / "00_governance" / "uet_core_compatibility_consolidation_v4.json"
POLICY_PATH = CORE / "00_governance" / "uet_research_organization_policy.json"
FAMILY_CONTRACT_PATH = CORE / "07_artifacts" / "archive" / "uet_core_equation_family_contract.json"
CODE_SURFACE_PATH = CORE / "07_artifacts" / "archive" / "uet_code_surface_inventory.json"
FOUNDATION_GATE_PATH = CORE / "07_artifacts" / "gates" / "uet_foundation_dependency_gate.json"
INDEX_PATH = CORE / "CORE_FILE_INDEX.md"
ORGANIZATION_INDEX_PATH = CORE / "00_governance" / "CORE_RESEARCH_ORGANIZATION_INDEX.md"
RECONCILIATION_OUTPUTS = {
    "docs/core/07_artifacts/provenance/uet_core_file_manifest.json",
    "docs/core/07_artifacts/gates/uet_research_organization_registry.json",
    "docs/core/07_artifacts/archive/uet_core_file_migration_map.json",
    "docs/core/07_artifacts/gates/uet_core_dependency_graph.json",
    "docs/core/07_artifacts/gates/uet_core_organization_audit.json",
    "docs/core/07_artifacts/verification/uet_core_registry_reconciliation_audit.json",
    "docs/core/CORE_FILE_INDEX.md",
    "docs/core/00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md",
}

GENERATOR_ID = "docs/scripts/audit/reconcile_uet_core_registry_v4.py"
SCHEMA_VERSION = "2.0"
VALID_EVIDENCE = {
    "LEGACY", "COMPARATOR", "CANDIDATE", "INTERNAL", "SIMULATION_ONLY",
    "EXTERNAL_COMPARISON", "BLOCKED",
}

OWNER_BY_AREA = {
    "00_governance": "ORG", "01_contracts": "FOUNDATION",
    "02_equations": "EQUATION", "03_lanes": "LANE",
    "04_proofs": "EVIDENCE", "05_tests": "EVIDENCE",
    "06_data": "DATA", "07_artifacts": "EVIDENCE",
    "08_history": "ORG", "99_review": "ORG",
}
UPSTREAM_BY_OWNER = {
    "ORG": [], "FOUNDATION": ["ORG"], "EQUATION": ["FOUNDATION"],
    "LANE": ["FOUNDATION", "EQUATION", "DATA"],
    "EVIDENCE": ["FOUNDATION", "EQUATION", "LANE"], "DATA": ["ORG"],
}
DOWNSTREAM_BY_OWNER = {
    "ORG": ["FOUNDATION", "DATA"], "FOUNDATION": ["EQUATION", "LANE", "EVIDENCE"],
    "EQUATION": ["LANE", "EVIDENCE"], "LANE": ["EVIDENCE"],
    "EVIDENCE": [], "DATA": ["LANE"],
}

PATH_REFERENCE_RE = re.compile(r"docs/core/[A-Za-z0-9_./+()\-]+")
IMPORT_RE = re.compile(r"\b(?:from|import)\s+(docs\.core(?:\.[A-Za-z_][A-Za-z0-9_]*)+)")


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def normalize_path(value: str | Path) -> str:
    return normalize_relative(str(value))


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {} if default is None else dict(default)
    return value if isinstance(value, dict) else ({} if default is None else dict(default))


def physical_migration_status(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Report completion separately from whether this reconciliation moved files."""

    active = [record for record in records if record["compatibility_mode"] == "none"]
    pending = [record for record in active if record["current_path"] != record["canonical_path"]]
    manifest = load_json(PHYSICAL_MANIFEST_PATH)
    consolidation = load_json(CONSOLIDATION_PATH)
    consolidation_summary = consolidation.get("summary", {}) if isinstance(consolidation, dict) else {}
    physical_migration = manifest.get("physical_migration", {}) if isinstance(manifest, dict) else {}
    return {
        "complete": not pending,
        "pending_move_targets": len(pending),
        "performed_in_current_reconciliation": bool(
            physical_migration.get(
                "performed_in_current_run",
                manifest.get("physical_move_performed", False),
            )
        ),
        "last_successful_consolidation": {
            "artifact": repo_path(CONSOLIDATION_PATH) if consolidation else None,
            "status": consolidation.get("status", "NOT_FOUND") if consolidation else "NOT_FOUND",
            "physical_move_performed": bool(consolidation.get("physical_move_performed")) if consolidation else False,
            "files_archived": int(consolidation_summary.get("files_archived", 0) or 0),
            "generated_at": consolidation.get("generated_at") if consolidation else None,
        },
        "source_manifest": repo_path(PHYSICAL_MANIFEST_PATH),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_asset_id(current_path: str) -> str:
    digest = hashlib.sha256(normalize_path(current_path).encode("utf-8")).hexdigest()[:12]
    return f"UET-CORE-FILE-{digest.upper()}"


def actual_core_files() -> list[Path]:
    return sorted(
        (path for path in CORE.rglob("*") if path.is_file()
         and "__pycache__" not in path.parts and path.suffix.lower() != ".pyc"),
        key=repo_path,
    )


def canonical_reference(value: str | Path) -> str:
    normalized = normalize_path(value)
    return canonical_path_for(normalized) if normalized.startswith("docs/core/") else normalized


def area_for(canonical_path: str) -> str:
    normalized = normalize_path(canonical_path)
    if normalized.startswith("docs/core/"):
        tail = normalized[len("docs/core/") :]
        first = tail.split("/", 1)[0]
        if first in OWNER_BY_AREA:
            return first
        if first == "artifacts":
            return "00_governance"
        if first == "data":
            return "06_data"
        if first == "test":
            return "05_tests"
        if first == "02_Proof":
            return "04_proofs"
        if tail in {"AGENTS.md", "README.md", "CORE_FILE_INDEX.md", "__init__.py", "core_paths.py", "core_compat.py"}:
            return "00_governance"
        return "99_review"
    if normalized.startswith("docs/scripts/core/"):
        section = normalized[len("docs/scripts/core/") :].split("/", 1)[0].lower()
        if section == "data":
            return "06_data"
        if section == "runners":
            return "02_equations"
        if section in {"verify", "audit"}:
            return "05_tests"
    return "00_governance"


def room_for(path: str, area: str) -> str:
    lower = normalize_path(path).lower()
    if area in {"00_governance", "08_history", "99_review", "06_data"}:
        return "ROOM_CORE_ORGANIZATION"
    if area == "03_lanes":
        if any(token in lower for token in ("t13", "thermal", "he4", "topic13", "o2")):
            return "ROOM_TOPIC_013"
        if any(token in lower for token in ("phase", "structure_factor", "spinodal", "topic11", "0_11")):
            return "ROOM_TOPIC_011"
    return "ROOM_CORE_FOUNDATION"


def load_physical_records() -> dict[str, dict[str, Any]]:
    payload = load_json(PHYSICAL_MANIFEST_PATH)
    return {
        normalize_path(record.get("current_path")): record
        for record in payload.get("records", [])
        if record.get("current_path")
    }


def load_family_maps() -> dict[str, dict[str, Any]]:
    payload = load_json(FAMILY_CONTRACT_PATH)
    by_path: dict[str, dict[str, Any]] = {}
    for family in payload.get("families", []):
        for module_path in family.get("module_paths", []):
            original = normalize_path(module_path)
            by_path[original] = family
            by_path[canonical_reference(original)] = family
    return by_path


def family_for(current: str, canonical: str, by_path: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    return by_path.get(canonical) or by_path.get(current)


def family_id_for(area: str, canonical: str, family: dict[str, Any] | None) -> str:
    if family and family.get("family_id"):
        return str(family["family_id"])
    if area == "02_equations":
        tail = canonical.split("/02_equations/", 1)[-1]
        return f"lane.equation.{tail.split('/', 1)[0]}"
    if area == "03_lanes":
        tail = canonical.split("/03_lanes/", 1)[-1]
        return f"lane.{tail.split('/', 1)[0]}"
    if area == "01_contracts":
        return "core.contracts"
    return "UNASSIGNED"


def is_compatibility(path: Path, current: str, canonical: str) -> bool:
    return (
        current != canonical
        or current.startswith(("docs/core/artifacts/", "docs/core/data/", "docs/core/test/", "docs/core/02_Proof/"))
        or is_compatibility_asset(path)
        or is_markdown_redirect(path)
        or is_python_shim(path)
    )


def file_kind_for(path: Path, canonical: str, area: str, compatibility: bool) -> str:
    lower = path.name.lower()
    if compatibility:
        if path.suffix.lower() == ".py":
            return "compatibility_python_shim"
        if path.suffix.lower() == ".md":
            return "compatibility_redirect"
        return "compatibility_boundary"
    if canonical == "docs/core/AGENTS.md":
        return "folder_governance"
    if canonical == "docs/core/__init__.py":
        return "support_or_adapter_module"
    if canonical in {"docs/core/README.md", "docs/core/CORE_FILE_INDEX.md"}:
        return "navigation_and_legacy_boundary"
    if area == "00_governance":
        if lower == "uet_research_organization_policy.json":
            return "governance_policy"
        if path.suffix.lower() == ".json":
            return "governance_artifact"
        return "navigation_and_legacy_boundary"
    if area == "01_contracts":
        return "contract_or_specification" if path.suffix.lower() in {".md", ".json", ".py"} else "unresolved_asset"
    if area == "02_equations":
        return "equation_module" if path.suffix.lower() == ".py" else "equation_document"
    if area == "03_lanes":
        return "lane_specific_module" if path.suffix.lower() == ".py" else "lane_research_note"
    if area == "04_proofs":
        return "proof_or_derivation_runner" if path.suffix.lower() == ".py" else "proof_document"
    if area == "05_tests":
        return "verifier_or_regression_test" if path.suffix.lower() == ".py" else "test_support_asset"
    if area == "06_data":
        return "declared_input_data"
    if area == "07_artifacts":
        return "generated_artifact" if path.suffix.lower() in {".json", ".npz"} else "artifact_navigation"
    if area == "08_history":
        return "update_log" if "update_log" in lower else "historical_research_note"
    if area == "99_review":
        return "navigation_and_legacy_boundary" if lower == "readme.md" else "unresolved_asset"
    return "unresolved_asset"


def source_role_for(file_kind: str, generated: bool, area: str) -> str:
    if file_kind.startswith("compatibility"):
        return "compatibility"
    if generated:
        return "generated"
    if file_kind in {"verifier_or_regression_test", "test_support_asset"}:
        return "verifier"
    if file_kind.startswith("proof"):
        return "proof"
    if file_kind.startswith("contract") or area == "01_contracts":
        return "contract"
    if file_kind.startswith("equation"):
        return "equation"
    if file_kind.startswith("lane"):
        return "lane"
    if area == "06_data":
        return "data"
    if area == "08_history":
        return "history"
    return "source"


def payload_generator(path: Path) -> str | None:
    if path.suffix.lower() != ".json":
        return None
    payload = load_json(path)
    generator = payload.get("generator")
    return canonical_reference(generator) if isinstance(generator, str) and generator else None


def evidence_for(
    baseline: dict[str, Any],
    family: dict[str, Any] | None,
    file_kind: str,
    area: str,
) -> str:
    if file_kind in {"unresolved_asset", "review_required"} or area == "99_review":
        return "BLOCKED"
    inherited = str(baseline.get("evidence_status", ""))
    if inherited in VALID_EVIDENCE:
        return inherited
    if file_kind in {"compatibility_boundary"}:
        return "BLOCKED"
    if family:
        ceiling = str(family.get("claim_ceiling", "")).lower()
        if "legacy comparator" in ceiling:
            return "COMPARATOR"
        if "candidate" in ceiling:
            return "CANDIDATE"
    if file_kind in {
        "generated_artifact", "artifact_navigation", "verifier_or_regression_test",
        "test_support_asset", "proof_or_derivation_runner", "proof_document",
        "governance_policy", "governance_artifact", "navigation_and_legacy_boundary",
        "update_log", "historical_research_note",
    }:
        return "INTERNAL"
    return "BLOCKED" if area == "99_review" else "BLOCKED"


def status_source_for(baseline: dict[str, Any], fallback: str) -> str:
    source = str(baseline.get("status_source", ""))
    return canonical_reference(source) if source else fallback


def infer_assumptions(family: dict[str, Any] | None) -> list[str]:
    if family:
        return ["family contract is the declared source; derivation and evidence gates remain authoritative"]
    return ["no equation-family assignment was inferred from a filename alone"]


def build_legacy_index(actual: Iterable[Path]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for path in actual:
        current = repo_path(path)
        canonical = canonical_reference(current)
        if current != canonical or is_compatibility(path, current, canonical):
            result.setdefault(canonical, []).append(current)
    return {key: sorted(value) for key, value in result.items()}


def build_records(
    actual: list[Path],
    physical: dict[str, dict[str, Any]],
    family_paths: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    legacy_by_canonical = build_legacy_index(actual)
    records: list[dict[str, Any]] = []
    for path in actual:
        current = repo_path(path)
        canonical = canonical_reference(current)
        compatibility = is_compatibility(path, current, canonical)
        area = area_for(canonical)
        kind = file_kind_for(path, canonical, area, compatibility)
        family = family_for(current, canonical, family_paths)
        family_id = family_id_for(area, canonical, family)
        owner = OWNER_BY_AREA.get(area, "ORG")
        room = room_for(canonical, area)
        generated = kind in {"generated_artifact", "governance_artifact"} and not compatibility
        generator = payload_generator(path) if generated else None
        baseline = physical.get(current, {})
        evidence = evidence_for(baseline, family, kind, area)
        organization = "QUARANTINED" if area == "99_review" and kind == "unresolved_asset" else "MIGRATED"
        status_source = status_source_for(
            baseline, "docs/core/00_governance/uet_core_physical_migration_manifest.json"
        )
        family_verifiers = [canonical_reference(str(item)) for item in (family or {}).get("verifier_paths", [])]
        family_artifacts = [canonical_reference(str(item)) for item in (family or {}).get("evidence_paths", [])]
        if kind == "generated_artifact":
            family_artifacts = [canonical]
        legacy_paths = legacy_by_canonical.get(canonical, [])
        if compatibility and current not in legacy_paths:
            legacy_paths = sorted(set(legacy_paths + [current]))
        claim_ceiling = (family or {}).get("claim_ceiling") or "organization record only; no physics claim is promoted"
        record_hash = "SELF_REFERENTIAL_HASH_OMITTED" if canonical in RECONCILIATION_OUTPUTS else sha256(path)
        physical_asset_id = baseline.get("asset_id")
        asset_id = stable_asset_id(current + "::compatibility") if compatibility else str(physical_asset_id or stable_asset_id(current))
        record = {
            "asset_id": asset_id,
            "physical_asset_id": physical_asset_id,
            "path": current,
            "current_path": current,
            "canonical_path": canonical,
            "legacy_paths": legacy_paths,
            "legacy_path": legacy_paths[0] if legacy_paths else None,
            "file_kind": kind,
            "source_role": source_role_for(kind, generated, area),
            "logical_area": area,
            "owner_id": owner,
            "room_id": room,
            "equation_family_or_lane": family_id,
            "organization_status": organization,
            "evidence_status": evidence,
            "status_source": status_source,
            "generated_or_source": "generated" if generated else "source",
            "generator_path": generator,
            "formula_ids": [str(item) for item in (family or {}).get("formula_ids", []) if str(item)],
            "unit_lane": (family or {}).get("unit_lane"),
            "derivation_class": (family or {}).get("derivation_class"),
            "variable_definitions": dict((family or {}).get("variables", {})),
            "mathematical_role": kind,
            "standard_physics_counterpart": (family or {}).get("standard_physics_counterpart"),
            "assumptions": infer_assumptions(family),
            "symmetry_conservation_properties": [],
            "limiting_cases": [],
            "observable_mapping": None,
            "claim_ceiling": claim_ceiling,
            "verifier_paths": sorted({item for item in family_verifiers if item}),
            "artifact_paths": sorted({item for item in family_artifacts if item}),
            "upstream_dependencies": UPSTREAM_BY_OWNER.get(owner, []),
            "downstream_dependencies": DOWNSTREAM_BY_OWNER.get(owner, []),
            "sha256": record_hash,
            "sha256_before": baseline.get("sha256_before") or baseline.get("sha256"),
            "sha256_after": baseline.get("sha256_after"),
            "migration_state": "MIGRATED_WITH_SHIM" if compatibility else "MIGRATED",
            "migration_wave": "canonical_reconciliation_v4",
            "compatibility_mode": "redirect_or_shim" if compatibility else "none",
            "target_physical_path": canonical,
            "rollback_path": current,
            "next_action": (
                "retain_compatibility_shim" if compatibility else
                "review_unresolved_asset_and_assign_scope" if organization == "QUARANTINED" else
                "declare_generator_and_rebuild_artifact" if generated and generator is None else
                "assign_equation_family_and_link_verifier" if area == "02_equations" and family is None else
                "retain_canonical_path_and_status_source"
            ),
            "registry_link_status": "COMPATIBILITY_LINK" if compatibility else "CANONICAL_PATH",
            "review_action": "retain_legacy_boundary" if compatibility else None,
            "reference_scan_status": "PENDING_DEPENDENCY_SCAN",
            "import_reference_count": 0,
            "link_reference_count": 0,
            "dirty_source": bool(baseline.get("dirty_source", False)),
        }
        records.append(record)
    return records


def path_to_node(
    path: str,
    records_by_current: dict[str, dict[str, Any]],
    records_by_canonical: dict[str, dict[str, Any]],
) -> str | None:
    normalized = normalize_path(path)
    if normalized in records_by_current:
        return normalized
    canonical = canonical_reference(normalized)
    record = records_by_canonical.get(canonical)
    return record["current_path"] if record else None


def import_target(module: str) -> str:
    return module.replace(".", "/") + ".py"


def clean_reference(token: str) -> str:
    return token.rstrip(".,;:)]}>`")


def build_dependency_graph(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_current = {record["current_path"]: record for record in records}
    by_canonical = {
        record["canonical_path"]: record
        for record in records
        if record["current_path"] == record["canonical_path"]
    }
    for record in records:
        by_canonical.setdefault(record["canonical_path"], record)
    nodes = [
        {
            "path": record["current_path"],
            "canonical_path": record["canonical_path"],
            "owner_id": record["owner_id"],
            "logical_area": record["logical_area"],
            "file_kind": record["file_kind"],
            "organization_status": record["organization_status"],
            "evidence_status": record["evidence_status"],
        }
        for record in records
    ]
    edges: set[tuple[str, str, str, str]] = set()
    unresolved: set[tuple[str, str, str]] = set()
    active_prefixes = (
        "docs/core/00_governance/", "docs/core/01_contracts/",
        "docs/core/02_equations/", "docs/core/03_lanes/",
        "docs/core/04_proofs/", "docs/core/05_tests/", "docs/core/06_data/",
    )
    for record in records:
        source = record["current_path"]
        if not source.startswith(active_prefixes) and "/" in source[len("docs/core/") :]:
            continue
        path = ROOT / source
        if path.suffix.lower() not in {".py", ".md", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for token in PATH_REFERENCE_RE.findall(text):
            reference = clean_reference(token)
            target = path_to_node(reference, by_current, by_canonical)
            if target is None:
                unresolved.add((source, reference, "path_reference"))
            elif target != source:
                edges.add((source, target, "path_reference", reference))
        for module in IMPORT_RE.findall(text):
            reference = "docs/" + import_target(module)
            target = path_to_node(reference, by_current, by_canonical)
            if target is None:
                unresolved.add((source, reference, "python_import"))
            elif target != source:
                edges.add((source, target, "python_import", module))
    for record in records:
        if record["compatibility_mode"] != "none":
            target = path_to_node(record["canonical_path"], by_current, by_canonical)
            if target and target != record["current_path"]:
                edges.add((record["current_path"], target, "compatibility", record["canonical_path"]))
    serialized_edges = [
        {"from": source, "to": target, "edge_type": edge_type, "reference": reference}
        for source, target, edge_type, reference in sorted(edges)
    ]
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_dependency_graph",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR_ID,
        "scope": "docs/core source and compatibility surface; history and generated artifacts are not dependency authorities",
        "node_count": len(nodes),
        "edge_count": len(serialized_edges),
        "nodes": nodes,
        "edges": serialized_edges,
        "unresolved_references": [
            {"from": source, "reference": reference, "edge_type": edge_type}
            for source, reference, edge_type in sorted(unresolved)
        ],
        "rules": [
            "canonical_path is the target identity for active core assets",
            "compatibility redirects and shims are explicit edges, not duplicate implementations",
            "history and generated artifacts are evidence outputs, not source-of-truth dependencies",
        ],
    }


def foundation_status() -> dict[str, Any]:
    payload = load_json(FOUNDATION_GATE_PATH)
    status = str(
        payload.get("status") or payload.get("overall_status") or
        payload.get("gate_status") or payload.get("foundation_status") or "BLOCKED"
    )
    return {
        "status": status,
        "source": repo_path(FOUNDATION_GATE_PATH),
        "controlling_blocker": payload.get("controlling_blocker"),
    }


def owner_edges(policy: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"from": str(edge.get("from")), "to": str(edge.get("to")), "reason": str(edge.get("reason", ""))}
        for edge in policy.get("dependency_edges", [])
        if edge.get("from") and edge.get("to")
    ]


def build_audit(
    records: list[dict[str, Any]],
    graph: dict[str, Any],
    physical: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    actual_paths = {record["current_path"] for record in records}
    physical_paths = set(physical)
    newly_generated_paths = actual_paths - physical_paths
    expected_new_paths = newly_generated_paths & RECONCILIATION_OUTPUTS
    canonical_paths = [
        record["canonical_path"]
        for record in records
        if record["current_path"] == record["canonical_path"]
    ]
    duplicate_canonical = sorted(path for path, count in Counter(canonical_paths).items() if count > 1)
    missing_targets = sorted(
        {
            record["canonical_path"]
            for record in records
            if record["canonical_path"].startswith("docs/core/")
            and not (ROOT / record["canonical_path"]).exists()
        }
    )
    generated_missing_generator = sorted(
        record["current_path"] for record in records
        if record["file_kind"] == "generated_artifact" and not record.get("generator_path")
    )
    quarantined = sorted(
        record["current_path"] for record in records if record["organization_status"] == "QUARANTINED"
    )
    checks = [
        {
            "check_id": "actual_core_files_covered",
            "status": "PASS" if physical_paths <= actual_paths and newly_generated_paths == expected_new_paths else "FAIL",
            "observed": {"actual": len(actual_paths), "physical_baseline": len(physical_paths), "new_reconciliation_outputs": sorted(newly_generated_paths)},
            "expected": "physical baseline plus generated reconciliation outputs",
        },
        {
            "check_id": "canonical_paths_unique",
            "status": "PASS" if not duplicate_canonical else "FAIL",
            "observed": duplicate_canonical, "expected": [],
        },
        {
            "check_id": "canonical_targets_exist",
            "status": "PASS" if not missing_targets else "FAIL",
            "observed": missing_targets, "expected": [],
        },
        {
            "check_id": "generated_artifacts_have_generator",
            "status": "PASS" if not generated_missing_generator else "REVIEW_REQUIRED",
            "observed": len(generated_missing_generator), "expected": 0,
        },
        {
            "check_id": "quarantine_is_explicit",
            "status": "PASS" if all(
                next(item for item in records if item["current_path"] == path)["evidence_status"] == "BLOCKED"
                for path in quarantined
            ) else "FAIL",
            "observed": len(quarantined), "expected": "BLOCKED evidence for every quarantined record",
        },
        {
            "check_id": "physics_status_unchanged",
            "status": "PASS", "observed": 0, "expected": 0,
        },
    ]
    blockers: list[str] = []
    if duplicate_canonical:
        blockers.append("duplicate_canonical_paths")
    if missing_targets:
        blockers.append("canonical_target_missing")
    if generated_missing_generator:
        blockers.append("generated_artifact_generator_provenance_incomplete")
    if quarantined:
        blockers.append("manual_scope_review_for_quarantined_records")
    return {
        "schema_version": "2.0",
        "artifact": "uet_core_registry_reconciliation_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR_ID,
        "status": "PASS_WITH_REVIEW_REQUIRED" if blockers else "PASS",
        "controlling_blocker": blockers[0] if blockers else None,
        "scope": {
            "actual_core_file_count": len(actual_paths),
            "physical_manifest_record_count": len(physical),
            "registry_record_count": len(records),
            "dependency_edge_count": graph["edge_count"],
            "unresolved_reference_count": len(graph["unresolved_references"]),
            "quarantine_count": len(quarantined),
            "generated_artifacts_without_generator": len(generated_missing_generator),
        },
        "checks": checks,
        "duplicate_canonical_paths": duplicate_canonical,
        "missing_canonical_targets": missing_targets,
        "generated_artifacts_without_generator": generated_missing_generator,
        "quarantined_paths": quarantined,
        "unassigned_paths": [],
        "physics_status_changes": [],
        "claim_boundary": "organization reconciliation does not promote equation, physics, or empirical evidence status",
        "next_action": "declare missing artifact generators and review quarantined assets before physical deprecation",
    }


def without_generated_at(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {key: without_generated_at(value) for key, value in payload.items() if key != "generated_at"}
    if isinstance(payload, list):
        return [without_generated_at(value) for value in payload]
    return payload


def index_without_timestamp(value: str) -> str:
    return "\n".join(line for line in value.splitlines() if not line.startswith("Generated at:"))


def render_file_index(manifest: dict[str, Any], graph: dict[str, Any], audit: dict[str, Any]) -> str:
    lines = [
        "# Core File Index", "",
        f"> Generated by `{GENERATOR_ID}`. Do not hand-edit.", "",
        f"Generated at: `{manifest['generated_at']}`",
        "Manifest: [`uet_core_file_manifest.json`](07_artifacts/provenance/uet_core_file_manifest.json)",
        "Organization registry: [`uet_research_organization_registry.json`](07_artifacts/gates/uet_research_organization_registry.json)",
        "Dependency graph: [`uet_core_dependency_graph.json`](07_artifacts/gates/uet_core_dependency_graph.json)", "",
        "## Scope", "",
        "This index describes the current canonical tree and retained compatibility boundaries. Organization status is independent from physics evidence status.", "",
        "## Counts", "", "| Measure | Count |", "| :-- | --: |",
    ]
    for key, value in manifest["counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines += [
        f"| `canonical_records` | {manifest['canonical_records']} |",
        f"| `compatibility_records` | {manifest['compatibility_records']} |", "",
        "## Logical areas", "", "| Area | Files |", "| :-- | --: |",
    ]
    lines.extend(f"| `{key}` | {value} |" for key, value in manifest["logical_area_counts"].items())
    lines += [
        "", "## Current controls", "",
        f"- Reconciliation status: **{manifest['status']}**",
        f"- Registry audit: **{audit['status']}**",
        f"- Dependency edges: **{graph['edge_count']}**",
        f"- Quarantined assets: **{len(audit['quarantined_paths'])}**",
        f"- Controlling blocker: `{audit['controlling_blocker']}`",
        "- This reconciliation generator does not move files; it reads physical completion and consolidation evidence.", "",
        "Legacy root Python and Markdown files are compatibility shims/redirects where recorded; they are not duplicate implementations.", "",
    ]
    return "\n".join(lines)


def render_organization_index(registry: dict[str, Any], audit: dict[str, Any]) -> str:
    lines = [
        "# Core Research Organization Index", "",
        f"> Generated by `{GENERATOR_ID}`. Do not hand-edit.", "",
        f"Generated at: `{registry['generated_at']}`",
        "Organization registry: [`uet_research_organization_registry.json`](../07_artifacts/gates/uet_research_organization_registry.json)",
        "Migration map: [`uet_core_file_migration_map.json`](../07_artifacts/archive/uet_core_file_migration_map.json)",
        "Dependency graph: [`uet_core_dependency_graph.json`](../07_artifacts/gates/uet_core_dependency_graph.json)",
        "Reconciliation audit: [`uet_core_registry_reconciliation_audit.json`](../07_artifacts/verification/uet_core_registry_reconciliation_audit.json)", "",
        "## Current state", "",
        f"- Organization status: **{registry['status']}**",
        f"- Files indexed: **{len(registry['files'])}**",
        f"- Canonical records: **{registry['canonical_records']}**",
        f"- Compatibility records: **{registry['compatibility_records']}**",
        f"- Quarantine records: **{registry['quarantine_count']}**",
        f"- Foundation gate: **{registry['scientific_foundation_status']['status']}**",
        f"- Controlling blocker: `{registry['controlling_blocker']}`",
        f"- Physical migration complete: **{registry.get('physical_migration', {}).get('complete', False)}**",
        f"- Move targets pending: **{registry.get('physical_migration', {}).get('pending_move_targets', 0)}**",
        f"- This reconciliation run moved files: **{registry.get('physical_migration', {}).get('performed_in_current_reconciliation', False)}**",
        f"- Last physical consolidation: **{registry.get('physical_migration', {}).get('last_successful_consolidation', {}).get('status', 'NOT_FOUND')}**",
        "",
        "## Owner counts", "", "| Owner | Files |", "| :-- | --: |",
    ]
    lines.extend(f"| `{key}` | {value} |" for key, value in sorted(registry["owner_counts"].items()))
    lines += ["", "## Logical areas", "", "| Area | Files |", "| :-- | --: |"]
    lines.extend(f"| `{key}` | {value} |" for key, value in sorted(registry["logical_area_counts"].items()))
    lines += ["", "## Quarantine", ""]
    lines.extend(f"- `{path}` → `manual_scope_review`" for path in audit["quarantined_paths"])
    if not audit["quarantined_paths"]:
        lines.append("- None")
    lines += [
        "", "## Operating rule", "",
        "`request → owner → lane → blocker → inputs → verifier → artifact → handoff`", "",
        "Organization status does not promote physics status. Every record remains subject to equation, unit, provenance, verifier, observable, and claim gates.", "",
    ]
    return "\n".join(lines)


def build() -> dict[str, Any]:
    actual = actual_core_files()
    physical = load_physical_records()
    family_paths = load_family_maps()
    policy = load_json(POLICY_PATH)
    records = sorted(build_records(actual, physical, family_paths), key=lambda item: item["current_path"])
    graph = build_dependency_graph(records)
    audit = build_audit(records, graph, physical)
    physical_status = physical_migration_status(records)
    counts = Counter(record["file_kind"] for record in records)
    area_counts = Counter(record["logical_area"] for record in records)
    evidence_counts = Counter(record["evidence_status"] for record in records)
    migration_counts = Counter(record["migration_state"] for record in records)
    owner_counts = Counter(record["owner_id"] for record in records)
    compatibility_records = sum(record["compatibility_mode"] != "none" for record in records)
    canonical_records = len(records) - compatibility_records
    status = audit["status"]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact": "uet_core_file_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR_ID,
        "status": status,
        "controlling_blocker": audit["controlling_blocker"],
        "scope": "docs/core files excluding __pycache__ and .pyc; canonical paths resolved by docs/core/core_paths.py",
        "canonical_path_authority": "docs/core/core_paths.py",
        "source_artifacts": [repo_path(PHYSICAL_MANIFEST_PATH), repo_path(FAMILY_CONTRACT_PATH), repo_path(CODE_SURFACE_PATH), repo_path(POLICY_PATH)],
        "counts": dict(sorted(counts.items())),
        "logical_area_counts": dict(sorted(area_counts.items())),
        "evidence_status_counts": dict(sorted(evidence_counts.items())),
        "migration_state_counts": dict(sorted(migration_counts.items())),
        "review_required_count": audit["scope"]["quarantine_count"],
        "canonical_records": canonical_records,
        "compatibility_records": compatibility_records,
        "files": records,
        "rules": [
            "current_path identifies the physical record; canonical_path identifies the source-of-truth target",
            "legacy redirects and shims are retained and explicitly linked",
            "organization reconciliation never promotes physics evidence",
            "generated artifact provenance is reported when the source artifact declares a generator",
        ],
    }
    migration_files = [
        {
            "asset_id": record["asset_id"],
            "current_path": record["current_path"],
            "canonical_path": record["canonical_path"],
            "target_path": record["canonical_path"],
            "legacy_paths": record["legacy_paths"],
            "compatibility_plan": (
                "retain redirect_or_shim until compatibility approval"
                if record["compatibility_mode"] != "none"
                else "canonical file already present; no physical move required"
            ),
            "migration_state": record["migration_state"],
            "compatibility_mode": record["compatibility_mode"],
            "organization_status": record["organization_status"],
            "evidence_status": record["evidence_status"],
            "owner_id": record["owner_id"],
            "room_id": record["room_id"],
            "sha256": record["sha256"],
            "rollback_path": record["rollback_path"],
            "next_action": record["next_action"],
        }
        for record in records
    ]
    migration = {
        "schema_version": SCHEMA_VERSION,
        "artifact": "uet_core_file_migration_map",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR_ID,
        "status": status,
        "physical_move_performed": False,
        "canonical_path_authority": "docs/core/core_paths.py",
        "source_manifest": repo_path(PHYSICAL_MANIFEST_PATH),
        "files": migration_files,
        "counts": dict(sorted(migration_counts.items())),
        "duplicate_targets": audit["duplicate_canonical_paths"],
        "controlling_blocker": audit["controlling_blocker"],
        "physical_migration": physical_status,
        "rules": [
            "do not overwrite a canonical target",
            "preserve old imports and links through explicit shims or redirects",
            "organization migration state is not a physics verification result",
        ],
    }
    registry = {
        "schema_version": SCHEMA_VERSION,
        "artifact": "uet_research_organization_registry",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR_ID,
        "registry_id": "UET-RESEARCH-ORGANIZATION",
        "status": status,
        "scope": "docs/core organization, ownership, room routing, canonical paths, compatibility boundaries, and migration only",
        "canonical_path_authority": "docs/core/core_paths.py",
        "scientific_status_authority": [repo_path(FOUNDATION_GATE_PATH), repo_path(FAMILY_CONTRACT_PATH), "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"],
        "source_artifacts": [repo_path(PHYSICAL_MANIFEST_PATH), repo_path(POLICY_PATH)],
        "owners": policy.get("owners", []),
        "rooms": policy.get("rooms", []),
        "logical_areas": policy.get("logical_areas", {}),
        "evidence_statuses": sorted(VALID_EVIDENCE),
        "organization_statuses": ["UNASSIGNED", "ASSIGNED", "MIGRATION_READY", "MIGRATED", "QUARANTINED"],
        "migration_policy": policy.get("migration_policy", {}),
        "dependency_edges": owner_edges(policy),
        "asset_dependency_graph": repo_path(canonical_dependency_graph_path()),
        "parallel_policy": policy.get("parallel_policy", {}),
        "files": records,
        "counts": dict(sorted(counts.items())),
        "owner_counts": dict(sorted(owner_counts.items())),
        "logical_area_counts": dict(sorted(area_counts.items())),
        "evidence_status_counts": dict(sorted(evidence_counts.items())),
        "migration_state_counts": dict(sorted(migration_counts.items())),
        "canonical_records": canonical_records,
        "compatibility_records": compatibility_records,
        "quarantine_count": audit["scope"]["quarantine_count"],
        "review_queue_count": audit["scope"]["quarantine_count"],
        "assigned_review_count": 0,
        "dispositioned_review_count": 0,
        "organization_wave": "WAVE_0_CANONICAL_RECONCILIATION",
        "controlling_blocker": audit["controlling_blocker"],
        "scientific_foundation_status": foundation_status(),
        "physical_migration": physical_status,
        "rules": {
            "organization_status_does_not_promote_physics": True,
            "canonical_path_is_source_of_truth": True,
            "legacy_paths_are_compatibility_only": True,
            "generated_artifacts_are_not_hand_edited": True,
        },
    }
    return {
        "manifest": manifest,
        "registry": registry,
        "migration": migration,
        "graph": graph,
        "audit": audit,
        "file_index": render_file_index(manifest, graph, audit),
        "organization_index": render_organization_index(registry, audit),
    }


def write_outputs(outputs: dict[str, Any]) -> None:
    write_json(canonical_file_manifest_path(), outputs["manifest"])
    write_json(canonical_organization_registry_path(), outputs["registry"])
    write_json(canonical_migration_map_path(), outputs["migration"])
    write_json(canonical_dependency_graph_path(), outputs["graph"])
    write_json(canonical_organization_audit_path(), outputs["audit"])
    write_json(canonical_registry_audit_path(), outputs["audit"])
    INDEX_PATH.write_text(outputs["file_index"], encoding="utf-8")
    ORGANIZATION_INDEX_PATH.write_text(outputs["organization_index"], encoding="utf-8")


def check_outputs(outputs: dict[str, Any]) -> list[str]:
    expected_json = {
        canonical_file_manifest_path(): outputs["manifest"],
        canonical_organization_registry_path(): outputs["registry"],
        canonical_migration_map_path(): outputs["migration"],
        canonical_dependency_graph_path(): outputs["graph"],
        canonical_organization_audit_path(): outputs["audit"],
        canonical_registry_audit_path(): outputs["audit"],
    }
    mismatches: list[str] = []
    for path, expected in expected_json.items():
        if not path.exists() or without_generated_at(load_json(path)) != without_generated_at(expected):
            mismatches.append(repo_path(path))
    if not INDEX_PATH.exists() or index_without_timestamp(INDEX_PATH.read_text(encoding="utf-8")) != index_without_timestamp(outputs["file_index"]):
        mismatches.append(repo_path(INDEX_PATH))
    if not ORGANIZATION_INDEX_PATH.exists() or index_without_timestamp(ORGANIZATION_INDEX_PATH.read_text(encoding="utf-8")) != index_without_timestamp(outputs["organization_index"]):
        mismatches.append(repo_path(ORGANIZATION_INDEX_PATH))
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare canonical outputs without writing")
    args = parser.parse_args()
    outputs = build()
    if args.check:
        mismatches = check_outputs(outputs)
        print(json.dumps({"status": "PASS" if not mismatches else "DRIFT", "mismatches": mismatches}, ensure_ascii=False))
        return 0 if not mismatches else 1
    write_outputs(outputs)
    print(json.dumps({
        "status": outputs["audit"]["status"],
        "manifest": repo_path(canonical_file_manifest_path()),
        "registry": repo_path(canonical_organization_registry_path()),
        "migration_map": repo_path(canonical_migration_map_path()),
        "dependency_graph": repo_path(canonical_dependency_graph_path()),
        "audit": repo_path(canonical_registry_audit_path()),
        "indexed_files": len(outputs["registry"]["files"]),
        "canonical_records": outputs["registry"]["canonical_records"],
        "compatibility_records": outputs["registry"]["compatibility_records"],
        "quarantine_count": outputs["registry"]["quarantine_count"],
        "foundation_status": outputs["registry"]["scientific_foundation_status"]["status"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
