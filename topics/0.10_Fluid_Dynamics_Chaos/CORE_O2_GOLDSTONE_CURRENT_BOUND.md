# Selected finite-K kinetic-current response: conditional weighted upper bound

Date:2026-10-01. Research-core / Topic10 jointly with Topic13 and Core.
Internal mathematical derivation, not formal/independent/interval verification.
Inventory: [continuum form](CORE_O2_GOLDSTONE_CONTINUUM_FORM.md), exact lower
Goldstone root, original leading cubic event density, Bose Gram measure and
[Galerkin source](CORE_O2_GOLDSTONE_GALERKIN_DERIVATION.md). No primary Core
equation, new collision channel, regulator, fitted rate or physical source is added.

## Assumptions, source and units

Same positive finite K,T,mu,r,lambda_c; B=r+2mu^2,c=sqrt(r/B),g3=mu sqrt(lambda_c)/B^(3/2).
E(k), w=k^2 N(1+N)/(6pi^2), W per dk dp and Q retain the previous card's definitions.
Vector trial F=A(k)hat{k}=h(k)Kvector, with h=A/k dimensionless.
On the maximal radial domain, A in L2(w dk), Q[A] finite.
w extends to T^2/(6pi^2 c^2)>0 at zero and is bounded below on finite[0,K].
Thus h is locally integrable on intervals away from zero and integral k^3 h^2 dk finite.

The exact selected kinetic-current source is
J(k)=k*(d(k)-dbar), d(k)=E(k)v(k)/k-c^2
 =8mu^4 k^2/[B*S(k)*(S(k)+B)], S(k)=sqrt(B^2+4mu^2 k^2).
dbar=integral w*k^2*d dk / integral w*k^2 dk is an exact integral definition,
not a fitted material frame. Then integral w*k*J dk=0 exactly.
b[A]=integral w*J*A dk; R_current=sup_{A in D,Q[A]>0} b[A]^2/Q[A], with the momentum null annihilated.
This variational quantity does not assert a strong Hilbert-space inverse exists.
An exact response of any trial subspace is a lower bound; old numerical quadrature
and its approximated frame are not automatically a certified continuum lower bound.

k,K,T:E; S,B,r:E2; g3:E-2; w,W:E2; A,J:E; h,d,dbar:1;
b:E5,Q:E6,R_current:E4. No SI/material heat-current interpretation is admitted.

## 1. Analytic positive event lower bound on two patches

Define S_K=sqrt(B^2+4mu^2 K^2), R_K=sqrt(r^2+4mu^2 K^2),
eta=8mu^4/[S_K*(B+S_K)^2] [E-2]. For f=E/k,
f'(k)=8mu^4*k/[f*S(k)*(B+S(k))^2]>=eta*k.
Consequently E(k)-E(p)-E(k-p)>=3eta*k*p*(k-p)/2.
Since c<=v<=1/c and E(q)=E(k)-E(p),
delta=q-(k-p)>=3c*eta*k*p*(k-p)/2>0.

Use disjoint-p patches P1: p in(0,K/4),k in[K/2,K];
P2: p in[K/4,K/2],k in[3K/4,K]. On both k-p>=K/4,q>=K/4,k>=K/2.
The daughter angle Gamma satisfies
sin^2 Gamma=[((p+q)^2-k^2)*(k^2-(p-q)^2)]/(4p^2q^2)
 >=k*delta*(k-p)/(p*q^2)>=3c*eta*K^2/32 =sigma>0.
No sampled minimum is used as a lower certificate.

Let H(E)=sqrt(r^2+4mu^2 E^2)-r. H'(E)>=4mu^2*E/R_K on E<=K.
E_k=E_p+E_q implies
F(E_k)-F(E_p)-F(E_q)>=6mu^2*E_k*E_p*E_q/R_K.
Hence |V|>=nu*k*p*q, nu=12*g3*mu^2*c^3/R_K [E-2].
Original W=k*p*q*V^2*N_k*(1+N_p)*(1+N_q)/(192pi^3 E_k E_p E_q v_q).
Use E_x<=x,v_q<=1/c,N_k>=exp(-K/T),1+N_x>=T/x:
W/p>=c*nu^2*T^2*exp(-K/T)*K^3/(3072pi^3)=beta [E1].
Therefore W*sin^2 Gamma/p>=alpha=beta*sigma>0 [E1] on both patches.
These constants are analytic lower formulas; floating evaluation is not interval certification.

For a=h(k)-h(p),b=h(k)-h(q), the two-vector angular matrix gives
|a P+b Q|^2>=sin^2 Gamma*(a^2 p^2+b^2 q^2)/2.
The smallest eigenvalue is1-|cos Gamma|>=sin^2 Gamma/2.
Thus Q[A]>=alpha*(E1+E2)/2, where
E1=integral_L p^3 dp integral_H (h(k)-h(p))^2 dk,
E2=integral_M p^3 dp integral_I (h(k)-h(p))^2 dk,
L=(0,K/4),M=(K/4,K/2),H=(K/2,K),I=(3K/4,K).
E1,E2:E5; the patch names are sets, not energy values.

## 2. Weighted graph Poincare estimate without a uniform Bose gap

Let ell=|I|=K/4,rho_L=integral_L p^3 dp=(K/4)^4/4,
rho_H=integral_H k^3 dk=(K^4-(K/2)^4)/4.
Anchor a_I=mean_I h. Jensen gives weighted L error<=E1/ell and M error<=E2/ell.
Let a_L be the p^3-weighted mean on L. Jensen and I subset H give
integral_H |h-a_L|^2<=E1/rho_L and |a_L-a_I|^2<=E1/(rho_L*ell).
Hence integral_H k^3|h-a_I|^2<=2K^3 E1/rho_L+2rho_H E1/(rho_L*ell).
With C_P=1/ell+2K^3/rho_L+2rho_H/(rho_L*ell) [E-1],
integral_0^K k^3|h-a_I|^2 dk<=C_P*(E1+E2)<=2C_P Q[A]/alpha.
This weighted norm is not the Bose Gram norm G; the old absence of a uniform
positive Q/G gap remains unchanged. No contradiction or added width arises.

## 3. Source dual norm and response upper formula

Exact momentum orthogonality allows b[A]=integral w*k*J*(h-a_I) dk.
Cauchy-Schwarz with weight k^3 gives
|b[A]|^2<=B_J*integral k^3|h-a_I|^2 dk,
B_J=integral_0^K w^2*J^2/k dk [E6].
Since0<=d<=D*K^2,D=4mu^4/B^3 [E-2], also0<=dbar<=D*K^2.
Thus |J|<=D*K^2*k and w<=wmax=T^2/(6pi^2 c^2):
B_J<=B_upper=wmax^2*D^2*K^6/2 [E6], finite.
Near zero the exact integrand is O(k), not a divergent source norm.
Therefore |b[A]|^2<=R_upper*Q[A],
R_upper=2C_P*B_upper/alpha [E4], and0<=R_current<=R_upper<infinity. The ratio has unitsE4; no subtraction of b:E5 and Q:E6 is used.
The unprojected source J0=k*(c^2+d) has b[k]>0 but Q[k]=0;
no finite bound of this kind holds for J0. This is a mandatory negative control.

The exp(-K/T) lower formula is intentionally conservative. A finite but enormous
upper constant proves conditional finiteness, not a useful1% response/error bracket.
No numerical current coefficient is calibrated to this bound or to Topic13.
No physical relaxation time, material conductivity or hydrodynamic window follows.

## Locked diagnostics and remaining controller

Before execution: same mu1.28,lambda.01,T=.002/.004,K=60T/c;
P1 k/K=.5/.625/.75/.875/1,p/K=1e-6/.001/.05/.125/.249999;
P2 k/K=.75/.875/1,p/K=.25/.375/.5.
Check analytic angle/vertex/W lower inequalities against original source events,
energy/geometry, source identity and angular matrix bound; no minima-fitting.
Current Gram/dual quadrature64/128/256,last-order1%; algebra1e-8,event1e-9.
Exact source-frame definition, unprojected null-source failure, units and scale2.
Numerics diagnose the explicit derivation; no Lean/interval/full inverse is executed.

Next controller: useful_certified_continuum_current_error_and_microscopic_heat_current_correspondence_open.
Need useful/certified continuum upper-lower/error control and independent/formal
review, then microscopic condensate/charge heat-current/frame, interacting-state/
channels, nonlinear/live/material/SI/protocol correspondence with Topic13.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Physical J04/J05/J06 remain NOT_STARTED; no Core/Topic13 promotion or dependency unlock.
