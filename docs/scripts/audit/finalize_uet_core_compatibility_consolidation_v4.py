"""Finalize the audit record after compatibility files were archived."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
GOVERNANCE = CORE / "00_governance"
ALIASES = GOVERNANCE / "uet_core_legacy_module_aliases.json"
OUTPUT = GOVERNANCE / "uet_core_compatibility_consolidation_v4.json"
GENERATOR = "docs/scripts/audit/finalize_uet_core_compatibility_consolidation_v4.py"
RUNPY = re.compile(r'_CANONICAL_RELATIVE\s*=\s*["\']([^"\']+)["\']')
LEGACY = re.compile(r"Legacy path:\s*([^\r\n]+)")
CANONICAL = re.compile(r"Canonical source:\s*\[[^\]]+\]\(([^)]+)\)")


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_link(path: Path, link: str) -> str:
    candidate = (path.parent / link).resolve()
    return repo_path(candidate)


def build_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    if ALIASES.exists():
        payload = json.loads(ALIASES.read_text(encoding="utf-8"))
        for alias in payload.get("aliases", []):
            archive = CORE / "08_history" / "legacy" / "compatibility_shims" / "python" / Path(str(alias["legacy_path"])).name
            records.append(
                {
                    "legacy_path": alias["legacy_path"],
                    "canonical_path": alias["canonical_path"],
                    "archive_path": repo_path(archive),
                    "kind": "root_python_shim",
                }
            )

    data_root = CORE / "08_history" / "legacy" / "compatibility_shims" / "data_scripts"
    data_archives = sorted(data_root.rglob("*.py")) if data_root.exists() else []
    for archive in data_archives:
        target = RUNPY.search(archive.read_text(encoding="utf-8"))
        if target is None:
            continue
        tail = archive.relative_to(data_root).as_posix()
        records.append(
            {
                "legacy_path": f"docs/core/data/scripts/{tail}",
                "canonical_path": target.group(1).replace("\\", "/"),
                "archive_path": repo_path(archive),
                "kind": "legacy_tool_shim",
            }
        )

    proof_root = CORE / "08_history" / "legacy" / "compatibility_shims" / "proofs"
    proof_archives = sorted(proof_root.rglob("*.py")) if proof_root.exists() else []
    for archive in proof_archives:
        target = RUNPY.search(archive.read_text(encoding="utf-8"))
        if target is None:
            continue
        records.append(
            {
                "legacy_path": f"docs/core/02_Proof/{archive.relative_to(proof_root).as_posix()}",
                "canonical_path": target.group(1).replace("\\", "/"),
                "archive_path": repo_path(archive),
                "kind": "legacy_proof_shim",
            }
        )

    redirect_root = GOVERNANCE / "redirects"
    redirect_archives = sorted(redirect_root.rglob("*.md")) if redirect_root.exists() else []
    for archive in redirect_archives:
        text = archive.read_text(encoding="utf-8")
        legacy_match = LEGACY.search(text)
        canonical_match = CANONICAL.search(text)
        if legacy_match is None or canonical_match is None:
            continue
        link = canonical_match.group(1)
        canonical = link if link.startswith("docs/") else resolve_link(archive, link)
        records.append(
            {
                "legacy_path": legacy_match.group(1).strip(),
                "canonical_path": canonical,
                "archive_path": repo_path(archive),
                "kind": "markdown_redirect",
            }
        )
    return sorted(records, key=lambda item: str(item["legacy_path"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the archived boundary without writing")
    args = parser.parse_args()
    records = build_records()
    failures: list[str] = []
    for item in records:
        archive = ROOT / str(item["archive_path"])
        target = ROOT / str(item["canonical_path"])
        if not archive.exists():
            failures.append(f"archive_missing:{item['archive_path']}")
        if not target.exists():
            failures.append(f"canonical_missing:{item['canonical_path']}")
    alias_count = 0
    if ALIASES.exists():
        alias_count = int(json.loads(ALIASES.read_text(encoding="utf-8")).get("alias_count", 0))
    root_redirects = sum(
        item["kind"] == "markdown_redirect"
        and str(item["legacy_path"]).startswith("docs/core/")
        and "/" not in str(item["legacy_path"])[len("docs/core/") :]
        for item in records
    )
    payload = {
        "schema_version": "1.0",
        "artifact": "uet_core_compatibility_consolidation",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "status": "PASS" if not failures else "BLOCKED",
        "physical_move_performed": bool(records),
        "physics_status_changes": 0,
        "summary": {
            "files_archived": len(records),
            "root_python_shims_archived": sum(item["kind"] == "root_python_shim" for item in records),
            "root_markdown_redirects_archived": root_redirects,
            "legacy_tool_shims_archived": sum(item["kind"] == "legacy_tool_shim" for item in records),
            "legacy_boundary_files_archived": len(records) - root_redirects - sum(item["kind"] == "root_python_shim" for item in records) - sum(item["kind"] == "legacy_tool_shim" for item in records),
            "legacy_module_aliases": alias_count,
            "active_reference_rewrite_status": "completed_and_checked_by_canonical_link_audit",
            "physics_status_changes": 0,
        },
        "actions": records,
        "failures": failures,
        "claim_boundary": "physical organization and compatibility consolidation only; no physics/evidence promotion",
    }
    if not args.check:
        if ALIASES.exists():
            alias_payload = json.loads(ALIASES.read_text(encoding="utf-8"))
            for alias in alias_payload.get("aliases", []):
                legacy_path = str(alias.get("legacy_path", ""))
                archive = CORE / "08_history" / "legacy" / "compatibility_shims" / "python" / Path(legacy_path).name
                alias["archive_path"] = repo_path(archive)
                alias["legacy_present"] = False
                alias["status"] = "ARCHIVED_ROOT_SHIM"
            ALIASES.write_text(json.dumps(alias_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "files_archived": payload["summary"]["files_archived"],
                "aliases": payload["summary"]["legacy_module_aliases"],
                "failures": len(failures),
            },
            ensure_ascii=False,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
