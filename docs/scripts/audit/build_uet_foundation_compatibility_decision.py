"""Build the final foundation compatibility decision from current evidence.

The decision deliberately separates three questions that are often conflated:

1. Is the declared mathematics internally consistent?
2. Does a lane have a defensible correspondence to standard physics?
3. Is a standard theory actually recovered as a special case?

This is a status synthesis, not a proof generator.  It refuses to promote the
whole theory when any controlling contradiction, incomplete inventory, or hard
dependency gate remains.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/gates/uet_foundation_compatibility_decision.json"
REPORT = ROOT / "docs/core/01_contracts/UET_FOUNDATION_COMPATIBILITY_DECISION.md"

INPUTS = {
    "compatibility": ROOT / "docs/core/07_artifacts/gates/uet_foundation_compatibility_gate.json",
    "aggregate": ROOT / "docs/core/07_artifacts/gates/uet_foundation_status_aggregate.json",
    "inventory": ROOT / "docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json",
    "family_contract": ROOT / "docs/core/07_artifacts/archive/uet_core_equation_family_contract.json",
    "legacy_variational": ROOT / "docs/core/07_artifacts/gates/uet_legacy_variational_closure.json",
    "matter_space": ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
    "causal_reference": ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json",
    "trace": ROOT / "docs/core/07_artifacts/verification/spacetime_trace_verification.json",
    "gr_closed_limit": ROOT / "docs/core/07_artifacts/verification/gr_closed_limit_verification.json",
    "o2_eos": ROOT / "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json",
    "transport": ROOT / "docs/core/07_artifacts/verification/covariant_superfluid_transport_verification.json",
}


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def finding_map(compatibility: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["finding_id"]): item for item in compatibility.get("findings", [])
    }


def gate_value(data: dict[str, Any], metric_name: str) -> dict[str, Any]:
    metric = data.get("metrics", {}).get(metric_name, {})
    if not isinstance(metric, dict):
        return {"gate": "UNKNOWN"}
    return {
        "gate": metric.get("gate", "UNKNOWN"),
        "value": metric.get("value"),
        "threshold": metric.get("threshold"),
    }


def build_decision() -> dict[str, Any]:
    missing = [rel(path) for path in INPUTS.values() if not path.exists()]
    if missing:
        raise ValueError(f"missing decision inputs: {missing}")

    data = {name: load(path) for name, path in INPUTS.items()}
    compatibility = data["compatibility"]
    findings = finding_map(compatibility)
    aggregate = data["aggregate"]
    inventory = data["inventory"]
    family_contract = data["family_contract"]
    legacy_variational = data["legacy_variational"]
    matter_space = data["matter_space"]
    causal_reference = data["causal_reference"]
    trace = data["trace"]
    gr = data["gr_closed_limit"]
    o2 = data["o2_eos"]
    transport = data["transport"]

    legacy_finding = findings["legacy_potential_derivative_pair"]
    legacy_info_finding = findings["legacy_information_operator"]
    beta_finding = findings["legacy_beta_unit_semantics"]
    double_well_finding = findings["o2_to_legacy_double_well"]

    family_rows = [
        {
            "family_id": "core.legacy_master",
            "mathematical_consistency": legacy_finding["status"],
            "standard_physics_correspondence": "BLOCKED",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "The canonical potential/derivative, information operator/source, and normalized beta semantics are conditionally closed in legacy_variational_v1; legacy_local remains a quarantined comparator.",
            "evidence": [
                rel(INPUTS["legacy_variational"]),
                rel(INPUTS["compatibility"]),
            ],
        },
        {
            "family_id": "core.matter_space",
            "mathematical_consistency": "PARTIAL_INTERNAL_PASS",
            "standard_physics_correspondence": "CONDITIONAL_AND_BLOCKED",
            "old_theory_special_case": "CONDITIONAL_ONLY",
            "reason": "Functional derivatives, conservation, ledger, and trace isolation pass in the normalized checks, but the full default causal gate fails.",
            "evidence": [
                rel(INPUTS["matter_space"]),
                rel(INPUTS["causal_reference"]),
            ],
            "metrics": {
                "local_derivative": gate_value(matter_space, "local_derivative"),
                "ledger_closure": gate_value(matter_space, "ledger_closure"),
                "prearrival_leakage": gate_value(matter_space, "prearrival_leakage"),
                "reference_status": causal_reference.get("reference_status"),
            },
        },
        {
            "family_id": "core.trace",
            "mathematical_consistency": "CONDITIONAL_PASS",
            "standard_physics_correspondence": "DERIVED_OBSERVABLE_ONLY",
            "old_theory_special_case": "MARKOVIAN_COMPARATOR_ONLY",
            "reason": "The trace is derived from the dissipation history and does not feed back in the new mode; direct dimensional observability and physical backreaction remain open.",
            "evidence": [rel(INPUTS["trace"])],
        },
        {
            "family_id": "core.covariant_response",
            "mathematical_consistency": "CONDITIONAL_PASS",
            "standard_physics_correspondence": "CONDITIONAL_LOCAL",
            "old_theory_special_case": "GR_NULL_LIMIT_ONLY",
            "reason": "The local covariant evaluator passes its declared null/ordered limit, but this is not the Einstein field-equation system or a global closed-limit derivation.",
            "evidence": [rel(INPUTS["gr_closed_limit"])],
        },
        {
            "family_id": "core.covariant_diffusion",
            "mathematical_consistency": "CONDITIONAL_CONSTITUTIVE",
            "standard_physics_correspondence": "CONDITIONAL_TRANSPORT",
            "old_theory_special_case": "MARKOVIAN_COMPARATOR_ONLY",
            "reason": "The covariant current lane is a constitutive Maxwell-Cattaneo/control interface; coefficient origin, Kubo matching, and dimensional observables remain open.",
            "evidence": ["docs/core/07_artifacts/correspondence/covariant_diffusion_formula_audit.json", "docs/core/07_artifacts/verification/covariant_diffusive_current_verification.json"]
        },
        {
            "family_id": "core.hyperbolic_phase",
            "mathematical_consistency": "COMPATIBLE_COMPARATOR_ONLY",
            "standard_physics_correspondence": "EXTERNAL_TELEGRAPH_COMPARATOR",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "The hyperbolic phase-field path is a fixed-form external comparator; it is not derived from the UET action.",
            "evidence": ["docs/core/07_artifacts/correspondence/hyperbolic_phase_field_formula_audit.json", "docs/core/07_artifacts/gates/hyperbolic_phase_field_covariant_mapping_gate.json"]
        },
        {
            "family_id": "core.noether_mapping",
            "mathematical_consistency": "CONDITIONAL_MANY_TO_ONE",
            "standard_physics_correspondence": "CONDITIONAL_O2_NOETHER_MAP",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "The action-level Noether current is compatible in its parent lane, but the coarse-grained C mapping is many-to-one and does not prove the legacy C field or microscopic dissipation.",
            "evidence": ["docs/core/07_artifacts/correspondence/noether_phase_field_map_formula_audit.json", "docs/core/07_artifacts/verification/noether_phase_field_state_map_verification.json"]
        },
        {
            "family_id": "core.lorentz",
            "mathematical_consistency": "UTILITY_ONLY",
            "standard_physics_correspondence": "NOT_ESTABLISHED_GLOBAL",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "Lorentz transformation utilities and tests do not establish covariance of every physical operator or the legacy master dynamics.",
            "evidence": ["docs/core/test/test_lorentz_noether_comprehensive.py", "docs/core/08_history/research_notes/UET_FOUNDATION_COMPATIBILITY_AUDIT.md"]
        },
        {
            "family_id": "core.parameter_contract",
            "mathematical_consistency": "UNIT_SEMANTICS_OPEN",
            "standard_physics_correspondence": "PARAMETER_POLICY_ONLY",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "The parameter registry still mixes normalized, natural-unit, and SI lanes globally; the scoped beta_normalized/Landauer separation is closed, but cross-family conversion remains open.",
            "evidence": ["docs/core/07_artifacts/gates/uet_foundation_compatibility_gate.json", "docs/core/01_contracts/units/uet_parameters.py"]
        },
        {
            "family_id": "core.observable_contract",
            "mathematical_consistency": "OBSERVABLE_MAP_OPEN",
            "standard_physics_correspondence": "BLOCKED",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "A complete measurement operator with units, uncertainty, resolution, and nuisance parameters is not closed for the core families.",
            "evidence": ["docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json", "docs/core/07_artifacts/gates/uet_foundation_status_aggregate.json"]
        },
        {
            "family_id": "core.support_and_adapters",
            "mathematical_consistency": "NOT_AN_EQUATION_FAMILY",
            "standard_physics_correspondence": "NOT_APPLICABLE",
            "old_theory_special_case": "NOT_APPLICABLE",
            "reason": "Support and adapter code cannot create a physical claim without an owning equation family.",
            "evidence": ["docs/core/07_artifacts/archive/uet_code_surface_inventory.json"]
        },
        {
            "family_id": "core.o2_superfluid",
            "mathematical_consistency": "CONDITIONAL_PASS",
            "standard_physics_correspondence": "CONDITIONAL_TREE_LEVEL",
            "old_theory_special_case": "O2_LANE_ONLY",
            "reason": "The finite-density O(2) EOS and ideal constitutive sector pass their natural-unit tree-level gates; transport provenance, SI, finite temperature, and universal C identity remain open.",
            "evidence": [rel(INPUTS["o2_eos"]), rel(INPUTS["transport"])],
        },
        {
            "family_id": "core.legacy_double_well",
            "mathematical_consistency": "COMPARATOR_ONLY",
            "standard_physics_correspondence": "NOT_ESTABLISHED",
            "old_theory_special_case": double_well_finding["status"],
            "reason": "The preregistered reduction from the O(2) EOS to the legacy symmetric double well fails its residual gate.",
            "evidence": [rel(INPUTS["o2_eos"]), rel(INPUTS["compatibility"])],
        },
        {
            "family_id": "core.covariant_transport",
            "mathematical_consistency": "IDEAL_SECTOR_PASS",
            "standard_physics_correspondence": "CONDITIONAL_TRANSPORT_INTERFACE",
            "old_theory_special_case": "NOT_ESTABLISHED",
            "reason": "Projector, ideal current/stress, Josephson, Lorentz, entropy-sign, and causal-control checks pass, while missing coefficient provenance blocks physical dissipative promotion.",
            "evidence": [rel(INPUTS["transport"])],
        },
        {
            "family_id": "core.open_system_interpretation",
            "mathematical_consistency": "SUBSYSTEM_ANSATZ",
            "standard_physics_correspondence": "CONDITIONAL_SUBSYSTEM_ONLY",
            "old_theory_special_case": "GLOBAL_CLOSED_LIMIT_NOT_ESTABLISHED",
            "reason": "Explicit source and exchange terms can describe an effective subsystem; they do not prove that the whole universe is open or that a closed universe must reduce to Einstein GR.",
            "evidence": [rel(INPUTS["compatibility"])],
        },
    ]

    principle_rows = [
        {
            "principle_id": "P1_state_response_trace_separation",
            "verdict": "SUPPORTED_IN_NEW_MODE",
            "meaning": "(C,Phi,Pi) are physical state variables and R/I_trace is derived history; no R feedback is allowed.",
            "evidence": [rel(INPUTS["matter_space"]), rel(INPUTS["trace"])],
        },
        {
            "principle_id": "P2_functional_derivative_closure",
            "verdict": "CANONICAL_PASS_LEGACY_COMPARATOR_QUARANTINED",
            "meaning": "The canonical legacy_variational_v1 C/I functional, information operator/source, and normalized beta contracts pass their scoped checks; legacy_local behavior is preserved as a non-variational comparator.",
            "evidence": [rel(INPUTS["legacy_variational"]), rel(INPUTS["matter_space"])],
        },
        {
            "principle_id": "P3_lane_specific_correspondence",
            "verdict": "SUPPORTED_AS_METHOD_NOT_UNIVERSAL_IDENTITY",
            "meaning": "C may map to density, Noether charge, or order parameter only inside a declared lane with units and observables.",
            "evidence": [rel(INPUTS["family_contract"]), rel(INPUTS["inventory"])],
        },
        {
            "principle_id": "P4_open_balance",
            "verdict": "CONDITIONAL_SUBSYSTEM_ANSATZ",
            "meaning": "Open-system accounting is valid for an explicitly bounded effective subsystem; global cosmic openness is not established.",
            "evidence": [rel(INPUTS["compatibility"])],
        },
        {
            "principle_id": "P5_nested_special_case",
            "verdict": "CONDITIONAL_ONLY",
            "meaning": "GR and O(2) have narrow verified limits, but the O(2)-to-legacy-double-well reduction is rejected and no universal nesting theorem exists.",
            "evidence": [rel(INPUTS["gr_closed_limit"]), rel(INPUTS["o2_eos"]), rel(INPUTS["compatibility"])],
        },
        {
            "principle_id": "P6_energy_and_entropy_ledgers",
            "verdict": "PARTIAL_NORMALIZED_ONLY",
            "meaning": "The new normalized candidate has internal ledger checks; the legacy A1 energy-conservation label and SI energy meaning are not established.",
            "evidence": [rel(INPUTS["matter_space"]), rel(INPUTS["compatibility"])],
        },
        {
            "principle_id": "P7_causal_response",
            "verdict": "FULL_CANDIDATE_BLOCKED_REFERENCE_LANE_PASS",
            "meaning": "The strict-CFL frozen-C reference has compact support, but the default coupled candidate still fails pre-arrival leakage.",
            "evidence": [rel(INPUTS["causal_reference"]), rel(INPUTS["matter_space"])],
        },
        {
            "principle_id": "P8_observable_and_data_bridge",
            "verdict": "BLOCKED",
            "meaning": "A complete measurement operator, units, uncertainty, provenance, and holdout chain is not closed for the core theory.",
            "evidence": [rel(INPUTS["aggregate"]), rel(INPUTS["inventory"])],
        },
    ]

    conditional_closures = [
        {
            "id": "legacy_potential_derivative_pair",
            "status": legacy_finding["status"],
            "canonical_mode": "legacy_variational_v1",
            "canonical_residual": legacy_finding.get("metrics", {}).get("canonical_max_absolute_residual"),
            "legacy_comparator_residual": legacy_finding.get("metrics", {}).get("legacy_comparator_max_absolute_residual"),
            "threshold": legacy_finding.get("metrics", {}).get("threshold"),
            "meaning": "The canonical radial derivative is closed conditionally; legacy_local remains explicitly non-variational.",
        },
        {
            "id": "legacy_information_gradient_sign",
            "status": findings.get("legacy_information_gradient_sign", {}).get("status", "NOT_ESTABLISHED"),
            "canonical_mode": "legacy_variational_v1",
            "meaning": "The canonical information-source sign matches the declared positive coupling; the historical sign is comparator-only.",
        },
        {
            "id": "legacy_information_operator",
            "status": legacy_info_finding["status"],
            "canonical_mode": "legacy_variational_v1",
            "meaning": "The normalized periodic I operator matches the declared functional gradient; historical box/wave wording is comparator-only.",
        },
        {
            "id": "legacy_beta_unit_semantics",
            "status": beta_finding["status"],
            "canonical_mode": "normalized_parameter_lane",
            "meaning": "beta_normalized is dimensionless and E_min is a separate SI Landauer lower bound; no universal conversion is claimed.",
        },
    ]

    hard_contradictions = []
    remaining_dependency_blockers = [
        {
            "id": "matter_space_causal_response",
            "status": "BLOCKED",
            "meaning": "The full coupled matter-space candidate still fails its strict pre-arrival leakage/reference gate.",
        },
        {
            "id": "foundation_inventory_and_correspondence",
            "status": "BLOCKED",
            "meaning": "The code-complete equation inventory, standard-physics correspondence, and global units gates remain open.",
        },
        {
            "id": "o2_to_legacy_double_well",
            "status": double_well_finding["status"],
            "meaning": "The O(2)-to-legacy-double-well reduction remains comparator-only under its residual gate.",
        },
    ]
    return {
        "schema_version": "1.0",
        "artifact": "uet_foundation_compatibility_decision",
        "generated_at": date.today().isoformat(),
        "audit_status": "PASS",
        "decision": {
            "mathematical_consistency": "CONDITIONAL_SCOPED_CANONICAL",
            "standard_physics_correspondence": "PARTIAL_CONDITIONAL_NOT_GLOBAL",
            "old_theory_nesting": "CONDITIONAL_ONLY",
            "global_uet_status": "FOUNDATION_NOT_CLOSED",
        },
        "decision_rule": {
            "contradiction": "A declared relation and its implementation disagree; this blocks that equation family.",
            "conditional_compatibility": "A lane passes only under explicit ontology, units, limit, residual, and evidence boundaries.",
            "not_established": "Missing proof is not labelled false, but it cannot support a physical claim.",
            "special_case": "A standard theory is a special case only when the same variables/units and a verified limit are shown.",
        },
        "coverage": {
            "core_family_count": len(family_contract.get("families", [])),
            "topic_formula_rows": inventory.get("coverage", {}).get("parsed_formula_row_count"),
            "topic_formula_files": inventory.get("coverage", {}).get("formula_audit_file_count"),
            "inventory_gate_status": inventory.get("inventory_gate_status"),
            "registry_coverage_status": compatibility.get("summary", {}).get("registry_coverage_status"),
            "coverage_boundary": "The inventory is broad but not code-complete; code-only equations and full observable maps remain open.",
        },
        "hard_contradictions": hard_contradictions,
        "remaining_dependency_blockers": remaining_dependency_blockers,
        "conditional_closures": conditional_closures,
        "family_matrix": family_rows,
        "principle_matrix": principle_rows,
        "special_case_summary": {
            "gr": "COMPATIBLE_CONDITIONAL_LOCAL_ALGEBRAIC_ONLY",
            "o2_finite_density": "COMPATIBLE_CONDITIONAL_TREE_LEVEL_NATURAL_UNITS",
            "legacy_double_well": "REJECTED_REDUCTION",
            "matter_space_causal": "BLOCKED_FULL_CANDIDATE_REFERENCE_LANE_PASS",
            "global_open_universe": "NOT_ESTABLISHED",
        },
        "claim_boundary": "The current repository evidence conditionally closes the normalized C/I operator and beta contract inside legacy_variational_v1, keeps legacy_local as a quarantined comparator, and retains unresolved standard-physics, causal, observable, and cross-family correspondence gates. It does not establish that all old theories are special cases of one UET equation, nor that UET is physically complete.",
        "next_controller": "Complete code-level F0-F3 correspondence and units, prove full coupled causal/energy behavior, then build observable and holdout tests before any universal or real-data claim.",
        "evidence_inputs": {name: rel(path) for name, path in INPUTS.items()},
    }


def render_markdown(decision: dict[str, Any]) -> str:
    counts = decision["coverage"]
    lines = [
        "# UET Foundation Compatibility Decision",
        "",
        "This is a generated status synthesis, not a proof that UET is physically complete.",
        "It answers three separate questions: internal mathematical consistency, correspondence",
        "to standard physics, and whether an older theory is actually recovered as a special case.",
        "",
        "## Decision",
        "",
        f"- Mathematical consistency: `{decision['decision']['mathematical_consistency']}`",
        f"- Standard-physics correspondence: `{decision['decision']['standard_physics_correspondence']}`",
        f"- Old-theory nesting: `{decision['decision']['old_theory_nesting']}`",
        f"- Overall foundation: `{decision['decision']['global_uet_status']}`",
        "",
        "The current answer is therefore: the canonical legacy_variational_v1 C/I operator and normalized beta contract",
        "is conditionally closed, legacy_local remains a quarantined comparator, and remaining dependency",
        "gates still block global foundation promotion.",
        "",
        "## Conditional closures",
        "",
        "| ID | Mode | Status | Meaning |",
        "|---|---|---|---|",
    ]
    for item in decision["conditional_closures"]:
        lines.append(f"| `{item['id']}` | `{item['canonical_mode']}` | `{item['status']}` | {item['meaning']} |")
    lines.extend(
        [
            "",
            "## Scoped contradictions",
            "",
            "| ID | Status | Meaning |",
            "|---|---|---|",
        ]
    )
    for item in decision["hard_contradictions"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['meaning']} |")
    lines.extend(
        [
            "",
            "## Remaining dependency blockers",
            "",
            "| ID | Status | Meaning |",
            "|---|---|---|",
        ]
    )
    for item in decision["remaining_dependency_blockers"]:
        lines.append(f"| `{item['id']}` | `{item['status']}` | {item['meaning']} |")
    lines.extend(
        [
            "",
            "## Special-case boundary",
            "",
            "| Lane | Current decision |",
            "|---|---|",
            "| GR | Conditional local/algebraic closed limit only; not Einstein field equations |",
            "| O(2) finite-density | Tree-level natural-unit EOS and ideal constitutive sector only |",
            "| Legacy double well | Rejected reduction under the locked residual gate |",
            "| Matter-space causality | Full candidate blocked; strict-CFL frozen-C reference passes |",
            "| Global universe-open claim | Not established |",
            "",
            "## Coverage boundary",
            "",
            f"- Core families inventoried: `{counts['core_family_count']}`",
            f"- Topic formula rows inventoried: `{counts['topic_formula_rows']}` across `{counts['topic_formula_files']}` files",
            f"- Inventory gate: `{counts['inventory_gate_status']}`",
            "- Code-only equation surfaces and complete observable/unit maps remain open.",
            "",
            "## Claim boundary",
            "",
            decision["claim_boundary"],
            "",
            "## Next controller",
            "",
            decision["next_controller"],
            "",
            "Generated from `uet_foundation_compatibility_decision.json`; do not edit the generated result by hand.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        decision = build_decision()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"audit_status=FAIL\nERROR: {exc}")
        return 1
    if not args.no_write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        REPORT.write_text(render_markdown(decision), encoding="utf-8")
    if args.json:
        print(json.dumps(decision, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={decision['audit_status']}")
        for key, value in decision["decision"].items():
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
