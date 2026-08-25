# Topic 13 Subresult Closure Map

This file is generated from the canonical Topic 13 closure progress artifact. It exposes result-level closure without treating a passing verifier as Full Topic 13 closure.

MAJOR_RESULT_CLOSURE:
- Full Topic 13: PARTIAL; status BLOCKED_OPEN_T13_FULL_BRIDGE.
- Required subresults: 36; CLOSED_FOR_LANE=21, CLOSED_AS_NO_GO=5, CLOSED_FOR_CORE=0, OPEN=10.

WHAT_IS_ACTUALLY_CLOSED:
- The causal conserved-C question has a scoped no-go, and the named finite-cone Phi branch is a bounded Core handoff only.
- Formal normalized/action, EOS, SK/KMS, entropy, heat-current, source-boundary, and comparator lanes have explicit evidence boundaries.
- The open rows below are the remaining acceptance requirements for the full thermal bridge; they are not missing merely because a script has not been rerun.

WHAT_REMAINS_OPEN:
| Subresult | Major result | Status | Required level | Controlling package | Evidence IDs | Acceptance requirement |
| --- | --- | --- | --- | --- | --- | --- |
| conserved_c_local_gradient_no_go | T13_CAUSAL_THERMAL_BRANCH_CLOSURE | CLOSED_AS_NO_GO | CLOSED_AS_NO_GO |  | none | The principal-symbol incompatibility is scoped to the declared baseline and recorded without deleting it. |
| finite_cone_telegraph_branch | T13_CAUSAL_THERMAL_BRANCH_CLOSURE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_CAUSAL_FLUX_TELEGRAPH_BRANCH | The branch has explicit equations, domain-of-dependence checks, and the unchanged leakage threshold. |
| coupled_flux_phi_causal_branch | T13_CAUSAL_THERMAL_BRANCH_CLOSURE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_CAUSAL_FLUX_PHI_COUPLED_LANE | The named coupled branch passes arrival, ledger, convergence, and anti-manipulation checks. |
| causal_branch_selection_boundary | T13_CAUSAL_THERMAL_BRANCH_CLOSURE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_CAUSAL_THERMAL_BRANCH_SELECTION | The named branch is not silently promoted as the original conserved-C baseline. |
| normalized_ttg_measurement_operator | T13_DIMENSIONAL_PHI_THERMAL_OBSERVABLE_MAP | CLOSED_FOR_LANE |  |  | none | The TTG and UET normalized curves use the declared ratio operators with no SI claim. |
| phi_e_named_dimensional_comparator | T13_DIMENSIONAL_PHI_THERMAL_OBSERVABLE_MAP | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR, T13_PHI_E_REFERENCE_NORMALIZATION, T13_PHI_E_TTG_BRIDGE_CONDITIONAL | Phi_E is kept as a separate conditional lane and is not relabeled as base Phi. |
| base_phi_si_anchor | T13_DIMENSIONAL_PHI_THERMAL_OBSERVABLE_MAP | OPEN | CLOSED_FOR_CORE | T13_INPUT_BASE_PHI_SI_ALPHA_BETA | none | A declared dimensionful action/free-energy origin or an independent paired base-Phi/SI response record is accepted. |
| alpha_candidate_search_boundary | T13_ALPHA_PHI_K_INDEPENDENT_CALIBRATION | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_ALPHA_PHI_K_PAIRED_RECORD_SEARCH | All screened candidates are recorded and zero eligible paired records is reported without a substitute value. |
| normalized_alpha_scale_no_go | T13_ALPHA_PHI_K_INDEPENDENT_CALIBRATION | CLOSED_AS_NO_GO | CLOSED_AS_NO_GO |  | T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO | The transformation Delta_Phi -> s Delta_Phi and alpha -> alpha/s is recorded as the reason normalized data cannot identify alpha. |
| independent_alpha_record | T13_ALPHA_PHI_K_INDEPENDENT_CALIBRATION | OPEN | CLOSED_FOR_CORE | T13_INPUT_BASE_PHI_SI_ALPHA_BETA | none | One eligible non-holdout paired record or a derivation with an independently fixed SI scale is accepted. |
| natural_beta_action_lane | T13_UET_BRIDGE_BETA_SI_CORRESPONDENCE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_ACTION_THERMAL_STIFFNESS_BETA_LANE, T13_THERMAL_RESPONSE_BETA_CONTRACT | The action-origin coefficient and finite-temperature response functional are recorded with natural-unit limits. |
| beta_noncircularity_no_go | T13_UET_BRIDGE_BETA_SI_CORRESPONDENCE | CLOSED_AS_NO_GO | CLOSED_AS_NO_GO |  | T13_BETA_SYMBOL_SEPARATION_NONCIRCULARITY_NO_GO, T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO | No Landauer identity or target response is used to infer beta_UET or beta_T13. |
| normalized_beta_si_map | T13_UET_BRIDGE_BETA_SI_CORRESPONDENCE | OPEN | CLOSED_FOR_CORE | T13_INPUT_BASE_PHI_SI_ALPHA_BETA | none | The base-Phi field normalization and dimensionful free-energy scale are independently fixed and propagated. |
| normalized_charge_eos | T13_CHARGE_DENSITY_EOS | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT | The candidate EOS and independent-variable contract are machine-checked. |
| eos_stability_reciprocity | T13_CHARGE_DENSITY_EOS | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY, T13_UET_O2_THERMAL_STABILITY_BOUNDARY | Positivity, Maxwell reciprocity, and declared domain checks pass on the chosen branch. |
| finite_temperature_normal_component | T13_CHARGE_DENSITY_EOS | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE, T13_UET_O2_THERMODYNAMIC_NORMAL_COMPONENT_LANE | The normal component and its thermodynamic derivatives are linked to the same declared state. |
| physical_source_backed_eos | T13_CHARGE_DENSITY_EOS | OPEN | CLOSED_FOR_CORE | T13_INPUT_DING_TTG_SOURCE + T13_INPUT_BASE_PHI_SI_ALPHA_BETA | none | Finite-temperature coefficients, material regime, c_v uncertainty, and SI Phi normalization are accepted together. |
| formal_covariant_transport_interface | T13_COVARIANT_THERMAL_TRANSPORT | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY | The tensor, frame, and coefficient provenance contract is explicit without a default physical value. |
| microscopic_natural_kubo_lane | T13_COVARIANT_THERMAL_TRANSPORT | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH, T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE | The selected natural-unit correlator and response match are state-matched and finite-cutoff bounded. |
| standard_fluid_comparator_boundary | T13_COVARIANT_THERMAL_TRANSPORT | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_GATECH_STANDARD_TRANSPORT_COMPARATOR | Fourier/Cattaneo behavior is reported only as an internal simplified benchmark. |
| physical_uet_kubo_record | T13_COVARIANT_THERMAL_TRANSPORT | OPEN | CLOSED_FOR_CORE | T13_INPUT_PHYSICAL_TRANSPORT_MATCH | none | One source-backed or fully microscopic state-matched coefficient with uncertainty is admitted. |
| formal_sk_kms_entropy_interface | T13_SK_KMS_MATCHING | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT, T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE | The formal contour, KMS/FDT, retardedness, and positivity interfaces are machine-checked. |
| interacting_finite_temperature_sk_match | T13_SK_KMS_MATCHING | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE, T13_UET_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE | The declared interaction channels have state-matched retarded, KMS, and FDT witnesses. |
| physical_sk_transport_match | T13_SK_KMS_MATCHING | OPEN | CLOSED_FOR_CORE | T13_INPUT_PHYSICAL_TRANSPORT_MATCH | none | The microscopic response is connected to a physical coefficient and uncertainty without a synthetic substitute. |
| formal_entropy_current_positivity | T13_ENTROPY_CURRENT_DISSIPATIVE_BALANCE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE | The entropy current, force basis, and nonnegative production witness are explicit. |
| covariant_dissipative_balance | T13_ENTROPY_CURRENT_DISSIPATIVE_BALANCE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE, T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY | Heat exchange, entropy production, and conservation constraints close on the declared formal branch. |
| physical_entropy_production_mapping | T13_ENTROPY_CURRENT_DISSIPATIVE_BALANCE | OPEN | CLOSED_FOR_CORE | T13_INPUT_PHYSICAL_TRANSPORT_MATCH | none | The physical coefficient, SI heat flux, source uncertainty, and entropy-production uncertainty are linked. |
| source_identity_and_row_controller | T13_TTG_SOURCE_UNCERTAINTY_PACKAGE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE, T13_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY | The requested numeric payload fields, locators, units, uncertainty, preprocessing, row identity, and hash are fixed. |
| public_route_boundary | T13_TTG_SOURCE_UNCERTAINTY_PACKAGE | CLOSED_AS_NO_GO | CLOSED_AS_NO_GO |  | T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY, T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO | The checked public routes are bounded without claiming author-held data are absent. |
| candidate_reproduction_comparator | T13_TTG_SOURCE_UNCERTAINTY_PACKAGE | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY, T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION | Candidate numerical stability and sensitivity are recorded separately from Ding acceptance. |
| accepted_numeric_csrc | T13_TTG_SOURCE_UNCERTAINTY_PACKAGE | OPEN | CLOSED_FOR_CORE | T13_INPUT_DING_TTG_SOURCE | none | An authorized Ding package or accepted same-regime independent reproduction is admitted with source-grade uncertainty. |
| material_and_uncertainty_closure | T13_TTG_SOURCE_UNCERTAINTY_PACKAGE | OPEN | CLOSED_FOR_CORE | T13_INPUT_DING_TTG_SOURCE | none | The TTG material regime, same-state thermodynamic correction, and c_v uncertainty are closed at the same evidence grade. |
| finite_cutoff_heat_current_match | T13_HEAT_FLUX_ENTROPY_PRODUCTION_MAPPING | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_HEAT_CURRENT_KUBO_MATCH | The natural heat-current response matches the declared covariant moment lane at finite cutoff. |
| heat_current_continuum_boundary | T13_HEAT_FLUX_ENTROPY_PRODUCTION_MAPPING | CLOSED_AS_NO_GO | CLOSED_AS_NO_GO |  | T13_UET_O2_HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY | The failed extrapolation route is recorded as a no-go and is not relabeled as physical Kubo closure. |
| regularized_heat_current_lane | T13_HEAT_FLUX_ENTROPY_PRODUCTION_MAPPING | CLOSED_FOR_LANE | CLOSED_FOR_LANE |  | T13_UET_O2_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE | The named regularized lane passes its declared convergence and conservation checks without replacing the failed baseline. |
| physical_heat_flux_entropy_map | T13_HEAT_FLUX_ENTROPY_PRODUCTION_MAPPING | OPEN | CLOSED_FOR_CORE | T13_INPUT_DING_TTG_SOURCE + T13_INPUT_BASE_PHI_SI_ALPHA_BETA + T13_INPUT_PHYSICAL_TRANSPORT_MATCH | none | The SI Phi anchor, physical coefficient, source C_src, and uncertainty chain are all accepted on one state. |

MAJOR_RESULT_BREAKDOWN:
| Major result | Level | Lane | No-go | Core | Open | Dependency unlocked | Claim boundary |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| T13_CAUSAL_THERMAL_BRANCH_CLOSURE | CLOSED_AS_NO_GO | 3 | 1 | 0 | 0 | Named causal branch as a bounded Core input only; no Full Topic 13 or downstream unlock. | The conserved-C structural question is a scoped no-go and the named causal branch is retained separately; neither alone closes the full thermal bridge. |
| T13_DIMENSIONAL_PHI_THERMAL_OBSERVABLE_MAP | OPEN | 2 | 0 | 0 | 1 | None. | The normalized operator is usable now; no absolute SI Phi map is promoted until its scale is derived or independently calibrated. |
| T13_ALPHA_PHI_K_INDEPENDENT_CALIBRATION | OPEN | 1 | 1 | 0 | 1 | None; the Xie 2026 holdout remains locked. | No numeric alpha is emitted from normalized shapes, Landauer, Phi_E convention, or Xie 2026. |
| T13_UET_BRIDGE_BETA_SI_CORRESPONDENCE | PARTIAL | 1 | 1 | 0 | 1 | Natural-unit/formal beta lanes only; no SI unlock. | The natural-unit beta lane does not become normalized beta_T13 or an SI coefficient without an independent scale map. |
| T13_CHARGE_DENSITY_EOS | PARTIAL | 3 | 0 | 0 | 1 | Candidate normalized EOS lane only. | Formal normalized EOS and stability do not establish a physical finite-temperature EOS without coefficient and SI provenance. |
| T13_COVARIANT_THERMAL_TRANSPORT | PARTIAL | 3 | 0 | 0 | 1 | Formal/natural transport interface only. | A standard-fluid comparator or formal Kubo interface is not physical UET transport validation. |
| T13_SK_KMS_MATCHING | PARTIAL | 2 | 0 | 0 | 1 | Formal SK/KMS interface only. | An algebraic KMS identity or synthetic noise kernel is not physical transport evidence. |
| T13_ENTROPY_CURRENT_DISSIPATIVE_BALANCE | PARTIAL | 2 | 0 | 0 | 1 | Formal balance interface only. | Formal positivity is not a measurement of physical entropy production or a proof of full transport closure. |
| T13_TTG_SOURCE_UNCERTAINTY_PACKAGE | OPEN | 2 | 1 | 0 | 2 | Source acceptance policy only. | Public-source boundaries, figure-derived rows, and candidate PBTE reruns do not become Ding numeric validation without material/state and uncertainty acceptance. |
| T13_HEAT_FLUX_ENTROPY_PRODUCTION_MAPPING | PARTIAL | 2 | 1 | 0 | 1 | Formal heat-flux/entropy interface only. | The Cattaneo/Fourier controls and finite-cutoff Kubo matches are not a physical UET heat-flux prediction. |

ROOT_INPUT_PACKAGES:
| Package | Status | Accepted for Core | Open subresults | Missing acceptance fields |
| --- | --- | --- | --- | --- |
| T13_INPUT_DING_TTG_SOURCE | BLOCKED | false | physical_source_backed_eos, accepted_numeric_csrc, material_and_uncertainty_closure, physical_heat_flux_entropy_map | authorized_numeric_C_src_payload, accepted_independent_reproduction, Ding_material_state_match, source_grade_uncertainty |
| T13_INPUT_BASE_PHI_SI_ALPHA_BETA | BLOCKED | false | base_phi_si_anchor, independent_alpha_record, normalized_beta_si_map, physical_source_backed_eos, physical_heat_flux_entropy_map | eligible_paired_alpha_record, numeric_alpha_emitted, dimensional_bridge_open_inputs_closed, dimensionful_action_SI_map |
| T13_INPUT_PHYSICAL_TRANSPORT_MATCH | BLOCKED | false | physical_uet_kubo_record, physical_sk_transport_match, physical_entropy_production_mapping, physical_heat_flux_entropy_map | physical_coefficient_record, finite_temperature_transport_completion, physical_anchor_supplied, physical_heat_flux_entropy_link |

DEPENDENCY_UNLOCKED:
- Only the bounded causal branch and explicitly scoped comparator/formal lanes are available as inputs.
- Full Topic 13 Core closure, curved 3+1, Gravity, and full constitutive transport remain locked.

STATUS:
- claim_promotion=false; full_core_unlock=false.

WHAT_CHANGED:
- Added a complete result-level register so progress can be read as closed lanes, no-go results, Core handoffs, and open acceptance rows rather than as undifferentiated PASS/FAIL counts.

EQUATION_OR_MAPPING:
- y_TTG = Delta_Tq(t) / Delta_Tq(0); y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi.
- C_src(T) = sum_mu c_mu(T) remains source/state/uncertainty controlled.

VERIFICATION:
- This report is generated from the closure matrix, full gate, input-package audit, and minimal-input contract; it creates no scientific value.
- Source hashes remain in docs/core/artifacts/t13_full_closure_progress.json; holdout access remains {'calibration_path_may_read_holdout': False, 'target_fit_performed': False, 'xie_2026_accessed': False}.

CONTROLLING_BLOCKER:
- dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing; grouped input blockers: Ding-compatible source, independent base-Phi/SI/alpha/beta, and physical transport matching.

NEXT_ACTION:
- Acquire an accepted external input or independently derived SI normalization for an open row; do not rerun unchanged numeric gates as a substitute.
- Keep Xie 2026 metadata-only until the separate holdout preregistration and access gate authorize a final comparison.

CLAIM_BOUNDARY:
- This map reports research closure boundaries only. It does not claim Full Topic 13 closure, an SI temperature prediction, external validation, or global UET closure.

Generated from docs/core/artifacts/t13_full_closure_progress.json.
