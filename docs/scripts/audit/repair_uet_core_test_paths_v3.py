"""Repair legacy core-test path calculations before physical relocation.

The old test tree used ``Path(__file__).parents[...]`` to reach repository
locations.  Once tests are grouped under ``05_tests`` those depths change.
This pass rewrites only known repository-root/core/artifact path idioms to the
shared path authority and records a machine-readable change list.  It does not
change assertions or scientific status.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "docs" / "core" / "test"
OUTPUT = ROOT / "docs" / "core" / "00_governance" / "uet_core_test_path_repair_v3.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def insert_import(source: str, names: set[str]) -> str:
    if not names:
        return source
    import_line = (
        "from docs.core.core_paths import "
        + ", ".join(sorted(names))
        + "\n"
    )
    if "from docs.core.core_paths import " in source:
        return source
    tree = ast.parse(source)
    insertion = 0
    body = list(tree.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
        if isinstance(body[0].value.value, str):
            insertion = body[0].end_lineno or 0
    if insertion < len(body) and isinstance(body[insertion], ast.ImportFrom) and body[insertion].module == "__future__":
        insertion = body[insertion].end_lineno or insertion
    lines = source.splitlines(keepends=True)
    offset = sum(len(line) for line in lines[:insertion])
    return source[:offset] + import_line + source[offset:]


def rewrite(source: str) -> tuple[str, list[str]]:
    changed: list[str] = []
    replacements: list[tuple[str, str, str]] = [
        (
            r'Path\(__file__\)\.resolve\(\)\.parents\[1\]\s*/\s*["\']artifacts["\']\s*/\s*["\']([^"\']+)["\']',
            r'canonical_artifact_path("\1")',
            "artifact_path",
        ),
        (
            r'Path\(__file__\)\.resolve\(\)\.parents\[1\]\s*/\s*["\']artifacts["\']',
            "CANONICAL_ARTIFACT_ROOT",
            "artifact_root",
        ),
        (
            r'Path\(__file__\)\.resolve\(\)\.parents\[3\]',
            "repo_root()",
            "repo_root",
        ),
        (
            r'Path\(__file__\)\.resolve\(\)\.parents\[2\]',
            '(repo_root() / "docs")',
            "repo_root",
        ),
        (
            r'Path\(__file__\)\.resolve\(\)\.parents\[1\]',
            "core_root()",
            "core_root",
        ),
        (
            r'Path\(__file__\)\.parent\.parent',
            "core_root()",
            "core_root",
        ),
        (
            r'os\.path\.join\(os\.path\.dirname\(__file__\),\s*["\']\.\./\.\.["\']\)',
            "str(core_root())",
            "core_root",
        ),
        (
            r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)\)',
            "str(repo_root())",
            "repo_root",
        ),
    ]
    names: set[str] = set()
    for pattern, replacement, label in replacements:
        source, count = re.subn(pattern, replacement, source)
        if count:
            changed.extend([label] * count)
            if label == "artifact_path":
                names.add("canonical_artifact_path")
            elif label == "artifact_root":
                names.add("CANONICAL_ARTIFACT_ROOT")
            else:
                names.add(label)
    return insert_import(source, names), changed


def main() -> int:
    rows: list[dict[str, object]] = []
    for path in sorted(SOURCE_ROOT.rglob("*.py")):
        if path.name in {"__init__.py", "sandbox_emergent.py"} or "parameter_engine" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        repaired, changes = rewrite(original)
        if not changes:
            continue
        ast.parse(repaired, filename=str(path))
        path.write_text(repaired, encoding="utf-8")
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256_before": hashlib.sha256(original.encode("utf-8")).hexdigest(),
                "sha256_after": sha256(path),
                "changes": changes,
            }
        )
    payload = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/repair_uet_core_test_paths_v3.py",
        "scope": "docs/core/test",
        "claim_boundary": "Path repair only; no test assertion or physics claim changed.",
        "files_repaired": len(rows),
        "change_counts": {key: sum(key in row["changes"] for row in rows) for key in sorted({item for row in rows for item in row["changes"]})},
        "records": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "files_repaired": len(rows), "artifact": OUTPUT.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
