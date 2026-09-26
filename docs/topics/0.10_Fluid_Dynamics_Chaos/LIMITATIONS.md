# Limitations

- The benchmark comparator is simplified and not a full survey of fluid solvers.
- Reported speedups are environment-sensitive.
- Current repository benchmark evidence does not justify proof-level Navier-Stokes claims on its own.
- No external CFD/turbulence validation dataset is packaged as a primary gate yet.
- Finite stress-test output is a useful diagnostic, not a proof of global regularity.

## J01 representability boundary (2026-09-26)

The periodic-control audit finds a scoped no-go for nonzero incompressible vortical targets
under the current 2D constant-scalar-mobility map u=-M grad(C): the represented field is
curl-free, and a periodic harmonic potential yields only zero velocity. This is not a
no-go for other UET realizations, variable/singular mobility, different boundaries, or a
separately registered vector/momentum state. The current 3D engine has scalar C,I evolution
but no vector velocity/momentum/pressure state.

The source audit finds the derived mobility overwritten by constructor value 0.5, while
PhysicalProperties.mobility is unused; the bridge constant is labeled a placeholder and
the velocity units remain unclosed. The default physical kappa cap is inactive for the
recorded default grid. A C floor of 0.01 is present, but clip-event counts are unknown
because the solver was not stepped. Importing the engine was blocked in the configured
runtime by missing scipy; the audit's manufactured controls do not depend on that import.
See Result/artifacts/fluid_state_velocity_representability_audit.json.
