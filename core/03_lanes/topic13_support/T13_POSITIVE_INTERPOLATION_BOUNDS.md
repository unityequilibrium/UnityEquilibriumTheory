# Positive interpolation: local and rate-weighted probe bounds

MAJOR_RESULT_CLOSURE: PARTIAL; explicit bounds established for two probe amplitudes and checked on all nine fixed grids.
WHAT_IS_ACTUALLY_CLOSED: Local-radius and sampled-rate-weighted channel bounds cover the measured probe errors in all cases. Normalization roundoff is included. This provides an error-accounting route without exact per-leg moment enforcement or unstable signed coefficients.
WHAT_REMAINS_OPEN: Tighter bounds, arbitrary response/operator errors, projection/boundary control, transport uncertainty and material mapping.
DEPENDENCY_UNLOCKED: No physical/Core unlock.
STATUS: PROBE_BOUNDS_MEASURED_NOT_OPERATOR_CLOSURE.
WHAT_CHANGED: Independent bounds runner, four tests, nine-case artifact and registry proposal. Production interpolation, rates, thresholds and historical results unchanged.
EQUATION_OR_MAPPING: b_leg=L sum_i a_i |p_i-p_target|+|sum_i a_i-1| |psi_target|; b_channel=|incidence| b_leg. Nonnegative rates preserve the inequality under the weighted quadratic norm.
VERIFICATION: Four tests PASS: local/channel bounds, signed-weight rejection, exact-node limit and normalization-defect accounting. Nine cases complete exit0 with no measured bound violation. F0 inventory369/no duplicates; foundation and compatibility audits PASS with physical gates BLOCKED. Source hashes verified.
CONTROLLING_BLOCKER: bounds_too_loose_for_operator_or_transport_accuracy.
NEXT_ACTION: Obtain tighter local derivative bounds, inspect channel contributions and conservation projection, and retain boundary errors. Do not mistake normalized sampled-rate RMS for a material uncertainty or a physical probability law.
CLAIM_BOUNDARY: Two specific nonlinear probes only, not a bound on every distribution or conductivity. No continuum, external or full Topic13 closure follows.

## Derivation

Let E=sqrt(m^2+|p|^2), m>0. For psi=p_x*p_y/E^2, the gradient norm is at most r/(m^2+r^2)+r^3/(m^2+r^2)^2, which is at most2r/(m^2+r^2)<=1/m. Thus L=1/m is a valid global bound. For psi=m/E the exact global gradient maximum is2/(3*sqrt(3)*m), attained at r=m/sqrt(2).

Subtract the target probe from the weighted sum. The triangle inequality and these Lipschitz constants give the leg bound, plus the displayed normalization defect for finite-precision weight sums. Applying the same inequality to the signed channel incidence gives the channel bound. Multiplication by nonnegative rates and summation preserve the squared-error bound.

Positive-part calculations in the artifact measure excess over a bound; they do not modify any probe, coefficient or physical output. Global Lipschitz bounds also cover outside-cutoff targets, but cannot make their geometric support distances vanish.

## Results and limits

For product8x16 at radial8/16/32, mean weighted support distance decreases11.104/9.147/7.588 in natural momentum units. The normalized sampled-rate RMS channel errors are:

| Probe |8|16|32|
| --- | ---: | ---: | ---: |
|p_x*p_y/E^2|0.05635|0.05629|0.04949|
|mass/E|0.20080|0.02648|0.02696|

The last mass/E step slightly worsens. Monotonic convergence is not claimed. At the finest tested product grid, corresponding channel bounds are10.563 and4.066, far above actual errors. Bounds are valid but presently too loose to certify useful transport accuracy. Raw rate-weighted error norms are also recorded; their small absolute scale is not evidence of small material error.

Rates and target channels are exactly the previously generated finite sample. Rate normalization is only descriptive RMS scaling, not fitting or a replacement collision model. No target/holdout dataset was used.

Evidence: artifacts/t13_positive_interpolation_bounds_audit.json. The preceding tenth-section checkpoint was committed as bcafcfd47 before this new section began.
