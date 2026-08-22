"""Build the conservative full Topic 0.13 Core-ready closure gate.

This verifier composes existing evidence. It does not invent a calibration,
promote the selected frozen-C control, or consume the locked holdout.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


LANE_KEY_BY_ID = {'T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO': 'alpha_phi_k_normalized_scale_no_go', 'T13_ALPHA_PHI_K_PAIRED_RECORD_SEARCH': 'alpha_phi_k_paired_record_search', 'T13_BASE_PHI_INDEPENDENT_CALIBRATION_REQUIREMENT': 'base_phi_independent_calibration_requirement', 'T13_BETA_SYMBOL_SEPARATION_NONCIRCULARITY_NO_GO': 'beta_symbol_separation_non_circularity_no_go', 'T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO': 'beta_action_normalized_correspondence_no_go', 'T13_CAUSAL_BRANCH_SELECTION': 'causal_branch_selection', 'T13_CAUSAL_THERMAL_BRANCH_SELECTION': 'causal_branch_selection', 'T13_CAUSAL_FLUX_PHI_COUPLED_LANE': 'causal_flux_phi_coupled_lane', 'T13_CAUSAL_FLUX_TELEGRAPH_BRANCH': 'causal_flux_telegraph_branch', 'T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT': 'collective_response_eos_stability_contract', 'T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE': 'covariant_action_si_anchor_route', 'T13_COVARIANT_ACTION_SYMBOLIC_SI_CONVERSION_CONTRACT': 'covariant_action_symbolic_si_conversion_contract', 'T13_COVARIANT_FIELD_NORMALIZATION_IDENTIFIABILITY_NO_GO': 'covariant_field_normalization_identifiability_no_go', 'T13_COVARIANT_MATTER_COUPLING_NORMALIZATION_IDENTIFIABILITY_NO_GO': 'covariant_matter_coupling_normalization_no_go', 'T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY': 'covariant_transport_implementation_boundary', 'T13_CP_CV_CORRECTION_CONTRACT': 'cp_cv_correction_contract', 'T13_ALPHA_PHI_K_CONDITIONAL_DERIVATION': 'alpha_phi_k_conditional_derivation', 'T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE': 'ding_pbte_author_request_package', 'T13_DING_FIG1D_NORMALIZED_SOURCE_LANE': 'ding_fig1d_normalized_source_lane', 'T13_DING_C_SRC_INDEPENDENT_REPRODUCTION_BOUNDARY': 'ding_c_src_independent_reproduction_boundary', 'T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY': 'ding_public_supplementary_payload_boundary', 'T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING': 'ding_pbte_energy_temperature_mapping', 'T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO': 'ding_pbte_oa_numeric_input_no_go', 'T13_GATECH_STANDARD_TRANSPORT_COMPARATOR': 'standard_graphite_transport_comparator', 'T13_GATECH_VOLUMETRIC_CP_INDEPENDENCE_NO_GO': 'gatech_volumetric_cp_independence_no_go', 'T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION': 'mp48_independent_graphite_cv_reproduction', 'T13_MP48_SPECTRAL_C_SRC_REPRODUCTION': 'mp48_spectral_csrc_reproduction', 'T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION': 'mp48_force_constant_harmonic_reconstruction', 'T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE': 'mp48_force_constant_csrc_mesh_convergence', 'T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY': 'huang_2023_supplementary_payload_boundary', 'T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY': 'nist_axm5q1_density_source_boundary', 'T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY': 'nist_graphite_alpha_v_source_boundary', 'T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE': 'graphite_elastic_bulk_modulus_source', 'T13_GRAPHITE_ISOTHERMAL_KT_SOURCE': 'graphite_isothermal_kt_source', 'T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR': 'tpg_anisotropic_alpha_v_comparator', 'T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR': 'natural_graphite_nelson_riley_alpha_v_comparator', 'T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR': 'bipm_specific_heat_cp_comparator', 'T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR': 'iaea_graphite_table_cv_comparator', 'T13_IAEA_CV_UNCERTAINTY_BOUNDARY': 'iaea_cv_uncertainty_boundary', 'T13_DING_MATERIAL_REGIME_BOUNDARY': 'ding_material_regime_boundary', 'T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR': 'mp48_phi_e_dimensional_anchor_comparator', 'T13_PHYSICAL_KUBO_COEFFICIENT_PROVENANCE_GATE': 'physical_kubo_coefficient_provenance', 'T13_PHI_E_REFERENCE_NORMALIZATION': 'phi_e_reference_normalization', 'T13_PHI_E_TTG_BRIDGE_CONDITIONAL': 'phi_e_ttg_bridge_conditional', 'T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO': 'phi_energy_anchor_identifiability_no_go', 'T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT': 'sk_kms_entropy_interface_contract', 'T13_SOURCE_CP_95CI_ANCHOR': 'source_cp_95ci_anchor', 'T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR': 'standard_o2_finite_temperature_normal_comparator', 'T13_THERMAL_RESPONSE_BETA_CONTRACT': 'thermal_response_beta_contract', 'T13_FORMAL_NONCIRCULAR_BRIDGE_BOUNDARY': 'formal_non_circular_bridge_boundary', 'T13_UET_O2_CONDENSATE_FLUCTUATION_SPECTRUM': 'uet_o2_condensate_fluctuation_spectrum', 'T13_UET_O2_CONDENSATE_GAUSSIAN_FINITE_T_LANE': 'uet_o2_condensate_gaussian_finite_t_lane','T13_UET_O2_GAUSSIAN_OFFSHELL_BACKGROUND_BOUNDARY': 'uet_o2_gaussian_offshell_background_boundary','T13_TRANSPORT_COEFFICIENT_IDENTIFIABILITY_NO_GO': 'transport_coefficient_identifiability_no_go','T13_UET_O2_NORMAL_RESPONSE_CURVATURE_LANE': 'uet_o2_normal_response_curvature_lane','T13_UET_O2_RENORMALIZED_NORMAL_ONE_LOOP_LANE': 'uet_o2_renormalized_normal_one_loop_lane','T13_UET_O2_THERMAL_STABILITY_BOUNDARY': 'uet_o2_thermal_stability_boundary','T13_UET_O2_GAUSSIAN_THERMAL_STATIONARITY_NO_GO': 'uet_o2_gaussian_thermal_stationarity_no_go',       'T13_UET_O2_CONDENSATE_GOLDSTONE_IDEAL_LANE': 'uet_o2_condensate_goldstone_ideal_lane', 'T13_UET_O2_ONE_LOOP_CONVERGENCE': 'uet_o2_one_loop_convergence', 'T13_UET_O2_ONE_LOOP_NORMAL_BRANCH': 'uet_o2_one_loop_normal_branch', 'T13_UET_O2_ONE_LOOP_THERMAL_UV_BOUNDARY': 'uet_o2_one_loop_uv_boundary', 'T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY': 'uet_o2_normal_thermodynamic_consistency', 'T13_BERUT_SOURCE_PACKAGE_AVAILABILITY_BOUNDARY': 'berut_source_package_availability_boundary', 'T13_BERUT_FIGURE3_REMOTE_BINARY_IDENTITY': 'berut_figure3_remote_binary_identity', 'T13_BERUT_FIGURE3_DIGITIZATION': 'berut_figure3_digitization', 'T13_OXFORD_TGS_COMPARATOR_PROVENANCE': 'oxford_tgs_comparator_provenance', 'T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR': 'phonix_mp47_graphite_harmonic_comparator', 'T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR': 'oxford_tgs_numeric_rows_comparator', 'T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR': 'desorbo_1955_ceylon_graphite_cp_comparator', 'T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE': 'uet_o2_finite_t_quasiparticle_eos_lane', 'T13_UET_O2_EQUILIBRIUM_KMS_LANE': 'uet_o2_equilibrium_kms_lane', 'T13_GRAPHITE_GREEN_KUBO_SOURCE_BOUNDARY': 'graphite_green_kubo_source_boundary', 'T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE': 'uet_o2_open_system_sk_kms_entropy_lane', 'T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT': 'independent_csrc_acceptance_contract', 'T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY': 'calorine_zenodo_nep_bte_candidate_boundary', 'T13_NIMS_GRAPHITE_LTC_ROUTE_NO_GO': 'nims_graphite_ltc_route_no_go'}

LANE_KEY_BY_ID["T13_DING_2017_ACS_SUPPLEMENTARY_PAYLOAD_BOUNDARY"] = "ding_2017_acs_supplementary_payload_boundary"
LANE_KEY_BY_ID["T13_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY"] = "ding_experimental_heating_input_boundary"
LANE_KEY_BY_ID["T13_DING_C_SRC_FIXED_VOLUME_THERMODYNAMIC_IDENTITY"] = "ding_c_src_fixed_volume_identity"
LANE_KEY_BY_ID["T13_HUBERMAN_2019_PUBLIC_PBTE_BOUNDARY"] = "huberman_2019_public_pbte_boundary"
LANE_KEY_BY_ID["T13_IAEA_GR280_SAME_STATE_CP_COMPARATOR"] = "iaea_gr280_same_state_cp_comparator"
LANE_KEY_BY_ID["T13_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR"] = "zenodo_hitrace_isotropic_graphite_cp_comparator"
LANE_KEY_BY_ID["T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE"] = "farooqui_ig210_thermophysical_source"
LANE_KEY_BY_ID["T13_FAROOQUI_IG210_VOLUMETRIC_CP_UNCERTAINTY"] = "farooqui_ig210_volumetric_cp_uncertainty"
LANE_KEY_BY_ID["T13_ZENODO_HITRACE_IG210_ALPHA_L_COMPARATOR"] = "zenodo_hitrace_ig210_alpha_l_comparator"
LANE_KEY_BY_ID["T13_PHI_SI_ANCHOR_PUBLIC_SOURCE_BOUNDARY"] = "phi_si_anchor_public_source_boundary"
LANE_KEY_BY_ID["T13_UET_O2_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH"] = "uet_o2_microscopic_finite_cutoff_kubo_match"
LANE_KEY_BY_ID["T13_UET_O2_HEAT_CURRENT_KUBO_MATCH"] = "uet_o2_heat_current_kubo_match"
LANE_KEY_BY_ID["T13_UET_O2_HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY"] = "uet_o2_heat_current_kubo_continuum_boundary"
LANE_KEY_BY_ID["T13_UET_O2_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE"] = "uet_o2_regularized_continuum_heat_current_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_RELATIVE_FLOW_COLLISION_KERNEL_LANE"] = "uet_o2_condensed_relative_flow_collision_kernel_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONTINUUM_RELATIVE_FLOW_KUBO_LANE"] = "uet_o2_continuum_relative_flow_kubo_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE"] = "uet_o2_condensed_loop_renormalized_contact_vertex_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE"] = "uet_o2_condensed_relative_flow_kubo_admission_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_SK_KMS_KUBO_MATCH_LANE"] = "uet_o2_condensed_sk_kms_kubo_match_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE"] = "uet_o2_finite_t_declared_retarded_1pi_response_grid_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SELF_ENERGY_HARTREE_LANE"] = "uet_o2_finite_t_self_energy_hartree_lane"
LANE_KEY_BY_ID["T13_UET_O2_HARTREE_EQUILIBRIUM_THERMODYNAMIC_LANE"] = "uet_o2_hartree_equilibrium_thermodynamic_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SCHEME_IDENTIFIABILITY_NO_GO"] = "uet_o2_finite_t_scheme_identifiability_no_go"
LANE_KEY_BY_ID["T13_UET_O2_HARTREE_NORMAL_STABILITY_BOUNDARY_LANE"] = "uet_o2_hartree_normal_stability_boundary_lane"
LANE_KEY_BY_ID["T13_UET_O2_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE"] = "uet_o2_renormalized_condensate_stationarity_scheme_dependence"
LANE_KEY_BY_ID["T13_UET_O2_RENORMALIZED_HARTREE_NORMAL_LANE"] = "uet_o2_renormalized_hartree_normal_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_GOLDSTONE_WARD_NO_GO"] = "uet_o2_condensed_goldstone_ward_no_go"
LANE_KEY_BY_ID["T13_UET_O2_WARD_CONSTRAINED_CONDENSED_LANE"] = "uet_o2_ward_constrained_condensed_lane"
LANE_KEY_BY_ID["T13_UET_O2_WARD_CONSTRAINED_COEFFICIENT_STATE_DEPENDENCE_NO_GO"] = "uet_o2_ward_constrained_coefficient_state_dependence_no_go"
LANE_KEY_BY_ID["T13_UET_O2_AUXILIARY_FIELD_WARD_PRESERVING_CONDENSED_LANE"] = "uet_o2_auxiliary_field_ward_preserving_condensed_lane"
LANE_KEY_BY_ID["T13_UET_O2_AUXILIARY_FIELD_WARD_PRESERVING_CONDENSED_LANE"] = "uet_o2_auxiliary_field_ward_preserving_condensed_lane"

LANE_KEY_BY_ID["T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY"] = "mp48_temperature_volume_uncertainty_boundary"
LANE_KEY_BY_ID["T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY"] = "graphite_alpha_v_kt_matched_source_boundary"
LANE_KEY_BY_ID["T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY"] = "ding_alternate_public_dataset_discovery_boundary"
LANE_KEY_BY_ID["T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION"] = "calorine_zenodo_nep_bte_numeric_reproduction"
LANE_KEY_BY_ID["T13_CALORINE_FULL_LBTE_NUMERICAL_STABILITY_BOUNDARY"] = "calorine_full_lbte_numerical_stability_boundary"
LANE_KEY_BY_ID["T13_CALORINE_ISOTOPE_MASS_SENSITIVITY"] = "calorine_isotope_mass_sensitivity"
LANE_KEY_BY_ID["T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION"] = "calorine_state_uncertainty_decomposition"
LANE_KEY_BY_ID["T13_CALORINE_C_SRC_EQUILIBRIUM_CROSSCHECK"] = "calorine_csrc_equilibrium_crosscheck"
LANE_KEY_BY_ID["T13_FIGSHARE_DFT_FORCE_DATA_BOUNDARY"] = "figshare_dft_force_data_boundary"
LANE_KEY_BY_ID["T13_HUANG_2023_NIMS_MDR_PAYLOAD_BOUNDARY"] = "huang_2023_nims_mdr_payload_boundary"
LANE_KEY_BY_ID["T13_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY"] = "calorine_public_model_variant_boundary"
LANE_KEY_BY_ID["T13_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY"] = "calorine_nep1_backend_compatibility"
LANE_KEY_BY_ID["T13_CALORINE_LEGACY_NEP2_BACKEND_PROBE"] = "calorine_legacy_nep2_backend_probe"
LANE_KEY_BY_ID["T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION"] = "calorine_legacy_nep2_pbte_reproduction"
LANE_KEY_BY_ID["T13_CALORINE_MODEL_FORM_STATE_SPREAD_COMPARISON"] = "calorine_model_form_state_spread_comparison"
LANE_KEY_BY_ID["T13_UET_O2_FORMAL_TRANSVERSE_RESPONSE_LANE"] = "uet_o2_formal_transverse_response_lane"
LANE_KEY_BY_ID["T13_UET_O2_KINETIC_COLLISION_KERNEL_LANE"] = "uet_o2_kinetic_collision_kernel_lane"
LANE_KEY_BY_ID["T13_UET_O2_QUANTUM_COLLISION_ENHANCEMENT_LANE"] = "uet_o2_quantum_collision_enhancement_lane"
LANE_KEY_BY_ID["T13_UET_O2_CHARGE_CONSERVING_LADDER_RESPONSE_LANE"] = "uet_o2_charge_conserving_ladder_response_lane"
LANE_KEY_BY_ID["T13_UET_O2_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE"] = "uet_o2_momentum_ladder_sk_kms_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_ENERGY_MOMENTUM_CONSERVING_BS_INTERFACE_LANE"] = "uet_o2_energy_momentum_conserving_bs_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE"] = "uet_o2_exact_kinematic_2to2_transition_kernel_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONTACT_SK_TRANSITION_VERTEX_MATCH_LANE"] = "uet_o2_contact_sk_transition_vertex_match_lane"
LANE_KEY_BY_ID["T13_UET_O2_CHARGED_CURRENT_CORRELATOR_LANE"] = "uet_o2_charged_current_correlator_lane"
LANE_KEY_BY_ID["T13_UET_O2_TREE_LEVEL_CHARGED_WARD_VERTEX_LANE"] = "uet_o2_tree_level_charged_ward_vertex_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE"] = "uet_o2_conservative_continuum_collocation_lane"
LANE_KEY_BY_ID["T13_UET_O2_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE"] = "uet_o2_tree_level_bs_sk_match_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONTINUUM_LIMIT_CURRENT_SCHEME_NO_GO"] = "continuum_limit_current_scheme_no_go"
LANE_KEY_BY_ID["T13_UET_O2_ONE_LOOP_VERTEX_UV_BOUNDARY"] = "uet_o2_one_loop_vertex_uv_boundary"
LANE_KEY_BY_ID["T13_UET_O2_RENORMALIZED_VERTEX_SCHEME"] = "uet_o2_renormalized_vertex_scheme"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_DENSITY_CHARGED_VERTEX_SCHEME"] = "uet_o2_finite_density_charged_vertex_scheme"
LANE_KEY_BY_ID["T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE"] = "uet_o2_interacting_sk_kms_action_interface"
LANE_KEY_BY_ID["T13_UET_O2_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE"] = "uet_o2_nonlocal_sk_kms_memory_kernel_lane"
LANE_KEY_BY_ID["T13_UET_O2_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO"] = "uet_o2_one_loop_retarded_self_energy_no_go"
LANE_KEY_BY_ID["T13_UET_O2_TWO_LOOP_SUNSET_CUT_LANE"] = "uet_o2_two_loop_sunset_cut_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE"] = "uet_o2_finite_channel_entropy_balance_lane"
LANE_KEY_BY_ID["T13_UET_O2_COLLISIONLESS_KUBO_NO_GO"] = "uet_o2_collisionless_kubo_no_go"
LANE_KEY_BY_ID["T13_UET_O2_FORMAL_TWO_SECTOR_THERMODYNAMIC_LANE"] = "uet_o2_formal_two_sector_thermodynamic_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE"] = "uet_o2_finite_t_two_fluid_static_response_lane"
LANE_KEY_BY_ID["T13_UET_O2_THERMODYNAMIC_NORMAL_COMPONENT_LANE"] = "uet_o2_thermodynamic_normal_component_lane"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_DISSIPATIVE_TRANSPORT_IDENTIFIABILITY_NO_GO"] = "condensed_dissipative_transport_identifiability_no_go"
LANE_KEY_BY_ID["T13_UET_O2_CONDENSED_RETARDED_DISSIPATION_NO_GO"] = "uet_o2_condensed_retarded_dissipation_no_go"
def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()
LANE_KEY_BY_ID["T13_UET_O2_CONTINUUM_SUNSET_CUT_LANE"] = "uet_o2_continuum_sunset_cut_lane"
LANE_KEY_BY_ID["T13_UET_O2_SUBTRACTED_SUNSET_DISPERSION_INTERFACE_LANE"] = "uet_o2_subtracted_sunset_dispersion_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_ACTION_NORMALIZED_SUNSET_SPECTRAL_INTERFACE_LANE"] = "uet_o2_action_normalized_sunset_spectral_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_ACTION_MATCHED_ZERO_ETA_SUNSET_SUBTRACTION_INTERFACE_LANE"] = "uet_o2_action_matched_zero_eta_sunset_subtraction_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_ACTION_1PI_SUNSET_TENSOR_INTERFACE_LANE"] = "uet_o2_action_1pi_sunset_tensor_interface_lane"
LANE_KEY_BY_ID["T13_UET_O2_EUCLIDEAN_1PI_SUNSET_REGULATED_SUBTRACTION_LANE"] = "uet_o2_euclidean_1pi_sunset_regulated_subtraction_lane"
LANE_KEY_BY_ID["T13_UET_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE"] = "uet_o2_vacuum_retarded_sunset_discontinuity_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE"] = "uet_o2_finite_t_three_body_sunset_sk_kms_lane"

LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SCATTERING_SUNSET_SK_KMS_LANE"] = "uet_o2_finite_t_scattering_sunset_sk_kms_lane"

LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE"] = "uet_o2_finite_t_declared_full_sunset_sk_kms_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE"] = "uet_o2_finite_t_signed_cut_kinematic_taxonomy_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE"] = "uet_o2_finite_t_sunset_cut_multiplicity_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE"] = "uet_o2_finite_t_all_onshell_cut_spectral_response_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE"] = "uet_o2_finite_t_declared_channel_retarded_advanced_keldysh_1pi_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_1PI_LANE"] = "uet_o2_finite_t_offshell_threshold_crossing_1pi_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE"] = "uet_o2_finite_t_all_22_permutation_identity_lane"
LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_OFFSHELL_1PI_FORMAL_LANE"] = "uet_o2_finite_t_offshell_1pi_formal_lane"

LANE_KEY_BY_ID["T13_UET_O2_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE"] = "uet_o2_on_shell_sunset_collision_width_lane"

LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE"] = "uet_o2_finite_t_sunset_vacuum_match_lane"

LANE_KEY_BY_ID["T13_UET_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO"] = "uet_o2_finite_t_sunset_renormalization_identifiability_no_go"

LANE_KEY_BY_ID["T13_UET_O2_PHYSICAL_RENORMALIZATION_CONDITION_CONTRACT"] = "uet_o2_physical_renormalization_condition_contract"
LANE_KEY_BY_ID["T13_UET_O2_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE"] = "uet_o2_covariant_entropy_heat_flux_balance_lane"
LANE_KEY_BY_ID["T13_UET_O2_ACTION_THERMAL_STIFFNESS_BETA_LANE"] = "uet_o2_action_thermal_stiffness_beta_lane"
LANE_KEY_BY_ID["T13_UET_O2_ACTION_NATURAL_PHI_THERMAL_BRIDGE_LANE"] = "uet_o2_action_natural_phi_thermal_bridge_lane"
LANE_KEY_BY_ID["T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY"] = "transport_kms_entropy_status_boundary"
LANE_KEY_BY_ID["T13_JUN_FINAL_SOURCE_BOUNDARY"] = "jun_final_source_boundary"
LANE_KEY_BY_ID["T13_HONG_FINAL_SOURCE_BOUNDARY"] = "hong_final_source_boundary"
LANE_KEY_BY_ID["T13_PETERSON_SOURCE_IDENTITY_NO_GO"] = "peterson_source_identity_no_go"
LANE_KEY_BY_ID["T13_THERMAL_BRIDGE_SCALE_DEPENDENCY_NO_GO"] = "thermal_bridge_scale_dependency_no_go"
LANE_KEY_BY_ID["T13_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY"] = "aist_graphite_source_route_boundary"
LANE_KEY_BY_ID["T13_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY"] = "nist_srm_3600_heat_capacity_comparator_boundary"
LANE_KEY_BY_ID["T13_PEREZ_CASTANEDA_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY"] = "perez_castaneda_hopg_specific_heat_source_boundary"
LANE_KEY_BY_ID["T13_QH15_GRAPHITE_CV_COMPARATOR_BOUNDARY"] = "qh15_graphite_cv_comparator_boundary"
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(rel_path: str) -> tuple[Path, dict[str, Any]]:
    path = ROOT / rel_path
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return path, value


def evidence(rel_path: str, value: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / rel_path
    return {
        "path": rel_path,
        "sha256": sha256(path),
        "summary": summary,
    }


def main() -> int:
    branch_path, branch = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json"
    )
    source_path, source_gate = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/thermal_parameter_provenance_gate.json"
    )
    constraint_path, constraint = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/0_13_core_thermodynamic_constraint_gate.json"
    )
    calibration_path, calibration = load("docs/core/artifacts/thermal_dimensional_calibration_contract.json")
    transport_path, transport = load("docs/core/artifacts/covariant_superfluid_transport_contract.json")
    transport_verification_path, transport_verification = load(
        "docs/core/artifacts/covariant_superfluid_transport_verification.json"
    )
    entropy_heat_flux_path, entropy_heat_flux = load(
        "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json"
    )
    on_shell_sunset_width_path, on_shell_sunset_width = load(
        "docs/core/artifacts/t13_uet_o2_on_shell_sunset_width_audit.json"
    )
    contact_sk_transition_path, contact_sk_transition = load(
        "docs/core/artifacts/t13_uet_o2_contact_sk_transition_vertex_match_audit.json"
    )
    charged_current_correlator_path, charged_current_correlator = load(
        "docs/core/artifacts/t13_uet_o2_charged_current_correlator_audit.json"
    )
    tree_level_charged_ward_path, tree_level_charged_ward = load(
        "docs/core/artifacts/t13_uet_o2_tree_level_charged_ward_vertex_audit.json"
    )
    action_beta_path, action_beta = load(
        "docs/core/artifacts/t13_uet_o2_action_thermal_stiffness_beta_audit.json"
    )
    natural_bridge_path, natural_bridge = load(
        "docs/core/artifacts/t13_uet_o2_action_thermal_observable_bridge_audit.json"
    )
    eos_path, eos = load("docs/core/artifacts/o2_finite_density_eos_verification.json")
    causal_path, causal = load("docs/core/artifacts/matter_space_causal_cone_compatibility.json")
    source_package_path, source_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"
    )
    ding_source_mapping_path, ding_source_mapping = load(
        "docs/core/artifacts/ding_2022_source_mapping_audit.json"
    )
    alpha_search_path, alpha_search = load(
        "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json"
    )
    ding_c_src_boundary_path, ding_c_src_boundary = load(
        "docs/core/artifacts/t13_ding_c_src_independent_reproduction_boundary_audit.json"
    )
    ding_public_supplementary_path, ding_public_supplementary = load(
        "docs/core/artifacts/t13_ding_public_supplementary_payload_boundary_audit.json"
    )
    ding_experimental_heating_path, ding_experimental_heating = load(
        "docs/core/artifacts/t13_ding_experimental_heating_input_boundary_audit.json"
    )
    ding_2017_acs_supplementary_path, ding_2017_acs_supplementary = load(
        "docs/core/artifacts/t13_ding_2017_acs_supplementary_payload_boundary_audit.json"
    )
    phi_si_anchor_boundary_path, phi_si_anchor_boundary = load(
        "docs/core/artifacts/t13_phi_si_anchor_public_source_boundary_audit.json"
    )
    spectral_csrc_path, spectral_csrc = load(
        "docs/core/artifacts/t13_mp48_spectral_csrc_reproduction_audit.json"
    )
    force_constant_path, force_constant = load(
        "docs/core/artifacts/t13_mp48_force_constant_harmonic_reconstruction_audit.json"
    )
    mesh_convergence_path, mesh_convergence = load(
        "docs/core/artifacts/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"
    )
    huang_supplementary_path, huang_supplementary = load(
        "docs/core/artifacts/t13_huang_2023_supplementary_payload_boundary_audit.json"
    )
    huberman_public_pbte_path, huberman_public_pbte = load(
        "docs/core/artifacts/t13_huberman_2019_public_pbte_boundary_audit.json"
    )
    nist_density_path, nist_density = load(
        "docs/core/artifacts/t13_nist_axm5q1_density_source_boundary_audit.json"
    )
    nist_alpha_v_path, nist_alpha_v = load(
        "docs/core/artifacts/t13_nist_graphite_alpha_v_source_boundary_audit.json"
    )
    elastic_bulk_path, elastic_bulk = load(
        "docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json"
    )
    isothermal_kt_path, isothermal_kt = load(
        "docs/core/artifacts/t13_graphite_isothermal_kt_source_audit.json"
    )
    tpg_alpha_v_path, tpg_alpha_v = load(
        "docs/core/artifacts/t13_tpg_anisotropic_alpha_v_source_audit.json"
    )
    natural_alpha_v_path, natural_alpha_v = load(
        "docs/core/artifacts/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json"
    )
    bipm_specific_heat_path, bipm_specific_heat = load(
        "docs/core/artifacts/t13_bipm_specific_heat_source_audit.json"
    )
    bipm_package_path, bipm_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bipm_2006_01_graphite_specific_heat_source_package.json"
    )
    iaea_graphite_cv_path, iaea_graphite_cv = load(
        "docs/core/artifacts/t13_iaea_graphite_constant_volume_source_audit.json"
    )
    iaea_graphite_cv_package_path, iaea_graphite_cv_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_handbook_constant_volume_source_package.json"
    )
    cv_uncertainty_path, cv_uncertainty = load(
        "docs/core/artifacts/t13_iaea_cv_uncertainty_boundary_audit.json"
    )
    cv_uncertainty_package_path, cv_uncertainty_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_graphite_cv_uncertainty_boundary_source_package.json"
    )
    iaea_gr280_path, iaea_gr280 = load(
        "docs/core/artifacts/t13_iaea_gr280_same_state_cp_source_audit.json"
    )
    iaea_gr280_package_path, iaea_gr280_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_gr280_same_state_cp_source_package.json"
    )
    farooqui_source_path, farooqui_source = load(
        "docs/core/artifacts/t13_farooqui_ig210_thermophysical_source_audit.json"
    )
    farooqui_package_path, farooqui_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/farooqui_2022_ig210_thermophysical_source_package.json"
    )
    phonix_path, phonix = load(
        "docs/core/artifacts/t13_phonix_mp47_graphite_comparator_audit.json"
    )
    oxford_numeric_path, oxford_numeric = load(
        "docs/core/artifacts/t13_oxford_tgs_numeric_rows_audit.json"
    )
    desorbo_ceylon_path, desorbo_ceylon = load(
        "docs/core/artifacts/t13_desorbo_ceylon_graphite_cp_audit.json"
    )
    desorbo_ceylon_package_path, desorbo_ceylon_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/desorbo_1955_ceylon_graphite_cp_source_package.json"
    )
    finite_qp_eos_path, finite_qp_eos = load(
        "docs/core/artifacts/t13_uet_o2_finite_temperature_quasiparticle_eos_audit.json"
    )
    equilibrium_kms_path, equilibrium_kms = load(
        "docs/core/artifacts/t13_uet_o2_equilibrium_kms_audit.json"
    )
    graphite_green_kubo_path, graphite_green_kubo = load(
        "docs/core/artifacts/t13_graphite_green_kubo_source_boundary_audit.json"
    )
    material_boundary_path, material_boundary = load(
        "docs/core/artifacts/t13_ding_material_regime_boundary_audit.json"
    )
    material_boundary_package_path, material_boundary_package = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_graphite_material_regime_boundary_source_package.json"
    )
    independent_csrc_acceptance_path, independent_csrc_acceptance = load(
        "docs/core/artifacts/t13_independent_csrc_acceptance_contract.json"
    )
    calorine_candidate_path, calorine_candidate = load(
        "docs/core/artifacts/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"
    )
    calorine_reproduction_path, calorine_reproduction = load(
        "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
    )
    calorine_model_form_state_spread_path, calorine_model_form_state_spread = load(
        "docs/core/artifacts/t13_calorine_model_form_state_spread_comparison_audit.json"
    )
    calorine_full_lbte_path, calorine_full_lbte = load(
        "docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json"
    )
    calorine_isotope_path, calorine_isotope = load(
        "docs/core/artifacts/t13_calorine_isotope_mass_sensitivity_audit.json"
    )
    calorine_uncertainty_path, calorine_uncertainty = load(
        "docs/core/artifacts/t13_calorine_state_uncertainty_decomposition_audit.json"
    )
    nims_graphite_route_path, nims_graphite_route = load(
        "docs/core/artifacts/t13_nims_graphite_ltc_route_no_go.json"
    )
    srm3600_path, srm3600 = load(
        "docs/core/artifacts/t13_nist_srm_3600_heat_capacity_boundary_audit.json"
    )
    perez_hopg_path, perez_hopg = load(
        "docs/core/artifacts/t13_perez_castaneda_hopg_source_boundary_audit.json"
    )
    holdout_audit_path, holdout_audit = load(
        "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json"
    )
    phi_e_comparator_path, phi_e_comparator = load(
        "docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json"
    )
    no_go_path, no_go = load("docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json")
    telegraph_path, telegraph = load("docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json")
    coupled_path, coupled = load("docs/core/artifacts/matter_space_flux_phi_coupled_verification.json")

    selected = branch.get("selected_causal_branch", {})
    full = branch.get("full_candidate_branch", {})
    measurement = branch.get("measurement_contract", {})
    source_contract = branch.get("source_contract", {})
    source_policy = source_gate.get("current_lane", {})
    constraint_gates = constraint.get("gates", {})
    source_status = source_contract.get("package", {}).get("status")
    alpha_status = measurement.get("alpha_Phi_K_status")
    holdout_controls = holdout_audit.get("audit", {})
    holdout_not_consumed = (
        holdout_audit.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY"
        and holdout_controls.get("numeric_payload_consumed") is False
        and holdout_controls.get("numeric_rows_consumed") is False
        and holdout_controls.get("source_data_payload_observed") is False
        and holdout_controls.get("audit_path_read_source_data") is False
        and holdout_controls.get("used_for_fit") is False
        and holdout_controls.get("used_for_tuning") is False
        and holdout_controls.get("used_for_calibration") is False
        and holdout_controls.get("used_for_threshold_adjustment") is False
        and holdout_controls.get("locked_holdout_remains_unconsumed") is True
    )

    causal_no_go_evidence = bool(
        causal.get("continuum_diagnostic", {})
        .get("cattaneo_extension", {})
        .get("high_k_group_speed_is_unbounded")
    )
    formal_no_go_recorded = no_go.get("status") == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS"
    named_finite_cone_branch_pass = (
        telegraph.get("status") == "PASS"
        and telegraph.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
    )
    named_coupled_branch_pass = (
        coupled.get("status") == "PASS"
        and coupled.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE"
    )
    causal_lane_pass = formal_no_go_recorded and named_finite_cone_branch_pass and named_coupled_branch_pass
    full_candidate_pass = (
        full.get("gate") == "PASS"
        and float(full.get("prearrival_leakage_fraction", 1.0)) <= float(full.get("threshold", 1.0e-6))
    )
    branch_pass = (
        float(selected.get("prearrival_leakage_fraction", 1.0)) <= float(selected.get("threshold", 1.0e-6))
        and float(selected.get("arrival_target_abs", 0.0)) > 0.0
    )
    normalized_source_ready = bool(
        source_contract.get("normalized_comparison_route_ready")
        or ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready", False)
    )
    raw_author_source_ready = bool(
        source_contract.get("raw_author_numeric_route_ready")
        or ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present", False)
    )
    independent_reproduction_ready = bool(
        independent_csrc_acceptance.get("acceptance", {}).get("accepted_for_full_topic13", False)
    )
    # A figure-derived normalized route is sufficient for the comparison
    # lane, but full Topic 13 still requires raw-author C_src or an
    # accepted independent reproduction package.
    source_ready = raw_author_source_ready or independent_reproduction_ready
    alpha_ready = alpha_status in {"DERIVED", "EXTERNAL_INPUT"}
    action_natural_bridge_pass = (
        natural_bridge.get("status")
        == "PASS_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE"
        and natural_bridge.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
    )
    # A natural-unit lane closure is not physical bridge closure.
    bridge_derived = constraint_gates.get("uet_bridge_derivation_gate", {}).get("status") == "PASS"
    eos_transport_entropy_ready = (
        constraint_gates.get("core_eos_transport_entropy_gate", {}).get("status") == "PASS"
        and transport.get("status") == "PASS"
        and transport_verification.get("physical_coefficient_evidence") not in {"BLOCKED_NOT_PROVIDED", "OPEN"}
    )
    dimensional_map_ready = bool(calibration.get("open_calibration_record", {}).get("physical_mapping_ready"))
    source_fit_forbidden = bool(source_gate.get("policy", {}).get("holdout_may_be_used_for_tuning") is False)

    previous_gate = json.loads(OUT.read_text(encoding="utf-8-sig")) if OUT.is_file() else {}
    previous_transport = previous_gate.get("verification_status", {}).get("eos_transport_kms_entropy", {})
    preserved_lane_integrations = {
        key: value
        for key, value in previous_transport.items()
        if key not in {
            "status",
            "constraint_gate_status",
            "transport_contract_status",
            "physical_coefficient_evidence",
            "finite_temperature_completion",
            "full_SK_KMS_completion",
            "controlling_blocker",
        }
    }
    discovered_lane_integrations = {}
    for artifact_root in (ROOT / "docs/core/artifacts", ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts"):
        for artifact_path in sorted(artifact_root.rglob("*.json")):
            try:
                candidate = json.loads(artifact_path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                continue
            major = candidate.get("major_result")
            if not isinstance(major, dict):
                continue
            result_id = major.get("major_result_id")
            if result_id not in LANE_KEY_BY_ID:
                continue
            key = LANE_KEY_BY_ID[result_id]
            # Keep lane-specific diagnostics instead of reducing the record
            # to a status-only summary.
            lane_record = {
                field: value
                for field, value in candidate.items()
                if field not in {"schema_version", "artifact", "generated_at", "major_result", "evidence_artifacts"}
            }
            lane_record.update({
                "major_result_id": result_id,
                "status": candidate.get("status", major.get("verification_status", "OPEN")),
                "closure_level": major.get("closure_level", "OPEN"),
                "data_role": major.get("data_role", "artifact-reported"),
                "audit": {
                    "path": rel(artifact_path),
                    "sha256": sha256(artifact_path),
                    "summary": {
                        "status": candidate.get("status"),
                        "major_result_id": result_id,
                        "closure_level": major.get("closure_level"),
                    },
                },
                "controlling_blocker": candidate.get("controlling_blocker", major.get("open_blockers", [None])[0]),
                "open_blockers": major.get("open_blockers", candidate.get("open_blockers", [])),
                "claim_boundary": major.get("claim_boundary", "artifact-reported boundary"),
            })
            discovered_lane_integrations[key] = lane_record
    previous_major = previous_gate.get("major_result", {})

    normalized_beta_correspondence_open = (
        not bridge_derived
        and action_natural_bridge_pass
        and discovered_lane_integrations.get(
            "beta_action_normalized_correspondence_no_go", {}
        ).get("closure_level")
        == "CLOSED_AS_NO_GO"
    )
    bridge_controlling_blocker = (
        None
        if bridge_derived
        else (
            "normalized_beta_and_SI_scale_correspondence_missing"
            if normalized_beta_correspondence_open
            else "non_circular_uet_bridge_and_beta_derivation_missing"
        )
    )

    gates = {
        "causal_full_candidate_or_formal_no_go_branch": {
            # The named lane may close without promoting the original
            # full-candidate causal gate.
            "status": "PASS" if full_candidate_pass else "BLOCKED",
            "status_role": "full_candidate_readiness_gate",
            "baseline_status": "PASS" if full_candidate_pass else "BLOCKED",
            "baseline_controlling_blocker": (
                None if full_candidate_pass else "original_conserved_c_gradient_baseline_blocked"
            ),
            "lane_status": "PASS" if causal_lane_pass else "BLOCKED",
            "lane_status_role": "scoped_named_branch_lane",
            "lane_closure_level": "CLOSED_FOR_LANE" if causal_lane_pass else "OPEN",
            "structural_question_closure": (
                "CLOSED_AS_NO_GO" if causal_lane_pass else "OPEN"
            ),
            "formal_no_go_closure": "CLOSED_AS_NO_GO" if formal_no_go_recorded else "OPEN",
            "full_candidate_pass": full_candidate_pass,
            "selected_reference_pass": branch_pass,
            "formal_no_go_recorded": formal_no_go_recorded,
            "structural_no_go_evidence_present": causal_no_go_evidence and formal_no_go_recorded,
            "threshold": 1.0e-6,
            "no_clipping_or_padding": True,
            "named_finite_cone_branch_pass": named_finite_cone_branch_pass,
            "named_finite_cone_branch_closure_level": telegraph.get("major_result", {}).get("closure_level", "OPEN"),
            "named_coupled_branch_pass": named_coupled_branch_pass,
            "named_coupled_branch_closure_level": coupled.get("major_result", {}).get("closure_level", "OPEN"),
            "no_go_scope": no_go.get("proof_scope"),
            "no_go_artifact": {"path": rel(no_go_path), "sha256": sha256(no_go_path)},
            "baseline_replaced": False,
            "full_core_unlock": False,
            "controlling_blocker": "original_conserved_c_gradient_baseline_blocked" if causal_lane_pass else "formal_conserved_C_no_go_or_explicit_regularization_missing",
        },
        "source_package": {
            "status": "PASS" if source_ready else "BLOCKED",
            "source_status": source_status,
            "source_ready_for_full_closure": raw_author_source_ready,
            "normalized_comparison_route_ready": normalized_source_ready,
            "raw_author_C_src_route_ready": raw_author_source_ready,
            "independent_reproduction_route_ready": independent_reproduction_ready,
            "independent_reproduction_acceptance_status": independent_csrc_acceptance.get("acceptance", {}).get("status"),
            "independent_reproduction_acceptance_artifact": {"path": rel(independent_csrc_acceptance_path), "sha256": sha256(independent_csrc_acceptance_path)},
            "provisional_source_present": bool(source_contract.get("provisional_source_present")),
            "raw_author_numeric_source_present": bool(
                ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present", False)
            ),
            "figure_derived_numeric_route_ready": bool(
                ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready", False)
            ),
            "numeric_fitting_allowed": bool(source_contract.get("numeric_fitting_allowed")),
            "raw_author_C_src_controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" if not raw_author_source_ready else None,
            "controlling_blocker": None if source_ready else "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        },
        "alpha_Phi_K": {
            "status": "PASS" if alpha_ready else "BLOCKED",
            "status_recorded": alpha_status,
            "independent_calibration_or_derivation": alpha_ready,
            "uncertainty_status": measurement.get("uncertainty_status"),
            "candidate_search_status": alpha_search.get("status"),
            "candidate_count": alpha_search.get("candidate_count"),
            "eligible_candidate_count": alpha_search.get("eligible_candidate_count"),
            "candidate_search_holdout_accessed": alpha_search.get("holdout_accessed"),
            "candidate_search_fit_performed": alpha_search.get("target_fit_performed"),
            "candidate_search_artifact": {"path": rel(alpha_search_path), "sha256": sha256(alpha_search_path)},
            "controlling_blocker": "alpha_Phi_K_independent_calibration_missing" if not alpha_ready else None,
        },
        "non_circular_bridge": {
            # The action-derived natural map closes the formal bridge lane.
            # Its SI/Phi normalization remains a separate physical gate.
            "status": "PASS" if bridge_derived else "BLOCKED",
            "constraint_gate_status": constraint_gates.get("uet_bridge_derivation_gate", {}).get("status"),
            "landauer_non_derivation_gate": constraint_gates.get("landauer_coefficient_non_derivation_gate", {}).get("status"),
            "formal_boundary_status": discovered_lane_integrations.get("formal_non_circular_bridge_boundary", {}).get("status", "OPEN"),
            "formal_boundary_closure_level": discovered_lane_integrations.get("formal_non_circular_bridge_boundary", {}).get("closure_level", "OPEN"),
            "formal_boundary_audit": discovered_lane_integrations.get("formal_non_circular_bridge_boundary", {}).get("audit"),
            "action_natural_bridge_status": natural_bridge.get("status"),
            "action_natural_bridge_closure_level": natural_bridge.get("major_result", {}).get("closure_level"),
            "action_natural_bridge_audit": {"path": rel(natural_bridge_path), "sha256": sha256(natural_bridge_path)},
            "natural_action_derivation_status": "PASS" if action_natural_bridge_pass else "BLOCKED",
            "physical_dimensional_bridge_status": "BLOCKED_PHI_SI_ANCHOR_OR_ALPHA_OPEN",
            "physical_derivation_status": "PASS_NATURAL_UNIT_ONLY" if action_natural_bridge_pass else "BLOCKED",
            "physical_derivation_controlling_blocker": bridge_controlling_blocker,
            "controlling_blocker": bridge_controlling_blocker,
        },
        "eos_transport_kms_entropy": {
            "status": "PASS" if eos_transport_entropy_ready else "BLOCKED",
            "constraint_gate_status": constraint_gates.get("core_eos_transport_entropy_gate", {}).get("status"),
            "transport_contract_status": transport.get("status"),
            "physical_coefficient_evidence": transport_verification.get("physical_coefficient_evidence"),
            "finite_temperature_completion": transport_verification.get("finite_temperature_two_fluid_completion"),
            "full_SK_KMS_completion": transport_verification.get("full_SK_KMS_completion"),
            "controlling_blocker": "eos_transport_kms_entropy_completion_missing" if not eos_transport_entropy_ready else None,
        },
        "dimensional_observable_map": {
            "status": "PASS" if dimensional_map_ready else "BLOCKED",
            "relation": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "physical_mapping_ready": dimensional_map_ready,
            "calibration_status": calibration.get("claim_status"),
            "controlling_blocker": "dimensional_phi_to_thermal_observable_map_missing" if not dimensional_map_ready else None,
        },
        "holdout_integrity": {
            "status": "PASS" if holdout_not_consumed and source_fit_forbidden else "BLOCKED",
            "holdout_consumed": not holdout_not_consumed,
            "numeric_fitting_disabled": source_fit_forbidden,
            "metadata_only_observed": holdout_controls.get("metadata_only_observed"),
            "numeric_payload_consumed": holdout_controls.get("numeric_payload_consumed"),
            "source_data_payload_observed": holdout_controls.get("source_data_payload_observed"),
            "used_for_fit": holdout_controls.get("used_for_fit"),
            "used_for_tuning": holdout_controls.get("used_for_tuning"),
            "used_for_calibration": holdout_controls.get("used_for_calibration"),
            "used_for_threshold_adjustment": holdout_controls.get("used_for_threshold_adjustment"),
            "canonical_access_audit": {"path": rel(holdout_audit_path), "sha256": sha256(holdout_audit_path)},
            "xie_2026_policy": source_contract.get("xie_2026_policy"),
            "controlling_blocker": None if holdout_not_consumed and source_fit_forbidden else "xie_2026_holdout_data_consumption_or_fit_audit_failed",
        },
    }

    all_core_ready = all(item.get("status") == "PASS" for item in gates.values())
    raw_blockers = [
        item["controlling_blocker"]
        for item in gates.values()
        if item.get("status") == "BLOCKED" and item.get("controlling_blocker")
    ]
    # The legacy baseline remains blocked, but a recorded scoped no-go and
    # named causal branches close the structural question for the lane.
    blockers = [
        blocker
        for blocker in raw_blockers
        if not (
            blocker == "original_conserved_c_gradient_baseline_blocked"
            and causal_lane_pass
        )
    ]
    if transport_verification.get("physical_coefficient_evidence") in {"BLOCKED_NOT_PROVIDED", "OPEN"}:
        blockers.append("physical_Kubo_coefficient_record_missing")
    primary_blocker = (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
        if not alpha_ready
        else (blockers[0] if blockers else None)
    )
    artifact = {
        "schema_version": "topic13-full-thermodynamic-bridge-core-ready-v1",
        "artifact": "topic13_full_thermodynamic_bridge_core_ready_gate",
        "generated_at": date.today().isoformat(),
        "status": "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY" if all_core_ready else "BLOCKED_OPEN_T13_FULL_BRIDGE",
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_FULL_THERMODYNAMIC_BRIDGE",
            "closure_level": "CLOSED_FOR_CORE" if all_core_ready else "PARTIAL",
            "what_is_closed": [
                "standard TTG normalized measurement operator",
                "normalized Phi response operator",
                "frozen-C compact-support control branch",
                "constraint-only Landauer and standard thermodynamic identities",
            ],
            "what_remains_open": blockers,
            "baseline_open_items": (
                [
                    "original conserved-C local-gradient candidate remains BLOCKED; the named no-go and finite-cone branches are separate lanes",
                ]
                if causal_lane_pass
                else []
            ),
            "dependency_unlocked": "Gravity/GR remains blocked until this full bridge and Core curved 3+1 gates pass",
        },
        "equation_or_mapping": {
            "standard": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            "uet_normalized": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
        },
        "units": {
            "y_TTG": "dimensionless",
            "y_TTG_UET": "dimensionless",
            "alpha_Phi_K": "K per normalized Phi; open until independent record exists",
        },
        "derivation_class": "standard observable definition plus blocked UET bridge derivation",
        "observable": "source-defined quasi-temperature difference and normalized UET response",
        "data_role": {
            "source_package": source_status,
            "calibration": source_policy.get("alpha_Phi_K_status"),
            "holdout": "Xie 2026 metadata-only locked holdout",
        },
        "verification_status": gates,
        "controlling_blocker": primary_blocker,
        "next_action": "Acquire an independent base-Phi SI energy/observable anchor or paired Phi/SI record; obtain Ding numeric C_src(T) or an accepted independent reproduction; source-lock beta_T13 and one state-matched physical Kubo coefficient; then complete EOS/transport/KMS/entropy gates. The original conserved-C question is closed only as a scoped no-go and remains blocked as the original baseline.",
        "claim_boundary": "Full Topic 13 is not Core-ready; current evidence supports normalized/internal controls and constraint exports only. No temperature prediction, external validation, or global UET closure is claimed.",
        "evidence_artifacts": [
            evidence(rel(branch_path), branch, {"status": branch.get("status"), "controlling_blocker": branch.get("controlling_blocker")}),
            evidence(rel(source_path), source_gate, {"alpha_Phi_K_status": source_policy.get("alpha_Phi_K_status"), "holdout_consumed": source_policy.get("2026_graphite_holdout_consumed")}),
            evidence(rel(constraint_path), constraint, {"status": constraint.get("status"), "controlling_blocker": constraint.get("controlling_blocker")}),
            evidence(rel(calibration_path), calibration, {"audit_status": calibration.get("audit_status"), "claim_status": calibration.get("claim_status")}),
            evidence(rel(transport_path), transport, {"status": transport.get("status"), "next_controller": transport.get("next_controller")}),
            evidence(rel(transport_verification_path), transport_verification, {"physical_coefficient_evidence": transport_verification.get("physical_coefficient_evidence"), "full_SK_KMS_completion": transport_verification.get("full_SK_KMS_completion")}),
            evidence(rel(entropy_heat_flux_path), entropy_heat_flux, {"status": entropy_heat_flux.get("status"), "closure_level": entropy_heat_flux.get("major_result", {}).get("closure_level"), "kappa_natural": entropy_heat_flux.get("state", {}).get("kappa_natural"), "full_core_unlock": entropy_heat_flux.get("full_core_unlock")}),
            evidence(rel(on_shell_sunset_width_path), on_shell_sunset_width, {"status": on_shell_sunset_width.get("status"), "closure_level": on_shell_sunset_width.get("major_result", {}).get("closure_level"), "combined_collision_width": on_shell_sunset_width.get("state", {}).get("reference", {}).get("combined_collision_width"), "cut_convergence_bound": on_shell_sunset_width.get("state", {}).get("reference", {}).get("cut_convergence_bound")}),
            evidence(rel(contact_sk_transition_path), contact_sk_transition, {"status": contact_sk_transition.get("status"), "closure_level": contact_sk_transition.get("major_result", {}).get("closure_level"), "cross_section_match_residual": contact_sk_transition.get("state", {}).get("reference", {}).get("cross_section_match_residual"), "max_channel_detailed_balance_residual": contact_sk_transition.get("state", {}).get("reference", {}).get("max_channel_detailed_balance_residual")}),
            evidence(rel(charged_current_correlator_path), charged_current_correlator, {"status": charged_current_correlator.get("status"), "closure_level": charged_current_correlator.get("major_result", {}).get("closure_level"), "kms_ratio_max_residual": charged_current_correlator.get("state", {}).get("reference", {}).get("kms_ratio_max_residual"), "fdt_max_residual": charged_current_correlator.get("state", {}).get("reference", {}).get("fdt_max_residual")}),
            evidence(rel(action_beta_path), action_beta, {"status": action_beta.get("status"), "closure_level": action_beta.get("major_result", {}).get("closure_level"), "beta_phi_natural": action_beta.get("state", {}).get("beta_phi_natural"), "normalized_beta_T13_emitted": action_beta.get("state", {}).get("normalized_beta_T13_emitted"), "full_core_unlock": action_beta.get("full_core_unlock")}),
            evidence(rel(natural_bridge_path), natural_bridge, {"status": natural_bridge.get("status"), "closure_level": natural_bridge.get("major_result", {}).get("closure_level"), "alpha_phi_temperature_natural": natural_bridge.get("state", {}).get("alpha_phi_temperature_natural"), "numeric_alpha_phi_k_emitted": natural_bridge.get("state", {}).get("numeric_alpha_phi_k_emitted"), "full_core_unlock": natural_bridge.get("full_core_unlock")}),
            evidence(rel(eos_path), eos, {"audit_status": eos.get("audit_status"), "evidence_status": eos.get("evidence_status")}),
            evidence(rel(causal_path), causal, {"audit_status": causal.get("audit_status"), "structural_blocker": causal.get("structural_blocker")}),
            evidence(rel(source_package_path), source_package, {"status": source_package.get("status")}),
            evidence(rel(farooqui_source_path), farooqui_source, {
                "status": farooqui_source.get("status"),
                "closure_level": farooqui_source.get("major_result", {}).get("closure_level"),
                "density_uncertainty_locked": farooqui_source.get("row_summary", {}).get("density_uncertainty_locked"),
                "specific_heat_uncertainty_locked": farooqui_source.get("row_summary", {}).get("specific_heat_uncertainty_locked"),
                "K_T_present": farooqui_source.get("row_summary", {}).get("K_T_present"),
            }),
            evidence(rel(farooqui_package_path), farooqui_package, {
                "status": farooqui_package.get("status"),
                "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
                "raw_sha256": farooqui_package.get("source", {}).get("local_raw_sha256"),
                "same_state_K_T_present": farooqui_package.get("derived_comparator", {}).get("same_state_K_T_present"),
                "Ding_TTG_material_match_closed": farooqui_package.get("derived_comparator", {}).get("Ding_TTG_material_match_closed"),
            }),            evidence(rel(ding_source_mapping_path), ding_source_mapping, {
                "status": ding_source_mapping.get("status"),
                "raw_author_numeric_source_present": ding_source_mapping.get("checks", {}).get("raw_author_numeric_source_present"),
                "permitted_figure_numeric_route_ready": ding_source_mapping.get("checks", {}).get("permitted_figure_numeric_route_ready"),
            }),
            evidence(rel(ding_experimental_heating_path), ding_experimental_heating, {
                "status": ding_experimental_heating.get("status"),
                "closure_level": ding_experimental_heating.get("major_result", {}).get("closure_level"),
                "pump_fluence_J_m2": ding_experimental_heating.get("derived_records", [{}])[0].get("value_si"),
                "absorbed_energy_density_status": ding_experimental_heating.get("energy_density_contract", {}).get("absorbed_energy_density", {}).get("status"),
                "controlling_blocker": ding_experimental_heating.get("controlling_blocker"),
            }),
            evidence(rel(alpha_search_path), alpha_search, {
                "status": alpha_search.get("status"),
                "candidate_count": alpha_search.get("candidate_count"),
                "eligible_candidate_count": alpha_search.get("eligible_candidate_count"),
                "holdout_accessed": alpha_search.get("holdout_accessed"),
                "numeric_alpha_Phi_K_emitted": alpha_search.get("numeric_alpha_Phi_K_emitted"),
            }),
            evidence(rel(phi_si_anchor_boundary_path), phi_si_anchor_boundary, {
                "status": phi_si_anchor_boundary.get("status"),
                "paired_base_phi_si_record_present": phi_si_anchor_boundary.get("source_availability", {}).get("public_numeric_paired_record_present"),
                "numeric_alpha_Phi_K_present": phi_si_anchor_boundary.get("source_availability", {}).get("numeric_alpha_Phi_K_present"),
                "author_request_state": phi_si_anchor_boundary.get("source_availability", {}).get("author_request_state"),
                "controlling_blocker": phi_si_anchor_boundary.get("controlling_blocker"),
            }),
            evidence(rel(independent_csrc_acceptance_path), independent_csrc_acceptance, {
                "status": independent_csrc_acceptance.get("status"),
                "accepted_for_full_topic13": independent_reproduction_ready,
                "controlling_blocker": independent_csrc_acceptance.get("controlling_blocker"),
            }),
            evidence(rel(calorine_candidate_path), calorine_candidate, {
                "status": calorine_candidate.get("status"),
                "accepted_for_full_topic13": calorine_candidate.get("acceptance", {}).get("accepted_for_full_topic13"),
                "controlling_blocker": calorine_candidate.get("controlling_blocker"),
            }),
            evidence(rel(calorine_reproduction_path), calorine_reproduction, {
                "status": calorine_reproduction.get("status"),
                "closure_level": calorine_reproduction.get("major_result", {}).get("closure_level"),
                "accepted_for_full_topic13": calorine_reproduction.get("acceptance_for_full_topic13"),
                "latest_pair_max_relative_change": calorine_reproduction.get("reproduction", {}).get("convergence", {}).get("latest_pair", {}).get("max_relative_change"),
                "controlling_blocker": calorine_reproduction.get("controlling_blocker"),
            }),
            evidence(rel(calorine_model_form_state_spread_path), calorine_model_form_state_spread, {
                "status": calorine_model_form_state_spread.get("status"),
                "closure_level": calorine_model_form_state_spread.get("major_result", {}).get("closure_level"),
                "max_absolute_relative_spread": calorine_model_form_state_spread.get("comparison", {}).get("spread_summary", {}).get("max_absolute_relative_spread"),
                "accepted_for_full_topic13": calorine_model_form_state_spread.get("acceptance_for_full_topic13"),
                "controlling_blocker": calorine_model_form_state_spread.get("controlling_blocker"),
            }),
            evidence(rel(calorine_full_lbte_path), calorine_full_lbte, {
                "status": calorine_full_lbte.get("status"),
                "closure_level": calorine_full_lbte.get("major_result", {}).get("closure_level"),
                "latest_pair_max_relative_change": calorine_full_lbte.get("mesh_convergence", {}).get("latest_pair", {}).get("max_relative_change"),
                "method0_negative_300K": calorine_full_lbte.get("checks", {}).get("method0_negative_in_plane_kappa_at_300K"),
                "controlling_blocker": calorine_full_lbte.get("controlling_blocker"),
            }),
            evidence(rel(calorine_isotope_path), calorine_isotope, {
                "status": calorine_isotope.get("status"),
                "closure_level": calorine_isotope.get("major_result", {}).get("closure_level"),
                "natural_composition_envelope": calorine_isotope.get("source", {}).get("representative_fraction_13C"),
                "controlling_blocker": calorine_isotope.get("controlling_blocker"),
            }),
            evidence(rel(calorine_uncertainty_path), calorine_uncertainty, {
                "status": calorine_uncertainty.get("status"),
                "closure_level": calorine_uncertainty.get("major_result", {}).get("closure_level"),
                "source_grade_uncertainty_present": calorine_uncertainty.get("checks", {}).get("source_grade_uncertainty_present"),
                "controlling_blocker": calorine_uncertainty.get("controlling_blocker"),
            }),
            evidence(rel(nims_graphite_route_path), nims_graphite_route, {
                "status": nims_graphite_route.get("status"),
                "route_closed_as_no_go": nims_graphite_route.get("acceptance", {}).get("route_closed_as_no_go"),
                "controlling_blocker": nims_graphite_route.get("controlling_blocker"),
            }),
            evidence(rel(srm3600_path), srm3600, {
                "status": srm3600.get("status"),
                "closure_level": srm3600.get("major_result", {}).get("closure_level"),
                "data_role": srm3600.get("major_result", {}).get("data_role"),
                "raw_sha256": srm3600.get("source", {}).get("local_sha256"),
                "numeric_rows_emitted": srm3600.get("acceptance", {}).get("numeric_rows_emitted"),
                "uncertainty_boundary": srm3600.get("source", {}).get("uncertainty_boundary", {}).get("reported_relative_magnitude"),
                "ding_material_match": srm3600.get("source", {}).get("material_identity", {}).get("ding_ttg_hopg_match"),
                "controlling_blocker": srm3600.get("controlling_blocker"),
            }),
            evidence(rel(perez_hopg_path), perez_hopg, {
                "status": perez_hopg.get("status"),
                "closure_level": perez_hopg.get("major_result", {}).get("closure_level"),
                "data_role": perez_hopg.get("major_result", {}).get("data_role"),
                "raw_sha256": perez_hopg.get("source", {}).get("local_sha256"),
                "numeric_rows_emitted": perez_hopg.get("acceptance", {}).get("numeric_rows_emitted"),
                "uncertainty_boundary": perez_hopg.get("source", {}).get("uncertainty_boundary", {}).get("method_comparison_relative_bound"),
                "ding_material_match": perez_hopg.get("source", {}).get("material_identity", {}).get("ding_ttg_match"),
                "controlling_blocker": perez_hopg.get("controlling_blocker"),
            }),
            evidence(rel(holdout_audit_path), holdout_audit, {
                "status": holdout_audit.get("status"),
                "metadata_only_observed": holdout_controls.get("metadata_only_observed"),
                "numeric_payload_consumed": holdout_controls.get("numeric_payload_consumed"),
                "used_for_fit": holdout_controls.get("used_for_fit"),
                "used_for_tuning": holdout_controls.get("used_for_tuning"),
                "used_for_calibration": holdout_controls.get("used_for_calibration"),
            }),
            evidence(rel(ding_c_src_boundary_path), ding_c_src_boundary, {
                "status": ding_c_src_boundary.get("status"),
                "closure_level": ding_c_src_boundary.get("major_result", {}).get("closure_level"),
                "mp48_is_ding_c_src": False,
                "numeric_alpha_Phi_K_emitted": ding_c_src_boundary.get("numeric_alpha_Phi_K_emitted"),
            }),
            evidence(rel(no_go_path), no_go, {"status": no_go.get("status"), "proof_scope": no_go.get("proof_scope")}),
            evidence(rel(telegraph_path), telegraph, {"status": telegraph.get("status"), "major_result_id": telegraph.get("major_result", {}).get("major_result_id")}),
            evidence(rel(coupled_path), coupled, {"status": coupled.get("status"), "major_result_id": coupled.get("major_result", {}).get("major_result_id")}),
        ],
    }
    artifact["verification_status"]["eos_transport_kms_entropy"].update(preserved_lane_integrations)
    # Current source artifacts override stale fields, while lane-specific
    # details emitted by a sync pass (for example fixed-background flags) are
    # retained until the corresponding lane is synchronized again.
    merged_lane_integrations = {}
    for lane_key, discovered in discovered_lane_integrations.items():
        previous = preserved_lane_integrations.get(lane_key, {})
        merged = dict(previous) if isinstance(previous, dict) else {}
        merged.update(discovered)
        merged_lane_integrations[lane_key] = merged
    artifact["verification_status"]["eos_transport_kms_entropy"].update(merged_lane_integrations)
    beta_correspondence_lane = merged_lane_integrations.get(
        "beta_action_normalized_correspondence_no_go"
    )
    if beta_correspondence_lane:
        artifact["verification_status"]["non_circular_bridge"][
            "beta_action_normalized_correspondence_no_go"
        ] = beta_correspondence_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "beta_action_normalized_correspondence_no_go", None
        )
    # Keep source-acquisition evidence in the source-package lane.
    # The discovery sweep is broad, but a source row must not be classified as
    # an EOS/transport result merely because it carries a major-result record.
    ding_c_src_boundary_lane = discovered_lane_integrations.get(
        "ding_c_src_independent_reproduction_boundary"
    )
    if ding_c_src_boundary_lane:
        artifact["verification_status"]["source_package"][
            "ding_c_src_independent_reproduction_boundary"
        ] = ding_c_src_boundary_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_c_src_independent_reproduction_boundary", None
        )
    independent_csrc_acceptance_lane = discovered_lane_integrations.get(
        "independent_csrc_acceptance_contract"
    )
    if independent_csrc_acceptance_lane:
        artifact["verification_status"]["source_package"][
            "independent_csrc_acceptance_contract"
        ] = independent_csrc_acceptance_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "independent_csrc_acceptance_contract", None
        )
    calorine_candidate_lane = discovered_lane_integrations.get(
        "calorine_zenodo_nep_bte_candidate_boundary"
    )
    if calorine_candidate_lane:
        artifact["verification_status"]["source_package"][
            "calorine_zenodo_nep_bte_candidate_boundary"
        ] = calorine_candidate_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "calorine_zenodo_nep_bte_candidate_boundary", None
        )
    calorine_reproduction_lane = discovered_lane_integrations.get(
        "calorine_zenodo_nep_bte_numeric_reproduction"
    )
    if calorine_reproduction_lane:
        artifact["verification_status"]["source_package"][
            "calorine_zenodo_nep_bte_numeric_reproduction"
        ] = calorine_reproduction_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "calorine_zenodo_nep_bte_numeric_reproduction", None
        )
    for lane_key in ("calorine_full_lbte_numerical_stability_boundary", "calorine_isotope_mass_sensitivity", "calorine_state_uncertainty_decomposition", "calorine_csrc_equilibrium_crosscheck", "figshare_dft_force_data_boundary", "huang_2023_nims_mdr_payload_boundary", "calorine_public_model_variant_boundary", "calorine_nep1_backend_compatibility", "calorine_legacy_nep2_backend_probe", "calorine_legacy_nep2_pbte_reproduction", "calorine_model_form_state_spread_comparison", "qh15_graphite_cv_comparator_boundary"):
        lane = discovered_lane_integrations.get(lane_key)
        if lane:
            artifact["verification_status"]["source_package"][lane_key] = lane
            artifact["verification_status"]["eos_transport_kms_entropy"].pop(lane_key, None)
    nims_graphite_route_lane = discovered_lane_integrations.get(
        "nims_graphite_ltc_route_no_go"
    )
    if nims_graphite_route_lane:
        artifact["verification_status"]["source_package"][
            "nims_graphite_ltc_route_no_go"
        ] = nims_graphite_route_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "nims_graphite_ltc_route_no_go", None
        )
    aist_graphite_route_lane = discovered_lane_integrations.get(
        "aist_graphite_source_route_boundary"
    )
    if aist_graphite_route_lane:
        artifact["verification_status"]["source_package"][
            "aist_graphite_source_route_boundary"
        ] = aist_graphite_route_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "aist_graphite_source_route_boundary", None
        )
    srm3600_lane = discovered_lane_integrations.get(
        "nist_srm_3600_heat_capacity_comparator_boundary"
    )
    if srm3600_lane:
        artifact["verification_status"]["source_package"]["nist_srm_3600_heat_capacity_comparator_boundary"] = srm3600_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "nist_srm_3600_heat_capacity_comparator_boundary", None
        )
    perez_hopg_lane = discovered_lane_integrations.get(
        "perez_castaneda_hopg_specific_heat_source_boundary"
    )
    if perez_hopg_lane:
        artifact["verification_status"]["source_package"]["perez_castaneda_hopg_specific_heat_source_boundary"] = perez_hopg_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "perez_castaneda_hopg_specific_heat_source_boundary", None
        )
    ding_public_supplementary_lane = discovered_lane_integrations.get(
        "ding_public_supplementary_payload_boundary"
    )
    ding_experimental_heating_lane = discovered_lane_integrations.get(
        "ding_experimental_heating_input_boundary"
    )
    if ding_experimental_heating_lane:
        artifact["verification_status"]["source_package"][
            "ding_experimental_heating_input_boundary"
        ] = ding_experimental_heating_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_experimental_heating_input_boundary", None
        )
    ding_c_src_fixed_volume_lane = discovered_lane_integrations.get(
        "ding_c_src_fixed_volume_identity"
    )
    if ding_c_src_fixed_volume_lane:
        artifact["verification_status"]["source_package"]["ding_c_src_fixed_volume_identity"] = ding_c_src_fixed_volume_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_c_src_fixed_volume_identity", None
        )
    if ding_public_supplementary_lane:
        artifact["verification_status"]["source_package"][
            "ding_public_supplementary_payload_boundary"
        ] = ding_public_supplementary_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_public_supplementary_payload_boundary", None
        )
    ding_2017_acs_supplementary_lane = discovered_lane_integrations.get(
        "ding_2017_acs_supplementary_payload_boundary"
    )
    if ding_2017_acs_supplementary_lane:
        artifact["verification_status"]["source_package"][
            "ding_2017_acs_supplementary_payload_boundary"
        ] = ding_2017_acs_supplementary_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_2017_acs_supplementary_payload_boundary", None
        )
    microscopic_finite_cutoff_kubo_lane = discovered_lane_integrations.get(
        "uet_o2_microscopic_finite_cutoff_kubo_match"
    )
    if microscopic_finite_cutoff_kubo_lane:
        artifact["verification_status"]["eos_transport_kms_entropy"][
            "microscopic_finite_cutoff_kubo_match"
        ] = microscopic_finite_cutoff_kubo_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop("uet_o2_microscopic_finite_cutoff_kubo_match", None)

    heat_current_kubo_lane = discovered_lane_integrations.get(
        "uet_o2_heat_current_kubo_match"
    )
    if heat_current_kubo_lane:
        artifact["verification_status"]["eos_transport_kms_entropy"][
            "heat_current_kubo_match"
        ] = heat_current_kubo_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "uet_o2_heat_current_kubo_match", None
        )
    heat_current_kubo_continuum_boundary_lane = discovered_lane_integrations.get(
        "uet_o2_heat_current_kubo_continuum_boundary"
    )
    if heat_current_kubo_continuum_boundary_lane:
        artifact["verification_status"]["eos_transport_kms_entropy"][
            "heat_current_kubo_continuum_boundary"
        ] = heat_current_kubo_continuum_boundary_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "uet_o2_heat_current_kubo_continuum_boundary", None
        )
    phi_e_comparator_lane = discovered_lane_integrations.get(
        "mp48_phi_e_dimensional_anchor_comparator"
    )
    if phi_e_comparator_lane:
        artifact["verification_status"]["dimensional_observable_map"][
            "mp48_phi_e_dimensional_anchor_comparator"
        ] = phi_e_comparator_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "mp48_phi_e_dimensional_anchor_comparator", None
        )
    matter_coupling_normalization_lane = discovered_lane_integrations.get(
        "covariant_matter_coupling_normalization_no_go"
    )
    if matter_coupling_normalization_lane:
        artifact["verification_status"]["dimensional_observable_map"][
            "covariant_matter_coupling_normalization_no_go"
        ] = matter_coupling_normalization_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "covariant_matter_coupling_normalization_no_go", None
        )
    scale_dependency_lane = discovered_lane_integrations.get(
        "thermal_bridge_scale_dependency_no_go"
    )
    if scale_dependency_lane:
        artifact["verification_status"]["dimensional_observable_map"][
            "thermal_bridge_scale_dependency_no_go"
        ] = scale_dependency_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "thermal_bridge_scale_dependency_no_go", None
        )
    spectral_csrc_lane = discovered_lane_integrations.get(
        "mp48_spectral_csrc_reproduction"
    )
    if spectral_csrc_lane:
        artifact["verification_status"]["source_package"][
            "mp48_spectral_csrc_reproduction"
        ] = spectral_csrc_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "mp48_spectral_csrc_reproduction", None
        )
    force_constant_lane = discovered_lane_integrations.get(
        "mp48_force_constant_harmonic_reconstruction"
    )
    if force_constant_lane:
        artifact["verification_status"]["source_package"][
            "mp48_force_constant_harmonic_reconstruction"
        ] = force_constant_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "mp48_force_constant_harmonic_reconstruction", None
        )
    mesh_convergence_lane = discovered_lane_integrations.get(
        "mp48_force_constant_csrc_mesh_convergence"
    )
    if mesh_convergence_lane:
        artifact["verification_status"]["source_package"][
            "mp48_force_constant_csrc_mesh_convergence"
        ] = mesh_convergence_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "mp48_force_constant_csrc_mesh_convergence", None
        )
    huang_supplementary_lane = discovered_lane_integrations.get(
        "huang_2023_supplementary_payload_boundary"
    )
    huberman_public_pbte_lane = discovered_lane_integrations.get(
        "huberman_2019_public_pbte_boundary"
    )
    if huberman_public_pbte_lane:
        artifact["verification_status"]["source_package"][
            "huberman_2019_public_pbte_boundary"
        ] = huberman_public_pbte_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "huberman_2019_public_pbte_boundary", None
        )
    nist_density_lane = discovered_lane_integrations.get(
        "nist_axm5q1_density_source_boundary"
    )
    if nist_density_lane:
        artifact["verification_status"]["source_package"][
            "nist_axm5q1_density_source_boundary"
        ] = nist_density_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "nist_axm5q1_density_source_boundary", None
        )
    if huang_supplementary_lane:
        artifact["verification_status"]["source_package"][
            "huang_2023_supplementary_payload_boundary"
        ] = huang_supplementary_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "huang_2023_supplementary_payload_boundary", None
        )
    nist_alpha_v_lane = discovered_lane_integrations.get(
        "nist_graphite_alpha_v_source_boundary"
    )
    if nist_alpha_v_lane:
        artifact["verification_status"]["source_package"][
            "nist_graphite_alpha_v_source_boundary"
        ] = nist_alpha_v_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "nist_graphite_alpha_v_source_boundary", None
        )
    elastic_bulk_lane = discovered_lane_integrations.get(
        "graphite_elastic_bulk_modulus_source"
    )
    if elastic_bulk_lane:
        artifact["verification_status"]["source_package"][
            "graphite_elastic_bulk_modulus_source"
        ] = elastic_bulk_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "graphite_elastic_bulk_modulus_source", None
        )
    isothermal_kt_lane = discovered_lane_integrations.get(
        "graphite_isothermal_kt_source"
    )
    if isothermal_kt_lane:
        artifact["verification_status"]["source_package"][
            "graphite_isothermal_kt_source"
        ] = isothermal_kt_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "graphite_isothermal_kt_source", None
        )
    tpg_alpha_v_lane = discovered_lane_integrations.get(
        "tpg_anisotropic_alpha_v_comparator"
    )
    if tpg_alpha_v_lane:
        artifact["verification_status"]["source_package"][
            "tpg_anisotropic_alpha_v_comparator"
        ] = tpg_alpha_v_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "tpg_anisotropic_alpha_v_comparator", None
        )
    natural_alpha_v_lane = discovered_lane_integrations.get(
        "natural_graphite_nelson_riley_alpha_v_comparator"
    )
    if natural_alpha_v_lane:
        artifact["verification_status"]["source_package"][
            "natural_graphite_nelson_riley_alpha_v_comparator"
        ] = natural_alpha_v_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "natural_graphite_nelson_riley_alpha_v_comparator", None
        )
    bipm_specific_heat_lane = discovered_lane_integrations.get(
        "bipm_specific_heat_cp_comparator"
    )
    if bipm_specific_heat_lane:
        artifact["verification_status"]["source_package"][
            "bipm_specific_heat_cp_comparator"
        ] = bipm_specific_heat_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "bipm_specific_heat_cp_comparator", None
        )
    desorbo_ceylon_lane = discovered_lane_integrations.get(
        "desorbo_1955_ceylon_graphite_cp_comparator"
    )
    if desorbo_ceylon_lane:
        artifact["verification_status"]["source_package"][
            "desorbo_1955_ceylon_graphite_cp_comparator"
        ] = desorbo_ceylon_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "desorbo_1955_ceylon_graphite_cp_comparator", None
        )
    iaea_graphite_cv_lane = discovered_lane_integrations.get(
        "iaea_graphite_table_cv_comparator"
    )
    if iaea_graphite_cv_lane:
        artifact["verification_status"]["source_package"][
            "iaea_graphite_table_cv_comparator"
        ] = iaea_graphite_cv_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "iaea_graphite_table_cv_comparator", None
        )
    iaea_gr280_lane = discovered_lane_integrations.get(
        "iaea_gr280_same_state_cp_comparator"
    )
    if iaea_gr280_lane:
        artifact["verification_status"]["source_package"][
            "iaea_gr280_same_state_cp_comparator"
        ] = iaea_gr280_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "iaea_gr280_same_state_cp_comparator", None
        )
    zenodo_hitrace_lane = discovered_lane_integrations.get(
        "zenodo_hitrace_isotropic_graphite_cp_comparator"
    )
    if zenodo_hitrace_lane:
        artifact["verification_status"]["source_package"][
            "zenodo_hitrace_isotropic_graphite_cp_comparator"
        ] = zenodo_hitrace_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "zenodo_hitrace_isotropic_graphite_cp_comparator", None
        )
    zenodo_ig210_alpha_l_lane = discovered_lane_integrations.get(
        "zenodo_hitrace_ig210_alpha_l_comparator"
    )
    if zenodo_ig210_alpha_l_lane:
        artifact["verification_status"]["source_package"][
            "zenodo_hitrace_ig210_alpha_l_comparator"
        ] = zenodo_ig210_alpha_l_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "zenodo_hitrace_ig210_alpha_l_comparator", None
        )
    farooqui_ig210_lane = discovered_lane_integrations.get(
        "farooqui_ig210_thermophysical_source"
    )
    if farooqui_ig210_lane:
        artifact["verification_status"]["source_package"]["farooqui_ig210_thermophysical_source"
        ] = farooqui_ig210_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "farooqui_ig210_thermophysical_source", None
        )
    farooqui_volumetric_cp_lane = discovered_lane_integrations.get(
        "farooqui_ig210_volumetric_cp_uncertainty"
    )
    if farooqui_volumetric_cp_lane:
        artifact["verification_status"]["source_package"][
            "farooqui_ig210_volumetric_cp_uncertainty"
        ] = farooqui_volumetric_cp_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "farooqui_ig210_volumetric_cp_uncertainty", None
        )
    cv_uncertainty_lane = discovered_lane_integrations.get(
        "iaea_cv_uncertainty_boundary"
    )
    if cv_uncertainty_lane:
        artifact["verification_status"]["source_package"][
            "iaea_cv_uncertainty_boundary"
        ] = cv_uncertainty_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "iaea_cv_uncertainty_boundary", None
        )
    mp48_temperature_volume_lane = discovered_lane_integrations.get(
        "mp48_temperature_volume_uncertainty_boundary"
    )
    if mp48_temperature_volume_lane:
        artifact["verification_status"]["source_package"][
            "mp48_temperature_volume_uncertainty_boundary"
        ] = mp48_temperature_volume_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "mp48_temperature_volume_uncertainty_boundary", None
        )
    graphite_alpha_v_kt_lane = discovered_lane_integrations.get(
        "graphite_alpha_v_kt_matched_source_boundary"
    )
    if graphite_alpha_v_kt_lane:
        artifact["verification_status"]["source_package"][
            "graphite_alpha_v_kt_matched_source_boundary"
        ] = graphite_alpha_v_kt_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "graphite_alpha_v_kt_matched_source_boundary", None
        )
    ding_alternate_public_dataset_lane = discovered_lane_integrations.get(
        "ding_alternate_public_dataset_discovery_boundary"
    )
    if ding_alternate_public_dataset_lane:
        artifact["verification_status"]["source_package"][
            "ding_alternate_public_dataset_discovery_boundary"
        ] = ding_alternate_public_dataset_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_alternate_public_dataset_discovery_boundary", None
        )
    phonix_lane = discovered_lane_integrations.get(
        "phonix_mp47_graphite_harmonic_comparator"
    )
    if phonix_lane:
        artifact["verification_status"]["source_package"][
            "phonix_mp47_graphite_harmonic_comparator"
        ] = phonix_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "phonix_mp47_graphite_harmonic_comparator", None
        )
    material_boundary_lane = discovered_lane_integrations.get(
        "ding_material_regime_boundary"
    )
    if material_boundary_lane:
        artifact["verification_status"]["source_package"][
            "ding_material_regime_boundary"
        ] = material_boundary_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "ding_material_regime_boundary", None
        )
    oxford_source_lane = discovered_lane_integrations.get(
        "oxford_tgs_comparator_provenance"
    )
    if oxford_source_lane:
        artifact["verification_status"]["source_package"][
            "oxford_tgs_comparator_provenance"
        ] = oxford_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "oxford_tgs_comparator_provenance", None
        )
    oxford_numeric_lane = discovered_lane_integrations.get(
        "oxford_tgs_numeric_rows_comparator"
    )
    if oxford_numeric_lane:
        artifact["verification_status"]["source_package"][
            "oxford_tgs_numeric_rows_comparator"
        ] = oxford_numeric_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "oxford_tgs_numeric_rows_comparator", None
        )
    berut_source_lane = discovered_lane_integrations.get(
        "berut_source_package_availability_boundary"
    )
    if berut_source_lane:
        artifact["verification_status"]["source_package"][
            "berut_source_package_availability_boundary"
        ] = berut_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "berut_source_package_availability_boundary", None
        )
        binary_lane = discovered_lane_integrations.get(
            "berut_figure3_remote_binary_identity"
        )
        if binary_lane:
            artifact["verification_status"]["source_package"][
                "berut_figure3_remote_binary_identity"
            ] = binary_lane
            artifact["verification_status"]["eos_transport_kms_entropy"].pop(
                "berut_figure3_remote_binary_identity", None
            )
            digitization_lane = discovered_lane_integrations.get(
                "berut_figure3_digitization"
            )
            if digitization_lane:
                artifact["verification_status"]["source_package"][
                    "berut_figure3_digitization"
                ] = digitization_lane
                artifact["verification_status"]["eos_transport_kms_entropy"].pop(
                    "berut_figure3_digitization", None
                )
    jun_source_lane = discovered_lane_integrations.get("jun_final_source_boundary")
    if jun_source_lane:
        artifact["verification_status"]["source_package"][
            "jun_final_source_boundary"
        ] = jun_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "jun_final_source_boundary", None
        )
    hong_source_lane = discovered_lane_integrations.get("hong_final_source_boundary")
    if hong_source_lane:
        artifact["verification_status"]["source_package"][
            "hong_final_source_boundary"
        ] = hong_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "hong_final_source_boundary", None
        )
    peterson_source_lane = discovered_lane_integrations.get("peterson_source_identity_no_go")
    if peterson_source_lane:
        artifact["verification_status"]["source_package"][
            "peterson_source_identity_no_go"
        ] = peterson_source_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "peterson_source_identity_no_go", None
        )
    # Keep the historical top-level names as read-only aliases.  The canonical
    # lane payload remains nested above; aliases prevent downstream readers from
    # mistaking a schema migration for loss of evidence.
    legacy_lane_aliases = {
        "collective_response_eos_stability_contract": "collective_response_eos_stability_contract",
        "base_phi_independent_calibration_requirement": "base_phi_independent_calibration_requirement",
        "covariant_action_si_anchor_route": "covariant_action_si_anchor_route",
        "covariant_field_normalization_no_go": "covariant_field_normalization_identifiability_no_go",
        "causal_branch_selection": "causal_branch_selection",
        "phi_energy_anchor_identifiability": "phi_energy_anchor_identifiability_no_go",
        "phi_e_reference_normalization": "phi_e_reference_normalization",
        "thermal_response_beta_contract": "thermal_response_beta_contract",
        "beta_symbol_separation_noncircularity_no_go": "beta_symbol_separation_non_circularity_no_go",
        "sk_kms_entropy_interface": "sk_kms_entropy_interface_contract",
    }
    for alias, lane_key in legacy_lane_aliases.items():
        lane = discovered_lane_integrations.get(lane_key)
        if lane:
            artifact["verification_status"][alias] = dict(lane)
    beta_alias = artifact["verification_status"].get("beta_symbol_separation_noncircularity_no_go")
    if beta_alias:
        # Keep the older status spelling only in the compatibility view.
        beta_alias["status"] = "PASS_SCOPED_NO_GO"
    mp48_lane = discovered_lane_integrations.get("mp48_independent_graphite_cv_reproduction")
    if mp48_lane:
        mp48_alias = dict(mp48_lane)
        # The legacy comparator contract used a generic PASS status; retain it
        # without changing the canonical artifact's more specific status.
        mp48_alias["status"] = "PASS"
        mp48_alias["calibration_consumed"] = False
        artifact["verification_status"]["independent_graphite_cv_route"] = mp48_alias
    lane_closures = []
    if discovered_lane_integrations.get("formal_non_circular_bridge_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal non-circular bridge boundary is closed for lane; physical beta, base-Phi SI anchor, and transport provenance remain open")
    if discovered_lane_integrations.get("uet_o2_action_natural_phi_thermal_bridge_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-derived natural Phi-to-thermal bridge is closed for lane; SI Phi normalization, alpha_Phi_K, source c_v, and physical transport remain open")
    if discovered_lane_integrations.get("mp48_independent_graphite_cv_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("independent harmonic graphite c_v comparator (mp-48) is closed for lane without calibration promotion")
    if discovered_lane_integrations.get("mp48_spectral_csrc_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("MP48 harmonic DOS C_src-like cross-file reproduction is closed for lane without Ding-source or alpha promotion")
    if discovered_lane_integrations.get("mp48_force_constant_harmonic_reconstruction", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("MP48 force-constant harmonic reconstruction is closed for lane without Ding-source, transport, or alpha promotion")
    if discovered_lane_integrations.get("mp48_force_constant_csrc_mesh_convergence", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("MP48 force-constant C_src mesh convergence is closed for the independent harmonic lane; the source remains unaccepted for Ding closure")
    if discovered_lane_integrations.get("huang_2023_supplementary_payload_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Huang 2023 graphite supplementary boundary is closed for lane without numeric PBTE, Ding C_src, or alpha promotion")
    if discovered_lane_integrations.get("huberman_2019_public_pbte_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Huberman 2019 public PBTE boundary is closed for lane without machine-readable C_src, raw force constants, accepted reproduction, or alpha promotion")
    if discovered_lane_integrations.get("nist_axm5q1_density_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("NIST AXM-5Q1 same-grade density availability is closed for lane; density uncertainty, c_v, and Ding mapping remain open")
    if discovered_lane_integrations.get("nist_srm_3600_heat_capacity_comparator_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("NIST SRM 3600 glassy-carbon/graphite-powder heat-capacity comparator boundary is closed for lane without numeric rows, Ding material-match, c_v uncertainty closure, or calibration promotion")
    if discovered_lane_integrations.get("nist_graphite_alpha_v_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("NIST AXM-5Q1 graphite alpha_V source boundary is closed for lane without K_T or Ding material-match promotion")
    if discovered_lane_integrations.get("graphite_elastic_bulk_modulus_source", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Bosak single-crystal graphite elastic bulk comparator is closed for lane without isothermal K_T or Ding material-match promotion")
    if discovered_lane_integrations.get("graphite_isothermal_kt_source", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Hanfland 300 K graphite isothermal K_T source is closed for lane without same-grade alpha_V or Ding material-match promotion")
    if discovered_lane_integrations.get("tpg_anisotropic_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("IHEP TPG anisotropic alpha_V comparator is closed for lane without same-specimen K_T or Ding material-match promotion")
    if discovered_lane_integrations.get("natural_graphite_nelson_riley_alpha_v_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("official Nelson-Riley natural/crystalline graphite alpha_V comparator is closed for lane without matched uncertainty or Ding material-match promotion")
    if discovered_lane_integrations.get("bipm_specific_heat_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("BIPM ultra-pure graphite volumetric c_p comparator is closed for lane without c_v conversion or Ding material-match promotion")
    if discovered_lane_integrations.get("iaea_graphite_table_cv_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("IAEA manufactured-graphite table-derived mass-specific c_v comparator is closed for lane without source-grade uncertainty, density conversion, or Ding material-match promotion")
    if discovered_lane_integrations.get("iaea_gr280_same_state_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("IAEA GR-280 same-state Cp and density availability is closed for lane; density standard uncertainty, c_v correction, and Ding material-match promotion remain open")
    if discovered_lane_integrations.get("zenodo_hitrace_isotropic_graphite_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Zenodo Hi-Trace same-block isotropic-graphite high-temperature Cp comparator is closed for lane; c_v conversion, density/alpha_V/K_T, Ding material-match, and alpha_Phi_K promotion remain open")
    if discovered_lane_integrations.get("zenodo_hitrace_ig210_alpha_l_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Zenodo Hi-Trace IG210 mean alpha_l source comparator is closed for lane; alpha_V is conditional, same-state K_T/Cp-Cv, Ding material-match, and alpha_Phi_K promotion remain open")
    if discovered_lane_integrations.get("farooqui_ig210_thermophysical_source", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("NPL/Hi-Trace published IG210 thermophysical source lane is closed: density, C_p, diffusivity, alpha_l, and source uncertainty are archived; K_T, C_v, Ding material-match, and alpha_Phi_K remain open")
    if discovered_lane_integrations.get("farooqui_ig210_volumetric_cp_uncertainty", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("IG-210 volumetric C_p conversion and conservative source-expanded uncertainty are closed for lane; C_v, same-state K_T, Ding mapping, and alpha_Phi_K remain open")
    if discovered_lane_integrations.get("desorbo_1955_ceylon_graphite_cp_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("DeSorbo 1955 Ceylon natural-graphite numeric Cp comparator is closed for lane without standard uncertainty, volumetric c_v conversion, or Ding material-match promotion")
    if discovered_lane_integrations.get("uet_o2_finite_t_quasiparticle_eos_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-temperature O(2) tree-condensate plus quasiparticle EOS is closed for lane without interacting self-energy, physical Kubo, SI, or alpha promotion")
    if discovered_lane_integrations.get("uet_o2_formal_two_sector_thermodynamic_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal O(2) finite-temperature condensate/normal thermodynamic split is closed for lane; transverse normal current, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_two_fluid_static_response_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-temperature O(2) two-sector static response and normal-branch formal heat balance are closed for lane; condensed dissipative transport, retarded physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_thermodynamic_normal_component_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-temperature thermodynamic normal component is closed for lane; physical normal flow, retarded Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_condensed_relative_flow_collision_kernel_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("condensed relative-flow collision kernel is closed for lane; continuum-renormalized physical Kubo, complete two-fluid tensor, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_continuum_relative_flow_kubo_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("continuum thermal relative-flow contact response is closed for lane; loop-renormalized vertex, physical Kubo, complete two-fluid tensor, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_condensed_loop_renormalized_contact_vertex_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("loop-renormalized condensed contact-channel vertex and state-matched natural retarded response are closed for lane; physical Kubo admission, complete condensed 1PI/scattering, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_condensed_relative_flow_kubo_admission_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("state-matched Kubo coefficient admission is closed for the declared condensed relative-flow natural-unit channel; independent physical anchor, complete SK/KMS/1PI transport, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_condensed_sk_kms_kubo_match_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("state-matched condensed SK/KMS/FDT interface and zero-frequency Kubo match are closed for lane; full retarded 1PI self-energy, all-channel renormalization, complete transport, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("condensed_dissipative_transport_identifiability_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("condensed dissipative transport identifiability is closed as a scoped no-go; the current static lane cannot identify a unique dissipative matrix without relative-flow/collision or retarded-correlator evidence")
    if discovered_lane_integrations.get("uet_o2_condensed_retarded_dissipation_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("condensed conservative-action retarded dissipation is closed as a scoped no-go; the action fixes phase stiffness and Goldstone response but cannot select a unique dissipative kernel without SK/influence or matched retarded evidence")
    if discovered_lane_integrations.get("uet_o2_formal_transverse_response_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal O(2) static transverse quasiparticle response is closed for lane; retarded Kubo, interacting self-energy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_collisionless_kubo_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("collisionless O(2) Kubo boundary is closed as a scoped no-go; a finite DC coefficient requires an interaction collision kernel or state-matched microscopic width")
    if discovered_lane_integrations.get("uet_o2_hartree_normal_stability_boundary_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Hartree normal-branch one-sided stability boundary is closed for lane; renormalized condensed phase, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_kinetic_collision_kernel_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-derived O(2) dilute-gas collision kernel and kinetic response are closed for lane; final-state Bose factors, ladder matching, condensed scattering, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_quantum_collision_enhancement_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("explicit elastic final-state Bose enhancement is closed for lane; ladder/vertex matching, condensed scattering, microscopic SK/KMS, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_charge_conserving_ladder_response_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("conserving two-channel retarded ladder response is closed for lane; microscopic momentum-dependent ladder vertices, SK/KMS matching, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_momentum_ladder_sk_kms_interface_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("momentum-dependent charge-conserving response and algebraic SK/KMS/FDT interface is closed for lane; full energy-momentum conservation, microscopic Bethe-Salpeter/SK matching, finite-cutoff limit, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_energy_momentum_conserving_bs_interface_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-grid charge and four-momentum conserving response plus algebraic Bethe-Salpeter/KMS interface is closed for lane; microscopic two-to-two transition kernel, microscopic vertex/SK action matching, finite-cutoff limit, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_exact_kinematic_2to2_transition_kernel_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("exact-kinematic action-derived two-to-two transition and detailed-balance response lane is closed for lane; connected continuum collision operator, microscopic Bethe-Salpeter vertex, SK action/KMS matching, finite-channel limit, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_contact_sk_transition_vertex_match_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("local contact SK vertex to charged transition-kernel normalization and detailed-balance interface is closed for lane; loop-renormalized off-shell self-energy, current-correlator Kubo, SI, alpha, TTG, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_charged_current_correlator_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("charged action-matched finite-cutoff current-correlator, Ward projection, KMS/FDT, and entropy interface are closed for lane; continuum limit, loop-renormalized off-shell self-energy, microscopic current vertex, physical Kubo, SI, alpha, TTG, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_conservative_continuum_collocation_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("conservative finite-cutoff continuum-collocation operator and algebraic vertex/KMS interface are closed for lane; continuum limit, microscopic Bethe-Salpeter vertex, SK/KMS action matching, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_microscopic_finite_cutoff_kubo_match", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-cutoff action-matched contact-SK, Bethe-Salpeter, charged-current KMS/FDT, and entropy response lane is closed without SI or continuum promotion")
    if discovered_lane_integrations.get("uet_o2_heat_current_kubo_match", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("state-matched finite-cutoff retarded heat-current response matches the covariant natural moment lane; continuum, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_heat_current_kubo_continuum_boundary", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("declared heat-current cutoff/order sequence is closed as a scoped continuum no-go; no extrapolated or physical Kubo coefficient is promoted")
    if discovered_lane_integrations.get("uet_o2_regularized_continuum_heat_current_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("named normal-branch compactified regularized continuum heat-current lane is closed for lane; loop-renormalized self-energy, physical Kubo, SI, condensed two-fluid, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_covariant_entropy_heat_flux_balance_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-derived Landau heat-current subtraction, positive finite-cutoff moment response, covariant entropy-current lift, and charge/energy/momentum dissipative balance are closed for lane; physical Kubo, SI heat flux, finite-temperature two-fluid completion, curved 3+1 transport, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_action_thermal_stiffness_beta_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("non-Landauer action-origin thermal response stiffness curvature and natural-unit T*partial_T a_Phi slope are closed for lane; normalized beta_T13, physical beta source, Phi SI normalization, alpha, transport, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_tree_level_bs_sk_match_interface_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("tree-level action vertex normalization and formal SK/KMS/Bethe-Salpeter interface are closed for lane; continuum limit, loop-renormalized microscopic vertex, full interacting SK action, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("continuum_limit_current_scheme_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("current finite-cutoff continuum-resolution controller is closed as a scoped no-go; the declared scheme remains nonconverged and no continuum or physical Kubo promotion is allowed")
    if discovered_lane_integrations.get("uet_o2_one_loop_vertex_uv_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("O(2) bare tensor, tree-level SK contour identity, and finite-cutoff one-loop vertex UV boundary are closed for lane; vacuum counterterm, renormalized microscopic vertex, finite-density charged propagator, full interacting SK action, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_renormalized_vertex_scheme", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("declared zero-density O(2) one-loop vertex subtraction scheme and finite-cutoff renormalized response are closed for lane; unique physical renormalization, finite-density charged vertex, full interacting SK/KMS action, continuum limit, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_density_charged_vertex_scheme", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("finite-density charged normal-branch propagator, particle/antiparticle KMS witness, and declared charged one-loop vertex scheme are closed for lane; unique physical renormalization, condensed/two-fluid completion, full interacting SK/KMS action, continuum limit, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_interacting_sk_kms_action_interface", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("local interacting O(2) SK contour action, charged KMS/FDT, and action-derived detailed-balance interface are closed for lane; nonlocal influence functional, microscopic retarded self-energy, physical dissipation/Kubo, condensed/two-fluid, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_nonlocal_sk_kms_memory_kernel_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal causal nonlocal SK/KMS memory kernel, positive spectral density, and entropy-positivity control are closed for lane; physical retarded self-energy, unique renormalization, condensed/two-fluid, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_one_loop_retarded_self_energy_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("the local quartic one-loop retarded tadpole no-go is closed: its self-energy is real and frequency independent with zero dissipative spectral density; a two-loop sunset or microscopic retarded branch is required")
    if discovered_lane_integrations.get("uet_o2_two_loop_sunset_cut_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("the action-derived finite-channel order-lambda^2 two-loop sunset-cut interface is closed for lane with positive forward/reverse phase-space weights and detailed balance; continuum 1PI self-energy and physical Kubo remain open")
    if discovered_lane_integrations.get("uet_o2_finite_channel_entropy_balance_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("the action-derived finite-channel formal entropy-balance/H-theorem interface is closed for lane; covariant entropy current, heat-flux balance, physical Kubo, and SI mapping remain open")
    if discovered_lane_integrations.get("uet_o2_renormalized_condensate_stationarity_scheme_dependence", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("finite-temperature condensed stationarity scheme-dependence is closed as a scoped no-go; no physical renormalization scheme or phase transition is selected")
    if discovered_lane_integrations.get("uet_o2_action_normalized_sunset_spectral_interface_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-normalized O(2) sunset spectral interface is closed for lane; full physical 1PI self-energy, renormalization, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_action_matched_zero_eta_sunset_subtraction_interface_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-matched O(2) sunset zero-eta distributional and declared subtraction interface is closed for lane; full microscopic 1PI action derivation, unique renormalization, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_action_1pi_sunset_tensor_interface_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-derived O(2) 1PI sunset tensor, symmetry factor, local counterterm basis, and invariant subtraction-variable match are closed for lane; full off-shell loop, unique physical renormalization, SK/KMS, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_euclidean_1pi_sunset_regulated_subtraction_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("regulated Euclidean off-shell O(2) sunset loop and invariant subtraction interface are closed for lane; retarded continuation, unique physical renormalization, finite-temperature SK/KMS, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_vacuum_retarded_sunset_discontinuity_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("vacuum O(2) three-body sunset cut, retarded i0 discontinuity, spacelike dispersion match, and analytic above-threshold principal-value real-part interface are closed for lane; finite-temperature SK/KMS, unique physical renormalization, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_three_body_sunset_sk_kms_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-derived finite-temperature O(2) 1<->3 sunset channel, thermal retarded sign, channel KMS/FDT, pole-subtracted channel retarded real part, and vacuum phase-space normalization are closed for lane; other thermal cuts, full finite-temperature 1PI, all-channel real-part subtraction, unique physical renormalization, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_scattering_sunset_sk_kms_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("action-derived finite-temperature O(2) labeled 2<->2 scattering sunset cut, channel KMS/FDT, retarded sign, and pole-subtracted channel real part are closed for lane; other thermal cuts, full finite-temperature 1PI, all-channel real-part subtraction, unique physical renormalization, Kubo, entropy, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_declared_full_sunset_sk_kms_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("declared timelike equal-mass order-lambda^2 finite-temperature sunset cut composition is closed for lane: action-derived 1<->3 plus labeled 2<->2 summed KMS/FDT, retarded-sign, and compositional PV interface; complete off-shell 1PI, unique physical renormalization, Kubo, entropy, SI, alpha, TTG, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_offshell_1pi_formal_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal finite-temperature off-shell O(2) 1PI object, all signed sunset cut assignments, retarded continuation, KMS, thermal-vacuum UV split, and local counterterm basis are closed for lane; a unique physical renormalization anchor, physical Kubo, entropy, SI, alpha, TTG, and external validation remain open")

    if discovered_lane_integrations.get("uet_o2_on_shell_sunset_collision_width_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("neutral action-matched on-shell sunset collision-width witness is closed for lane; charged off-shell self-energy, current-correlator Kubo matching, SI, alpha, TTG, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_sunset_vacuum_match_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("low-temperature finite-temperature sunset composition matches the action-derived vacuum spectral, retarded-sign, and PV interfaces for lane; physical renormalization, complete 1PI, transport, entropy, SI, alpha, TTG, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_finite_t_sunset_renormalization_identifiability_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("finite-temperature sunset physical-renormalization identifiability is closed as a scoped no-go: reference changes move the PV real part while spectral/KMS/FDT cuts remain invariant; no physical scheme is selected")
    if discovered_lane_integrations.get("uet_o2_renormalized_hartree_normal_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("renormalized Hartree normal branch closes one declared vacuum-plus-thermal interacting normal functional; condensed/two-fluid, physical Kubo, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_condensed_goldstone_ward_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("current finite-temperature condensed stationarity witness fails the zero-momentum Goldstone/Ward condition; a Ward-preserving 2PI or controlled 1/N completion is required")
    if discovered_lane_integrations.get("uet_o2_ward_constrained_condensed_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal Ward-constrained condensed stationarity is closed for lane; the coefficient is symmetry-derived but physical renormalization, full condensed EOS, two-fluid transport, Kubo/SK-KMS, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_ward_constrained_coefficient_state_dependence_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("fixed-reference Ward-constrained coefficient state dependence is closed as a scoped no-go; no state-independent physical finite-temperature renormalization scheme is selected")
    if discovered_lane_integrations.get("uet_o2_auxiliary_field_ward_preserving_condensed_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("fixed-prescription Ward-preserving auxiliary-field condensed lane is closed for lane; microscopic 2PI/controlled 1/N matching, physical EOS, Kubo/SK-KMS, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_auxiliary_field_ward_preserving_condensed_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("fixed-prescription Ward-preserving auxiliary-field condensed lane is closed for lane; microscopic 2PI/controlled 1/N matching, physical EOS, Kubo/SK-KMS, SI, alpha, and external validation remain open")
    if discovered_lane_integrations.get("uet_o2_equilibrium_kms_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("equilibrium O(2) KMS/FDT identity lane is closed without promoting it to interacting SK, dissipative transport, physical Kubo, SI, or alpha")
    if discovered_lane_integrations.get("graphite_green_kubo_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("public graphite/graphene Green-Kubo source boundary is closed as comparator evidence without UET space-response, Ding state, physical Kubo, or alpha promotion")
    if discovered_lane_integrations.get("uet_o2_open_system_sk_kms_entropy_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("formal open-system SK/KMS, FDT, retardedness, and entropy-positivity lane is closed without promoting formal gamma/noise to physical Kubo, SI, alpha, or TTG evidence")
    if discovered_lane_integrations.get("transport_kms_entropy_status_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("transport/KMS/entropy structural and formal status boundary is closed for lane; physical Kubo, finite-temperature normal sector, dimensional Phi map, and curved 3+1 transport remain open")
    if discovered_lane_integrations.get("iaea_cv_uncertainty_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("IAEA Table 4.11 uncertainty-grade volumetric c_v route is closed as a scoped no-go; probable error is not promoted to c_v uncertainty")
    if discovered_lane_integrations.get("mp48_temperature_volume_uncertainty_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("MP48 temperature-resolved volumetric c_v uncertainty boundary is closed as a scoped no-go; the room-temperature fixed-volume comparator and non-statistical envelope cannot substitute for source-grade C_v^vol(T)")
    if discovered_lane_integrations.get("berut_figure3_digitization", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Berut Figure 3c marker transcription and figure-derived comparison boundary are closed for lane; raw numeric source, source-grade error bars, SI mapping, alpha, and external validation remain open")
    if discovered_lane_integrations.get("ding_material_regime_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Ding/comparator material-regime equivalence is closed as a scoped no-go; comparator c_v and c_p lanes cannot substitute for Ding C_src")
    if discovered_lane_integrations.get("graphite_alpha_v_kt_matched_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("current graphite alpha_V/K_T source-pair inventory is closed as a scoped no-go; existing comparator rows are not same-state, same-grade uncertainty inputs for Cp-to-Cv correction")
    if discovered_lane_integrations.get("ding_alternate_public_dataset_discovery_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("current alternate public Ding dataset inventory is closed as a scoped no-go; ISIS PDOS and Caltech c-axis MFP routes do not supply Ding mode-resolved volumetric C_src(T)")
    if discovered_lane_integrations.get("calorine_zenodo_nep_bte_numeric_reproduction", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Calorine/Zenodo graphite NEP PBTE numeric C_src reproduction is closed for lane; latest q-mesh pair is numerically stable, but Ding material equivalence, source-grade uncertainty, and UET calibration remain open")
    if discovered_lane_integrations.get("figshare_dft_force_data_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("public Figshare DFT energy/force archive provenance and PBTE-capability boundary are closed for lane; C_src, force-constant/scattering derivation, alpha, and Ding mapping remain open")
    if discovered_lane_integrations.get("huang_2023_nims_mdr_payload_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("public NIMS MDR Huang 2023 payload boundary is closed for lane; the downloadable archive contains the article PDF only, so numeric PBTE C_src, Ding mapping, and alpha remain open")
    if discovered_lane_integrations.get("calorine_public_model_variant_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("public Calorine C-CX model-variant provenance is closed for lane; model-form spread still requires a same-workflow rerun and is not source-grade uncertainty")
    if discovered_lane_integrations.get("calorine_nep1_backend_compatibility", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("public Calorine C-CX is identified as legacy NEP1; the current Calorine 3.5 backend rejects the model, so a legacy-compatible backend is required before a same-workflow C_src rerun")
    if discovered_lane_integrations.get("calorine_legacy_nep2_backend_probe", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("legacy NEP2 C-CX PBTE candidate rows and q-mesh preflight are closed for lane; source-grade uncertainty, Ding material mapping, alpha_Phi_K, and full bridge remain open")
        lane_closures.append("pinned Calorine 1.0 legacy NEP2 engine accepts the hash-locked C-CX model; same-workflow fc2/fc3, PBTE C_src, convergence, and uncertainty remain open")
    if discovered_lane_integrations.get("calorine_model_form_state_spread_comparison", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Calorine baseline versus C-CX legacy model/state C_src spread is closed for lane on the common 10x10x5 mesh; backend and primitive-volume differences make it a comparator diagnostic, not source-grade uncertainty or Ding acceptance")
    if discovered_lane_integrations.get("calorine_isotope_mass_sensitivity", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Calorine natural-isotope mass sensitivity is closed for lane; composition bounds do not close defect, morphology, isotope-scattering, or Ding-state uncertainty")
    if discovered_lane_integrations.get("calorine_state_uncertainty_decomposition", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Calorine numerical/state uncertainty decomposition is closed for lane; its mesh and mass-only envelopes are not source-grade uncertainty")
    if discovered_lane_integrations.get("phonix_mp47_graphite_harmonic_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Phonix mp-47 graphite harmonic comparator is closed for lane; arbitrary-unit DOS and uncertainty prevent volumetric c_v or Ding C_src promotion")
    if discovered_lane_integrations.get("mp48_phi_e_dimensional_anchor_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("MP48 named Phi_E dimensional comparator is closed for lane without base-Phi or alpha_Phi_K promotion")
    if discovered_lane_integrations.get("thermal_bridge_scale_dependency_no_go", {}).get("closure_level") == "CLOSED_AS_NO_GO":
        lane_closures.append("joint field, energy-density, and Kelvin scale dependency is closed as a scoped no-go for the current normalized/action lane")
    if discovered_lane_integrations.get("ding_fig1d_normalized_source_lane", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("permitted Ding Fig. 1d normalized-source lane is closed for lane without raw-author or alpha claims")
    if discovered_lane_integrations.get("oxford_tgs_comparator_provenance", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Oxford TGS Figure 1 provenance archive is closed for lane without numeric-row or calibration promotion")
    if discovered_lane_integrations.get("oxford_tgs_numeric_rows_comparator", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Oxford TGS Figure 1 numeric rows are closed for lane without physical thermal or Phi calibration promotion")
    if discovered_lane_integrations.get("alpha_phi_k_paired_record_search", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("current alpha_Phi_K paired-record search is closed for lane with no eligible calibration record")
    if discovered_lane_integrations.get("ding_c_src_independent_reproduction_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("independent c_v comparator boundary is closed for lane without promoting it to Ding C_src")
    if discovered_lane_integrations.get("perez_castaneda_hopg_specific_heat_source_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Perez-Castaneda HOPG specific-heat source boundary is closed for lane; the specimen and below-3-percent method-comparison bound are source-locked, but figure-only rows, source-grade uncertainty, Ding C_src, and alpha remain open")
    if discovered_lane_integrations.get("qh15_graphite_cv_comparator_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("QH-15 macroscopic graphite C_v comparator is closed for lane; its unit conversion and Calorine cross-check do not establish Ding C_src, material equivalence, source-grade uncertainty, or alpha_Phi_K")
    if discovered_lane_integrations.get("ding_c_src_fixed_volume_identity", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Ding C_src fixed-volume thermodynamic identity is closed for lane; numeric source rows, material/state equivalence, uncertainty, and alpha remain open")
    if discovered_lane_integrations.get("ding_public_supplementary_payload_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Ding public supplementary payload boundary is closed for lane without promoting PDFs or figures to numeric C_src")
    if discovered_lane_integrations.get("ding_2017_acs_supplementary_payload_boundary", {}).get("closure_level") == "CLOSED_FOR_LANE":
        lane_closures.append("Ding 2017 ACS supplementary payload boundary is closed for lane without promoting PDF equations or figures to numeric C_src")
    closed_items = list(dict.fromkeys([
        *artifact["major_result"].get("what_is_closed", []),
        *lane_closures,
        *previous_major.get("what_is_closed", []),
    ]))
    artifact["major_result"]["what_is_closed"] = [
        item
        for item in closed_items
        if "mesh-convergence question is closed as a scoped no-go" not in item
    ]
    source_level_blockers = {
        "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing",
        "density_uncertainty_not_source_locked",
        "c_v_source_uncertainty_not_closed",
        "direct_volumetric_c_v_or_same_state_Cp_source_missing",
        "same_grade_alpha_V_and_K_T_missing",
        "material_regime_mapping_to_TTG_not_closed",
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    }
    source_independence_lane = discovered_lane_integrations.get(
        "gatech_volumetric_cp_independence_no_go", {}
    )
    # Preserve unresolved source-dependency blockers in the major-result
    # projection. A scoped no-go closes the circular route. The independently
    # measured AXM-5Q1 density lane removes only the density-availability
    # blocker; the source-locked IG-210 table also removes the density-
    # uncertainty blocker, while Cp-to-Cv and material matching remain open.
    density_availability_closed = (
        nist_density_lane.get("closure_level") == "CLOSED_FOR_LANE"
        and str(nist_density_lane.get("status", "")).startswith("PASS_")
    )
    farooqui_density_uncertainty_closed = (
        farooqui_source.get("major_result", {}).get("closure_level")
        == "CLOSED_FOR_LANE"
        and str(farooqui_source.get("status", "")).startswith("PASS_")
        and farooqui_source.get("row_summary", {}).get("density_uncertainty_locked")
        is True
    )
    density_uncertainty_closed = farooqui_density_uncertainty_closed
    for blocker in source_independence_lane.get("open_blockers", []):
        if blocker not in source_level_blockers:
            continue
        if blocker == "independent_same_grade_density_or_direct_volumetric_heat_capacity_missing" and density_availability_closed:
            continue
        if blocker == "density_uncertainty_not_source_locked" and density_uncertainty_closed:
            continue
        blockers.append(blocker)
    same_state_cp_lane = discovered_lane_integrations.get(
        "iaea_gr280_same_state_cp_comparator", {}
    )
    same_state_cp_availability_closed = (
        same_state_cp_lane.get("closure_level") == "CLOSED_FOR_LANE"
        and str(same_state_cp_lane.get("status", "")).startswith("PASS_")
        and same_state_cp_lane.get("same_state_cp_and_density_rows") is True
    )
    if density_availability_closed:
        for blocker in nist_density_lane.get("open_blockers", []):
            if blocker in source_level_blockers:
                if (
                    blocker == "direct_volumetric_c_v_or_same_state_Cp_source_missing"
                    and same_state_cp_availability_closed
                ):
                    continue
                if blocker == "density_uncertainty_not_source_locked" and density_uncertainty_closed:
                    continue
                blockers.append(blocker)
    # Keep the major-result projection readable: only the full-gate
    # controllers and explicit source prerequisites belong here. Lane-specific
    # diagnostics remain nested in verification_status and evidence artifacts.
    open_blockers = list(dict.fromkeys(blockers))
    artifact["major_result"]["what_remains_open"] = open_blockers
    artifact["major_result"]["resolved_blockers"] = [
        {
            "blocker": "density_uncertainty_not_source_locked",
            "status": (
                "CLOSED_FOR_LANE"
                if density_uncertainty_closed
                else "OPEN"
            ),
            "resolution_source": {
                "major_result_id": "T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE",
                "artifact": rel(farooqui_source_path),
                "artifact_sha256": sha256(farooqui_source_path),
                "row_count": farooqui_source.get("row_summary", {}).get("count"),
                "coverage_factor": 2,
                "source_field": "row_summary.density_uncertainty_locked",
            },
            "what_is_closed": (
                "IG-210 density uncertainty is source-locked for the archived "
                "500/700/1000 C rows and is no longer a full-gate blocker."
                if density_uncertainty_closed
                else "No source-locked density uncertainty record is accepted."
            ),
            "what_remains_open": [
                "same_state_IG210_isothermal_K_T_missing",
                "C_p_to_C_v_correction_not_closed",
                "material_regime_mapping_to_TTG_not_closed",
            ],
            "claim_boundary": (
                "This resolves only the density-uncertainty gate projection. "
                "It does not emit C_v, Ding C_src, alpha_Phi_K, or a UET "
                "temperature prediction."
            ),
        }
    ]

    # Preserve scoped closure results separately from the full-topic blockers.
    # A route can be closed as a no-go or comparator lane while its required
    # Core-grade input remains open.
    artifact["major_result"]["resolved_blockers"].extend(
        [
            {
                "blocker": "ding_public_numeric_C_src_route",
                "status": "CLOSED_AS_NO_GO",
                "resolution_source": {
                    "major_result_id": "T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY",
                    "artifact": rel(ding_public_supplementary_path),
                    "artifact_sha256": sha256(ding_public_supplementary_path),
                    "source_data_availability": "author_request_only",
                    "numeric_payload_present": False,
                },
                "what_is_closed": (
                    "The captured public Ding OA/supplementary route does not "
                    "provide an accepted numeric C_src(T) payload. The public "
                    "availability question is closed for this route as a scoped "
                    "no-go."
                ),
                "what_remains_open": [
                    "authorized_Ding_author_payload_or_accepted_independent_PBTE_reproduction",
                    "C_src_uncertainty_or_convergence_contract",
                    "material_regime_mapping_to_TTG_not_closed",
                ],
                "claim_boundary": (
                    "This is not a proof that no author-held or future permitted "
                    "source exists. It emits no C_src rows, does not synthesize "
                    "data, and does not unlock alpha_Phi_K or Full Topic 13."
                ),
            },
            {
                "blocker": "current_graphite_alpha_V_K_T_inventory",
                "status": "CLOSED_AS_NO_GO",
                "resolution_source": {
                    "major_result_id": "T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY",
                    "artifact": rel(
                        ROOT / "docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json"
                    ),
                    "artifact_sha256": sha256(
                        ROOT / "docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json"
                    ),
                    "representative_source_artifact": rel(natural_alpha_v_path),
                    "representative_source_sha256": sha256(natural_alpha_v_path),
                },
                "what_is_closed": (
                    "The current screened graphite alpha_V/K_T inventory does not "
                    "contain a same-state, same-specimen, uncertainty-bearing pair "
                    "that can close the c_p-to-c_v correction."
                ),
                "what_remains_open": [
                    "same_grade_alpha_V_and_K_T_missing",
                    "c_v_source_uncertainty_not_closed",
                    "material_regime_mapping_to_TTG_not_closed",
                ],
                "claim_boundary": (
                    "Comparator alpha_V or K_T rows remain comparison evidence only. "
                    "No cross-specimen substitution is promoted to Ding C_src or "
                    "alpha_Phi_K calibration."
                ),
            },
            {
                "blocker": "independent_harmonic_c_v_comparator_uncertainty_lane",
                "status": "CLOSED_FOR_LANE",
                "resolution_source": {
                    "major_result_id": "T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION",
                    "artifact": rel(
                        ROOT / "docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json"
                    ),
                    "artifact_sha256": sha256(
                        ROOT / "docs/core/artifacts/t13_mp48_independent_graphite_cv_audit.json"
                    ),
                    "uncertainty_status": "NON_STATISTICAL_DISPLAY_ONLY",
                },
                "what_is_closed": (
                    "An independent harmonic graphite c_v comparator with numeric "
                    "rows and an explicit non-statistical envelope is available "
                    "for comparison-only use."
                ),
                "what_remains_open": [
                    "c_v_source_uncertainty_not_closed",
                    "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                    "material_regime_mapping_to_TTG_not_closed",
                ],
                "claim_boundary": (
                    "The comparator envelope is not a source-grade standard uncertainty "
                    "for Ding C_src, is not an alpha_Phi_K calibration, and does not "
                    "unlock Full Topic 13."
                ),
            },
            {
                "blocker": "action_beta_to_normalized_beta_identifiability",
                "status": "CLOSED_AS_NO_GO",
                "resolution_source": {
                    "major_result_id": "T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO",
                    "artifact": rel(
                        ROOT / "docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json"
                    ),
                    "artifact_sha256": sha256(
                        ROOT / "docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json"
                    ),
                },
                "what_is_closed": (
                    "The current natural-unit action slope cannot identify the named "
                    "normalized beta without an independent field, free-energy, and "
                    "natural-to-Kelvin scale map."
                ),
                "what_remains_open": [
                    "normalized_beta_and_SI_scale_correspondence_missing",
                    "beta_UET_finite_temperature_coefficient_provenance_missing",
                    "independent_alpha_Phi_K_calibration_missing",
                ],
                "claim_boundary": (
                    "This closes only the present identifiability question as a "
                    "scoped no-go. It does not produce beta_UET, a Kelvin observable, "
                    "or a Landauer-derived coefficient."
                ),
            },
        ]
    )
    artifact["major_result"]["resolved_blockers"].extend(
        [
            {
                "blocker": "base_phi_to_SI_anchor_identifiability",
                "status": "CLOSED_AS_NO_GO",
                "resolution_source": {
                    "major_result_id": "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO",
                    "artifact": "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json",
                    "artifact_sha256": sha256(
                        ROOT / "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json"
                    ),
                    "normalization_boundary_artifact": rel(phi_si_anchor_boundary_path),
                    "normalization_boundary_sha256": sha256(phi_si_anchor_boundary_path),
                },
                "what_is_closed": (
                    "The current normalized and covariant natural-unit lanes retain "
                    "field and energy rescaling freedom, so they cannot identify a "
                    "numeric base-Phi SI anchor or e0 without an independent scale contract."
                ),
                "what_remains_open": [
                    "dimensional_phi_to_thermal_observable_map_missing",
                    "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
                    "e0_energy_density_scale_not_source_locked",
                ],
                "claim_boundary": (
                    "This closes the current identifiability question as a scoped "
                    "no-go. It does not reject a future source-locked action scale, "
                    "derive e0, or emit a Kelvin observable."
                ),
            },
            {
                "blocker": "normalized_alpha_Phi_K_scale_identifiability",
                "status": "CLOSED_AS_NO_GO",
                "resolution_source": {
                    "major_result_id": "T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO",
                    "artifact": "docs/core/artifacts/t13_alpha_phi_k_identifiability_audit.json",
                    "artifact_sha256": sha256(
                        ROOT / "docs/core/artifacts/t13_alpha_phi_k_identifiability_audit.json"
                    ),
                },
                "what_is_closed": (
                    "The normalized TTG operator is invariant under a compensating "
                    "Phi rescaling, so the absolute K per normalized Phi coefficient "
                    "cannot be identified from the normalized lane alone."
                ),
                "what_remains_open": [
                    "alpha_Phi_K_independent_calibration_missing",
                    "dimensional_phi_to_thermal_observable_map_missing",
                    "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
                ],
                "claim_boundary": (
                    "This is a structural scale no-go only. It does not emit, fit, "
                    "or predict alpha_Phi_K and does not use Landauer, TTG residuals, "
                    "or the locked holdout."
                ),
            },
        ]
    )
    closed_lane_records = [
        record
        for _, record in sorted(discovered_lane_integrations.items())
        if record.get("closure_level")
        in {
            "CLOSED_AS_NO_GO",
            "CLOSED_FOR_LANE",
            "CLOSED_FOR_CORE",
            "CLOSED_FOR_EXTERNAL_CLAIM",
        }
    ]
    source_blockers = {
        "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "same_grade_alpha_V_and_K_T_missing",
        "material_regime_mapping_to_TTG_not_closed",
        "density_uncertainty_not_source_locked",
        "c_v_source_uncertainty_not_closed",
    }
    dimensional_blockers = {
        "alpha_Phi_K_independent_calibration_missing",
        "normalized_beta_and_SI_scale_correspondence_missing",
        "dimensional_phi_to_thermal_observable_map_missing",
    }
    transport_blockers = {
        "eos_transport_kms_entropy_completion_missing",
        "physical_Kubo_coefficient_record_missing",
    }
    blocker_groups = {
        "source_and_material": [item for item in open_blockers if item in source_blockers],
        "dimensional_and_calibration": [
            item for item in open_blockers if item in dimensional_blockers
        ],
        "thermodynamic_transport": [
            item for item in open_blockers if item in transport_blockers
        ],
        "unclassified": [
            item
            for item in open_blockers
            if item not in source_blockers | dimensional_blockers | transport_blockers
        ],
    }
    artifact["major_result"]["closure_summary"] = {
        "closed_lane_count": len(closed_lane_records),
        "closed_as_no_go_count": sum(
            record.get("closure_level") == "CLOSED_AS_NO_GO"
            for record in closed_lane_records
        ),
        "closed_lane_result_ids": [
            record.get("major_result_id")
            for record in closed_lane_records
            if record.get("major_result_id")
        ],
        "open_blocker_count": len(open_blockers),
        "open_blocker_groups": blocker_groups,
        "dependency_gate_state": "NORMALIZED_INTERNAL_TOPIC13_LANES_ONLY",
        "downstream_dependency_unlocked": False,
    }
    oxford_package_path = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/oxford_tgs_figure1_source_package.json"
    if oxford_package_path.is_file() and not any(
        item.get("path") == rel(oxford_package_path)
        for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    ):
        artifact["evidence_artifacts"].append(
            evidence(
                rel(oxford_package_path),
                {},
                {"status": "PASS_OXFORD_TGS_PROVENANCE_ARCHIVE_LOCKED_EXTRACTION_PENDING", "data_role": "TRAINING/COMPARISON", "numeric_rows_emitted": 0},
            )
        )
    oxford_numeric_rel = rel(oxford_numeric_path)
    if oxford_numeric_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                oxford_numeric_rel,
                oxford_numeric,
                {
                    "status": oxford_numeric.get("status"),
                    "closure_level": oxford_numeric.get("major_result", {}).get("closure_level"),
                    "data_role": oxford_numeric.get("major_result", {}).get("data_role"),
                    "numeric_rows_emitted": oxford_numeric.get("numeric_rows_emitted"),
                    "numeric_alpha_Phi_K_emitted": oxford_numeric.get("numeric_alpha_Phi_K_emitted"),
                    "controlling_blocker": oxford_numeric.get("controlling_blocker"),
                },
            )
        )
    mp48_package_path = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
    if mp48_package_path.is_file() and not any(
        item.get("path") == rel(mp48_package_path)
        for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    ):
        artifact["evidence_artifacts"].append(
            evidence(
                rel(mp48_package_path),
                {},
                {"status": "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE", "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION"},
            )
        )
    mp48_temperature_volume_path = ROOT / "docs/core/artifacts/t13_mp48_temperature_volume_uncertainty_boundary_audit.json"
    if mp48_temperature_volume_path.is_file() and not any(
        item.get("path") == rel(mp48_temperature_volume_path)
        for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    ):
        mp48_temperature_volume = json.loads(
            mp48_temperature_volume_path.read_text(encoding="utf-8-sig")
        )
        artifact["evidence_artifacts"].append(
            evidence(
                rel(mp48_temperature_volume_path),
                mp48_temperature_volume,
                {
                    "status": mp48_temperature_volume.get("status"),
                    "closure_level": mp48_temperature_volume.get("major_result", {}).get("closure_level"),
                    "data_role": mp48_temperature_volume.get("major_result", {}).get("data_role"),
                    "temperature_volume_uncertainty_status": mp48_temperature_volume.get("boundary_observations", {}).get("temperature_volume_uncertainty_status"),
                    "controlling_blocker": mp48_temperature_volume.get("controlling_blocker"),
                },
            )
        )
    graphite_alpha_v_kt_path = ROOT / "docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json"
    if graphite_alpha_v_kt_path.is_file() and not any(
        item.get("path") == rel(graphite_alpha_v_kt_path)
        for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    ):
        graphite_alpha_v_kt = json.loads(
            graphite_alpha_v_kt_path.read_text(encoding="utf-8-sig")
        )
        artifact["evidence_artifacts"].append(
            evidence(
                rel(graphite_alpha_v_kt_path),
                graphite_alpha_v_kt,
                {
                    "status": graphite_alpha_v_kt.get("status"),
                    "closure_level": graphite_alpha_v_kt.get("major_result", {}).get("closure_level"),
                    "data_role": graphite_alpha_v_kt.get("major_result", {}).get("data_role"),
                    "controlling_blocker": graphite_alpha_v_kt.get("controlling_blocker"),
                },
            )
        )
    ding_alternate_public_dataset_path = ROOT / "docs/core/artifacts/t13_ding_alternate_public_dataset_discovery_boundary_audit.json"
    if ding_alternate_public_dataset_path.is_file() and not any(
        item.get("path") == rel(ding_alternate_public_dataset_path)
        for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    ):
        ding_alternate_public_dataset = json.loads(
            ding_alternate_public_dataset_path.read_text(encoding="utf-8-sig")
        )
        artifact["evidence_artifacts"].append(
            evidence(
                rel(ding_alternate_public_dataset_path),
                ding_alternate_public_dataset,
                {
                    "status": ding_alternate_public_dataset.get("status"),
                    "closure_level": ding_alternate_public_dataset.get("major_result", {}).get("closure_level"),
                    "data_role": ding_alternate_public_dataset.get("major_result", {}).get("data_role"),
                    "candidate_count": len(ding_alternate_public_dataset.get("candidate_observations", [])),
                    "controlling_blocker": ding_alternate_public_dataset.get("controlling_blocker"),
                },
            )
        )
    public_supplementary_rel = rel(ding_public_supplementary_path)
    if public_supplementary_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                public_supplementary_rel,
                ding_public_supplementary,
                {
                    "status": ding_public_supplementary.get("status"),
                    "closure_level": ding_public_supplementary.get("major_result", {}).get("closure_level"),
                    "numeric_payload_objects": len(ding_public_supplementary.get("source", {}).get("numeric_payload_objects", [])),
                    "controlling_blocker": ding_public_supplementary.get("controlling_blocker"),
                },
            )
        )
    ding_2017_acs_supplementary_rel = rel(ding_2017_acs_supplementary_path)
    if ding_2017_acs_supplementary_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                ding_2017_acs_supplementary_rel,
                ding_2017_acs_supplementary,
                {
                    "status": ding_2017_acs_supplementary.get("status"),
                    "closure_level": ding_2017_acs_supplementary.get("major_result", {}).get("closure_level"),
                    "numeric_payload_objects": len(ding_2017_acs_supplementary.get("source", {}).get("numeric_payload_objects", [])),
                    "controlling_blocker": ding_2017_acs_supplementary.get("controlling_blocker"),
                },
            )
        )
    phi_e_rel = rel(phi_e_comparator_path)
    if phi_e_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                phi_e_rel,
                phi_e_comparator,
                {
                    "status": phi_e_comparator.get("status"),
                    "closure_level": phi_e_comparator.get("major_result", {}).get("closure_level"),
                    "data_role": phi_e_comparator.get("major_result", {}).get("data_role"),
                    "reference_alpha_Phi_E_K": phi_e_comparator.get("reference_alpha_Phi_E_K"),
                    "numeric_alpha_Phi_K_emitted": phi_e_comparator.get("numeric_alpha_Phi_K_emitted"),
                },
            )
        )
    spectral_rel = rel(spectral_csrc_path)
    if spectral_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                spectral_rel,
                spectral_csrc,
                {
                    "status": spectral_csrc.get("status"),
                    "closure_level": spectral_csrc.get("major_result", {}).get("closure_level"),
                    "data_role": spectral_csrc.get("major_result", {}).get("data_role"),
                    "max_abs_relative_reproduction_residual": spectral_csrc.get("convergence", {}).get("max_abs_relative_reproduction_residual"),
                    "numeric_alpha_Phi_K_emitted": spectral_csrc.get("numeric_alpha_Phi_K_emitted"),
                },
            )
        )
    force_constant_rel = rel(force_constant_path)
    if force_constant_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                force_constant_rel,
                force_constant,
                {
                    "status": force_constant.get("status"),
                    "closure_level": force_constant.get("major_result", {}).get("closure_level"),
                    "data_role": force_constant.get("major_result", {}).get("data_role"),
                    "q_grid_max_frequency_THz": force_constant.get("reconstruction", {}).get("q_grid_frequency_max_THz"),
                    "numeric_alpha_Phi_K_emitted": force_constant.get("numeric_alpha_Phi_K_emitted"),
                },
            )
        )
    mesh_convergence_rel = rel(mesh_convergence_path)
    if mesh_convergence_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                mesh_convergence_rel,
                mesh_convergence,
                {
                    "status": mesh_convergence.get("status"),
                    "closure_level": mesh_convergence.get("major_result", {}).get("closure_level"),
                    "max_abs_relative_mesh_step": mesh_convergence.get("max_abs_relative_mesh_step"),
                    "controlling_blocker": mesh_convergence.get("controlling_blocker"),
                },
            )
        )
    huang_supplementary_rel = rel(huang_supplementary_path)
    if huang_supplementary_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                huang_supplementary_rel,
                huang_supplementary,
                {
                    "status": huang_supplementary.get("status"),
                    "closure_level": huang_supplementary.get("major_result", {}).get("closure_level"),
                    "data_role": huang_supplementary.get("major_result", {}).get("data_role"),
                    "reviewed_page_count": huang_supplementary.get("source", {}).get("reviewed_page_count"),
                    "machine_readable_payload_files": len(huang_supplementary.get("source", {}).get("machine_readable_payload_files", [])),
                    "controlling_blocker": huang_supplementary.get("controlling_blocker"),
                },
            )
        )
    huberman_public_pbte_rel = rel(huberman_public_pbte_path)
    if huberman_public_pbte_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                huberman_public_pbte_rel,
                huberman_public_pbte,
                {
                    "status": huberman_public_pbte.get("status"),
                    "closure_level": huberman_public_pbte.get("major_result", {}).get("closure_level"),
                    "data_role": huberman_public_pbte.get("major_result", {}).get("data_role"),
                    "reviewed_page_count": huberman_public_pbte.get("source", {}).get("reviewed_page_count"),
                    "machine_readable_payload_files": len(huberman_public_pbte.get("source", {}).get("machine_readable_payload_files", [])),
                    "controlling_blocker": huberman_public_pbte.get("controlling_blocker"),
                },
            )
        )
    nist_density_rel = rel(nist_density_path)
    if nist_density_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                nist_density_rel,
                nist_density,
                {
                    "status": nist_density.get("status"),
                    "closure_level": nist_density.get("major_result", {}).get("closure_level"),
                    "data_role": nist_density.get("major_result", {}).get("data_role"),
                    "density_kg_per_m3": nist_density.get("rows", [{}])[0].get("density_kg_per_m3"),
                    "precision_bound": nist_density.get("rows", [{}])[0].get("uncertainty_boundary", {}).get("reported_relative_precision_bound"),
                    "controlling_blocker": nist_density.get("controlling_blocker"),
                },
            )
        )
    tpg_alpha_v_rel = rel(tpg_alpha_v_path)
    if tpg_alpha_v_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                tpg_alpha_v_rel,
                tpg_alpha_v,
                {
                    "status": tpg_alpha_v.get("status"),
                    "closure_level": tpg_alpha_v.get("major_result", {}).get("closure_level"),
                    "data_role": tpg_alpha_v.get("major_result", {}).get("data_role"),
                    "alpha_V_per_K": tpg_alpha_v.get("derived_comparator", {}).get("alpha_V_per_K"),
                    "alpha_V_uncertainty_per_K": tpg_alpha_v.get("derived_comparator", {}).get("alpha_V_uncertainty_per_K"),
                    "same_specimen_alpha_V": tpg_alpha_v.get("derived_comparator", {}).get("same_specimen_alpha_V"),
                },
            )
        )
    natural_alpha_v_rel = rel(natural_alpha_v_path)
    if natural_alpha_v_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                natural_alpha_v_rel,
                natural_alpha_v,
                {
                    "status": natural_alpha_v.get("status"),
                    "closure_level": natural_alpha_v.get("major_result", {}).get("closure_level"),
                    "data_role": natural_alpha_v.get("major_result", {}).get("data_role"),
                    "alpha_V_per_K": natural_alpha_v.get("derived_comparator", {}).get("alpha_V_per_K"),
                    "alpha_V_uncertainty_per_K": natural_alpha_v.get("derived_comparator", {}).get("alpha_V_uncertainty_per_K"),
                    "same_specimen_alpha_V": natural_alpha_v.get("derived_comparator", {}).get("same_specimen_alpha_V"),
                },
            )
        )
    bipm_specific_heat_rel = rel(bipm_specific_heat_path)
    if bipm_specific_heat_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                bipm_specific_heat_rel,
                bipm_specific_heat,
                {
                    "status": bipm_specific_heat.get("status"),
                    "closure_level": bipm_specific_heat.get("major_result", {}).get("closure_level"),
                    "data_role": bipm_specific_heat.get("major_result", {}).get("data_role"),
                    "volumetric_cp_J_per_m3_K": bipm_specific_heat.get("derived_comparator", {}).get("volumetric_cp_J_per_m3_K"),
                    "volumetric_cp_uncertainty_J_per_m3_K": bipm_specific_heat.get("derived_comparator", {}).get("volumetric_cp_standard_uncertainty_J_per_m3_K"),
                    "cv_emitted": bipm_specific_heat.get("derived_comparator", {}).get("cv_emitted"),
                    "controlling_blocker": bipm_specific_heat.get("controlling_blocker"),
                },
            )
        )
    bipm_package_rel = rel(bipm_package_path)
    if bipm_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                bipm_package_rel,
                bipm_package,
                {
                    "status": bipm_package.get("status"),
                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
                    "raw_sha256": bipm_package.get("source", {}).get("local_raw_sha256"),
                    "material_match_to_Ding_TTG": bipm_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),
                },
            )
        )
    desorbo_ceylon_rel = rel(desorbo_ceylon_path)
    if desorbo_ceylon_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                desorbo_ceylon_rel,
                desorbo_ceylon,
                {
                    "status": desorbo_ceylon.get("status"),
                    "closure_level": desorbo_ceylon.get("major_result", {}).get("closure_level"),
                    "data_role": desorbo_ceylon.get("major_result", {}).get("data_role"),
                    "numeric_cp_J_per_mol_K": desorbo_ceylon.get("source_row", {}).get("value_J_per_mol_K"),
                    "volumetric_cv_emitted": desorbo_ceylon.get("volumetric_cv_emitted"),
                    "controlling_blocker": desorbo_ceylon.get("controlling_blocker"),
                },
            )
        )
    desorbo_ceylon_package_rel = rel(desorbo_ceylon_package_path)
    if desorbo_ceylon_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                desorbo_ceylon_package_rel,
                desorbo_ceylon_package,
                {
                    "status": desorbo_ceylon_package.get("status"),
                    "data_role": desorbo_ceylon_package.get("source_row", {}).get("data_role"),
                    "raw_sha256": desorbo_ceylon_package.get("source", {}).get("local_raw_sha256"),
                    "standard_uncertainty": desorbo_ceylon_package.get("uncertainty_boundary", {}).get("standard_uncertainty_value"),
                    "conversion_status": desorbo_ceylon_package.get("required_quantity_contract", {}).get("conversion_status"),
                },
            )
        )
    finite_qp_eos_rel = rel(finite_qp_eos_path)
    if finite_qp_eos_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                finite_qp_eos_rel,
                finite_qp_eos,
                {
                    "status": finite_qp_eos.get("status"),
                    "closure_level": finite_qp_eos.get("major_result", {}).get("closure_level"),
                    "data_role": finite_qp_eos.get("major_result", {}).get("data_role"),
                    "failed_checks": finite_qp_eos.get("failed_checks"),
                    "controlling_blocker": finite_qp_eos.get("controlling_blocker"),
                },
            )
        )
    formal_two_sector_rel = "docs/core/artifacts/t13_uet_o2_formal_two_sector_thermodynamics_audit.json"
    formal_two_sector_path = ROOT / formal_two_sector_rel
    if formal_two_sector_path.is_file() and formal_two_sector_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        formal_two_sector = json.loads(formal_two_sector_path.read_text(encoding="utf-8-sig"))
        artifact["evidence_artifacts"].append(
            evidence(
                formal_two_sector_rel,
                formal_two_sector,
                {
                    "status": formal_two_sector.get("status"),
                    "closure_level": formal_two_sector.get("major_result", {}).get("closure_level"),
                    "data_role": formal_two_sector.get("major_result", {}).get("data_role"),
                    "controlling_blocker": formal_two_sector.get("controlling_blocker"),
                },
            )
        )
    formal_transverse_rel = "docs/core/artifacts/t13_uet_o2_formal_transverse_response_audit.json"
    formal_transverse_path = ROOT / formal_transverse_rel
    if formal_transverse_path.is_file() and formal_transverse_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        formal_transverse = json.loads(formal_transverse_path.read_text(encoding="utf-8-sig"))
        artifact["evidence_artifacts"].append(
            evidence(
                formal_transverse_rel,
                formal_transverse,
                {
                    "status": formal_transverse.get("status"),
                    "closure_level": formal_transverse.get("major_result", {}).get("closure_level"),
                    "data_role": formal_transverse.get("major_result", {}).get("data_role"),
                    "controlling_blocker": formal_transverse.get("controlling_blocker"),
                },
            )
        )
    equilibrium_kms_rel = rel(equilibrium_kms_path)
    if equilibrium_kms_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                equilibrium_kms_rel,
                equilibrium_kms,
                {
                    "status": equilibrium_kms.get("status"),
                    "closure_level": equilibrium_kms.get("major_result", {}).get("closure_level"),
                    "data_role": equilibrium_kms.get("major_result", {}).get("data_role"),
                    "failed_checks": equilibrium_kms.get("failed_checks"),
                    "controlling_blocker": equilibrium_kms.get("controlling_blocker"),
                },
            )
        )
    graphite_green_kubo_rel = rel(graphite_green_kubo_path)
    if graphite_green_kubo_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                graphite_green_kubo_rel,
                graphite_green_kubo,
                {
                    "status": graphite_green_kubo.get("status"),
                    "closure_level": graphite_green_kubo.get("major_result", {}).get("closure_level"),
                    "data_role": graphite_green_kubo.get("major_result", {}).get("data_role"),
                    "failed_checks": graphite_green_kubo.get("failed_checks"),
                    "controlling_blocker": graphite_green_kubo.get("controlling_blocker"),
                },
            )
        )
    iaea_graphite_cv_rel = rel(iaea_graphite_cv_path)
    if iaea_graphite_cv_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                iaea_graphite_cv_rel,
                iaea_graphite_cv,
                {
                    "status": iaea_graphite_cv.get("status"),
                    "closure_level": iaea_graphite_cv.get("major_result", {}).get("closure_level"),
                    "data_role": iaea_graphite_cv.get("major_result", {}).get("data_role"),
                    "cv_mass_J_per_kg_K": iaea_graphite_cv.get("derived_comparator", {}).get("cv_mass_J_per_kg_K"),
                    "cv_standard_uncertainty_J_per_kg_K": iaea_graphite_cv.get("derived_comparator", {}).get("cv_standard_uncertainty_J_per_kg_K"),
                    "cv_volumetric_emitted": iaea_graphite_cv.get("derived_comparator", {}).get("cv_volumetric_emitted"),
                    "controlling_blocker": iaea_graphite_cv.get("controlling_blocker"),
                },
            )
        )
    iaea_graphite_cv_package_rel = rel(iaea_graphite_cv_package_path)
    if iaea_graphite_cv_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                iaea_graphite_cv_package_rel,
                iaea_graphite_cv_package,
                {
                    "status": iaea_graphite_cv_package.get("status"),
                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
                    "raw_sha256": iaea_graphite_cv_package.get("source", {}).get("local_raw_sha256"),
                    "material_match_to_Ding_TTG": iaea_graphite_cv_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),
                },
            )
        )
    iaea_gr280_rel = rel(iaea_gr280_path)
    if iaea_gr280_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                iaea_gr280_rel,
                iaea_gr280,
                {
                    "status": iaea_gr280.get("status"),
                    "closure_level": iaea_gr280.get("major_result", {}).get("closure_level"),
                    "data_role": iaea_gr280.get("major_result", {}).get("data_role"),
                    "same_state_cp_and_density_rows": iaea_gr280.get("same_state_cp_and_density_rows"),
                    "cp_volumetric_J_per_m3_K": iaea_gr280.get("derived_comparator", {}).get("cp_volumetric_J_per_m3_K"),
                    "density_standard_uncertainty_reported": iaea_gr280.get("derived_comparator", {}).get("density_standard_uncertainty_reported"),
                    "controlling_blocker": iaea_gr280.get("controlling_blocker"),
                },
            )
        )
    iaea_gr280_package_rel = rel(iaea_gr280_package_path)
    if iaea_gr280_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                iaea_gr280_package_rel,
                iaea_gr280_package,
                {
                    "status": iaea_gr280_package.get("status"),
                    "data_role": "COMPARISON_ONLY_NOT_CALIBRATION",
                    "raw_sha256": iaea_gr280_package.get("source", {}).get("local_raw_sha256"),
                    "same_state_cp_density_rows": iaea_gr280_package.get("derived_comparator", {}).get("same_state_cp_density_rows"),
                    "material_match_to_Ding_TTG": iaea_gr280_package.get("derived_comparator", {}).get("material_match_to_Ding_TTG"),
                },
            )
        )
    cv_uncertainty_rel = rel(cv_uncertainty_path)
    if cv_uncertainty_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                cv_uncertainty_rel,
                cv_uncertainty,
                {
                    "status": cv_uncertainty.get("status"),
                    "closure_level": cv_uncertainty.get("major_result", {}).get("closure_level"),
                    "data_role": cv_uncertainty.get("major_result", {}).get("data_role"),
                    "controlling_blocker": cv_uncertainty.get("controlling_blocker"),
                    "direct_volumetric_cv_with_uncertainty": cv_uncertainty.get("boundary_observations", {}).get("direct_volumetric_cv_with_uncertainty"),
                },
            )
        )
    cv_uncertainty_package_rel = rel(cv_uncertainty_package_path)
    if cv_uncertainty_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                cv_uncertainty_package_rel,
                cv_uncertainty_package,
                {
                    "status": cv_uncertainty_package.get("status"),
                    "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
                    "raw_sha256": cv_uncertainty_package.get("source", {}).get("local_raw_sha256"),
                    "equivalence_result": cv_uncertainty_package.get("mapping_contract", {}).get("equivalence_result"),
                },
            )
        )
    material_boundary_rel = rel(material_boundary_path)
    if material_boundary_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                material_boundary_rel,
                material_boundary,
                {
                    "status": material_boundary.get("status"),
                    "closure_level": material_boundary.get("major_result", {}).get("closure_level"),
                    "data_role": material_boundary.get("major_result", {}).get("data_role"),
                    "equivalence_result": material_boundary.get("mapping_contract", {}).get("equivalence_result"),
                    "comparator_count": len(material_boundary.get("source", {}).get("comparators", [])),
                    "controlling_blocker": material_boundary.get("controlling_blocker"),
                },
            )
        )
    material_boundary_package_rel = rel(material_boundary_package_path)
    if material_boundary_package_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                material_boundary_package_rel,
                material_boundary_package,
                {
                    "status": material_boundary_package.get("status"),
                    "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
                    "equivalence_result": material_boundary_package.get("mapping_contract", {}).get("equivalence_result"),
                },
            )
        )
    isothermal_kt_rel = rel(isothermal_kt_path)
    if isothermal_kt_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                isothermal_kt_rel,
                isothermal_kt,
                {
                    "status": isothermal_kt.get("status"),
                    "closure_level": isothermal_kt.get("major_result", {}).get("closure_level"),
                    "data_role": isothermal_kt.get("major_result", {}).get("data_role"),
                    "K_T_GPa": isothermal_kt.get("source_row", {}).get("K_T_GPa"),
                    "K_T_uncertainty_GPa": isothermal_kt.get("source_row", {}).get("K_T_uncertainty_GPa"),
                    "Ding_material_regime_mapping_closed": isothermal_kt.get("thermodynamic_contract", {}).get("Ding_material_regime_mapping_closed"),
                },
            )
        )
    elastic_bulk_rel = rel(elastic_bulk_path)
    if elastic_bulk_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                elastic_bulk_rel,
                elastic_bulk,
                {
                    "status": elastic_bulk.get("status"),
                    "closure_level": elastic_bulk.get("major_result", {}).get("closure_level"),
                    "data_role": elastic_bulk.get("major_result", {}).get("data_role"),
                    "reconstructed_B_elastic_GPa": elastic_bulk.get("reconstruction", {}).get("reconstructed_B_elastic_GPa"),
                    "K_T_emitted": elastic_bulk.get("isothermal_boundary", {}).get("K_T_emitted"),
                },
            )
        )
    nist_alpha_v_rel = rel(nist_alpha_v_path)
    if nist_alpha_v_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                nist_alpha_v_rel,
                nist_alpha_v,
                {
                    "status": nist_alpha_v.get("status"),
                    "closure_level": nist_alpha_v.get("major_result", {}).get("closure_level"),
                    "data_role": nist_alpha_v.get("major_result", {}).get("data_role"),
                    "row_count": len(nist_alpha_v.get("rows", [])),
                    "numeric_alpha_Phi_K_emitted": nist_alpha_v.get("numeric_alpha_Phi_K_emitted"),
                },
            )
        )
    existing_evidence_paths = {item.get("path") for item in artifact.get("evidence_artifacts", [])}
    for item in previous_gate.get("evidence_artifacts", []):
        if isinstance(item, dict) and item.get("path") not in existing_evidence_paths:
            artifact["evidence_artifacts"].append(item)
            existing_evidence_paths.add(item.get("path"))
    # Re-expose the pre-registry lane contract after the canonical rebuild.
    # These are projections of existing artifacts, not new physical evidence.
    def compatibility_lane(key):
        value = discovered_lane_integrations.get(key, {})
        return dict(value) if isinstance(value, dict) else {}

    alpha = artifact["verification_status"]["alpha_Phi_K"]
    alpha["identifiability_status"] = "NO_GO_FROM_NORMALIZED_PHI"
    conditional = compatibility_lane("alpha_phi_k_conditional_derivation")
    if conditional:
        alpha.update({
            "conditional_derivation_status": conditional.get("status"),
            "conditional_derivation_artifact": conditional.get("audit"),
            "conditional_formula_status": "CLOSED_FOR_LANE",
            "conditional_unit_contract_status": "CLOSED_FOR_LANE",
            "conditional_open_inputs": conditional.get("open_blockers", []),
            "conditional_next_controller": conditional.get("next_controller"),
        })

    energy_lane = compatibility_lane("phi_e_ttg_bridge_conditional")
    source_anchor = dict(energy_lane.get("standard_pbte_source_anchor", {}))
    if energy_lane:
        named_branch = {
            "branch_id": "T13-PHI-E-001",
            "status": energy_lane.get("status", "PASS_NAMED_BRANCH_OPEN_INPUTS"),
            "closure_level": energy_lane.get("closure_level", "CLOSED_FOR_LANE"),
            "artifact": energy_lane.get("audit"),
            "source_package": source_anchor.get("source_package"),
            "formula_status": "CLOSED_FOR_LANE",
            "base_Phi_identity": "not asserted",
            "base_Phi_to_Phi_E_mapping": "OPEN_DERIVATION_OR_CALIBRATION",
            "c_v_status": "OPEN_CP_TO_CV_UNCERTAINTY",
            "e0_status": "OPEN_NOT_SOURCE_LOCKED",
            "independent_base_alpha_calibration": False,
            "xie_2026_accessed": False,
            "pbte_energy_temperature_source": source_anchor,
            "source_anchor": energy_lane.get("source_anchor", {}),
            "pbte_numeric_input_availability_no_go": energy_lane.get("pbte_numeric_input_availability", {}),
        }
        availability = named_branch["pbte_numeric_input_availability_no_go"]
        author_lane = compatibility_lane("ding_pbte_author_request_package")
        author_status = author_lane.get("status", "PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE")
        author_closure = author_lane.get("closure_level", "CLOSED_FOR_LANE")
        request_state = author_lane.get("request_state", "REQUEST_PACKAGE_READY_NOT_SENT")
        request = {
            "major_result_id": "T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE",
            "status": author_status,
            "closure_level": author_closure,
            "request_state": request_state,
            "sent": False,
            "response_received": False,
            "numeric_C_src_emitted": False,
            "numeric_alpha_Phi_K_emitted": False,
            "target_curve_used": False,
            "xie_2026_accessed": False,
            "audit": author_lane.get("audit"),
            "claim_boundary": author_lane.get("claim_boundary"),
        }
        named_branch["pbte_author_request_package"] = request
        if not availability:
            named_branch["pbte_numeric_input_availability_no_go"] = {
                "status": "PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO",
                "closure_level": "CLOSED_FOR_LANE",
                "direct_oa_numeric_route": "CLOSED_AS_SCOPED_NO_GO",
                "author_request_route": "OPEN_NOT_EXECUTED",
                "independent_reproduction_route": "OPEN_INPUT_PACKAGE_NOT_BUILT",
                "audit": compatibility_lane("ding_pbte_oa_numeric_input_no_go").get("audit"),
            }
        source_independence = compatibility_lane(
            "gatech_volumetric_cp_independence_no_go"
        )
        if source_independence:
            source_independence["same_workbook_density_inversion_allowed"] = False
            source_independence["same_workbook_volumetric_cp_inversion_allowed"] = False
        named_branch["source_independence_no_go"] = source_independence
        alpha["named_energy_response_branch"] = named_branch
    phi_si_anchor_lane = discovered_lane_integrations.get(
        "phi_si_anchor_public_source_boundary"
    )
    if phi_si_anchor_lane:
        artifact["verification_status"]["dimensional_observable_map"][
            "phi_si_anchor_public_source_boundary"
        ] = phi_si_anchor_lane
        artifact["verification_status"]["eos_transport_kms_entropy"].pop(
            "phi_si_anchor_public_source_boundary", None
        )

    legacy_aliases = {
        "base_phi_independent_calibration_requirement": "base_phi_independent_calibration_requirement",
        "covariant_action_si_anchor_route": "covariant_action_si_anchor_route",
        "covariant_field_normalization_no_go": "covariant_field_normalization_identifiability_no_go",
        "phi_energy_anchor_identifiability": "phi_energy_anchor_identifiability_no_go",
        "causal_branch_selection": "causal_branch_selection",
        "collective_response_eos_stability_contract": "collective_response_eos_stability_contract",
    }
    for alias, key in legacy_aliases.items():
        lane = compatibility_lane(key)
        if not lane:
            continue
        artifact["verification_status"][alias] = lane

    base_requirement = artifact["verification_status"].get("base_phi_independent_calibration_requirement")
    if base_requirement:
        base_requirement["status"] = "OPEN_REQUIREMENT"
    action_route = artifact["verification_status"].get("covariant_action_si_anchor_route")
    if action_route:
        action_route["status"] = "PASS_ROUTE_IDENTIFIED_SI_BLOCKED"
        action_route["numeric_e0_emitted"] = False
        action_route["numeric_alpha_Phi_K_emitted"] = False
    field_route = artifact["verification_status"].get("covariant_field_normalization_no_go")
    if field_route:
        field_route["status"] = "PASS_SCOPED_NO_GO"
        field_route["numeric_e0_emitted"] = False
        field_route["numeric_alpha_Phi_K_emitted"] = False
        field_route["target_data_used"] = False
        field_route["xie_2026_accessed"] = False
    phi_anchor = artifact["verification_status"].get("phi_energy_anchor_identifiability")
    if phi_anchor:
        phi_anchor["status"] = "PASS_SCOPED_NO_GO"
        phi_anchor["numeric_e0_emitted"] = False
        phi_anchor["numeric_alpha_Phi_K_emitted"] = False
    causal_alias = artifact["verification_status"].get("causal_branch_selection")
    if causal_alias:
        causal_alias["status"] = "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH"
        causal_alias["baseline_full_candidate_pass"] = False
        causal_alias["baseline_replaced"] = False
        causal_alias["closure_level"] = "CLOSED_FOR_LANE"

    beta_alias = artifact["verification_status"].get("beta_symbol_separation_noncircularity_no_go")
    if beta_alias:
        beta_alias["status"] = "PASS_SCOPED_NO_GO"

    transport = artifact["verification_status"]["eos_transport_kms_entropy"]
    covariant_transport = transport.get("covariant_transport_implementation_boundary")
    if covariant_transport:
        covariant_transport.update({
            "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
            "temperature_scope": "T_ZERO_PURE_SUPERFLUID_ONLY",
            "si_lane": "BLOCKED",
            "synthetic_controls_physical": False,
        })
    kubo = transport.get("physical_kubo_coefficient_provenance")
    if kubo:
        kubo["physical_coefficient_evidence"] = "BLOCKED_NOT_PROVIDED"
        kubo["synthetic_controls_physical"] = False
    graphite = transport.get("standard_graphite_transport_comparator")
    if graphite:
        graphite["synthetic_controls_physical"] = False
        graphite["alpha_Phi_K_emitted"] = False
    standard_o2 = transport.get("standard_o2_finite_temperature_normal_comparator")
    if standard_o2:
        standard_o2.update({
            "physical_uet_eos": False,
            "physical_kubo_coefficient_emitted": False,
            "alpha_Phi_K_emitted": False,
            "R_gen_used_as_state": False,
        })
    one_loop = transport.get("uet_o2_one_loop_normal_branch")
    if one_loop:
        state = one_loop.get("state", {})
        one_loop.update({
            "vacuum_counterterm_included": state.get("vacuum_counterterm_included", False),
            "condensate_contribution_included": state.get("condensate_contribution_included", False),
            "normal_two_fluid_completion": state.get("normal_two_fluid_completion", False),
            "physical_kubo_coefficient_emitted": False,
            "alpha_Phi_K_emitted": False,
            "R_gen_used_as_state": False,
        })

    phonix_rel = rel(phonix_path)
    if phonix_rel not in {
        item.get("path") for item in artifact.get("evidence_artifacts", [])
        if isinstance(item, dict)
    }:
        artifact["evidence_artifacts"].append(
            evidence(
                phonix_rel,
                phonix,
                {
                    "status": phonix.get("status"),
                    "closure_level": phonix.get("major_result", {}).get("closure_level"),
                    "data_role": phonix.get("major_result", {}).get("data_role"),
                    "source_revision": phonix.get("source", {}).get("dataset_revision"),
                    "dos_units": phonix.get("major_result", {}).get("units", {}).get("DOS"),
                    "numeric_c_v_emitted": phonix.get("numeric_c_v_emitted"),
                    "controlling_blocker": phonix.get("controlling_blocker"),
                },
            )
        )
    artifact["source_acquisition_controller"] = "ding_pbte_author_data_or_independent_reproduction_package_missing"
    artifact["claim_promotion"] = False
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "closure_level": artifact["major_result"]["closure_level"], "blockers": blockers, "artifact": rel(OUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
