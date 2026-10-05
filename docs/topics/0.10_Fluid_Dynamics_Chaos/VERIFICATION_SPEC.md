# Verification Spec

- Primary command:
  - `python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/02_Proof/Proof_Turbulence_Benchmarks.py`
- Inputs:
  - Benchmark grid configuration embedded in script
  - Internal comparator implementation
  - `Data/03_Research/source_lock_manifest.json`
- Reported metrics:
  - Runtime for comparator and UET solver
  - Relative speedup
  - Stability under stress test
  - machine-readable `results.status`
  - source-lock, benchmark-script, and core-equation hashes
- Current threshold:
  - `speedup > 2.0`
  - finite stress-test output
- Artifact target:
  - `Result/artifacts/fluid_benchmark_validation.json`
- Interpretation:
  - `PASS` means the implementation beat the embedded simplified comparator under this
    declared configuration and finite-output stress gate.
  - It does not establish external CFD validation or theorem-level Navier-Stokes results.

## Chaos Method Validation

- Command: `python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Chaos_Method_Validation.py`
- Artifact: `Result/artifacts/chaos_method_validation.json`
- Controls: stable linear flow, logistic map at `r=4`, and Lorenz-63.
- Primary estimator: Benettin/QR tangent evolution.
- Cross-check: periodically renormalized shadow trajectories.
- Acceptance: known sign/value controls, time-step convergence, method agreement,
  and explicit exclusion of `R_gen` and `R_obs` from dynamical state.
- Interpretation: a pass validates the internal numerical method only; it is
  independent of the speed comparator and does not establish chaos in UET.

## J01 state/velocity representability audit

- Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_State_Velocity_Representability.py
- Artifact: Result/artifacts/fluid_state_velocity_representability_audit.json
- Controls: periodic smooth scalar potential versus a manufactured divergence-free rotational
  target with nonzero vorticity; centered periodic finite differences at N=16, 32, 64;
  discrete gradient-subspace projection; vorticity refinement check against its analytic value.
- Source checks: 2D mobility assignment/reset, use of PhysicalProperties.mobility, kappa cap,
  C clipping floors, and 3D vector-state assignments.
- Acceptance: gradient curl and target divergence below 1e-12 relative scale; target
  vorticity nonzero; gradient projection below 1e-12; best relative L2 residual equals one
  to 1e-10; vorticity observed order at least 1.8.
- Interpretation: a pass closes only representability of the declared legacy periodic map
  for the target class. It is not a solver trajectory, physical CFD validation, UET-wide
  no-go, theorem result, or Core dependency admission.
- Runtime limitation: the current configured Python runtime cannot import the UET engines
  because a transitive Core import requires SciPy; dynamic clip counts are therefore not
  reported. Source paths, unit scope, and hashes remain in the artifact.

## Vector-state conditional reference audit

- Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Vector_State_Contract.py
- Contract: Data/03_Research/fluid_vector_state_research_contract.json
- Result: Result/artifacts/fluid_vector_state_contract_audit.json
- Retained insensitive-control result: Result/artifacts/fluid_vector_state_contract_initial_control_failure.json
- Grid controls: N=16/32/64; instantaneous resolved Fourier fields, no timestep.
- Identity tolerance: 1e-9 relative to max(1, RMS reference scales).
- Directional derivative tolerance: 1e-7; central steps 1e-3, 1e-4, 1e-5.
- Negative-control work sensitivity floor: 1e-8 normalized work units; missing
  force, wrong sign and omitted Phi advection must produce nonzero defects.
- Version 1 intentionally fails nine sensitivity checks across three grids;
  version 2 adds a mixed harmonic after preview, with unchanged thresholds.
- Source hashes: script, candidate registry/card/contract, parent formula/spec,
  ontology, foundation gate and legacy J01 artifact.
- Regression: Code/03_Research/test_fluid_vector_state_contract.py checks source
  freshness, current success and preservation of the insensitive-control FAIL.
- Interpretation: PASS_NORMALIZED_VECTOR_REFERENCE_IDENTITIES_ONLY is a reference
  diagnostic, not Core F5 admission or a physical J04/J05 gate. F2/F3/F4/F7/F8 stay
  blocked; there is no observable, SI, chaos, performance or external-data result.
## Conditional variational-origin audit

- Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Vector_Variational_Origin.py
- Contract: Data/03_Research/fluid_vector_variational_origin_contract.json
- Artifact: Result/artifacts/fluid_vector_variational_origin_audit.json
- Source: canonical scalar AST algebra plus declared action and independent
  displacement/internal variations. Controls locked before the numerical run.
- N=16/32/64 in time and two periodic spatial dimensions; xi/chi zero at endpoints.
- Identity tolerance 1e-9; action/fibre central-derivative tolerance 1e-7;
  steps 1e-3/1e-4/1e-5; negative-control floor 1e-8.
- Checks: first variation versus direct action finite difference and integration
  by parts; C tangent constraint and Q chain; canonical fibre momenta; Hamiltonian
  inverse and sampled positive rate Hessian. Manufactured paths are not stationary.
- Negative controls: omitted Phi transport alters action derivative; omitted Q
  transport breaks local chain despite zero integrated work; rho0 u alone fails
  the canonical velocity derivative.
- Three regression tests rerun the audit, verify source freshness/claim boundary
  and guard the hidden local-transport/canonical-momentum errors.
- PASS_CONDITIONAL_VARIATIONAL_REFERENCE_ONLY does not admit a physical UET
  operator, full reduced Poisson structure, dissipative closure, SI/He-II mode,
  PDE trajectory/convergence, formal kernel proof or global regularity.

## Second-sound mode eligibility reference

- Verifier: Code/03_Research/Research_Fluid_Second_Sound_Mode_Eligibility.py
- Contract/card: Data/03_Research/fluid_second_sound_mode_eligibility_contract.json;
  SECOND_SOUND_MODE_ELIGIBILITY.md.
- Current artifact: Result/artifacts/fluid_second_sound_mode_eligibility_audit.json;
  139 checks pass, source hashed, complex warnings treated as errors in regression.
- Retained preview: Result/artifacts/fluid_second_sound_mode_initial_metric_diagnostic.json;
  nominal 123-check PASS is INVALID_COMPLEX_METRIC_PREVIEW_NOT_ACCEPTED.
- k=0.2 down to 0.003125 by halving; identity tolerance 1e-9;
  Hessian directional derivative 1e-7; finest slow/sound slope tolerance 1e-3;
  error-control floor 1e-8. Original controls/thresholds unchanged after preview.
- Tests cover source freshness, bounded admission state, invalid-preview retention,
  diffusion/gap versus acoustic/advection/massless classes and imaginary/sign errors.
- Added imaginary-work and reversed-counterflow controls are post-preview harness
  repair, not preregistration. Complex RMS is sqrt(mean(abs(a)^2)).
- PASS_CURRENT_CANDIDATE_HYDRODYNAMIC_MODE_EXCLUSION_ONLY is a scoped rest-frame
  reference result. Audit failure reports UNRESOLVED_AUDIT_FAILED. No physical
  He-II prediction, PDE trajectory, formal checker or Core/Topic 13 unlock.

## Standard two-fluid/EOS reference audit

- Verifier: Code/03_Research/Research_Fluid_Two_Fluid_EOS_Reference.py.
- Contract/card: Data/03_Research/fluid_two_fluid_eos_reference_contract.json;
  TWO_FLUID_STATE_EOS_REFERENCE.md.
- Inputs: Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json;
  material values/uncertainties remain null, not an admitted dataset.
- Artifact: Result/artifacts/fluid_two_fluid_eos_reference_audit.json; 59 checks.
- Identity tolerance 1e-9; EOS/Gibbs/c_p directional tolerance 1e-7,
  steps 1e-3/1e-4/1e-5; error sensitivity floor 1e-8.
- Seven halved wavenumbers; N=32 periodic work/flux controls, no time evolution.
- Compare two acoustic pairs/quartic, ideal complex work, local/mean conservation,
  common/relative inertia, zero-expansion subspace and finite-expansion defects.
- Distinct EOS witnesses must share the specified local SVP tangent and yield
  different modes; omitting the saturation heat correction must be detectable.
- Three source-fresh regression tests guard physical non-admission, forbidden
  entropy/common-flow shortcuts and path-input underdetermination.
- Controls were specified before the first audit and not amended after preview.
  PASS_STANDARD_TWO_FLUID_AND_PATH_UNDERDETERMINATION_REFERENCE_ONLY does not
  advance physical J05/J06, perform material prediction or formal verification.

## He-II fixed-constraint source audit

- Verifier: Code/03_Research/Research_He4_Fixed_Constraint_EOS_Source.py.
- Card/package: HE4_FIXED_CONSTRAINT_EOS_SOURCE_CARD.md;
  Data/03_Research/he4_tn1334_fixed_constraint_eos_source_candidate.json.
- Artifact: Result/artifacts/he4_tn1334_fixed_constraint_eos_source_audit.json;
  56 checks on source metadata, three SI-converted liquid rows, EOS branch,
  assumed printing compatibility and retained physical-admission boundaries.
- Before first execution: symmetric half-last-displayed-unit boxes, including T;
  closed overlap for three standard thermodynamic relations, no adjustable
  residual tolerance and no physical acceptance budget. Decimal precision 60.
- Five locked negative controls: MPa treated as Pa, alpha*T not divided by T,
  P*kappa not divided by P, vapor density substitution and blank transport as zero.
- Four regressions rerun the source-fresh audit, guard conversion/constraints,
  distinguish printing compatibility from exact point identities, and require
  corrupted phase/blank imports to emit a failed artifact and exit 1.
- PASS_SOURCE_CANDIDATE_PRINTING_COMPATIBILITY_ONLY does not establish physical
  row uncertainty, independent experiments, material input admission or UET
  prediction. Raw PDF review is manual; the offline verifier hashes the curated
  transcription and does not rediscover it from the upstream PDF.

## Entropy-source/reference-coordinate audit (2026-09-30)

Source contract: [he4_entropy_source_and_reference_contract.json](Data/03_Research/he4_entropy_source_and_reference_contract.json).
Before code it locks normalized base/offsets [-0.3,0,0.4,1.0], 1e-10 identity
tolerance, 1e-8 negative-control floor and grid 32. First audit passes 116/116;
no rule, token or tolerance was amended after execution.

[Research_He4_Entropy_Source_Reference.py](Code/03_Research/Research_He4_Entropy_Source_Reference.py)
checks source/branch/date/SI boundaries, independently assembled flux/force
versus similarity, work congruence/positivity, Gibbs pressure/capacities, invariant
roots and local periodic balances. Omitting entropy correction, phase correction
or both is detected for each nonzero shift. Both-omitted positive-work PASS is
deliberately recorded to prevent energy-only correspondence claims.
[test_he4_entropy_source_reference.py](Code/03_Research/test_he4_entropy_source_reference.py)
adds four fresh-output regressions, including corrupt units/anchor claims.

Artifact: [he4_entropy_source_reference_audit.json](Result/artifacts/he4_entropy_source_reference_audit.json).
Source hashes exclude temporary PDFs; full rendered-page review is manual and
cannot be independently established by the offline audit. Six source tokens
are candidates only. Central nominal differences have no acceptance threshold,
temperature interpolation or reference conversion. Original material values
stay null. No physical/Core/Topic 13 gate is promoted.

## Core common-flow composition probe (2026-09-30)

[Contract](Data/03_Research/fluid_core_o2_common_flow_contract.json) locks five
state points, quadrature orders 128/256/384 at fixed cutoff 70, cutoffs 45/70/100
at fixed order 384, and five-point derivative steps 1e-3/3e-4/1e-4.
Composition tolerance 1e-5, observed component-change budget 1e-6,
tree/spectrum identity tolerance 1e-8 and sensitivity floor 1e-7 are unchanged
after the first execution.

[Research_Fluid_Core_O2_Common_Flow.py](Code/03_Research/Research_Fluid_Core_O2_Common_Flow.py)
executes selected source definitions only, with exact quadrature memoization.
The local full Core import was inspected and requires unavailable scipy;
its facade/whole runtime is not executed. Native Core derivative/state functions
are not replaced. New wrapper derivatives are explicitly identified.

Artifact [fluid_core_o2_common_flow_composition_audit.json](Result/artifacts/fluid_core_o2_common_flow_composition_audit.json):
69/69 execution/control checks pass, but the condensed composition gate
FAIL_REQUIRED_COMMON_FLOW_IDENTITY remains at all three selected points.
Normal controls and tree EOS/Goldstone match pass. No gate is promoted by the
diagnostic PASS. No post-preview threshold/control amendment occurred.
[test_fluid_core_o2_common_flow.py](Code/03_Research/test_fluid_core_o2_common_flow.py)
adds four fresh-output/source-hash/boundary regressions, including false-admission
rejection and numerical-stability separation. No physical coefficient is repaired
to force common-flow closure.

## Independent fixed-Phi flow Hessian (2026-09-30)

[Contract](Data/03_Research/fluid_core_o2_flow_hessian_contract.json) locks three
previous condensed states, radial orders128/256/384, cutoffs45/70/100, angular
orders12/24/36 and phase-source steps |h|/mu=1e-3/3e-4/1e-4.
Composition tolerance1e-5; implicit component refinement1e-6; independent
thermal correction agreement and step refinement1e-5; root/determinant/parity
tolerances1e-9/1e-10/1e-9. No numerical thresholds changed after preview.

[Research_Fluid_Core_O2_Flow_Hessian.py](Code/03_Research/Research_Fluid_Core_O2_Flow_Hessian.py)
passes 98 controls and a separate scalar target at all three points.
Implicit and finite-flow thermal corrections agree within 2.7e-7 relative;
common-flow residuals are below 8e-12. Current zero-flow Core sources are
source-verbatim AST references; the finite-flow kernel is new topic-local code.

The [first 96-check output](Result/previews/fluid_core_o2_flow_hessian_first_execution.json)
and [exact executed source archive](Result/previews/core_o2_flow_hessian_first_execution_verifier.py.txt)
are immutable historical records, not current source-fresh audits. Subsequent
changes add empty-state rejection and archive-integrity guards only.
[test_fluid_core_o2_flow_hessian.py](Code/03_Research/test_fluid_core_o2_flow_hessian.py)
checks fresh input identities, target independence, two curvature methods,
unchanged prior FAIL, term omission sensitivity and false-admission/empty-state
failure. No full Ward, physical dynamics, He-II state or Core/Topic 13 gate is admitted.

## Local scalar tensor and conditional ideal modes (2026-09-30)

[Contract](Data/03_Research/fluid_core_o2_ideal_modes_contract.json) locks the
three prior controls, radial orders128/256/384 and cutoffs45/70/100 separately,
thermal and source/metric steps1e-3/3e-4/1e-4. Derivative correspondence1e-5,
implicit refinement1e-6, finite refinement1e-5, source/metric1e-7, algebra/
covariance/work/pole1e-8, proxy correspondence1e-5 and sensitivity floor1e-7.

[Research_Fluid_Core_O2_Ideal_Modes.py](Code/03_Research/Research_Fluid_Core_O2_Ideal_Modes.py)
passes 171 controls; numerical tolerances, states and coefficients did not
change after the first execution. Thermal Hessian derivatives, finite metric/
phase derivatives, local stress symmetry and conjugate-map inverse pass.
Independent state-coordinate operators, positive energy and real/complex local
work cancellation agree, with two distinct real acoustic pairs at each point.

[test_fluid_core_o2_ideal_modes.py](Code/03_Research/test_fluid_core_o2_ideal_modes.py)
adds four fresh-source/tensor/mode/assumption regressions. Unsupported
thermalization, empty states and false physical operator admission fail closed.
Earlier source/phase artifacts remain current and unchanged. A local ideal
PASS is not full microscopic Ward completion, nonlinear dynamics, material
He-II prediction, thermalization or physical package execution.

## Leading cubic Goldstone channel (2026-10-01)

[Contract](Data/03_Research/fluid_core_o2_goldstone_collision_contract.json):
mu=1.28, fixed Phi=.15, source mass/Z unchanged; exploratory couplings .01/.001,
momenta .02/.01/.005, orders48/96/192. Locked energy1e-11, algebra1e-10,
order1e-7, leading coefficient/curvature1e-3, group-velocity1e-6 tolerances.
[Verifier](Code/03_Research/Research_Fluid_Core_O2_Goldstone_Collision.py)
passes159 controls, including source-root balance, polarized vertex, k^5,
coupling scaling, pole factor two, NR limit and triad conservation/null modes.

The [first diagnostic](Result/previews/fluid_core_o2_goldstone_collision_first_execution.json)
retains153/159 with endpoint triangle defects up to7.84e-8 against1e-11.
[Exact old source](Result/previews/core_o2_goldstone_collision_first_execution_verifier.py.txt)
matches its original hash. Stable factored geometry repairs all six failures;
thresholds/rates/action/state did not change. A later temporary-contract path
handling repair allows unsupported-admission tests to emit a failing artifact.
[Four regressions](Code/03_Research/test_fluid_core_o2_goldstone_collision.py)
check fresh source hashes, rates/normalization, extra null modes, archived
failure identity and fail-closed unsupported thermalization/operator/empty inputs.
No physical transport or package gate is promoted.

## Shared scalar/vector Goldstone Galerkin diagnostic (2026-10-01)

[Contract](Data/03_Research/fluid_core_o2_goldstone_galerkin_contract.json):
T=.002/.004, mu1.28, exploratory lambda.01, cutoffs20/30/40*T/c,
orders24/48/72 and features2/3/4/5. Event1e-9 and algebra1e-8 controls;
relative spectral tolerance1e-9 with no absolute rate cutoff.
R/current-time order, cutoff and last-basis acceptance remain1%.
Source representation has its own1% squared-norm target.
Whole-action scale2 checks G:E5,Q:E6,R:E4,rate:E1 and basis-time:E-1.

[Verifier](Code/03_Research/Research_Fluid_Core_O2_Goldstone_Galerkin.py)
passes454 structural controls. The separate measured gate remains OPEN because
basis/cutoff targets fail at both states. No tolerance or parameter is fitted.
[Four regressions](Code/03_Research/test_fluid_core_o2_goldstone_galerkin.py)
preserve fresh hashes, raw invariants, source constraint/independent resolvents
and failed target boundaries; false current admission, empty states and relaxed
basis targets fail closed.

The [first diagnostic](Result/previews/fluid_core_o2_goldstone_galerkin_first_execution.json)
and [exact source](Result/previews/core_o2_goldstone_galerkin_first_execution_verifier.py.txt)
are retained. First source encoded the linear-current zero; current source
executes the current/momentum constraint numerically. R/time, locked rules and
all measured refinement outcomes remain unchanged. No physical promotion.

## Stable vector and soft trial-space refinement (2026-10-01)

[Contract](Data/03_Research/fluid_core_o2_vector_refinement_contract.json):
same mu1.28, exploratory lambda.01 and T=.002/.004; parent/daughter Gauss
orders96/144/192, cutoffs40/50/60*T/c, EVEN orders5/9/13/17 and
SOFT orders5/9/17/25/35. Energy cutoff/gap<=.1; scale2 dimensions.
Event1e-9, algebra1e-8, relative spectral1e-9, same-span1e-8.
All response/refinement/source targets remain1%, fixed before execution.

[Verifier](Code/03_Research/Research_Fluid_Core_O2_Vector_Refinement.py)
passes541 structural checks; measured refinement remains OPEN at both states.
SOFT within-family targets pass; EVEN basis/cutoff and cross-family targets fail.
[Four regressions](Code/03_Research/test_fluid_core_o2_vector_refinement.py)
check source freshness/non-admission, shared invariants/same-span/nested response,
honest failed targets and fail-closed admission/empty/relaxed-target mutations.
First execution needed no repair. Older failed Galerkin results remain unchanged.
A green diagnostic or regression is not a green physical convergence gate.

## Independent enriched/smooth trial acceptance (2026-10-01)

[Contract](Data/03_Research/fluid_core_o2_infrared_trials_contract.json):
same exploratory states/coupling; Gauss96/192/384, cutoffs40/50/60*T/c,
HYBRID6/10/14/18, SOFT35 and EVEN17. Smooth HYBRID18 delta=.1/.03/.01/.003.
All response/refinement/source targets remain1%; algebra1e-8, event1e-9,
relative spectral1e-9, correspondence1e-8 and E_cut/gap<=.1.

[Verifier](Code/03_Research/Research_Fluid_Core_O2_Infrared_Trials.py)
passes664 structural checks and the declared finite enriched/smooth targets.
Cross-family0.04684%/0.04251%; HYBRID last basis0.02286%/0.02409%, last
cutoff0.01249%/0.01083%. Last smooth/HYBRID differences below6.3e-7 relative.
[Four regressions](Code/03_Research/test_fluid_core_o2_infrared_trials.py)
cover fresh hashes/archive/collision-tail, discrete bounds versus historical
failure, smooth origin/rounded geometry and fail-closed physical/continuum claims.

First execution124/126 stopped before any complete state on rounded geometry.
[First source](Result/previews/core_o2_infrared_trials_first_execution_verifier.py.txt)
and [output](Result/previews/fluid_core_o2_infrared_trials_first_execution.json)
remain exact. The full function AST change is reported; physical collision-tail
AST matches. Precision repair uses no clipping, floors or changed acceptance.
664 includes30 source-relation guards. No continuum/physical gate promotion.

## Selected finite-cutoff continuum-form diagnostics

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Continuum_Form.py.
Contract: [locked controls](Data/03_Research/fluid_core_o2_continuum_form_contract.json).
Artifact: [continuum-form audit](Result/artifacts/fluid_core_o2_continuum_form_audit.json).

Before execution the card/contract/separate registry locks states, cutoff,
point grids, smooth/bump deltas, Gram64/128/256 and unchanged tolerances.
Exact Fraction polynomial subtraction vanishes; removing a pressure term is
a nonzero negative control. Original source events check vertex/density
majorants, positive noncollinear geometry and energy closure. Gram quadrature
checks explicit bump/projection lower formulas,1% last-order targets and scale2
checks w:E2,W:E2,prefactor:E-3,G:E5,Q:E6,Q/G:E1.

First execution291/291 passes without a kernel/parameter/target repair.
Current292/292 adds explicit prior-source hash freshness and its rejection
control. Four regressions pass; guards reject stale input, false formal/physical/
current admission, empty states and relaxed/changed controls.
PASS supports only the explicit conditional internal derivation. It is not a
formal or interval certificate, full continuum inverse, external math review,
material current or physical hydrodynamic admission.

## Selected current-bound diagnostics (2026-10-01)

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Current_Bound.py.
[Contract](Data/03_Research/fluid_core_o2_current_bound_contract.json),
[card](CORE_O2_GOLDSTONE_CURRENT_BOUND.md),
[artifact](Result/artifacts/fluid_core_o2_current_bound_audit.json).

Before execution: same states/coupling/cutoff60, two patch grids, current
Gauss64/128/256 and existing algebra1e-8/event1e-9/refinement1%/scale2 locks.
Pre-execution dimensional review defines the response as sup b^2/Q, unitsE4.
First execution267/267 passes without parameter/threshold repair. Current289/289
adds explicit raw momentum-null and soft dual O(k) diagnostics.
Four regressions check immutable inputs, analytic-not-sampled constants, exact
polynomial identity/wrong-factor control, source-frame null obstruction,
quadrature/soft/unit limits, and fail-closed physical/formal/useful-error/strong
inverse claims, stale sources and altered controls. Same-runtime bytes are
reproducible; published/fresh analytic values use locked relative tolerance.
No full continuum inverse, formal/interval/external verification or physical
transport execution. A conditional loose upper formula does not pass a useful
relative-error or material admission gate.

## Tree spatial current Ward diagnostics (2026-10-01)

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Current_Ward.py.
[Contract](Data/03_Research/fluid_core_o2_current_ward_contract.json),
[card](CORE_O2_MICROSCOPIC_CURRENT_WARD.md),
[artifact](Result/artifacts/fluid_core_o2_current_ward_audit.json).

Prelocked: unchanged low-T states/mu/coupling/cutoff; two positive branches,
four parent momenta, phase orders8/16/32, amplitudes.001/.002/.004 and phases0/.37;
five-point flow derivatives at three steps and three momenta; projection
Gauss64/128/256. Algebra/source/phase/index/scale1e-8, derivative1e-5,
last-order projection1%, negative-control floor.001 and energy scale2.
First execution303/303 passes without scientific repair, fit or target change.

Four regressions repeat fresh execution twice with same-runtime byte comparison,
source/AST/card/registry identity, all288 field controls/36 derivative controls,
charge/index/omission rejection, projected old-source correspondence, unit powers,
density/frame boundaries and fail-closed stale inputs/false admissions/controls.
Published/fresh nonzero mode/source values use the locked relative tolerance.
No full density/interacting/formal/material or physical package execution.

## Leading mean density/source and fixed-domain Gaussian diagnostics

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Density_Backreaction.py.
[Contract](Data/03_Research/fluid_core_o2_density_backreaction_contract.json),
[card](CORE_O2_DENSITY_BACKREACTION.md),
[artifact](Result/artifacts/fluid_core_o2_density_backreaction_audit.json).

Prelocked states/source/coupling, two branches/four momenta, phase orders8/16/32,
phases0/.37 and coefficient amplitudes.01/.02/.04/.08. Exact rational
interpolation weights extract the source quadratic coefficient. Conditioned
source/algebra/phase/unit1e-8, centered five-point derivative1e-5 at three
relative steps, thermal Gauss64/128/256 last-order1%, energy scale2.
Actual post-cancellation charge errors and condition numbers are reported.

First process stopped before a state on an incorrect Core function name;
the next stopped on an offset/absolute-mu derivative caller mismatch.
[Binding repair](CORE_O2_DENSITY_SOURCE_BINDING_REPAIR.md) and
[derivative-center repair](CORE_O2_DENSITY_DERIVATIVE_CENTER_REPAIR.md) preserve
both source/failure records and the first contract. Only caller wiring changed;
no scientific formula, state, steps or threshold changed. First complete
diagnostic398/398 passes. Four regressions cover source/archive identity,
192 coefficient sets,48 root variations, conditioned/raw/mean source and
fixed-domain thermal/Legendre/unit controls and false/stale-scope rejection.
Same-runtime fresh outputs are byte deterministic; cross-runtime nonzero
quantities use the locked1e-8 relative tolerance. No full interacting/formal/material result.

## Interacting method/source branch and conditional algebra diagnostics

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Interacting_Method.py.
[Contract](Data/03_Research/fluid_core_o2_interacting_method_contract.json),
[card](CORE_O2_INTERACTING_METHOD_ADMISSION.md),
[artifact](Result/artifacts/fluid_core_o2_interacting_method_audit.json).

Prelocked before first execution: unchanged selected .002/.004,mu1.28 and
separate .2,mu.3 normal control, source definitions, Gauss64/128/256, cutoff60,
gap/functional1e-8, Legendre relative1e-8, last-order mass/pressure1%, three
rational I_minus witnesses, off-shell coefficient negatives and scale2 E2/E4.
First execution156/156 passes without repair, refit or target relaxation.
Four tests cover twice-fresh same-runtime bytes, source/preregistry hashes,
exact branch messages, independent normal controls, exact residual tradeoff,
alternate scale3, and false gates/admissions/changed states/thresholds/stale
prior source rejection before computation. Cross-runtime nonzero normal
quantities use relative1e-8. No condensed state or dynamic Ward is executed.

## SD01 conditional gHF functional diagnostics

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Gapless_Functional.py.
[Contract](Data/03_Research/fluid_core_o2_gapless_functional_contract.json),
[handoff](CORE_O2_GAPLESS_FUNCTIONAL_HANDOFF.md),
[artifact](Result/artifacts/fluid_core_o2_gapless_functional_audit.json).

The contract/card/addendum hashes were locked before execution. Exact Fraction
and polynomial arithmetic requires zero residual without a relaxed tolerance.
Three off-shell symmetric Q/phi points, steps 1/7 and 1/11, rational 3/5-4/5 rotation,
three I_minus witnesses and scale 2 are unchanged. Detected negatives omit or
halve DeltaV2, misuse its symmetric off-diagonal derivative, or identify frozen
and external responses. The last negative is a symbolic obligation, not a vertex
calculation. First execution 186/186 is immutable; four additional mean-field
checks and two archive guards produce 192/192 with 81 fresh input hashes.
Four regressions cover independent expanded-coordinate/Richardson variations,
extra rational rotation, old/new residual tradeoff, repeatability and false/stale
scope rejection. Temperature integrals and all sixteen admissions remain false;
all ten method gates remain NOT_STARTED. Required central audit failures are
reported separately in the handoff and must not be renamed into physics passes.

## SD02 exact stationary-source derivation controls

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Core_O2_Stationary_Source_Response.py.
[Contract](Data/03_Research/fluid_core_o2_stationary_source_response_contract.json),
[result](Result/artifacts/fluid_core_o2_stationary_source_response.json),
[handoff](CORE_O2_STATIONARY_SOURCE_HANDOFF.md).
91 inputs were prelocked before first execution. First 147/147 source/result are
retained; actual quotient-solving/rejection and two archive guards give 149/149
with 95 input identities. Exact Fraction residuals, steps 1/7 and 1/11, one
quadratic fixture, three symmetric variations and energy scale 2 are unchanged.
Four tests use independent expanded pressure/cofactor/tensor expressions,
quotient-domain rejection and false/stale scope guards. A handwritten first-test
cross expectation was corrected from its polynomial expansion; its original
source is retained. No verifier/contract/threshold changed for that correction.
Topic13 artifacts are pinned predecessor scope, not numerical reruns. All sixteen
admissions false and ten method gates NOT_STARTED; no physical benchmark/state.

## SD03 exact material-frame and fixed-pressure handoff checks

Command: python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Material_Frame_EOS_Handoff.py.
[Contract](Data/03_Research/fluid_material_frame_eos_handoff_contract.json),
[result](Result/artifacts/fluid_material_frame_eos_handoff.json),
[handoff](MATERIAL_FRAME_EOS_HANDOFF.md).
108 identities were prelocked. First154/156 failed two entropy-current reference
targets omitting convective charge. Original source/result retained. Correct
J_N,total=n*u+j_N target and two new omission negatives plus archive guards give
160/160 with112 fresh identities. No EOS/source equation, fixture, threshold,
physical input or calibration changed. Four independent regressions cover
pressure Taylor/tangent/Richardson and entropy derivative, total-current/frame,
covariance/unit factors, and archive/provenance/false or stale scope. All exact
checks use Fraction algebra; material covariance/scales and inputs remain null.
No physical heat/current, thermal solver, material benchmark or gate promotion.
