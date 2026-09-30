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
