# Method

- 2D solver: `Code/01_Engine/Engine_UET_2D.py`
- 3D solver: `Code/01_Engine/Engine_UET_3D.py`
- Benchmark workflow: `Code/02_Proof/Proof_Turbulence_Benchmarks.py`
- Supporting research workflows: `Code/03_Research/`

Method boundary:

- Current repository evidence is benchmark-oriented.
- The topic should be described as an internal solver and benchmark program, not as a
  conclusive theorem package.
- The primary benchmark uses an embedded simplified Navier-Stokes-style comparator and a
  UET master-equation update under a fixed grid, step count, trial count, and timing statistic.
- The source-lock manifest records that this is an internal benchmark package and identifies
  the future need for external CFD validation cases.

## J01 periodic velocity-representability audit

Run python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_State_Velocity_Representability.py.
The script writes Result/artifacts/fluid_state_velocity_representability_audit.json.
It audits the current 2D/3D source with Python AST and uses periodic, smooth manufactured
fields with centered finite differences at grids 16, 32, and 64. The rotational target is
divergence-free and has nonzero vorticity; the verifier also projects it onto the discrete
scalar-gradient subspace and reports the best-fit residual.

The result is scoped to the legacy 2D map u=-M grad(C) with constant scalar mobility on a
periodic domain, and to the current 3D source surface. It does not run the UET engine,
test physical CFD accuracy, or approve an added velocity state. Runtime import probes and
unmeasured clipping counts are disclosed in the artifact.
