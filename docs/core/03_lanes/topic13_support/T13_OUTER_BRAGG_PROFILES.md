# Outer Bragg baseline profile comparison

MAJOR_RESULT_CLOSURE: PARTIAL; substantial center-estimator dependence established on actual outer peaks.
WHAT_IS_ACTUALLY_CLOSED: Existing unrotated and rotated Voigt solvers evaluated on six outer peaks in each baseline image at two window sizes. Profile centers can differ from raw centroids by0.67-to0.74px; rotated fitted centers vary by at most0.0772px across the tested windows.
WHAT_REMAINS_OPEN: Profile/background adequacy, measured noise floor, rotated multi-start sensitivity, processing covariance and calibrated geometry uncertainty.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: PROFILE_COMPARISON_NOT_REGISTRATION_CLOSURE.
WHAT_CHANGED: Frozen solvers reused for72 fits, retaining source/peak unrotated starts and one primary rotated start per patch. No image transformed and no best-cost selection.
EQUATION_OR_MAPPING: Existing separable/rotated Voigt product plus constant background, uniform normalized residuals and unchanged parameter bounds; positions in pixels.
VERIFICATION: Four existing profile tests PASS;72 fits terminate successfully; unrotated start-center differences at most1.98e-6px. Rotated relative residual norms range0.03690-to0.11977. Source/export hashes checked; foundation audit PASS/foundation BLOCKED.
CONTROLLING_BLOCKER: profile_background_adequacy_and_coordinate_uncertainty.
NEXT_ACTION: Examine structured residuals and background adequacy before treating fitted centers as truth. A consistent profile-based multi-shell map requires the same center estimator on every shell, not mixing outer fits with inner raw centroids.
CLAIM_BOUNDARY: Optimizer success, small start dependence or window consistency is not physical accuracy or a statistical uncertainty bound. No applied registration, alpha, temperature, Xie holdout or Full Topic13 promotion.

## Measured comparison

| Dataset | Maximum rotated-fit versus raw-centroid distance | Maximum rotated-center difference between windows |
| --- | --- | --- |
| 400nm | 0.74407px | 0.07712px |
| 800nm | 0.67070px | 0.05756px |

Baseline OFF indices and nominal patch locations are exactly those of the preceding multi-Bragg audit. All six shell4 peaks are retained, with half-widths4 and8. Unrotated fits start at both the nominal window center and intensity maximum. The rotated fit starts from the unrotated nominal solution at angle pi, as in the existing controlled solver. No new source width bounds, residual weights or stopping tolerances are introduced.

The much smaller window dependence of the fitted centers is promising for instrument modeling, but the result measures estimator dependence, not an independently known centroid bias. Actual peak centers are not known here. Residuals of3.69-to11.98% remain, and no measured detector noise floor establishes whether they are acceptable. A constant background and separable Voigt form may be inadequate. Rotated multi-start behavior on these new patches has not been tested; the earlier central-beam test does not establish it for them.

This changes the interpretation of the previous shell-transfer failure: radial coordinate distortion is not the only plausible explanation. Raw moment/background effects are large enough to matter. It would be premature to add more map-distortion parameters or apply the earlier affine centroid map as a physical correction.

Evidence: `artifacts/t13_outer_bragg_profiles.json`, including all parameters, bounds activity, optimizer status, residual norms, window comparisons and source/array hashes. No raw image is published by this pass.
