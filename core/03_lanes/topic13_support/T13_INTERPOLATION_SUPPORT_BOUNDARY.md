# Interpolation support and massive mass-shell boundary

MAJOR_RESULT_CLOSURE: PARTIAL; fixed-support sensitivity measured and a conditional limit on exact positive pointwise interpolation established.
WHAT_IS_ACTUALLY_CLOSED: All six locked cases completed. Within each direction rule, trace(K)/3 changes by less than2e-16 relative across supports16/40/64, while unweighted pre-projection energy and momentum defects remain substantial. Tensor stability alone does not certify interpolation consistency.
WHAT_REMAINS_OPEN: Refinement-controlled interpolation error, rate-weighted functional accuracy, input sensitivity, charged-frame production integration and material mapping.
DEPENDENCY_UNLOCKED: No physical/Core unlock. The next useful target is interpolation consistency, not repeated precision-only solves.
STATUS: SUPPORT_SENSITIVITY_MEASURED_NOT_CONVERGENCE.
WHAT_CHANGED: Locked plan, support-study runner, three tests, complete artifact, this note and registry proposal. No production interpolation, threshold, parameter or historical artifact changed.
EQUATION_OR_MAPPING: E(p)=sqrt(m^2+|p|^2) is strictly convex for m>0. Positive normalized interpolation obeys E(sum a_i p_i)<=sum a_i E(p_i), with equality only for coincident supported momenta.
VERIFICATION: Three tests PASS: off-grid positive mixture, exact matching-node limit and support saturation. Six tensor cases complete exit0 at the predeclared120 digits. F0 inventory369/no duplicates, PASS_WITH_DISCLOSED_GAPS. Foundation/compatibility audits PASS with physical gates BLOCKED. Evidence hashes verified.
CONTROLLING_BLOCKER: interpolation_consistency_under_refinement_and_rate_weighted_accuracy.
NEXT_ACTION: Compare a declared moment-reproducing interpolation candidate with this frozen positive kernel, or demonstrate decreasing approximation error under spatial/momentum refinement. Signed interpolation coefficients, if used, must be explicitly numerical coefficients rather than probabilities; positivity of physical rates and collision dissipation must remain separately checked. Do not choose support16 merely because its unweighted error is smaller.
CLAIM_BOUNDARY: Per-leg pointwise errors are not material conductivity errors. This conditional no-go does not forbid approximate positive interpolation, convergence with finer grids, or exact aggregate conservation by a channel-level construction. Full Topic13 remains open.

## Complete support comparison

State and all controls remain those of the coarse constrained tensor reference, except the declared support count. The requested64-node support saturates at48 same-species nodes in axis6 and is recorded as such, not mistaken for64 actual nodes.

| Rule | Requested / effective support | RMS relative energy error | Maximum relative energy error | Maximum momentum error / target energy |
| --- | ---: | ---: | ---: | ---: |
|axis6|16 /16|0.3690|1.2784|0.8425|
|axis6|40 /40|1.5028|7.7437|0.8827|
|axis6|64 /48|1.9058|9.6069|0.9530|
|axis_cube14|16 /16|0.2337|0.4773|0.7755|
|axis_cube14|40 /40|0.3779|1.4552|0.8712|
|axis_cube14|64 /64|0.8078|4.2527|0.8459|

These are unweighted errors over channel legs BEFORE projection, not rate-weighted uncertainties. All cases give natural trace(K)/3 approximately254.8247192563 with positive symmetric-part response eigenvalues and very small factorized-balance residuals. Thus even striking response stability can coexist with large pointwise mapping defects. Wider support here is stronger smoothing, not necessarily higher resolution.

## Conditional exactness boundary

The Hessian of E is I/E-p p.T/E^3. Its eigenvalues are1/E in transverse directions and m^2/E^3 in the radial direction, all positive for m>0. Jensen's inequality is therefore strict for a mixture containing distinct momenta with positive coefficients.

If an off-grid target lies on the same massive shell and positive normalized coefficients reproduce its momentum exactly, their interpolated energy is strictly larger than the target energy. Hence exact energy AND momentum reproduction cannot both be required of that nontrivial positive per-leg mixture. The two-point manufactured example p=(-1,0,0),(1,0,0), weights1/2 and m=1 reproduces zero momentum but gives energy sqrt(2), not1.

This does not eliminate the need for an error bound. It identifies why demanding exact pointwise four-moment reproduction from the current positive blur would be an inappropriate acceptance requirement. A consistent approximate scheme may reduce this gap under refinement; a different representation may preserve aggregate channel moments. Neither has been demonstrated by the present support scan.

Evidence: artifacts/t13_interpolation_support_plan.json and artifacts/t13_interpolation_support_audit.json. The latter records every tensor, pre-projection defect and input hash. No source or holdout dataset was used.
