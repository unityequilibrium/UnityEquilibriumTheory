# Topic 13 Research Wave: Formal Finite-T Off-Shell 1PI Boundary

MAJOR_RESULT_CLOSURE:
`T13_UET_O2_FINITE_T_OFFSHELL_1PI_FORMAL_LANE` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED:
The declared O(2) action now has one explicit finite-temperature off-shell two-point 1PI object through the one-loop tadpole and two-loop sunset order. The full Matsubara sum-integral represents all signed three-line thermal cut assignments, and its retarded continuation, spectral representation, KMS relation, thermal-vacuum UV split, and local counterterm basis are machine-checked.

WHAT_REMAINS_OPEN:
The result does not select a unique physical renormalization anchor, evaluate a physical finite-temperature self-energy, emit a Kubo coefficient, close covariant entropy/heat-flux balance, map `Phi` to SI, calibrate `alpha_Phi_K`, or provide Ding `C_src(T)` numeric rows.

DEPENDENCY_UNLOCKED:
Only the formal finite-temperature off-shell 1PI/KMS interface is unlocked. The full Topic 13 Core-ready gate, Core curved 3+1, Gravity, constitutive transport, TTG calibration, and external validation remain blocked.

STATUS:
`PASS_ACTION_DERIVED_O2_FINITE_T_COMPLETE_OFFSHELL_1PI_FORMAL_LANE`.

WHAT_CHANGED:
Added the formal action-level off-shell 1PI object, verifier artifact, regression tests, and registry projection. No TTG target, Xie holdout, fit, or synthetic source was consumed.

EQUATION_OR_MAPPING:
`Gamma_E,ab^(2)(P;T) = delta_ab*[P^2 + m^2 + Sigma_tad,T + Sigma_sunset,T^(2)] + delta_Gamma_local`.

`Sigma_tad,T = (N+2)*lambda*T*sum_n*integral_d3k G_T(K)`.

`Sigma_sunset,T^(2)(P) = 2*(N+2)*lambda^2*T^2*sum_{n,m}*integral_d3k d3q G_T(K)G_T(Q)G_T(P-K-Q)`.

`Gamma_R(omega,p;T) = Gamma_E(i*nu_l -> omega+i0+,p)` with `Sigma^> = exp(beta*omega) Sigma^<`.

VERIFICATION:
The dedicated audit and three regression tests pass. Evidence is in `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_offshell_1pi_audit.json`.

CONTROLLING_BLOCKER:
`unique_physical_renormalization_scheme_or_external_anchor_missing` for this lane; the full Topic 13 gate remains controlled by source, calibration, dimensional mapping, and EOS/transport/KMS/entropy completion.

NEXT_ACTION:
Source-lock an independent physical renormalization anchor or explicitly preserve the formal boundary, then continue the dimensional map and independent `alpha_Phi_K` route without using holdout data.

CLAIM_BOUNDARY:
This is an action-derived formal lane, not a proof of a physical thermal transport coefficient and not full Topic 13 closure. `Phi` remains an effective response variable, `C` remains a collective coordinate, `R_gen` remains a derived history trace, and `R_obs` remains separate from dynamics.
