# Topic 10-13: finite-temperature phase-flow Hessian derivation
Date: 2026-09-30. Role: APPROXIMATE_FIXED_PHI_FLOW_HESSIAN_REFERENCE_NOT_ADMISSION.
Overall controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.

## Question and source boundary
The previous [composition diagnostic](CORE_O2_COMMON_FLOW_COMPOSITION_CONTRACT.md)
rejected tree stiffness plus the formal Doppler momentum proxy at three condensed
points. Preserve that artifact. Derive an independent thermal phase correction
from a flowing quadratic action, rather than solve an inertia identity for it.

Primary method: [Alford et al. v3](https://arxiv.org/html/1212.0670v3),
(5b),(28) for the quadratic action/propagator, (34)-(36) for current variation,
(71)-(75) for the normal-rest ensemble and (111)-(113) for phase derivatives.
This is a selected-equation correspondence calculation, not full paper replication.
Its thermal Gaussian approximation and tree condensate do not include thermal
melting, self-energy, vacuum counterterms, Kubo transport or liquid helium physics.

Core matter/response/EOS/static source files are read only. Reuse the previous
verifier's source-verbatim AST extraction for zero-flow comparison. The finite-flow
kernel below is a NEW topic-local derivation, not an existing Core source function.
A whole Core runtime import is not executed.

## F0-F4: ontology, units, frame, correspondence
Natural units hbar=c=k_B=1; use +--- for this derivation and consistently translate
the Core -+++ convention. psi is the O(2) condensate phase, not UET response Phi.
Phi is fixed at 0.15 with response coupling closed. T is the normal-bath rest
temperature; mu=partial_0 psi>0 and h=partial_z psi are held as separate sources.
Physical superflow is v_s=-h/mu in this convention. k_z=k*cos(theta).

mu,h,T,m_c and k have E units; generalized pressure has E^4; phase curvature
f_s=-partial_h^2 P has E^2; current densities have E^3. No SI density is emitted.
Canonical field normalization gives m_c^2=m_eff^2/Z, lambda_c=lambda/Z^2.
sigma_phase^2=mu^2-h^2 is distinct from Topic 10 entropy density sigma.
Tree q(h)=Z*(mu^2-h^2)-m_eff^2; A_tree^2=q(h)/lambda.
The tree pressure is q(h)^2/(4*lambda); its zero-flow curvature is Z*q(0)/lambda.

For a homogeneous tree-stationary condensate, the canonical quadratic determinant
is F(E,h)=(E^2-k^2)*(E^2-k^2-2*r(h))-4*(mu*E+h*k_z)^2,
where r(h)=mu^2-h^2-m_c^2. At h=0 it reproduces the current Core two branches.
This follows by expanding the matter action to second order in amplitude/phase
fluctuations; do not introduce a separately tuned Doppler coefficient.

Use both positive roots of F at finite h in the thermal Gaussian pressure
P_th=-T*integral[d^3k/(2*pi)^3]*sum_a log(1-exp(-E_a(h)/T)).
The tree amplitude follows its tree stationary value at each h; it is NOT a
thermal gap-equation solution. Vacuum and measure constants are excluded in
the same named approximation as the current zero-flow EOS.

## Independent zero-flow implicit derivatives
Set x=E^2-k^2, r=mu^2-m_c^2, A=x-r-2*mu^2 at h=0.
F_E=4*E*A; F_EE=4*(A+2*E^2);
F_h=-8*mu*E*k_z; F_Eh=-8*mu*k_z; F_hh=4*x-8*k_z^2.
Implicit differentiation gives a=E_h=2*mu*k_z/A and
b=E_hh=-(F_hh+2*F_Eh*a+F_EE*a^2)/F_E.
Angular averages use <k_z^2>=k^2/3, so
<a^2>=4*mu^2*k^2/(3*A^2) and
<b>=-[4*x-8*k^2/3-32*mu^2*k^2/(3*A)
       +16*mu^2*k^2*(A+2*E^2)/(3*A^2)]/(4*E*A).
No root clipping or modification of negative/complex roots is permitted.

With N(E)=1/(exp(E/T)-1), the independently derived thermal phase correction is
delta_f_s=integral[k^2 dk/(2*pi^2)]*sum_a[N*<b>-N*(1+N)*<a^2>/T].
Set f_s_flow=f_s_tree+delta_f_s. This calculation must NOT read enthalpy or the
static momentum proxy when constructing f_s_flow.
Check this against a five-point second derivative of the finite-flow pressure.
Differentiate the thermal part only to avoid subtracting large tree pressures;
add the analytic tree curvature afterward.

## Separate correspondence target and sensitivity controls
Reuse zero-flow p_T,p_mu and formal chi_perp_qp from the source diagnostic.
Test T*p_T+mu*p_mu versus mu^2*f_s_flow+chi_perp_qp. This is an independently
evaluated common-flow scalar correspondence target, not a definition of f_s.
Even a PASS does not establish every Ward identity, finite-flow stress/entrainment,
longitudinal two-fluid modes, live-Phi response or physical material admission.

Negative controls: keep tree stiffness only (previous failure); replace the
action roots by pure E(0)+(h/mu)*k_z so their b term vanishes; or omit the occupation
curvature term. Compare corrections and the scalar target under locked floors.
A positive check tests the new quartic roots against Core at h=0, determinant
residuals at finite h, pressure parity h->-h, and the tree limit.

## Locked computation
[Contract](Data/03_Research/fluid_core_o2_flow_hessian_contract.json).
Reuse the three previous condensed points: mu=1.28, T=0.04/0.08/0.16;
Z=1, mass_squared=1, lambda=1, Phi=0.15, closed response coupling.
These are computational controls, not an established weak-coupling material regime.
Implicit radial orders 128/256/384 at cutoff factor70; cutoff45/70/100 at order384.
Finite-flow angular orders12/24/36; flow steps |h|/mu=1e-3,3e-4,1e-4.
Five-point pressure first derivatives retain relative step1e-4.
Composition target1e-5; component refinement1e-6; implicit/finite-flow thermal
correction agreement1e-5; finite-flow correction step stability1e-5;
root/determinant/parity relative tolerances1e-9/1e-10/1e-9; sensitivity floor1e-7.
Lock before code/first execution, retain initial output even if FAIL, and do not
fit a coefficient or relax thresholds after seeing results.

## Handoff boundary
If the independent Hessian matches the source common-flow scalar target, narrow
the next controller to complete current/stress/entrainment and longitudinal-mode
derivation at the same fixed ensemble, before nonrelativistic/material/SI mapping.
If it fails, retain the scalar action-response mismatch as controlling.
Physical J04/J05/J06, Topic 13 constants, source acquisition blockers and original
null-valued material requirements remain unchanged in either case.
