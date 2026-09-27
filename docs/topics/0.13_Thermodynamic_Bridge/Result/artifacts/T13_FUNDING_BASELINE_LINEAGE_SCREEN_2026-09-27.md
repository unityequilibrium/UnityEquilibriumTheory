# Topic 13 funding baseline lineage screen

MAJOR_RESULT_CLOSURE: `PARTIAL` for `T13_FUNDING_CLEAN_BASELINE_LINEAGE_SCREEN`; this is a reproducibility screen, not G0 completion or physical closure.

WHAT_IS_ACTUALLY_CLOSED: On the clean `codex/research/t13-funding-evidence` checkout, all five saved pre-sprint Topic 13 artifacts match their declared hashes, and the separate partial compressibility source-route manifest matches. The eight older baseline references in the funding plan are classified individually: zero match this checkout, four have different content hashes, and four are absent.

WHAT_REMAINS_OPEN: Select and verify clean equivalents for the older Core inputs, explain each replacement/missing record, bring in the referenced J02 protocol only after dependency review, and rerun the relevant Core/source/holdout-exposure audits. The clean checkout currently lacks `HE4_SECOND_SOUND_PROTOCOL_CARD.md`.

DEPENDENCY_UNLOCKED: None. The five reproduced subresults can be reviewed independently, but G0 remains open.

STATUS: `PASS_IDENTITY_SCREEN_WITH_OPEN_G0`; G0 = `BLOCKED_LINEAGE_RECONCILIATION`.

WHAT_CHANGED: Added a deterministic script, three tests and a hash-backed JSON that compare the historical dirty-branch snapshot with current files without treating historical hashes as the required content of a new clean baseline. No Core files or scientific thresholds were changed.

EQUATION_OR_MAPPING: Input identity is `path + SHA-256`; neither hash agreement nor a local test pass is a physical mapping. The selected clean equivalent must be reviewed by content, data role and dependencies, not made to equal an old dirty-worktree hash.

VERIFICATION: The current checkout has `MATCH=0`, `DRIFT=4`, `MISSING=4` for the eight historical references; five pre-sprint artifacts and the source-route record match. Three focused lineage tests pass. Audit SHA-256: `6053a6e0dece7abca08cc0713db66de8914ea83f07bebbb8f89eb1006cc6c85c`. This identity screen cannot open G0; a separate hash-backed clean Core baseline verifier and J02 dependency review are required.

CONTROLLING_BLOCKER: `full_clean_core_baseline_not_revalidated`; the missing J02 protocol and the historical-to-clean equivalence decisions are named subblockers.

NEXT_ACTION: Build a selected clean-baseline manifest for the Core composition, matching, SI-`Phi`, source, curved-3+1 and holdout-exposure records, with one explicit decision for each historical reference. Review J02's source commit before importing anything. Only rerun G0 when those prerequisites are present; do not promote the five pre-sprint results to G0.

CLAIM_BOUNDARY: This audit does not revalidate Core, reopen the holdout, admit the Noether-to-atom map, close Full Topic 13 or make the funding portfolio submission-ready.

Evidence: [machine-readable audit](t13_funding_baseline_lineage_audit.json), [verifier](../../Code/03_Research/Research_T13_Funding_Baseline_Lineage.py), [tests](../../Code/03_Research/test_t13_funding_baseline_lineage.py).
