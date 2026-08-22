# Topic 13 Research Wave - C_src and Transport Regime Decomposition

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_C_SRC_THERMODYNAMIC_TRANSPORT_REGIME_DECOMPOSITION`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.

WHAT_IS_ACTUALLY_CLOSED: Under the declared fixed-volume mode basis, `C_src` is treated as the thermodynamic mode-capacity denominator. The archived Calorine run summaries quantify that the latest q-mesh change in `C_src` is much smaller than the change in the RTA in-plane conductivity. Therefore `C_src` convergence is not transport convergence, and morphology, isotope/defect state, scattering solver, and grating geometry remain separate acceptance fields.

WHAT_REMAINS_OPEN: The Calorine route is not Ding material-equivalent and does not provide source-grade uncertainty. A Ding-compatible mode-resolved `C_src`, a same-regime PBTE reproduction, an independent `alpha_Phi_K`, and the TTG transport-state mapping remain open.

DEPENDENCY_UNLOCKED: Only the C_src-versus-transport gate-separation lane. No Ding source acceptance, physical transport, alpha calibration, Core, Gravity, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; `claim_promotion=false`; `holdout_accessed=false`.

WHAT_CHANGED: Added a reproducible audit that reads the archived 4x4x2, 6x6x3, 8x8x4, and 10x10x5 Calorine summaries, compares the latest `C_src` and RTA conductivity changes, records the direct-versus-transport requirement partition, and projects the result into the full gate and major-result register. No target curve, fit, threshold adjustment, synthetic replacement, or Xie 2026 numeric data was used.

EQUATION_OR_MAPPING: `u_ph(T,V) = V^-1 sum_mu [hbar*omega_mu(V)*n_B]`; `C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu`; `Delta_Tq = Delta_u_ph / C_src`; `Delta_Tq = alpha_Phi_K * Delta_Phi` remains open. The latest mesh pair gives `max Delta C_src/C_src = 0.0023965432` and `max Delta kappa/kappa = 0.0908120112`.

VERIFICATION: The new audit passed all source, unit, state, no-fit, and holdout checks. Full gate, closure matrix, major-result register, dependency gate, and Topic 13 lane sync were regenerated. The matrix still reports 9 open blocker groups and `full_core_unlock=false`.

CONTROLLING_BLOCKER: `ding_C_src_mode_state_and_source_grade_uncertainty_missing` controls this new lane. The nearest full-topic controllers remain `alpha_Phi_K_independent_calibration_missing` and `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.

NEXT_ACTION: Obtain an authorized Ding-compatible mode-resolved `C_src` package or same-regime PBTE reproduction with material/state identity, convergence, and uncertainty. Keep the RTA transport comparator outside the Phi calibration path.

CLAIM_BOUNDARY: This is a source-locked standard-physics decomposition for an independent Calorine candidate. It is not Ding `C_src` acceptance, material equivalence, an `alpha_Phi_K` calibration, a `Phi`-to-temperature prediction, physical UET transport, external validation, or Full Topic 13 closure.

EVIDENCE_PATHS: `docs/scripts/audit/audit_topic13_csrc_thermodynamic_transport_regime.py`; `docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json`; `docs/core/artifacts/t13_csrc_fixed_volume_identity_audit.json`; `docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/t13_topic13_closure_matrix.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.
