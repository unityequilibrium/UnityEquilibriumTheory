"""Build the F0 inventory from topic formula-audit registries.

The inventory is deliberately a discovery artifact, not a physics validation artifact.
It records what the repository already names as a formula and keeps scaffold/open rows
visible instead of silently treating them as established equations.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json"


ROLE_BY_TOPIC = {
    "0.10": "pilot_or_comparator",
    "0.11": "active_foundation_pilot",
    "0.12": "standard_benchmark_with_open_bridge",
    "0.13": "active_foundation_pilot",
    "0.17": "downstream_particle_mass_lane",
    "0.19": "covariant_foundation_comparator",
    "0.20": "standard_benchmark_with_open_bridge",
    "0.23": "cross_scale_dependency_lane",
    "0.26": "downstream_cosmic_lane",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def parse_table_row(line: str, header_count: int) -> list[str] | None:
    if not line.lstrip().startswith("|"):
        return None
    raw = line.strip()
    if raw.startswith("|--") or raw.startswith("| :--") or set(raw.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
        return None
    parts = [part.strip() for part in raw.strip("|").split("|")]
    if not parts or parts[0].startswith(":") or set("-:") >= set(parts[0] or "-"):
        return None
    if len(parts) > header_count:
        # Formula relations occasionally contain |grad(...)|.  In the known registries
        # the extra bars belong to the relation column, so merge them there.
        extra = len(parts) - header_count
        relation_end = 2 + extra
        parts = [parts[0], " | ".join(parts[1:relation_end]), *parts[relation_end:]]
    if len(parts) < header_count:
        parts.extend([""] * (header_count - len(parts)))
    return parts[:header_count]


def classify_row(row: dict[str, str], topic_id: str) -> dict[str, Any]:
    clean = lambda value: re.sub(r"[`*]", "", value).lower()
    origin = clean(row.get("constant origin", row.get("constant_origin", "")))
    proof = clean(row.get("proof status", row.get("proof_status", "")))
    relation = clean(row.get("relation", ""))
    code = clean(row.get("code surface", row.get("code_surface", "")))
    text = " ".join((origin, proof, relation, code))

    if "open_placeholder" in text or "scaffold" in text:
        evidence_class = "SCAFFOLD_BLOCKED"
    elif "heuristic" in text or re.search(r"\bopen\b", text):
        evidence_class = "OPEN_OR_HEURISTIC"
    elif (
        "source-backed" in text
        or "source_locked" in text
        or "standard" in text
        or "identity" in text
        or "benchmark_anchor" in text
    ):
        evidence_class = "STANDARD_OR_BENCHMARK"
    elif "checked local" in text or "checked_local" in text:
        evidence_class = "INTERNAL_CHECKED"
    else:
        evidence_class = "REVIEW_REQUIRED"

    if "legacy" in text or "comparator" in text:
        correspondence_status = "LEGACY_OR_COMPARATOR"
    elif "heuristic" in text or "open" in text or "uet" in relation:
        correspondence_status = "UET_BRIDGE_OPEN"
    elif evidence_class == "STANDARD_OR_BENCHMARK":
        correspondence_status = "STANDARD_COUNTERPART_NOT_UET_DERIVATION"
    else:
        correspondence_status = "OPEN_CORRESPONDENCE_REVIEW"

    if topic_id in {"0.11", "0.13"}:
        equation_class = "foundation_pilot_or_constitutive"
    elif topic_id in {"0.19", "0.23", "0.26"}:
        equation_class = "foundation_dependency_or_downstream"
    elif "proof" in code or "research" in code:
        equation_class = "application_or_diagnostic"
    else:
        equation_class = "topic_formula"

    return {
        "equation_class": equation_class,
        "topic_role": ROLE_BY_TOPIC.get(topic_id, "topic_formula_registry"),
        "evidence_class": evidence_class,
        "correspondence_status": correspondence_status,
        "requires_manual_correspondence": correspondence_status not in {
            "STANDARD_COUNTERPART_NOT_UET_DERIVATION",
            "LEGACY_OR_COMPARATOR",
        },
    }


def parse_formula_audit(path: Path) -> list[dict[str, Any]]:
    topic_match = re.search(r"docs[\\/]topics[\\/]([^\\/]+)", rel(path))
    topic_folder = topic_match.group(1) if topic_match else path.parent.name
    topic_id_match = re.match(r"(0\.\d+)", topic_folder)
    topic_id = topic_id_match.group(1) if topic_id_match else topic_folder
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    records: list[dict[str, Any]] = []
    headers: list[str] | None = None

    for line_number, line in enumerate(lines, start=1):
        if not line.lstrip().startswith("|"):
            headers = None
            continue
        raw_headers = [normalize_header(part) for part in line.strip().strip("|").split("|")]
        if "formula id" in raw_headers or "formula id" in raw_headers or "formula_id" in line.lower():
            headers = raw_headers
            continue
        if headers is None:
            continue
        values = parse_table_row(line, len(headers))
        if values is None:
            continue
        row = dict(zip(headers, values))
        formula_id = row.get("formula id") or row.get("formula_id") or row.get("formula id ")
        relation = row.get("relation", "")
        if not formula_id or not relation or formula_id.lower() in {"formula id", "formula_id"}:
            continue
        metadata = classify_row(row, topic_id)
        records.append(
            {
                "topic_id": topic_id,
                "topic_folder": topic_folder,
                "formula_id": formula_id.strip("`").strip(),
                "relation": relation,
                "code_surface": row.get("code surface", ""),
                "variables_and_units": row.get("variables and units", ""),
                "constant_origin": row.get("constant origin", ""),
                "proof_status": row.get("proof status", ""),
                "verification_role": row.get("verification role", ""),
                "failure_mode": row.get("failure mode", row.get("limitation", "")),
                "next_hardening_step": row.get("next hardening step", ""),
                "source": {"path": rel(path), "line": line_number},
                **metadata,
            }
        )
    return records


def build_inventory() -> dict[str, Any]:
    audit_paths = sorted((ROOT / "docs/topics").glob("*/FORMULA_AUDIT.md"))
    records: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    for path in audit_paths:
        try:
            records.extend(parse_formula_audit(path))
        except OSError as exc:
            parse_errors.append(f"{rel(path)}: {exc}")

    by_formula: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_formula[record["formula_id"]].append(record)
    duplicate_ids = {
        formula_id: [item["source"] for item in items]
        for formula_id, items in by_formula.items()
        if len(items) > 1
    }

    topic_counts = Counter(record["topic_id"] for record in records)
    evidence_counts = Counter(record["evidence_class"] for record in records)
    correspondence_counts = Counter(record["correspondence_status"] for record in records)
    scaffold_topics = sorted({record["topic_id"] for record in records if record["evidence_class"] == "SCAFFOLD_BLOCKED"})
    missing_scope = [
        "equations defined only in Python code without a FORMULA_AUDIT row",
        "equations in README/METHOD prose that are not represented in a registry table",
        "complete standard-physics correspondence and observable map for each row",
        "core registry entries outside its current initial seed",
    ]
    if scaffold_topics:
        missing_scope.append("explicit formula replacement for scaffold topics: " + ", ".join(scaffold_topics))

    status = "PASS_WITH_DISCLOSED_GAPS" if records and not parse_errors else "FAIL"
    return {
        "schema_version": "1.0",
        "artifact": "uet_foundation_equation_inventory",
        "generated_at": date.today().isoformat(),
        "audit_status": status,
        "inventory_gate_status": "BLOCKED" if missing_scope or duplicate_ids or parse_errors else "PASS",
        "controlling_blocker": "topic_formula_audits_not_code_complete_or_correspondence_incomplete" if missing_scope or duplicate_ids or parse_errors else None,
        "coverage": {
            "formula_audit_file_count": len(audit_paths),
            "parsed_formula_row_count": len(records),
            "coverage_status": "TOPIC_FORMULA_AUDITS_INVENTORIED_NOT_CODE_COMPLETE",
            "missing_scope": missing_scope,
            "scaffold_topics": scaffold_topics,
        },
        "summary": {
            "topic_counts": dict(sorted(topic_counts.items())),
            "evidence_class_counts": dict(sorted(evidence_counts.items())),
            "correspondence_status_counts": dict(sorted(correspondence_counts.items())),
            "duplicate_formula_ids": duplicate_ids,
        },
        "interpretation": {
            "purpose": "F0 discovery inventory; it is not a proof or promotion gate",
            "standard_formula_rule": "A standard physics formula in a topic registry is a baseline/counterpart unless a UET derivation is separately recorded",
            "scaffold_rule": "SCAFFOLD_BLOCKED rows cannot support a downstream claim",
            "correspondence_rule": "requires_manual_correspondence=true keeps physical interpretation open",
        },
        "records": records,
        "parse_errors": parse_errors,
        "next_controller": "complete core-to-topic dependency mapping and manually review every foundational or UET_BRIDGE_OPEN row",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the complete inventory")
    parser.add_argument("--no-write", action="store_true", help="do not write the generated artifact")
    args = parser.parse_args()
    inventory = build_inventory()
    if not args.no_write and inventory["audit_status"] != "FAIL":
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(inventory, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={inventory['audit_status']}")
        print(f"formula_audit_file_count={inventory['coverage']['formula_audit_file_count']}")
        print(f"parsed_formula_row_count={inventory['coverage']['parsed_formula_row_count']}")
        print(f"scaffold_topics={','.join(inventory['coverage']['scaffold_topics'])}")
        print(f"duplicate_formula_id_count={len(inventory['summary']['duplicate_formula_ids'])}")
    return 0 if inventory["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    sys.exit(main())
