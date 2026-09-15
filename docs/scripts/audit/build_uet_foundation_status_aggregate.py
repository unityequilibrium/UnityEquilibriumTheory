"""Build the current UET foundation status aggregate and stopping criteria."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/gates/uet_foundation_status_aggregate.json"

INPUTS = {
    "foundation_gate": ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json",
    "compatibility": ROOT / "docs/core/07_artifacts/gates/uet_foundation_compatibility_gate.json",
    "topic_inventory": ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json",
    "code_inventory": ROOT / "docs/core/07_artifacts/archive/uet_code_surface_inventory.json",
    "coverage_closure": ROOT / "docs/core/07_artifacts/gates/uet_foundation_coverage_closure.json",
    "full_correspondence": ROOT / "docs/core/07_artifacts/correspondence/uet_full_correspondence_coverage.json",
    "family_contract": ROOT / "docs/core/07_artifacts/archive/uet_core_equation_family_contract.json",
    "correspondence_matrix": ROOT / "docs/core/07_artifacts/gates/uet_foundation_correspondence_matrix.json",
    "matter_space": ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
    "gr_closed_limit": ROOT / "docs/core/07_artifacts/verification/gr_closed_limit_verification.json",
    "o2_eos": ROOT / "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json",
    "trace": ROOT / "docs/core/07_artifacts/verification/spacetime_trace_verification.json",
    "legacy_variational": ROOT / "docs/core/07_artifacts/gates/uet_legacy_variational_closure.json",
    "causal_discretization": ROOT / "docs/core/07_artifacts/archive/matter_space_causal_discretization_diagnostic.json",
    "causal_reference": ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json",
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"not an object: {path}")
    return value


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_aggregate() -> dict[str, Any]:
    missing = [rel(path) for path in INPUTS.values() if not path.exists()]
    if missing:
        raise ValueError(f"missing aggregate inputs: {missing}")
    data = {key: load(path) for key, path in INPUTS.items()}

    compatibility = data["compatibility"]
    topic_inventory = data["topic_inventory"]
    code_inventory = data["code_inventory"]
    coverage_closure = data["coverage_closure"]
    full_correspondence = data["full_correspondence"]
    family_contract = data["family_contract"]
    matrix = data["correspondence_matrix"]
    matter = data["matter_space"]
    gr = data["gr_closed_limit"]
    o2 = data["o2_eos"]
    trace = data["trace"]
    legacy_variational = data["legacy_variational"]
    causal_discretization = data["causal_discretization"]
    causal_reference = data["causal_reference"]

    gates = [
        {
            "id": "F0",
            "name": "inventory",
            "status": "PASS_CONDITIONAL" if coverage_closure.get("coverage_gate_status") == "PASS_WITH_EXPLICIT_QUARANTINES" else "BLOCKED",
            "status_detail": "PASS_CONDITIONAL_WITH_EXPLICIT_QUARANTINES" if coverage_closure.get("coverage_gate_status") == "PASS_WITH_EXPLICIT_QUARANTINES" else "BLOCKED",
            "evidence": ["topic_inventory", "code_inventory", "coverage_closure"],
            "controller": "all discovered surfaces are assigned or quarantined; open correspondence/units/observable gates remain separate",
        },
        {
            "id": "F1",
            "name": "ontology",
            "status": "PASS_CONDITIONAL" if family_contract.get("coverage", {}).get("missing_core_paths") == [] else "BLOCKED",
            "evidence": ["family_contract", "compatibility"],
            "controller": "lane-specific C mappings exist; universal physical identity remains disallowed",
        },
        {
            "id": "F2",
            "name": "standard_physics_correspondence",
            "status": "BLOCKED" if full_correspondence.get("matrix_status") == "BLOCKED_OPEN_CORRESPONDENCE_ROWS" else ("BLOCKED" if matrix.get("matrix_status") == "BLOCKED" else "PASS_CONDITIONAL"),
            "status_detail": "BLOCKED_OPEN_CORRESPONDENCE_ROWS" if full_correspondence.get("matrix_status") == "BLOCKED_OPEN_CORRESPONDENCE_ROWS" else ("BLOCKED" if matrix.get("matrix_status") == "BLOCKED" else "PASS_CONDITIONAL"),
            "evidence": ["correspondence_matrix", "full_correspondence"],
            "controller": "all inventoried rows are recorded; open standard-counterpart and UET candidate mappings remain",
        },
        {
            "id": "F3",
            "name": "units",
            "status": "BLOCKED",
            "evidence": ["family_contract", "compatibility"],
            "controller": "normalized/natural/SI lanes remain mixed across families; the scoped beta/Landauer contract is separated",
        },
        {
            "id": "F4",
            "name": "derivation",
            "status": "BLOCKED" if compatibility.get("controlling_blockers") else "PASS_CONDITIONAL",
            "evidence": ["compatibility", "family_contract"],
            "controller": "open heuristic bridges and family-specific correspondence remain",
        },
        {
            "id": "F5",
            "name": "formal_verification",
            "status": "BLOCKED" if legacy_variational.get("closure_status") == "BLOCKED" or "legacy_potential_derivative_pair" in compatibility.get("controlling_blockers", []) else "PASS_CONDITIONAL",
            "evidence": ["compatibility", "matter_space", "legacy_variational"],
            "controller": "canonical potential/source closure passes conditionally; legacy_local comparator remains quarantined",
        },
        {
            "id": "F6",
            "name": "numerical_verification",
            "status": "BLOCKED" if matter.get("status") == "FAIL" else "PASS_CONDITIONAL",
            "evidence": ["matter_space", "code_inventory", "causal_discretization", "causal_reference"],
            "controller": causal_discretization.get("classification", matter.get("controlling_blocker", "causal and code-surface checks")) + "; strict-CFL frozen-C reference lane=" + causal_reference.get("reference_status", "UNKNOWN") + "; full candidate remains blocked",
        },
        {
            "id": "F7",
            "name": "observable_mapping",
            "status": "BLOCKED",
            "evidence": ["family_contract", "compatibility"],
            "controller": "measurement operator, SI map, uncertainty and resolution are not closed for core families",
        },
        {
            "id": "F8",
            "name": "data_and_claim",
            "status": "BLOCKED",
            "evidence": ["foundation_gate", "correspondence_matrix"],
            "controller": "upstream foundation status blocks real-data promotion",
        },
    ]

    status_counts: dict[str, int] = {}
    for gate in gates:
        status_counts[gate["status"]] = status_counts.get(gate["status"], 0) + 1

    conditional_limits = [
        {
            "theory": "Einstein/GR",
            "status": "COMPATIBLE_CONDITIONAL",
            "what_is_verified": "algebraic/local closed-limit evaluator at epsilon_nc=0 and ordered reference",
            "what_is_not_verified": "full Einstein field equations, Bianchi identity, metric PDE, physical GR validation",
            "evidence": rel(INPUTS["gr_closed_limit"]),
        },
        {
            "theory": "relativistic O(2) EOS",
            "status": "COMPATIBLE_CONDITIONAL",
            "what_is_verified": "tree-level natural-unit finite-density EOS and ideal T=0 constitutive sector",
            "what_is_not_verified": "universal C ontology, full finite-temperature transport, SI and external physical validation",
            "evidence": rel(INPUTS["o2_eos"]),
        },
        {
            "theory": "Cahn-Hilliard/Markovian comparator",
            "status": "COMPATIBLE_CONDITIONAL",
            "what_is_verified": "selected normalized/internal relation and decoupled/adiabatic diagnostics",
            "what_is_not_verified": "material-unit derivation, causal matter-space response and universal phase-transition claim",
            "evidence": rel(INPUTS["matter_space"]),
        },
        {
            "theory": "trace/Markovian memory limit",
            "status": "COMPATIBLE_CONDITIONAL",
            "what_is_verified": "derived trace-only comparator tests and no-backreaction contract",
            "what_is_not_verified": "dimensional direct observable and any physical backreaction law",
            "evidence": rel(INPUTS["trace"]),
        },
    ]

    principles = [
        "State variables, response variables, and derived traces must remain separate.",
        "A dynamics force must be the derivative of its declared functional before it is called variational.",
        "Every coupled state equation must use the same functional sign convention; matching only one field equation is insufficient.",
        "C has no universal physical identity; mass, density, charge and order parameter require lane-specific mappings.",
        "Open-system language applies to an explicit effective subsystem balance, not automatically to the whole universe.",
        "A standard theory is a special case only after an explicit limit, same ontology/units, and residual verification.",
        "Free-energy descent, physical energy conservation, entropy production and open exchange are separate ledgers.",
        "No real-data claim is allowed before an observable operator and uncertainty/provenance contract exist.",
    ]

    stopping_criteria = [
        "No unresolved CONTRADICTION or CONFLICT remains in the declared core equation families.",
        "F0 inventory is code-complete for core and topic dependencies, or every exclusion is explicitly quarantined.",
        "F1-F3 ontology, standard counterpart and units are closed for each family used in a claim.",
        "Every special-case claim has an explicit limit and residual/ convergence artifact.",
        "F5-F6 formal and numerical gates pass without hidden clipping, fitting or fallback.",
        "F7 measurement operator maps the family to a measured observable with units and uncertainty.",
        "F8 holdout/external comparison is completed before promotion of a physical claim.",
    ]

    legacy_blockers = legacy_variational.get("controlling_blockers", [])
    controlling_blockers = list(dict.fromkeys(compatibility.get("controlling_blockers", []) + legacy_blockers + [
        "open_correspondence_rows_and_lane_mappings",
        "active_lane_units_and_observable_contracts_remain_open",
        "prearrival_leakage",
    ]))

    return {
        "schema_version": "1.0",
        "artifact": "uet_foundation_status_aggregate",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "foundation_status": "BLOCKED",
        "controlling_blockers": controlling_blockers,
        "gate_summary": {"status_counts": status_counts, "gates": gates},
        "known_conflicts": [
            "legacy_local reaction is a quarantined non-variational comparator",
            "canonical normalized C/I operator and beta semantics are conditionally closed in legacy_variational_v1",
            "matter-space causal response fails its pre-arrival leakage threshold",
            "current Heun/RK2 discrete domain-of-dependence is wider than the declared physical cone",
            "O2-to-legacy-double-well reduction fails its residual gate",
        ],
        "conditional_special_cases": conditional_limits,
        "principles": principles,
        "stopping_criteria": stopping_criteria,
        "evidence_inputs": {key: rel(path) for key, path in INPUTS.items()},
        "next_controller": "F1-F7: close open active-lane correspondence, units and observable rows before any new downstream physical claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        aggregate = build_aggregate()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(aggregate, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={aggregate['audit_status']}")
        print(f"foundation_status={aggregate['foundation_status']}")
        print(f"controlling_blocker_count={len(aggregate['controlling_blockers'])}")
        print(f"gate_status_counts={aggregate['gate_summary']['status_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
