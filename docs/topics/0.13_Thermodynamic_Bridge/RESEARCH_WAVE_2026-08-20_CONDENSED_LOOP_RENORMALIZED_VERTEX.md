# Research Wave 2026-08-20: Condensed Loop-Renormalized Vertex

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The declared condensed relative-flow contact channel now has a finite thermal one-loop derivative-channel bubble, an explicit reference-subtracted coupling, a positive effective-coupling contract, and a state-matched natural-unit retarded response. Radial order, angular order, compactification-scale refinement, common-flow conservation, positivity, KMS/FDT, and entropy checks pass.

WHAT_REMAINS_OPEN: The result is not a complete condensed 1PI vertex or all-channel scattering calculation. Physical Kubo admission still lacks an independent physical anchor/source record with accepted provenance, uncertainty, and the required state-matched units. The complete two-fluid tensor, dimensional `Phi` map, independent `alpha_Phi_K`, Ding-compatible `C_src`, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: Loop-renormalized condensed contact-channel and state-matched natural retarded lane only. No physical Kubo, SI, alpha, Core, Gravity, transport, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added the loop-renormalized condensed contact-channel implementation, audit artifact, focused regression, equation-registry addendum, full-gate mapping, major-result register entry, dependency evidence, and this wave record. The implementation uses the existing O(2) condensed dispersion and does not consume external numeric data or the locked Xie 2026 holdout.

EQUATION_OR_MAPPING:

```text
B_ab^th=(integral d^3k/(2*pi)^3)*(k/L)^2*(n_a+n_b)/(2 E_a E_b (E_a+E_b))
B_ab^R(T,mu,Phi)=B_ab^th(T,mu,Phi)-B_ab^th(T,mu,Phi_ref)
lambda_ab^R=lambda/(1+lambda B_ab^R)
sigma_ab^R=(lambda_ab^R)^2/[16*pi*(s_med+2 lambda A_*^2)]
L_rel=Gamma_rel*((1,-1),(-1,1))
G_R^rel(omega)=2 D_rel/(2 Gamma_rel-i omega)
K_rel^natural=lim_(omega->0) Re G_R^rel(omega)
```

VERIFICATION: The audit reports zero failed checks. The reference state is `(T,mu,Phi_ref)=(0.20,1.28,0.0)` and the target is `(0.20,1.28,0.15)` on the condensed branch with the declared nonzero `Phi` coupling. Numerical uncertainty bound is `3.500054507989025e-06`; loop-bubble relative change is `9.321205929180344e-13`; loop-coupling relative change is `3.261235996489399e-14`; the state-matched response is positive; common-flow and symmetry residuals are zero at machine precision; KMS/FDT and entropy checks pass; focused regression is `2 passed`.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`, together with `independent_physical_condensed_vertex_anchor_missing` and `complete_condensed_1PI_vertex_and_scattering_channels_missing`.

NEXT_ACTION: Obtain or derive one state-matched physical condensed retarded/Kubo record with `coefficient_name`, value, units, hydrodynamic frame, state, correlator locator, source path/hash, evidence status, and uncertainty. Then test the full interacting SK/KMS and complete scattering-channel admission without using target residuals, fitting, synthetic replacement data, or Xie 2026.

CLAIM_BOUNDARY: This is an action-derived natural-unit loop-renormalized contact-channel lane with a state-matched retarded interface. It is not a full 1PI renormalization, a physical Kubo coefficient, an SI thermal observable, an `alpha_Phi_K` calibration, a TTG prediction, external validation, or Full Topic 13 closure.

EVIDENCE_HASHES:

- module `docs/core/uet_o2_condensed_loop_renormalized_vertex.py`: `6384e8bc5553b696c17a079b93fd97df95b8f545475732b2a23f7133f03fe0dc`
- audit `docs/core/07_artifacts/topic13/t13_uet_o2_condensed_loop_renormalized_vertex_audit.json`: `6a3b581978b4020648c5f2c9b9d38fef4aed501267190e5a8c5c2178e666737b`
- equation registry `docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json`: `ae143f9bd06738ae777415b46d39752c8fbb4a96b17f31de94eac3e563a7be44`
- full gate `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`: `3336e8e0ee0fa3e0d4f455f39010a3c9426af8583074d830c8143518dbc94c09`
- closure register `docs/core/07_artifacts/gates/uet_major_result_closure_register.json`: `fd0db3bd2358b0e66c480464ddf088e13fa37ccb8b0b1df0a542ec383740078d`
- dependency gate `docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json`: `ec6199d171b0aea536c0f072e498c0bfd9988ae66612bedfac94d422b5462637`
