# Local derivative bounds and two-probe collision form

MAJOR_RESULT_CLOSURE: PARTIAL; segment-local bounds connected to the sampled channel quadratic form on a fixed two-probe span.
WHAT_IS_ACTUALLY_CLOSED: Local bounds are no larger than the preceding global bounds and cover measured errors on all nine grids. A matrix-norm certificate bounds the quadratic-form error for every linear combination of the two declared probes, not only separate probe amplitudes.
WHAT_REMAINS_OPEN: Tight operator accuracy, larger function spaces, width-term and conservation-projection effects, boundary control, inverse transport uncertainty and material mapping.
DEPENDENCY_UNLOCKED: None.
STATUS: LOCAL_PROBE_FORM_CERTIFICATE_NOT_FULL_OPERATOR_CLOSURE.
WHAT_CHANGED: Segment-envelope and matrix-certificate runner, three tests, nine-case artifact and registry proposal; no production equations, rates, thresholds or historical results changed.
EQUATION_OR_MAPPING: For A=sqrt(R_normalized)*exact_probe_amplitudes and B=sqrt(R_normalized)*mapped_probe_amplitudes, ||B.T B-A.T A||_2<=2||A||_2*epsilon+epsilon^2, where epsilon bounds ||B-A||_2 using the weighted Frobenius norm of entrywise channel bounds.
VERIFICATION: Three tests PASS: gradient envelopes along segments including origin crossing, sharper far-field bounds, and quadratic certificate with mixed probe coefficients. Nine grids complete exit0, no measured leg or matrix-bound violation. F0 inventory369/no duplicates; foundation/compatibility audit PASS with physical gates BLOCKED. Input hashes verified.
CONTROLLING_BLOCKER: sampled_channel_form_accuracy_and_certificate_tightness.
NEXT_ACTION: Investigate the channel contributions responsible for the remaining large relative error, with wider/refined test functions and controlled interpolation/boundary changes. Do not infer transport accuracy from a stable conductivity scalar or a valid but loose bound.
CLAIM_BOUNDARY: This is the unprojected sampled channel contribution on two fixed probes. It excludes the diagonal width term and conservation projection, and is not a full operator norm, continuum result, conductivity error bound or Full Topic13 closure.

## Local envelope derivation

For each source-to-target momentum segment, compute its minimum radius by the closest point on that closed segment and its maximum radius from the endpoints. The segment parameter is restricted to[0,1] as a geometric minimization; no data or physical output is clipped.

For p_x*p_y/E^2 the gradient norm is bounded by f1(r)=r/(m^2+r^2)+r^3/(m^2+r^2)^2. This envelope peaks at r=m*sqrt((3+sqrt(17))/4). For mass/E, f2(r)=m*r/(m^2+r^2)^(3/2) peaks at r=m/sqrt(2). Evaluate each envelope at its peak if inside the segment's radial interval, otherwise at the closer endpoint. Integrating the resulting derivative bound over each segment and summing positive weights gives the local error bound. Normalization roundoff is retained.

Writing B=A+D gives B.T B-A.T A=A.T D+D.T A+D.T D. Submultiplicativity and the triangle inequality give the displayed certificate. For any coefficient vector c, the quadratic-form discrepancy is at most the certificate times ||c||_2^2. The statement is relative to the declared probe basis and its scaling. Raw-rate bounds are obtained by multiplying the rate-normalized result by the unchanged sum of sampled rates.

## Results and caution

At radial32/product8x16, global-to-local RMS leg bounds tighten from8.8204 to0.78943 for p_x*p_y/E^2, and3.3950 to0.07847 for mass/E: factors about11.17 and43.26. Actual RMS errors remain0.03972 and0.01984; the underlying interpolation has not changed.

On product8x16, the normalized quadratic certificates decrease54.294/28.034/16.970 for radial8/16/32. The directly measured matrix errors are0.06637/0.00601/0.00557. The last error is still about55.17% of the exact sampled two-probe Gram matrix spectral norm. A certificate covering that error is not evidence that the approximation is accurate enough.

The reference is the existing finite sample of exact-kinematic channels, not an external dataset or an exact continuum collision operator. No source or holdout data, fitting, eigenvalue clipping or tolerance relaxation is used.

Evidence: artifacts/t13_local_quadratic_bounds_audit.json. Prior global-bound evidence remains unchanged.
