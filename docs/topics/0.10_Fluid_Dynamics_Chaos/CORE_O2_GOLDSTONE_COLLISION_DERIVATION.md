# Core O(2) low-energy Goldstone collision channel

Date: 2026-10-01. Research-core; J01/J02 microscopic preparation only.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
This card and the contract/registry are recorded before numerical execution.

## Scope and prior evidence
The current local ideal two-fluid reference assumes entropy conservation. Its
two acoustic pairs are conditional hydrodynamic eigenmodes, not automatically
the upper radial and lower Goldstone quasiparticle branches. Topic 13 already
has scalar/gain-loss, screened condensed contact and lane-specific Kubo records.
Reuse those records as historical scoped evidence, rather than rebuilding or
equating their mode-space relative eigenvalue with hydrodynamic thermalization.
The archived condensed sound-speed field and source formula precede the current
rationalized spectrum. They are not overwritten or used as a current derivative.

Use the current fixed-Phi matter action with positive canonical mass m_c^2 =
m_eff^2/Z and lambda_c = lambda/Z^2, natural units hbar=c=k_B=1,
metric +--- (explicitly converted from the Core convention).
Matter phase theta and canonical fluctuation varphi are not response Phi.
Here response coupling is zero. No live response or material assignment.

## Leading action and interactions
Let r=mu^2-m_c^2>0, B=3mu^2-m_c^2 and
X=(mu+theta_t)^2-|grad theta|^2.
Algebraically eliminating the tree radial amplitude gives P(X)=(X-m_c^2)^2/
(4lambda_c). This neglects radial-gradient/higher-derivative interactions.
L2=B/(2lambda_c)*theta_t^2-r/(2lambda_c)*|grad theta|^2.
varphi=sqrt(B/lambda_c)*theta; c_s^2=r/B.
L3=g3*(varphi_t^3-varphi_t*|grad varphi|^2),
g3=mu*sqrt(lambda_c)/B^(3/2) [E^-2].
L4=g4*(varphi_t^2-|grad varphi|^2)^2,
g4=lambda_c/(4B^2) [E^-4].
P,L have dimension E^4; varphi E; derivatives E^2.
These are leading tree interactions, not the complete finite-T effective action.

Current source tree dispersion:
E_-^2=k^2+B-sqrt(B^2+4mu^2*k^2), evaluated with source rationalization.
E_-=c_s*k+gamma*k^3+O(k^5);
gamma=mu^4/(sqrt(r)*B^(5/2)) [E^-2] is positive.
Positive curvature admits a small non-collinear 1->2 phase space. Exactly
linear dispersion has an endpoint degeneracy and is not a substitute for the
curved on-shell calculation.

For k=p+q and E_k=E_p+E_q, the leading cubic vertex (irrelevant overall sign):
M=g3*[6E_k E_p E_q-2(E_k p.q+E_p k.q+E_q k.p)] [E].
Permutation factors are independently checked by polarization of P's cubic
term. The derivative vertex vanishes if a full external four-momentum vanishes.
Combining this leading vertex with the full tree dispersion is an asymptotic
diagnostic; finite-k corrections do not claim matched higher-derivative vertices.

## Decay normalization and limits
With canonical external states and identical daughters (factor 1/2!):
Gamma_occ=1/(32*pi*E_k*k) integral_0^k dp
[p*q/(E_p*E_q*v_g(q))]*|M|^2.
Solve E_q=E_k-E_p without angular clipping, reconstruct
cos(theta)=(k^2+p^2-q^2)/(2kp), check both triangle and energy constraints.
Gamma_occ [E] is occupation/probability decay; pole-amplitude damping is
gamma_pole=Gamma_occ/2. It is not a counterflow relaxation time.
At T=0 and k->0,
Gamma_occ/k^5=3*g3^2*(1-c_s^2)^2/(80*pi*c_s^2)
=3lambda_c*mu^6/(20*pi*r*B^4) [E^-4].
For mu=m_c+mu_NR, mu_NR/m_c->0:
g_NR=lambda_c/(2m_c^2), n_NR=2m_c^2*mu_NR/lambda_c,
gamma_pole/k^5 -> 3/(640*pi*m_c*n_NR).
This is a nonrelativistic leading-coefficient correspondence, not a liquid-He
density conversion or replication of a rigorous many-body theorem.

## Collision balance versus thermalization
For a Bose-equilibrium bath, each on-shell 1<->2 triad obeys
N_k(1+N_p)(1+N_q)=(1+N_k)N_p N_q.
The linearized entropy variable has positive quadratic form
sum W*N_k(1+N_p)(1+N_q)*(phi_k-phi_p-phi_q)^2.
Energy and momentum are invariants; phonon number is not.
A finite disconnected triad diagnostic retains extra null modes and cannot
establish a continuum spectral gap, vector heat-current relaxation or a
hydrodynamic frequency window. No fitted Gamma_rel, entropy-conservation
derivation, finite-T rate, Landau channel, full 2<->2 kernel or SI Kubo is emitted.

## Locked verification and next controller
The JSON fixes source identity, weak-coupling exploratory values .01/.001
(separate from the earlier lambda=1 ideal controls), momenta .02/.01/.005,
Gauss orders 48/96/192, tolerances and negative controls before execution.
Retain every first-run failure; do not relax thresholds or tune parameters.
Next: connected condensed collision/current projection and interacting
self-consistent thermal state, including allowed processes and convergence,
before identifying a transport time and testing omega*tau << 1.
Nonlinear/live-Phi, nonrelativistic/SI/material and independent He-II sources
remain separate obligations. Physical J04/J05/J06 remain unexecuted.

## Selected primary-source correspondence
- [Son, hep-ph/0204199v2](https://arxiv.org/html/hep-ph/0204199v2):
  equations 14-20, 25 and the finite-T/higher-derivative exclusions. EOS-derived
  leading phonon vertices; no claim that this supplies finite-T hydrodynamics.
- [Dereziński, Li and Napiórkowski, 2024](https://link.springer.com/article/10.1007/s10955-024-03328-2):
  equations 13-22, selected convex-kinematics/Fermi-golden-rule discussion and
  factor-two pole-versus-decay convention. Distinct dilute Bose model; selected
  leading-coefficient comparison only, not a theorem transfer to UET/He-II.
