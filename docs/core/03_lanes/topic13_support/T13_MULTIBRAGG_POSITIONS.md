# Baseline multi-Bragg position check

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Eighteen candidate Bragg patches per processed scan contain interior maxima at both fixed window sizes. Pixel-scale offsets from the nominal reciprocal map are measured.
WHAT_REMAINS_OPEN: Subpixel peak/background model, indexing and distortion uncertainty, finite-patch response/covariance and UET mapping.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: POSITION_DIAGNOSTIC_NOT_GEOMETRY_CALIBRATION.
WHAT_CHANGED: Baseline OFF multi-peak runner, two tests, artifact and this note; no fitted map, image shifting or smoothing.
EQUATION_OR_MAPPING: Integer local maxima and uncorrected intensity centroids relative to nominal reciprocal coordinates, in pixels.
VERIFICATION: Two tests PASS in the scientific pass;36 patches at two window sizes measured with no boundary maxima. Source/export hashes checked. Foundation audit PASS with foundation BLOCKED; this is not physical validation.
CONTROLLING_BLOCKER: peak_shape_background_and_geometry_uncertainty.
NEXT_ACTION: Quantify generic-q patch sensitivity to coordinate ambiguity before physical extraction; reuse existing profile/background methods rather than recentering on integer maxima.
CLAIM_BOUNDARY: Processed-image peak containment is not independent indexing, a statistical uncertainty bound, physical displacement, alpha or Full Topic13 closure.

## Measured outcome

Only OFF rows at delays below-0.5ps are averaged. Missing values propagate rather than being replaced. Candidate reciprocal vectors lie within2.05 times the first reciprocal-vector magnitude; the origin is excluded. Window half-widths4 and8 pixels were fixed before signal inspection.

| Dataset | Maximum integer-peak offset | Maximum centroid offset, radius4 | Maximum centroid offset, radius8 |
| --- | --- | --- | --- |
| 400nm | 1.22964px | 1.06162px | 1.13240px |
| 800nm | 1.79612px | 1.12193px | 1.17385px |

The integer maxima agree between the two window sizes at each candidate. Centroids depend on the window, reflecting possible background/shape effects. Neither statistic is a fitted subpixel center or confidence interval. No boundary maximum is found; that rules out one simple truncation symptom, not all peak misidentification.

These offsets are comparable in scale to the earlier1.5-pixel half-width generic-q footprints. Radial offset versus square half-width is only a scale comparison, not proof that a peak leaves the square or that a diffuse patch shares the same displacement. The nominal support/rank result therefore remains conditional until geometry sensitivity is measured.

The processed images inherit source symmetrization. Mirrored ideal lattice sets share Bragg locations, so this diagnostic cannot establish handedness or independent orientation accuracy. No correction is applied. The generic-q route remains plausible, but not calibrated.

Evidence: `artifacts/t13_multibragg_positions.json`, including nominal/measured coordinates, contrast, baseline indices and source/array hashes. Raw images remain local-only.
