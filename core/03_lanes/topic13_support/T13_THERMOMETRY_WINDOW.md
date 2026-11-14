# Late-time thermometry does not transfer to the acquired window

MAJOR_RESULT_CLOSURE: PARTIAL; this proposed source-to-data calibration justification is rejected, not thermometry in general.

WHAT_IS_ACTUALLY_CLOSED: The acquired 400/800 nm records end at 42.26244/8.93244 ps. Neither has rows in the reviewed source's >100 ps quasi-equilibrium window. No time shift or invented late rows can repair that mismatch.

WHAT_REMAINS_OPEN: Same-sample equilibrium evidence and independent calibration rows, numerical uncertainty, preparation and Phi coupling.

DEPENDENCY_UNLOCKED: None physically; redirects source acquisition away from unsupported transfer.

STATUS: NO_OVERLAP_NO_CALIBRATION_TRANSFER.

WHAT_CHANGED: Added source-window audit, two tests and artifact. Targeted title/dataset searches did not locate a matched numeric calibration package in this pass; that is not proof no package exists.

EQUATION_OR_MAPPING: Compare actual delays to one source-specific condition. The condition is not a universal equilibration time or a new causal threshold.

VERIFICATION: Two tests pass; actual numeric-inventory evidence hashes verified. Zero eligible rows in both scans. Primary arXiv full text and SI 5 inspected; publisher access returned 403 and PMC returned a browser challenge. Neither restriction was bypassed.

CONTROLLING_BLOCKER: same_preparation_equilibrium_evidence_and_independent_calibration_rows.

NEXT_ACTION: Use a same-preparation calibration or source-backed nonequilibrium response. If neither is available, retain model comparison and pursue independent Phi coupling in parallel. Do not keep searching this paper as if its reported temperatures were ready-made calibration data.

CLAIM_BOUNDARY: Does not prove the acquired samples fail to equilibrate; it shows that this other experiment's timing assumption cannot justify their thermometry. No holdout, fit, physical alpha or full-topic promotion.

## Source audit

The reviewed [Feist source, SI 5](https://arxiv.org/pdf/1709.02805) infers temperature
through a Debye model and thermalized-population assumption. Its pump-energy
cross-check depends on material constants and an uncertain initial temperature.
These are useful physical constraints, but not an independent calibration table
for our experiment. Quoted temperatures must retain their model origin.

The source search surfaced article supplements, not verified per-row calibration
data with covariance. No numeric data were digitized from plots. The previously
noted timing-unit discrepancy remains unresolved because the final publisher
version could not be inspected in this pass.

This narrows the earlier source-route note: the capability remains relevant for
future matched measurements, but it cannot calibrate the currently acquired UED
window by direct transfer. Evidence: `artifacts/t13_thermometry_window_audit.json`.
