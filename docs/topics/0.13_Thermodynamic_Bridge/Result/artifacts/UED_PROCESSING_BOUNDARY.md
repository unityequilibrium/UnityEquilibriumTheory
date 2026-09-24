# UED processing boundary: five rotations, paired support and response weights

MAJOR_RESULT_CLOSURE: PARTIAL; the pinned source-to-save path and ideal averaging identities are resolved, not physical calibration.
WHAT_IS_ACTUALLY_CLOSED: The archived notebook constructs five rotations, applies paired intensity/NaN masks and saves their averages. Ratio-of-averages requires OFF-intensity weights rather than equal ratio weights.
WHAT_REMAINS_OPEN: Whether the published arrays used this notebook revision, actual rotation/mask weights, detector covariance and physical material/Phi normalization.
DEPENDENCY_UNLOCKED: None. This diagnostic does not change any physical dependency or the separate O(2)/He-4 acceptance record.
STATUS: SOURCE_PATH_VERIFIED_PUBLISHED_ARRAY_LINEAGE_OPEN.
WHAT_CHANGED: Added a static source audit, eight tests and a machine-readable topic-owned artifact; neither the upstream notebook nor any image was edited.
EQUATION_OR_MAPPING: H_m(N)=sum_i exp(i*m*i*pi/3)/N; processed ON/OFF=sum_i w_i(ON_i/OFF_i), with w_i=M_i OFF_i/sum_j M_j OFF_j.
VERIFICATION: Eight tests pass, pinned notebook SHA-256 matches the existing inventory, source cells 19/20/24 are checked through the save call, and the two hashed closure controls are unchanged. Initial test collection failed on the numbered-directory import; corrected loader passes. No foundation, thermal or calibration audit was rerun.
CONTROLLING_BLOCKER: published_array_processing_lineage_and_detector_operator.
NEXT_ACTION: Replay raw-cut pooling, centering, interpolation and masking using source-locked parameters, then compare with published arrays before selecting any correction or inversion.
CLAIM_BOUNDARY: Source-code behavior does not prove archive execution history. Ideal/synthetic examples are not measured residual explanations, new data, uncertainty bounds, alpha calibration or a full-topic closure.

## Evidence and Ownership

- Owner: Topic 0.13, source-method diagnostic, not a new Core equation.
- [Machine-readable artifact](ued_processing_boundary.json).
- [Runner](../../Code/03_Research/Research_UED_Processing_Boundary.py).
- [Tests](../../Code/03_Research/test_ued_processing_boundary.py).
- Source: local-only `Data/03_Research/raw/ued_treat_pickle_7f7036b.ipynb`, pinned UED_processing commit `7f7036bfda28f9330f19b40e57f4edf464b67d64`.
- Notebook SHA-256: `1492289fde53f4cadeacb7e4132344c899a660c31fad23a305f4024b1c2c7b52`, matching the prior numeric-inventory record.
- The notebook is parsed as JSON/text/AST only, never executed. No pickle deserialization or new remote acquisition occurs. The notebook is not redistributed; code licensing remains unestablished.

## What the Source Actually Says

Zero-based cell 19 describes sixfold symmetry but constructs angles alpha plus
0, 60, 120, 180 and 240 degrees, not 300 degrees. It rotates both channels using
bilinear interpolation. Cell 20 removes intensities below 100 in either channel,
shares the missing-value mask between ON and OFF and averages over rotations.
Cell 24 passes those averages through the declared zero-sigma Gaussian step and
writes the ON/OFF columns. No compensating sixth append appears in the inspected
notebook. The exact source hash, rather than permissive text matching alone,
locks this conclusion to the inspected revision.

This is not yet a reproduction of the published images: notebooks can be run
out of order, use different input cuts/parameters, or differ from the revision
that created an archive. The notebook's save path proves a static code route,
not execution provenance. Do not silently change five to six.

## Consequences for the Observable Map

For exact unmasked rotations, the five-angle average retains magnitude 0.2 of
angular harmonics m=1 through 5; the six-angle average cancels them to numerical
roundoff. Both retain m=0 and m=6. An initial alpha changes phase, not these
magnitudes. Equivalently, A5=(6*A6-R5)/5. This is a finite-sum identity, not an
estimate of the real image discrepancy: pixel interpolation, crop boundaries
and per-pixel masks violate the ideal uniform-rotation assumptions.

With paired retained support, ON/OFF of the two averaged images is the
OFF-intensity-weighted mean of individual rotation ratios. A manufactured
example gives 1.6 instead of the equal-weight value 1.5. A second manufactured
example crosses the unchanged intensity threshold by 0.002 and changes the
ratio from 2 to 1.400002 because one rotation enters support. Neither number is
an experimental error estimate. The point is that differentiating a fixed
linear average across a support change is invalid.

For fixed geometry and fixed masks, the conditional forward map is
`I_processed=W I_raw`. Its covariance is `W Sigma_raw W^T`, not automatically
the independent-replicate covariance divided by five. Reusing samples during
rotations/interpolation can correlate outputs. The manufactured covariance test
contrasts independent and perfectly shared samples; it does not assert either
extreme for this detector. Actual W and input covariance are still required.

The existing 18-to-74 residual/scatter ratios are not attributed to this count
discrepancy. Their source is still open. No image correction, profile refit,
holdout read, new Phi state or physical parameter is introduced.

## Bounded Next Experiment

1. Match raw archive member/cut identity, delay rows and acquisition pooling to each processed scan; do not choose pooling to minimize a thermal residual.
2. Recover declared centers, angles, scale, interpolation boundary convention and ON/OFF masks. Record any unrecoverable runtime setting rather than fitting it silently.
3. Replay five-angle source processing independently without executing the notebook. Compare finite support and pixel residuals with the saved arrays. Predeclare numeric comparison tolerances from datatype/interpolation reproducibility, not from UET agreement.
4. Only after lineage is supported, use six-angle processing as a separately named counterfactual. Propagate the actual processed-image operator through finite patches and paired ratios before physical inversion.

If replay inputs are unavailable, retain the lineage blocker. It does not imply
that UET is false or that all Topic 13 work is blocked; it limits this UED-based
material-calibration route. Existing graphite/Phi and physical transport inputs
remain separate requirements.
