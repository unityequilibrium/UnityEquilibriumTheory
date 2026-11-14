# Local EOS revision impact

MAJOR_RESULT_CLOSURE: PARTIAL; historical-to-current local alpha/beta differences measured without rematching.

WHAT_IS_ACTUALLY_CLOSED: At the existing normal reference T=.22, mu=.35, Phi=.15, quadrature128, current default builders retain the same branch. Natural alpha changes from .00231385784478 to .00231385492883 (relative1.26021e-6). Natural beta changes from -2.42719816414e-6 to -2.42725979290e-6 (relative2.53909e-5). These two comparisons do not show a large reference-value shift. Refined beta changes relatively1.83146e-4; derivative error diagnostics must not be confused with physical uncertainty.

WHAT_REMAINS_OPEN: Physical perturbation protocol correspondence; full dependent EOS/entropy/two-fluid/SK/causal evidence review. This is not a complete historical runtime reproduction: current implementations are compared with frozen recorded outputs.

DEPENDENCY_UNLOCKED: None. Historical He-4 composition is not rewritten or promoted.

STATUS: REVISION_IMPACT_MEASURED_NOT_FULL_COMPOSITION_REVALIDATED.

WHAT_CHANGED: New audit, tests and t13_eos_revision_impact_audit.json. Existing historical artifacts, field scales, calibration and gate values are preserved.

EQUATION_OR_MAPPING: Existing alpha=(partial_Phi epsilon)/(partial_T epsilon) at fixed declared variables; beta=T partial_T(partial_Phi^2(-p)). No new equation or physical mapping.

VERIFICATION: Two unit tests and two current default-state evaluations. Declared recursive Core path/hash edges:61 MATCH,9 STALE,0 MISSING,30 EXCLUDED_NOT_READ. Counts are edges, not independent scientific results. Traversal reads current JSON descendants even when a historical hash differs, and cannot reconstruct that older graph. Unlisted imports and excluded external sources are outside coverage. No holdout payload or excluded file read; prior incidental context exposure remains disclosed separately.

CONTROLLING_BLOCKER: Nine stale edges include three references to EOS code, one to transverse-response code, and five to downstream artifacts. Hash mismatch alone is not a numerical or physical contradiction. Direct composition hashes alone are insufficient to certify recursive currency.

NEXT_ACTION: Evaluate the current covariant entropy/heat-flux reference with unchanged settings and trace the two-fluid transverse-response revision. Review SK and causal descendants separately. Keep all old values visible; do not merely replace hashes to make a gate green.

CLAIM_BOUNDARY: Local normal-reference numerical comparison only, not an SI calibration, independent He-4 prediction, complete finite-temperature branch sweep, or global closure. Alpha protocol dependence remains unresolved even though these revision differences are small.
