"""Smoke-test the public UET core import surface without changing source files."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
AUDIT = CORE / "00_governance" / "uet_core_imports_audit.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build() -> dict[str, object]:
    module_names = sorted(
        f"docs.core.{path.stem}"
        for path in CORE.glob("*.py")
        if path.name not in {"__init__.py", "core_paths.py", "core_compat.py"}
    )
    imported: list[str] = []
    failures: list[dict[str, str]] = []
    for module_name in module_names:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - exact failure is recorded for diagnosis
            failures.append({"module": module_name, "error": f"{type(exc).__name__}: {exc}"})
        else:
            imported.append(module_name)
    try:
        importlib.import_module("docs.core")
    except Exception as exc:  # pragma: no cover
        facade_error = f"{type(exc).__name__}: {exc}"
    else:
        facade_error = None
    checks = [
        {"check_id": "core_facade_imports", "status": "PASS" if facade_error is None else "FAIL"},
        {
            "check_id": "root_module_imports",
            "status": "PASS" if not failures else "FAIL",
            "observed": len(failures),
        },
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_imports_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_imports.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "public_core_import_surface_failed",
        "checks": checks,
        "module_count": len(module_names),
        "imported_modules": imported,
        "failed_modules": failures,
        "facade_error": facade_error,
        "claim_boundary": "import compatibility smoke test only; no physics-status promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "module_count": result["module_count"], "failed": len(result["failed_modules"])}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
