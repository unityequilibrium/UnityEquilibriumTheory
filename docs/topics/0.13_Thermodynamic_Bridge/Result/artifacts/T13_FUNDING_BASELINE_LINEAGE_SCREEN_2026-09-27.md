# Topic 13 funding baseline lineage screen

MAJOR_RESULT_CLOSURE: `PARTIAL` for `T13_FUNDING_CLEAN_BASELINE_LINEAGE_SCREEN`; this is a reproducibility screen, not G0 completion or physical closure.

WHAT_IS_ACTUALLY_CLOSED: On the clean `codex/research/t13-funding-evidence` checkout, all five saved pre-sprint Topic 13 artifacts match their declared hashes, and the separate partial compressibility source-route manifest matches. The eight older baseline references in the funding plan remain classified as zero matches, four content drifts and four missing at their historical paths. The J02 source package and protocol card are now present and reviewed as a nonblind source/protocol candidate, not a prediction.

WHAT_REMAINS_OPEN: Select and verify clean equivalents for the older Core inputs, explain each replacement/missing record and rerun the relevant Core/source/holdout-exposure audits. J02 still lacks a primary frequency/geometry/row-uncertainty match and an admitted UET two-fluid operator.

DEPENDENCY_UNLOCKED: None. The five reproduced subresults can be reviewed independently, but G0 remains open.

STATUS: `PASS_IDENTITY_SCREEN_WITH_OPEN_G0`; G0 = `BLOCKED_LINEAGE_RECONCILIATION`.

WHAT_CHANGED: Imported a reviewed Topic 13-only J02 protocol/source package from commit `c42385d07` and extended the deterministic lineage script, tests and JSON to check its nonblind role and frozen constants against current Core artifacts. No Topic 10 or Core file or scientific threshold was changed.

EQUATION_OR_MAPPING: Input identity is `path + SHA-256`; neither hash agreement nor a local test pass is a physical mapping. The selected clean equivalent must be reviewed by content, data role and dependencies, not made to equal an old dirty-worktree hash.

VERIFICATION: Historical references remain `MATCH=0`, `DRIFT=4`, `MISSING=4`; five pre-sprint artifacts and the source-route record match. J02's four Table 4.3 recommended rows, null row uncertainty, nonblind policy and frozen He-4 calibration/SI/shear constants pass the source-protocol review. The [NIST Table 4.3](https://srd.nist.gov/jpcrdreprint/1.556028.pdf) rows and [Lane et al. abstract](https://journals.aps.org/pr/abstract/10.1103/PhysRev.71.600) were inspected on 27 September 2026; the latter is not state-matched. Three lineage tests and eight related Core calibration/SI/shear/matching tests pass. Audit SHA-256: `6f9b1c31ff4e86157b3709c9bec678757a16697d2bcf47a1b4df3f6bcda73ee0`. The source package SHA-256 is `f32e6244fcc110de62bf99b9421ea24c9783ce2f448081aefc869dcccadade07`.

CONTROLLING_BLOCKER: `full_clean_core_baseline_not_revalidated`; J02 file absence is no longer a blocker, but historical-to-clean Core equivalence and physical protocol/operator remain open.

NEXT_ACTION: Build a selected clean-baseline manifest for the Core composition, matching, SI-`Phi`, source, curved-3+1 and holdout-exposure records, with one explicit decision for each historical reference. Only rerun G0 when those prerequisites are present; do not promote the five pre-sprint results or J02 protocol to G0.

CLAIM_BOUNDARY: This audit does not revalidate Core, reopen the holdout, admit a two-fluid operator or Noether-to-atom map, close Full Topic 13 or make the funding portfolio submission-ready. J02 rows were seen and cannot be called blind validation.

Evidence: [machine-readable audit](t13_funding_baseline_lineage_audit.json), [verifier](../../Code/03_Research/Research_T13_Funding_Baseline_Lineage.py), [tests](../../Code/03_Research/test_t13_funding_baseline_lineage.py), [J02 protocol](../../HE4_SECOND_SOUND_PROTOCOL_CARD.md), and [J02 source package](../../Data/03_Research/he4_svp_second_sound_response_source_package.json).

Subsequent read-only observation: [historical snapshot recovery](T13_FUNDING_HISTORICAL_SNAPSHOT_RECOVERY_2026-09-27.md) located all eight exact plan bytes in the dirty primary worktree. The clean-checkout counts above remain unchanged; G0 still requires owner handoff and revalidation.

28 September addendum: The J02 package was reclassified after a [source-ancestry audit](T13_HE4_J02_CALIBRATION_SOURCE_ANCESTRY_2026-09-28.md). It is a source-overlap comparator, not an independent He-II test. The earlier SHA-256 values above remain a dated snapshot; the current generated lineage audit is `91ca07ee8dbfa0edaf4ee1abce103499c6d5a1a69611973112cc2065a504ee86`. G0 remains blocked.
