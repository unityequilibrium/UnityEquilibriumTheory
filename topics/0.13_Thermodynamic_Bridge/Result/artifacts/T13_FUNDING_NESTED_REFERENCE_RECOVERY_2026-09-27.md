# Topic 13 nested composition-reference recovery

MAJOR_RESULT_CLOSURE: `PARTIAL` for `T13_FUNDING_NESTED_REFERENCE_RECOVERY`; this recovers a historical reference graph, not the Core composition result.

WHAT_IS_ACTUALLY_CLOSED: All 12 old `docs/core/artifacts/` paths embedded in the He-4 composition are absent in both worktrees, but a unique relocated candidate exists for each. Eight relocated source-worktree files match the recorded SHA-256 exactly; four do not. Source and clean statuses match the composition record for all 12. Comparing relocated source with clean candidates, nine parsed JSON payloads are identical and three have field differences.

WHAT_REMAINS_OPEN: For the four historical-hash drifts, the originally recorded bytes were not recovered at the old paths; parsed-JSON equality of current relocated candidates does not prove what those old bytes contained. For the three field deltas, Core must review nested reference paths/hashes and one change in `/major_result/evidence_artifacts/1/summary/closure_level` of the causal compatibility artifact. The remaining upstream sources and Core verifier still need revalidation.

DEPENDENCY_UNLOCKED: None. G0 remains blocked.

STATUS: `PASS_NESTED_REFERENCE_RECOVERY_ONLY`.

WHAT_CHANGED: Added a read-only 12-reference verifier, machine record and focused tests in Topic 13. No Core, source-worktree or holdout experimental file was changed or copied.

EQUATION_OR_MAPPING: For each old composition reference, compare recorded path/hash/status to the unique relocated source and clean artifacts. This is provenance mapping, not `Phi -> Delta_Tq` or physical equivalence.

VERIFICATION: The saved [12-row record](t13_funding_nested_reference_recovery.json) matches live relocated bytes and parsed fields; the [verifier](../../Code/03_Research/Research_T13_Nested_Reference_Recovery.py) reports `8` historical-hash matches, `4` drifts, `9` source/clean parsed-JSON equalities and `3` field deltas. The causal summary's `closure_level` is absent in the recovered source and `CLOSED_FOR_LANE` in clean; the outer status is unchanged. The no-go and flat-component deltas are generated-time and evidence-path/hash fields. This is a field inventory, not a proof those referenced files are valid.

CONTROLLING_BLOCKER: `nested_core_reference_source_chain_not_revalidated`, alongside the separate owner-admission blocker for the four missing top-level funding inputs.

NEXT_ACTION: Have Core review the causal nested-summary addition and provenance substitutions in the three changed candidates, then rerun the affected Core verifiers on the selected clean inputs. Preserve the four unmatched historical hashes as unresolved until old bytes or a documented clean-equivalence decision exists.

CLAIM_BOUNDARY: Matching status or relocated bytes does not close Core, G0, He-II prediction or Full Topic 13. Xie 2026 experimental rows were not used, and holdout-access metadata does not certify blind validation after prior exposure.
