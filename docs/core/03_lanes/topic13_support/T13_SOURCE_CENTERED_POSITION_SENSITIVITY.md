# Source-centered position sensitivity

MAJOR_RESULT_CLOSURE: PARTIAL; raw image moment differences measured, no physical registration closure.

WHAT_IS_ACTUALLY_CLOSED: Both400nm cuts were inspected around the nominal zero-order source position (row242,column247). Source treat_pickle.ipynb cell13 uses half-width15 for its Voigt fitting ROI; this diagnostic instead computes unmodified intensity centroids. Half-widths10 and20 were declared as sensitivity cases before running and all are retained. Every image's global intensity maximum lies inside all three ROIs.

WHAT_REMAINS_OPEN: Moment shifts can arise from background and shape differences, not only translation. Source Voigt fit replication, cut-specific geometry and registration uncertainty remain open. The nominal source notebook selects800nm by default; peak containment is a data check for the400nm use here, not a claim of matched physical calibration.

DEPENDENCY_UNLOCKED: Registration-method comparison only; no physical unlock.

STATUS: MOMENTS_MEASURED_REGISTRATION_OPEN.

WHAT_CHANGED: Moment diagnostic/tests and [all row-level positions](../../07_artifacts/topic13/t13_ued_beam_position_audit.json). External find_peak.py inspected as text to check ROI slicing convention, not executed or redistributed.

EQUATION_OR_MAPPING: Positive-intensity weighted raw pixel coordinates, no background subtraction, source fit, shifting, interpolation or new UET physical equation.

VERIFICATION: Three tests PASS; axes/localized image, edge/global-peak handling and invalid input. Source hash checks and inert decode of both cuts; foundation audit PASS with foundation BLOCKED.

CONTROLLING_BLOCKER: At source half-width15, maximum between-cut centroid distances are0.0399854px OFF and0.0401461px ON. Maximum within-cut ON/OFF distances are0.00958964px and0.0119495px. Across half-widths10/15/20, between-cut maxima remain about0.0392-0.0407px. This supports a reproducible moment difference, not a pure-translation estimate or statistical significance. Up to4.16%,2.58%,1.85% of ROI intensity lies on its one-pixel boundary for the respective widths; no claim that tails or background are negligible.

NEXT_ACTION: Compare source-style fitted positions with raw moments and assess background/shape sensitivity before applying an image transformation. Preserve both cuts; quantify any interpolation-induced change separately. Do not attribute prior tile differences to this moment difference without a forward sensitivity calculation.

CLAIM_BOUNDARY: No correction applied, no physical displacement/noise estimate, no covariance, heat, temperature, alpha or full-topic closure. No holdout read or claim promotion; detector centroids are not UET states.
