"""Acceptance contract for closing Topic 13 at the Full Topic level.

The canonical full bridge gate supplies current readiness.  This module only
declares the required major results and their evidence-producing subresults.
"""

from __future__ import annotations

from typing import Any


TOPIC_ID = "0.13_Thermodynamic_Bridge"


# Full-topic closure is controlled by three evidence packages. Existing lane
# artifacts can close the formal pieces, but these packages carry the minimum
# non-derivable inputs needed for a Core-ready physical bridge.
CLOSURE_INPUT_PACKAGES: tuple[dict[str, Any], ...] = (
    {
        "package_id": "T13_INPUT_DING_TTG_SOURCE",
        "label": "Ding-compatible TTG source package",
        "status": "OPEN_EXTERNAL_INPUT",
        "purpose": "Accept the numeric source and same-regime thermodynamic uncertainty needed to connect PBTE energy to Delta_Tq.",
        "minimum_records": [
            "mode-resolved C_src(T) rows in J m^-3 K^-1 with temperature/state identity",
            "material morphology, isotope/defect state, TTG response contract, and PBTE convergence record",
            "source locator, permission, preprocessing, row identity, uncertainty, and SHA-256",
            "same-grade alpha_V and K_T or a justified c_v conversion with propagated uncertainty",
        ],
        "unlocks_subresults": [
            "accepted_numeric_csrc",
            "material_and_uncertainty_closure",
            "physical_source_backed_eos",
            "physical_heat_flux_entropy_map",
        ],
        "controlling_blockers": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "material_regime_mapping_to_TTG_not_closed",
            "c_v_source_uncertainty_not_closed",
        ],
        "claim_boundary": "A comparator or figure-derived normalized curve is not accepted as the Ding numeric source without material/state and uncertainty equivalence.",
    },
    {
        "package_id": "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "label": "Base-Phi SI anchor and independent alpha/beta package",
        "status": "OPEN_EXTERNAL_OR_DERIVATION_INPUT",
        "purpose": "Fix the otherwise non-identifiable scale between normalized Phi and a dimensional energy or temperature response.",
        "minimum_records": [
            "dimensionful action/free-energy origin with coefficient provenance, or an independent paired base-Phi/SI response record",
            "Phi amplitude, reference state, field normalization, and e0 in declared units",
            "paired Delta_Phi with Delta_Tq or Delta_u_ph, uncertainty, locator, preprocessing, row identity, and hash",
            "beta derivation separate from Landauer and from target/holdout tuning, with limiting-case and uncertainty checks",
        ],
        "unlocks_subresults": [
            "base_phi_si_anchor",
            "independent_alpha_record",
            "normalized_beta_si_map",
            "physical_source_backed_eos",
            "physical_heat_flux_entropy_map",
        ],
        "controlling_blockers": [
            "dimensional_phi_to_thermal_observable_map_missing",
            "alpha_Phi_K_independent_calibration_missing",
            "normalized_beta_and_SI_scale_correspondence_missing",
        ],
        "claim_boundary": "Normalized Phi shapes, Phi_E comparators, Landauer, and Xie 2026 cannot supply this scale by themselves.",
    },
    {
        "package_id": "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        "label": "Physical Kubo and SK/KMS transport package",
        "status": "OPEN_MICROSCOPIC_OR_EXTERNAL_INPUT",
        "purpose": "Connect the declared formal response lanes to one state-matched physical transport coefficient and its entropy/heat-flux consequences.",
        "minimum_records": [
            "coefficient_name, value, units, frame, temperature, chemical potential, and space-response state",
            "retarded-correlator formula identifier, source locator, source hash, evidence status, and uncertainty",
            "finite-temperature normal/condensed matching, KMS/FDT residuals, and no synthetic substitute",
            "heat-flux and entropy-production propagation on the same state, including uncertainty",
        ],
        "unlocks_subresults": [
            "physical_uet_kubo_record",
            "physical_sk_transport_match",
            "physical_entropy_production_mapping",
            "physical_heat_flux_entropy_map",
        ],
        "controlling_blockers": [
            "physical_Kubo_coefficient_record_missing",
        ],
        "claim_boundary": "The existing natural-unit Kubo and formal SK/KMS lanes remain lane evidence until a state-matched physical record passes this contract.",
    },
)


MAJOR_RESULT_CONTRACTS: dict[str, dict[str, Any]] = {
    "causal_structure": {
        "major_result_id": "T13_CAUSAL_THERMAL_BRANCH_CLOSURE",
        "topic": TOPIC_ID,
        "equation_or_mapping": {
            "baseline": "conserved-C local-gradient finite-cone candidate",
            "named_branch": "coupled conserved-flux/Phi telegraph branch",
            "gate": "pre_arrival_leakage <= 1e-6; arrival_target > 0",
        },
        "units": {"C": "lane-specific collective coordinate units", "Phi": "normalized effective response variable", "leakage": "dimensionless"},
        "derivation_class": "structural no-go plus explicit finite-cone verification",
        "observable": ["pre-arrival leakage", "arrival target", "energy ledger", "convergence"],
        "data_role": "INTERNAL_VERIFICATION",
        "claim_boundary": "The conserved-C structural question is a scoped no-go and the named causal branch is retained separately; neither alone closes the full thermal bridge.",
        "acceptance_criteria": [
            "formal no-go or explicit regularization is recorded",
            "pre-arrival leakage <= 1e-6 without clipping or cone padding",
            "arrival target is nonzero",
            "temporal/spatial convergence and energy-ledger closure pass",
            "C, Phi, R_gen, and R_obs retain their declared meanings",
        ],
        "blocker_keys": [],
        "evidence_paths": [
            "docs/core/artifacts/conserved_c_finite_cone_no_go_assessment.json",
            "docs/core/artifacts/matter_space_conserved_flux_telegraph_verification.json",
            "docs/core/artifacts/matter_space_flux_phi_coupled_verification.json",
        ],
        "required_subresults": [
            {"subresult_id": "conserved_c_local_gradient_no_go", "label": "Conserved-C local-gradient no-go", "required_closure_level": "CLOSED_AS_NO_GO", "gate_key": "causal_full_candidate_or_formal_no_go_branch", "acceptance": "The principal-symbol incompatibility is scoped to the declared baseline and recorded without deleting it."},
            {"subresult_id": "finite_cone_telegraph_branch", "label": "Named finite-cone telegraph branch", "evidence_result_ids": ["T13_CAUSAL_FLUX_TELEGRAPH_BRANCH"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The branch has explicit equations, domain-of-dependence checks, and the unchanged leakage threshold."},
            {"subresult_id": "coupled_flux_phi_causal_branch", "label": "Coupled flux-Phi causal branch", "evidence_result_ids": ["T13_CAUSAL_FLUX_PHI_COUPLED_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The named coupled branch passes arrival, ledger, convergence, and anti-manipulation checks."},
            {"subresult_id": "causal_branch_selection_boundary", "label": "Baseline versus named-branch selection boundary", "evidence_result_ids": ["T13_CAUSAL_THERMAL_BRANCH_SELECTION"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The named branch is not silently promoted as the original conserved-C baseline."},
        ],
    },
    "dimensional_phi_to_thermal_observable_map": {
        "major_result_id": "T13_DIMENSIONAL_PHI_THERMAL_OBSERVABLE_MAP",
        "topic": TOPIC_ID,
        "equation_or_mapping": {
            "measurement": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            "uet_measurement": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            "dimensional": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "conditional_energy": "Phi_E = s_material * Phi_base; e0 = c_v(T_ref) * T_ref",
        },
        "units": {"y_TTG": "dimensionless", "Delta_Tq": "K", "Delta_Phi": "normalized Phi until an SI anchor exists", "alpha_Phi_K": "K per normalized Phi", "e0": "J m^-3"},
        "derivation_class": "conditional dimensional derivation plus independent calibration requirement",
        "observable": "TTG thermal response amplitude Delta_Tq",
        "data_role": "DERIVED_OR_CALIBRATION",
        "claim_boundary": "The normalized operator is usable now; no absolute SI Phi map is promoted until its scale is derived or independently calibrated.",
        "acceptance_criteria": [
            "normalized and dimensional operators remain separate",
            "Phi-to-energy or Phi-to-temperature map has an explicit SI anchor",
            "all coefficients have units and uncertainty propagation",
            "the map is not selected from the target curve or Xie holdout",
        ],
        "blocker_keys": ["dimensional_phi_to_thermal_observable_map_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_dimensional_bridge_contract_audit.json",
            "docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json",
            "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json",
        ],
        "required_subresults": [
            {"subresult_id": "normalized_ttg_measurement_operator", "label": "Normalized TTG measurement operator", "current_status": "CLOSED_FOR_LANE", "acceptance": "The TTG and UET normalized curves use the declared ratio operators with no SI claim."},
            {"subresult_id": "phi_e_named_dimensional_comparator", "label": "Named Phi_E dimensional comparator", "evidence_result_ids": ["T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR", "T13_PHI_E_REFERENCE_NORMALIZATION", "T13_PHI_E_TTG_BRIDGE_CONDITIONAL"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "Phi_E is kept as a separate conditional lane and is not relabeled as base Phi."},
            {"subresult_id": "base_phi_si_anchor", "label": "Base-Phi SI energy/temperature anchor", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "A declared dimensionful action/free-energy origin or an independent paired base-Phi/SI response record is accepted."},
        ],
    },
    "independent_alpha_Phi_K": {
        "major_result_id": "T13_ALPHA_PHI_K_INDEPENDENT_CALIBRATION",
        "topic": TOPIC_ID,
        "equation_or_mapping": "alpha_Phi_K = (e0 / c_v) * s_material; Delta_Tq = alpha_Phi_K * Delta_Phi",
        "units": {"alpha_Phi_K": "K per normalized Phi", "e0": "J m^-3", "c_v": "J m^-3 K^-1", "s_material": "dimensionless scale map only when independently derived"},
        "derivation_class": "derived only from a declared scale origin or external independent calibration",
        "observable": "TTG thermal amplitude per base-Phi amplitude",
        "data_role": "CALIBRATION_ONLY",
        "claim_boundary": "No numeric alpha is emitted from normalized shapes, Landauer, Phi_E convention, or Xie 2026.",
        "acceptance_criteria": [
            "paired base-Phi amplitude and SI thermal/energy response",
            "source identity, locator, preprocessing, row identity, units, uncertainty, and hash",
            "independence statement proving the record was not selected from the target curve",
            "calibration path audit proves Xie 2026 was not read",
        ],
        "blocker_keys": ["alpha_Phi_K_independent_calibration_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json",
            "docs/core/artifacts/t13_alpha_phi_k_identifiability_audit.json",
            "docs/core/artifacts/t13_base_phi_independent_calibration_requirement.json",
        ],
        "required_subresults": [
            {"subresult_id": "alpha_candidate_search_boundary", "label": "Independent alpha candidate search boundary", "evidence_result_ids": ["T13_ALPHA_PHI_K_PAIRED_RECORD_SEARCH"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "All screened candidates are recorded and zero eligible paired records is reported without a substitute value."},
            {"subresult_id": "normalized_alpha_scale_no_go", "label": "Normalized-alpha scale identifiability no-go", "evidence_result_ids": ["T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO"], "required_closure_level": "CLOSED_AS_NO_GO", "acceptance": "The transformation Delta_Phi -> s Delta_Phi and alpha -> alpha/s is recorded as the reason normalized data cannot identify alpha."},
            {"subresult_id": "independent_alpha_record", "label": "Independent numeric alpha record with uncertainty", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "One eligible non-holdout paired record or a derivation with an independently fixed SI scale is accepted."},
        ],
    },
    "beta_and_si_correspondence": {
        "major_result_id": "T13_UET_BRIDGE_BETA_SI_CORRESPONDENCE",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"normalized": "beta_T13 = T0 * (d a_Phi / dT)|T0", "natural": "beta_phi_natural = T * partial_T(partial_Phi^2 Omega_T)", "rule": "Landauer k_B T ln(2) is an imported constraint, not a beta derivation"},
        "units": {"beta_T13": "normalized local temperature slope", "beta_phi_natural": "action-defined natural-unit coefficient", "SI_map": "requires declared field and energy normalization"},
        "derivation_class": "non-circular action-origin formal derivation plus SI correspondence gate",
        "observable": "temperature-dependent Phi response coefficient",
        "data_role": "DERIVED_WITH_EXTERNAL_SCALE_INPUT",
        "claim_boundary": "The natural-unit beta lane does not become normalized beta_T13 or an SI coefficient without an independent scale map.",
        "acceptance_criteria": ["beta origin is separate from Landauer identity", "field normalization, energy reference, and Kelvin scale are declared", "normalized beta and uncertainty are derived without holdout fitting", "limiting cases and unit closure pass"],
        "blocker_keys": ["normalized_beta_and_SI_scale_correspondence_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json",
            "docs/core/artifacts/t13_beta_symbol_separation_noncircularity_audit.json",
            "docs/core/artifacts/t13_uet_o2_action_thermal_stiffness_beta_audit.json",
        ],
        "required_subresults": [
            {"subresult_id": "natural_beta_action_lane", "label": "Action-origin natural beta/stiffness lane", "evidence_result_ids": ["T13_UET_O2_ACTION_THERMAL_STIFFNESS_BETA_LANE", "T13_THERMAL_RESPONSE_BETA_CONTRACT"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The action-origin coefficient and finite-temperature response functional are recorded with natural-unit limits."},
            {"subresult_id": "beta_noncircularity_no_go", "label": "Beta/Landauer non-circularity boundary", "evidence_result_ids": ["T13_BETA_SYMBOL_SEPARATION_NONCIRCULARITY_NO_GO", "T13_BETA_ACTION_NORMALIZED_CORRESPONDENCE_NO_GO"], "required_closure_level": "CLOSED_AS_NO_GO", "acceptance": "No Landauer identity or target response is used to infer beta_UET or beta_T13."},
            {"subresult_id": "normalized_beta_si_map", "label": "Normalized beta to SI correspondence", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "The base-Phi field normalization and dimensionful free-energy scale are independently fixed and propagated."},
        ],
    },
    "charge_density_eos": {
        "major_result_id": "T13_CHARGE_DENSITY_EOS",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"eos": "n_q = partial_mu p(T, mu, Phi)", "stability": "partial_mu n_q >= 0", "reciprocity": "mixed thermodynamic derivatives commute on the declared lane"},
        "units": {"p": "J m^-3 when dimensionful; natural-unit pressure in formal lane", "n_q": "declared charge-density units", "susceptibility": "charge-density per chemical-potential unit"},
        "derivation_class": "action-derived normalized EOS plus source-backed finite-temperature closure",
        "observable": "charge density, susceptibility, and thermal response",
        "data_role": "DERIVED_PLUS_EXTERNAL_INPUT",
        "claim_boundary": "Formal normalized EOS and stability do not establish a physical finite-temperature EOS without coefficient and SI provenance.",
        "acceptance_criteria": ["EOS origin and independent variables are explicit", "stability, reciprocity, and Gibbs-Duhem checks pass", "finite-temperature normal component is declared and matched", "physical coefficients, uncertainty, and Phi/SI map are source-backed"],
        "blocker_keys": ["c_v_source_uncertainty_not_closed", "material_regime_mapping_to_TTG_not_closed"],
        "evidence_paths": [
            "docs/core/artifacts/t13_collective_response_eos_stability_audit.json",
            "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json",
        ],
        "required_subresults": [
            {"subresult_id": "normalized_charge_eos", "label": "Normalized charge-density EOS", "evidence_result_ids": ["T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The candidate EOS and independent-variable contract are machine-checked."},
            {"subresult_id": "eos_stability_reciprocity", "label": "EOS stability and reciprocity", "evidence_result_ids": ["T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY", "T13_UET_O2_THERMAL_STABILITY_BOUNDARY"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "Positivity, Maxwell reciprocity, and declared domain checks pass on the chosen branch."},
            {"subresult_id": "finite_temperature_normal_component", "label": "Finite-temperature normal component", "evidence_result_ids": ["T13_UET_O2_FINITE_T_QUASIPARTICLE_EOS_LANE", "T13_UET_O2_THERMODYNAMIC_NORMAL_COMPONENT_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The normal component and its thermodynamic derivatives are linked to the same declared state."},
            {"subresult_id": "physical_source_backed_eos", "label": "Physical source-backed EOS coefficients", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "Finite-temperature coefficients, material regime, c_v uncertainty, and SI Phi normalization are accepted together."},
        ],
    },
    "covariant_thermal_transport": {
        "major_result_id": "T13_COVARIANT_THERMAL_TRANSPORT",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"constitutive": "q^mu = constitutive_response(Phi, T, gradients, state)", "coefficient": "KuboCoefficientRecord -> physical coefficient only after provenance gate", "comparator": "Fourier/Cattaneo/standard-fluid controls remain separate"},
        "units": {"q": "W m^-2 when SI heat flux is established", "conductivity": "source-specific SI units", "formal_transport": "natural-unit or conditional interface"},
        "derivation_class": "covariant constitutive interface plus microscopic Kubo or external coefficient match",
        "observable": "heat flux and thermal transport coefficient",
        "data_role": "SYNTHETIC_CONTROL_PLUS_EXTERNAL_OR_MICROSCOPIC_INPUT",
        "claim_boundary": "A standard-fluid comparator or formal Kubo interface is not physical UET transport validation.",
        "acceptance_criteria": ["constitutive tensor and frame conventions are explicit", "finite-temperature normal and condensed sectors are stated", "physical Kubo coefficient has state, unit, locator, hash, and uncertainty", "stability, causality, and entropy constraints pass without replacing the baseline"],
        "blocker_keys": ["physical_Kubo_coefficient_record_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json",
            "docs/core/artifacts/t13_transport_kms_entropy_status_boundary_audit.json",
        ],
        "required_subresults": [
            {"subresult_id": "formal_covariant_transport_interface", "label": "Formal covariant transport interface", "evidence_result_ids": ["T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The tensor, frame, and coefficient provenance contract is explicit without a default physical value."},
            {"subresult_id": "microscopic_natural_kubo_lane", "label": "Matched microscopic natural-unit Kubo lane", "evidence_result_ids": ["T13_UET_O2_MICROSCOPIC_FINITE_CUTOFF_KUBO_MATCH", "T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The selected natural-unit correlator and response match are state-matched and finite-cutoff bounded."},
            {"subresult_id": "standard_fluid_comparator_boundary", "label": "Standard-fluid comparator boundary", "evidence_result_ids": ["T13_GATECH_STANDARD_TRANSPORT_COMPARATOR"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "Fourier/Cattaneo behavior is reported only as an internal simplified benchmark."},
            {"subresult_id": "physical_uet_kubo_record", "label": "Physical UET Kubo coefficient record", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "One source-backed or fully microscopic state-matched coefficient with uncertainty is admitted."},
        ],
    },
    "sk_kms_matching": {
        "major_result_id": "T13_SK_KMS_MATCHING",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"kms": "G^K(omega) = coth(beta omega / 2) * (G^R(omega) - G^A(omega))", "retarded": "Im G^R has the declared sign and analytic half-plane", "fdt": "noise/dissipation relation is state matched"},
        "units": {"correlators": "operator-dependent", "beta": "inverse temperature in the declared unit system", "noise": "coefficient-specific units"},
        "derivation_class": "formal SK/KMS interface plus microscopic finite-temperature matching",
        "observable": "retarded response, spectral density, and fluctuation-dissipation relation",
        "data_role": "DERIVED_FORMAL_PLUS_MICROSCOPIC_MATCH",
        "claim_boundary": "An algebraic KMS identity or synthetic noise kernel is not physical transport evidence.",
        "acceptance_criteria": ["SK contour, retarded/advanced/Keldysh conventions, and KMS sign are explicit", "spectral positivity and FDT checks pass on the declared state", "microscopic response and coefficient provenance are matched", "the interface is linked to the entropy and heat-flux records"],
        "blocker_keys": ["physical_Kubo_coefficient_record_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json",
            "docs/core/artifacts/t13_transport_kms_entropy_status_boundary_audit.json",
        ],
        "required_subresults": [
            {"subresult_id": "formal_sk_kms_entropy_interface", "label": "Formal SK/KMS/FDT interface", "evidence_result_ids": ["T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT", "T13_UET_O2_OPEN_SYSTEM_SK_KMS_ENTROPY_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The formal contour, KMS/FDT, retardedness, and positivity interfaces are machine-checked."},
            {"subresult_id": "interacting_finite_temperature_sk_match", "label": "Interacting finite-temperature SK/KMS match", "evidence_result_ids": ["T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE", "T13_UET_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The declared interaction channels have state-matched retarded, KMS, and FDT witnesses."},
            {"subresult_id": "physical_sk_transport_match", "label": "Physical SK/KMS-to-transport match", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "The microscopic response is connected to a physical coefficient and uncertainty without a synthetic substitute."},
        ],
    },
    "entropy_current_and_dissipative_balance": {
        "major_result_id": "T13_ENTROPY_CURRENT_DISSIPATIVE_BALANCE",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"entropy": "nabla_mu J_S^mu = q_perp^2/(kappa T^2) + X_A L^(AB) X_B >= 0", "balance": "matter/UET energy exchange is explicit and does not silently backreact R_gen"},
        "units": {"J_S": "entropy current units in the declared SI or natural system", "entropy_production": "entropy per volume per time", "L": "Onsager coefficient-specific units"},
        "derivation_class": "formal entropy-current construction plus physical dissipative matching",
        "observable": "entropy production, heat flux, and energy-exchange balance",
        "data_role": "DERIVED_FORMAL_PLUS_EXTERNAL_OR_MICROSCOPIC_INPUT",
        "claim_boundary": "Formal positivity is not a measurement of physical entropy production or a proof of full transport closure.",
        "acceptance_criteria": ["entropy current and forces are defined in one frame and unit system", "Onsager/positivity conditions pass", "dissipative-Bianchi or energy-exchange balance closes on the same state", "uncertainty is propagated from heat-flux and thermal-response inputs"],
        "blocker_keys": ["physical_Kubo_coefficient_record_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_transport_kms_entropy_status_boundary_audit.json",
            "docs/core/artifacts/t13_flat_thermodynamic_bridge_components_gate.json",
        ],
        "required_subresults": [
            {"subresult_id": "formal_entropy_current_positivity", "label": "Formal entropy-current positivity", "evidence_result_ids": ["T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The entropy current, force basis, and nonnegative production witness are explicit."},
            {"subresult_id": "covariant_dissipative_balance", "label": "Covariant dissipative balance", "evidence_result_ids": ["T13_UET_O2_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE", "T13_TRANSPORT_KMS_ENTROPY_STATUS_BOUNDARY"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "Heat exchange, entropy production, and conservation constraints close on the declared formal branch."},
            {"subresult_id": "physical_entropy_production_mapping", "label": "Physical entropy-production mapping", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "The physical coefficient, SI heat flux, source uncertainty, and entropy-production uncertainty are linked."},
        ],
    },
    "heat_flux_entropy_production_mapping": {
        "major_result_id": "T13_HEAT_FLUX_ENTROPY_PRODUCTION_MAPPING",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"source_response": "C_src(T) = sum_mu c_mu(T); Delta_Tq = Delta_u_ph / C_src(T)", "heat_flux": "q^mu = thermal_response(Phi, T, gradients, state)", "entropy": "nabla_mu J_S^mu >= 0"},
        "units": {"C_src": "J m^-3 K^-1", "Delta_u_ph": "J m^-3", "Delta_Tq": "K", "q": "W m^-2 when SI map is closed"},
        "derivation_class": "source-to-observable mapping with formal covariant heat-current lift",
        "observable": "TTG Delta_Tq, heat flux, and entropy production",
        "data_role": "DERIVED_PLUS_EXTERNAL_VALIDATION_INPUT",
        "claim_boundary": "The Cattaneo/Fourier controls and finite-cutoff Kubo matches are not a physical UET heat-flux prediction.",
        "acceptance_criteria": ["C_src, Delta_u_ph, Delta_Tq, heat flux, and entropy production share one state", "all units and uncertainty propagation are explicit", "the physical heat-current coefficient is source-backed or microscopically matched", "R_gen remains a derived history trace with no unregistered backreaction"],
        "blocker_keys": ["physical_Kubo_coefficient_record_missing", "dimensional_phi_to_thermal_observable_map_missing"],
        "evidence_paths": [
            "docs/core/artifacts/t13_energy_response_bridge_audit.json",
            "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json",
            "docs/core/artifacts/t13_uet_o2_heat_current_kubo_match_audit.json",
        ],
        "required_subresults": [
            {"subresult_id": "finite_cutoff_heat_current_match", "label": "State-matched finite-cutoff heat-current match", "evidence_result_ids": ["T13_UET_O2_HEAT_CURRENT_KUBO_MATCH"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The natural heat-current response matches the declared covariant moment lane at finite cutoff."},
            {"subresult_id": "heat_current_continuum_boundary", "label": "Heat-current continuum boundary", "evidence_result_ids": ["T13_UET_O2_HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY"], "required_closure_level": "CLOSED_AS_NO_GO", "acceptance": "The failed extrapolation route is recorded as a no-go and is not relabeled as physical Kubo closure."},
            {"subresult_id": "regularized_heat_current_lane", "label": "Named regularized heat-current lane", "evidence_result_ids": ["T13_UET_O2_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The named regularized lane passes its declared convergence and conservation checks without replacing the failed baseline."},
            {"subresult_id": "physical_heat_flux_entropy_map", "label": "Physical SI heat-flux/entropy map", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "The SI Phi anchor, physical coefficient, source C_src, and uncertainty chain are all accepted on one state."},
        ],
    },
    "source_and_uncertainty": {
        "major_result_id": "T13_TTG_SOURCE_UNCERTAINTY_PACKAGE",
        "topic": TOPIC_ID,
        "equation_or_mapping": {"source": "C_src(T) = sum_mu c_mu(T)", "observable": "Delta_Tq = Delta_u_ph / C_src(T)", "record": "source identity + locator + units + uncertainty + preprocessing + row identity + hash"},
        "units": {"C_src": "J m^-3 K^-1", "Delta_u_ph": "J m^-3", "Delta_Tq": "K"},
        "derivation_class": "source provenance and independent reproduction acceptance",
        "observable": "TTG source C_src(T) and thermal response",
        "data_role": "DERIVED/CALIBRATION/TRAINING_COMPARISON/HOLDOUT",
        "claim_boundary": "Public-source boundaries, figure-derived rows, and candidate PBTE reruns do not become Ding numeric validation without material/state and uncertainty acceptance.",
        "acceptance_criteria": ["Ding numeric C_src payload or accepted same-regime independent PBTE reproduction", "material/state mapping and mode-resolved row identity", "source-grade uncertainty and convergence package", "data-role separation and hash audit", "Xie 2026 remains locked and unread by calibration/fitting paths"],
        "blocker_keys": ["ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing", "material_regime_mapping_to_TTG_not_closed", "c_v_source_uncertainty_not_closed"],
        "evidence_paths": [
            "docs/core/artifacts/t13_ding_alternate_public_dataset_discovery_boundary_audit.json",
            "docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json",
            "docs/core/artifacts/t13_independent_csrc_acceptance_contract.json",
            "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json",
            "docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json",
        ],
        "required_subresults": [
            {"subresult_id": "source_identity_and_row_controller", "label": "Source identity and row controller", "evidence_result_ids": ["T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE", "T13_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "The requested numeric payload fields, locators, units, uncertainty, preprocessing, row identity, and hash are fixed."},
            {"subresult_id": "public_route_boundary", "label": "Public Ding route boundary", "evidence_result_ids": ["T13_DING_ALTERNATE_PUBLIC_DATASET_DISCOVERY_BOUNDARY", "T13_DING_PBTE_OA_NUMERIC_INPUT_NO_GO"], "required_closure_level": "CLOSED_AS_NO_GO", "acceptance": "The checked public routes are bounded without claiming author-held data are absent."},
            {"subresult_id": "candidate_reproduction_comparator", "label": "Independent PBTE candidate reproduction comparator", "evidence_result_ids": ["T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY", "T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION"], "required_closure_level": "CLOSED_FOR_LANE", "acceptance": "Candidate numerical stability and sensitivity are recorded separately from Ding acceptance."},
            {"subresult_id": "accepted_numeric_csrc", "label": "Accepted Ding-compatible numeric C_src(T)", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "An authorized Ding package or accepted same-regime independent reproduction is admitted with source-grade uncertainty."},
            {"subresult_id": "material_and_uncertainty_closure", "label": "Material regime and uncertainty closure", "current_status": "OPEN", "required_closure_level": "CLOSED_FOR_CORE", "acceptance": "The TTG material regime, same-state thermodynamic correction, and c_v uncertainty are closed at the same evidence grade."},
        ],
    },
}
