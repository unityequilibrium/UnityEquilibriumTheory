# Frozen profile residual versus actual baseline scatter

MAJOR_RESULT_CLOSURE: PARTIAL; observed frame variation is too small to simply relabel the profile discrepancy as that variation.
WHAT_IS_ACTUALLY_CLOSED: Every outer-shell frozen rotated-profile residual is compared with actual OFF baseline frame scatter on identical pixels, without refitting or assuming independent frames.
WHAT_REMAINS_OPEN: Physical error model, structured residual origin, preprocessing bias, coordinate uncertainty and detector response.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: DESCRIPTIVE_RESIDUAL_SCALE_COMPARISON_NOT_STATISTICAL_REJECTION.
WHAT_CHANGED: Fixed fit predictions reused with baseline frame arrays, two tests, artifact and this note; no model/image correction.
EQUATION_OR_MAPPING: Compare ||mean(I)-model|| with sqrt(sum_t||I_t-mean(I)||^2/(N-1)); both divided by ||mean(I)|| for relative metrics. No division by sqrt(N).
VERIFICATION: Two tests PASS. All24 reconstructed mean-profile residuals agree with the prior fit artifact; source/export hashes checked. Foundation audit PASS/foundation BLOCKED.
CONTROLLING_BLOCKER: profile_background_adequacy_and_detector_error_model.
NEXT_ACTION: Inspect spatial residual structure and source-processing effects before extending the profile or using fitted-center errors for calibration. Treat empirical-template or alternate-profile approaches as explicit model comparisons, not automatic fixes.
CLAIM_BOUNDARY: Not a chi-square test, p-value, independent noise estimate or physical accuracy bound. No refit, alpha, Xie access, image shift or full-topic promotion.

## Measured ranges across six peaks and two windows

| Dataset | Observed relative frame scatter | Mean-profile residual / observed frame scatter |
| --- | --- | --- |
| 400nm | 0.1508-to0.1742% | 47.25-to73.99 |
| 800nm | 0.2051-to0.2355% | 17.97-to50.06 |

These are norms over a patch, not single-pixel noise values. The residuals are those of the previously fitted mean image and are not independent test residuals. Nevertheless, they are substantially larger than the actually observed frame-to-frame variation in the same pixels; optimizer success and window agreement alone cannot justify calling the mismatch random baseline scatter.

The samples are processed OFF frames at delays below-0.5ps, not known independent repeats. Their variation can contain drift and correlated preprocessing; it can also omit systematic detector bias common to all frames. Thus the ratios are descriptive scales and must not be interpreted as sigma counts, statistical significance or proof of a unique physical cause. No sample standard error of the mean is inferred.

No fit parameters, missing values or pixels change. The next research question is what systematic structure the residual contains, not how to make the same optimizer return a greener status. A finite-patch response and credible coordinate-error model remain prerequisites for physical second-moment extraction.

Evidence: `artifacts/t13_profile_residual_baseline_scatter.json`, including all baseline indices,24 comparisons and source/array hashes. Raw images remain local-only.
