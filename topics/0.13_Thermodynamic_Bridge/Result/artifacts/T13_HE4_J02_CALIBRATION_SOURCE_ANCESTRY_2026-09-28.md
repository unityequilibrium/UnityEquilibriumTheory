# He-4/J02 calibration source-ancestry boundary

MAJOR_RESULT_CLOSURE: `T13_HE4_J02_CALIBRATION_SOURCE_ANCESTRY_BOUNDARY` is `CLOSED_FOR_LANE` as a data-role classification only.

WHAT_IS_ACTUALLY_CLOSED: The current J02 Table 4.3 reference is a source-overlap comparator, not an independent He-II validation set. The direct J02 rows were not used to fit the local He-4 alpha, but the adopted superfluid-density reference used for that alpha partly comes from sound measurements in the same temperature window.

WHAT_REMAINS_OPEN: Exact cross-table row covariance, an independent non-sound calibration or separate response source, matched primary response protocol, and an admitted UET two-fluid operator.

DEPENDENCY_UNLOCKED: None. G0 and Full Topic 13 stay open.

STATUS: `PASS_METHOD_LEVEL_OVERLAP_SCREEN_ROW_COVARIANCE_OPEN`; no physical claim promotion.

WHAT_CHANGED: Corrected the J02 data role and narrowed the meaning of calibration independence. Core calibration constants and source package were not edited.

EQUATION_OR_MAPPING: `alpha_Phi_K = (rho_s/rho)|T0 / d_T(rho_s/rho)|T0` uses Section 2 superfluid-density rows at 1.6, 1.7 and 1.8 K. Section 2's adopted data include Maynard and Tam-Ahlers sound-derived measurements; Section 4's second-sound compilation contains overlapping study families. This is method-level ancestry overlap, not proof that the exact Table 4.3 values were reused.

VERIFICATION: Compared the local calibration/source packages against [Donnelly and Barenghi, Sections 2 and 4, Tables 2.1, 4.1 and 4.3](https://srd.nist.gov/jpcrdreprint/1.556028.pdf) and the [Maynard measurement-method abstract](https://link.aps.org/doi/10.1103/PhysRevB.14.3868). Local package hashes and the row-level uncertainty gap are recorded in [the machine audit](t13_he4_j02_calibration_source_ancestry_audit.json). No Xie 2026 data were read.

CONTROLLING_BLOCKER: `independent_non_sound_calibration_or_response_source_not_admitted` for an independent He-II test. This is separate from G0's clean Core baseline blocker.

NEXT_ACTION: Either find a permitted non-sound measurement of the calibration variable with rows, protocol, uncertainty and provenance, or designate J02 solely as a disclosed method-overlap comparator and source a genuinely independent response measurement. Do not call a different page of the same compilation an independent test without ancestry review.

CLAIM_BOUNDARY: This does not invalidate the numerical local alpha or its independence from graphite TTG/Xie fitting; it prevents treating J02 as blind/statistically independent He-II validation. It does not close G0, the two-fluid prediction, or Full Topic 13.
