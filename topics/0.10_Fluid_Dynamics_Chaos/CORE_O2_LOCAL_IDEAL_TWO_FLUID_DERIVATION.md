# Topic 10-13: local current/stress and conditional ideal two-fluid modes
Date: 2026-09-30. Role: FIXED_PHI_LOCAL_IDEAL_TWO_FLUID_REFERENCE_NOT_ADMISSION.
Overall controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.

## Source chain and additional assumption
Use the current Core fixed-Phi Gaussian EOS and the independently derived
[phase-flow Hessian](CORE_O2_FLOW_HESSIAN_DERIVATION.md). Both earlier artifacts
remain unchanged. The current/stress variation below applies to a LOCAL pressure
Taylor model, not to a newly admitted nonlinear microscopic action.
Primary method: [Alford et al. v3](https://arxiv.org/html/1212.0670v3),
(49)-(64),(78),(110)-(121) for two currents, conjugate momenta and ideal modes.
This is selected-equation correspondence, not full paper replication.

The ideal closure adds local-equilibrium entropy conservation. Gaussian
quasiparticles alone do not derive thermalization, a collision rate, a dissipative
tensor or an experimental hydrodynamic frequency window. Keep this assumption
machine-readable. No material coefficients, phase identification of Phi, SI state,
live-Phi dynamics or physical package is admitted.

## F0-F4 ontology, units and local scalar pressure
Natural hbar=c=k_B=1 and +--- metric; translate Core -+++ consistently.
p_mu=partial_mu psi is the matter-phase covector, not pressure and not Phi.
beta^mu is an independent normal-bath inverse-temperature vector.
T=(g_mu_nu beta^mu beta^nu)^(-1/2), u^mu=T*beta^mu,
y=u^mu p_mu and x=g^mu_nu p_mu p_nu.
The rest reference has y=mu and x=mu^2. s is entropy density, not specific entropy.
mu,T,p_mu have E units, beta has E^-1; n,s E^3, pressure/stress E^4,
phase curvature f E^2, EOS Hessian H=partial_(mu,T)^2 P has E^2.

Write a second-order LOCAL pressure
P_loc=P0+n*dy+s*dT+1/2*(dy,dT)*H*(dy,dT)^t+f/2*(x-y^2).
Here P0,n,s,H and f are evaluated independently at the declared reference.
This truncation supplies rest linear response only. Freezing f does not claim
the exact nonlinear EOS or its derivatives at nonzero superflow.

For this convention define j^mu=partial P_loc/partial p_mu and
T^mu_nu=-2/sqrt(-g)*delta[sqrt(-g)*P_loc]/delta g_mu_nu
at fixed beta^mu and p_mu. Direct variation gives
j^mu=f*p^mu+P_y*u^mu and
T^mu_nu=f*p^mu*p^nu+(T*P_T+y*P_y)*u^mu*u^nu-P_loc*g^mu_nu.
Test these against independent finite source/metric derivatives of the scalar
action density and Lorentz/rotation transformations of all sources.

At the rest reference, n_s=mu*f, n_n=n-mu*f and
chi_n=mu*n_n+T*s. These are natural-unit charge/current coefficients in this
conditional ideal model, not a physical He-II density assignment.
The previous formal static proxy provides a separate scalar comparison.
The signed residual pressure-sector derivative n_thermal is not n_n.

The entropy current is s^mu=s*u^mu. Its conjugate thermal momentum is
Theta^mu=-(n_n/s)*p^mu+(chi_n/s)*u^mu.
This yields the same stress -g*P+j^mu*p^nu+s^mu*Theta^nu and local entrainment
B=1/f, A=-n_n/(s*f), C=n_n^2/(s^2*f)+chi_n/s^2.
Test the current-to-momentum map, its inverse, symmetry and positive kinetic
matrix. These are local constitutive correspondences, not all microscopic Ward
identities, a thermal gap equation or a full nonlinear dynamics derivation.

## EOS derivatives independently from the mode integral
At h=0 let X=E^2-k^2, r=mu^2-m_eff^2/Z, D=X-r-2*mu^2.
For F=X*(X-2*r)-4*mu^2*E^2,
F_E=4*E*D; F_EE=4*(D+2*E^2); F_mu=-4*mu*(3*E^2-k^2);
F_mu_mu=-4*(3*E^2-k^2); F_E_mu=-24*mu*E.
Hence E_mu=-F_mu/F_E and
E_mu_mu=-(F_mu_mu+2*F_E_mu*E_mu+F_EE*E_mu^2)/F_E.

For N=(exp(E/T)-1)^(-1), integrate both source modes with k^2 dk/(2*pi^2):
n_th=-int N*E_mu;
s=int[-log(1-exp(-E/T))+(E/T)*N];
H_mu_mu=H_tree+int[N*(1+N)*E_mu^2/T-N*E_mu_mu];
H_mu_T=-int[N*(1+N)*E*E_mu/T^2];
H_T_T=int[N*(1+N)*E^2/T^3].
Add analytic tree pressure/charge/susceptibility. Compare thermal derivatives
against fixed-bound five-point finite differences; separately refine integration
order/cutoff. No EOS Hessian is fitted to a desired sound speed.

## Conditional ideal linear operator and work
With K=H^-1, state a=(delta n,delta s,g,v_s) and
v_n=(g-mu^2*f*v_s)/chi_n, delta(mu,T)=K*delta(n,s),
derive the rows independently from:
delta n_t+div(n_n*v_n+mu*f*v_s)=0;
delta s_t+div(s*v_n)=0;
g_t+grad(n*delta mu+s*delta T)=0;
mu*v_s_t+grad(delta mu)=0.
The last equation is matter-phase integrability; entropy conservation is the
additional ideal local-equilibrium assumption.

Energy is e2=1/2*delta(n,s)*K*delta(n,s)^t
+1/2*chi_n*v_n^2+1/2*mu^2*f*v_s^2.
Its local flux is delta mu*(n_n*v_n+mu*f*v_s)+delta T*s*v_n.
Check positivity, the complete local work cancellation and S*A=A^t*S for e2's
state Hessian S. Independently form the generalized operator in
(delta mu,delta T,v_n,v_s) and compare via the coordinate transformation.

Inspect all eigenvalues: two distinct real acoustic pairs are an eligibility
result of this conditional ideal model, not an admitted He-II second sound.
Record velocities in natural c=1 units, eigenvector entropy current and relative
motion. A finite-temperature entropy pole needs a measured collision/relaxation
window before any comparison with physical data.
Negative controls: omit T*s from normal inertia, give entropy the superfluid
velocity, or reverse the Josephson sign. Detect local/tensor/work or pole defects.

## Locked execution and handoff
[Contract](Data/03_Research/fluid_core_o2_ideal_modes_contract.json).
Same three condensed points and source configuration as the flow Hessian.
Radial orders128/256/384 at cutoff70, cutoffs45/70/100 at order384.
Thermal derivative steps1e-3/3e-4/1e-4; relative derivative agreement1e-5,
implicit refinement1e-6, finite-difference refinement1e-5.
Local source/metric steps1e-3/3e-4/1e-4; derivative correspondence1e-7.
Algebra/covariance/work/pole matching1e-8; scalar proxy correspondence1e-5;
positive-spectrum/negative-control floor1e-7.
No threshold relaxation or coefficient fitting after preview.

If controls pass, the next controller is thermal local-equilibrium/interaction,
live-response and material/observable admission. A local Taylor action plus
ideal conservation is not an admitted nonlinear thermal UET operator.
Physical J04/J05/J06, Topic 13 constants, existing He-II source blockers and
original null material requirements remain unchanged.
