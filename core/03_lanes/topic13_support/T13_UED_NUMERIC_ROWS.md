# UED numeric rows and source preprocessing

MAJOR_RESULT_CLOSURE: PARTIAL. Storage decoding and row identities are established; physical population/temperature mapping remains open.

WHAT_IS_ACTUALLY_CLOSED: Both processed records are interpreted without invoking serialized globals. There are 38 paired image rows for 400 nm and 32 for 800 nm, each image 512 by 512. Delay arrays, reciprocal calibration, image buffer hashes and finite-value counts are exported as non-executable JSON summaries. Source time-index meaning is reconciled without changing any delay.

WHAT_REMAINS_OPEN: Spatial validity masks/full numeric image export, processing covariance, physical timing uncertainty, absolute intensity meaning, detector-to-mode inversion, material equivalence and independent Phi coupling.

DEPENDENCY_UNLOCKED: Source-row and mask-aware signal inspection only; no physical downstream gate.

STATUS: NUMERIC_ROWS_EXTRACTED_MAPPING_OPEN; full_core_unlock=false.

WHAT_CHANGED: Added an inert pickle-syntax interpreter, strict source-table interpretation, tests and numeric inventory. This is not a general pandas unpickler. Unsupported layouts stop. The source notebooks are read as JSON and never run.

EQUATION_OR_MAPPING: The source stores t0_index=8 using one-based numbering, so the zero-time row is 7 in Python numbering. The delay array already has zero there. Calibration is approximately 0.03105463 and 0.03101929 inverse angstrom per pixel for 400 and 800 nm respectively, as interpreted through the author notebook. These are detector calibrations, not Phi calibrations.

VERIFICATION: Nine linked tests pass: inert handling of a serialized eval reference, numeric buffer decoding, shared references, truncated-input rejection, opaque ZIP inventory, source-layout parsing, image-pair preservation, missing-value preservation and index-base behavior. First attempts exposed NumPy namespace and pandas block-layout differences; the reader accepts only explicit known namespace aliases and the tests now construct the declared source layout. Raw source hash chain and member compression checks complete successfully. No external callable is invoked and no missing pixel is filled.

CONTROLLING_BLOCKER: mask_aware_detector_signal_and_uncertainty_missing.

NEXT_ACTION: Export reviewed numeric images with per-frame validity masks; compare a common spatial support across time and pump states. Establish how mask selection and symmetry averaging affect uncertainty before estimating any population or relaxation rate. A processed image ratio is not automatically a mode population.

CLAIM_BOUNDARY: Seventy paired processed-image rows, not seventy independent experiments or absolute phonon populations. No image statistics are labeled heat or temperature. No holdout use, physical alpha, rate fitting or Full Topic 13 promotion.

## Source-backed interpretation

The pinned `treat_pickle.ipynb` sets one-based t0_num and subtracts the stage
position at t0_num-1 before saving t0_num as t0_index. Cells 1 and 24 resolve the
apparent index mismatch. No 0.26664 ps shift is warranted by that metadata.
Physical uncertainty in locating pump/probe time zero is a separate issue.

Cell 20 masks rotated pixels with intensity below 100, combines ON/OFF NaN masks,
then uses nanmean across symmetry-related images. The archived arrays contain
482116 and 401488 nonfinite pixel occurrences respectively, counted across all
paired frames. These are occurrences, not counts of unique spatial locations.
The extraction retains the absence of finite values; it does not repeat or alter
the author's threshold. Intensity-dependent masking need not be missing at random,
and symmetry-averaged pixels need not have independent noise.

Delay coverage is -2.39976 to 42.26244 ps (400 nm) and -2.39976 to 8.93244 ps
(800 nm). Different coverage does not imply a measured difference in relaxation.
Any later comparison must declare a shared time window and preprocessing policy.

Source: [Zenodo 14760926](https://zenodo.org/records/14760926), CC-BY-4.0;
author preprocessing at [commit 7f7036b](https://github.com/remiclaude/UED_processing/blob/7f7036bfda28f9330f19b40e57f4edf464b67d64/treat_pickle.ipynb).
The code copy remains local-only because its redistribution license is not established.
Evidence: `artifacts/t13_ued_numeric_inventory_audit.json`, including source hashes,
individual buffer/row hashes and explicit open uncertainties. Full image arrays are
not exported in this wave; JSON contains their numerical summaries and identifiers.
