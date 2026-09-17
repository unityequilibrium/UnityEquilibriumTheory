"""Build the Wave 0 inventory/dependency packet for main-theory closure.

This audit is status-only. It joins canonical artifacts, checks JSON-key
hygiene, and records the dependency order without promoting physics claims.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import (  # noqa: E402
    CANONICAL_ARTIFACT_ROOT,
    canonical_artifact_path,
)

ARTIFACTS = CANONICAL_ARTIFACT_ROOT

REQUIRED_INPUTS = (
    "uet_foundation_equation_inventory.json",
    "uet_equation_correspondence_registry.json",
    "uet_foundation_dependency_gate.json",
    "uet_foundation_compatibility_decision.json",
    "covariant_action_formula_audit.json",
    "covariant_bianchi_exchange_verification.json",
    "o2_finite_density_eos_verification.json",
    "matter_space_research_program_gate.json",
    "uet_impact_effect_information_flow_contract.json",
    "resource_persistence_principle_contract.json",
)

WAVES = (
    ("W0", "foundation_inventory_and_metadata", ()),
    ("W1", "minimal_postulates_and_ontology", ("W0",)),
    ("W2", "covariant_conservative_parent", ("W1",)),
    ("W3", "lane_specific_coarse_graining", ("W2",)),
    ("W4", "open_system_sk_kms_memory", ("W2", "W3")),
    ("W5", "hyperbolic_curved_3p1", ("W2", "W4")),
    ("W6", "operational_quantum_measurement", ("W1",)),
    ("W7", "quantum_interpretation_comparison", ("W6",)),
    ("W8", "dimensional_observable_closure", ("W3", "W4", "W5")),
    ("W9", "gr_gravity_correspondence", ("W5", "W8")),
    ("W10", "fundamental_unification_hypothesis", ("W2", "W6")),
    ("W11", "external_evidence_unlock", ("W8", "W9")),
    ("W12", "final_closure_audit", tuple(f"W{i}" for i in range(12))),
)

# These are distinct mathematical symbols that intentionally differ only by
# case inside variable-definition maps (metric g versus Einstein tensor G,
# and physical current j versus normalized current J).  The scientific-link
# audit reports them for human review; Wave 0's JSON-schema hygiene check must
# not treat them as duplicate object keys.
CASE_SENSITIVE_SYMBOL_PAIRS = {
    frozenset({"g_munu", "G_munu"}),
    frozenset({"j", "J"}),
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_with_case_audit(path: Path) -> tuple[Any, list[dict[str, str]]]:
    duplicates: list[dict[str, str]] = []

    def hook(items: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: dict[str, str] = {}
        result: dict[str, Any] = {}
        for key, value in items:
            folded = key.casefold()
            if folded in seen:
                pair = frozenset({seen[folded], key})
                if pair not in CASE_SENSITIVE_SYMBOL_PAIRS:
                    duplicates.append(
                        {"path": _rel(path), "first": seen[folded], "second": key}
                    )
            seen[folded] = key
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=hook), duplicates


def _artifact_status(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "UNCLASSIFIED"
    for key in ("status", "overall_status", "compatibility_status", "audit_status"):
        value = payload.get(key)
        if value is not None:
            return str(value)
    return "UNCLASSIFIED"


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    missing: list[str] = []
    parse_errors: list[dict[str, str]] = []
    duplicate_keys: list[dict[str, str]] = []
    inputs: list[dict[str, str]] = []

    for name in REQUIRED_INPUTS:
        path = canonical_artifact_path(name)
        if not path.exists():
            missing.append(_rel(path))
            continue
        try:
            payload, duplicates = _load_with_case_audit(path)
        except (OSError, json.JSONDecodeError) as exc:
            parse_errors.append({"path": _rel(path), "error": str(exc)})
            continue
        duplicate_keys.extend(duplicates)
        inputs.append(
            {
                "path": _rel(path),
                "sha256": _sha256(path),
                "reported_status": _artifact_status(payload),
            }
        )

    duplicate_keys = list(
        {
            (item["path"], item["first"], item["second"]): item
            for item in duplicate_keys
        }.values()
    )

    nodes = [
        {
            "wave_id": wave_id,
            "name": name,
            "depends_on": list(dependencies),
            "track": "secondary_hypothesis" if wave_id == "W10" else "primary_effective",
            "initial_status": "PASS_ACCOUNTING_ONLY" if wave_id == "W0" else "BLOCKED",
        }
        for wave_id, name, dependencies in WAVES
    ]
    edges = [
        {"from": dependency, "to": wave_id, "type": "required_dependency"}
        for wave_id, _, dependencies in WAVES
        for dependency in dependencies
    ]
    graph = {
        "schema_version": "1.0",
        "artifact": "uet_main_theory_dependency_graph",
        "generated_at": date.today().isoformat(),
        "program_tracks": {
            "primary": "covariant_effective_theory",
            "secondary": "fundamental_unification_hypothesis_track",
        },
        "nodes": nodes,
        "edges": edges,
        "claim_rule": "A downstream PASS cannot override a blocked required dependency.",
    }

    hygiene_pass = not missing and not parse_errors and not duplicate_keys
    gate = {
        "schema_version": "1.0",
        "artifact": "uet_main_theory_wave0_gate",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS" if hygiene_pass else "FAIL",
        "research_status": (
            "ACCOUNTING_CLOSED_PHYSICS_NOT_PROMOTED" if hygiene_pass else "BLOCKED"
        ),
        "controlling_blocker": (
            "main_axioms_and_parent_action_not_unified"
            if hygiene_pass
            else "foundation_input_or_json_schema_hygiene_incomplete"
        ),
        "checks": {
            "required_inputs_present": not missing,
            "json_parseable": not parse_errors,
            "case_insensitive_duplicate_keys_absent": not duplicate_keys,
            "dependency_graph_complete": len(nodes) == 13 and bool(edges),
        },
        "inputs": inputs,
        "missing_inputs": missing,
        "parse_errors": parse_errors,
        "case_insensitive_duplicate_keys": duplicate_keys,
        "historical_intent_policy": {
            "original_notes": "source material, not current proof",
            "current_contracts": "controlling ontology and claim boundary",
            "rejected_or_legacy_interpretations": "preserved without promotion",
        },
        "claim_impact": "NO_PHYSICAL_PROMOTION",
        "next_controller": "define minimal postulates and one parent-theory ontology gate",
    }
    return graph, gate


def main() -> int:
    graph, gate = build()
    outputs = {
        "uet_main_theory_dependency_graph.json": graph,
        "uet_main_theory_wave0_gate.json": gate,
    }
    for name, payload in outputs.items():
        path = canonical_artifact_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(f"audit_status={gate['audit_status']}")
    print(f"controlling_blocker={gate['controlling_blocker']}")
    print(f"duplicate_key_count={len(gate['case_insensitive_duplicate_keys'])}")
    return 0 if gate["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
