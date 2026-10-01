# Formula Audit: 0.10 Fluid Dynamics and Chaos

## Scope

This registry covers the current primary benchmark gate and the formulas that directly
support it: the embedded simplified Navier-Stokes comparator, the UET master-equation update,
the UET 2D fluid mobility bridge, the stress-test stability check, and the speedup metric.
Many exploratory fluid scripts exist, but they are not promoted here unless a verifier
artifact ties them to data, thresholds, and units.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `FD-NS-DIFFUSION` | `u <- u + dt * nu * Laplacian(u)` and same for `v` | `Proof_Turbulence_Benchmarks.SimplifiedNSSolver.step` | `u`, `v` dimensionless velocity arrays in embedded benchmark; `dt` solver time units; `nu` dimensionless benchmark diffusivity; `dx`, `dy` unit-square spacing | `benchmark_anchor`; embedded simplified comparator | `checked local comparator formula` | primary speed baseline | Comparator is not a full CFD solver; speedup can overstate practical CFD advantage if treated as external validation. | Add external CFD validation cases and compare against a documented solver/version. |
| `FD-NS-POISSON-JACOBI` | `p_ij <- 0.25*(p_E+p_W+p_N+p_S)` repeated 20 times | `Proof_Turbulence_Benchmarks.SimplifiedNSSolver.step` | `p` dimensionless pressure-like array | `benchmark_anchor` | `checked local comparator formula` | primary speed baseline cost driver | Fixed 20 Jacobi sweeps are an implementation choice and can bias speed comparison. | Record solver tolerance/sweep sensitivity and competitor solver variants. |
| `FD-UET-MASTER-STEP` | `C,I <- UETMasterEquation.step(C, dt, dx, I)` | `Proof_Turbulence_Benchmarks.time_uet_once`; `docs/core/uet_master_equation.py` | `C`, `I` dimensionless fields; `dt` solver time units; `dx=1/grid_size` | `topic_derived_relation` from core UET master equation | `checked local implementation relation` | candidate solver under primary benchmark | If master-equation internals change, speed/stability result may change without topic docs noticing. | Hash core master-equation file in artifact and add formula-level regression tests. |
| `FD-UET-FLUID-LAPLACIAN` | `Laplacian(C) = d2C/dx2 + d2C/dy2` by central differences | `Engine_UET_2D.compute_laplacian` | `C` dimensionless in benchmark; `dx`, `dy` grid spacing | `standard numerical identity` | `identity / checked local implementation` | engine formula registry, not primary artifact gate | Unit-square benchmark may hide physical-unit behavior. | Add physical-unit benchmark with declared density, viscosity, Reynolds number, and boundary conditions. |
| `FD-UET-MOBILITY` | `u = -M * grad_x(C)`, `v = -M * grad_y(C)` | `Engine_UET_2D.step` | `u`, `v` velocity-like arrays; `M` mobility scale; `grad(C)` per length | `heuristic_bridge` via `FLUID_MOBILITY_BRIDGE / mu / rho` when physical properties are used | `heuristic bridge` | engine diagnostic and future physical benchmark path | Mobility bridge can be mistaken for a validated physical constitutive law. | Source-lock physical fluids and validate velocity/pressure fields against external cases. |
| `FD-PHYSICAL-KAPPA` | `kappa = min(mu/rho, stability_limit)`; `stability_limit = 0.4/(dt*(1/dx^2+1/dy^2))` | `Engine_UET_2D._derive_uet_parameters` | `mu` Pa s; `rho` kg m^-3; `mu/rho` m^2 s^-1; `stability_limit` numerical diffusion bound | `source_locked_physics_relation` for kinematic viscosity plus numerical stability cap | `checked local implementation relation` | future physical-unit gate | Stability cap can silently move from physical viscosity to numerical constraint. | Artifact should record whether cap is active for each physical run. |
| `FD-STABILITY-GATE` | `stable = all(isfinite(C_stress))` after stress update | `Proof_Turbulence_Benchmarks.run_benchmarks` | Boolean gate over dimensionless stress field; stress seed `1e6` benchmark amplitude | `benchmark_anchor` | `checked local benchmark gate` | primary stability gate | Finite output does not prove boundedness or smoothness for arbitrary initial data. | Add norm growth metrics and repeated stress amplitudes; separate theorem work from benchmark work. |
| `FD-SPEEDUP` | `speedup = median(t_NS_trials) / median(t_UET_trials)` | `Proof_Turbulence_Benchmarks.run_benchmarks` | runtimes in seconds; speedup dimensionless | `topic_derived_metric` | `metric definition` | primary PASS/FAIL metric; threshold `> 2.0` | Environment jitter or comparator choice can shift the pass result. | Record hardware/runtime metadata and repeated runs across grid sizes. |

## Current Artifact Link

- Primary command: `python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/02_Proof/Proof_Turbulence_Benchmarks.py`
- Artifact: `Result/artifacts/fluid_benchmark_validation.json`
- Current gate: speedup greater than `2.0` and finite stress-test output.
- Claim boundary: internal implementation benchmark only.

## Current Formula Boundary

- The benchmark gate can support speed/stability wording for the embedded comparator and
  configuration.
- It cannot support external CFD accuracy, arbitrary-turbulence generalization, or
  Millennium-problem closure.
- Paper-facing claims require external validation datasets, physical-unit Reynolds-number
  cases, and theorem-target assumptions separated from implementation benchmarks.

## Chaos Diagnostic Formula Addendum

Chaos diagnostic formulas remain separate from the speed gate and constitutive-transport claims.

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `FD-CHAOS-TANGENT` | `delta_x[n+1] = D F(x[n]) delta_x[n]` | `docs/core/uet_dynamical_stability.py` | tangent state in the declared normalized lane | analytic Jacobian of the declared evolution | checked against central finite difference | primary Benettin/QR estimator | numerical instability or an undeclared source JVP is treated as physical sensitivity | admit state-dependent sources only with an explicit JVP |
| `FD-CHAOS-SPECTRUM` | `lambda_i = lim_T log(s_i)/T` | same module and `Research_Chaos_Method_Validation.py` | inverse normalized time; logistic exponent per iteration | standard dynamical-systems diagnostic | validated on linear, logistic, and Lorenz controls | diagnostic method gate | Lyapunov exponent is confused with the free-energy Lyapunov function | retain the terminology and evidence-class separation |
| `FD-CHAOS-RESOLUTION` | `lambda_res = max(delta_dt, delta_dx, 2 SE_block, delta_method)` | same module | same inverse-time lane as `lambda` | preregistered diagnostic gate | checked implementation contract | sign-resolution gate | arbitrary epsilon or one unconverged run controls the classification | add topic-specific spatial/statistical budgets |

## J01 representability addendum

For the current constant scalar mobility map u=-M d_x(C), v=-M d_y(C), the continuum
curl vanishes for every smooth C. On a periodic domain, requiring incompressibility also
imposes Laplacian(C)=0; integration by parts then gives grad(C)=0, so the only represented
incompressible velocity is zero. This is a mathematical consequence of the declared map,
not a no-go for all UET models. The finite-difference control, source identity, units
limitation, and exact scope are recorded in
Result/artifacts/fluid_state_velocity_representability_audit.json.

The source audit also records that the computed mobility is reset to 0.5 in the 2D
constructor, the bridge constant is an unverified placeholder, and velocity units are not
closed. The formula remains a heuristic gradient bridge, not an admitted momentum law.

## Candidate vector-state formula addendum (2026-09-30)

The [candidate registry draft](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_vector_state_addendum.json)
and [derivation card](VECTOR_STATE_RESEARCH_CONTRACT.md) inventory a conditional
normalized scalar/fluid reference; they are not merged into the central equation
registry or admitted physical Core gates.

| Relation | Origin and boundary |
| --- | --- |
| Q = D_t Phi; Pi = Q - u dot grad Phi | Coordinate identity within a proposed material-frame state |
| tau D_t Q + Q = -M_Phi mu_Phi + J_Phi | Constitutive ansatz; UET action origin open |
| rho0 D_t u = -grad p + div(2 eta D(u)) + f_rev + F_ext | Independent incompressible momentum reference; rho0 is not C |
| f_rev = mu_C grad C + mu_Phi grad Phi | Conditional reciprocal-work derivation from the parent functional |
| f_rev = grad f - div(gradient stress) | Conditional translation/stress identity |
| dE/dt + D - P = 0 | Normalized instantaneous work identity; no physical heat/entropy closure |
| partial_t Pi = partial_t Q - partial_t u dot grad Phi - u dot grad(partial_t Phi) | Required Eulerian coordinate transform; unmodified parent RHS is a negative control |

At u=0, Pi=Q at that instant. Parent Eulerian evolution also requires
partial_t u=0; nonuniform scalar force can invalidate that frozen-flow assumption.
The source-linked scalar formulas, synthetic inertia/viscosity and all exclusions
are hashed in the reference audit. Bounded polynomial energy is not global
regularity. Next controller: vector momentum origin and material-frame admission.
## Conditional vector action and canonical rate audit

Candidate registry: ../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_variational_addendum.json;
derivation: VECTOR_VARIATIONAL_ORIGIN.md. The scalar density is source-linked,
while rho0 fluid inertia, material h Q^2/2 and volume preservation are declared
reference assumptions. The conservative equations follow conditionally from
these choices. They are not derived from a microscopic UET action.
Q=D_t Phi and Pi=partial_t Phi remain distinct. At fixed Pi, partial L/partial u
is rho0 u+h Q grad Phi, and partial L/partial Pi=h Q. The inverse fibre map and
Hamiltonian agree with the existing normalized energy reference. The formal
SI dimensions are targets with no measured scale. Dissipative/thermal terms
and material observable mapping remain blocked. The registry is a separate
candidate addendum and has not been merged into the central admitted inventory.

## Second-sound mode-class addendum

[Registry candidate](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_second_sound_mode_addendum.json)
and [derivation](SECOND_SOUND_MODE_ELIGIBILITY.md) record F0-F4 before code.
The current scalar characteristic polynomial has one simple zero root and a
finite-gap pair at k=0; lambda_slow=-M_C(A-B^2/D)k^2+O(k^4).
Linear scalar force is a pressure gradient; solenoidal shear modes decouple.
This is an analytic reference branch exclusion with sampled numerical controls,
not an all-UET theorem or formal kernel proof. Even-in-k matrix parity alone is
insufficient; the out-of-contract massless undamped scalar provides a wave control.

Separate standard reference: c2^2=(rho_s/rho_n)T s^2/c_p, with s,c_p specific per
mass. Its reciprocal coefficients satisfy H_T a=H_w b=rho_s s.
The positive perturbation availability is not full SI internal energy or entropy.
No C=mass, Phi=T, Q=entropy flux assignment is made. Numerical coefficients are
synthetic; EOS/transport and independent He-II measurement remain unadmitted.

## Compressible two-fluid and thermodynamic derivative reference

The [separate registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_two_fluid_eos_reference.json)
records a standard comparator, not a new admitted UET equation.
e(rho,sigma) is a material internal-energy target; mu_mass=e_rho and T=e_sigma.
Gibbs pressure gives the mass/entropy mixed longitudinal mode matrix.
Its positive availability weight makes H M symmetric and yields two sound pairs.
The c^4 quartic retains compressibility/thermal expansion; the reduced c2 relation
is exact in the declared decoupling limit only.

The SVP-to-fixed-pressure chain rules and heat-capacity difference come from
thermodynamic differentials with explicit held variables. NIST C_s/path expansion
cannot silently supply c_p/c_v or alpha_p/kappa_T. Local synthetic witnesses
demonstrate this missing derivative freedom. Source-locked SI conversion factors
do not repair it. The full Core Helmholtz/entropy/internal-energy Legendre mapping
and superfluid phase/stiffness correspondence remain unperformed admission tasks.

## Source conversion audit: TN1334 candidate (2026-09-30)

The source card records the material ontology, held variables and SI conventions
before code. c_p-c_v=T alpha_p^2/(rho kappa_T), c_adiabatic^2=c_p/(c_v rho kappa_T)
and Gamma=alpha_p/(rho c_v kappa_T) are standard thermodynamic reference identities.
The last ratio is dimensionless; the first has J/(kg K), and the second m^2/s^2.
The source's phi is Gamma, not the UET Phi field. Source alpha*T and P*kappa are
dimensionless products, not directly SI coefficients. Printing-interval
compatibility is not physical uncertainty or a proof of the material EOS.
No new central equation or UET scalar-to-material correspondence is promoted.

## Standard entropy-coordinate covariance addendum

[HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md](HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md)
records F0-F4 before code: material sigma_star=sigma+a*rho, EOS/conjugate/Hessian
chain rule, pressure invariance, transformed entropy current and superfluid force,
and SI dimensions of a. Registry:
[standard entropy-reference addendum](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_entropy_reference_addendum.json).
This is a standard-reference coordinate relation, not a new UET core equation.

The [116-check result](Result/artifacts/he4_entropy_source_reference_audit.json)
checks explicit flux/force assembly against similarity and availability congruence.
Wrong unmodified shifted-entropy dynamics can pass positive work but change poles.
No physical a is fitted or assigned; s_star cannot be substituted into the
unmodified entropy-speed expression as a physical absolute entropy. All C/Phi/Q/R
ontology, SI admission, microscopic origin and physical phase/response restrictions
remain unchanged.

## Conditional Core common-flow composition correspondence

[The new F0-F4 contract](CORE_O2_COMMON_FLOW_COMPOSITION_CONTRACT.md) records
natural-unit charge/entropy density, phase stiffness E^2, momentum inertia E^4,
fixed-Phi ensemble and a separate superfluid phase. It derives the conditional
target w=T*s+mu*n=mu^2*f_s+chi_n from one ideal relativistic current/stress state.
Paper phase-gradient sigma and prior entropy-density sigma are distinct.
Registry: [O(2) common-flow addendum](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_common_flow_addendum.json).

Current source tree phase stiffness and formal Doppler response fail this
composition target at the declared condensed points; the 69-check execution
audit does not convert that FAIL into admission. Tree T=0 inertia and long-wave
Goldstone/EOS controls pass. No finite-T stiffness is fitted or emitted from
the identity. A consistent common flow-dependent effective action/current/stress
and entrainment derivation remains required, followed by nonrelativistic,
material/SI and physical-response correspondence. No C/Phi/Q/R relabeling.

## Fixed-Phi phase-flow Hessian correspondence

[Derivation card](CORE_O2_FLOW_HESSIAN_DERIVATION.md) and the separate
[unmerged registry addendum](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_flow_hessian_addendum.json)
record phase ontology, canonical normalization, metric/frame conventions and
units before computation. psi is the matter phase; Phi is fixed response,
and phase-gradient sigma is distinct from entropy-density sigma.

The action-derived quartic kernel yields implicit E_h/E_hh and an independent
thermal correction to -P_hh, with E^2 stiffness units. Multiplying by mu^2
gives E^4 inertia units. Neither enthalpy nor the proxy defines that correction.
The current scalar test passes, but no full tensor Ward identity, stress or
entrainment audit, material mass density, Kubo coefficient or physical second
sound derivation is claimed. The overall physical controller is unchanged.

## Local scalar-pressure tensor, entrainment and ideal modes

[Derivation](CORE_O2_LOCAL_IDEAL_TWO_FLUID_DERIVATION.md) and the separate
[unmerged registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_ideal_modes_addendum.json)
record the inverse-temperature vector, phase covector, density/temperature
Hessian, metric convention and natural dimensions before numerical execution.

Current/stress follow local scalar source/metric variation; the conjugate
two-current map exposes symmetric local entrainment. The thermal EOS Hessian
is differentiated independently from both Gaussian modes. Charge, momentum
and phase integrability plus ASSUMED ideal entropy conservation give the
linear operator. Positive quadratic energy and reciprocal local work pass.

The signed thermal pressure derivative is not the normal charge coefficient.
No phase meaning is assigned to Phi. Local ideal-mode eligibility is not
thermalization, a complete nonlinear action, a physical material normal density,
He-II speed or SI observable correspondence. Overall physical admission stays open.

## Tree derivative phonon collision channel

[Derivation](CORE_O2_GOLDSTONE_COLLISION_DERIVATION.md) and the
[separate registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_goldstone_collision_addendum.json)
record matter-phase ontology, canonical normalization, dimensions and derivation
class before execution. L3/L4 follow the tree P(X); curvature follows the current
source spectrum. The canonical identical-daughter phase-space convention gives
occupation Gamma and pole Gamma/2; the low-k/NR coefficients are cross-checked.

This leading asymptotic channel is distinct from screened contact mode-space
Kubo, ideal collective mode damping and heat-current relaxation. Bose triad
entropy positivity does not prove connected thermalization. No live Phi,
complete finite-T vertex, nonlinear operator, SI mapping or Core unlock.

## Shared kinetic collision form versus physical heat current

[Card](CORE_O2_GOLDSTONE_GALERKIN_DERIVATION.md) and
[unmerged registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_goldstone_galerkin_addendum.json)
record Bose gain/loss variables, identical-daughter normalization, natural
Gram/collision dimensions and source-frame constraint before execution.
Whole-action scaling confirms G:E5,Q:E6, generalized rates:E1 and R:E4.
Raw collision invariants are checked before source reduction.

The leading cubic process is integrated over shared scalar/vector functions;
it is not all-channel/self-consistent interacting thermal completion.
E*v_g is a kinetic quasiparticle current, not automatically T^0i-mu*j^i.
Constrained finite response/time has failed basis/cutoff acceptance and no
continuum gap, physical frame/SI, two-fluid damping or dependency admission.

## Stable radial Hilbert trial spaces and unchanged cubic collision form

[Card](CORE_O2_GOLDSTONE_VECTOR_REFINEMENT.md) and
[topic-local numerical registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_vector_refinement_addendum.json)
record radial amplitude unitsE, actual GramE5, collisionE6, responseE4 and
basis-timeE-1. The same leading cubic event form is retained; momentum is the
first invariant and only the source/state is reduced to its zero-momentum frame.

Same-span coordinate correspondence isolates roundoff from trial enrichment.
SOFT order35 includes EVEN order17's highest radial degree33; nested variational
response checks pass. Finite Hilbert admissibility is not a continuum-domain or
gap proof. The physical kinetic-to-material heat-current mapping stays open.

## Enrichment, smooth Gram limit and near-collinear coordinate identity

[Trial card](CORE_O2_GOLDSTONE_INFRARED_TRIALS.md),
[trial registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_infrared_trials_addendum.json),
[geometry card](CORE_O2_GOLDSTONE_INFRARED_GEOMETRY_REPAIR.md) and
[geometry registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_infrared_geometry_addendum.json)
record seed/epsilon momentum unitsE and unchanged G:E5,Q:E6,R:E4.
Heron d-form/direct soft-vector placement is an algebraic event identity.
Float/Decimal parameter consistency is bounded; no new interaction is introduced.

The physical velocity/vertex/measure/Bose/gain-loss AST is unchanged even though
the explicit geometry implementation's full AST differs. Smooth finite-cutoff
Gram dominated convergence is a local mathematical lemma, not collision-form
or continuum-current convergence. Physical heat-current/frame remains unadmitted.

## Selected continuum measure/domain and compact soft noncoercivity

[Card](CORE_O2_GOLDSTONE_CONTINUUM_FORM.md) and
[unmerged correspondence addendum](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_continuum_form_addendum.json)
record radial Gram density w:E2 and event density W:E2, distinct from quadrature
weights; bounded amplitude/epsilon:E, g3:E-2, prefactor:E-3, integralW:E4,
G:E5,Q:E6 and Rayleigh:E1. Whole-action scale2 diagnostics pass independently.

The original cubic vertex equals -2g3 times the on-shell F(E) difference by
exact rational polynomial algebra. Measure majorants and compact-bump/Gram
projection inequalities derive conditional finite-K domain/no-uniform-gap
statements. Their floating evaluation is not interval certification, Lean
verification or independent math review. No new primary Core equation or
physical parameter is added. Source-weighted current bounds and microscopic
heat-current/frame/material correspondence stay open.

## Selected kinetic-current weighted response upper formula

[Card](CORE_O2_GOLDSTONE_CURRENT_BOUND.md),
[unmerged registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_current_bound_addendum.json)
and [artifact](Result/artifacts/fluid_core_o2_current_bound_audit.json)
record topic-derived analytic constants eta:E-2,sigma:1,nu:E-2,beta/alpha:E1,
C_P:E-1,D:E-2,wmax:E2,B_upper/B_J:E6,b:E5,Q:E6 and R_upper:E4.
The response is sup b^2/Q; pre-execution unit review excludes dimensionally
incompatible subtraction of b and Q. Whole-action energy scale2 checks pass.

Origin: conditional variational derivation from the same selected curved
source/cubic measure, two-patch Jensen estimate and exact momentum frame.
Wrong polynomial coefficient and unprojected-null source are negative controls.
No fitted constant, primary Core equation, formal/interval/independent proof,
strong continuum inverse or physical heat-current/material mapping is added.
The explicit finite upper formula remains too loose for a useful error claim.

## Action-normalized tree spatial currents and generator distinction

[Card](CORE_O2_MICROSCOPIC_CURRENT_WARD.md),
[unmerged registry](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_current_ward_addendum.json)
and [artifact](Result/artifacts/fluid_core_o2_current_ward_audit.json) record
fields:E, amplitude:E, covariant gradients:E2, averaged quadratic action:E4,
wave-action density:E3, charge current:E3, stress flux:E4, J_N:E0,
J_E/J_G:E1 and projected source Gram:E5. Scale2 checks pass.

Origin is the same selected tree action and Noether/stress/flow source. Raise
both stress indices with the inverse metric and translate conjugate phase.
J_E=J_G+mu*J_N=k and J_G=E*v_g hold for the two positive reference modes.
P_perp J_G=-mu P_perp J_N recovers the old lower-branch projected source.
Naive thermodynamic-charge advection, omitted charge and wrong index/conjugation
are explicit negative controls. Spatial correspondence does not establish
density backreaction, interacting Ward identities or physical heat/material frame.
No primary Core equation, formal certificate or physical admission is promoted.
