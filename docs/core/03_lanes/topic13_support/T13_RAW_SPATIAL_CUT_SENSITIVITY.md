# Raw spatial cut sensitivity

MAJOR_RESULT_CLOSURE: PARTIAL; fixed-grid spatial sensitivity measured without a physical mode assignment.

WHAT_IS_ACTUALLY_CLOSED: All 16 disjoint 128x128 tiles of the 512x512 detector were specified before computing tile results. Both 400nm cuts were decoded inertly; every required image buffer was matched by its source hash. Tile sums reproduce the whole-detector ratios within relative tolerance 1e-12. No clipping, interpolation, missing-pixel exclusion or selected-region fit was applied.

WHAT_REMAINS_OPEN: Pixel-to-mode geometry, cut-dependent alignment, detector gain and independent acquisition uncertainty. Tile boundaries have no Bragg/diffuse/thermal meaning. Different denominators prevent interpreting larger local ratio differences as greater physical noise or energy.

DEPENDENCY_UNLOCKED: Geometry-aware cut comparison only; full_core_unlock=false.

STATUS: SPATIAL_DIFFERENCES_MEASURED_PHYSICAL_ATTRIBUTION_OPEN.

WHAT_CHANGED: Fixed-grid audit/tests and [all tile traces and metrics](../../artifacts/t13_ued_cut_tiles_audit.json). No raw images were exported or external pickle callables invoked.

EQUATION_OR_MAPPING: Disjoint detector sums followed by the previous exploratory ON/OFF ratio and negative-delay baseline subtraction. Detector additivity is not an energy-conservation proof. No new physical equation or registry claim.

VERIFICATION: Six tile/cut-signal tests PASS; complete/nonoverlapping partition, localized input, rejection of missing support and full-detector reconstruction. Foundation audit PASS with foundation BLOCKED. All 16 denominators were positive in the acquired data.

CONTROLLING_BLOCKER: Whole-detector agreement cannot establish spatial robustness. Tile 5 (rows128:256, columns128:256, zero-based half-open) carries about45.40%/45.32% of integrated OFF intensity, but its maximum baseline-subtracted cut difference is0.000161175. Tile0 carries only0.717%/0.722% of OFF intensity and has a larger ratio difference0.001358918. Across tiles the maxima range0.000161175-0.001358918, versus0.000155508 for the whole detector. These are descriptive maxima over38 delays, not confidence bounds, causal leakage, or evidence that tile0 contains thermal physics.

NEXT_ACTION: Use source-backed geometric registration and a physically defined scattering observable rather than interpreting arbitrary tiles. Retain both cuts and check alignment sensitivity before constructing a covariance. No need to repeat fixed-grid tests without new evidence.

CLAIM_BOUNDARY: No significance test, measured covariance, TTG prediction, heat, temperature, alpha calibration or Full Topic13 closure. Low-intensity tiles may show larger ratios for denominator/noise reasons; this analysis does not resolve the cause. No holdout read or claim promotion.
