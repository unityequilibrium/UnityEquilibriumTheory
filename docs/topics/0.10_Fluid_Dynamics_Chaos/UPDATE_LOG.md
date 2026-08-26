## Wave 1 Research Room Checkpoint (2026-08-10)

STATUS: Wave 1 coordination checkpoint recorded; claim promotion remains disabled.

WHAT_CHANGED: Core room contract now links Topic 0.13, Topic 0.11, Core O(2), and Topic 0.10 comparator evidence with explicit blockers and next actions.

EQUATION_OR_MAPPING: The declared TTG mapping remains `y_TTG = Delta_Tq(t)/Delta_Tq(0)`, `y_TTG^UET = Delta_Phi(t)/Delta_Phi(0)`, and `Delta_Tq = alpha_Phi_K * Delta_Phi`; `alpha_Phi_K` remains open.

VERIFICATION: Wave 1 contract and integration gate were regenerated from local artifacts. The selected frozen-C causal reference is kept separate from the full coupled leakage gate.

CONTROLLING_BLOCKER: Full coupled pre-arrival leakage, independent thermal calibration, and Topic 0.11 source/estimator acceptance remain open.

NEXT_ACTION: Resolve the owning room blocker and rerun its machine-readable gate before expanding scope.

CLAIM_BOUNDARY: Internal/provisional evidence only; no proof, prediction, external validation, or theory closure.

## 2026-08-26 Chaos method validation

MAJOR_RESULT_CLOSURE: `T010_CHAOS_METHOD_VALIDATED` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: Benettin/QR and shadow estimators reproduce a stable linear exponent, logistic `ln(2)`, and a resolved positive Lorenz-63 exponent.

WHAT_REMAINS_OPEN: No physical UET fluid-chaos or external CFD validation claim has been tested. The speed comparator remains `FAIL` at approximately `1.914x < 2.0x`.

DEPENDENCY_UNLOCKED: The normalized Topic 13 diagnostic pilot only.

STATUS: `PASS_CHAOS_METHOD_VALIDATION`; claim promotion remains disabled.

WHAT_CHANGED: Added a machine-readable chaos-method artifact separate from the existing runtime/stability comparator.

EQUATION_OR_MAPPING: `delta_x[n+1]=D F(x[n])delta_x[n]`; `lambda_i=lim_T log(s_i)/T`.

VERIFICATION: Stable linear `lambda=-0.4`, logistic `lambda approximately ln(2)`, and Lorenz-63 positive-exponent controls pass with tangent/shadow agreement.

CONTROLLING_BLOCKER: Physical UET constitutive transport and external validation remain outside this method-control lane.

NEXT_ACTION: Consume the validated method in bounded, preregistered topic diagnostics without changing the speed threshold.

CLAIM_BOUNDARY: Internal numerical-method validation only; not evidence that UET fluid dynamics is chaotic.
