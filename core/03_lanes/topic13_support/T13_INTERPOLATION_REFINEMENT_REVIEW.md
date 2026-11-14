# Nine-grid mapping refinement review

MAJOR_RESULT_CLOSURE: PARTIAL; the fixed-support signed candidate is not ready under the tested refinement.
WHAT_IS_ACTUALLY_CLOSED: All nine planned grids were attempted. Two fail support rank; several full-rank grids amplify nonlinear errors despite small enforced-moment residuals. The preceding two-grid moment result remains valid but does not establish refinement readiness.
WHAT_REMAINS_OPEN: Stable approximation, rate-weighted operator error, boundary treatment, input sensitivity and material mapping.
DEPENDENCY_UNLOCKED: None.
STATUS: FIXED_SUPPORT_SIGNED_CANDIDATE_NOT_READY_UNDER_TESTED_REFINEMENT.
WHAT_CHANGED: Mapping-only nine-grid study, tests, artifact and this review; no production or thermal tensor rerun.
EQUATION_OR_MAPPING: Same support40 and rank floor1e-12; radial8/16/32 crossed with14/32/128 directions. Product sphere rules are diagnostic nodes, not installed production grids.
VERIFICATION: Six tests PASS including prior candidate regression. Study completes with exit1 because two rank failures remain visible. F0 inventory369/no duplicates; foundation and compatibility audit PASS with physical gates BLOCKED. Artifact source hashes verified.
CONTROLLING_BLOCKER: stable_interpolation_error_control_not_exact_moment_enforcement_alone.
NEXT_ACTION: Measure positive interpolation local-radius bounds and rate-weighted channel errors under refinement. A rank-aware bounded-amplification signed stencil would be a separate candidate, not an automatic fallback.
CLAIM_BOUNDARY: No continuum proof, physical contradiction or material conductivity claim. No rank-floor change, coefficient clipping or source selection.

## Findings

Radial8/product8x16 has25 rank-deficient legs; radial32/axis_cube14 has one. All26 are inside cutoff. Twelve of256 target legs are outside cutoff and are separately reported, not discarded.

At radial32/product8x16, the signed feature residual is about1.52e-10 but the maximum coefficient L1 norm is692015 and feature condition number4.27e7. Its RMS errors for p_x*p_y/E^2 and mass/E are168.29 and1.1425, versus0.03972 and0.01984 for the positive seed. Inside-only signed errors remain172.21 and1.1472: extrapolation is not the sole problem.

On product8x16, positive-seed RMS errors decrease with radial8/16/32: cross-momentum0.07810/0.05697/0.03972 and mass/E0.09481/0.03367/0.01984. This trend supports further investigation, not a convergence claim. Exact per-leg constraints cannot substitute for approximation stability.

For positive normalized weights and a Lipschitz probe, error is at most L times the weighted mean support distance, hence at most L times the maximum support distance. This follows by subtracting the target value, applying the triangle inequality and the Lipschitz bound. Shrinking support radii, rate weighting, boundary handling and conservation-projection control still need verification.

Evidence: artifacts/t13_interpolation_refinement_audit.json, including every failed index and separate inside/outside probe metrics. Earlier moment/tensor artifacts are unchanged.

## Tenth-section checkpoint

Commit this coherent local unit before expanding scope. Preserve unrelated dirty files. Under docs/core/AGENTS.md do not push or open a PR without explicit request. The prior usage rejection prevented this documentation/commit step; subsequent read-only account status permits normal execution, without redeeming a reset.
