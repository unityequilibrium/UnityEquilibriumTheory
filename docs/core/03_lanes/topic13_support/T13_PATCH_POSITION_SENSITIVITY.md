# Generic-q detector signal sensitivity to readout coordinates

MAJOR_RESULT_CLOSURE: PARTIAL; actual coordinate sensitivity measured rather than inferred from peak offsets.
WHAT_IS_ACTUALLY_CLOSED: Nine fixed readout offsets retain21-to22 usable rows per case but can alter baseline-subtracted detector ratios by more than the nominal signal amplitude in the most sensitive patches.
WHAT_REMAINS_OPEN: Registration/shape model, calibrated coordinate uncertainty, detector covariance, finite-patch scattering response and UET mapping.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: EXTERNAL_READOUT_STRESS_TEST_NOT_CALIBRATION.
WHAT_CHANGED: Actual ON/OFF patch-ratio curves computed for fixed nominal and axial +/-1,+/-2 pixel offsets; two tests and source-hashed artifact. No image moved or optimum chosen.
EQUATION_OR_MAPPING: r=sum ON/sum OFF; delta r=r-mean(r at delay<-.5ps). Each fixed offset has its own unchanged baseline rule. Units dimensionless ratio and pixels.
VERIFICATION: Two tests PASS; source/export hashes checked, all16 q/mirror/dataset cases evaluated. Foundation audit PASS with foundation BLOCKED. No physical threshold or data value changed.
CONTROLLING_BLOCKER: registration_response_and_detector_covariance.
NEXT_ACTION: Model baseline registration/background and propagate its uncertainty through the finite-patch response. Do not perform a unique population/variance inversion at nominal coordinates while ignoring the measured sensitivity.
CLAIM_BOUNDARY: Offsets are deterministic stress scenarios, not a calibrated error bound or confidence interval. No alpha, branch population, temperature, holdout, fit or full-topic promotion.

## Measured scale

Offsets are(0,0),(+/-1,0),(0,+/-1),(+/-2,0),(0,+/-2), in row/column pixels. The prior1.5-pixel half-width is retained. A patch is unresolved if it crosses the image boundary, contains any nonfinite ON/OFF value at any time, or has a nonpositive OFF sum. No replacement pixels or selected frames are substituted.

| Dataset | Largest absolute change from nominal curve | Nominal maximum absolute signal in that same patch |
| --- | --- | --- |
| 400nm | 0.0304602 | 0.0179255 |
| 800nm | 0.0429036 | 0.0335967 |

These are maxima over the declared cases, offsets and times, not typical errors. They occur at G=(1,2,0) but need not use the same q/mirror in each scan. All curves and offsets are retained in the artifact. Across individual q/mirror cases, maximum curve differences span0.01777-to0.03046 for400nm and0.01814-to0.04290 for800nm. The examples demonstrate that position sensitivity cannot be assumed negligible; they do not establish a statistical significance level.

All-offset-complete support counts remain21 or22, so missing pixels are not the mechanism removing these particular row sets. Spatial gradients, image processing and noise can all contribute to the changed ratios. This audit does not distinguish those causes or assert a true detector translation. The baseline subtraction is repeated with the same time rule per offset, not tuned to flatten the response.

The two datasets are not merged and the mirror scenarios are not independent replicates. No optimum offset is selected. The ideal nominal row-space result remains algebraically valid, but extracting a physical target requires the coordinate-dependent forward model and covariance, not just full rank at nominal q.

Evidence: `artifacts/t13_patch_position_sensitivity.json`, with complete ratio/baseline-subtracted curves, delays, source/array hashes and unresolved cases. Raw images remain local-only.
