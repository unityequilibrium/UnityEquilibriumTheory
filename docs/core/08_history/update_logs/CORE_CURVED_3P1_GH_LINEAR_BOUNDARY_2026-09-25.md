# Core Curved 3+1 GH Linear Boundary Residuals - 2026-09-25

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_LINEAR_DIFFERENTIAL_BOUNDARY_RESIDUALS / CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: Source-matched, linearized/frozen-background evaluation of the incoming subsidiary-constraint residual, incoming Weyl/Psi_0 residual, algebraic gauge-data residual, and the positive-normal-shift incoming `u2_A` definition-curl residual. The rank-4 and rank-2 normal-derivative maps have kernels matching the source constraint and physical projectors.

WHAT_REMAINS_OPEN: The residuals are not imposed on an evolution scheme. Nonlinear variable-coefficient CPBC, non-periodic SBP/SAT evolution, a discrete boundary energy estimate, stability/convergence, edge/corner compatibility, matter-boundary consistency, and dimensional observables remain open.

DEPENDENCY_UNLOCKED: Boundary residual implementation and verification only. The Core parent remains `PARTIAL`; Gravity, transport, and Galaxy remain blocked.

STATUS: `PASS_GH_LINEAR_BOUNDARY_RESIDUAL_OPERATOR_AUDIT`; `claim_promotion=false`.

WHAT_CHANGED: Added `uet_curved_3p1_gh_linear_boundary.py`, a deterministic source-hashed audit, and focused analytic regression tests. The periodic GH solver and UET ontology were not modified.

EQUATION_OR_MAPPING:

- `c0_minus_a=0` from Rinne 2006 Eq. (27).
- `w_minus_ab=partial_t hP_ab` from Eqs. (30)-(33).
- `P_G u1_minus_ab=hG_ab` from Eqs. (35)-(36).
- For positive subluminal normal shift, `partial_n u2_Aab-partial_A Phi_nab=0` from Eq. (29).
- `A_C(I-P_C)=0`, `A_P(I-P_P)=0`, with `rank(A_C)=4` and `rank(A_P)=2`.
- Boundary mode count is `4+2+4=10` for `u1_minus`; positive subluminal shift adds 20 incoming `u2_A` modes with a rank-20 normal-derivative map.

VERIFICATION: 26 normalized face normals; maximum projector-kernel residuals `4.17e-16` and `2.76e-16`; prescribed physical/gauge data residuals below `8.89e-15`; symmetric-Hessian `u2_A` residual `2.22e-16`; positive-shift `u2_A` map rank 20 with zero identity residual; 12 focused regression tests passed. Artifact: `docs/core/07_artifacts/verification/curved_3p1_gh_linear_boundary_residual_audit.json`.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`.

NEXT_ACTION: Implement a non-periodic SBP/SAT or equivalently justified boundary evolution; verify the discrete subsidiary-constraint energy estimate, radiation/gauge data application, stability, spatial/temporal convergence, and edges/corners before nonlinear GH integration.

CLAIM_BOUNDARY: Local source-matched linear residual evaluation only; no nonlinear CPBC implementation or proof of a well-posed repository IBVP ([Rinne 2006](https://arxiv.org/abs/gr-qc/0606053)). The source's Fourier-Laplace boundary analysis is not inherited by this code.
