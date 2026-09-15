"""Repair repository-root bootstrap in the remaining core tooling scripts.

The repair is intentionally limited to path resolution.  It does not alter
equations, numerical logic, assertions, data values, or physics status.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
GOVERNANCE = ROOT / "docs" / "core" / "00_governance"
INPUT_MANIFEST = GOVERNANCE / "uet_core_data_tooling_migration_manifest.json"
OUTPUT = GOVERNANCE / "uet_core_data_tooling_path_repair_v3.json"
GENERATOR = "docs/scripts/audit/repair_uet_core_data_tooling_paths_v3.py"

BOOTSTRAP_BEGIN = "# BEGIN UET REPO ROOT BOOTSTRAP"
BOOTSTRAP_END = "# END UET REPO ROOT BOOTSTRAP"
BOOTSTRAP = f'''{BOOTSTRAP_BEGIN}
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
{BOOTSTRAP_END}
'''

PATH_HINT = re.compile(
    r"(?:(?:Path\(__file__\)(?:\.resolve\(\))?|current_file|current_path|script_dir|project_root)\.parents\s*\[\d+\]|"
    r"os\.path\.dirname\([^)]*__file__|"
    r"sys\.path\.(?:insert|append)\([^)]*(?:__file__|os\.getcwd|Path)|"
    r"Path\s*\(\s*[rRuUbB]*['\"](?:[A-Za-z]:|docs/))"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_rows() -> list[dict[str, Any]]:
    payload = json.loads(INPUT_MANIFEST.read_text(encoding="utf-8"))
    return [
        row
        for row in payload.get("records", [])
        if row.get("file_kind") == "python_tool"
        and row.get("migration_state") == "QUARANTINED"
        and (ROOT / row["legacy_path"]).exists()
    ]


def insertion_offset(text: str) -> int:
    tree = ast.parse(text)
    offset = 0
    body = tree.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
        if isinstance(body[0].value.value, str):
            offset = body[0].end_lineno or 0
    future_end = max(
        (
            node.end_lineno or 0
            for node in body
            if isinstance(node, ast.ImportFrom) and node.module == "__future__"
        ),
        default=0,
    )
    return max(offset, future_end)


def replace_path_bootstrap(text: str) -> str:
    replacements = (
        (
            r"(?m)^(current_dir\s*=\s*os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\s*)\n"
            r"^(project_root\s*=\s*os\.path\.dirname\(current_dir\)\s*)",
            "current_dir = str(_UET_REPO_ROOT / \"docs\" / \"scripts\" / \"core\")\nproject_root = str(_UET_REPO_ROOT)\n",
        ),
        (
            r"(?m)^(\s*)script_dir\s*=\s*os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\s*$",
            r'\1script_dir = str(_UET_REPO_ROOT / "docs" / "scripts" / "core")',
        ),
        (
            r"Path\(\s*r?[\"'][^\"']*(?:\\\\|/)docs(?:\\\\|/)topics[\"']\s*\)",
            r'_UET_REPO_ROOT / "docs" / "topics"',
        ),
        (
            r"Path\(\s*r?[\"'][^\"']*docs[\\/]topics[\"']\s*\)",
            r'_UET_REPO_ROOT / "docs" / "topics"',
        ),
        (
            r"Path\(\s*[\"']docs/topics[\"']\s*\)",
            r'_UET_REPO_ROOT / "docs" / "topics"',
        ),
        (
            r"Path\(\s*[\"']docs[\"']\s*\)",
            r'_UET_REPO_ROOT / "docs"',
        ),
        (
            r"Path\(\s*[\"']docs/scripts/maintenance[\"']\s*\)",
            r'_UET_REPO_ROOT / "docs" / "scripts" / "maintenance"',
        ),
        (
            r"Path\(\s*[\"']docs/Figures[\"']\s*\)",
            r'_UET_REPO_ROOT / "docs" / "Figures"',
        ),
        (
            r"(?:Path\(__file__\)\.resolve\(\)|current_file|current_path)\.parents\[\d+\]\s*/\s*[\"']topics[\"']",
            r'_UET_REPO_ROOT / "docs" / "topics"',
        ),
        (
            r"(?:current_file|current_path)\.parents\[\d+\]\s*/\s*[\"']topics[\"']",
            r'_UET_REPO_ROOT / "docs" / "topics"',
        ),
        (
            r"(?:Path\(__file__\)\.resolve\(\)|current_file|current_path)\.parents\[\d+\]",
            r'_UET_REPO_ROOT / "docs"',
        ),
        (
            r"Path\(__file__\)\.parents\[\d+\]",
            r"_UET_REPO_ROOT",
        ),
        (
            r"(?:current_file|current_path)\.parent\.parent\.parent",
            r"_UET_REPO_ROOT",
        ),
        (
            r"Path\(__file__\)\.parent\.parent",
            r"_UET_REPO_ROOT",
        ),
        (
            r"sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent\.parent\)\)",
            r"sys.path.insert(0, str(_UET_REPO_ROOT))",
        ),
        (
            r"sys\.path\.append\(os\.path\.abspath\(os\.path\.join\(os\.path\.dirname\(__file__\),\s*[\"']\.\.[\"']\)\)\)",
            r"sys.path.append(str(_UET_REPO_ROOT))",
        ),
        (
            r"sys\.path\.insert\(0,\s*os\.getcwd\(\)\)",
            r"sys.path.insert(0, str(_UET_REPO_ROOT))",
        ),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    text = re.sub(
        r"Path\(\s*r?[\"']docs[\\/](.*?)[\"']\s*\)",
        lambda match: '_UET_REPO_ROOT / "docs"' + "".join(
            f' / "{part}"' for part in re.split(r"[\\/]+", match.group(1)) if part
        ),
        text,
    )
    text = re.sub(
        r"(?m)^(\s*)root_dir\s*=\s*os\.path\.abspath\(os\.path\.join\(script_dir,\s*[\"']\.\.[\"'],\s*[\"']\.\.[\"']\)\)\s*$",
        r'\1root_dir = _UET_REPO_ROOT',
        text,
    )
    text = re.sub(
        r"(?m)^(\s*)base_dir\s*=\s*os\.path\.abspath\(os\.path\.join\(script_dir,\s*[\"']\.\.[\"'],\s*[\"']\.\.[\"'],\s*[\"']topics[\"']\)\)\s*$",
        r'\1base_dir = _UET_REPO_ROOT / "docs" / "topics"',
        text,
    )
    text = re.sub(
        r"(?m)^(\s*(?:repo_root|root)\s*=\s*)Path\(\s*r?[\"'][^\"']*lad[^\"']*[\"']\s*\)",
        r"\1_UET_REPO_ROOT",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"(?m)^(\s*repo_root\s*=\s*)Path\(\s*r?[\"'][^\"']*v0\.[^\"']*[\"']\s*\)",
        r"\1_UET_REPO_ROOT",
        text,
        flags=re.IGNORECASE,
    )
    return text


def repair_text(text: str) -> tuple[str, list[str]]:
    if BOOTSTRAP_BEGIN not in text:
        offset = insertion_offset(text)
        lines = text.splitlines(keepends=True)
        lines.insert(offset, "\n" + BOOTSTRAP)
        text = "".join(lines)
    repaired = replace_path_bootstrap(text)
    stripped = re.sub(
        rf"(?s){re.escape(BOOTSTRAP_BEGIN)}.*?{re.escape(BOOTSTRAP_END)}\s*",
        "",
        repaired,
    )
    unresolved = sorted(set(match.group(0) for match in PATH_HINT.finditer(stripped)))
    return repaired, unresolved


def build_records(apply: bool) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    changed = 0
    for row in source_rows():
        path = ROOT / row["legacy_path"]
        before = path.read_bytes()
        before_text = before.decode("utf-8")
        try:
            repaired_text, unresolved = repair_text(before_text)
            ast.parse(repaired_text, filename=str(path))
        except (UnicodeDecodeError, SyntaxError, ValueError) as exc:
            records.append(
                {
                    "legacy_path": row["legacy_path"],
                    "status": "BLOCKED_PARSE",
                    "error": str(exc),
                    "sha256_before": sha256_bytes(before),
                    "sha256_after": sha256_bytes(before),
                    "unresolved_path_hints": ["parse_failure"],
                }
            )
            continue
        after = repaired_text.encode("utf-8")
        changed_here = after != before
        if apply and changed_here:
            path.write_bytes(after)
            changed += 1
        records.append(
            {
                "legacy_path": row["legacy_path"],
                "canonical_path": row["canonical_path"],
                "status": "REPAIRED" if changed_here else "UNCHANGED",
                "sha256_before": sha256_bytes(before),
                "sha256_after": sha256_bytes(after),
                "unresolved_path_hints": unresolved,
                "bootstrap_marker_present": BOOTSTRAP_BEGIN in repaired_text,
                "physics_status_change": False,
            }
        )
    return records, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.check and args.apply:
        parser.error("--check and --apply are mutually exclusive")
    records, changed = build_records(args.apply)
    blocked = [
        row
        for row in records
        if row["status"] == "BLOCKED_PARSE" or row.get("unresolved_path_hints")
    ]
    payload = {
        "schema_version": "1.0",
        "artifact": "uet_core_data_tooling_path_repair_v3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "path-sensitive Python tooling under docs/core/data/scripts",
        "physical_move_performed": False,
        "status": "PASS" if not blocked else "BLOCKED_REVIEW_REQUIRED",
        "summary": {
            "files_total": len(records),
            "files_changed": sum(row["status"] == "REPAIRED" for row in records),
            "files_unchanged": sum(row["status"] == "UNCHANGED" for row in records),
            "parse_blocked": sum(row["status"] == "BLOCKED_PARSE" for row in records),
            "unresolved_path_hint_files": sum(bool(row.get("unresolved_path_hints")) for row in records),
            "physics_status_changes": 0,
        },
        "records": records,
        "claim_boundary": "repository path/bootstrap repair only; no physics or evidence promotion",
        "controlling_blocker": None if not blocked else "remaining_path_bootstrap_review",
    }
    GOVERNANCE.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "changed": changed, "summary": payload["summary"]}, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
