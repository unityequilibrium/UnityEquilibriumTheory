# Topic 10 vector-state research contract

Date: 2026-09-30. Status: CANDIDATE_NORMALIZED_REFERENCE_ONLY.
Controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.

This contract addresses the missing state and mechanical work exchange after J01's
legacy gradient-map no-go. It is a proposed normalized extension of the existing
matter-space functional, with a separate incompressible-fluid reference. Its
instantaneous identities do not admit a UET fluid model or begin physical J04.

## State and frame

Use independent (C, Phi, Q, u) with div u = 0 and constant rho0 > 0.
C remains a lane-specific structural coordinate, not rho. Phi retains its
effective-response meaning. rho0 is a separate inertia coefficient.
Define D_t = partial_t + u dot grad and Q = D_t Phi. Core Pi keeps its existing
meaning: Pi = partial_t Phi = Q - u dot grad Phi. A uniform Galilean boost changes
Pi but leaves Q invariant. Renaming Pi to the material rate would change ontology.

The transform back to the Core Pi coordinate also changes its evolution:
partial_t Pi = partial_t Q - partial_t u dot grad Phi
               - u dot grad(partial_t Phi).
Thus the old fixed-frame Pi RHS cannot be reused at nonzero velocity unchanged.
At an instant u = 0 gives Q = Pi. Recovering parent Eulerian evolution also
requires partial_t u = 0, a frozen-flow algebraic control. Merely starting at
rest does not enforce this: the solenoidal scalar force can accelerate the fluid.

R_gen and R_obs are derived records with no feedback. Legacy I is excluded.
This is a candidate state contract awaiting Core review, not a new universal ontology.

## Source-linked functional and conditional derivation

The polynomial and chemical potentials come from
[canonical Core implementation](../../core/02_equations/matter_space/uet_matter_space.py)
and [parent specification](../../core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md).
The parent implementation is normalized and 1D; extending the continuum gradients
to 2D is a stated research assumption, not a tested Core runtime migration.

~~~text
f = a_C C^2/2 + b_C C^4/4 + kappa_C |grad C|^2/2
  + a_Phi Phi^2/2 + b_Phi Phi^4/4 + kappa_Phi |grad Phi|^2/2
  - g C^2 Phi/2
mu_C = a_C C + b_C C^3 - kappa_C Delta C - g C Phi
mu_Phi = a_Phi Phi + b_Phi Phi^3 - kappa_Phi Delta Phi - g C^2/2
D_t C = M_C Delta mu_C + J_C
D_t Phi = Q
tau_Phi D_t Q + Q = -M_Phi mu_Phi + J_Phi
rho0 D_t u = -grad p + div(2 eta D(u)) + f_rev + F_ext
D(u) = (grad u + grad u^T)/2
f_rev = mu_C grad C + mu_Phi grad Phi
~~~

Independent fluid inertia, incompressibility, Newtonian stress, and material
advection are constitutive assumptions. The scalar functional alone does not
derive them. The reversible force follows conditionally from cancellation of
scalar advective work with mechanical power, not from a microscopic UET action.
A pressure gradient and other work-orthogonal forces are not uniquely fixed
by a global energy identity.

The standard constant-density Navier–Stokes/Cahn–Hilliard reference has separate
velocity and capillary stress; see [Abels, Garcke and Grün, Section 1,
equations (1.1)–(1.4)](https://arxiv.org/abs/1104.1336).
Our material Phi/Q pair is an additional proposal. Unequal densities require
additional mass/momentum flux terms and are outside this contract.

Translation invariance gives the explicit stress relation
f_rev = grad f - div(kappa_C grad C tensor grad C
                    + kappa_Phi grad Phi tensor grad Phi).
On a periodic domain it has zero mean force. Its solenoidal part can be nonzero;
an independent u can represent the J01 vortical target. This does not demonstrate
that a UET scalar state produces that target dynamically.

## Energy, source power and dissipation

~~~text
E = integral [f + rho0 |u|^2/2 + h Q^2/2] dx; h = tau_Phi/M_Phi
D = integral [M_C |grad mu_C|^2 + Q^2/M_Phi + 2 eta D(u):D(u)] dx
P = integral [mu_C J_C + Q J_Phi/M_Phi + u dot F_ext] dx
dE/dt + D - P = 0
~~~

For smooth periodic fields and constant positive coefficients, integration by
parts cancels scalar advection against u dot f_rev, cancels mu_Phi Q against
the material oscillator work, and eliminates pressure/advection power.
Closed scalar mass requires integral J_C = 0. Mean fluid momentum changes only
by integral F_ext. The shear convention uses 2 eta D:D, not eta D:D.

Positive b_C and b_Phi bound the polynomial below, even for negative a_C.
Young's inequality with epsilon = b_C/8 yields
f_local >= (b_C/8) C^4 + (a_C/2) C^2
         + (b_Phi/4) Phi^4 + (a_Phi/2 - g^2/(2 b_C)) Phi^2.
Each quartic-plus-quadratic term has lower bound
-min(B,0)^2/(4 A), where A > 0. This is an energy lower bound,
not convexity, equilibrium stability, PDE well-posedness or global regularity.

E and D here are normalized ledger quantities. In an SI isothermal realization,
free-energy dissipation would need an explicit heat-bath/work ledger before
being interpreted as heat or entropy. It is not a complete isolated thermal
energy model or a second-sound equation.

## Dimensional proposal

Let q_C and q_Phi denote the separately declared field units, L length,
t time and e energy per volume. The formal dimensional targets are:

| Quantity | Dimension required in an SI realization |
| --- | --- |
| a_C, b_C, kappa_C | e/q_C^2, e/q_C^4, e L^2/q_C^2 |
| a_Phi, b_Phi, kappa_Phi | e/q_Phi^2, e/q_Phi^4, e L^2/q_Phi^2 |
| g | e/(q_C^2 q_Phi) |
| M_C (conserved) | q_C^2 L^2/(e t) |
| M_Phi, tau_Phi, h | q_Phi^2/(e t), t, e t^2/q_Phi^2 |
| Q and Pi | q_Phi/t with distinct frame definitions |
| rho0, eta, p, f_rev | e t^2/L^2, e t, e, e/L |

The SI table is a 3D density convention. A 2D slice integral would be per unit
out-of-plane length until a measured thickness is specified.
No numeric normalization or material coefficient is calibrated by this table.
No He-4 eta, alpha, theta_T, Z or e0 is imported. SI and physical observable
admission remain blocked.

## Verification and next controller

The [machine contract](Data/03_Research/fluid_vector_state_research_contract.json)
locks synthetic coefficients, grids 16/32/64, tolerances and sources before
the first run. The initial control had cancelling net mechanical work and failed
negative-control sensitivity; version 2 adds a mixed harmonic and preserves the
failed diagnostic and unchanged tolerances. This amendment followed a preview,
so the controls are not a blind preregistration. The audit uses the canonical Core formula expressions through
AST extraction, not a successful Core import. It checks independent directional
derivatives, the stress gauge, closed/open instantaneous energy and momentum
ledgers, incompressibility, material-frame transformation, and missing-force,
wrong-sign and rate-misidentification negative controls. It also rejects an
invalid coefficient domain and nonzero closed scalar source.

It has no timestep solver, temporal convergence, external data or SI outputs.
A passing diagnostic cannot satisfy any blocked upstream UET admission gate.

For Topic 13, the useful handoff is the reciprocal work and frame contract.
Full-He-II second sound still requires separate normal/superfluid relative
velocities, entropy/temperature dynamics, matched EOS/transport, uncertainty and
a primary frequency-specific protocol. Q is not an entropy flux, and Phi is
not temperature.

Next: Core must assess/admit or reject the independent momentum origin and the
material-frame state transform. Only then select an admitted operator and the
time-discrete verification scope for J04.

The conserved scalar retains C/Phi ontology; neither momentum nor Q is admitted
by passing this reference test. The unchanged Eulerian Pi RHS is tested as a
negative control against the explicitly transformed coordinate RHS.
