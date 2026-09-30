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

## Vector-reference boundary (2026-09-30)

The new (C, Phi, Q, u) package is a normalized constitutive candidate. Independent
momentum, incompressibility and material advection were assumed rather than
derived from a UET action. Reciprocal work constrains the force but does not
uniquely fix all possible work-orthogonal stresses. Pi remains partial_t Phi;
using the parent Pi RHS unchanged is inconsistent with this candidate's
material-rate dynamics in general.

The reference audit is instantaneous and uses resolved synthetic trigonometric
fields. Three grids demonstrate the identities on these fields, not PDE spatial
convergence, time stability, turbulence, global regularity or SI validity.
Canonical algebra is read statically; migrated Core runtime imports are not repaired.
The initial control failure and post-preview amendment are retained.

The SI dimension table has no material calibration; a 2D integral needs a physical
thickness before a total joule interpretation. Positive quartics bound the
polynomial below without proving convexity or a stable equilibrium. Normalized
free-energy loss is not heat/entropy or a complete isolated energy model.
Topic 13 still needs independent relative-fluid/entropy/temperature dynamics and
source-independent measurements; its current J02 rows have unresolved calibration
ancestry overlap. All required physical admission gates remain blocked.
## Variational-origin boundary

The conditional conservative action is an additional constitutive ansatz with a
volume-preserving flow and material internal scalar. Its first-variation
consistency does not show that Phi is physically attached to a fluid parcel or
that a microscopic UET reduction supplies this action. Diffusion, viscosity,
damping, heat/entropy/FDT and sources remain independently unclosed constitutive
questions. Canonical m is an unprojected rate derivative, not a new measured mass
or automatically the total physical momentum. The positive rate Hessian and
invertible fibre Legendre map do not prove equilibrium/PDE stability. The
manufactured spacetime path obeys kinematics but is not an EOM trajectory; 72
checks are reference identities only. Physical F2/F3/F4/F7/F8 remain blocked.

## Hydrodynamic second-sound exclusion boundary

The stable homogeneous, finite-gap, gamma>0 candidate cannot supply the rest-frame
long-wave counterflow acoustic pair. Changing finite unit scales or reinterpreting
the gapped oscillator's frequency does not repair that missing branch.
This excludes only the declared linearized branch; massless/undamped or critical
limits, nonlinear propagation, finite-frequency resonances and other UET states
are outside the result. Numerical symbols do not prove global PDE behavior.

The separate standard two-fluid controls are synthetic and use a low-expansion,
constant-pressure, zero-mass-flow reduction. They are not an admitted UET/He-II
model or full internal-energy/entropy/FDT closure. Real attenuation needs
state-matched conductivity, shear/bulk transport, relaxation and, where relevant,
mutual friction and boundary data; D_w is not measured normal viscosity.
The 123-check preview is invalid evidence; the repaired 139 checks include
post-preview harness controls and are not a blind preregistration.

## Two-fluid/EOS reference boundary

The 59-check standard comparator is ideal, longitudinal, linear and at zero mean
flow/counterflow, with positive normal/superfluid densities and EOS Hessian.
It omits vortices, full entrainment at finite counterflow, dissipation, full
nonlinear entropy/FDT and material frequency/geometry effects. The matrix
symmetrizer is not a global PDE or UET stability proof.

The local path witnesses demonstrate first-derivative underdetermination, not
that all experimental EOS data are insufficient or that a chosen EOS ansatz
cannot be calibrated. No real He-II corrections or mode speeds are calculated.
NIST saturation-path calorimetry and heat-integrated entropy are not independent
fixed-pressure inputs. A Core-to-material Helmholtz/entropy/internal-energy
Legendre map, independent superfluid response density and source-matched EOS,
protocol and covariance remain open. Physical J05/J06 stay unexecuted.

## He-II source-candidate admission boundary

The three TN1334 rows are calculated fitted-EOS values, not independent
experimental observations. Their fixed-variable derivatives can be used for
source/reference checks without equating an SVP path derivative to c_p or c_v.
The assumed printing boxes are not experimental errors. Global density
uncertainty estimates do not supply per-row errors for all derived quantities.

Exact EOS training/response overlap, the selected edition's absolute entropy
anchor, derivative covariance and primary response frequency/geometry/state
remain unresolved. Arp fits sound as well as thermodynamic data; its bibliography
does not establish which exact rows overlap. The TN1334 rho_s fit and calculated
second/fourth sound are not independent targets and are not ingested here.
Its classical adiabatic speed is not silently identified with the full mixed
two-fluid first-sound eigenvalue.

IR8474 explicitly excludes He-II; older NBS1029 code/data use T58 and fitted
Brooks-Donnelly ancestry, not a fresh independent validation source.
No frozen Topic 13 matching constant, physical Core equation or original
unassigned material requirement changed. Physical operator/SI/phase mapping,
transport, prediction and J05/J06 remain blocked.

## Entropy-reference transfer remains a material blocker

[The latest source/reference audit](Result/artifacts/he4_entropy_source_reference_audit.json)
establishes the Table 8.5 source integration convention and complete coordinate
covariance only. It does not resolve TN1334's entropy anchor or assign a physical
reference offset. Printed-temperature comparisons omit scale conversion and
physical uncertainty propagation and have no physical acceptance threshold.

Fountain-pressure measurements provide a distinct thermodynamic source family,
but recommended spline values are not new raw data or an independently locked
sound test. Calorimetric entropy shares the input heat-capacity ancestry; source
precision/accuracy is not row covariance. Full experimental geometry/protocol
and exact calibration/response split remain unresolved.

The source controller is
he4_entropy_integration_anchor_found_but_TN1334_reference_transfer_covariance_and_independence_open.
A partial entropy-coordinate substitution can preserve positive work yet alter
sound poles. Neither this diagnostic nor finding a zero-T integration convention
admits a physical Core entropy/phase/mass/SI map. J04/J05/J06 remain unexecuted.

## Core static pieces do not yet define one admitted two-fluid inertia

The [current source diagnostic](Result/artifacts/fluid_core_o2_common_flow_composition_audit.json)
rejects only the proposed identification chi_n=chi_perp_qp with unmodified
f_s_tree at the three declared condensed points. The normal branch controls
pass. A target FAIL is retained despite 69/69 execution/control checks passing.
Observed refinement spread is numerical stability evidence, not a rigorous
truncation/error bound or physical uncertainty. No full-temperature theorem.

The configurations use lambda=1, a declared Core control rather than an
established weak-coupling physical regime. No interacting/renormalized error
estimate, live Phi, complete master function/entrainment or full Core runtime
execution is supplied. Relativistic natural-unit enthalpy is not He-II SI mass
density; pressure-sector labels are not measured normal/superfluid fractions.

Candidate controller:
finite_temperature_phase_stiffness_and_normal_momentum_common_action_match_missing.
A consistent finite-T phase/current/stress and normal response is required.
Even a scalar target PASS would not admit the two acoustic modes, physical
Kubo/transport, material state/SI map or independent response protocol.
Prior physical/Core/Topic 13 gates and single-velocity exclusion remain unchanged.

## Phase-flow curvature narrows only a scalar correspondence gap

[The independent Hessian artifact](Result/artifacts/fluid_core_o2_flow_hessian_audit.json)
shows that a thermal phase correction from the new tree-reduced Gaussian-flow
kernel removes the prior shortcut's common-flow scalar defect at the three
declared controls. It does not show that all possible UET operators, all
temperatures or an interacting liquid material satisfy this relation.

The tree amplitude follows each phase invariant; no thermal gap equation,
self-energy, renormalized vacuum completion or uncertainty estimate for those
omissions is supplied. lambda=1 remains a computational control, not an
established weak-coupling physical regime. Two numerical curvature methods and
refinement evidence are internal checks, not external replication or formal proof.

Full stress/current/entrainment and longitudinal hydrodynamic modes from the same
ensemble, live Phi, nonrelativistic mass/charge matching, He-II SI state, Kubo
transport and an independent response protocol remain unadmitted. The earlier
tree-only FAIL is retained; no coefficient is fitted to enthalpy.
The overall material/frame controller remains unchanged; only the next candidate
task narrows to complete two-fluid current/stress/entrainment/mode correspondence.

## Local ideal modes do not establish a physical hydrodynamic window

[The local reference](Result/artifacts/fluid_core_o2_ideal_modes_audit.json)
has two real acoustic pairs under ideal local-equilibrium entropy conservation.
Gaussian quasiparticles alone do not establish collisions, relaxation times,
local equilibration or a physical frequency window. This added assumption is
machine-readable and cannot be counted as derived thermalization.

Current/stress variations refer to a local second-order pressure Taylor model
with independently sourced coefficients, not arbitrary nonlinear/interacting
finite-flow Ward completion. Entrainment is a local constitutive correspondence.
Live Phi, nonlinear dynamics, thermal gap/self-energy/vacuum completion,
dissipative tensors, Kubo transport and physical frequency/source matching remain
open. The declared lambda=1 controls are not an established weak-coupling material.

Natural n_n=n-mu*f is a conditional charge/current coefficient. It differs from
the signed thermal pressure-sector derivative and is not kg/m^3. The recorded
natural speeds are not He-II velocities or a physical Topic 13 response test.
Material/SI and independent thermodynamic/calibration/response ancestry remain
separate; no physical package, dependency, claim tier or Core gate is promoted.

## A phonon decay channel is not a two-fluid transport time

[The collision artifact](Result/artifacts/fluid_core_o2_goldstone_collision_audit.json)
uses a leading tree derivative vertex with the current curved tree spectrum;
finite-k numbers are asymptotic diagnostics without matched higher-gradient
vertices or a self-consistent interacting thermal state. Exploratory
lambda=.01/.001 does not recalibrate the previous lambda=1 ideal controls.

Only T=0 occupation/pole decay is emitted. Bose detailed balance at one
reference bath temperature tests the triad structure, not a computed finite-T
rate, full Landau/2<->2 kernel, or derived entropy conservation. Disconnected
triads have extra null modes: no continuum spectral gap/vector heat-current
projection/transport time or physical hydrodynamic frequency window is known.
Upper/lower quasiparticle branches are not the two ideal collective sounds.
No existing contact-channel Kubo value or archived sound-speed field is treated
as current physical two-fluid admission. Physical/material/SI gates stay open.

## Current response is not converged or physically matched

[The shared-basis artifact](Result/artifacts/fluid_core_o2_goldstone_galerkin_audit.json)
has four finite-basis nulls and positive dissipative subspaces, but finite rank
does not establish continuum connectivity or a spectral gap. Its selected
finite-T cubic gain/loss form uses tree energies/leading vertices without
self-consistent thermal self-energy or all additional scattering channels.

The kinetic E*v_g current constrained against momentum is not yet matched to
the full condensate/charge material heat current or hydrodynamic frame.
Finite natural response and source-weighted basis time are diagnostic quantities.
Last basis response changes18-19%; cutoff changes5-6% exceed the locked1%
acceptance targets. Neither value is an admitted transport coefficient,
thermalization time, frequency window or collective sound damping.
A nearly exact source expansion does not cure an unconverged collision solution.

## Stable coordinates do not close soft-mode or continuum convergence

[The vector refinement](Result/artifacts/fluid_core_o2_vector_refinement_audit.json)
resolves the raw Gram-conditioning ambiguity by same-span correspondence and
nearly unit Gram condition. SOFT within-family responses plateau, but EVEN
basis/cutoff targets and20.4462%/19.5268% cross-family differences fail1%.
These failures remain controlling despite all541 structural checks passing.

A bounded angular trial at k->0 has finite Hilbert norm; this does not prove
the collision solution's infrared domain, continuum finiteness or spectral gap.
The scalar block is reused from earlier evidence, not rerun in this vector pass.
Kinetic energy-current still lacks full condensate/charge heat-current/frame
matching, self-consistent thermal-state/all-channel completion and material/SI/
independent-source admission. No physical relaxation/damping time is assigned.

## Enriched finite targets pass; continuum and material heat-current stay open

[The new artifact](Result/artifacts/fluid_core_o2_infrared_trials_audit.json)
passes the predeclared HYBRID/SOFT/smooth finite targets at both low-T controls.
This narrows the old20% trial-space discrepancy through explicit soft enrichment;
it does not relabel the old EVEN/basis/cutoff failures or make all continuum
spaces equivalent. Finite polynomial nesting gives discrete variational ordering.

Smooth-seed dominated convergence proves Gram-norm approximation only. No
collision quadratic-form domain, continuum source-weighted upper/error bound
or spectral gap is established. The selected leading cubic channel remains
tree/kinetic, without full interacting thermal self-energy/additional channels.
Its source is not admitted condensate/charge heat current or a physical frame.
No material/SI coefficient, relaxation/damping time or two-fluid prediction.
