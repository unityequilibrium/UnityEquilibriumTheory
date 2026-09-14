# Raw cut signal sensitivity

MAJOR_RESULT_CLOSURE: PARTIAL; between-cut whole-detector signal difference quantified, not physical uncertainty.

WHAT_IS_ACTUALLY_CLOSED: On the 38 aligned 400nm rows, all pixels are finite and share a 512x512 support. Arithmetic ON/OFF mean ratios are therefore also total-intensity ratios. Each cut is baseline-subtracted using all strictly negative source-relative delays (exploratory choice, not a preregistered author estimator). Maximum absolute cut difference is 0.0001555084076; RMS difference is 0.0000555467890. Peak-to-peak responses are 0.0006306933912 and 0.0008050467114. These are dimensionless detector ratios, not percent temperature change.

WHAT_REMAINS_OPEN: Whether differences arise from acquisition noise, drift, gain or physical preparation. Whole-detector sums mix direct beam, Bragg and diffuse components and can conceal opposing spatial changes. They cannot identify phonon energy or temperature.

DEPENDENCY_UNLOCKED: Cut-resolved robustness assessment only; no physical unlock.

STATUS: CUT_DIFFERENCE_MEASURED_CAUSE_UNRESOLVED.

WHAT_CHANGED: Descriptive comparison audit, three tests, [generated rows and metrics](../../artifacts/t13_ued_cut_signal_audit.json). Corrected previous pooling locator to treat_pickle.ipynb, confirmed against pinned Git blob 12410c47274320d1c6e770872772e5d8cf864be0; regenerated pooling artifact/hash chain.

EQUATION_OR_MAPPING: Ratio of ON/OFF image means, baseline subtraction and ratio after file-axis pooling. Pooling is denominator-weighted, not the arithmetic average of cut ratios. No new UET physical equation or registry claim is introduced.

VERIFICATION: Six cut-signal/pooling tests PASS, including identical-cut and unequal-intensity fixtures. Foundation audit PASS with foundation BLOCKED. Source/hash dependencies checked before computing. Maximum pooled versus unweighted raw-ratio difference is 0.0000119596209; pooled baseline response differs from the individual cuts by at most 0.0000681904791 and 0.0000873179285.

CONTROLLING_BLOCKER: Pre-sorting acquisition, independent repetitions and detector gain remain unverified. The two-cut difference is not a covariance estimate, standard error, confidence interval, statistical significance result or causal leakage measurement.

NEXT_ACTION: Cut-resolved spatial/geometry diagnostics with acquisition provenance; evaluate whether the physical observable is identifiable before investing in full covariance estimation. Do not substitute this whole-detector scalar for the complementary mode-resolving design.

CLAIM_BOUNDARY: This is exploratory source sensitivity, not TTG validation, alpha calibration, heat/temperature inference or Full Topic 13 closure. No holdout, clipping, fit, smoothing, physical acceptance threshold or claim promotion.
