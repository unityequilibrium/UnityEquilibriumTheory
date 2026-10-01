# Selected tree wave density and mean condensate response

Date:2026-10-01. Internal order-A0^2 reference, not interacting/material admission.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Extends [tree spatial currents](CORE_O2_MICROSCOPIC_CURRENT_WARD.md) without
changing its source, dispersion, collision kernel or old artifact. No primary
Core equation is added. Matter phase psi is distinct from fixed response Phi.

## Source and approximation boundary

Same +--- action and Core -+++ conjugate-phase/index translation. Let
r=mu^2-m_c^2>0, rho=sqrt(r/lambda_c), B=r+2mu^2, a=(k^2-E^2)/(2mu E),
n=E*(a^2+1)/2+mu*a>0 and Nwave=A0^2*n. The two positive branches are
kinematic controls; only the old lower branch enters thermal subset diagnostics.
The homogeneous mean shift below solves the phase-averaged radial equation
to order A0^2 at fixed mu. It does not solve a full nonlinear travelling wave,
its second harmonics, a self-consistent interacting thermal state or a vacuum problem.

Primary [Alford et al. v3](https://arxiv.org/html/1212.0670v3), equations1-5b,
11,27-28,41 and discussionIII.1, supplies action and source correspondence.
Its weak-coupling small-T approximation additionally requires T^2>>lambda*mu^2.
At our locked T=.002/.004, mu1.28,lambda_c.01, those ratios are approximately
0.000244/0.000977, not in that regime. Thus neither the paper's retained full
thermal accuracy nor omission of interacting corrections is admitted here.
Earlier tree/selected-kernel diagnostics remain scoped references, not new
validation of the paper approximation. No source payload is vendored.

## Off-stationary quadratic action and mean tadpole

Keep background rho independent while taking the derivative:
M_u^2=m_c^2+3lambda_c*rho^2-mu^2,
M_v^2=m_c^2+lambda_c*rho^2-mu^2,
Lbar2/A0^2=(E^2-k^2)*(a^2+1)/4+mu*a*E-(M_u^2*a^2+M_v^2)/4.
At the tree stationary rho, M_u^2=2r,M_v^2=0 and Lbar2=0 on shell.
Partial_rho Lbar2/A0^2=-lambda_c*rho*(3a^2+1)/2.
The classical background action has curvature -2r, so
delta_rho/A0^2=-(3a^2+1)/(4rho).
The averaged radial field equation is
-2r*delta_rho-lambda_c*rho*A0^2*(3a^2+1)/2=0+O(A0^4).
Use original Core matter Euler-Lagrange and action functions to diagnose this;
do not obtain box from the on-shell helper or insert the EOM as a definition.

## Charge and energy densities

The raw unshifted wave density is
q_raw/A0^2=mu*(a^2+1)/2+a*E.
The mean condensate contributes
delta_q_bg/A0^2=2mu*rho*delta_rho/A0^2=-mu*(3a^2+1)/2.
Thus q_corrected/Nwave=a*(E-mu*a)/n=-dE/dmu along the tree stationary background.
The derivative holds k,m_c^2,lambda_c fixed and includes d rho/dmu.
Without this shift, the raw charge is not the thermodynamic mode charge.

Raw stress energy per A0^2 is
e_raw=(E^2+k^2+mu^2+m_c^2)*(a^2+1)/4+mu*a*E+r*(3a^2+1)/4.
The background energy derivative is 2mu^2*rho, hence delta_e_bg=mu*delta_q_bg.
Consequently e_corrected/Nwave=E+mu*q_corrected/Nwave, while
(e_corrected-mu*q_corrected)/Nwave=E. Grandcanonical density is unchanged
by the mean shift to this order because the classical background is stationary.

No elementary-charge advection is inferred: the prior spatial J_N=-dE/dh
still differs from (-dE/dmu)*v_g. Density/flux identities do not select a
material heat/enthalpy frame, zero mass/charge flow, SI atom normalization or
an experimental He-II state. Source coefficient extraction below is a polynomial
diagnostic, not a finite-amplitude physical solution or full Ward proof.

## Fixed-domain Gaussian thermal subset

For the lower branch only, use D(k)dk=k^2 dk/(2pi^2) and Bose f(E/T).
At each central state K=60T/c_s is fixed during every mu/T derivative:
P_T=-T*integral_0^K D log(1-exp(-E/T)),
q_T=integral D*f*q_corrected/Nwave=dP_T/dmu,
U_G=integral D*f*E=T*dP_T/dT-P_T,
e_T=U_G+mu*q_T.
The mean thermal shift is integral D*f*(delta_rho/A0^2)/n and its background
charge 2mu*rho*delta_rho_T must equal the difference q_T-q_raw,T.
These are finite-domain Gaussian bookkeeping identities. No interacting EOS,
infinite-domain tail certificate, self-consistent gap solution, damping or
physical coefficient follows. A negative thermal correction to charge/energy
at fixed mu is not a negative total density or material instability claim.

## Locked controls and conditioning

Both branches at k/(T/c_s)=.1/1/10/60, same two temperatures/mu/coupling and
closed response. Direct source phase averages8/16/32, phases0/.37. Amplitude
coefficients use A0/rho=.01/.02/.04/.08, with polynomial extrapolation in A0^2
for the quadratic coefficient (source quartic potential, mean shift give up
to A0^8); these are extraction controls, not a solved nonlinear wave.
Compare full source densities with and without the mean shift, the mean radial
residual and original source action. Source cancellation errors use the larger
raw/corrected same-dimension coefficient as scale; actual corrected-charge
relative error and cancellation condition number are also reported, not hidden.
Source/algebra/phase/unit conditioned tolerance1e-8; independent five-point
mu derivative relative tolerance1e-5, steps mu*.001/.0003/.0001.
Thermal Gauss64/128/256 last-order1%; fixed-domain mu/T five-point steps
.001/.0003/.0001 relative, derivative tolerance1e-5. Negative floor.001 and
energy scale2; q:Nwave ratio dimensionless, energy ratio:E, delta_rho:E,
q density:E3,e density:E4,delta_rho_T:E,thermal pressure:E4.
No threshold fitting, source clipping or branch repair after execution.

Next selected controller:
useful_certified_current_error_and_interacting_Noether_heat_frame_material_correspondence_open.
The same controller is retained: leading mean density response is narrowed,
but interacting/state/heat/frame/material, useful certified continuum error
and Topic13 EOS/independent protocol remain open. Physical J04/J05/J06 stay unexecuted.
