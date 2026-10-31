# Topic 13 SI Phi Normalization Jacobian Audit

Generated: 2026-09-24.
Canonical artifact: docs/core/07_artifacts/topic13/t13_si_phi_normalization_jacobian_audit.json.

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE.

WHAT_IS_ACTUALLY_CLOSED:
- The chain-rule factor between a covariant-field derivative and a derivative with respect to dimensionless normalized Phi is Phi_scale_nat.
- The O(2) action-derived thermal coefficient differentiates with respect to its covariant Phi field, whose declared natural mass dimension is E^1; it is not already a derivative with respect to dimensionless base Phi.
- The existing alpha_energy_to_si helper converts a supplied natural coefficient by E_ref/k_B but takes no Phi scale; it is sufficient for normalized-Phi units only when its input is already a derivative with respect to normalized Phi.
- The current symbolic contract labels alpha_Phi_K as K per normalized Phi but does not identify the derivative coordinate or state the normalization Jacobian.

WHAT_REMAINS_OPEN:
- The generic SI contract does not connect the O(2) covariant derivative to the base normalized-Phi coordinate.
- Phi_scale_nat and its coefficient provenance remain open; no normalized SI alpha can be emitted from the current contract alone.
- The base-Phi-to-energy-density map and independent graphite alpha_Phi_K calibration remain open.

DEPENDENCY_UNLOCKED: None.

STATUS: PASS_SCOPED_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY; 17/17 checks.

WHAT_CHANGED: Read-only audit of the derivative-coordinate convention; no coefficient, action, source record, or gate was changed.

EQUATION_OR_MAPPING:
alpha_Phi_K = (E_ref/k_B) * Phi_scale_nat * alpha_Phi_theta_covariant_nat
Phi_scale_nat = Phi_scale_SI/E_ref
This factor is required when Phi_normalized = Phi_covariant/Phi_scale.

VERIFICATION: All local formula-boundary checks passed: {'covariant_to_normalized_map_is_explicit': True, 'normalized_alpha_units_are_declared': True, 'existing_alpha_formula_does_not_name_derivative_coordinate': True, 'existing_alpha_formula_omits_phi_scale_jacobian': True, 'si_helper_has_no_field_scale_argument': True, 'si_helper_only_applies_temperature_reference': True, 'normalization_helper_uses_declared_field_scale': True, 'natural_action_alpha_is_not_sourced_as_normalized_si_alpha': True, 'o2_action_phi_has_mass_dimension_one': True, 'o2_energy_response_derivative_is_wrt_action_phi': True, 'symbolic_si_audit_keeps_phi_scale_open': True, 'action_anchor_route_keeps_phi_scale_open': True, 'normalized_lane_scale_rescaling_is_nonidentifiable': True, 'lane_composition_keeps_cross_lane_map_open': True, 'chain_rule_witness_applies_scale_once': True, 'no_physical_alpha_or_target_result_is_emitted': True, 'no_holdout_numeric_payload_is_consumed': True}.
No numeric source rows, target data, fit, or holdout payload were consumed. Xie 2026 blind-use eligibility remains REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE.

CONTROLLING_BLOCKER: O2_covariant_to_normalized_Phi_scale_unproven_and_missing_in_generic_SI_formula.

NEXT_ACTION: Declare the derivative coordinate and source-backed Phi_scale before emitting K per normalized Phi; do not infer either from TTG residuals.

CLAIM_BOUNDARY: This is a formula-interface and chain-rule boundary only. It does not establish a physical Phi scale, emit alpha_Phi_K, validate graphite TTG, change the Topic 13 gate, or promote a global UET claim.
