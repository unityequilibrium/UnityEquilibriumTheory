"""Build the cross-topic gate for the matter-space research program.

This audit summarizes already-generated core and pilot evidence.  It does not
rerun the simulations, promote a topic, or turn normalized diagnostics into
external validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPO_ROOT / "docs" / "core" / "artifacts" / "matter_space_research_program_gate.json"

INPUT_PATHS = {
    "ontology_contract": REPO_ROOT / "docs/core/07_artifacts/correspondence/matter_space_ontology_contract.json",
    "formula_audit": REPO_ROOT / "docs/core/07_artifacts/correspondence/matter_space_formula_audit.json",
    "alignment_gate": REPO_ROOT / "docs/core/07_artifacts/gates/master_equation_alignment_gate_v2.json",
    "core_verification": REPO_ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json",
    "core_dependency_gate": REPO_ROOT / "docs/core/07_artifacts/gates/matter_space_dependency_gate.json",
    "thermal_pilot": REPO_ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json",
    "thermal_source_package": REPO_ROOT
    / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json",
    "phase_pilot": REPO_ROOT
    / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_matter_space_coupled_diagnostic.json",
    "phase_topic_status": REPO_ROOT
    / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_closure_status_audit.json",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _generated_at(inputs: Iterable[dict[str, Any]]) -> str:
    candidates: list[str] = []
    for payload in inputs:
        value = payload.get("generated_at") or payload.get("audit_date")
        if isinstance(value, str) and value:
            candidates.append(value)
    return max(candidates) if candidates else "SOURCE_TIMESTAMP_UNAVAILABLE"


def _status(payload: dict[str, Any]) -> str:
    return str(payload.get("status", "UNSPECIFIED"))


def _input_record(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": _relative(path),
        "sha256": _sha256(path),
        "status": _status(payload),
    }
    if payload.get("controlling_blocker") is not None:
        record["controlling_blocker"] = payload["controlling_blocker"]
    return record


def _output_records(payload: dict[str, Any]) -> list[dict[str, str]]:
    outputs = payload.get("outputs", {})
    records: list[dict[str, str]] = []
    for value in outputs.values():
        candidates = value if isinstance(value, list) else [value]
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            path = candidate.get("path")
            sha256 = candidate.get("sha256")
            if isinstance(path, str) and isinstance(sha256, str):
                records.append({"path": path, "expected_sha256": sha256})
    return records


def _artifact_integrity(
    core: dict[str, Any], thermal: dict[str, Any], phase: dict[str, Any]
) -> dict[str, Any]:
    records = _output_records(thermal) + _output_records(phase)
    checks: list[dict[str, Any]] = []
    for record in records:
        path = REPO_ROOT / record["path"]
        exists = path.is_file()
        actual = _sha256(path) if exists else None
        checks.append(
            {
                **record,
                "exists": exists,
                "actual_sha256": actual,
                "match": exists and actual == record["expected_sha256"],
            }
        )

    linked_checks = [
        {
            "consumer": "thermal_pilot",
            "path": thermal["core_dependency"]["path"],
            "expected_sha256": thermal["core_dependency"]["sha256"],
        },
        {
            "consumer": "phase_pilot",
            "path": phase["dependencies"]["matter_space_core"]["path"],
            "expected_sha256": phase["dependencies"]["matter_space_core"]["sha256"],
        },
        {
            "consumer": "phase_pilot",
            "path": phase["dependencies"]["topic_closure_status"]["path"],
            "expected_sha256": phase["dependencies"]["topic_closure_status"]["sha256"],
        },
    ]
    for check in linked_checks:
        path = REPO_ROOT / check["path"]
        exists = path.is_file()
        actual = _sha256(path) if exists else None
        check.update(
            {
                "exists": exists,
                "actual_sha256": actual,
                "match": exists and actual == check["expected_sha256"],
            }
        )

    all_checks = checks + linked_checks
    return {
        "status": "PASS" if all(item["match"] for item in all_checks) else "FAIL",
        "checked_output_count": len(checks),
        "checked_dependency_count": len(linked_checks),
        "checks": all_checks,
        "core_artifact_status": core["status"],
    }


def build_program_gate(*, generated_at: str | None = None) -> dict[str, Any]:
    inputs = {name: _read_json(path) for name, path in INPUT_PATHS.items()}
    ontology = inputs["ontology_contract"]
    alignment = inputs["alignment_gate"]
    core = inputs["core_verification"]
    thermal = inputs["thermal_pilot"]
    source_package = inputs["thermal_source_package"]
    phase = inputs["phase_pilot"]
    phase_status = inputs["phase_topic_status"]

    core_gates = core["metrics"]
    core_passed = sum(metric["gate"] == "PASS" for metric in core_gates.values())
    core_total = len(core_gates)
    no_backreaction = all(
        [
            ontology["ontology"]["R"]["independent_state"] is False,
            ontology["ontology"]["R"]["feeds_back_into_dynamics"] is False,
            core_gates["trace_switch_invariance"]["gate"] == "PASS",
            core_gates["trace_history_no_backreaction"]["gate"] == "PASS",
            phase["gates"]["trace_switch_invariance"],
            phase["gates"]["different_trace_history_invariance"],
        ]
    )
    internal_closure = all(
        core_gates[name]["gate"] == "PASS"
        for name in (
            "local_derivative",
            "directional_derivative_periodic",
            "directional_derivative_zero_flux",
            "conserved_matter_drift",
            "minimum_dissipation_density",
            "closed_energy_increase",
            "ledger_closure",
            "open_space_ledger_closure",
            "temporal_convergence",
            "spatial_convergence",
            "adiabatic_local_equilibrium",
        )
    )
    ledger_refined = (
        phase["gates"]["ledger_closure_refined"]
        and thermal["gates"]["ledger_closure_refined"]
    )
    disclosed_amendments = (
        phase["numerical_amendment"]["blind_preregistration"] is False
        and thermal["numerical_amendment"]["blind_preregistration"] is False
        and phase["numerical_amendment"]["physical_parameters_changed"] is False
        and thermal["numerical_amendment"]["physical_parameters_changed"] is False
        and phase["numerical_amendment"]["thresholds_changed"] is False
        and thermal["numerical_amendment"]["thresholds_changed"] is False
    )
    causal_gate = core_gates["prearrival_leakage"]
    artifact_integrity = _artifact_integrity(core, thermal, phase)

    figure_paths = [
        item["path"]
        for payload in (thermal, phase)
        for item in payload.get("outputs", {}).get("figures", [])
    ]
    legacy_figure_paths = [path for path in figure_paths if "/Result/03_show_Result/" in path]
    artifact_layout_status = "WARN" if legacy_figure_paths else "PASS"

    causal_failed = causal_gate["gate"] != "PASS"
    source_blocked = source_package.get("status") == "BLOCKED"
    status = "BLOCKED" if causal_failed or source_blocked else "WARN"

    return {
        "schema_version": "1.0",
        "artifact": "matter_space_research_program_gate",
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "source_snapshot_at": _generated_at(inputs.values()),
        "status": status,
        "program_state": "CANDIDATE_WITH_BLOCKED_PHYSICAL_INTERPRETATION",
        "controlling_blocker": "core_prearrival_leakage",
        "claim_ceiling": "candidate normalized effective model",
        "input_artifacts": {
            name: _input_record(INPUT_PATHS[name], payload)
            for name, payload in inputs.items()
        },
        "summary": {
            "core_gates_passed": core_passed,
            "core_gates_total": core_total,
            "core_status": core["status"],
            "thermal_status": thermal["status"],
            "thermal_internal_gate_status": thermal["internal_gate_status"],
            "thermal_dependency_status": thermal["dependency_status"],
            "phase_status": phase["status"],
            "phase_internal_gate_status": phase["internal_gate_status"],
            "phase_dependency_status": phase["dependency_status"],
            "phase_topic_status_impact": phase["topic_status_impact"],
            "phase_topic_readiness": phase_status["current_readiness"],
            "phase_topic_tier": phase_status["current_tier"],
            "phase_topic_controller": phase_status["controlling_blocker"],
        },
        "gates": {
            "ontology_separation": {
                "status": "PASS" if ontology["status"] == "PASS" and no_backreaction else "FAIL",
                "evidence": "C, Phi, and Pi are physical state; R is derived and has no feedback edge.",
            },
            "internal_variational_and_ledger_closure": {
                "status": "PASS" if internal_closure else "FAIL",
                "evidence": "Functional derivatives, conservation, dissipation sign, energy descent, ledgers, convergence, and the three-scale adiabatic limit pass in the normalized core verifier.",
            },
            "causal_compact_support": {
                "status": causal_gate["gate"],
                "value": causal_gate["value"],
                "threshold": causal_gate["threshold"],
                "comparator": causal_gate["comparator"],
                "arrival_speed_relative_error": core_gates["causal_arrival_speed"]["value"],
                "arrival_speed_threshold": core_gates["causal_arrival_speed"]["threshold"],
            },
            "trace_no_backreaction": {
                "status": "PASS" if no_backreaction else "FAIL",
                "core_trace_history_physical_difference": core_gates[
                    "trace_history_no_backreaction"
                ]["value"],
                "phase_trace_history_physical_difference": phase["metrics"][
                    "different_trace_history_physical_difference"
                ],
            },
            "pilot_energy_ledgers": {
                "status": "WARN" if ledger_refined and disclosed_amendments else "FAIL",
                "evidence_state": "PASS_WITH_DISCLOSED_POST_DIAGNOSTIC_NUMERICAL_AMENDMENTS",
                "locked_runs_passed": False,
                "refined_runs_passed": ledger_refined,
                "blind_preregistration": False,
                "physical_parameters_changed": False,
                "thresholds_changed": False,
            },
            "thermal_control": {
                "status": thermal["internal_gate_status"],
                "claim_class": thermal["status"],
                "dependency_status": thermal["dependency_status"],
                "failed_gates": thermal["failed_gates"],
                "external_source_package_status": source_package.get("status", "UNSPECIFIED"),
            },
            "phase_transition_diagnostic": {
                "status": phase["internal_gate_status"],
                "claim_class": phase["status"],
                "dependency_status": phase["dependency_status"],
                "topic_status_impact": phase["topic_status_impact"],
                "topic_controller_unchanged": phase["topic_controlling_blocker_unchanged"],
            },
            "SI_units": {
                "status": "BLOCKED",
                "reason": "No lane-specific observable map, dimensional coefficients, or SI ledger contract exists in v1.",
            },
            "external_validation": {
                "status": "BLOCKED",
                "reason": "The thermal source package is metadata-only and no Phi-to-observable map with units and extraction uncertainty exists.",
            },
            "artifact_integrity": artifact_integrity,
            "artifact_layout": {
                "status": artifact_layout_status,
                "legacy_figure_count": len(legacy_figure_paths),
                "legacy_figure_paths": legacy_figure_paths,
                "required_canonical_location": "Result/02_Figures",
                "impact": "layout warning only; JSON evidence and recorded hashes remain the controlling evidence",
            },
        },
        "downstream_dependency_gates": {
            "0.10_Fluid_Dynamics_Chaos": {
                "status": "BLOCKED",
                "next_requirement": "constitutive stress and history-dependent viscosity mapping",
            },
            "0.12_Vacuum_Energy_Casimir": {
                "status": "BLOCKED",
                "next_requirement": "ordered-space boundary interpretation without identifying Phi with vacuum substance",
            },
            "0.19_Gravity_GR": {
                "status": "BLOCKED",
                "next_requirement": "geometry and Lorentz-covariant bridge",
            },
            "0.23_Unity_Scale_Link": {
                "status": "BLOCKED",
                "next_requirement": "SI units and cross-scale parameter policy",
            },
            "0.1_Galaxy_Rotation_Problem": {
                "status": "BLOCKED",
                "next_requirement": "full curves, uncertainties, baryonic and instantaneous baselines, history policy, locked parameters, and holdout",
            },
            "0.26_Cosmic_Dynamic_Frame": {
                "status": "BLOCKED",
                "next_requirement": "passing core causality plus 0.1 evidence and a causal-memory parameter policy",
            },
        },
        "deferred_foundation": {
            "topics": [
                "0.5_Nuclear_Binding_Hadrons",
                "0.6_Electroweak_Physics",
                "0.7_Neutrino_Physics",
                "0.9_Quantum_Nonlocality",
                "0.17_Mass_Generation",
                "0.20_Atomic_Physics",
            ],
            "entry_requirements": [
                "Lorentz-covariant action",
                "spinor representation",
                "conserved current",
                "CPT gates",
            ],
            "claim_state": "NOT_ESTABLISHED_DEFERRED",
        },
        "falsification_state": {
            "causal_response_outside_declared_cone": "TRIGGERED_FOR_CURRENT_DISCRETIZATION",
            "coupling_indistinguishable_from_numerical_error": "NOT_TRIGGERED_IN_0.11_PILOT",
            "energy_ledger_cannot_close": "NOT_TRIGGERED_AFTER_DISCLOSED_DT_REFINEMENT",
            "trace_feedback_required": "NOT_TRIGGERED",
            "new_mass_or_energy_identity_required": "NOT_TRIGGERED",
            "single_dataset_fit_required": "NOT_TESTED_EXTERNAL_DATA_ABSENT",
            "interpretation": "The current physical spacetime-response interpretation is blocked; this does not by itself reject the entire effective ontology or variational model.",
        },
        "claim_boundary": {
            "allowed": [
                "matter-space equation as a candidate normalized effective model",
                "Phi as an effective space-response variable",
                "R as a derived causal observable with no backreaction",
                "0.13 as synthetic control / simulation-only",
                "0.11 as internal diagnostic",
                "space subsystem openness as a constitutive ansatz",
            ],
            "blocked": [
                "universe globally proven to be an open system",
                "Phi established as spacetime geometry, ether, metric tensor, antimatter, or particle",
                "R established as matter, energy, or an independent information field",
                "external thermodynamic validation",
                "Dirac, positron, neutrino, or CPT derivation",
                "galaxy dynamics or dark-matter replacement",
            ],
        },
        "next_controller": "repair or replace the physical-response discretization so pre-arrival leakage is <= 1e-6 without clipping or cone padding",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true", help="return nonzero while the program gate is blocked")
    args = parser.parse_args()
    artifact = build_program_gate()
    write_json(OUTPUT_PATH, artifact)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "status": artifact["status"],
                    "controlling_blocker": artifact["controlling_blocker"],
                    "core_gates": [
                        artifact["summary"]["core_gates_passed"],
                        artifact["summary"]["core_gates_total"],
                    ],
                    "thermal": artifact["summary"]["thermal_status"],
                    "phase": artifact["summary"]["phase_status"],
                    "artifact_integrity": artifact["gates"]["artifact_integrity"]["status"],
                    "artifact_layout": artifact["gates"]["artifact_layout"]["status"],
                },
                indent=2,
            )
        )
    return 2 if args.strict and artifact["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
