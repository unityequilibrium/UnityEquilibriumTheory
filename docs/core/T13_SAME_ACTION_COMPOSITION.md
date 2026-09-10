# Same-action local thermodynamic composition

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE; local alpha, beta, EOS and corrected entropy evaluated with one explicit action configuration.
WHAT_IS_ACTUALLY_CLOSED: The configuration mismatch is removed for this new reference composition. Pressure, entropy density, energy density and charge density agree exactly between the relevant builders, which receive the same immutable config. The full config and its canonical JSON hash are recorded.
WHAT_REMAINS_OPEN: Frame/charge-diffusion mapping, transport convergence, material/protocol correspondence and historical Core integration review.
DEPENDENCY_UNLOCKED: Internal same-action reference only; no new physical/Core unlock.
STATUS: SAME_ACTION_REFERENCE_CONSISTENT.
WHAT_CHANGED: New common-configuration driver, tests and t13_same_action_composition_audit.json. Existing default entropy builder, action parameters, alpha calibration and all historical artifacts are unchanged.
EQUATION_OR_MAPPING: Existing alpha/beta derivatives and sigma=X.q/T on T=.22,mu=.35,Phi=.15 with natural_bridge_config(), response_coupling=.8,epsilon_nc=.05. No new equation, fit or parameter search.
VERIFICATION: Two configuration tests pass, rejecting default/different-coupling configurations and distinguishing quadrature controls. Shared-action pressure/entropy/energy/charge match; original entropy balance threshold1e-7 is met by5.15436e-8. Charge, energy, momentum, covariance and isotropy checks pass. This reference is not a continuum convergence study.
CONTROLLING_BLOCKER: hydrodynamic_frame_charge_diffusion_map and physical_state_and_protocol_correspondence.
NEXT_ACTION: Establish whether the projected heat source represents energy flux, charge diffusion or a frame-invariant combination, then build the corresponding entropy current consistently. Do not identify the moment response with an SI heat conductivity.
CLAIM_BOUNDARY: Natural same-action reference closure only; not full He4 physical validation, microscopic SK matching, full two-fluid transport or global UET closure. Historical composition is not automatically refreshed by this result.

## Measured change

Current default-config kappa is257.3728670227229; the shared-action value is254.8247192440348, a relative change of-0.99006%. The corrected shared-action entropy production is1158.2941783819765 for the declared unit thermal-force probe. Alpha and beta remain the current same-default-action values from the EOS revision audit. The kappa comparison changes the full configuration, including quadrature128 versus192 and cutoff60 versus70, so it is not an isolated measurement of coupling sensitivity. No real material uncertainty is inferred from it.

The new driver explicitly passes the same config into all three builders; the identity guard is not a general guarantee against undocumented configuration changes in other pipelines. Such callers still need their own provenance checks.
