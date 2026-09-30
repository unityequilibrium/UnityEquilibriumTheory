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

## Conditional vector/material-rate reference audit

Run python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Fluid_Vector_State_Contract.py.
The normalized instantaneous 2D periodic controls use Fourier derivatives at
N=16/32/64, restricted arithmetic extraction of the canonical Core scalar
polynomial/potentials, and an explicit independent momentum constitutive reference.
Core modules are not imported, and no trajectory is advanced.

The [contract](VECTOR_STATE_RESEARCH_CONTRACT.md) derives conditional reciprocal
force and the Eulerian/material rate transform. Checks cover directional energy
and Pi-coordinate derivatives, pressure projection, stress gauge, closed/open
mass/momentum/work balances, Galilean transformations, frozen-flow and initial-rest
distinction, coefficient/source rejection and failure-sensitive controls.
The initial cancelling-work control is reproducible with --initial-control-diagnostic
and intentionally exits 1. Version 2 follows that preview and is not blind
preregistration; tolerances are unchanged. --output supports isolated test outputs.
No physical J04 or Topic 13 mode is implemented.
## Conservative variational reference

Use VECTOR_VARIATIONAL_ORIGIN.md and
Data/03_Research/fluid_vector_variational_origin_contract.json for the separate
action/configuration assumptions. The reversible C field is materially advected;
Phi has independent internal evolution. The displacement/internal variations
give a conditional conservative vector equation and material oscillator from
one reference action. Action finite differences perturb the admissible tangent
and recompute Q from the perturbed Phi and u; the path is not an EOM solution.
Independent fibre derivatives hold Eulerian Pi fixed to distinguish canonical
m=rho0 u+h Q grad Phi from mechanical rho0 u. The Legendre test is before full
incompressible Poisson reduction. A local Q-chain test is required because an
omitted Q transport term is invisible in integrated kinetic work. No trajectory,
physical action assignment, dissipative closure or operator admission occurs.

## Long-wave second-sound eligibility

Use SECOND_SOUND_MODE_ELIGIBILITY.md and
Data/03_Research/fluid_second_sound_mode_eligibility_contract.json.
Linearize the parent canonical chemical potentials at a synthetic stable uniform
equilibrium. Compare the scalar matrix's characteristic polynomial, simple
zero-root diffusive expansion and finite-gap sector, plus pressure-projected
transverse velocity. Compare to an independently reduced standard two-fluid
counterflow operator with positive quadratic wave availability.

Halve continuum wavenumbers from 0.2 to 0.003125. These symbols are neither
fixed-box eigenmode measurements nor time trajectories. Remove uniform Doppler
advection; retain a massless undamped scalar wave outside the candidate assumptions.
Use Hermitian magnitude norms for complex work matrices. The first preview's
invalid real-only norm is retained; added post-preview sign-error controls detect
both imaginary work defects and real unstable poles. All tolerances are unchanged.
A failed verifier leaves exclusion unresolved. A passing reference exclusion
requires separate two-fluid state admission before physical J02/J05/J06.

## Compressible two-fluid/EOS comparator

Use TWO_FLUID_STATE_EOS_REFERENCE.md and
Data/03_Research/fluid_two_fluid_eos_reference_contract.json. Construct a standard
ideal longitudinal matrix from mass/normal-entropy transport, total pressure
momentum and the superfluid chemical-potential equation at rest.
The positive internal-energy Hessian and common/relative kinetic decomposition
supply a reciprocal quadratic-work symmetrizer. Both acoustic branches are
compared with an independently derived thermodynamic quartic.

Finite differences check Gibbs pressure and constant-pressure specific heat.
A periodic local work-flux calculation checks the operator; wrong entropy-carrier
and superfluid-sign controls must fail. Zero expansion admits the reduced
zero-mass-current subspace; finite expansion explicitly drives its missing momentum.
Two different isothermal compressibilities reproduce the same synthetic local
SVP tangent yet change the EOS/modes. No material rows or Core scalar equations
are numerically mapped into this standard comparator.
