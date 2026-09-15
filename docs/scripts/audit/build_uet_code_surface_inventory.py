"""Inventory equation-like code surfaces that are not yet represented in formula audits.

This is a conservative static scan.  It does not decide whether a line is an equation;
it identifies code that contains mathematical operators or named physical quantities so
that F0/F1/F2 review cannot silently omit implementation-only relations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
INVENTORY_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"
REGISTRY_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
OUTPUT = ROOT / "docs/core/07_artifacts/archive/uet_code_surface_inventory.json"


MATH_TOKENS = (
    "np.",
    "math.",
    "**",
    "sqrt",
    "exp",
    "log",
    "sin",
    "cos",
    "tan",
    "gradient",
    "laplacian",
    "potential",
    "energy",
    "entropy",
    "stress",
    "current",
    "density",
    "mass",
    "omega",
    "mu_",
    "phi",
    "kappa",
    "beta",
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def strip_comment(line: str) -> str:
    # This is intentionally not a Python parser; preserve code text while removing the
    # most common trailing comment noise from the inventory display.
    return line.split("#", 1)[0].rstrip()


def is_candidate(line: str) -> bool:
    code = strip_comment(line).strip()
    if not code or code.startswith(("#", "\"\"\"", "'''")):
        return False
    if code.startswith("def ") or code.startswith("class "):
        return True
    if "=" not in code or "==" in code or ">=" in code or "<=" in code or "!=" in code:
        return False
    return any(token in code.lower() for token in MATH_TOKENS)


def build_inventory() -> dict[str, Any]:
    formula_inventory = load(INVENTORY_PATH)
    registry = load(REGISTRY_PATH)
    formula_records = formula_inventory.get("records", [])
    referenced_surfaces = " ".join(
        str(record.get("code_surface", "")) for record in formula_records
    ).lower()
    referenced_core_paths = " ".join(
        str(path)
        for entry in registry.get("entries", [])
        for path in entry.get("implementation_paths", [])
    ).lower()

    python_paths = sorted(
        path
        for path in (ROOT / "docs/core").rglob("*.py")
        if not (set(part.lower() for part in path.relative_to(ROOT).parts[:-1]) & {"data", "test", "scripts", "__pycache__"})
    )
    records: list[dict[str, Any]] = []
    file_summary: Counter[str] = Counter()
    unlinked_files: list[str] = []

    for path in python_paths:
        path_rel = rel(path)
        path_lower = path_rel.lower()
        if path_lower not in referenced_surfaces and path_lower not in referenced_core_paths:
            unlinked_files.append(path_rel)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        current_function: str | None = None
        for line_number, raw_line in enumerate(lines, start=1):
            code = strip_comment(raw_line).strip()
            match = re.match(r"def\s+([A-Za-z_]\w*)", code)
            if match:
                current_function = match.group(1)
            if not is_candidate(raw_line):
                continue
            if code.startswith("def "):
                kind = "function_surface"
            else:
                kind = "equation_like_assignment"
            records.append(
                {
                    "surface_id": f"{path_rel}:{line_number}",
                    "path": path_rel,
                    "line": line_number,
                    "function": current_function,
                    "kind": kind,
                    "code": code,
                    "registry_link_status": "REVIEW_REQUIRED",
                    "ontology_status": "OPEN",
                    "unit_status": "OPEN",
                    "derivation_status": "OPEN",
                    "claim_status": "NOT_EVIDENCE",
                }
            )
            file_summary[path_rel] += 1

    category_counts = Counter(record["kind"] for record in records)
    return {
        "schema_version": "1.0",
        "artifact": "uet_code_surface_inventory",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS_WITH_DISCLOSED_GAPS",
        "inventory_gate_status": "BLOCKED" if records or unlinked_files else "PASS",
        "controlling_blocker": "code_only_equation_surfaces_require_F1_F2_F3_review" if records or unlinked_files else None,
        "coverage": {
            "core_python_file_count": len(python_paths),
            "candidate_surface_count": len(records),
            "unlinked_core_file_count": len(unlinked_files),
            "scope": "docs/core Python implementation surfaces excluding tests",
            "limitation": "static candidate scan; not a parser or equation proof",
        },
        "summary": {
            "candidate_kind_counts": dict(sorted(category_counts.items())),
            "candidate_files": dict(sorted(file_summary.items())),
            "unlinked_core_files": unlinked_files,
        },
        "records": records,
        "interpretation": {
            "rule": "candidate code is not accepted as a physical equation until registry, ontology, units, derivation, and observable mapping are linked",
            "no_claim_rule": "this artifact cannot promote a formula or prove a contradiction; it only prevents omission from F0",
        },
        "next_controller": "manually classify candidate surfaces that belong to the core equation family or quarantine them as implementation/comparator code",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit full inventory")
    parser.add_argument("--no-write", action="store_true", help="do not write artifact")
    args = parser.parse_args()
    try:
        inventory = build_inventory()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(inventory, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={inventory['audit_status']}")
        print(f"inventory_gate_status={inventory['inventory_gate_status']}")
        print(f"core_python_file_count={inventory['coverage']['core_python_file_count']}")
        print(f"candidate_surface_count={inventory['coverage']['candidate_surface_count']}")
        print(f"unlinked_core_file_count={inventory['coverage']['unlinked_core_file_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
