# Transition pullback implementation and failure boundary

MAJOR_RESULT_CLOSURE: PARTIAL; coordinate identity implemented, full transport response remains numerically blocked.
WHAT_IS_ACTUALLY_CLOSED: An explicit weighted_psi_pullback path reaches the actual collision builder. Four locked combinations of coordinate map and direction rule were attempted. Legacy results reproduce; both corrected-coordinate cases fail to produce a positive heat coefficient.
WHAT_REMAINS_OPEN: Stable rate-weighted response, interpolation consistency in susceptibility tails, angular/transition convergence and material correspondence.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: BLOCKED_PULLBACK_NUMERICAL_FAILURE.
WHAT_CHANGED: Private _transition_map selection and validated coordinate-row helper; appended state identity; fixed four-case pilot and tests. The legacy default is preserved only as a comparator, not endorsed as a consistent psi interpolation.
EQUATION_OR_MAPPING: U=V sqrt(W_exact) S.T inv_sqrt(W_basis); existing rates, projector, tensor response and thresholds unchanged.
VERIFICATION: Eleven tests cover coordinate identity, independent manufactured controls, invalid inputs, legacy collision regression and blocked-artifact discipline. F0 PASS_WITH_DISCLOSED_GAPS,369 rows,no duplicates. Foundation and compatibility audits PASS as audits, physical gates remain BLOCKED. Pilot exits1 because two declared cases fail, not because they were skipped.
CONTROLLING_BLOCKER: weighted_interpolation_conditioning_and_response_solver.
NEXT_ACTION: Audit rate-weighted interpolation support and tail contributions, then test a factorized/constrained response solve against controlled matrices. Do not reduce weights, clip eigenvalues, change rcond or choose support settings to force acceptance.
CLAIM_BOUNDARY: Correct coordinate algebra does not establish a stable or accurate continuum discretization. Failed cases emit no valid kappa. No material transport, Full Topic13 or global closure is claimed.

## Matched failure evidence

Same state, action and coarse controls as the preceding weighted-direction pilot: T=.22,mu=.35,Phi=.15,radial8,collision24,angular24,cutoff48,transition24,64 channels,interpolation40.

| Quantity | Axis6 legacy | Axis6 pullback | Axis/cube14 legacy | Axis/cube14 pullback |
| --- | ---: | ---: | ---: | ---: |
| Kappa |254.824719|ERROR|254.824712|ERROR|
| Largest absolute eigenvalue / largest width |1.00|1.15e64|1.00|2.13e29|
| Modes retained at existing relative1e-12 cutoff |91|5|219|9|
| Vertex trace / base trace |1.60e-6|9.55e62|6.43e-7|4.00e27|

The susceptibility weight span is approximately8e87 in these finite grids. The corrected coordinate factors expose huge stiffness in the current interpolation. This suggests a tail-support/conditioning issue; it does not yet isolate interpolation approximation from response-solver error.

Negative computed eigenvalues are tiny relative to the largest scale but enormous relative to the width scale. They must not be interpreted automatically as physical negative dissipation: the exact outer-product vertex is positive semidefinite, while finite precision can lose the small modes. Conversely, a tiny normalized projection correction is not a success criterion when the underlying scale is enormous.

The previous coordinate counterexample artifact remains frozen. New evidence and source hashes: artifacts/t13_transition_pullback_pilot.json. Registry proposal remains unmerged and explicitly numerically blocked.
