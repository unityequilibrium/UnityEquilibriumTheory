"""Validate the foundation-first equation registry, protocol, and dependency gate.

This audit validates workflow integrity. A BLOCKED foundation gate is a valid research
state; it is reported as such and does not become PASS merely because the JSON parses.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
STANDARD = ROOT / "docs/topics/For Work/EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md"
REGISTRY_PATH = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
PROTOCOL_PATH = ROOT / "docs/core/07_artifacts/archive/uet_equation_research_protocol.json"
GATE_PATH = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"

REQUIRED_ENTRY_FIELDS = {
    "equation_id",
    "version",
    "classification",
    "relation_or_code_path",
    "variables",
    "mathematical_role",
    "standard_physics_counterpart",
    "observable_mapping",
    "unit_lane",
    "parameter_dimensions",
    "source_or_origin",
    "assumptions",
    "symmetry_and_conservation",
    "limiting_cases",
    "implementation_paths",
    "verifier_paths",
    "evidence_class",
    "proof_status",
    "downstream_dependencies",
    "claim_boundary",
    "failure_mode",
    "next_hardening_step",
}
REQUIRED_GATES = [f"F{i}_" for i in range(9)]


class DuplicateKeyError(ValueError):
    pass


def _no_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not path.exists():
        return None, [f"missing file: {path.relative_to(ROOT)}"]
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle, object_pairs_hook=_no_duplicate_pairs)
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        return None, [f"invalid JSON {path.relative_to(ROOT)}: {exc}"]
    if not isinstance(value, dict):
        errors.append(f"top level is not an object: {path.relative_to(ROOT)}")
        return None, errors
    return value, errors


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("artifact") != "uet_equation_correspondence_registry":
        errors.append("registry artifact name is incorrect")
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        return errors + ["registry entries must be a non-empty list"]

    seen: set[str] = set()
    for index, entry in enumerate(entries):
        prefix = f"registry.entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} is not an object")
            continue
        missing = sorted(REQUIRED_ENTRY_FIELDS - set(entry))
        errors.extend(f"{prefix} missing {field}" for field in missing)
        equation_id = entry.get("equation_id")
        if not isinstance(equation_id, str) or not equation_id:
            errors.append(f"{prefix}.equation_id must be a non-empty string")
        elif equation_id in seen:
            errors.append(f"duplicate equation_id: {equation_id}")
        else:
            seen.add(equation_id)

        for field in ("implementation_paths", "verifier_paths"):
            paths = entry.get(field, [])
            if not isinstance(paths, list):
                errors.append(f"{prefix}.{field} must be a list")
                continue
            for raw_path in paths:
                if not isinstance(raw_path, str):
                    errors.append(f"{prefix}.{field} contains a non-string path")
                    continue
                candidate = ROOT / raw_path
                if not candidate.exists():
                    errors.append(f"{prefix}.{field} missing path: {raw_path}")

        mapping = entry.get("observable_mapping")
        if not isinstance(mapping, dict) or "status" not in mapping:
            errors.append(f"{prefix}.observable_mapping must include status")

    coverage = registry.get("coverage", {})
    if coverage.get("coverage_status") != "INITIAL_SEED_NOT_EXHAUSTIVE":
        errors.append("registry must disclose whether the initial inventory is exhaustive")
    return errors


def validate_protocol(protocol: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if protocol.get("artifact") != "uet_equation_research_protocol":
        errors.append("protocol artifact name is incorrect")
    stages = protocol.get("mandatory_sequence")
    ids = [stage.get("id") for stage in stages] if isinstance(stages, list) else []
    expected = [f"F{i}" for i in range(9)]
    if ids != expected:
        errors.append(f"protocol sequence must be {expected}, got {ids}")
    rules = protocol.get("status_rules")
    if not isinstance(rules, dict):
        errors.append("protocol status_rules is missing")
    elif "PASS" not in rules.get("pass_dependency_states", []):
        errors.append("protocol must define PASS as the dependency pass state")
    return errors


def validate_gate(gate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if gate.get("artifact") != "uet_foundation_dependency_gate":
        errors.append("gate artifact name is incorrect")
    if gate.get("status") not in {"PASS", "WARN", "BLOCKED"}:
        errors.append("gate status must be PASS, WARN, or BLOCKED")
    for field, expected in (("protocol", PROTOCOL_PATH), ("registry", REGISTRY_PATH)):
        raw_path = gate.get(field)
        if not isinstance(raw_path, str) or not (ROOT / raw_path).exists():
            errors.append(f"gate {field} does not point to an existing artifact")
    gates = gate.get("gates")
    if not isinstance(gates, dict):
        return errors + ["gate.gates is missing"]
    for prefix in REQUIRED_GATES:
        matches = [key for key in gates if key.startswith(prefix)]
        if len(matches) != 1:
            errors.append(f"expected exactly one gate with prefix {prefix}, got {matches}")
    if gate.get("status") == "BLOCKED" and not gate.get("controlling_blocker"):
        errors.append("BLOCKED gate must name controlling_blocker")
    return errors


def build_report() -> dict[str, Any]:
    errors: list[str] = []
    for required in (STANDARD, REGISTRY_PATH, PROTOCOL_PATH, GATE_PATH):
        if not required.exists():
            errors.append(f"missing required protocol input: {required.relative_to(ROOT)}")

    registry, registry_errors = load_json(REGISTRY_PATH)
    protocol, protocol_errors = load_json(PROTOCOL_PATH)
    gate, gate_errors = load_json(GATE_PATH)
    errors.extend(registry_errors + protocol_errors + gate_errors)
    if registry is not None:
        errors.extend(validate_registry(registry))
    if protocol is not None:
        errors.extend(validate_protocol(protocol))
    if gate is not None:
        errors.extend(validate_gate(gate))

    return {
        "audit": "uet_equation_foundation",
        "audit_status": "PASS" if not errors else "FAIL",
        "foundation_gate_status": gate.get("status") if gate else "UNKNOWN",
        "controlling_blocker": gate.get("controlling_blocker") if gate else "missing_gate",
        "registry_entry_count": len(registry.get("entries", [])) if registry else 0,
        "errors": errors,
        "inputs": {
            "standard": str(STANDARD.relative_to(ROOT)),
            "registry": str(REGISTRY_PATH.relative_to(ROOT)),
            "protocol": str(PROTOCOL_PATH.relative_to(ROOT)),
            "gate": str(GATE_PATH.relative_to(ROOT)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    args = parser.parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"foundation_gate_status={report['foundation_gate_status']}")
        print(f"controlling_blocker={report['controlling_blocker']}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
