"""Build a conservative logical manifest for docs/core without moving files."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
ARTIFACTS = CORE / "artifacts"
CONTRACT_PATH = ARTIFACTS / "uet_core_equation_family_contract.json"
CODE_INVENTORY_PATH = ARTIFACTS / "uet_code_surface_inventory.json"
MANIFEST_PATH = ARTIFACTS / "uet_core_file_manifest.json"
INDEX_PATH = CORE / "CORE_FILE_INDEX.md"


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return {}, f"{repo_path(path)}: {type(exc).__name__}: {exc}"


def family_maps() -> tuple[dict[str, dict[str, Any]], set[str], list[str]]:
    contract, contract_error = load_json(CONTRACT_PATH)
    inventory, inventory_error = load_json(CODE_INVENTORY_PATH)
    by_module: dict[str, dict[str, Any]] = {}
    for family in contract.get("families", []):
        for path in family.get("module_paths", []):
            by_module[path.replace("\\", "/")] = family
    unlinked = {
        path.replace("\\", "/")
        for path in inventory.get("summary", {}).get("unlinked_core_files", [])
    }
    errors = [error for error in (contract_error, inventory_error) if error]
    return by_module, unlinked, errors


def artifact_domain(name: str) -> str:
    topic13_prefixes = (
        "t13_", "topic13_", "thermal_", "he4_", "ding_", "gaia_", "xie_",
        "nist_", "nims_", "gatech_", "oxford_", "berut_", "huang_", "hitrace_",
        "desorbo_", "calorine_", "farooqui_", "lowitzer_", "perez_", "peterson_",
        "phonix_", "mp48_", "ued_", "source_",
    )
    return "topic13_or_source" if name.startswith(topic13_prefixes) else "foundation_or_shared"


def base_record(path: Path) -> dict[str, Any]:
    return {
        "path": repo_path(path),
        "file_kind": "review_required",
        "logical_area": "99_review",
        "owner_family_or_lane": None,
        "registry_link_status": "NOT_APPLICABLE",
        "status_source": "MANIFEST_CLASSIFICATION_ONLY",
        "generated_or_source": "source",
        "sha256": file_hash(path),
        "review_action": "classify_and_link",
    }


def classify(path: Path, families: dict[str, dict[str, Any]], unlinked: set[str]) -> dict[str, Any]:
    relative = repo_path(path)
    name = path.name
    suffix = path.suffix.lower()
    record = base_record(path)

    if relative.startswith("docs/core/artifacts/"):
        record.update(
            file_kind="generated_artifact",
            logical_area="07_artifacts",
            owner_family_or_lane=artifact_domain(name),
            generated_or_source="generated",
            review_action="retain_path_and_link_generator",
        )
        return record

    if relative.startswith("docs/core/test/"):
        record.update(
            file_kind="verifier_or_regression_test",
            logical_area="05_tests",
            owner_family_or_lane="core_test_surface",
            review_action="link_to_equation_family_or_artifact",
        )
        return record

    if relative.startswith("docs/core/data/"):
        record.update(
            file_kind="declared_input_data",
            logical_area="06_data",
            owner_family_or_lane="core_data_surface",
            review_action="add_provenance_manifest_and_unit_lane",
        )
        return record

    if relative.startswith("docs/core/02_Proof/"):
        record.update(
            file_kind="proof_or_derivation_runner",
            logical_area="04_proofs",
            owner_family_or_lane="proof_surface",
            review_action="link_formula_and_verifier_output",
        )
        return record

    if name == "AGENTS.md":
        record.update(
            file_kind="folder_governance",
            logical_area="00_governance",
            owner_family_or_lane="core_governance",
            review_action="keep_as_folder_rule",
        )
        return record

    if name == "README.md":
        record.update(
            file_kind="navigation_and_legacy_boundary",
            logical_area="00_governance",
            owner_family_or_lane="core_navigation",
            review_action="link_to_current_gate_and_generated_index",
        )
        return record

    if name.endswith("UPDATE_LOG.md"):
        record.update(
            file_kind="update_log",
            logical_area="08_history",
            owner_family_or_lane="core_history",
            review_action="retain_one_entry_per_completed_wave",
        )
        return record

    if suffix == ".py":
        family = families.get(relative)
        if family:
            is_equation = bool(family.get("equation_family"))
            record.update(
                file_kind="equation_module" if is_equation else "support_or_adapter_module",
                logical_area="02_equations" if is_equation else "03_lanes",
                owner_family_or_lane=family.get("family_id"),
                registry_link_status="LINKED_BY_FAMILY_CONTRACT",
                status_source="docs/core/artifacts/uet_core_equation_family_contract.json",
                review_action="update_family_record_when_surface_changes",
            )
            return record
        if relative in unlinked:
            record.update(
                file_kind="unlinked_python_surface",
                logical_area="99_review",
                owner_family_or_lane="REVIEW_REQUIRED",
                registry_link_status="REVIEW_REQUIRED",
                status_source="docs/core/artifacts/uet_code_surface_inventory.json",
                review_action="assign_family_or_quarantine",
            )
            return record
        if name.startswith(("uet_o2_", "thermal_", "he4_", "standard_")):
            record.update(
                file_kind="lane_specific_module",
                logical_area="03_lanes",
                owner_family_or_lane="lane_owner_review_required",
                registry_link_status="REVIEW_REQUIRED",
                review_action="declare_lane_and_registry_link",
            )
            return record
        record.update(
            file_kind="unassigned_python_surface",
            logical_area="99_review",
            owner_family_or_lane="REVIEW_REQUIRED",
            registry_link_status="REVIEW_REQUIRED",
            review_action="assign_family_or_quarantine",
        )
        return record

    if suffix == ".md":
        if name.startswith("T13_"):
            area = "03_lanes"
            owner = "topic13_lane_review_required"
        elif name.startswith(("UET_", "MATTER_", "O2_", "CARRIER_", "IMPACT_", "RESOURCE_", "TRACE_")):
            area = "01_contracts"
            owner = "core_contract_or_report_review_required"
        else:
            area = "01_contracts"
            owner = "core_document_review_required"
        record.update(
            file_kind="specification_or_research_note",
            logical_area=area,
            owner_family_or_lane=owner,
            review_action="link_to_registry_and_current_artifact",
        )
        return record

    record["review_action"] = "classify_nonstandard_file"
    return record


def write_index(manifest: dict[str, Any]) -> None:
    review = [
        record["path"]
        for record in manifest["files"]
        if record["registry_link_status"] == "REVIEW_REQUIRED"
    ]
    lines = [
        "# Core File Index",
        "",
        "> Generated by `docs/scripts/audit/build_uet_core_file_manifest.py`. Do not hand-edit.",
        "",
        f"Generated at: `{manifest['generated_at']}`",
        "Manifest: [`uet_core_file_manifest.json`](artifacts/uet_core_file_manifest.json)",
        "",
        "## Scope",
        "",
        "Logical index only. Files have not been physically moved; existing import and link paths remain valid.",
        "",
        "## Counts",
        "",
        "| Measure | Count |",
        "| :-- | --: |",
    ]
    for key, value in manifest["counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines += ["", "## Logical areas", "", "| Area | Files |", "| :-- | --: |"]
    for key, value in manifest["logical_area_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines += ["", "## Review queue", "", f"Paths requiring review: **{len(review)}**.", ""]
    lines.extend(f"- `{path}`" for path in review)
    lines += [
        "",
        "Review-required means organization is incomplete; it does not mean the path contains a physical equation.",
        "",
    ]
    INDEX_PATH.write_text("\n".join(lines), encoding="utf-8")


def build() -> dict[str, Any]:
    families, unlinked, parse_errors = family_maps()
    paths = sorted(
        path
        for path in CORE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix.lower() != ".pyc"
    )
    records = [classify(path, families, unlinked) for path in paths]
    counts = Counter(record["file_kind"] for record in records)
    area_counts = Counter(record["logical_area"] for record in records)
    review_count = sum(record["registry_link_status"] == "REVIEW_REQUIRED" for record in records)
    manifest = {
        "schema_version": "1.0",
        "artifact": "uet_core_file_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": repo_path(Path(__file__)),
        "status": "PASS_WITH_REVIEW_REQUIRED" if review_count else "PASS",
        "controlling_blocker": "unlinked_or_ambiguous_core_paths_require_family_assignment_or_quarantine" if review_count else None,
        "scope": "docs/core files excluding __pycache__ and .pyc",
        "source_artifacts": [repo_path(CONTRACT_PATH), repo_path(CODE_INVENTORY_PATH)],
        "counts": dict(sorted(counts.items())),
        "logical_area_counts": dict(sorted(area_counts.items())),
        "review_required_count": review_count,
        "source_artifact_parse_errors": parse_errors,
        "files": records,
        "rules": [
            "classification does not promote a physical claim",
            "unlinked or ambiguous paths remain review-required",
            "physical moves require import/link and targeted-test gates",
            "generated artifacts must be rebuilt by their generator",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_index(manifest)
    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps({
        "artifact": repo_path(MANIFEST_PATH),
        "index": repo_path(INDEX_PATH),
        "status": result["status"],
        "file_count": len(result["files"]),
        "review_required_count": result["review_required_count"],
        "counts": result["counts"],
    }, ensure_ascii=False, sort_keys=True))
