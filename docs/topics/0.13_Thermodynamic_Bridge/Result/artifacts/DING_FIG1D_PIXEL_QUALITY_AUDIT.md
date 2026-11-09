# Ding 2022 Fig. 1d pixel-quality audit

MAJOR_RESULT_CLOSURE: `PARTIAL`; the existing extraction was replayed, and a localized blue-trace pixel-mask ambiguity was identified.

WHAT_IS_ACTUALLY_CLOSED: The stored 432-row CSV reproduces from the archived figure and declared median-per-column extractor. Red and green traces have no gross adjacent jumps under the declared diagnostic triage rule. The blue trace has gross jumps and competing mask components near pixel columns 562-595 (about 760-897 ps).

WHAT_REMAINS_OPEN: This audit does not identify the physical cause of the blue pixels or repair the digitization. The affected segment is not qualified for dip-time, derivative, or velocity inference. Figure-pixel uncertainty is not experimental uncertainty; raw author numeric data, graphite Phi normalization, independent `alpha_Phi_K`, and physical transport remain open.

DEPENDENCY_UNLOCKED: A localized exclusion boundary for derivative-like use of the affected blue segment only. No alpha, prediction, Core, or Full Topic 13 dependency is unlocked.

STATUS: `PASS_SOURCE_IDENTITY_AND_REPLAY_WITH_LOCALIZED_PIXEL_MASK_WARNING`; the normalized-source lane remains at its prior scope.

WHAT_CHANGED: Added a read-only replay/quality auditor, focused regression tests, and `ding_2022_fig1d_pixel_quality_audit.json`. The CSV, source package, Core gates, and equations were not changed.

EQUATION_OR_MAPPING: `y=1-(pixel_y-top)/(bottom-top)*1.2`; the extractor uses the median selected color-mask y pixel in each x column. The stored pixel uncertainty half-width is `0.0114286` normalized units; a 10x two-row uncertainty bound is used only to flag gross discontinuities, not as a scientific acceptance threshold.

VERIFICATION: Source PNG/CSV hashes and all 432 digitized rows replay exactly. The blue trace contains 10 adjacent jumps over the diagnostic threshold; the largest is `0.942857` normalized units, or `41.25x` the two-row uncertainty bound. The source CSV is unchanged, and Xie 2026 was not accessed.

CONTROLLING_BLOCKER: `localized_blue_trace_pixel_mask_components_unresolved_for_dynamic_observables`.

NEXT_ACTION: Inspect the source figure at the flagged pixel columns and compare with an independent/manual digitization or author-supplied numeric trace before any blue-trace dip/velocity inference. Do not smooth, interpolate, or silently replace rows.

CLAIM_BOUNDARY: Digitization quality only; no physical discontinuity, UET validation, dimensional temperature map, alpha calibration, or Full Topic 13 closure is claimed.
