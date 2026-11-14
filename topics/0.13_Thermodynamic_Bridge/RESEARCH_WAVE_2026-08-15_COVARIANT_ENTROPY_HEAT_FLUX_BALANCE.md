# Topic 13 Research Wave: Covariant Entropy and Heat-Flux Balance

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE/PARTIAL`.

WHAT_IS_ACTUALLY_CLOSED: The declared normal-quasiparticle lane now has a Landau-frame energy-current subtraction, a finite-cutoff action-derived moment response, a covariant entropy-current lift, and an exact finite-grid charge/energy/momentum dissipative balance. The result is a formal natural-unit lane, not a physical transport measurement.

WHAT_REMAINS_OPEN: Physical Kubo matching, SI heat-flux units, finite-temperature two-fluid completion, microscopic SK/KMS matching, curved 3+1 transport, the dimensional `Phi` map, independent `alpha_Phi_K`, Ding `C_src` provenance, source uncertainty, and external validation remain open.

DEPENDENCY_UNLOCKED: Only the named Topic 13 covariant entropy-current and finite-cutoff formal heat-flux balance lane. No Core-ready, Gravity, SI, `alpha_Phi_K`, TTG prediction, or external-validation dependency is unlocked.

STATUS: Lane verifier `PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE`; focused regression `9 passed`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE/PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added `uet_o2_covariant_entropy_heat_flux_balance.py`, its audit, regression tests, machine-readable artifact, full-gate integration, major-result registry sync, and dependency-hash update. The heat source is built from the existing action-derived continuum state and is Gram-projected against signed charge plus energy and three-momentum invariants.

EQUATION_OR_MAPPING: `h=(epsilon+p)/n`; `b_i=(E-h*q)(p_i/E)sqrt(w)`; `K_ab=(b_a^perp)^T L_cont^+ b_b^perp`; `X_T^mu=-Delta^(mu nu)(nabla_nu T+T a_nu)/T`; `q^mu=kappa_natural X_T^mu`; `J_S^mu=s u^mu+q^mu/T`; `sigma=X_T_mu q^mu>=0`; `I_A^T L_cont delta_f=0`.

VERIFICATION: `kappa_natural=257.37286696883626` in the declared natural moment lane; heat-response isotropy residual `4.43e-11`; entropy-balance residual `1.14e-8`; kinetic equation residual `5.12e-17`; charge, energy, and momentum balance residuals below `2e-19`; Lorentz-lift residual `1.42e-14`; equilibrium heat flux `0`. No fit, target data, synthetic replacement, SI coefficient, numeric `alpha_Phi_K`, or Xie 2026 holdout access was used.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_missing` for this transport lane, while the full Topic 13 gate is still controlled by the dimensional `Phi` energy anchor / independent calibration chain and the unresolved source, bridge, EOS, transport, KMS, entropy, and uncertainty gates.

NEXT_ACTION: Obtain a state-matched microscopic retarded correlator or permitted physical transport source with units and uncertainty; separately source-lock the independent `Phi` energy anchor and TTG numeric `C_src` package. Do not reinterpret `kappa_natural` as SI conductivity or use it to fit the locked holdout.

CLAIM_BOUNDARY: This is an action-derived finite-cutoff natural-unit moment-response and formal covariant entropy/balance result on the normal quasiparticle lane. It is not a physical Kubo coefficient, SI heat flux, complete two-fluid theory, curved 3+1 transport result, `alpha_Phi_K` calibration, TTG validation, or Full Topic 13 closure.

EVIDENCE: `docs/core/07_artifacts/topic13/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/07_artifacts/gates/uet_major_result_closure_register.json`; `docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json`.
