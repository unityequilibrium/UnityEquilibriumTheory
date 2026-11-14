# UED numeric export and spatial-support sensitivity

MAJOR_RESULT_CLOSURE: PARTIAL; lossless image export and whole-detector support comparison completed.

WHAT_IS_ACTUALLY_CLOSED: All 70 ON/OFF image pairs exported to non-executable numeric arrays. Source row identities and missing pixels are preserved. Common and per-frame finite masks are available separately for each scan.

WHAT_REMAINS_OPEN: Region-specific scattering inversion, preprocessing covariance, unseen modes, physical timing uncertainty, relaxation dynamics and independent Phi coupling.

DEPENDENCY_UNLOCKED: Mask-aware detector analysis only; no physical downstream unlock.

STATUS: EXPORTED_WITH_SUPPORT_DEPENDENCE_DISCLOSED; full_core_unlock=false.

WHAT_CHANGED: Added optional read-only numeric sink to the inert parser, export/support audit and three tests. Regenerated the inventory to match its parser hash. Raw arrays remain ignored local-only.

EQUATION_OR_MAPPING: R(t)=sum_ON(mask)/sum_OFF(mask), followed by subtraction of the mean at delay < -0.5 ps. Compare pairwise finite support against the intersection across all frames within each scan. This custom whole-detector diagnostic is not a reproduction of the author's complete estimator.

VERIFICATION: Twelve linked tests pass, including a synthetic example where changing support alone creates a false signal. Both actual archive members decode with unchanged row hashes. A second export pass checks existing arrays against source bytes, including NaNs. No missing values are filled.

CONTROLLING_BLOCKER: region_specific_scattering_map_and_preprocessing_covariance_missing.

NEXT_ACTION: Define source-backed reciprocal-space regions and forward scattering weights before population inversion. Quantify support effects within those regions and account for correlations from symmetry averaging. Do not infer rates or temperature from the whole-detector ratio.

CLAIM_BOUNDARY: No physical alpha, TTG validation, lifetime or Full Topic 13 promotion. No holdout is an input. Separate He-4 status and closure gates are unchanged.

## Actual support comparison

| Scan | Common pixels | Per-frame paired pixels | Maximum baseline-subtracted ratio difference |
| --- | ---: | ---: | ---: |
| 400 nm | 255379 | 255514-256294 | 8.2056868e-7 |
| 800 nm | 255530 | 255617-256307 | 9.0138554e-6 |

Differences are dimensionless absolute ratio differences, approximately 0.821
and 9.014 parts per million. They are not confidence intervals or percentages of
the physical signal. No acceptance threshold was applied; the unrelated causal
leakage threshold must not be used here. Whole-detector sums include Bragg peaks
and can hide larger local differences. A common mask can itself discard relevant
regions and does not undo the source's intensity-dependent preprocessing.
Both mask rules were specified before this run, without choosing the more
desirable curve. They describe this retrospective dataset, not a deployable
future-data selection rule.

Evidence: `artifacts/t13_ued_mask_support_audit.json`, with source-chain hashes,
per-row identities, exported-array hashes, masks and complete diagnostic curves.
This note supersedes only the earlier inventory note's pending full-image export.
