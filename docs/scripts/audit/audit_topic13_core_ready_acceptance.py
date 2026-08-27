"""Verify Full Topic 13 Core-ready acceptance requirement by requirement."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/core/artifacts/t13_full_core_ready_acceptance_audit.json"

PATHS = {
    "gate": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json",
    "matrix": "docs/core/artifacts/t13_topic13_closure_matrix.json",
    "composition": "docs/core/artifacts/t13_he4_core_thermodynamic_bridge_composition_audit.json",
    "causal": "docs/core/artifacts/t13_causal_named_branch_core_compatibility.json",
    "no_go": "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json",
    "ttg_source": "docs/core/artifacts/ding_2022_source_mapping_audit.json",
    "alpha": "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json",
    "beta": "docs/core/artifacts/t13_he4_o2_si_beta_mapping_audit.json",
    "normal_component": "docs/core/artifacts/t13_uet_o2_thermodynamic_normal_component_audit.json",
    "formal_bridge": "docs/core/artifacts/t13_formal_thermodynamic_bridge_integration_audit.json",
    "sk_kms": "docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json",
    "entropy": "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json",
    "transport": "docs/core/artifacts/t13_he4_normal_viscosity_kubo_audit.json",
    "landauer": "docs/core/artifacts/t13_landauer_core_disposition_audit.json",
    "holdout": "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json",
    "chaos": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_thermal_dynamical_regime_audit.json",
    "register": "docs/core/artifacts/uet_major_result_closure_register.json",
    "dependency": "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(name: str, docs: dict[str, dict]) -> dict:
    path = ROOT / PATHS[name]
    return {"path": PATHS[name], "sha256": sha256(path), "status": docs[name].get("status")}


def main() -> int:
    docs = {name: load(ROOT / path) for name, path in PATHS.items()}
    gate = docs["gate"]
    core = gate["closure_tracks"]["o2_he4_core_ready"]
    causal = docs["causal"]
    alpha = docs["alpha"]["record"]
    beta = docs["beta"]["record"]
    transport = docs["transport"]
    ttg = docs["ttg_source"]
    holdout_audit = docs["holdout"].get("audit", {})
    register_entry = next(
        item
        for item in docs["register"]["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
    )
    dependency = docs["dependency"]

    criteria = {
        "causal_branch_passes_locked_threshold": (
            causal["status"] == "PASS_CAUSAL_NAMED_BRANCH_CORE_COMPATIBILITY"
            and causal["baseline_preservation"]["locked_threshold"] == 1.0e-6
            and causal["selected_branch"]["prearrival_leakage_fraction"] <= 1.0e-6
            and causal["selected_branch"]["C_arrival_target_abs"] > 0.0
            and causal["selected_branch"]["Phi_arrival_target_abs"] > 0.0
            and causal["checks"]["temporal_and_spatial_convergence_pass"]
            and causal["checks"]["energy_ledger_passes"]
            and causal["checks"]["no_clipping_padding_or_fit"]
        ),
        "conserved_c_no_go_or_regularization_is_recorded": (
            docs["no_go"]["status"]
            == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS"
            and causal["checks"]["original_baseline_is_not_promoted"]
        ),
        "alpha_is_independent_not_fitted": (
            docs["alpha"]["status"] == "PASS_HE4_LOCAL_ALPHA_AND_FIELD_NORMALIZATION"
            and alpha["record_kind"] == "EXTERNAL_INPUT"
            and alpha["data_role"] == "CALIBRATION"
            and math.isfinite(alpha["alpha_Phi_K"])
            and alpha["alpha_uncertainty_K_per_normalized_base_Phi"] > 0.0
            and alpha["holdout_policy"]["target_curve_used"] is False
            and alpha["holdout_policy"]["fit_or_tuning_used"] is False
        ),
        "ttg_numeric_source_provenance_is_complete_for_comparison": (
            ttg["status"] == "PASS"
            and ttg["checks"]["permitted_figure_numeric_route_ready"]
            and ttg["checks"]["row_identity_complete"]
            and ttg["checks"]["units_declared"]
            and ttg["checks"]["uncertainty_declared"]
            and ttg["checks"]["preprocessing_declared"]
            and ttg["checks"]["license_declared"]
            and ttg["observed_package"]["row_count"] > 0
            and ttg["checks"]["holdout_not_accessed"]
            and ttg["checks"]["numeric_fitting_disabled"]
        ),
        "landauer_controllers_are_dispositioned": (
            docs["landauer"]["status"] == "PASS_LANDAUER_CORE_ROLE_DISPOSITION"
            and docs["landauer"]["major_result"]["closure_level"] == "CLOSED_FOR_CORE"
            and all(docs["landauer"]["checks"].values())
        ),
        "dimensional_map_and_uncertainty_pass": (
            docs["beta"]["status"] == "PASS_HE4_SI_SCALE_AND_NORMALIZED_BETA"
            and beta["temperature_standard_uncertainty_K"] > 0.0
            and beta["energy_density_scale_uncertainty_J_m3"] > 0.0
            and beta["beta_T13_uncertainty_bound"] > 0.0
            and beta["beta_SI_uncertainty_J_m3_per_normalized_Phi2"] > 0.0
            and beta["holdout_policy"]["landauer_identity_used"] is False
        ),
        "finite_temperature_normal_component_passes": (
            docs["normal_component"]["status"]
            == "PASS_ACTION_DERIVED_THERMODYNAMIC_NORMAL_COMPONENT_LANE"
            and all(docs["normal_component"]["checks"].values())
        ),
        "eos_transport_kms_entropy_and_balance_pass": (
            docs["formal_bridge"]["status"] == "PASS_FORMAL_T13_THERMODYNAMIC_BRIDGE_INTEGRATION"
            and all(docs["formal_bridge"]["checks"].values())
            and docs["sk_kms"]["status"] == "PASS_NAMED_SK_KMS_ENTROPY_INTERFACE_CONTRACT"
            and all(docs["sk_kms"]["checks"].values())
            and docs["entropy"]["status"]
            == "PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE"
            and all(docs["entropy"]["checks"].values())
            and transport["status"] == "PASS_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT"
            and transport["record_validation"]["status"] == "PASS_PHYSICAL_TRANSPORT_RECORD"
        ),
        "heat_flux_mapping_preserves_ontology": (
            docs["entropy"]["checks"]["Phi_ontology_is_preserved"]
            and docs["entropy"]["checks"]["C_ontology_is_preserved"]
            and docs["entropy"]["checks"]["R_gen_ontology_is_preserved"]
            and docs["entropy"]["checks"]["R_obs_remains_separate"]
            and docs["composition"]["checks"]["R_gen_absent_from_physical_state_vectors"]
        ),
        "xie_holdout_access_audit_passes": (
            docs["holdout"]["status"] == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY"
            and holdout_audit.get("numeric_payload_consumed") is False
            and holdout_audit.get("numeric_rows_consumed") is False
            and holdout_audit.get("used_for_fit") is False
            and holdout_audit.get("used_for_tuning") is False
            and holdout_audit.get("used_for_calibration") is False
            and holdout_audit.get("used_for_threshold_adjustment") is False
        ),
        "chaos_is_nonblocking_and_does_not_relabel_state": (
            docs["chaos"]["status"] == "PASS_SCOPED_THERMAL_DYNAMICAL_REGIME_PILOT"
            and docs["chaos"]["full_core_unlock"] is False
            and docs["chaos"]["branches"]["trace_only"]["classification"]
            == "NOT_APPLICABLE_AS_DYNAMICAL_STATE"
            and docs["chaos"]["holdout_access"]["holdout_consumed"] is False
        ),
        "registry_matrix_and_dependency_are_consistent": (
            gate["core_result_status"] == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
            and core["status"] == "CLOSED_FOR_CORE"
            and docs["matrix"]["status"] == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
            and docs["matrix"]["full_core_unlock"] is True
            and register_entry["closure_level"] == "CLOSED_FOR_CORE"
            and dependency["topic13_core_ready"]["full_core_unlock"] is True
            and dependency["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]["status"]
            == "UNLOCKED"
            and dependency["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"]
            == "BLOCKED_DEPENDENCY"
        ),
        "global_claim_promotion_remains_false": (
            gate["claim_promotion"] is False
            and docs["matrix"]["claim_promotion"] is False
            and docs["composition"]["claim_promotion"] is False
            and docs["register"]["claim_promotion"] is False
            and docs["dependency"]["claim_promotion"] is False
        ),
    }
    passed = all(criteria.values())
    status = "PASS_T13_FULL_CORE_READY_ACCEPTANCE" if passed else "FAIL_T13_FULL_CORE_READY_ACCEPTANCE"
    evidence_names = list(PATHS)
    report = {
        "schema_version": "t13-full-core-ready-acceptance-v1",
        "artifact": "t13_full_core_ready_acceptance_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY_ACCEPTED",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_CORE" if passed else "PARTIAL",
            "what_is_closed": [name for name, value in criteria.items() if value],
            "what_remains_open": [] if passed else [name for name, value in criteria.items() if not value],
            "equation_or_mapping": {
                "measurement": "y_TTG = Delta_Tq(t)/Delta_Tq(0); y_TTG^UET = Delta_Phi(t)/Delta_Phi(0)",
                "dimensional": "Delta_Tq = alpha_Phi_K Delta_Phi_norm",
                "field_and_energy": "Delta_Phi_norm=Z_Phi Delta_Phi_natural; f_SI=e0 f_natural",
                "entropy": "J_S^mu=s u^mu+q^mu/T; nabla_mu J_S^mu>=0",
            },
            "units": {"alpha_Phi_K": "K per normalized base Phi", "beta_SI": "J m^-3 per normalized Phi squared", "eta": "Pa s"},
            "derivation_class": "REQUIREMENT_BY_REQUIREMENT_ACCEPTANCE_AUDIT_OF_HASHED_CORE_EVIDENCE",
            "observable": "bounded O(2)/He-4 thermal bridge Core handoff",
            "data_role": "INTERNAL_CORE_ACCEPTANCE_NOT_EXTERNAL_VALIDATION",
            "evidence_artifacts": [evidence(name, docs) for name in evidence_names],
            "verification_status": status,
            "open_blockers": [] if passed else [name for name, value in criteria.items() if not value],
            "dependency_unlocked": "Core curved 3+1 research may start; Gravity remains blocked until that separate result closes.",
            "claim_boundary": "Acceptance is limited to the bounded internal O(2)/He-4 Core bridge. Ding figure-derived TTG rows remain comparison-only, raw-author/graphite external validation remains open, the original conserved-gradient baseline remains blocked, and global UET closure remains false.",
        },
        "criteria": criteria,
        "quantitative_witnesses": {
            "causal_prearrival_leakage_fraction": causal["selected_branch"]["prearrival_leakage_fraction"],
            "causal_locked_threshold": causal["baseline_preservation"]["locked_threshold"],
            "alpha_Phi_K": alpha["alpha_Phi_K"],
            "alpha_uncertainty": alpha["alpha_uncertainty_K_per_normalized_base_Phi"],
            "beta_T13": beta["beta_T13"],
            "beta_T13_uncertainty": beta["beta_T13_uncertainty_bound"],
            "beta_SI": beta["beta_SI_J_m3_per_normalized_Phi2"],
            "beta_SI_uncertainty": beta["beta_SI_uncertainty_J_m3_per_normalized_Phi2"],
            "physical_eta_Pa_s": transport["record"]["value"],
            "physical_eta_uncertainty_Pa_s": transport["record"]["uncertainty"],
            "ttg_comparison_row_count": ttg["observed_package"]["row_count"],
        },
        "external_tracks_still_open": {
            "graphite_ttg": gate["closure_tracks"]["graphite_ttg_external_validation"],
            "raw_author_ding_source": ttg["checks"]["raw_author_numeric_source_present"],
            "landauer_numeric_gaps": {
                name: item["external_open_blockers"]
                for name, item in docs["landauer"]["controllers"].items()
            },
            "curved_3p1_result_ready": False,
            "gravity_ready": False,
        },
        "controlling_blocker": None if passed else next(name for name, value in criteria.items() if not value),
        "next_action": "Start CORE_CURVED_3P1_OBSERVABLE_PARENT_READY as the next major result; keep graphite TTG and raw Landauer acquisition on external comparison tracks.",
        "claim_boundary": "Core-ready is not external-ready and not global UET closure.",
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "criteria_passed": sum(criteria.values()), "criteria_total": len(criteria), "failed": [name for name, value in criteria.items() if not value], "artifact": OUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
