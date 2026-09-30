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
