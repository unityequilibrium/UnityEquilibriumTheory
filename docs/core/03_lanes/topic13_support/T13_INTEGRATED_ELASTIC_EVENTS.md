# Integrating the existing action-normalized elastic branch

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Independent double-radial integration now uses the existing charge-resolved tree amplitude, full outgoing angular measure and Bose factors. Incoming tag exchange and charge conjugation are checked.
WHAT_REMAINS_OPEN: Cutoff/joint-resolution error, linearized gain-loss response, invariant projection, full transport and material calibration.
DEPENDENCY_UNLOCKED: None.
STATUS: INTEGRATED_ELASTIC_EVENT_DIAGNOSTIC_NOT_TRANSPORT.
WHAT_CHANGED: New integration wrapper, two tests and hashed result. Existing amplitude and legacy finite channels unchanged.
EQUATION_OR_MAPPING: R_event=1/2 sum_q integral d^3k/(2*pi)^3 f_q(k) Gamma_q(k). Units natural energy^4; two incoming tags per event account for1/2. The final-state identical-particle factor is already inside the differential cross section and is not inserted again.
VERIFICATION: Existing scattering tests17 PASS; new integration tests2 PASS. Radial8/16/24 at fixed angular8 and cutoff12 produce3.4475064e-11,3.6033709e-11,3.6017504e-11. Angular12 at radial24 gives3.6016039e-11. Last radial change0.04497%; angular change0.004066%. Incoming exchange discrepancies below7.3e-16; detailed balance below2.2e-14. Artifact hashes match; foundation audit PASS with physical gate BLOCKED.
CONTROLLING_BLOCKER: linearized_collision_gain_loss_and_conserved_projection_with_resolution_control.
NEXT_ACTION: Connect charge-resolved collision amplitudes to the quadratic gain-loss form on independent nodes; validate invariant null modes and rate-weighted probe forms before solving any transport inverse. Check cutoff and independent angular refinements.
CLAIM_BOUNDARY: Synthetic normal-background nonresonant tree elastic calculation. Event density is not a relaxation rate, transport eigenvalue, microscopic SK match or SI conductivity. No holdout access, fitting, threshold change or Full Topic13 promotion.

## Recovered existing evidence, not a new derivation

The previous measure pilot named differential cross-section and species conventions as its next blocker. Inspection recovered `audit_topic13_action_normalized_elastic_scattering.py` and its existing registry ID `uet.o2.thermal.normal_tree_elastic_scattering`. Its tests pass against the current sources. Thus this convention need not be derived again for this named branch; integration and response construction remain open.

In the contact-only limit that branch gives amplitude4*lambda_c and total cross sections8 times the unit comparator for like charges,16 times for unlike charges. Phi exchange introduces angular and channel dependence, so a single rescaling of legacy rates is not the repair. This runner reuses the full differential cross section through tagged_loss_rates, not a fitted multiplier.

The previous dimensionless product-measure pilot is a separate analytic control. This wrapper reuses the existing physical natural-unit measure in the tagged-loss implementation and integrates the independent tag leg. It does not claim to have installed the earlier pilot in production. Only scalar equilibrium event density is computed; no fixed-orientation tensor is inferred.

Evidence: artifacts/t13_integrated_elastic_events_audit.json. Historical scattering artifact is retained without regeneration; current tests, not historical hashes, support this fresh integration.
