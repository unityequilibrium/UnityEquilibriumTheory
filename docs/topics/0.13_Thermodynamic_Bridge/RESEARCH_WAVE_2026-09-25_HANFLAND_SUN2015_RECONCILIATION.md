# Topic 13 Research Wave: Hanfland-Sun 2015 Raman Reconciliation (2026-09-25)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for a conditional Raman source-model reconciliation only.

WHAT_IS_ACTUALLY_CLOSED:
- Sun et al.'s published 0 K DFT axial coefficient has the sign and units needed to reproduce its reported E2g(2) frequency shift to printed precision.
- Holding that rounded DFT coefficient fixed, Hanfland's Table II pressure-slope route gives conditional gamma=2.07934 with endpoint sensitivity [1.93693, 2.22722]. The separate abstract absolute-slope route gives gamma=2.08970 with endpoint sensitivity [1.84537, 2.35168]. These endpoint rectangles are not confidence intervals.
- Sun's reported gamma=1.90 predicts a pressure slope whose propagated rectangle does not overlap Hanfland's narrow Table II slope interval, but does overlap the broader abstract-derived interval. The routes are therefore reconciliation-sensitive; their difference does not reject the DFT model because fit ranges and temperatures differ and DFT model uncertainty/covariance are unreported.
- Sun's DFT value is a model condition, not an independent measurement. Empirical rank gain is zero; the measured one-mode constraint still has rank 1 for two unknown strain components.

WHAT_REMAINS_OPEN:
- A source-locked independent axial-strain Raman row at a matched material state, plus uncertainty and covariance.
- Uncertainty/model error for the DFT axial coefficient and transfer from 0 K calculation to 300 K measurement.
- Raman-mode-to-UET observable correspondence, the dimensional Phi energy anchor, and independent graphite alpha_Phi_K calibration.
- Numeric Ding-compatible C_src, TTG material/initial-state map, and the remaining EOS, transport, SK/KMS, entropy, and heat-flux closure.

DEPENDENCY_UNLOCKED: None. Core equation registry and dependency gates are unchanged.

STATUS: PASS_CONDITIONAL_SOURCE_MODEL_RECONCILIATION; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE with claim_promotion=false.

WHAT_CHANGED: Added a published DFT comparator package, deterministic reconciliation audit, focused tests, and source-row/evidence hashes. No fit, physical UET coefficient, or holdout use was introduced.

EQUATION_OR_MAPPING: dln(nu)/dP = 2*gamma/B_a + gamma_prime/B_c; gamma = (dln(nu)/dP - gamma_prime/B_c)*B_a/2. Conditional spectral ratios are D_ab/x=-2*gamma and D_c/x=-2*gamma_prime; they are not identified as a physical UET D tensor.

VERIFICATION: Focused unittest suite: 5 passed. Audit status: PASS_CONDITIONAL_SOURCE_MODEL_RECONCILIATION. Artifact SHA-256: BC4E0671129ABC7291B161503FE857D74C1969B6F41350A2816067345090FFAD. Full-gate SHA-256: 20cc32438f365e3a4cee4b22954665c41447aec751f30a4b80cdf360744455eb. Audit asserts the Hanfland PDF hash; no Xie 2026 data were accessed.

CONTROLLING_BLOCKER: For this Raman lane, independent same-state axial-strain evidence and its uncertainty are missing. The full Topic 13 controller remains dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing.

NEXT_ACTION: Seek an allowed, directly located axial-strain Raman measurement with row-level uncertainty at a comparable graphite state. In parallel, resolve the dimensional Phi anchor/independent alpha calibration; if neither is obtainable, keep the thermal-scale claim limited rather than substituting DFT for experiment.

CLAIM_BOUNDARY: This is a conditional graphite Raman source/model comparison, not an independent experimental constraint, UET derivation, physical D tensor, alpha_Phi_K calibration, TTG validation, Full Topic 13 closure, dependency unlock, or global UET promotion.

EVIDENCE_PATHS:
- docs/core/07_artifacts/topic13/t13_hanfland_sun2015_reconciliation.json
- docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/hanfland_1989_raman_deformation_source_package.json
- docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/sun_2015_graphite_raman_strain_model_source_package.json
- docs/scripts/audit/audit_topic13_hanfland_sun2015_reconciliation.py
- docs/core/05_tests/regression/root/test_topic13_hanfland_sun2015_reconciliation.py
- docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json
