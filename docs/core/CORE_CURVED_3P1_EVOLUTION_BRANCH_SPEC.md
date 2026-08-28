# Core Curved 3+1 Evolution Branch Specification

MAJOR_RESULT_CLOSURE: `GH_PRINCIPAL_SYSTEM_CLOSED_FOR_LANE / PARENT_PARTIAL`

WHAT_IS_ACTUALLY_CLOSED: The nonlinear periodic ADM metric/extrinsic-curvature right-hand-side operator, its analytic controls, and the fixed-geodesic ADM strong-hyperbolicity question are closed for their declared lanes. The fixed-gauge branch is closed as a no-go because its zero-speed principal-symbol sector has algebraic multiplicity 6 but geometric multiplicity 3.

WHAT_REMAINS_OPEN: Complete nonlinear GH algebraic right-hand sides, gamma0 gauge-constraint damping, a time integrator/CFL policy, full constraint propagation, temporal convergence, constraint-preserving non-periodic boundaries, Topic 13 stress-energy wiring, and SI observable mapping.

DEPENDENCY_UNLOCKED: Implementation and verification of the first-order generalized-harmonic branch only. Gravity/GR remains blocked.

STATUS: `PARTIAL_GH_PRINCIPAL_SYSTEM_READY`

WHAT_CHANGED: Fixed-gauge ADM remains a failed baseline. The source-locked first-order GH principal system now has a complete characteristic basis, positive analytic symmetrizer, source-matched causal normal-frame speeds, and a verified reduction-constraint damping operator. This does not include the complete nonlinear RHS or time evolution.

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

CONTROLLING_BLOCKER: `curved_3p1_generalized_harmonic_nonlinear_rhs_and_gamma0_constraint_damping_missing`

NEXT_ACTION: Transcribe and independently verify the complete nonlinear GH algebraic right-hand sides and gamma0 gauge-constraint damping before adding a time integrator.

CLAIM_BOUNDARY: This specification selects and preregisters a standard numerical-relativity formulation target. It does not establish a GH implementation, a curved UET solution, Einstein-equation derivation, Gravity compatibility, or external validation.

## Stop Rules

The branch closes `CLOSED_FOR_LANE` only when every verification item above passes with source-locked equations and fixed thresholds. A reproducible principal-symbol or constraint-propagation failure closes the attempted formulation as `CLOSED_AS_NO_GO` and requires a new named branch. More runtime alone cannot promote either result.

## Sources

- C. Gundlach and J. M. Martin-Garcia, *Well-posedness of formulations of the Einstein equations with dynamical lapse and shift conditions*, arXiv:gr-qc/0604035, DOI: 10.1103/PhysRevD.74.024016.
- L. Lindblom et al., *A New Generalized Harmonic Evolution System*, arXiv:gr-qc/0512093, DOI: 10.1088/0264-9381/23/16/S09.
