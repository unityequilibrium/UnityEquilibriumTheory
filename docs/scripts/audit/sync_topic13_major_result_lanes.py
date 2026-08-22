from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"

LANES = (
    ("T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE", "graphite_elastic_bulk_modulus_source"),
    ("T13_GRAPHITE_ISOTHERMAL_KT_SOURCE", "graphite_isothermal_kt_source"),
    ("T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE", "mp48_force_constant_csrc_mesh_convergence"),
    ("T13_MP48_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING", "mp48_ding_csrc_response_mapping"),
    ("T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY", "mp48_temperature_volume_uncertainty_boundary"),
    ("T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY", "graphite_alpha_v_kt_matched_source_boundary"),
    ("T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY", "ding_alternate_public_dataset_discovery_boundary"),
    ("T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY", "huang_2023_supplementary_payload_boundary"),
    ("T13_HUBERMAN_2019_PUBLIC_PBTE_BOUNDARY", "huberman_2019_public_pbte_boundary"),
    ("T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY", "nist_axm5q1_density_source_boundary"),
    ("T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR", "tpg_anisotropic_alpha_v_comparator"),
    (
        "T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR",
        "natural_graphite_nelson_riley_alpha_v_comparator",
    ),
    ("T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR", "bipm_specific_heat_cp_comparator"),
    ("T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR", "iaea_graphite_table_cv_comparator"),
    ("T13_IAEA_GR280_SAME_STATE_CP_COMPARATOR", "iaea_gr280_same_state_cp_comparator"),
    ("T13_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR", "zenodo_hitrace_isotropic_graphite_cp_comparator"),
    ("T13_ZENODO_HITRACE_IG210_ALPHA_L_COMPARATOR", "zenodo_hitrace_ig210_alpha_l_comparator"),

    ("T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE", "farooqui_ig210_thermophysical_source"),
    ("T13_IAEA_CV_UNCERTAINTY_BOUNDARY", "iaea_cv_uncertainty_boundary"),
    ("T13_DING_MATERIAL_REGIME_BOUNDARY", "ding_material_regime_boundary"),
    ("T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR", "phonix_mp47_graphite_harmonic_comparator"),
    ("T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR", "oxford_tgs_numeric_rows_comparator"),
    ("T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR", "desorbo_1955_ceylon_graphite_cp_comparator"),
    ("T13_UET_O2_KINETIC_COLLISION_KERNEL_LANE", "uet_o2_kinetic_collision_kernel_lane"),
    ("T13_UET_O2_QUANTUM_COLLISION_ENHANCEMENT_LANE", "uet_o2_quantum_collision_enhancement_lane"),
    ("T13_UET_O2_CHARGE_CONSERVING_LADDER_RESPONSE_LANE", "uet_o2_charge_conserving_ladder_response_lane"),
    ("T13_UET_O2_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE", "uet_o2_momentum_ladder_sk_kms_interface_lane"),
    ("T13_UET_O2_ENERGY_MOMENTUM_CONSERVING_BS_INTERFACE_LANE", "uet_o2_energy_momentum_conserving_bs_interface_lane"),
    ("T13_UET_O2_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE", "uet_o2_exact_kinematic_2to2_transition_kernel_lane"),
    ("T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE", "uet_o2_finite_t_quasiparticle_eos_lane"),
    ("T13_UET_O2_EQUILIBRIUM_KMS_LANE", "uet_o2_equilibrium_kms_lane"),
    ("T13_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY", "graphite_green_kubo_source_boundary"),
    ("T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE", "uet_o2_open_system_sk_kms_entropy_lane"),
    ("T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT", "independent_csrc_acceptance_contract"),
    ("T13_DING_C_SRC_FIXED_VOLUME_THERMODYNAMIC_IDENTITY", "ding_c_src_fixed_volume_identity"),
    ("T13_C_SRC_THERMODYNAMIC_TRANSPORT_REGIME_DECOMPOSITION", "csrc_thermodynamic_transport_regime_decomposition"),
    ("T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY", "csrc_equilibrium_component_acceptance"),
    ("T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION", "calorine_zenodo_nep_bte_numeric_reproduction"),
    ("T13_CALORINE_FULL_LBTE_NUMERICAL_STABILITY_BOUNDARY", "calorine_full_lbte_numerical_stability_boundary"),
    ("T13_UET_O2_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE", "uet_o2_conservative_continuum_collocation_lane"),
    ("T13_UET_O2_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE", "uet_o2_tree_level_bs_sk_match_interface_lane"),
    ("T13_UET_O2_ONE_LOOP_VERTEX_UV_BOUNDARY", "uet_o2_one_loop_vertex_uv_boundary"),
    ("T13_UET_O2_RENORMALIZED_VERTEX_SCHEME", "uet_o2_renormalized_vertex_scheme"),
    ("T13_UET_O2_FINITE_DENSITY_CHARGED_VERTEX_SCHEME", "uet_o2_finite_density_charged_vertex_scheme"),
    ("T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE", "uet_o2_interacting_sk_kms_action_interface"),
    ("T13_UET_O2_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE", "uet_o2_nonlocal_sk_kms_memory_kernel_lane"),
    ("T13_UET_O2_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO", "uet_o2_one_loop_retarded_self_energy_no_go"),
    ("T13_UET_O2_TWO_LOOP_SUNSET_CUT_LANE", "uet_o2_two_loop_sunset_cut_lane"),
    ("T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE", "uet_o2_finite_channel_entropy_balance_lane"),
    ("T13_JUN_FINAL_SOURCE_BOUNDARY", "jun_final_source_boundary"),
    ("T13_HONG_FINAL_SOURCE_BOUNDARY", "hong_final_source_boundary"),
    ("T13_PETERSON_SOURCE_IDENTITY_NO_GO", "peterson_source_identity_no_go"),
    ("T13_CALORINE_ISOTOPE_MASS_SENSITIVITY", "calorine_isotope_mass_sensitivity"),
    ("T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION", "calorine_state_uncertainty_decomposition"),
    ("T13_CALORINE_C_SRC_EQUILIBRIUM_CROSSCHECK", "calorine_csrc_equilibrium_crosscheck"),
    ("T13_FIGSHARE_DFT_FORCE_DATA_BOUNDARY", "figshare_dft_force_data_boundary"),
    ("T13_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY", "huang_2023_nims_mdr_payload_boundary"),
    ("T13_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY", "calorine_public_model_variant_boundary"),
    ("T13_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY", "calorine_nep1_backend_compatibility"),
    ("T13_CALORINE_LEGACY_NEP2_BACKEND_PROBE", "calorine_legacy_nep2_backend_probe"),
    ("T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION", "calorine_legacy_nep2_pbte_reproduction"),
    ("T13_CALORINE_MODEL_FORM_STATE_SPREAD_COMPARISON", "calorine_model_form_state_spread_comparison"),
    ("T13_DING_2017_ACS_SUPPLEMENTARY_PAYLOAD_BOUNDARY", "ding_2017_acs_supplementary_payload_boundary"),
    ("T13_PHI_SI_ANCHOR_PUBLIC_SOURCE_BOUNDARY", "phi_si_anchor_public_source_boundary"),
    ("T13_COVARIANT_ACTION_SYMBOLIC_SI_CONVERSION_CONTRACT", "covariant_action_symbolic_si_conversion_contract"),
    ("T13_UET_O2_FINITE_T_SELF_ENERGY_HARTREE_LANE", "uet_o2_finite_t_self_energy_hartree_lane"),
    ("T13_UET_O2_HARTREE_EQUILIBRIUM_THERMODYNAMIC_LANE", "uet_o2_hartree_equilibrium_thermodynamic_lane"),
    ("T13_UET_O2_FINITE_T_SCHEME_IDENTIFIABILITY_NO_GO", "uet_o2_finite_t_scheme_identifiability_no_go"),
    ("T13_UET_O2_FORMAL_TWO_SECTOR_THERMODYNAMIC_LANE", "uet_o2_formal_two_sector_thermodynamic_lane"),
    ("T13_UET_O2_FORMAL_TRANSVERSE_RESPONSE_LANE", "uet_o2_formal_transverse_response_lane"),
    ("T13_UET_O2_THERMODYNAMIC_NORMAL_COMPONENT_LANE", "uet_o2_thermodynamic_normal_component_lane"),
    ("T13_UET_O2_CONDENSED_RELATIVE_FLOW_COLLISION_KERNEL_LANE", "uet_o2_condensed_relative_flow_collision_kernel_lane"),
    ("T13_UET_O2_CONTINUUM_RELATIVE_FLOW_KUBO_LANE", "uet_o2_continuum_relative_flow_kubo_lane"),
    ("T13_UET_O2_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE", "uet_o2_condensed_loop_renormalized_contact_vertex_lane"),
    ("T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE", "uet_o2_condensed_relative_flow_kubo_admission_lane"),
    ("T13_UET_O2_CONDENSED_SK_KMS_KUBO_MATCH_LANE", "uet_o2_condensed_sk_kms_kubo_match_lane"),
    ("T13_UET_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE", "uet_o2_finite_t_declared_retarded_1pi_response_grid_lane"),
    ("T13_UET_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE", "uet_o2_finite_t_signed_cut_kinematic_taxonomy_lane"),
    ("T13_UET_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE", "uet_o2_finite_t_sunset_cut_multiplicity_lane"),
    ("T13_UET_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE", "uet_o2_finite_t_all_onshell_cut_spectral_response_lane"),
    ("T13_UET_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE", "uet_o2_finite_t_declared_channel_retarded_advanced_keldysh_1pi_lane"),
    ("T13_UET_O2_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_1PI_LANE", "uet_o2_finite_t_offshell_threshold_crossing_1pi_lane"),
    ("T13_UET_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE", "uet_o2_finite_t_all_22_permutation_identity_lane"),
    ("T13_UET_O2_COLLISIONLESS_KUBO_NO_GO", "uet_o2_collisionless_kubo_no_go"),
    ("T13_UET_O2_HARTREE_NORMAL_STABILITY_BOUNDARY_LANE", "uet_o2_hartree_normal_stability_boundary_lane"),
    ("T13_UET_O2_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE", "uet_o2_renormalized_condensate_stationarity_scheme_dependence"),
    ("T13_UET_O2_RENORMALIZED_HARTREE_NORMAL_LANE", "uet_o2_renormalized_hartree_normal_lane"),
    ("T13_UET_O2_CONDENSED_GOLDSTONE_WARD_NO_GO", "uet_o2_condensed_goldstone_ward_no_go"),
    ("T13_UET_O2_WARD_CONSTRAINED_CONDENSED_LANE", "uet_o2_ward_constrained_condensed_lane"),
    ("T13_UET_O2_FINITE_T_OFFSHELL_1PI_FORMAL_LANE", "uet_o2_finite_t_offshell_1pi_formal_lane"),
    ("T13_UET_O2_WARD_CONSTRAINED_COEFFICIENT_STATE_DEPENDENCE_NO_GO", "uet_o2_ward_constrained_coefficient_state_dependence_no_go"),
    ("T13_UET_O2_AUXILIARY_FIELD_WARD_PRESERVING_CONDENSED_LANE", "uet_o2_auxiliary_field_ward_preserving_condensed_lane"),
    ("T13_UET_O2_CONDENSED_RETARDED_DISSIPATION_NO_GO", "uet_o2_condensed_retarded_dissipation_no_go"),
)


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def lane_register_record(major: dict, full_hash: str) -> dict:
    record = {
        field: major.get(field)
        for field in (
            "major_result_id",
            "topic",
            "closure_level",
            "what_is_closed",
            "equation_or_mapping",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "open_blockers",
            "dependency_unlocked",
            "claim_boundary",
        )
    }
    record["evidence_artifacts"] = list(major.get("evidence_artifacts", []))
    record["evidence_artifacts"].append(
        {
            "path": FULL_REL,
            "sha256": full_hash,
            "summary": {
                "projection": "Topic 13 full-gate source_package lane",
                "full_core_unlock": False,
            },
        }
    )
    return record


def main() -> int:
    register = load(REGISTER_REL)
    full = load(FULL_REL)
    full_hash = digest(FULL_REL)
    entries = register["entries"]

    full_entry = next(
        item for item in entries if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    full_major = full["major_result"]
    for field in (
        "closure_level",
        "what_is_closed",
        "equation_or_mapping",
        "units",
        "derivation_class",
        "observable",
        "data_role",
        "claim_boundary",
    ):
        full_entry[field] = full_major.get(field, full_entry.get(field))
    full_entry["open_blockers"] = full_major.get("what_remains_open", [])
    full_entry["verification_status"] = full.get("status", full_entry.get("verification_status"))
    full_evidence = next(
        item for item in full_entry["evidence_artifacts"] if item.get("path") == FULL_REL
    )
    full_evidence["sha256"] = full_hash
    full_evidence.setdefault("summary", {})["status"] = full.get("status")
    full_evidence["summary"]["controlling_blocker"] = full.get("controlling_blocker")

    existing = {item.get("major_result_id") for item in entries}
    source_package = full["verification_status"]["source_package"]

    def projection_for_lane(lane_key: str) -> dict:
        """Read a lane from the section that owns its evidence role."""

        sections = full.get("verification_status", {})
        for section_name in (
            "source_package",
            "eos_transport_kms_entropy",
            "dimensional_observable_map",
        ):
            section = sections.get(section_name, {})
            candidate = section.get(lane_key)
            if isinstance(candidate, dict):
                return candidate
        return {}
    new_records = []
    for major_result_id, lane_key in LANES:
        if major_result_id in existing:
            continue
        projection = projection_for_lane(lane_key)
        if not isinstance(projection, dict):
            raise SystemExit(f"missing full-gate projection: {lane_key}")
        audit_path = projection.get("audit", {}).get("path")
        if not audit_path:
            raise SystemExit(f"missing audit path: {lane_key}")
        lane_artifact = load(audit_path)
        major = lane_artifact.get("major_result")
        if not isinstance(major, dict) or major.get("major_result_id") != major_result_id:
            raise SystemExit(f"major-result identity mismatch: {lane_key}")
        new_records.append(lane_register_record(major, full_hash))

    if new_records:
        full_index = next(
            index
            for index, item in enumerate(entries)
            if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
        )
        entries[full_index + 1 : full_index + 1] = new_records
    refreshed_records = 0
    for major_result_id, lane_key in LANES:
        if major_result_id not in existing:
            continue
        projection = projection_for_lane(lane_key)
        if not isinstance(projection, dict):
            raise SystemExit(f"missing full-gate projection: {lane_key}")
        audit_path = projection.get("audit", {}).get("path")
        if not audit_path:
            raise SystemExit(f"missing audit path: {lane_key}")
        lane_artifact = load(audit_path)
        major = lane_artifact.get("major_result")
        if not isinstance(major, dict) or major.get("major_result_id") != major_result_id:
            raise SystemExit(f"major-result identity mismatch: {lane_key}")
        current = next(item for item in entries if item.get("major_result_id") == major_result_id)
        current.update(lane_register_record(major, full_hash))
        refreshed_records += 1


    register["generated_at"] = date.today().isoformat()
    register["claim_promotion"] = False
    register["topic13_lane_sync"] = {
        "full_gate": {"path": FULL_REL, "sha256": full_hash},
        "major_result_ids": [item[0] for item in LANES],
        "added_count": len(new_records),
        "refreshed_count": refreshed_records,
        "full_core_unlock": False,
    }
    register_path = ROOT / REGISTER_REL
    register_path.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency_path = ROOT / DEPENDENCY_REL
    dependency = load(DEPENDENCY_REL)
    register_hash = digest(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["register_sha256"] = register_hash
    partial["full_core_unlock"] = False
    partial["source_lanes"] = {
        lane_key: {
            "major_result_id": major_result_id,
            "closure_level": projection_for_lane(lane_key).get("closure_level"),
            "status": projection_for_lane(lane_key).get("status"),
            "full_core_unlock": False,
            "audit": projection_for_lane(lane_key).get("audit"),
        }
        for major_result_id, lane_key in LANES
    }
    dependency_path.write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS_TOPIC13_MAJOR_RESULT_REGISTER_SYNC",
                "added_count": len(new_records),
        "refreshed_count": refreshed_records,
                "full_gate_sha256": full_hash,
                "register_sha256": register_hash,
                "full_core_unlock": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
