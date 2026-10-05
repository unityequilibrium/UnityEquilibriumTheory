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

## Offline He-II EOS source conversion

Use HE4_FIXED_CONSTRAINT_EOS_SOURCE_CARD.md and
Data/03_Research/he4_tn1334_fixed_constraint_eos_source_candidate.json.
Match the liquid first row to the parallel derivative table; preserve raw
printed tokens. Convert MPa to Pa by 1e6, J/(g K) to J/(kg K) by 1000, divide
alpha*T by T and P*kappa_T by P in Pa. Density is already SI.
The source Gruneisen symbol is not the UET response field. Transport blanks
stay null.

The offline verifier uses Decimal arithmetic at precision 60 and endpoint
enclosures from an assumed symmetric half-last-displayed-unit printing rule,
including T. Check interval compatibility of c_p-c_v, classical adiabatic
sound squared and the Gruneisen relation. These boxes are diagnostic printing
enclosures, not row uncertainties or a probabilistic covariance. Failures
must be retained without relaxing the rule. Deliberately wrong unit, derivative,
phase and blank-as-zero interpretations must be detected. No material
two-fluid/UET mode prediction or EOS parameter fit occurs.

## Entropy-source and reference-coordinate follow-up

Use [HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md](HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md)
before mixing thermodynamic source values. Its new package records separate
fountain and calorimetric ancestry, source units, explicit Table 8.5 integration
convention and the primary publication-date correction. Prior TN1334 rows and
Topic 13 sources are read only. Compare only central values at nominal printed
temperatures; no interpolation, reference-offset fit or physical source test.

For the unchanged standard two-fluid base, declare sigma_star=sigma+a*rho.
Transform the EOS conjugates/Hessian, entropy current AND superfluid force;
independently assemble local flux rows and compare with matrix similarity.
Work congruence, pressure, capacities and characteristic speeds must agree.
The shifted-entropy unmodified operator is a different model: its own energy
check can pass. Local entropy/phase defects and pole comparisons are required.
The 116 checks and four tests are synthetic/reference/source checks, not an
admitted UET action, physical trajectory, SI He-II response or full nonlinear closure.

## Current Core source-function common-flow probe

[CORE_O2_COMMON_FLOW_COMPOSITION_CONTRACT.md](CORE_O2_COMMON_FLOW_COMPOSITION_CONTRACT.md)
locks the conditional relativistic common-flow target w=mu^2*f_s+chi_n.
Execute named source-verbatim AST definitions in isolated explicit-config
namespaces: reciprocal response/mass, fixed-Phi quasiparticle pressure/spectrum
and formal Doppler response. Source/function hashes identify what actually ran;
historical static artifacts provide boundary context only, not a fresh native
Core runtime or validation of their old source-path metadata.

Compute fixed-Phi pressure derivatives with a separate five-point wrapper.
Sweep quadrature order and cutoff separately, plus derivative steps; keep the
composition target PASS/FAIL separate from successful diagnostic execution.
Normal-gas enthalpy and tree phase/charge/Goldstone controls establish sensitivity.
At the declared condensed points, formal Doppler proxy plus tree stiffness
fails the common-flow target. Do not force f_s=(w-chi)/mu^2 and call it derived.
The next action is a common finite-T flow effective-action/current/stress
derivation, not fitting a stiffness or importing He-II sound speeds.

## Independent phase-flow pressure curvature

[The flow Hessian derivation](CORE_O2_FLOW_HESSIAN_DERIVATION.md) declares the
normal-rest ensemble, canonical field normalization and phase-source units
before execution. Expand the O(2) quadratic action with r=mu^2-h^2-m_eff^2/Z
and mixing mu*E+h*k_z. At h=0 the quartic roots must match current Core sources.

Compute f_s=-P_hh from implicit mode derivatives, including both the mode
curvature and occupation curvature terms. Separately integrate both positive
finite-flow quartic roots and use a five-point second pressure derivative.
Differentiate only thermal pressure and add tree curvature analytically.
Do not use enthalpy or the static proxy in the phase-curvature calculation.

Then independently compare mu^2*f_s+chi_perp_qp with T*p_T+mu*p_mu. Keep the
earlier tree-only mismatch as a negative control; detect pure-Doppler and
omitted-occupation-curvature errors. Orders/cutoffs, angles and source steps
are locked and swept separately. A scalar target PASS does not derive all
Ward identities, stress/entrainment or physical two-fluid dynamics.

## Source-derived local two-current operator

[The local derivation](CORE_O2_LOCAL_IDEAL_TWO_FLUID_DERIVATION.md) keeps
matter phase and UET response distinct. Independently integrate E_mu/E_mu_mu
for n,s and the EOS Hessian; compare thermal derivatives with fixed-bound
five-point differences and separate order/cutoff refinements.

Construct a declared second-order local scalar P(T,y,x). Differentiate its
phase sources for current and its metric at fixed beta/p for stress. Check
finite source/metric derivatives, Lorentz/rotation transformations and the
two-current conjugate/entrainment map. These checks apply to this local model,
not the untruncated microscopic action in arbitrary flow.

Build (delta n,delta s,g,v_s) from charge, entropy, momentum conservation and
phase integrability. Entropy conservation is explicitly an ideal local-equilibrium
assumption. Independently assemble the generalized chemical/temperature/velocity
operator. Check positive work Hessian, local real/complex energy cancellation,
coordinate/pole agreement and both acoustic pairs. Detect wrong entropy velocity,
missing T*s inertia and reversed phase-force sign. No speed is fitted.

## Microscopic 1->2 channel before thermalization

[The leading collision card](CORE_O2_GOLDSTONE_COLLISION_DERIVATION.md) reduces
the tree radial field algebraically and normalizes the phase fluctuation.
Polarization checks cubic permutation factors; current source-verbatim
Goldstone dispersion supplies curvature, on-shell roots and group velocity.
Integrate canonical two-body phase space with the identical-daughter factor
at three orders/momenta and two explicitly exploratory weak couplings.

Reconstruct triangles using factored area and direct soft-daughter placement,
without angular clipping. Separate occupation decay from pole damping.
Check the nonrelativistic coefficient, derivative soft limit, off-shell Bose
balance failure, energy/momentum invariants, number nonconservation and a
positive disconnected entropy form. Its extra null modes prohibit identifying
a physical relaxation time. Existing Topic13 scalar/contact/Kubo lanes are
reviewed as bounded prior evidence, not transferred to hydrodynamic velocities.

## Shared cubic Galerkin form and constrained current response

[The new card](CORE_O2_GOLDSTONE_GALERKIN_DERIVATION.md) reuses the prior
canonical identical-daughter decay measure and Bose detailed balance to
linearize the complete gain/loss form for the selected 1<->2 process.
Parent and daughter roles enter the same event integral; no extra daughter
term or symmetry factor is appended. Current spectrum/inverse-root checks and
parent linearization factors guard this normalization.

Use exact isotropic averaging of scalar and Cartesian-vector polynomial
features. Check raw energy/momentum invariant columns before Gram whitening;
then constrain only the source/state to zero total kinetic momentum.
Solve the finite reduced Q-i*omega*G system and its independent whitened
spectral form. Execute the linear-dispersion zero-current limit and detect
parent-loss-only invariant failure. Separate quadrature, cutoff, basis and
source-representation targets; preserve failed refinement despite structural PASS.

## Stable shared vector coordinates and soft variational refinement

[The new card](CORE_O2_GOLDSTONE_VECTOR_REFINEMENT.md) keeps momentum first,
records full two-pass weighted projection/beta coefficients and evaluates the
same recurrence at off-grid parent/daughter momenta. Actual Gram is computed,
not overwritten; no collision projector, interpolation or fitted width is added.
Compare EVEN order5 against the immutable raw implementation through an
independent polynomial coordinate transformation of G/Q/source and response.

EVEN spans k*polynomial(k^2/K^2). SOFT adds constant radial amplitude and powers
of k/K; the single-point angular nonsmoothness is Bose-Hilbert admissible.
This is a trial enrichment, not an assumed solution asymptote or matter phase.
Principal shared-bank subspaces check nested variational response growth.
Source representation, kernel conditioning, within-family refinement and
independent-family agreement remain separate acceptance obligations.

## Independent enriched and smooth infrared trials

[HYBRID](CORE_O2_GOLDSTONE_INFRARED_TRIALS.md) orthogonalizes seeds
k,T,EVEN1..N-2 with a recorded seed transform and shared off-grid evaluation.
HYBRID18 contains EVEN17 and is contained in SOFT35. Their discrete variational
response ordering passes; it is not a continuum response upper bound.

Replace only the soft seed by T*k/sqrt(k^2+epsilon^2) for epsilon>0, keeping
event integration limits and interaction unchanged. The Cartesian feature is
smooth at the origin; its epsilon->0 convergence in finite-cutoff Bose Gram
norm follows by dominated convergence. The collision-form domain needs a
separate argument. Epsilon and parent/daughter quadrature sweeps remain distinct.

[Geometry repair](CORE_O2_GOLDSTONE_INFRARED_GEOMETRY_REPAIR.md) evaluates
Heron factors using the positive on-shell excess and places the soft vector
directly. Decimal60 repairs only gaps below128 machine-epsilon*k.
The original floating q/energy/measure/occupations remain; raw geometry,
source parameter consistency, invariants and old matrix correspondence pass.

## Conditional finite-K collision form and compact soft sequence

The [card](CORE_O2_GOLDSTONE_CONTINUUM_FORM.md) derives a positive interior
vertex using the exact on-shell cubic identity and increasing F(E)/E.
An integrable measure majorant gives finite Q for bounded vector trials;
explicit soft-set bounds prove smooth-seed approximation in both Gram and
collision norms. Radial/event a.e. pullbacks give the maximal-domain closure
argument; noncollinearity/positive event density identify the momentum null.

Project a smooth compact soft bump off momentum. Q is unchanged; its upper
bound is O(epsilon^2), while the projected Gram lower bound is O(epsilon).
Thus the selected form has no uniform positive vector Rayleigh gap.
Diagnostics evaluate the derived formulas, Gram quadrature64/128/256 and
pointwise original-kernel inequalities; they do not invert the full continuum
operator, certify intervals, or assign physical transport. Internal derivation
and independent mathematical verification remain distinct.

## Selected current dual bound without a uniform vector gap

[The card](CORE_O2_GOLDSTONE_CURRENT_BOUND.md) keeps the exact current
J=k*(d-dbar), where d=E*v/k-c^2 and dbar is the integral-defined momentum
projection. No material frame or fitted scattering width is inferred.
A lower phase-velocity derivative gives strict angle separation on two
disjoint-p patches. A lower derivative of F(E)/E gives a vertex lower bound;
Bose inequalities then give W*sin^2(Gamma)/p>=alpha>0 analytically.
A Jensen graph argument controls integral k^3|h-a_I|^2 by Q for h=A/k.
The finite source dual norm yields |b|^2<=R_upper Q and sup b^2/Q<=R_upper.
The ratio preservesE4 units; b:E5 and Q:E6 are not subtracted.

Unprojected current has a nonzero momentum overlap while Q[momentum]=0,
so exact source-frame annihilation is essential. The soft dual integrand is
O(k); this weighted estimate is distinct from the Bose Gram norm and does
not contradict the old no-uniform-gap result. Floating evaluations and
finite Gauss projection remain diagnostics, not interval/exact integral
certificates or a computed strong continuum inverse.

## Direct tree spatial Noether and energy-current correspondence

[The current card](CORE_O2_MICROSCOPIC_CURRENT_WARD.md) derives the quadratic
wave-action norm from the selected action. Source-verbatim matter functions
evaluate phase-averaged paired positive/negative wave amplitudes, using the
Core -+++ and conjugate-phase convention. Covariant-input stress indices are
raised before comparison. No whole Core runtime or source helper substitution
is used; selected definition hashes are recorded.

For both positive branches, independent flowing quartic-root differentiation
matches J_N=-partial_h E; direct source currents give J_E=k and
J_G=J_E-mu*J_N=E*v_g. Three phase orders, three amplitudes and two constant phases
give288 controls at16 mode points;36 finite-flow derivative controls also pass.
The lower-mode Bose momentum projection matches the unchanged old source at
Gauss64/128/256. These diagnose tree spatial identities, not certified integrals
or a material frame. Complete charge/energy-density condensate backreaction,
interacting Noether currents and heat/enthalpy/frame correspondence remain next.

## Leading mean density and condensate response

[Density derivation](CORE_O2_DENSITY_BACKREACTION.md) keeps rho independent
before varying the quadratic action. Its mean radial force and classical
curvature give delta_rho/A0^2=-(3a^2+1)/(4rho). Direct original Core action,
independently differentiated box/EOM, charge and stress are evaluated for raw
waves and shifted mean backgrounds. Polynomial extraction in A0^2 removes
higher amplitude terms; it does not solve the nonlinear travelling wave.

Both branches at16 points use192 source coefficient sets (four amplitudes each),
phase orders8/16/32 and phases0/.37. Forty-eight centered mu root derivatives
test corrected charge independently. Lower-mode Gauss64/128/256 thermal subset
uses the same central physical K during every mu/T derivative; a moving thermal
cutoff is not silently differentiated. Complete interacting state/source Ward,
material heat/enthalpy/frame and useful certified error remain next.

## Interacting method/source branch audit

Reuse original Core normal self-energy/thermal functional/vacuum-subtraction/
renormalized functional definitions through verbatim AST extraction, retaining
the exact prelocked source identities. Pure coordinate/weight memoization is
value-preserving; no solver equation or quadrature is replaced. Probe the same
selected condensate points and a separate synthetic normal control at orders
64/128/256 with each solver's own cutoff.

Use independent residual inputs and exact Fraction arithmetic for the
source-transcribed R_rho,R_Y,R_D,R_G identity, synthetic stationary/gapless
witnesses, off-shell wrong-coefficient negatives and E2/E4 scaling. No thermal
tadpole integral is inferred from these witnesses. See
[method card](CORE_O2_INTERACTING_METHOD_ADMISSION.md).

Selected Alford sections distinguish original stationarity, gapless constraint
and appropriate pressure; Pilaftsis/Teresi supplies a different constrained
method. Brown et al. was accessible only as author abstract/metadata and
motivates a separate dynamic-source gate. Neither a full-paper reproduction
nor a finite-density symmetry-improved implementation is reported.

## SD01 same-functional conditional variation

Use the [frozen gHF candidate](CORE_O2_GAPLESS_FUNCTIONAL_CANDIDATE.md) and
[completed handoff](CORE_O2_GAPLESS_FUNCTIONAL_HANDOFF.md): sparse exact polynomial
identities plus independent Fraction coordinate variations, rotations and unit
scaling. Derive h from the declared fixed-Q V_field and Sigma from V2 using the
symmetric off-diagonal variation convention. Synthetic tadpoles test conditional
static stationarity only. Retain the original Hartree comparator, correction
omission/half-normalization negatives and first execution. No thermal solver or
source-varied vertex is executed; SD02 remains planned and Topic 10 secondary.

## SD02 tensor and stationary source chain

The [locked derivation](CORE_O2_STATIONARY_SOURCE_RESPONSE.md) computes the full
symmetric-index derivative of SD01 Sigma_g and compares trace/traceless sectors
with Hartree. One exact synthetic quadratic functional discriminates frozen,
relaxed and direct-contact source Hessians through independent stationary
substitution/finite differences and coordinate/unit transformations. Actual
quotient solving rejects incompatible phase sources and singular domains.
This checks the conditional method, not a gHF thermal state or physical response.
Existing Topic13 source curvature is inspected/pinned without importing its
numeric result or changing its parent. See [handoff](CORE_O2_STATIONARY_SOURCE_HANDOFF.md).

## SD03 pressure-ensemble and material-frame chain

Use the [preregistered contract](MATERIAL_FRAME_EOS_HANDOFF_CONTRACT.md) and
[handoff](MATERIAL_FRAME_EOS_HANDOFF.md): exact derivative jets transform the full
stationary p(T,mu) Hessian into fixed-pressure specific entropy/c_p. Independently
check source/reference shifts, linear enthalpy heat subtraction and total-versus-
perturbation current. Rational SI Jacobians/covariance controls carry no physical
scale/noise assignment. Existing two-fluid quartic, normal-lane frame and material
source/protocol records are pinned at their own scopes, not numerically rerun.
