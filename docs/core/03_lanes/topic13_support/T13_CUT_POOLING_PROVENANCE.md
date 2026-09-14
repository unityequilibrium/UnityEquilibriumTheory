# Topic 13 cut pooling provenance

MAJOR_RESULT_CLOSURE: PARTIAL; source pooling operation identified, physical covariance remains open.

WHAT_IS_ACTUALLY_CLOSED: Pinned treat_pickle.ipynb cell 1 sums ON/OFF images across matching files before subsequent processing. It uses the final input table's stage positions to form the relative time axis. Actual 400nm cut stage/delay coordinates agree, so this inspection finds no actual time-axis mismatch. No independence check or exposure weighting appears in this import/pooling cell. Corrected the earlier notebook-name locator: local bytes match Git blob 12410c47274320d1c6e770872772e5d8cf864be0, which the pinned upstream tree assigns to treat_pickle.ipynb.

WHAT_REMAINS_OPEN: How each RAW_sorted image was accumulated, whether cuts are independent acquisitions, and whether differences reflect drift or detector noise. No independent-frame axis was found in the supplied table layout. The observed repository tree and treat_pickle.ipynb at the same commit expose processing of already sorted files, not an established pre-sorting acquisition protocol.

DEPENDENCY_UNLOCKED: Cut-resolved sensitivity only; no physical unlock.

STATUS: POOLING_IDENTIFIED_INDEPENDENCE_UNVERIFIED.

WHAT_CHANGED: Pooling provenance audit, three tests and [generated artifact](../../artifacts/t13_ued_cut_pooling_audit.json), with source/hash linkage to the earlier raw structure audit. No external notebook was executed or redistributed.

EQUATION_OR_MAPPING: Source file-axis image sum, not a new UET equation. Source metadata is preserved separately; neither Temperature_B nor PHI instrument columns are relabeled as UET variables.

VERIFICATION: Three tests passed; actual paired metadata inspected. Pressure, Sensor_B_Ohm and Temperature_B differ in all 38 rows. Maximum Temperature_B difference is 0.0930381333 in unverified sensor units, not an uncertainty or a calibrated temperature excursion. Shutter differs in one row. Foundation audit PASS with foundation BLOCKED.

CONTROLLING_BLOCKER: Pre-sorting acquisition/aggregation semantics and cut independence. These differences alone neither prove physical drift nor invalidate published processing; they prevent silently assuming identical independent trials.

NEXT_ACTION: Retain both cuts for sensitivity analysis without turning between-cut differences into a noise covariance. Seek frame-level acquisition, gain/count and sensor provenance; do not infer exposure counts from nimages=2 or sensor calibration from its name.

CLAIM_BOUNDARY: No covariance closure, independent alpha, thermal observable, holdout access or topic promotion. Raw images remain local-only. The 800nm package has one file, so the two-cut diagnostic must not be transferred to it.

Source: [pinned processing repository](https://github.com/remiclaude/UED_processing/tree/7f7036bfda28f9330f19b40e57f4edf464b67d64). Scientific conclusions above rely on the locally hash-locked notebook and raw row artifacts, not the repository file list alone.
