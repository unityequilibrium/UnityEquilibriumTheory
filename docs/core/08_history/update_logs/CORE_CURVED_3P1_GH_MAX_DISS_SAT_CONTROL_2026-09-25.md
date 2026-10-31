# Core Full-U1 Maximally Dissipative SAT Control - 2026-09-25

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_MAX_DISSIPATIVE_SAT_CONTROL / CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A full ten-component, zero-shift frozen-background GH control uses weak homogeneous incoming-characteristic SAT data. The packed symmetric-tensor Frobenius metric is positive and makes the constraint/physical/gauge projectors self-adjoint and mutually orthogonal on 26 normalized face normals. The LGL-SBP energy balance has an explicit lower-order Gronwall term and nonnegative boundary dissipation. The definition constraint obeys `C_dot=-gamma2*C`.

WHAT_REMAINS_OPEN: The control does not impose Rinne's differential subsidiary-constraint or Weyl/`Psi_0` boundary conditions. Positive-shift `u2_A`, tangential derivatives, edges/corners, variable coefficients, nonlinear GH, matter boundaries, and dimensional observables remain open.

DEPENDENCY_UNLOCKED: None. The Core curved 3+1 parent remains `PARTIAL`; Gravity remains blocked.

STATUS: `PASS_FULL_U1_MAX_DISS_SAT_CONTROL`; `claim_promotion=false`.

WHAT_CHANGED: Added a distinct maximally dissipative SAT RHS module, deterministic audit/artifact, focused regression, and Core progress registration. The frozen failing full-u1 Rinne pilot and periodic solver were not modified.

EQUATION_OR_MAPPING:

- `q_n=Pi-n*Phi_n-gamma2*psi`.
- `Pi_dot=-D(Phi)-H^-1 e_L*q_L-H^-1 e_R*q_R`; `psi_dot=-Pi`; `Phi_dot=-D(Pi)+gamma2*D(psi)-gamma2*Phi`.
- `G` is the positive tensor Frobenius metric, with packed-coordinate weights 1 on diagonal and 2 off-diagonal components.
- `dE/dt=R_lower-sum_faces||Pi-gamma2*psi||_G^2`, where `R_lower<=2*mu*E`; `mu=1.0675210254` and `2*mu=2.1350420507` for `gamma2=0.7`, `lambda=2`.
- `C=D(psi)-Phi` gives `C_dot=-gamma2*C`.

VERIFICATION: 10/10 control checks pass at LGL orders 4/8/12. Projector ranks are 4/2/4 over 26 normals; maximum self-adjoint residual `5.55e-17`; SBP residual `4.69e-14`; energy identity residual `2.07e-13`; reduction identity residual `1.43e-14`; control spectral abscissa `-0.38843`, with no mode above `1e-6`. Three focused regression functions pass by direct invocation. The separate strong-Rinne LGL comparison FAILS at orders 8/12/16: energy ratios `3.529/1.267/1.833` exceed `0.05`, reduction residuals `0.249/0.384/0.00404` exceed `2e-6`, and orders 12/16 each have eight modes above `1e-6`. This is finite-grid sensitivity evidence, not a continuum no-go. Artifact SHA-256: `F6D154A4D437DC4BC37069F39151261FF7AC2F3317E7892C7EC23702A49ACD87`.

CONTROLLING_BLOCKER: `rinne_differential_constraint_and_weyl_residuals_not_yet_imposed_in_a_full_u1_sbp_sat_evolution`.

NEXT_ACTION: Use this as the direct-characteristic control while deriving and auditing a projector-compatible weak penalty for the differential constraint and Weyl residuals. Do not replace the frozen Rinne pilot or promote the curved parent from this control.

CLAIM_BOUNDARY: Standard-GR numerical control for direct incoming characteristic data only; not Rinne differential CPBC, a continuum/nonlinear IBVP proof, Gravity compatibility, Einstein-equation derivation by UET, or global UET closure.
