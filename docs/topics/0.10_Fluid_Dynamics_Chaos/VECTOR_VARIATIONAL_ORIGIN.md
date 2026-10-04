# Conditional variational origin of the Topic 10 vector reference

Date: 2026-09-30. Candidate/reference scope only. Physical controller remains
vector_momentum_constitutive_origin_and_material_frame_admission_open.

## F0-F4 record before implementation

Parent: [vector-state contract](VECTOR_STATE_RESEARCH_CONTRACT.md) and canonical
[scalar functional](../../core/02_equations/matter_space/uet_matter_space.py).
This separate action candidate does not rewrite the parent contract or admit a
Core equation. It asks whether one declared conservative generator can reproduce
the reversible subset of that proposal. The functional, fluid inertia and material
attachment are independent assumptions until a physical correspondence is supplied.

Ontology: C is a structural scalar, not mass density; Phi an effective response,
not temperature/entropy. u is independent constant-density incompressible velocity,
rho0 a separate positive inertia coefficient. Q=D_t Phi is the material rate;
Pi=partial_t Phi=Q-u dot grad Phi retains its Eulerian Core meaning.
R_gen/R_obs stay derived with no feedback. Legacy I is not substituted.

Units: all numerical checks are normalized 2D periodic reference controls.
The parent formal SI table is a target, not a calibration. An SI Lagrangian density
would have energy-per-volume units and the action energy*time; h=tau/M_Phi has
energy-density*time^2/Phi-unit^2. Canonical p_Phi has energy-density*time/Phi-unit,
and h Q grad Phi has momentum-density units, matching rho0 u. A 2D slice requires
thickness before a total SI action interpretation.

Primary method references:
[Holm, Marsden and Ratiu, Section 6 / Theorem 6.1](https://arxiv.org/abs/chao-dyn/9801015)
for continuum displacement variations; and
[Holm, Trouve and Younes, Sections 3-4](https://arxiv.org/abs/0806.0870)
for independently evolving internal variables under a flow.
Only the kinematic method is used. Image-matching boundary/momentum conditions
from the second paper are not imposed as fluid physics.

## Declared action and admissible variations

On a periodic domain with smooth fields and constant positive rho0,h, choose a
volume-preserving flow map and a materially evolving internal scalar. In the
reversible sector C is materially advected: D_t C=0. Phi is internally dynamical,
not a frozen advected scalar. With f from the canonical parent functional:

~~~text
D_t = partial_t + u dot grad
Q = D_t Phi; h = tau_Phi/M_Phi
S = integral dt dx [rho0 |u|^2/2 + h Q^2/2 - f(C,Phi,grad C,grad Phi)]
~~~

Let xi be a divergence-free flow displacement and chi an independent internal
scalar variation, both zero at temporal endpoints. With the stated bracket sign:

~~~text
delta u = partial_t xi + u dot grad xi - xi dot grad u
delta C = -xi dot grad C
delta Phi = chi - xi dot grad Phi
delta Q = D_t chi - xi dot grad Q
~~~

The last identity follows from differentiating Q=partial_t Phi+u dot grad Phi.
Treating delta Phi=chi without its transport correction is not this variation.
These formulas also satisfy the linearized D_t C=0 constraint.
Endpoint variations of Phi and the flow map vanish; Q itself need not have zero
variation there. Linear perturbations in the numerical audit are tangent tests,
not exact finite-epsilon volume-preserving trajectories.

## First variation and conservative equations

Using mu_C=delta Omega/delta C and mu_Phi=delta Omega/delta Phi:

~~~text
delta S = integral [rho0 u dot delta u + h Q delta Q
                    - mu_C delta C - mu_Phi delta Phi] dt dx
A_xi = -rho0 D_t u + mu_C grad C + mu_Phi grad Phi
       - grad(rho0 |u|^2/2 + h Q^2/2)
A_chi = -(h D_t Q + mu_Phi)
delta S = integral [A_xi dot xi + A_chi chi] dt dx
~~~

Integration by parts uses periodic space, zero endpoint xi/chi and div u=0.
For all admissible xi and chi, stationarity gives, up to a pressure gauge:

~~~text
rho0 D_t u = -grad p + mu_C grad C + mu_Phi grad Phi
h D_t Q = -mu_Phi
D_t Phi = Q; D_t C = 0
~~~

This is a conditional conservative derivation from the declared action.
The action choice does not derive incompressibility, inertia, material attachment,
or a microscopic UET origin. M_C diffusion, eta stress, oscillator damping,
external sources and physical FDT/entropy closures are outside this conservative
action; their existing reference ledger remains a separate constitutive proposal.

## Canonical rate momenta and Legendre transform

At fixed C,Phi,gradients and independent Eulerian rate Pi:

~~~text
p_Phi = partial L/partial Pi = h Q
m = partial L/partial u = rho0 u + p_Phi grad Phi
H = m dot u + p_Phi Pi - L
  = |m-p_Phi grad Phi|^2/(2 rho0) + p_Phi^2/(2 h) + f
  = rho0 |u|^2/2 + h Q^2/2 + f
~~~

m is an unprojected representative of the canonical Eulerian velocity derivative,
before incompressibility reduction. Not every canonical m is an independently
admissible constrained state. This fibre Legendre transform is not a construction
of the full reduced Poisson structure. m is not automatically a new physical
mass density or a separately measured total mechanical momentum. The displacement
variation removes its field exchange term up to gradients to give the mechanical
rho0 u equation above. No Noether identification of integral m is claimed.

The rate Hessian in (u,Pi), with a=grad Phi, is
[[rho0 I+h a tensor a, h a],[h a^T,h]].
Its Schur complement is rho0 I and determinant h rho0^d, so the rate-to-momentum
Legendre map is invertible for positive rho0,h. This is not convexity of f,
equilibrium stability, PDE well-posedness or global regularity.

## Verification design locked before the first run

The [machine contract](Data/03_Research/fluid_vector_variational_origin_contract.json)
records 16/32/64 spacetime periodic controls, central steps 1e-3/1e-4/1e-5,
identity tolerance 1e-9, directional-derivative tolerance 1e-7, and negative-control
sensitivity floor 1e-8. Tests compare the action finite difference to both the
direct and integrated-by-parts variation, independently check the Q chain rule
and linearized scalar advection, rate momenta, Hamiltonian and Hessian.

The manufactured path obeys kinematic constraints but is not an equation-of-motion
solution. Its nonzero first variation is expected, not a stationarity failure.
Neither a PDE trajectory nor a formal-kernel proof is produced.

Negative controls omit delta Phi's flow transport, omit material Q transport, or
replace m by rho0 u. Each must change the checked derivative by more than the
locked floor. An insensitive negative control cannot yield a passing audit.

## Handoff to Core and Topic 13

The new evidence can narrow the conditional conservative-origin question, but
physical assignment and constitutive coefficients remain unadmitted. Core must
assess the action/configuration assumptions, material correspondence and SI
observable mapping before J04/J05. No physical dependency unlock is requested.

For Topic 13 the candidate contributes only a work/rate/canonical-coordinate
interface. It supplies no normal/superfluid relative motion, entropy transport,
second-sound mode, Kubo coefficient or independent measurement. Q is not entropy
flux and Phi is not temperature. Existing source-ancestry overlap stays open.
