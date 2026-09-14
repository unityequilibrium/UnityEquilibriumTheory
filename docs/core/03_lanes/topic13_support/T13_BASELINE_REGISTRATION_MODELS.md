# Baseline-only registration model comparison

MAJOR_RESULT_CLOSURE: PARTIAL; a common translation is insufficient relative to richer tested coordinate models.
WHAT_IS_ACTUALLY_CLOSED: Translation, similarity and affine centroid maps are compared with internal leave-one-peak-out checks at two extraction radii. Richer maps reduce held-out-peak residuals, but window-dependent bias remains.
WHAT_REMAINS_OPEN: Centroid/background bias, distortion interpretation, independent registration uncertainty and detector forward/covariance mapping.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: BASELINE_MODEL_COMPARISON_NOT_CALIBRATED_CORRECTION.
WHAT_CHANGED: Linear baseline coordinate fits, two tests and hashed artifact; no ON/OFF signal fitting, image transformation or applied correction.
EQUATION_OR_MAPPING: Nominal position plus fitted linear displacement, centered at pixel(256,256). Translation has2, similarity4, affine6 coefficients; displacement intercepts pixels, linear slopes dimensionless.
VERIFICATION: Two tests PASS, including exact known maps and excluded-point recovery and rank-deficiency rejection. Twelve real-data model/window fits and all leave-one-peak-out cases recorded. Foundation audit PASS with foundation BLOCKED.
CONTROLLING_BLOCKER: centroid_shape_bias_and_physical_registration_uncertainty.
NEXT_ACTION: Check peak/background model bias and source preprocessing before selecting a registration model; propagate baseline-estimated coordinate uncertainty into patch response. Do not interpret the internal residual RMS as a calibrated uncertainty or automatically apply the most flexible model.
CLAIM_BOUNDARY: Fits use baseline OFF centroid metadata only. No physical coefficient/alpha fit, Xie access, external validation, image warp or Full Topic13 promotion.

## Internal excluded-peak residual RMS, pixels

| Dataset/window | Translation | Similarity | Affine |
| --- | --- | --- | --- |
| 400nm/radius4 | 0.7870 | 0.3224 | 0.2948 |
| 400nm/radius8 | 0.9000 | 0.3117 | 0.2683 |
| 800nm/radius4 | 0.7478 | 0.3776 | 0.3583 |
| 800nm/radius8 | 0.8377 | 0.3782 | 0.3493 |

Each peak is predicted using the other17 peaks; the fit is not evaluated solely on its training positions. Nevertheless, source symmetry averaging correlates the peaks, so these are internal diagnostics rather than independent validation. Equal-weight least squares is an exploratory model choice, not a claim of equal or independent measurement noise.

Affine maximum excluded-peak errors remain0.523-to0.607px across these cases. Changing extraction radius changes the fitted affine map by up to0.215px for400nm and0.154px for800nm at the fitted peak locations. These method differences are not probability distributions, and bounds at those locations do not cover every generic-q detector coordinate.

The source map may therefore need more than a common translation, but this result does not identify whether the discrepancy comes from physical rotation/strain, detector distortion, interpolation or centroid/background bias. The same baseline images generated both window estimates. Their agreement cannot establish independence, and lower residuals do not certify physical geometry.

## Application boundary

This pass deliberately estimates nuisance detector coordinates from baseline information, not from the desired thermal curve. It does not weaken the prohibition on fitting alpha to a holdout. No candidate map is selected or applied here. A valid next use requires an explicit coordinate/uncertainty model and finite-patch response, rather than translating the earlier +/-2px stress envelope into an error bar or silently replacing it with a smaller fitted residual.

Evidence: `artifacts/t13_baseline_registration_models.json`, with coefficients, training/excluded-peak residual vectors, window comparisons and source/code hashes.
