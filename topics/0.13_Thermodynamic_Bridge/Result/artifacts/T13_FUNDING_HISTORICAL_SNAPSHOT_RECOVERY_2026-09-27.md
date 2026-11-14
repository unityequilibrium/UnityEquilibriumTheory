# Topic 13 historical funding snapshot recovery

MAJOR_RESULT_CLOSURE: `PARTIAL` for `T13_FUNDING_HISTORICAL_SNAPSHOT_RECOVERY`. The historical bytes have been located, not admitted into a clean Core baseline.

WHAT_IS_ACTUALLY_CLOSED: All eight baseline files named in the funding plan exist in the dirty primary worktree and match its recorded SHA-256 values exactly. Two are tracked and clean, two tracked but modified, and four untracked. The earlier `0 MATCH / 4 DRIFT / 4 MISSING` classification remains correct **for this clean checkout**, not for the primary worktree.

WHAT_REMAINS_OPEN: Owner review and handoff of the modified/untracked records; upstream source-chain and content-role reconciliation; clean Core verifier rerun. Matching historical bytes alone cannot establish that the current relocated inputs and code have equivalent scientific meaning.

DEPENDENCY_UNLOCKED: None. Source discovery narrows G0's provenance question but does not pass G0 or Full Topic 13.

STATUS: `PASS_HISTORICAL_BYTE_RECOVERY_ONLY`; `G0=BLOCKED_LINEAGE_RECONCILIATION`.

WHAT_CHANGED: Added a Topic 13-only machine-readable read-only observation and a verifier that optionally rechecks the source worktree. No Core, primary-worktree, holdout or physical-model file was edited or copied.

EQUATION_OR_MAPPING: File identity is `relative path + SHA-256`. This is a provenance equality, not the `Phi -> Delta_Tq` map or a proof of independent predictive content.

VERIFICATION: The verifier matches all eight saved hashes to the plan and, with the source worktree supplied, rehashes all eight live files and checks their Git states. Its recorded source HEAD differs from the historical plan HEAD, so this is a present-day recovery observation, not a recreation of that exact Git revision. See [machine record](t13_funding_historical_snapshot_recovery.json) and [read-only verifier](../../Code/03_Research/Research_T13_Historical_Snapshot_Recovery.py).

CONTROLLING_BLOCKER: `full_clean_core_baseline_not_revalidated`. Specifically, four untracked and two modified owner records have not been admitted; some nested Core references also need source-chain review.

NEXT_ACTION: Ask the Core owner to decide which of the eight artifacts can be handed off and under what public-safety/source policy. Then reconcile nested provenance and rerun the scoped clean Core tests before evaluating G0; do not copy files solely to force hash agreement.

CLAIM_BOUNDARY: The eight files are recoverable, not independently reproduced or validated. This result does not authorize publication, open Xie 2026 for fitting, admit a two-fluid operator, or close the thermal bridge.
