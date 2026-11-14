# He-4 Core composition reference-lineage screen

MAJOR_RESULT_CLOSURE: `T13_HE4_COMPOSITION_REFERENCE_LINEAGE_SCREEN` is `PARTIAL`. It classifies one Core baseline dependency graph, not the physical bridge.

WHAT_IS_ACTUALLY_CLOSED: All 12 references embedded in the current bounded He-4 Core composition artifact were located and classified in this clean checkout. Each old `docs/core/artifacts/` path is absent; exactly one same-basename candidate exists under `docs/core/07_artifacts/` for each. All 12 candidates retain the recorded top-level status. Against the *committed* baseline `a62efba425f1b219241cf149bc4bab50cce4c379`, nine current candidate files are byte-identical and three have field-level differences recorded in JSON.

WHAT_REMAINS_OPEN: All 12 current files have hashes different from the hashes embedded in the composition artifact. The nine byte-identical comparisons are to the committed tree, **not** the historically dirty working tree whose hashes entered the funding plan. The three changed files update timestamps and upstream path/hash references; one causal-branch evidence summary also changes `closure_level` from null to `CLOSED_FOR_LANE`. No equivalence to the dirty snapshot, recursive source provenance, or clean Core baseline reproduction was established. The separate J02 protocol is still absent from this checkout.

DEPENDENCY_UNLOCKED: None. G0 remains `BLOCKED_LINEAGE_RECONCILIATION`; the five pre-sprint Topic 13 results are not promoted.

STATUS: `REFERENCE_DRIFT_CLASSIFIED_NOT_REVALIDATED` with `12 RELOCATED_HASH_DRIFT`, `0 EXACT`, `0 MISSING`, `0 AMBIGUOUS`.

WHAT_CHANGED: Added a read-only composition-reference verifier, three regression tests, and a machine-readable evidence record. No Core files or scientific gates were edited.

EQUATION_OR_MAPPING: Reference identity is path plus SHA-256. A matching `status` string is only a triage signal; it is not a proof that the equations, source rows, assumptions, or uncertainties are unchanged.

VERIFICATION: Four lineage tests pass; five related clean-checkout Core test modules give 14 passes. The Core composition test checks saved status/check flags and claim wording, not its twelve cited path/hash pairs. The committed-tree comparison found `9 BYTE_IDENTICAL_TO_COMMIT / 3 CHANGED_SINCE_COMMIT / 0 unavailable`. Artifact SHA-256: `a23978b888dcbb49f9979a6b14d296bf9996965a2cbb10fd5b5e4adcd284fc95`.

CONTROLLING_BLOCKER: `clean_equivalence_and_upstream_provenance_not_revalidated`. The committed-tree field deltas narrow the likely migration effects, but cannot reconstruct the dirty snapshot or authorize replacing the recorded hashes.

NEXT_ACTION: For each relocated file, compare the prior and current payloads and producer/input provenance; select a new clean evidence chain only after its source rows, assumptions, units, uncertainty, and claim boundary are checked. Then rerun the independent Core verifier and review J02 before evaluating G0.

CLAIM_BOUNDARY: The Core artifact records a `CLOSED_FOR_CORE` **internal lane-bounded composition** and explicitly disclaims independent He-4 coefficient prediction, graphite TTG validation, a complete two-fluid tensor, curved 3+1, and global UET closure. This lineage screen neither retracts nor revalidates that physical claim. No Xie 2026 data was read.

Evidence: [machine-readable audit](t13_he4_composition_reference_lineage.json), [verifier](../../Code/03_Research/Research_T13_He4_Composition_Reference_Lineage.py), [tests](../../Code/03_Research/test_t13_he4_composition_reference_lineage.py).
