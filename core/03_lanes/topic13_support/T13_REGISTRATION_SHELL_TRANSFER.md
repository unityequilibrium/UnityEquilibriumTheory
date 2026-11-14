# Registration transfer with whole radial shells excluded

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Grouped radial transfer exposes larger outer-shell errors than the earlier aggregate one-peak-out diagnostic.
WHAT_REMAINS_OPEN: Peak/background bias, distortion interpretation, independently calibrated geometry uncertainty and detector forward response.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: INTERNAL_GROUPED_TRANSFER_NOT_CALIBRATION.
WHAT_CHANGED: Existing baseline coordinate fits reused with entire shells excluded; two tests, artifact and this note. No correction applied.
EQUATION_OR_MAPPING: Shell label h^2+k^2+hk verified against squared source reciprocal magnitudes; train on two shells and predict the remaining six peaks.
VERIFICATION: Two tests PASS: exact affine transfer with disjoint groups, and detection of a synthetic shell-specific bias.36 grouped real-data fits evaluated; source hashes checked. Foundation audit PASS with foundation BLOCKED.
CONTROLLING_BLOCKER: centroid_shape_bias_and_physical_registration_uncertainty.
NEXT_ACTION: Focus peak/background-model adequacy on outer-shell centroids and compare against raw/source processing. Do not add higher-order distortion parameters solely to reduce these residuals or treat one-peak-out RMS as a global geometry error bound.
CLAIM_BOUNDARY: The excluded shell still belongs to the same symmetry-processed image. This is internal validation, not an independent experiment, calibrated uncertainty, alpha or full-topic closure.

## Affine RMS on excluded shells, pixels

| Dataset/window | Inner shell1 | Middle shell3 | Outer shell4 |
| --- | --- | --- | --- |
| 400nm/radius4 | 0.2277 | 0.3048 | 0.5157 |
| 400nm/radius8 | 0.1887 | 0.2935 | 0.4816 |
| 800nm/radius4 | 0.2841 | 0.3893 | 0.6337 |
| 800nm/radius8 | 0.2879 | 0.3803 | 0.6344 |

The earlier aggregate one-peak-out affine RMS0.268-to0.358px therefore cannot be read as a guaranteed accuracy everywhere. The grouped check withholds all same-radius peers, avoiding one source of optimistic transfer estimates. It does not remove shared image preprocessing or establish independence across shells.

Similarity models have outer-shell RMS0.511-to0.676px, and translation models0.675-to0.886px. Richer linear models remain useful comparators, but systematic radial/shape effects persist. The experiment does not distinguish a true geometric distortion from intensity-dependent centroid bias; neither a higher-order distortion fit nor physical strain is inferred.

Each shell has six peaks, each training set twelve, and each model fit is checked for full design rank. All three models and both windows are retained. No thermal curve, pump response or Xie holdout participates in the fit.

Evidence: `artifacts/t13_registration_shell_transfer.json` records train/excluded indices, residual vectors and hashes. Original baseline registration artifacts are preserved.
