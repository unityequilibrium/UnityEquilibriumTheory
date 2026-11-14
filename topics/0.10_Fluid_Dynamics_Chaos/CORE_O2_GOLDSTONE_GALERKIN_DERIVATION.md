# Goldstone Galerkin collision and projected energy-current reference

Date: 2026-10-01. Research-core; J01/J02 preparation, not physical J04/J05/J06.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Card, units, registry and numerical targets are locked before execution.

## Reuse and scope
Extend the previous leading tree Goldstone 1<->2 channel. Topic13 already
integrates normal-state scalar 2<->2 invariant Galerkin forms. Its finite
collocation/projected contact operators are historical comparators, not a
condensed derivative-vertex replacement. The new form uses shared scalar and
vector functions evaluated on every exact event: no disconnected node graph,
interpolation, added diagonal width, posterior collision projector or fitted rate.
Finite basis rank is not proof of connectivity/completeness of the continuum.

Use the same canonical m_c^2=m_eff^2/Z, lambda_c=lambda/Z^2, fixed response,
matter phase and low-energy tree vertex/curved spectrum from
[the previous derivation](CORE_O2_GOLDSTONE_COLLISION_DERIVATION.md).
Natural hbar=c=k_B=1. Exploratory lambda=.01 and T=.002/.004 are new kinetic
reference controls, not recalibration of lambda=1 ideal modes or liquid helium.
No live Phi, finite-T self-energy or matched higher-gradient vertices.

## Linearized three-phonon form and normalization
Let N(E)=1/(exp(E/T)-1), delta f=N(1+N)*phi.
For each parent k and identical daughters p,q:
R=N_k(1+N_p)(1+N_q)-(1+N_k)N_p N_q,
delta R=N_k(1+N_p)(1+N_q)*(phi_k-phi_p-phi_q).
Use dGamma_0(k;p) from the previous canonical decay calculation; it ALREADY
contains 1/2! for identical daughters. Do not insert another factor of two.

G_ab=integral d^3k/(2pi)^3 N_k(1+N_k) F_a(k)F_b(k).
Q_ab=integral d^3k/(2pi)^3 integral dGamma_0(k;p)
 N_k(1+N_p)(1+N_q) Delta F_a Delta F_b.
Q is the full gain/loss quadratic form for this selected 1<->2 process:
a tagged mode can be a parent or a daughter across the integral. No separate
daughter Landau contribution should be appended to this already symmetrized form.
This is not all physical scattering channels or the complete thermal action.
The identity (1+Np)(1+Nq)/(1+Nk)=1+Np+Nq checks the parent linearization convention.
Q>=0 and exact energy/momentum invariants follow eventwise; phonon number does not.

Scalar basis: (E,T,T(k/K)^2,T(k/K)^4,...), energy first.
Vector basis for each Cartesian direction: F_j=k_i(k/K)^(2j), momentum first.
Analytic isotropic averaging gives <Delta V_a,i Delta V_b,i>=Delta V_a.Delta V_b/3.
Thus one scalar block and three identical vector blocks have four expected
conservation nulls in the finite basis. Cross scalar/vector blocks vanish by parity.
Cholesky Gram whitening gives L=G^-1/2 Q G^-1/2, without altering Q.
All features have dimension E; G [E^5], Q [E^6], L [E].
No absolute rate cutoff, clipping or artificial diagonal regulator is permitted.

## Current source, frame and response
The kinetic single-phonon energy-current feature is
J_i=E*v_g*hat{k}_i=k_i*a(k),
a(k)=1-2mu^2/sqrt(B^2+4mu^2*k^2).
It is NOT automatically the material heat current T^0i-mu*j^i:
condensate/charge/frame/source correspondence remains to be derived.

Project the SOURCE onto zero total kinetic momentum using the same equilibrium
inner product: a0=<k_i,J_i>/<k_i,k_i>, J_perp=J-a0*k_i.
This frame constraint is distinct from projecting an incorrectly conserving
collision operator. Verify raw Q*energy=Q*momentum=0 before source reduction.
For exactly linear E=c*k, J=c^2*k and J_perp=0. A conserved-momentum contribution
must not be counted as a dissipative heat-current coefficient.

In the equivalent basis F'_j=F_j-G_0j/G_00*F_0 (j>=1):
G_red=G_jl-G_j0*G_0l/G_00; Q_red=Q_jl; b_j=<F'_j,J_perp>.
R_basis(omega)=b^T*(Q_red-i*omega*G_red)^-1*b [E^4].
R_basis(0) is a finite variational current response, not SI conductivity.
tau_basis=R_basis(0)/<J_perp,J_perp> [E^-1] is a source-weighted basis
diagnostic, not a global collision gap or physical hydrodynamic relaxation time.
Solve this constrained linear system independently of its Gram-whitened
spectral form; no arbitrary singular-matrix pseudoinverse or fitted width.

## Locked controls and acceptance boundary
T=.002/.004, mu=1.28, lambda=.01; k cutoffs=20/30/40*T/c.
Parent and daughter Gauss orders24/48/72; feature orders2/3/4/5.
Separate order, cutoff and basis sweeps. Whole-action energy scale2 checks
G~E^5,Q~E^6,current response~E^4 and finite rates~E^1.
Source projection, invariants, PSD, balance and normalization are structural
controls. Refinement of R/tau at 1% and matrix/rate control at 1% are separate
measured acceptance gates; a structural PASS cannot conceal a failed target.
Retain the first diagnostic and source if a repair is necessary; never relax targets.

Negative controls: parent-loss-only form breaks conserved modes; unprojected
current overlaps momentum; constant linear current has no dissipative source.
Record raw rank, expected nulls, source representation error, basis conditioning,
natural energy cutoffs, frequency response and cutoff/basis effects.
A finite-basis positive spectrum is not a continuum spectral-gap theorem.

Next: resolve any measured basis/cutoff/controller, then complete interacting
finite-T state, allowed additional scattering/matched vertices and physical
charge/condensate heat-current/frame correspondence. Assess soft-mode/continuum
current response before using omega*tau<<1 or damping collective two-fluid modes.
Nonlinear/live response, material/SI and independent He-II sources remain open.

## Primary reference role
[Manuel, Sarkar and Tolos, arXiv:1407.7431v2](https://arxiv.org/pdf/1407.7431v2),
selected equations10-23, supports the kinetic current/conservation constraints
and polynomial variational method. Their neutron model has downward curvature
and uses binary collisions; its scattering channels, gap and conductivity
values are not transferred to our upward-curving O(2) reference.
Source metadata fixes v2 (2014-11-22); the PDF internal typesetting date differs.
Earlier leading-action and Beliaev source roles remain as recorded.
