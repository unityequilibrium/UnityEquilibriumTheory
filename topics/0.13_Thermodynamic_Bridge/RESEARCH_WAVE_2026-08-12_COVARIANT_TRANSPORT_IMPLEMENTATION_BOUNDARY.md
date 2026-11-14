# Research Wave: Covariant Transport Implementation Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The current covariant transport implementation is
explicitly a natural-unit, Landau-frame, `T=0` pure-superfluid ideal sector
with a minimal longitudinal Kubo interface. Ideal covariance, entropy
positivity, causal control, and provenance blocking are verified. Synthetic
coefficients are opt-in controls only.

WHAT_REMAINS_OPEN: No physical Kubo coefficient is supplied. The finite-
temperature normal component, full transport tensor, SI transport lane, and
curved 3+1 solver are not implemented. The base-Phi SI anchor and
`alpha_Phi_K` remain independent blockers.

DEPENDENCY_UNLOCKED: Implementation-boundary result only. Full Topic 13,
physical transport, Core curved 3+1, and Gravity remain blocked.

STATUS: `PASS_CLOSED_TRANSPORT_IMPLEMENTATION_BOUNDARY`

WHAT_CHANGED: Added a source/test-hashed implementation-boundary audit and
linked it into the Topic 13 full gate, major-result register, dependency gate,
formula audit, current-state report, update log, and work ledger.

EQUATION_OR_MAPPING:

```text
P = P(X, Phi)
N^mu = (Z*q/lambda) xi^mu
T^mu_nu = f_s xi^mu xi^nu + p g^mu_nu
KuboCoefficientRecord -> coefficient only when matched evidence passes
sigma = X_A L^(AB) X_B >= 0
```

VERIFICATION: T=0 and missing-coefficient paths reject unsupported use;
natural-unit/SI boundaries, synthetic-control opt-in, trace isolation, ideal
covariance, entropy sign, causal speed, and blocked physical provenance all
match the implementation and tests.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`

NEXT_ACTION: Acquire a state-matched physical Kubo coefficient and independently
derive the finite-temperature normal sector and SI Phi observable map.

CLAIM_BOUNDARY: Implementation scope only. This is not a microscopic Kubo
match, finite-temperature two-fluid derivation, SI transport result, external
validation, or Full Topic 13 closure.
