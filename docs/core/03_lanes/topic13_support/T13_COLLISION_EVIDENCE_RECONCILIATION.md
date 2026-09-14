# Collision evidence reconciliation, 2026-09-12

MAJOR_RESULT_CLOSURE: PARTIAL; existing coupled gain-loss evidence recovered and checked for current-source reuse.
WHAT_IS_ACTUALLY_CLOSED: The repository already contains scalar and coupled gain-loss constructions; current regression tests53 PASS. All declared hashes of the coupled artifact match. Its recorded finite-grid refinement gate is true. Starting gain-loss from scratch is not the next task.
WHAT_REMAINS_OPEN: Basis completeness, physical collision-current matching, higher-order/number-changing channels, finite-temperature self-energy/background, full SK/KMS/entropy/material matching.
DEPENDENCY_UNLOCKED: No new physical dependency.
STATUS: EXISTING_GAIN_LOSS_EVIDENCE_REVALIDATED_NOT_FULL_TRANSPORT.
WHAT_CHANGED: Read-only reconciliation runner/artifact and this correction of the preceding next-action wording. No production equations, historical artifacts or thresholds changed.
EQUATION_OR_MAPPING: Existing coupled lane uses delta f=f(1+f)psi and Delta psi=psi1+psi2-psi3-psi4, with reaction-resolved positive quadratic forms and metric momentum projection. This is not a new derivation.
VERIFICATION:53 existing tests PASS, covering scalar invariants, coupled gain-loss derivative, charge conjugation, reaction counting, positivity and finite-basis response. Coupled and integrated-event reference hashes match; scalar artifact has historical drift in uet_o2_continuum_collision_operator.py. Archived coupled radial/angular/azimuth/cutoff changes are1.033e-4/8.914e-7/5.089e-7/3.420e-4; largest-basis quadrature change5.383e-5, below its existing2e-3 diagnostic threshold. These full refinement runs were not repeated today.
CONTROLLING_BLOCKER: basis_completeness_and_physical_collision_current_matching.
NEXT_ACTION: Inspect existing vector/current and material handoffs before choosing a basis extension or missing physical match. Reuse this coupled branch; do not reimplement its scalar/vector gain-loss or treat event counts as conductivity.
CLAIM_BOUNDARY: Finite tree-quasiparticle basis and numerical convergence are not continuum completeness or Full Topic13 closure. Current regression success does not make the historical scalar full artifact fresh.

## Correction to the preceding wave

T13_INTEGRATED_ELASTIC_EVENTS.md said to build a gain-loss form next. That was an incomplete inventory, not evidence that gain-loss was absent. The event-count integration remains a valid separate control, but it should not replace the more advanced existing coupled operator. The active controller is now the one above.

The largest early nested-basis relative increase in the archived coupled result is12.7529 (not percent); later increases shrink to1.770e-4 and1.519e-5. This is evidence that a small basis can miss an important mode, not a proof that later small changes certify completeness. Any extension must target missing physical modes or matching conditions rather than merely generate another passing counter.

Evidence: artifacts/t13_collision_evidence_reconciliation.json and the referenced immutable hashes. No external data or holdout read in this pass.
