# Constrained precision response and tail audit

MAJOR_RESULT_CLOSURE: PARTIAL; positive constrained x-response recovered for both fixed coarse grids without a spectral cutoff.
WHAT_IS_ACTUALLY_CLOSED: The two direction rules yield positive K_xx at both preregistered precisions120/180, agreeing in the50 reported significant digits for each rule. Work-response and factorized dissipation agree, with all five constraints imposed. Previous float64 response failure is not evidence that this finite-grid quadratic problem lacks a positive response.
WHAT_REMAINS_OPEN: Full response tensor, production integration, binary64 input sensitivity, interpolation consistency, angular/radial/transition convergence and material mapping.
DEPENDENCY_UNLOCKED: No physical/Core unlock. A working reference-solver route is available for the next transport diagnostic.
STATUS: PRECISION_STUDY_MEASURED_NOT_PHYSICAL_CLOSURE.
WHAT_CHANGED: Independent constrained solver/audit, two manufactured tests, four evaluated actual-grid cases, new evidence artifact and registry proposal. Production defaults and failed historical artifacts are unchanged.
EQUATION_OR_MAPPING: z=sqrt(W)*psi; H=diag(w*gamma)+J.T R J, J=(V sqrt(W_exact))*S.T; solve H psi+C lambda=W*g, C.T psi=0 with C=W*F. Each constraint column is rescaled by a nonzero scalar for numerical convenience, leaving its nullspace unchanged.
VERIFICATION: Two tests PASS, including a1e64 stiffness example with known response. All four actual cases complete, exit0. F0 inventory369/no duplicates, PASS_WITH_DISCLOSED_GAPS. Foundation and compatibility audits PASS as audits, physical gates remain BLOCKED. No source or holdout dataset is an input. Evidence hashes verified against current input files.
CONTROLLING_BLOCKER: full_tensor_reference_and_interpolation_consistency, not absence of a positive fixed-grid x-response.
NEXT_ACTION: Extend the constrained solve to all three independent heat sources and cross responses; compare factorized entropy and frame identities. Audit tail interpolation support and input-rounding sensitivity before interpreting convergence or replacing production defaults.
CLAIM_BOUNDARY: Agreement of a high-precision solve of fixed binary64 inputs is not50-digit physical accuracy. K_xx is not trace(K)/3, a full tensor test, SI conductivity, material validation or Full Topic13 closure.

## Actual results

All physical/numerical controls match the previous pilot: T=.22,mu=.35,Phi=.15,radial8,collision24,angular24,cutoff48,transition24,64 channels,interpolation40. No best parameter or precision was fitted.

| Rule | K_xx at120 and180 digits, rounded here | Largest balance relative residual | Largest constraint residual |
| --- | ---: | ---: | ---: |
|axis6|254.82471925625518525|4.30e-116|2.05e-115|
|axis_cube14|254.82471925625526431|6.82e-119|6.84e-116|

The full50-digit response strings are identical across precisions within each rule. These numbers characterize only this fixed finite approximation.

The largest unprojected rate-weighted vertex diagonal occurs at p/T approximately213.21 for axis6 with weight1.01e-91; that node accounts for about60% of the vertex trace. For axis_cube14 it occurs at p/T approximately195.41 with weight9.57e-83 and accounts for almost all the trace. This localizes the enormous matrix scale to tail nodes; it does not establish that interpolation there is physically accurate or that those nodes can be discarded.

## Why this solve is different

The old route assembled a projected weighted matrix in binary64, then used a relative pseudoinverse cutoff. Here the diagonal width and channel factors are retained, the scalar-response coordinates are used directly, and conservation is imposed through a constrained linear system. No rcond is changed and no eigenvalue is clipped.

For positive finite w and gamma and nonnegative rates, H is positive definite because x.T H x=sum(w*gamma*x^2)+sum(R*(J*x)^2)>0 for any nonzero x. With independent constraint columns the finite KKT system is nonsingular. Its response is nonnegative and equals the dissipative quadratic form; it is positive when the force has a nonzero component on the allowed subspace. This is a finite-dimensional result, not continuum well-posedness.

The solver reconstructs the mathematical factorized prescription from fixed binary64 weights, widths, interpolation and channel factors. It does NOT invert the already-rounded failed dense matrix at extra precision, and it does not correct physical input errors. The identity with an exact projected solve is algebraic; roundoff in the old projector/assembled matrix can be strongly amplified at the measured scale separation.

Evidence: artifacts/t13_constrained_precision_audit.json. Previous failure evidence remains artifacts/t13_transition_pullback_pilot.json. The initial attempt was rejected by a usage-limit approval error before file creation; later read-only account status showed no active limit, absent files/process were confirmed, and normal authorized execution resumed without redeeming a reset.
