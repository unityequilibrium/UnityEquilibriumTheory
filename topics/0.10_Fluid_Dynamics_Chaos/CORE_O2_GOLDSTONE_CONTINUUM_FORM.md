# Selected Goldstone continuum form domain and absence of uniform vector coercivity

Date: 2026-10-01. Conditional internal mathematical derivation, not formal Lean
verification, independent mathematical review or physical Core admission.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Previous controller: infrared_collision_form_domain_continuum_current_and_physical_heat_current_admission_open.
Inventory: existing [selected collision form](CORE_O2_GOLDSTONE_GALERKIN_DERIVATION.md),
[infrared trials](CORE_O2_GOLDSTONE_INFRARED_TRIALS.md), their current source/artifacts.
No primary Core equation, physical parameter or collision channel is added.

## Assumptions, ontology and units
Finite K>0, T>0, mu>0, lambda_c>0, r=mu^2-m_c^2>0, B=r+2mu^2.
g3=mu*sqrt(lambda_c)/B^(3/2), c_s=sqrt(r/B).
Keep exact lower tree dispersion, leading cubic vertex, Bose occupations and
identical-daughter measure. This is one selected model, not full liquid He-II,
all-channel interacting thermal completion or infinite-momentum validity.

A(k)*hat{k} is an isotropic vector trial, not matter phase or a new substance.
G[A]=integral_0^K w(k) A(k)^2 dk, w=k^2 N(1+N)/(6pi^2).
Q[A]=integral_0^K dk integral_0^k dp W(k,p)|Delta F|^2.
W includes the isotropic1/3 and the existing identical-daughter1/2! once.
A and its sup bound M have unitsE; k,p,q,K,T,epsilon:E; r,B:E2;
g3:E^-2; c_s:1; w:E2 (the discrete w*dk hasE3); W:E2;
G:E5, Q:E6, Q/G:E1. No SI coefficient or physical time is assigned.

## 1. Dispersion and vertex identities
E(k)^2=k^2+B-sqrt(B^2+4mu^2 k^2).
E(k)/k increases from c_s to at most1:
E^2/k^2=1-4mu^2/(B+sqrt(B^2+4mu^2 k^2)).
Hence c_s*k<=E(k)<=k and v(k)>=c_s.
Also v(k)<=1/c_s since v=(k/E)*(1-2mu^2/sqrt(...)).
Strictly increasing phase velocity gives E(p)+E(k-p)<E(k);
q=E^-1(E(k)-E(p)) therefore satisfies k-p<q<k.
All interior triangles are noncollinear; the geometric precision repair does
not replace this mathematical condition.

On-shell E_k=E_p+E_q and K=P+Q imply
V=-2g3*[F(E_k)-F(E_p)-F(E_q)],
F(E)=E*(sqrt(r^2+4mu^2 E^2)-r).
The verifier checks the original Cartesian cubic vertex identity by exact
rational polynomial arithmetic, not fitted numerical agreement.
F(E)/E is strictly increasing for E>0, so the bracket is positive and V is
nonzero on every interior event. W>0 there. This is not a statement about
other scattering channels or scalar angular sectors.

## 2. An integrable collision-measure majorant
Let h_T=T/c_s and
W_prefactor=3*g3^2*T/(4pi^3*c_s^5) [E^-3].
Use |V|<=12|g3|*k*p*q, E>=c_s*k, v>=c_s,
N_k<=T/(c_s*k), 1+N_p<=1+T/(c_s*p), likewise q.
Then
W <= W_prefactor*k*p*q*(p+h_T)*(q+h_T)
  <= W_prefactor*k^2*p*(k+h_T)^2.
Define U(x)=x^7/7+h_T*x^6/3+h_T^2*x^5/5 [E7],
H(K)=K^5/5+h_T*K^4/2+h_T^2*K^3/3 [E5].
I_total=integral W dk dp <= W_prefactor*U(K)/2 [E4].
A bounded vector trial satisfies Q[A]<=9*M^2*I_total < infinity.

For soft-event sets k<s, p<s, q<s:
I_k<=W_prefactor*U(s)/2,
I_p<=W_prefactor*s^2*H(K)/2,
I_q<=W_prefactor*s^2*H(K)/(2*c_s^2).
For I_q use dp/dq=v(q)/v(p)<=1/c_s^2. No event is dropped.

## 3. Smooth soft trials converge in BOTH G and Q norms
For the earlier raw soft seed d_epsilon(k)=T*k/sqrt(k^2+epsilon^2)-T,
|d_epsilon|<=T*min(1,epsilon^2/(2k^2)).
For any0<s<=K,
G[d_epsilon]<=w_max*T^2*(s+epsilon^4/(12*s^3)),
w_max=T^2/(6pi^2*c_s^2).
Q[d_epsilon]<=3*T^2*(I_k+I_p+I_q)
            +9*T^2*epsilon^4*I_total/(4*s^4).
Choose s=sqrt(epsilon*K). Both explicit upper formulas go to zero.
This extends the earlier Gram-only statement to the selected finite-cutoff
collision form. Fixed bounded raw-seed combinations inherit the conclusion.

The maximal radial domain D={A in L2(w dk):Delta F in L2(W dk dp)}
is closed in the joint G+Q norm: H convergence has an a.e. radial subsequence;
the k,p,q pullbacks preserve null sets because the monotone energy map has
positive derivative. A second event-L2 subsequence identifies the limit as
Delta F. Bounded radial functions are dense in H and all are in D by the majorant.
Thus the selected nonnegative form has a dense closed domain.
This is an internal derivation under the stated finite-K kernel, not an
unbounded-K/all-channel domain theorem or external/formal verification.

## 4. Vector nullspace versus uniform gap
Write F=h(k)*K, h=A/k. Then
Delta F=(h(k)-h(p))*P+(h(k)-h(q))*Q.
Positive W and noncollinear P,Q force h(k)=h(p)=h(q) a.e. if Q[A]=0.
The triangular0<p<k domain implies h is a constant a.e.; vector nullspace is
momentum only. Scalar energy and other angular sectors are not re-proved here.

Nevertheless no positive gamma can obey Q[A]>=gamma*G[A] for ALL
zero-momentum vector trials in this domain. Use smooth compact vector bump
A_epsilon(k)=M*psi(k/epsilon),
psi(x)=x*exp(-1/(1-x^2)) for0<=x<1, zero otherwise.
Its Cartesian vector is smooth at zero and its support is0<=k<epsilon.
Let psi_min=exp(-9/5)/3 on x in[1/3,2/3].
w>=T^2*exp(-2epsilon/T)/(6pi^2) on this support; w<=w_max.

Q[A_epsilon]<=3*M^2*W_prefactor/2 *
 [U(epsilon)+(1+c_s^-2)*epsilon^2*H(K)] =O(epsilon^2).
G[A_epsilon]>=M^2*psi_min^2*epsilon*T^2*exp(-2epsilon/T)/(18pi^2).
Subtract its momentum projection; Q is unchanged, and G loses at most
w_max^2*M^2*epsilon^4/(4*G_momentum). G_momentum>0 is fixed.
For explicit evaluated bounds use L=min(K,T/2),
G_momentum>=T^2*exp(-2L/T)*L^3/(18pi^2).
At sufficiently small epsilon projected G is bounded below by a positive
constant*epsilon. Hence Q/G<=constant*epsilon->0.
Nonnegativity gives inf_{momentum-perp} Q/G=0: no uniform positive Rayleigh gap.
This does NOT imply divergent source-weighted current response or absence of
every source-specific hydrodynamic window. New interacting channels may change it.

## Locked numerical/identity checks and remaining controller
Same mu1.28, lambda.01, T=.002/.004 and K=60*T/c_s.
Bump epsilon=d*T/c_s for d=.001/.0005/.00025/.000125.
Smooth-seed bound deltas=.1/.03/.01/.003.
Gram bump quadrature64/128/256 with last-order target1%, no fit.
Check pointwise source inequalities/vertex/measure across declared parent and
daughter grids; exact rational cubic identity and missing-term negative control;
positive projected Gram lower formula, analytical bound decay and scale2.
Numbers evaluate analytic formulas in floating arithmetic; no interval certificate,
formal checker, full continuum collision inversion or new dynamics is run.

Next controller:
source_weighted_continuum_current_upper_bound_and_microscopic_heat_current_correspondence_open.
Need an upper/error bound for the selected current inverse, microscopic
condensate/charge heat-current/frame and interacting-state/channels, followed
by nonlinear/live/material/SI/source admission. A no-uniform-gap result cannot
be turned into a physical relaxation time or silently repaired with a fitted width.
