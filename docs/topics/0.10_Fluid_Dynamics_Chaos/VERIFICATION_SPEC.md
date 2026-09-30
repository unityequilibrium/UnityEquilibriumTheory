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
