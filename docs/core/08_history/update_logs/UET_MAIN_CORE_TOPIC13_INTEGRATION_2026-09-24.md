# Main Core Integration Update: Topic 13 Evidence Wave (2026-09-24)

This is a date-scoped Core integration addendum. It supplements, but does not rewrite, `UET_MAIN_THEORY_UPDATE_LOG.md`, the equation registry, or dependency gates.

MAJOR_RESULT_CLOSURE: `PARTIAL` for bounded normalized-observable and source-method subquestions only. This update closes no new Core dependency.

WHAT_IS_ACTUALLY_CLOSED:
- Ding 2022 supplementary-method boundary: the reviewed package documents separate phase/amplitude gratings, Savitzky-Golay smoothing for acoustic oscillations, and a typical waveform-error scale near 0.01 estimated from negative-delay samples. The reviewed text did not provide machine-readable waveform rows, pointwise uncertainty/covariance, mode-resolved `C_src`, or located filter-window/order settings.
- Normalized-scale identifiability: for nonzero constant `alpha`, `alpha*x(t)/(alpha*x(0)) = x(t)/x(0)`. Therefore normalized-shape comparison cannot identify the dimensional `alpha_Phi_K` scale. This is a scoped identifiability result, not an absolute-temperature calibration.
- Dip-time boundary: the selected damped-mode ansatz has a conditional first-dip formula, but its dispersion relation alone does not determine the measured dip without an independently specified initial-rate condition. This does not establish a physical TTG dip-time prediction.
- Figure-pixel sensitivity: excluding a manually inspected legend region removes previously flagged large blue-mask jumps in a challenger extraction. The post-hoc sensitivity check does not separate measured markers from simulated curves, recover author data, or validate UET.

WHAT_REMAINS_OPEN:
- The Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`, with `claim_promotion=false` and controlling blocker `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.
- Its seven recorded blockers remain: accepted numeric Ding-compatible `C_src` or same-regime reproduction; independent graphite `alpha_Phi_K`; normalized beta/SI scale correspondence; physical Kubo coefficient provenance; dimensional `Phi`-to-thermal observable map; TTG material-regime mapping; and source-grade `c_v` uncertainty.
- The physical pump-to-`(Phi, Pi)` initial-state map, physical heat-flux/entropy mapping, and complete graphite transport bridge remain open.

DEPENDENCY_UNLOCKED: None. The already-existing O(2)/He-4 `CLOSED_FOR_CORE` lane remains unchanged and is not transferred to graphite. Gravity and full constitutive transport remain locked by their existing dependencies.

STATUS: `PASS_SCOPED_SOURCE_METHOD_AND_NORMALIZED_IDENTIFIABILITY`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_CHANGED: This addendum records the Topic 13 handoff in the Core history. It makes no edits to the central equation registry, Core dependency graph, or Topic 13 canonical gate. The canonical Core theory log remains the source of its historical wave entries; this file is a dated integration supplement, not a claim that those central artifacts were regenerated.

EQUATION_OR_MAPPING:
```text
y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq = alpha_Phi_K * Delta_Phi

x(t) = exp(-gamma*t) cos(omega*t)
t_d = (pi - atan(gamma/omega)) / omega
```
The first three relations preserve the registered normalized measurement convention. The last two are conditional analytic diagnostics and are not a source-identified physical prediction.

VERIFICATION: The source-method audit reports `PASS_SUPPLEMENTARY_METHOD_BOUNDARY` (5 checks); the normalized identifiability audit reports `PASS_CONDITIONAL_DIP_TIME_IDENTIFIABILITY` (5 checks); focused tests reported 7 passes for the source/figure-boundary group and 3 passes for normalized dip-time. One normalized-dip test contains a self-comparison assertion and is not an independent check; the audit artifact and remaining assertions are the substantive evidence. Evidence hashes are listed below. No numeric Xie 2026 payload was read or used for calibration. A public summary from that holdout was incidentally exposed in the current research context, so future blind-use eligibility is `REVIEW_REQUIRED`; the holdout remains excluded pending review.

CONTROLLING_BLOCKER: The full Topic 13 gate's root controller is the missing dimensional `Phi` energy anchor or independent `alpha_Phi_K` calibration. Numeric source acceptance and physical transport/uncertainty closure are additional independent blockers listed above.

NEXT_ACTION: End the current open-ended loop with one explicit disposition after source and identifiability work: (1) derive the dimensional map from an accepted action and physical correspondence; (2) acquire an independent, provenance-complete calibration that does not use the target curve or holdout; or (3) record a scoped no-go/claim limitation to normalized shape and simulation. In parallel, request authorized Ding numeric rows with row identity and uncertainty or retain Fig. 1d as figure-derived comparison only. Review holdout eligibility before any future blind comparison.

CLAIM_BOUNDARY: These are documentary, analytic, and internal figure-sensitivity results. They do not externally validate graphite TTG, identify graphite `alpha_Phi_K`, close full Topic 13, unlock Gravity/transport, or promote a global UET claim.

## Latest Scoped Result: Phi_E Lane Composition (2026-09-24)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for rejecting silent identification of the two lane-specific Phi_E coordinates only.

WHAT_IS_ACTUALLY_CLOSED:
- The thermoelastic field-amplitude lane assigns Phi_E_field mass dimension E^1; the normalized energy-response lane assigns Phi_E_energy mass dimension E^0.
- Composing these lanes requires an explicit kappa_E with mass dimension E^-1. Dimensional agreement of the resulting alpha expressions does not determine kappa_E or its value.
- The thermoelastic C_p^V route and the fixed-volume c_v/C_src energy route have distinct boundary and material conditions; they are not interchangeable without a same-state observable map.

WHAT_REMAINS_OPEN:
- Derivation or independent calibration of kappa_E and the base-Phi-to-energy-density map.
- Physical Z_Phi and g_Phi_theta, source-locked e0 and c_v, and same-state material evidence.
- Correspondence among C_p^V, c_v, C_src, finite-q TTG initialization, detector response, and uncertainty.

DEPENDENCY_UNLOCKED: None. Explicit lane typing is a scoped result, not a physical or downstream dependency unlock.

STATUS: PASS_SCOPED_PHI_E_LANE_COMPOSITION_BOUNDARY (15/15 audit checks; focused test 5/5).

WHAT_CHANGED: Integrated the local F0-F4 lane-composition audit into the Core history. No central equation registry, accepted action, Topic 13 closure gate, or dependency graph was changed.

EQUATION_OR_MAPPING: Phi_E_field = Z_Phi*DeltaPhi_base; Phi_E_energy = Delta_u/e0; Phi_E_energy = kappa_E*Phi_E_field with [kappa_E]=E^-1. Conditional routes: alpha_thermoelastic = T*alpha_V*g_Phi_theta*Z_Phi/C_p^V and alpha_energy = (e0/c_v)*kappa_E*Z_Phi.

VERIFICATION: The local audit reports 15/15 structural/unit checks passed; focused tests report 5 passed. Audit SHA-256: 374ccb4f0bc2810685f9329b0b86e0f808e16401fdbf16513b12268c0d7bd72. No numeric source rows, target data, fit, or holdout payload were used. Blind-use eligibility for Xie 2026 remains REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE.

CONTROLLING_BLOCKER: The full Topic 13 controller remains the missing dimensional Phi energy anchor or independent alpha_Phi_K calibration. This audit narrows the composition question to the missing kappa_E/base-Phi energy map; it does not resolve the full controller.

NEXT_ACTION: Derive kappa_E and Z_Phi from an accepted action or obtain an independent, provenance-complete calibration for one declared material/state; then resolve heat-capacity/boundary correspondence before any target comparison.

CLAIM_BOUNDARY: This is a scoped no-go on silently identifying two lane coordinates. It emits no physical alpha_Phi_K, validates no graphite TTG result, closes no full Topic 13 bridge, and promotes no global UET claim.

## Latest Scoped Result: SI Phi Normalization Jacobian (2026-09-24)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the chain-rule requirement only.

WHAT_IS_ACTUALLY_CLOSED: Given Phi_normalized = Phi_covariant/Phi_scale and a natural coefficient differentiated with respect to covariant Phi, the normalized response coefficient requires Phi_scale_nat. The O(2) action-derived coefficient is explicitly differentiated with respect to its covariant Phi field, whose natural mass dimension is E^1. The existing SI helper applies E_ref/k_B but has no field-scale argument, so it cannot by itself convert that O(2) coefficient to K per normalized base Phi.

WHAT_REMAINS_OPEN: Phi_scale_nat and E_ref have no physical provenance; the generic SI contract does not connect the O(2) covariant derivative to normalized base Phi; the base-Phi-to-energy-density map and independent graphite alpha_Phi_K remain open.

DEPENDENCY_UNLOCKED: None.

STATUS: PASS_SCOPED_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY; 17/17 checks passed.

WHAT_CHANGED: Added a read-only Topic 13 formula-interface audit. The existing converter, action, equations, registry, and closure gates were not changed.

EQUATION_OR_MAPPING: alpha_Phi_K = (E_ref/k_B) * Phi_scale_nat * alpha_Phi_theta_covariant_nat; Phi_scale_nat = Phi_scale_SI/E_ref. If alpha_Phi_theta is already differentiated with respect to normalized Phi, the factor is already included and must not be applied twice.

VERIFICATION: The refined audit passes 17/17 checks; its focused and existing SI-conversion tests pass 9/9; Core path audit passes. Artifact SHA-256: 088c4294dfe8a487073ee84f1a28f48fc23c270f60c274d7f3beb5874e9cabf3. No numeric source rows, target data, fit, or holdout payload were consumed. Blind-use eligibility remains REVIEW_REQUIRED_AFTER_SESSION_EXPOSURE.

CONTROLLING_BLOCKER: The O(2)-to-base-normalized Phi scale and its provenance are missing.

NEXT_ACTION: Source-lock Phi_scale_nat and E_ref for the declared material/field route, then correct the generic SI contract to include the Jacobian before emitting any coefficient per normalized Phi.

CLAIM_BOUNDARY: This closes a mathematical interface requirement only. It emits no physical alpha_Phi_K, validates no graphite TTG response, and closes no full Topic 13/Core dependency.

## Evidence Identity

| Evidence | Result / scope | SHA-256 |
|:--|:--|:--|
| docs/core/07_artifacts/topic13/t13_si_phi_normalization_jacobian_audit.json | PASS_SCOPED_SI_PHI_NORMALIZATION_JACOBIAN_BOUNDARY; 17/17 checks; no physical alpha or unlock | 088c4294dfe8a487073ee84f1a28f48fc23c270f60c274d7f3beb5874e9cabf3 |
| docs/core/07_artifacts/topic13/t13_phi_e_lane_composition_boundary_audit.json | PASS_SCOPED_PHI_E_LANE_COMPOSITION_BOUNDARY; 15/15 checks; no physical alpha or unlock | 374ccb4f0bc2810685f9329b0b86e0f808e16401fdbf16513b12268c0d7bd72 |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/ding_2022_fig1d_legend_contamination_audit.json` | Post-hoc figure-pixel sensitivity diagnostic | `656f3c0ad3fe55b8742da8861674578fdcb0e8a74f657806a157abe225348d3d` |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/ding_2022_ttg_preprocessing_boundary_audit.json` | `PASS_SUPPLEMENTARY_METHOD_BOUNDARY` | `3844bbbc8c232648d273fc2813e7c9881eccb6fab9726d542889f9497b00048d` |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_normalized_dip_time_identifiability.json` | `PASS_CONDITIONAL_DIP_TIME_IDENTIFIABILITY` | `4791d35583f4cefeed5d6f3a07cec7fd6f11d783af7bc9462a49503ab0374704` |
| `docs/core/07_artifacts/topic13/t13_full_closure_progress.json` | O(2)/He-4 `CLOSED_FOR_CORE`; graphite external lane `OPEN` | `1d3614914c9d19525b0a2622c29a8845945bab172f582374ca2ee6e052807df1` |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json` | `BLOCKED_OPEN_T13_FULL_BRIDGE`; `claim_promotion=false` | `7df4ec9a05d1c858dfd3a43ac1a32bd677da6d57d30c20c502fdb27a8447ccc6` |
