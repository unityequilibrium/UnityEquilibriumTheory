# Tree spatial Noether currents and the selected grandcanonical kinetic flux

Date:2026-10-01. Conditional source correspondence, not physical material admission.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Inventory: [flowing quadratic kernel](CORE_O2_FLOW_HESSIAN_DERIVATION.md),
[local ideal currents](CORE_O2_LOCAL_IDEAL_TWO_FLUID_DERIVATION.md),
[selected current bound](CORE_O2_GOLDSTONE_CURRENT_BOUND.md) and unchanged Core
matter Noether/stress source. No new primary Core equation or collision channel.
Primary reference: [Alford et al. v3](https://arxiv.org/html/1212.0670v3),
(5b),(8),(28),(34)-(36),(41). Selected source/action correspondence only;
not full one-loop paper replication, vacuum renormalization or interacting transport.

## Conventions, ontology and source boundary

Natural units hbar=c=k_B=1. Derive with +--- and psi=+mu*t+h*z;
Core uses -+++ and theta=-psi. Matter phase is distinct from response Phi.
At zero flow, translate paper real fluctuations (rho+u,v) to Core doublet
chi=(rho+u,-v) at background phase zero. Rotate both fields and covariant
derivatives together for any constant phase. Core gradient inputs are covariant;
its stress expression uses gradient_outer and g, hence yields lower-index T.
Raise both indices with the inverse metric before comparing T^{0z}/T^{z0}.
No inference of a material/SI charge or mass normalization.

Same tree-stationary r=mu^2-m_c^2>0,B=r+2mu^2,lambda_c>0,
rho=sqrt(r/lambda_c), closed response and fixed Phi. The selected collision
states remain T=.002/.004,mu1.28,lambda_c.01,K=60T/c_s.
The two tree branches are inspected as kinematic controls; no radial scattering
channel or upper-branch transport is added.

## Quadratic action, mode polarization and wave action

L2=1/2*(u_t^2-|grad u|^2+v_t^2-|grad v|^2)
 +mu*(u*v_t-v*u_t)-r*u^2.
For u=A0*a*cos(varphi),v=A0*sin(varphi),varphi=E*t-k*z,
(k^2+2r-E^2)*a=2mu E and (k^2-E^2)=2mu E*a.
Thus a=(k^2-E^2)/(2mu E) on either positive branch.
E_-^2=k^2+B-S,E_+^2=k^2+B+S,S=sqrt(B^2+4mu^2 k^2).
Use the old rationalized lower branch; do not clip roots or mix branches.

The averaged rotating-frame action is
Lbar=A0^2*((E^2-k^2)*(a^2+1)/4+mu*a*E-r*a^2/2).
At fixed polarization the wave-action density is
Nwave=partial_E Lbar=A0^2*(E*(a^2+1)/2+mu*a)>0.
It is a mode normalization derived from the action, not a fitted occupation.
A0:E,fields:E,gradients:E2,Lbar:E4,Nwave:E3; a:1.

## Independently varied spatial fluxes

Directly from the original field Noether and stress expressions, phase averaging
and retaining the quadratic part gives
j_N,z=A0^2*a*k,
T^{0z}=T^{z0}=A0^2*k*(E*(a^2+1)/2+mu*a)=k*Nwave,
j_G,z=A0^2*E*k*(a^2+1)/2=T^{z0}-mu*j_N,z.
Here j_G is the energy flux of the rotating generator H-mu Q.
The field calculation must execute source-verbatim Core functions; the Ward
identity is a comparison target, never a definition substituted into those functions.

Per normalized mode, J_N=j_N,z/Nwave is dimensionless, while
J_E=T^{z0}/Nwave=k [E] and J_G=j_G,z/Nwave [E].
Differentiating the mode action in k gives v_g=k*(a^2+1)/(2*Nwave/A0^2),
so J_G=E*v_g. This identifies the old selected kinetic flux with the tree
rotating-generator flux, conditional on this zero-flow normalization.

Independent flowing determinant F(E,h)=(E^2-k^2)*(E^2-k^2-2r(h))
 -4*(mu E+h*k_z)^2,r(h)=mu^2-h^2-m_c^2.
At h=0, A=E^2-k^2-r-2mu^2 is -S/+S and E_h=2mu*k_z/A.
Thermal source variation gives J_N=-E_h; hence J_E=J_G+mu*J_N=k.
Verify this against positive quartic roots at finite +/-h and against direct
field Noether/stress evaluation, including index/phase translation.

Omitting mu*J_N would misidentify E*v_g as total energy flux. Keeping the
wrong stress index sign or reversing the charge convention also fails the target.
The complete field stress is symmetric; grandcanonical flux alone need not equal momentum.

## Momentum projection and the unresolved heat-current frame

For the old lower-mode Bose Gram measure w and exact integral projection
P_perp X=X-k*(integral w*k*X)/(integral w*k^2),
P_perp J_E=0 and P_perp J_G=-mu*P_perp J_N.
The old source k*(d-dbar),d=E*v_g/k-c_s^2, is exactly P_perp J_G.
The conditional finite current bound therefore applies to this selected
projected rotating-generator flux; it is not a bound for arbitrary heat currents.
Finite Gauss comparison is a diagnostic, not a certified exact integral projection.

Thermodynamic mode charge is q_th=-partial_mu E along the tree-stationary
background. It is not a fixed elementary charge that may simply be advected
as q_th*v_g; that shortcut fails the spatial Noether current. A raw quadratic
j^0 from unadjusted waves omits the second-order condensate shift/tadpole.
No complete charge-density/energy-density backreaction identity is claimed here.

Neither J_G=J_E-mu J_N nor a zero-momentum constraint fixes the experimental
heat flux or material frame. Particle/enthalpy subtraction, condensate response,
zero net mass/charge flow versus momentum, interacting thermal state/channels,
SI charge/atom mapping and the Topic13 protocol remain separate obligations.
No conductivity, physical relaxation time, collective damping, frequency window
or admitted He-II second sound follows from this tree correspondence.

## Prelocked diagnostics

Same selected states/cutoff, both positive roots at k/(T/c_s)=.1/1/10/60.
Phase-average orders8/16/32; A0/rho=.001/.002/.004; constant background phases0/.37.
Finite-flow derivatives use five-point h/mu=.001/.0003/.0001 at k/(T/c_s)=1/10/60.
Algebra/source/phase/index/scale correspondence1e-8, finite derivative1e-5,
projection quadrature64/128/256 last-order1%, negative-control floor1e-3.
Use paired +/-wave amplitudes to remove linear terms; no fitting or threshold relaxation.
Whole-energy scale2 and amplitude-density powers distinguish units from occupancy.
No whole Core import, live Phi, formal/interval/independent proof or physical J04/J05/J06.

Next controller:
useful_certified_current_error_and_interacting_Noether_heat_frame_material_correspondence_open.
The selected tree spatial-current origin is narrowed; interacting density/backreaction,
heat/material frame, useful/certified continuum error and Topic13 EOS/protocol remain open.
