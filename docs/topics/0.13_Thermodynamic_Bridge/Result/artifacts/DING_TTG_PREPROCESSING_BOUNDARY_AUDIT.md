MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the documentary preprocessing/uncertainty boundary only.

WHAT_IS_ACTUALLY_CLOSED: The archived Supplementary Information states that phase- and amplitude-grating signals are separated, the phase-grating waveform is smoothed with Savitzky-Golay to suppress acoustic oscillations, and waveform error is estimated from negative-time-delay variation; typical reported error is around `0.01`.

WHAT_REMAINS_OPEN: The three reviewed supplementary PDFs provide no machine-readable waveform rows, pointwise uncertainty/covariance, or enough located detail to reproduce the filter window/order. This does not separate measured points from calculated curves in Fig. 1d or supply Ding-compatible `C_src`, physical `Phi`, `alpha_Phi_K`, or transport.

DEPENDENCY_UNLOCKED: A source-grounded preprocessing contract for future figure-level comparison only. No numeric-source acceptance, calibration, prediction, or Core dependency is unlocked.

STATUS: `PASS_SUPPLEMENTARY_METHOD_BOUNDARY`; source hashes match the existing supplementary review package.

WHAT_CHANGED: Added a read-only archived-PDF auditor, focused tests, JSON evidence, and this interpretation note. The PDFs, source packages, digitized CSV, full Topic 13 gate, and Core artifacts were not changed.

EQUATION_OR_MAPPING: `sigma_signal` is estimated from negative-time-delay baseline variation; the authors report a typical value around `0.01`. This source-level waveform error is not combined with the distinct pixel-derived digitization bound. The shape comparison remains `y_TTG=Delta_Tq(t)/Delta_Tq(0)` versus `y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)`.

VERIFICATION: Hashes for all three archived supplementary PDFs match their manifest; targeted text checks find the stated filter/noise method and do not find filter window/order parameters; the existing package records no numeric rows or `C_src`. No calibration, fitting, holdout access, source modification, or claim promotion.

CONTROLLING_BLOCKER: `authorized_numeric_waveform_and_pointwise_uncertainty_missing`.

NEXT_ACTION: For any measured waveform comparison, obtain authorized row data and filter settings or keep results explicitly figure-derived; keep the author's approximate error, pixel extraction bound, and model uncertainty as separate terms.

CLAIM_BOUNDARY: Documentary method and uncertainty boundary only; not raw-data reproduction, experimental validation, alpha calibration, temperature prediction, or Full Topic 13 closure.
