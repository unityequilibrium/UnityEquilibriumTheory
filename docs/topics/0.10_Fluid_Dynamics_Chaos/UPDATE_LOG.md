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

## 2026-09-26 OpenAI Navier–Stokes applicability review

- Wave type: source and claim-boundary review; no evidence-producing model change.
- Changed: added `OPENAI_NAVIER_STOKES_APPLICABILITY_2026-09-26.md` and linked it from Topic 10 and the joint plan.
- Verified: read OpenAI Theorem 1.1 and construction outline, Lean repository README and Clay statement/rules; compared them with the Topic 10 2D/3D engines, formula audit, speed script and latest artifact. Link and diff checks recorded in the daily ledger. No Lean build, CFD run or new UET verifier was performed.
- Result: high method/proof-scope utility, conditional future 3D adversarial-test utility, no direct evidence for UET speed, physical fluid validity, thermal transport or theorem closure.
- Blocker narrowed in source review: theorem requirements are mapped to the exact missing Topic 10 state/momentum/forcing/norm obligations; no scientific blocker closed.
- Next controller: J00 scope and source admission, then J01 rotational-flow representability. Paper-specific finite-window control requires J04 admission and a reproducible forcing package.
- Claim impact: none; legacy speed FAIL, method-control PASS and Core/Topic 13 boundaries are unchanged.

## 2026-09-26 J01 periodic state/velocity representability audit

- Wave type: scoped mathematical-control and source audit under the Topic 10–13 plan.
- Changed: added the reproducible verifier and result artifact; synced METHOD, FORMULA_AUDIT, LIMITATIONS, VERIFICATION_SPEC, DATA_MANIFEST, README, the joint plan, and OpenAI applicability notes.
- Verified: periodic manufactured controls at N=16/32/64; gradient-curl relative residuals below 5.0e-16; rotational target divergence exactly zero in the discrete control; gradient projection zero to numerical precision; best relative L2 residual 1; vorticity refinement orders 1.9917 and 1.9979. Static source checks passed for the mobility reset, unused physical mobility field, default kappa cap, clipping floors, and absent 3D vector state.
- Result: scoped no-go established for nonzero periodic incompressible vortical targets under the current constant-M 2D scalar-gradient map. This is not a UET-wide no-go and does not validate a physical trajectory.
- Runtime boundary: both engine imports are blocked in the configured Python runtime by missing SciPy; no integration or clip-event count was run. Claim promotion and dependency unlock remain false.
- Controlling blocker: a separately registered Topic 10 velocity/momentum state with closed units and derivation must pass Core F0-F8 before physical matched-flow J04; Topic 13 J02/J03 work remains parallel.
- Next action: review the candidate state contract with Core, restore the declared runtime dependency environment for the dynamic clipping pass, then begin J04 only after state admission.

## 2026-09-26 J02 He-4 second-sound source/protocol candidate

- Wave type: Topic 13 source/protocol and claim-boundary pass linked to Topic 10; no UET dynamic model was run.
- Changed: added the He-4 second-sound source package and protocol card, a reproducible audit artifact, J02 manifest progress, and Topic 10/OpenAI applicability notes.
- Verified: J02 protocol audit passed 15/15 checks; recommended source rows and frozen alpha/theta_T/Z/e0 plus external eta identities match the existing records.
- Result: a bounded full-He-II dynamic response candidate is available for future comparison; current Topic 10 scalar state cannot emit this eigenmode.
- Blocker narrowed: exact primary-row uncertainty/frequency/state and the admitted UET two-fluid operator remain open; response rows were seen and are not a blind holdout.
- Next controller: source-lock a primary resonance protocol, then derive/admit a two-fluid thermal eigenmode through Core F0–F8; J06 needs a fresh blind source or a retrospective label.
- Claim impact: none; no UET prediction, external validation, Core closure or dependency unlock.

## 2026-09-26 OpenAI Euler result applicability addendum

- Wave type: primary-source literature review; no model, benchmark, or acceptance-gate change.
- Changed: expanded the Topic 10 OpenAI assessment and joint-plan source review to cover OpenAI's 3D unforced Euler result alongside its forced Navier–Stokes construction.
- Verified: read both official papers, OpenAI's announcement, and the Lean repository README; local J01 outcome and current velocity-state blocker were cross-checked. Lean/Comparator, CFD, and UET solver were not run.
- Result: theorem-scope, norm, vorticity and residual design value remains high; direct evidence for UET physics, performance or Topic 13 response remains absent.
- Controlling blocker: register a vector velocity/momentum state with ontology, units and derivation through Core F0–F8; J01's no-go remains scoped to the current legacy mapping.
- Next action: prepare that state contract for Core admission; only after admission define the matched physical-flow J04 test.
- Claim impact: none; no readiness change, calibration, dependency unlock or promotion.
