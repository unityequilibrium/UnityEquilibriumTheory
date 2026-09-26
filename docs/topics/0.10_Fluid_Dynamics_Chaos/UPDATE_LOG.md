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

## 2026-09-26 Joint Topic 10–13 research design

- Wave type: planning / claim-boundary pass; scientific execution not started.
- Changed: added `JOINT_RESEARCH_PLAN_TOPIC10_TOPIC13.md` and `Data/03_Research/fluid_thermal_joint_research_plan.json`; linked both topic entrypoints.
- Verified: JSON structure, 10 unique work-package IDs, acyclic dependencies, required acceptance/failure fields, 16 published-base evidence hashes and relative plan links checked using PowerShell; no scientific verifier rerun because equations, inputs and thresholds were not changed.
- Result: a reviewable joint plan with all work packages `NOT_STARTED`, `claim_promotion=false` and `dependency_unlock=false`.
- Blocker narrowed in planning: general fluid-model readiness is separated into state/velocity representability, matched numerical verification, admitted constitutive interface, independent physical response and work–precision claims. No scientific blocker is newly closed.
- Next controller: J00 source/protocol/admission lock; first scientific wave J01 `fluid_state_and_velocity_observable_correspondence_unestablished`.
- Still open: external CFD, physical fluid-chaos validation, Core admission for full constitutive transport, and independent He-4 response protocol; graphite remains on its separate input track.
- Claim impact: none; legacy speed FAIL and standard chaos-method PASS remain separate.
- Publication: based on public main `d069507651964c0f963d1568667e2a9218400e42` in an isolated worktree; original dirty-workspace differences are recorded as hashes, not imported.
