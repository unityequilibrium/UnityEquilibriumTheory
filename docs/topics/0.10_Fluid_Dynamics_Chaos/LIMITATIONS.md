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
