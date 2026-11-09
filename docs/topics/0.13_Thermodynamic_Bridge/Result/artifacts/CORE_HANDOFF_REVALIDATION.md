# Core handoff revalidation from the Topic 13 room

MAJOR_RESULT_CLOSURE: PARTIAL; fresh focused tests and exact ADM provenance differences established.
WHAT_IS_ACTUALLY_CLOSED: The one failing focused test is an ADM artifact identity mismatch. Fresh ADM numeric results, checks, thresholds and claims equal the stored values; two source hashes differ. The old module hash is recovered exactly from Git and its complete AST matches the current module.
WHAT_REMAINS_OPEN: Reviewed provenance refresh, coupled matter conservation/evolution, non-periodic constraint-preserving boundaries and dimensional observable mapping.
DEPENDENCY_UNLOCKED: None; no new Core, GR or graphite acceptance.
STATUS: BLOCKED_HANDOFF_REVALIDATION, not a newly discovered numerical-physics failure.
WHAT_CHANGED: Added a Topic 13-owned read-only Core revalidation runner, three comparator tests and this handoff with machine-readable evidence. No Core artifact, threshold or equation was edited.
EQUATION_OR_MAPPING: Prescribed T_ab -> ADM projections -> trace-reversed GH RHS is an implemented interface, not a self-consistent evolved matter solution.
VERIFICATION: Seven focused Core modules rerun: 54 tests pass, one provenance test fails. Three audit-comparator tests pass. Parent has 11 stale hashes among 20 references. Fresh ADM payload comparison reports every difference except top-level generated_at. All hashed inputs remain unchanged during the runner.
CONTROLLING_BLOCKER: stale_core_provenance_and_prescribed_vs_conserved_matter_handoff.
NEXT_ACTION: Core owner reviews the exact source differences, refreshes evidence in dependency order, and explicitly dispositions the open matter-evolution/conservation requirements before accepting the full parent.
CLAIM_BOUNDARY: This does not recertify all Core physics, withdraw the bounded O(2)/He-4 acceptance, identify graphite alpha, or equate source wiring with matter evolution. Full_core_unlock=false.

## Evidence

- [Machine-readable result](core_handoff_revalidation.json), including complete focused test output, actual versus expected hashes, fresh ADM differences and a Git locator for the old module.
- [Runner](../../Code/03_Research/Research_Core_Handoff_Revalidation.py), which deliberately returns exit 1 while handoff revalidation is blocked.
- [Comparator tests](../../Code/03_Research/test_core_handoff_revalidation.py), including safeguards against ignoring hash, status, numeric, type or missing-field changes.

## What Changed Versus the Old Diagnosis

There are three distinct tracks, not one interchangeable Topic 13 status:

| Track | Recorded/current evidence | What this pass establishes |
| --- | --- | --- |
| O(2)/He-4 thermal bridge | Existing bounded CLOSED_FOR_CORE acceptance record | Its scope is preserved, not independently recertified by these 55 tests |
| Curved 3+1 Core parent | Periodic vacuum evolution and prescribed Topic 13 source interfaces | Fresh focused checks support these implementations within their test coverage; provenance refresh remains required |
| Graphite/TTG/UED material matching | Source/physical normalization and detector mapping still open | He-4 calibration cannot be transferred here silently; this pass does not test UED data |

Earlier per-stage GH gates describe their own limited implementation surfaces.
An older principal-system gate listing nonlinear evolution as open is not by
itself evidence that the later nonlinear/time-evolution module is absent.
Read the cumulative parent and its actual supporting evidence together.

## Exact Failure Boundary

The failing test is
`test_artifacts_are_stable_hash_linked_and_select_gh_without_claiming_it`.
The fresh ADM verification, no-go and formula artifacts each differ from their
stored counterparts only at two source-hash fields: the ADM module and its
audit generator. The formulation-selection artifact matches exactly after
removing only generated_at. No metric or threshold is suppressed in this
comparison, and provenance mismatches remain failures.

The stored ADM module hash matches the file before migration commit
`1fd96a48ed977a473688ae8301e6e6768b14c712`. The complete parsed AST of that
historical module and the current module is identical, including imports.
This supports a non-equation-text migration discrepancy for this module; it
is not proof of equivalence of all dependencies or an authorization to accept
new source hashes without review. The generator's old/new source diff and
all 11 parent-link mismatches remain in the Core owner's refresh scope.

## Physical Work Hidden by a Short Summary

The current matter contract explicitly leaves these unimplemented:

- Matter-state time evolution.
- Stress-energy conservation propagation.
- Self-consistent two-fluid curved transport.
- Numerical SI Einstein-coupling provenance.

The parent requirement map does not list these four as explicit keys. It does
list open boundary and dimensional-observable requirements. This is a handoff
coverage concern, not proof that the four items must all be owned by exactly
one future gate: Core should either add explicit acceptance requirements or
document which downstream contract owns each one. A prescribed T_ab input
must not be interpreted as already satisfying conservation during evolution.

## Core Owner Repair Order

1. Review the recorded old/new ADM source hashes and generator changes; preserve the fixed-gauge no-go and every physical threshold.
2. Regenerate the ADM evidence family through its existing generator, then refresh cumulative parent hashes in dependency order. Follow the migration policy for semantic-hash review; do not suppress non-timestamp differences or hand-edit hashes to green.
3. Rerun the same seven test modules and parent evidence-link verification; preserve the original failure in this handoff history.
4. Make the physical handoff requirements explicit, distinguishing prescribed source, conserved matter evolution, boundary conditions and a detector/observable map.

No Core files were changed in this pass because this room is validating a
handoff, not taking over another room's equation or migration controls.
