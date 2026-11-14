# Signed local moment interpolation candidate

MAJOR_RESULT_CLOSURE: PARTIAL; fixed-support reproduction of constant, energy and momentum features achieved before projection in both candidate grids.
WHAT_IS_ACTUALLY_CLOSED: The explicit least-correction interpolation reduces maximum scaled feature residual from0.976/0.788 to1.11e-15/8.88e-16 for axis6/axis_cube14. Raw channel feature residuals are below1.49e-15 without using the conserved projector to conceal them. Both candidate tensors remain positive with factorized balance.
WHAT_REMAINS_OPEN: Nonlinear interpolation accuracy, refinement, coefficient/input sensitivity, finite-amplitude occupation admissibility, production integration and material mapping.
DEPENDENCY_UNLOCKED: Candidate reference route only; no physical/Core unlock.
STATUS: SIGNED_MOMENT_CANDIDATE_MEASURED_NOT_CONVERGED.
WHAT_CHANGED: Preregistered fixed-support plan, numerical correction helper, three tests, two full-tensor cases, artifact and registry proposal. Production defaults and historical results unchanged.
EQUATION_OR_MAPPING: On existing support A s=t for features(1,E/cutoff,p/cutoff). With A.T=Q R, delta_s=Q solve(R.T,t-A s0) is the minimum Euclidean coefficient correction; s=s0+delta_s. Physical susceptibility weights and collision rates remain positive and unchanged.
VERIFICATION: Three tests PASS: massive-shell signed reproduction and minimum-norm property, rank-deficiency rejection without fallback, and unchanged already-exact mapping. Both locked cases complete exit0 at120 digits. F0 inventory369/no duplicates; foundation/compatibility audit PASS with physical gates BLOCKED. Input hashes checked.
CONTROLLING_BLOCKER: nonlinear_interpolation_accuracy_under_refinement_and_input_sensitivity.
NEXT_ACTION: Refine the moment grid and audit the two preregistered nonlinear probes, signed coefficient norms, and tensor response together. Keep axis6 as a restricted comparator: it cannot represent p_x*p_y regardless of coefficient correction. Do not add probes to the constraints merely to make their validation errors vanish.
CLAIM_BOUNDARY: This is a numerical interpolation ansatz with enforced moments, not a microscopic transport derivation, positive-probability redistribution, material validation or Full Topic13 closure.

## Matched two-grid results

All prior coarse controls remain fixed; support40 and rank relative floor1e-12 were declared before execution. No rank failure, support expansion, clipping or target-data fit occurred.

| Quantity | Axis6 | Axis/cube14 |
| --- | ---: | ---: |
| Maximum scaled feature error, before |0.97575|0.78825|
| Maximum scaled feature error, after |1.11e-15|8.88e-16|
| Raw channel feature error |1.30e-15|1.48e-15|
| Most negative coefficient |-0.17356|-0.13582|
| Largest column L1 norm |3.9882|4.0497|
| Largest local feature condition number |5.728|21.638|
| Natural trace(K)/3 |254.82471925625518525|254.82471925625526431|

For fixed coefficients, the column L1 norm bounds amplification of uniform nodal-value error at each interpolated point. It is not a bound on coefficient sensitivity or the full transport error. The coefficients multiply the linear-response variable psi; they are not particle probabilities, quadrature measures or collision rates. Finite-amplitude positivity of an occupation perturbation is not established here.

## Independent nonlinear checks

Neither p_x*p_y/E^2 nor mass/E is included in the constraint features. Errors below are unweighted RMS absolute errors across generated channel legs, not measured material uncertainties.

| Probe | Axis6 before / after | Axis/cube14 before / after |
| --- | ---: | ---: |
|p_x*p_y/E^2|0.15842 /0.15842|0.14769 /0.08278|
|mass/E|0.12559 /0.13122|0.14116 /0.10670|

Thus exact low-order moment reproduction does not certify general interpolation accuracy. The six-axis cross-momentum probe is identically zero at every basis node, so no linear combination restores its off-grid shape. The mass/E RMS error even worsens slightly on axis6. Both findings are retained rather than selecting only improved metrics.

## Algebra and physical boundary

The QR correction lies in the row space of A and satisfies A delta_s=t-A s0. Any additional homogeneous correction lies in the nullspace, orthogonal to that minimum-norm correction. Negative coefficients are expected from the previously proved positive mass-shell exactness boundary.

For nonnegative rates R, J.T R J remains positive semidefinite even when the interpolation coefficients entering J are signed. This algebraic property and the measured response balance do not prove interpolation convergence or positivity of a finite perturbed distribution. The local rest-frame grid and its interpolation remain explicit approximations.

Evidence: artifacts/t13_moment_interpolation_plan.json and artifacts/t13_moment_interpolation_audit.json; unmerged registry proposal artifacts/t13_signed_moment_registry_addendum.json. No external source or holdout dataset was used.
