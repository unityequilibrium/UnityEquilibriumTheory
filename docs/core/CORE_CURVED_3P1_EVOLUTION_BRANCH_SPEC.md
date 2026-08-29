# Core Curved 3+1 Evolution Branch Specification

MAJOR_RESULT_CLOSURE: `GH_NONLINEAR_VACUUM_RHS_CLOSED_FOR_LANE / PARENT_PARTIAL`

WHAT_IS_ACTUALLY_CLOSED: The fixed-geodesic ADM branch remains closed as a branch-local hyperbolicity no-go. The selected generalized-harmonic branch now closes its principal/characteristic system and the complete nonlinear vacuum Eqs. (35)-(40) right-hand-side operator, including metric-derived kinematics, Christoffel/gauge-constraint reconstruction, and the algebraic `gamma0` damping term.

WHAT_REMAINS_OPEN: A time integrator/CFL policy, gauge/reduction constraint propagation over time, temporal convergence, constraint-preserving non-periodic boundaries, Topic 13 stress-energy wiring, and SI observable mapping.

DEPENDENCY_UNLOCKED: The GH time-integration and constraint-propagation wave only. Gravity/GR remains blocked.

STATUS: `PARTIAL_GH_NONLINEAR_VACUUM_RHS_READY`

WHAT_CHANGED: The source-locked first-order GH implementation now evaluates the complete vacuum RHS for declared `H_a` and `nabla_a H_b`. Independent explicit-index controls cover constant and spatially varying periodic states; Minkowski, gauge-derivative injection, `gamma0` isolation/scaling, tensor symmetry, metric-signature rejection, and ontology boundaries pass. No time stepper or matter source was added.

EQUATION_OR_MAPPING:

- Evolve the spacetime metric `psi_ab`, its normal derivative `Pi_ab`, and spatial derivatives `Phi_iab`.
- Enforce the reduction constraint `C_iab = partial_i psi_ab - Phi_iab`.
- Enforce the gauge constraint `C_a = H_a + Gamma_a` with a declared gauge source `H_a`.
- Keep `psi_ab` as geometry, not `Phi`; keep the stress-energy projection lane-specific, not universal `C`; exclude `R_gen` and `R_obs` from the dynamical state.

VERIFICATION:

- Match the analytic GH principal symbol and obtain a complete characteristic basis in every preregistered direction.
- Demonstrate symmetric or strong hyperbolicity and causal declared characteristic speeds.
- Pass Minkowski, gauge-wave, robust-stability, and constraint-violation controls.
- Pass temporal and spatial convergence without clipping, fitted damping, or hidden filtering.
- Verify constraint damping and propagation separately from solution accuracy.
- Add constraint-preserving boundary tests before any non-periodic or black-hole claim.
- Keep the current RHS result operator-only until temporal convergence and propagated-constraint gates pass.

CONTROLLING_BLOCKER: `curved_3p1_generalized_harmonic_time_integration_and_constraint_propagation_missing`

NEXT_ACTION: Add a preregistered explicit time integrator and CFL policy, then verify Minkowski/gauge-wave evolution, reduction/gauge-constraint propagation, and temporal-spatial convergence on the periodic branch.

CLAIM_BOUNDARY: This closes a standard vacuum RHS operator lane only. It does not establish a time-integrated numerical-relativity solver, matter-coupled curved UET solution, Einstein-equation derivation, Gravity compatibility, or external validation.

## Stop Rules

The branch closes `CLOSED_FOR_LANE` only when every verification item above passes with source-locked equations and fixed thresholds. A reproducible principal-symbol or constraint-propagation failure closes the attempted formulation as `CLOSED_AS_NO_GO` and requires a new named branch. More runtime alone cannot promote either result.

## Sources

- C. Gundlach and J. M. Martin-Garcia, *Well-posedness of formulations of the Einstein equations with dynamical lapse and shift conditions*, arXiv:gr-qc/0604035, DOI: 10.1103/PhysRevD.74.024016.
- L. Lindblom et al., *A New Generalized Harmonic Evolution System*, arXiv:gr-qc/0512093, DOI: 10.1088/0264-9381/23/16/S09.
