# Core Curved 3+1 Evolution Branch Specification

MAJOR_RESULT_CLOSURE: `GH_PERIODIC_VACUUM_EVOLUTION_CLOSED_FOR_LANE / PARENT_PARTIAL`

WHAT_IS_ACTUALLY_CLOSED: The fixed-geodesic ADM branch remains closed as a branch-local hyperbolicity no-go. The selected generalized-harmonic branch closes its principal/characteristic system, complete nonlinear vacuum Eqs. (35)-(40) RHS, and periodic RK4 evolution with a fixed characteristic CFL contract. Minkowski, exact harmonic gauge-wave, gauge/reduction/curl propagation, and `gamma2` damping controls pass.

WHAT_REMAINS_OPEN: Constraint-preserving non-periodic boundaries, Topic 13 stress-energy wiring, multi-chart/strong-field controls, and SI detector-observable mapping.

DEPENDENCY_UNLOCKED: Constraint-preserving boundary and Topic 13 stress-energy wiring waves only. Gravity/GR remains blocked.

STATUS: `PARTIAL_GH_PERIODIC_VACUUM_EVOLUTION_READY`

WHAT_CHANGED: Added a separate periodic vacuum evolution module using classical RK4 and `dt <= cfl min(dx_i)/max(alpha+||beta||_2)`. The stepper evaluates the verified nonlinear RHS at all stages and records unprojected gauge, reduction, and curl constraints without filtering, artificial dissipation, clipping, or fitting.

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
- Periodic gauge-wave spatial order is at least `1.9845`; RK4 temporal self-convergence order is `3.9266`.
- The constant off-diagonal reduction violation follows `exp(-gamma2 t)` within the locked relative-error threshold.
- Keep the parent partial until non-periodic boundary, matter, and observable gates pass.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_topic13_stress_energy_wiring_missing`

NEXT_ACTION: Add a named constraint-preserving non-periodic boundary interface and wire the bounded Topic 13 stress-energy projection without relabelling `C`, `Phi`, or `R_gen`.

CLAIM_BOUNDARY: This closes a bounded periodic vacuum evolution lane only. It does not establish a production numerical-relativity solver, matter-coupled curved UET solution, Einstein-equation derivation, Gravity compatibility, or external validation.

## Stop Rules

The branch closes `CLOSED_FOR_LANE` only when every verification item above passes with source-locked equations and fixed thresholds. A reproducible principal-symbol or constraint-propagation failure closes the attempted formulation as `CLOSED_AS_NO_GO` and requires a new named branch. More runtime alone cannot promote either result.

## Sources

- C. Gundlach and J. M. Martin-Garcia, *Well-posedness of formulations of the Einstein equations with dynamical lapse and shift conditions*, arXiv:gr-qc/0604035, DOI: 10.1103/PhysRevD.74.024016.
- L. Lindblom et al., *A New Generalized Harmonic Evolution System*, arXiv:gr-qc/0512093, DOI: 10.1088/0264-9381/23/16/S09.
