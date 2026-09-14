# Entropy force normalization counterexample

MAJOR_RESULT_CLOSURE: PARTIAL; a concrete interpretation defect is isolated, not thermodynamic closure.

WHAT_IS_ACTUALLY_CLOSED: The declared heat-force, entropy-current and production formulas cannot all represent physical heat-only entropy balance as written. With X=-grad(T)/T, q=K X and Js=s u+q/T, local energy balance gives sigma=X.q/T, not X.q. At T=.22, the existing reported value is .22 times the independently calculated divergence. T=1 masks the defect; T=.5 and2 expose it too.

WHAT_REMAINS_OPEN: Consistent collision-source/force normalization, hydrodynamic frame and charge-diffusion identification, and action-configuration correspondence. No claim that fixing one factor completes physical thermal transport.

DEPENDENCY_UNLOCKED: None. Physical entropy interpretation requires repair before renewed composition acceptance; historical evidence remains frozen, not silently overwritten.

STATUS: BLOCKED_PHYSICAL_ENTROPY_INTERPRETATION.

WHAT_CHANGED: Added independent convention audit, counterexample tests and t13_entropy_force_convention_audit.json. No production core equation, calibration, threshold or historical gate changed.

EQUATION_OR_MAPPING: At rest, with no work or charge diffusion, T*partial_t s=-partial_x q. The product rule gives partial_t s+partial_x(q/T)=-q*partial_x T/T^2. The reported X.q is temperature-weighted dissipation under the declared X convention. Natural units k_B=1 do not set variable T to1.

VERIFICATION: Four manufactured temperatures and three centered-difference resolutions reproduce the entropy-current derivative; error falls by about4 under halving the step. Seven tests passed: four establish the counterexample and three unchanged legacy tests still pass. Thus legacy positivity, covariance and kinetic quadratic-form agreement are not independent checks of physical entropy-current divergence. Current reference kappa differs relatively2.09372e-10 from historical, so small EOS drift does not explain away the convention problem.

CONTROLLING_BLOCKER: thermal_force_flux_entropy_normalization. A separate frame issue remains: the finite moment current with an enthalpy subtraction is not automatically an energy flux in a fully specified Landau-frame entropy current. Also, the entropy builder uses default EOS parameters, whereas alpha/beta use action_thermal_stiffness_config. Matching T,mu,Phi alone is insufficient evidence of matching actions.

NEXT_ACTION: Derive the collision driving term with one declared entropy-conjugate force and current/frame convention. Either keep X and explicitly distinguish X.q from sigma, or use Y=X/T and consistently transform response/source normalization. Do not divide one output by T while leaving the kinetic matching assertion unchanged. Then rerun independent energy/entropy divergence tests, reference calculation and downstream composition review.

CLAIM_BOUNDARY: This is an internal counterexample to a physical interpretation, not negative entropy, invalidation of matrix positivity, or proof against UET globally. No material data, holdout or fit used. The old CLOSED_FOR_CORE composition must not be presented as newly revalidated while this defect is unresolved.

## Correspondence source

Schianchi and Abalos, arXiv:2602.20254v3, Lemma4, equations73-74, printed page11, explicitly distinguishes temperature times entropy divergence from the thermal flux-force contraction. This corroborates the local product-rule derivation; it is not used to establish UET microscopic matching. [Primary paper](https://arxiv.org/pdf/2602.20254v3).
