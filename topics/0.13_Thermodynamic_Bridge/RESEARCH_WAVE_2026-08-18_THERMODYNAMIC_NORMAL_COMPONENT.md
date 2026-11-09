# Topic 13 Research Wave: Thermodynamic Normal Component (2026-08-18)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_THERMODYNAMIC_NORMAL_COMPONENT_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The finite-temperature thermal quasiparticle sector is now named explicitly as the thermodynamic normal component. Its pressure, charge, entropy, energy, susceptibility, static momentum response, branch coverage, low-temperature suppression, and total-state stability checks are recorded together.

WHAT_REMAINS_OPEN: This result does not derive a physical normal-fluid mass density, a condensed relative-flow tensor, a retarded physical Kubo coefficient, an SI Phi map, or independent `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Thermodynamic normal-component lane only. No physical transport, Ding `C_src`, calibration, Core, Gravity, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_THERMODYNAMIC_NORMAL_COMPONENT_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.

WHAT_CHANGED: Added a dedicated normal-component state/contract, verifier artifact, regression coverage, equation-registry addendum, and full-gate/closure-register projection. Existing two-fluid values are not relabeled as physical flow or Kubo data.

EQUATION_OR_MAPPING: `p_n=p_qp`; `n_n=partial_mu p_n`; `s_n=partial_T p_n`; `epsilon_n=-p_n+T*s_n+mu*n_n`; `chi_n=partial_mu n_n`; `Pi_n=(1/3) sum_a integral[d^3k/(2*pi)^3] k^2[-partial_E n_B(E_a)]`.

VERIFICATION: Normal and condensed branches are explicit; normal entropy and static response are nonnegative on the reference grid; both branches suppress the normal sector at lower temperature; residual sector signs are retained without clipping; no fit, target data, alpha calibration, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `physical_normal_flow_component_or_retarded_kubo_match_missing`, plus SI Phi anchoring, independent `alpha_Phi_K`, and Ding-compatible `C_src`.

NEXT_ACTION: Obtain a state-matched physical normal-flow/retarded Kubo record with units and uncertainty, while separately pursuing the independent Phi/SI anchor and accepted Ding C_src route.

CLAIM_BOUNDARY: This is an action-derived natural-unit thermodynamic lane. It is not a physical normal-fluid measurement, a temperature prediction, external validation, or Full Topic 13 closure.
