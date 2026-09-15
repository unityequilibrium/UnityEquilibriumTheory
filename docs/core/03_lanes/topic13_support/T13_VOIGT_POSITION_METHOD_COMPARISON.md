# Voigt position method comparison

MAJOR_RESULT_CLOSURE: PARTIAL; source-form profile optimization compared with raw centroids, not registration accuracy.

WHAT_IS_ACTUALLY_CLOSED: All152 ON/OFF ROIs from the two400nm cuts were fitted from two initial positions (304 fits). All optimizers terminated successfully; maximum initial-position disagreement is5.86e-10px. This rules out a material difference between these two starts for this solver, not other minima or model error. Maximum between-cut position differences are0.0469088px ON and0.0469301px OFF.

WHAT_REMAINS_OPEN: The relative residual L2 norm is0.112989-0.114387 (about11.3% of ROI data L2 norm). Optimizer convergence therefore does not establish an accurate profile or subpixel physical calibration. Source-form fitted positions can differ from raw intensity centroids by0.150594px, greater than the between-cut difference; that is estimator disagreement, not a calibrated error bound. Shape/background, rotation/asymmetry, weighting and detector-response effects remain open.

DEPENDENCY_UNLOCKED: Profile residual/model comparison only; no physical unlock.

STATUS: METHOD_COMPARISON_REGISTRATION_OPEN.

WHAT_CHANGED: Independent source-form Voigt solver, tests, [full fit records](../../07_artifacts/topic13/t13_ued_voigt_position_audit.json). Source helper stored ignored/local-only, read as text and not imported or executed. Source Git blob c2a9dd3b357f7f6d64d886d1fe354fbaabd017e0 matches pinned upstream find_peak.py at commit7f7036bfda28f9330f19b40e57f4edf464b67d64.

EQUATION_OR_MAPPING: Constant offset plus amplitude times row/column normalized Voigt profiles. Source bounds and source initial widths are retained; one source-center start and one peak-pixel start are both reported. ROI intensity is divided by its maximum, rescaling amplitude/offset without changing the uniform least-squares objective's minimizer. scipy least_squares TRF differs from the source lmfit default; this is not an exact source-pipeline replication. SciPy voigt_profile uses the same standard Voigt form with defined zero-width limits.

VERIFICATION: Two tests PASS, including synthetic position recovery at both starts with intensity rescaling. All152 actual ROIs retained. F0 inventory369/no duplicates; foundation/compatibility audits PASS while physical states remain BLOCKED. Actual file/hash chain checked. Source lmfit is not installed and was not silently replaced under its name.

CONTROLLING_BLOCKER: Profile/model adequacy, not optimizer starting position within the tested pair. Residual norms are not chi-squared, confidence intervals or a new acceptance threshold because detector covariance is unavailable.

NEXT_ACTION: Inspect residual structure and compare an explicitly declared rotated/background model before transforming images. Keep source-form fit as a comparator rather than selecting a flexible model purely for lower residual. Do not infer that fitting an instrument profile supplies independent alpha or thermal closure.

CLAIM_BOUNDARY: No image shifted, no fitted uncertainty accepted, no detector-to-heat conversion, alpha calibration, holdout use or Full Topic13 promotion. The1e-10 solver stopping settings are numerical criteria, not physical precision claims or changes to the causal threshold.

Source: [pinned helper](https://github.com/remiclaude/UED_processing/blob/7f7036bfda28f9330f19b40e57f4edf464b67d64/find_peak.py).
