"""Build the machine-readable Wave 1 research-room contract.

The contract joins topic artifacts without changing their status. It deliberately
records selected control lanes separately from full candidate lanes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
BRIEF = ROOT / "docs/core/00_governance/UET_RESEARCH_ROOM_BRIEF.md"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def snapshot(path: Path, selectors: tuple[str, ...] = ()) -> dict[str, Any]:
    if not path.is_file():
        return {"path": rel(path), "present": False}
    value = load(path)
    selected = {key: value.get(key) for key in selectors if key in value}
    return {"path": rel(path), "present": True, "sha256": sha256(path), "summary": selected}


def main() -> int:
    registry_path = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json"
    foundation_path = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
    causal_reference = ROOT / "docs/core/07_artifacts/verification/matter_space_causal_reference_verification.json"
    causal_full = ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
    thermal = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json"
    thermal_map = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_observable_map_readiness.json"
    thermal_calibration = ROOT / "docs/core/07_artifacts/topic13/thermal_dimensional_calibration_contract.json"
    thermal_source = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"
    thermal_review = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_thermal_source_review.json"
    phase_source = ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_source_archive_policy_gate.json"
    phase_formula = ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_full_text_formula_readiness_gate.json"
    phase_next = ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_structure_factor_ch_finite_k_next_path_decision_gate.json"
    phase_replication = ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_conserved_order_spectral_finite_size_replication.json"
    fluid = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json"
    o2 = ROOT / "docs/core/07_artifacts/verification/o2_finite_density_eos_verification.json"
    o2_formula = ROOT / "docs/core/07_artifacts/correspondence/o2_eos_formula_audit.json"

    causal_ref = load(causal_reference) if causal_reference.is_file() else {}
    causal_full_value = load(causal_full) if causal_full.is_file() else {}
    thermal_value = load(thermal) if thermal.is_file() else {}
    thermal_map_value = load(thermal_map) if thermal_map.is_file() else {}
    thermal_cal_value = load(thermal_calibration) if thermal_calibration.is_file() else {}
    phase_values = [load(path) for path in (phase_source, phase_formula, phase_next, phase_replication) if path.is_file()]
    fluid_value = load(fluid) if fluid.is_file() else {}
    o2_value = load(o2) if o2.is_file() else {}
    o2_formula_value = load(o2_formula) if o2_formula.is_file() else {}

    def gate(value: dict[str, Any], *keys: str) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if key in value}

    phase_statuses = [value.get("status", value.get("audit_status")) for value in phase_values]
    phase_blockers = [
        value.get("controlling_blocker")
        or value.get("next_controller")
        or value.get("claim_boundary")
        for value in phase_values
    ]

    rooms = {
        "core": {
            "ontology": "central UET candidate effective theory; C, Phi, R_gen, and R_obs remain lane-separated",
            "units": "registry-declared normalized/natural lanes with SI mapping incomplete",
            "derivation_class": "foundation registry and dependency integration",
            "observable": "central equation-to-observable mapping and dependency gates",
            "data_role": "metadata and artifact integration; no new external claim",
            "verification_status": "BLOCKED_FOUNDATION_GATE",
            "controlling_blocker": "foundation_coverage_units_observable_and_external_claim_gates_incomplete",
            "claim_boundary": "candidate effective theory; no global closure",
            "next_action": "close open-system/SK-KMS, dimensional observable, and curved 3+1 dependency artifacts",
            "evidence": [snapshot(BRIEF), snapshot(registry_path, ("status", "generated_at", "coverage")), snapshot(foundation_path, ("status", "controlling_blocker"))],
        },
        "topic_0_13": {
            "ontology": "Phi is a normalized effective response; Delta_Tq is a source-defined quasi-temperature difference",
            "units": "normalized y_TTG; alpha_Phi_K in K per normalized Phi remains open",
            "derivation_class": "standard observable definition plus candidate lane mapping; alpha not derived",
            "observable": "y_TTG=Delta_Tq(t)/Delta_Tq(0); y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)",
            "data_role": "provisional Ding 2022 figure intake for shape/provenance only; Xie 2026 locked holdout",
            "verification_status": thermal_value.get("status", "MISSING_ARTIFACT"),
            "controlling_blocker": thermal_value.get("controlling_blocker", "thermal_artifact_missing"),
            "claim_boundary": "simulation/internal control and provisional source intake; no temperature prediction or external validation",
            "next_action": "independently derive or calibrate alpha_Phi_K with uncertainty and rerun the preregistered source comparison without holdout access",
            "evidence": [snapshot(thermal, ("status", "internal_gate_status", "controlling_blocker", "failed_gates", "gates")), snapshot(thermal_map, ("audit_status", "mapping_status", "gates")), snapshot(thermal_calibration, ("audit_status", "claim_status", "gates")), snapshot(thermal_source, ("status", "usage_policy", "source_access_audit")), snapshot(thermal_review, ("numeric_fitting_allowed", "holdout_consumed"))],
            "selected_causal_branch": {
                "verification_status": causal_ref.get("audit_status", "MISSING_ARTIFACT"),
                "prearrival_leakage_fraction": causal_ref.get("reference", {}).get("metrics", {}).get("prearrival_leakage_fraction"),
                "threshold": 1.0e-6,
                "full_candidate_gate_preserved": True,
                "full_candidate_prearrival_leakage_fraction": causal_full_value.get("metrics", {}).get("prearrival_leakage", {}).get("value"),
                "claim_boundary": "frozen-C normalized compact-support control only",
                "evidence": [snapshot(causal_reference, ("audit_status", "reference_status", "default_candidate_status")), snapshot(causal_full, ("status", "controlling_blocker"))],
            },
        },
        "topic_0_11": {
            "ontology": "conserved phase/order coordinate with source-declared structure-factor observable",
            "units": "normalized finite-size diagnostic; source-specific estimator dimensions open",
            "derivation_class": "source archive and estimator policy; no universality derivation",
            "observable": "finite-k structure factor and correlation length only after source/estimator acceptance",
            "data_role": "source archive/formula fragments and internal finite-size replication; no holdout claim",
            "verification_status": "BLOCKED_SOURCE_AND_ESTIMATOR_POLICY",
            "controlling_blocker": "source_formula_extraction_and_accepted_estimator_policy_remain_blocked",
            "claim_boundary": "diagnostic/replication lane; no exponent or universality promotion",
            "next_action": "finish source-backed formula extraction, estimator acceptance, and temporal/replicate acquisition before any exponent rerun",
            "evidence": [snapshot(path, ("status", "audit_status", "controlling_blocker", "next_controller")) for path in (phase_source, phase_formula, phase_next, phase_replication)],
            "current_artifact_statuses": phase_statuses,
            "current_blocker_text": phase_blockers,
        },
        "core_o2": {
            "ontology": "existing global O(2) matter doublet; C remains a normalized coarse coordinate and Phi remains response scalar",
            "units": "tree-level natural-unit EOS; SI, finite-temperature, Kubo, and curved transport lanes open",
            "derivation_class": "tree-level mean-field EOS derivation and formal transport contract",
            "observable": "finite-density EOS and formal transport coefficients; no accepted SI observable map",
            "data_role": "external source metadata/comparator roles only",
            "verification_status": o2_value.get("audit_status", o2_value.get("status", "MISSING_ARTIFACT")),
            "controlling_blocker": "finite_temperature_Kubo_SI_and_curved_transport_completion_open",
            "claim_boundary": "formal natural-unit O(2) lane; no signed-O(2)-charge identity for C",
            "next_action": "retain current lane and complete coefficient/transport mapping only after Core dependencies permit",
            "evidence": [snapshot(o2, ("audit_status", "evidence_status", "claim_boundary")), snapshot(o2_formula, ("status", "controlling_blockers", "next_controller"))],
        },
        "topic_0_10_comparator": {
            "ontology": "standard-fluid comparator variables are benchmark variables, not UET universal fields",
            "units": "dimensionless benchmark units under the declared grid/timing contract",
            "derivation_class": "formula audit and internal simplified comparator",
            "observable": "runtime, stability, and declared comparator metrics",
            "data_role": "internal benchmark only",
            "verification_status": fluid_value.get("status", fluid_value.get("audit_status", "MISSING_ARTIFACT")),
            "controlling_blocker": "full_UET_constitutive_transport_deferred_until_post_Gravity_dependency_gate",
            "claim_boundary": "internal simplified benchmark only; no external CFD validation",
            "next_action": "keep comparator separate and defer full constitutive transport",
            "evidence": [snapshot(fluid, ("status", "claim_boundary", "notes", "gates"))],
        },
    }

    contract = {
        "schema_version": "1.0",
        "artifact": "uet_research_room_wave1_contract",
        "generated_at": date.today().isoformat(),
        "status": "PASS_WITH_BLOCKED_LANES",
        "claim_promotion": False,
        "brief": {"path": rel(BRIEF), "sha256": sha256(BRIEF)},
        "required_mapping_fields": ["ontology", "units", "derivation_class", "observable", "data_role", "verification_status", "controlling_blocker", "claim_boundary"],
        "rooms": rooms,
        "phase_gates": {
            "wave1_exit": "all room artifacts parse, blockers and next actions are explicit, and Topic 0.13/0.11 hashes are recorded",
            "gravity_start": "BLOCKED until Wave 1 integration gate and Core observable/causal dependencies permit",
            "galaxy_start": "BLOCKED until curved 3+1 parent and observable mapping permit",
            "full_constitutive_transport": "BLOCKED until post-Gravity dependency gate",
        },
        "integration_blockers": [
            "core full coupled pre-arrival leakage remains above the locked 1e-6 threshold",
            "alpha_Phi_K has no independent derivation or calibration with uncertainty",
            "TTG source rows are provisional digitized intake, not raw author data",
            "Xie 2026 remains locked holdout and was not consumed",
            "Topic 0.11 source/formula/estimator policy remains blocked",
            "Core O(2) finite-temperature/Kubo/SI/curved lanes remain open",
        ],
        "claim_boundary": "Wave 1 closes coordination ambiguity only; UET remains a candidate effective theory with blocked foundation dependencies.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": contract["status"], "rooms": list(rooms), "artifact": rel(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
