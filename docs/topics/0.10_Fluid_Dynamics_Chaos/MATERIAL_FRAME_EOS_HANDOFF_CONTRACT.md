# SD03 material heat/frame and pressure-ensemble derivation contract

Date: 2026-10-05. Owner: Topic10 shared Core/Topic13 secondary derivation.
Role: PREREGISTERED_CONDITIONAL_HANDOFF_NOT_MATERIAL_ADMISSION.
Prior: [SD02 handoff](CORE_O2_STATIONARY_SOURCE_HANDOFF.md).

## Decision and stopping rule

Connect the same stationary pressure/source response to material heat subtraction,
fixed-pressure heat capacity, entropy-reference transformation and SI/covariance
requirements. Complete when the conditional exact chain/frame identities and
specified negative controls pass with locked inputs, and each unfilled material
prerequisite points to its existing controller. No interacting solver, new material
benchmark, row comparison, transport fit or physical gate promotion in this wave.

## Frame and generator distinction

For one declared conserved particle charge at homogeneous isotropic rest, let
n=p_mu, S=p_T, enthalpy density w=epsilon+p=T*S+mu*n and h=w/n.
For small linear frame shift delta v, j_N'=j_N-n delta v and
j_E'=j_E-w delta v. Hence

    q_heat = j_E-h*j_N
    j_G = j_E-mu*j_N = q_heat+T*(S/n)*j_N.

q_heat is invariant to this linear frame shift; j_G shifts by -T*S delta v.
Zero charge flux fixes the Eckart particle frame only if n is a nonsingular,
properly mapped material particle density. Zero momentum and zero signed Core
charge need not mean zero material mass flow. The nonlinear, vortical and
relativistic/two-fluid extensions need their own stress/particle mappings.

This extends the frame comparison already explicit in Core's normal-lane
covariant entropy module: u_E=u_L+V/n, q=Q-hV and
S_L=S*u_L+(Q-mu V)/T=S*u_E+q/T. It does not replace that module or its
finite-cutoff normal collision state with the gHF condensate. Topic10's tree
Ward record identified j_G, not material q_heat. A sign-correct Noether flux
alone does not supply h, n, mass/atom normalization or a material frame.

In the existing linear ideal material comparator, mass flux j=rho_s*v_s+rho_n*v_n
and entropy flux J_S=Sigma*v_n give energy flux
J_E=mu_mass*j+T*J_S, with epsilon+p=mu_mass*rho+T*Sigma.
Consequently q_mass=J_E-((epsilon+p)/rho)*j
=T*Sigma*(rho_s/rho)*(v_n-v_s). This is derived from the declared standard
linear constitutive inputs, not from Core or an SI experiment. Entropy-reference
changes must transform J_S and mu consistently, as already specified in the
[entropy reference contract](HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md).

## Fixed-pressure EOS from the same fully stationary p(T,mu)

For n>0 and smooth p, define sigma=S/n (entropy per conserved particle).
At fixed pressure, mu_T=-S/n=-sigma. Chain differentiation gives

    c_p,particle = (T/n)*(p_TT-2sigma*p_Tmu+sigma^2*p_mumu).

This needs the total stationary Hessian from SD02, not a frozen-state Hessian.
At fixed mu the specific entropy derivative instead gives
(T/n)*(p_TT-sigma*p_Tmu). For a path P(T) the heat-capacity-like derivative
T*d sigma/dT acquires the extra term

    (T/n)*(P_prime/n)*(p_Tmu-sigma*p_mumu).

Thus an SVP path is not fixed pressure without its measured slope/constraint
translation. This complements the existing material e(rho,Sigma) Hessian and
SVP ambiguity result; it does not replace its full two-fluid quartic or domain
failures. A heat-capacity label must first be tied to its actual heat/work protocol.

Under entropy-coordinate offset S'=S+a*n, mu'=mu-a*T, let
p'(T,mu')=p(T,mu'+a*T). Then sigma'=sigma+a and
p'_TT=p_TT+2a*p_Tmu+a^2*p_mumu,
p'_Tmu'=p_Tmu+a*p_mumu, p'_mu'mu'=p_mumu.
The displayed fixed-pressure combination, Gibbs enthalpy and q_heat are invariant.
Keeping old Hessian or convection law with shifted entropy defines another model;
it cannot establish a material entropy-reference transfer.

## SI and statistical-source map required before numbers

Only after particle/atom source normalization and measure are admitted, write
p_SI=P0*pbar, T_K=Theta0*Tbar, mu_J_per_atom=E0*mubar. Derivatives imply
n_SI=(P0/E0)*pbar_mu and S_SI=(P0/Theta0)*pbar_T. With a common natural
energy convention in the Bose exponent, E0=k_B*Theta0 is a required consistency
condition, not a new fit. Specific entropy and c_p per mass acquire the factor
E0/(m_atom*Theta0); h per atom acquires E0. A declared velocity scale V0 gives
J_E,SI=P0*V0*J_Ebar and J_N,SI=(P0/E0)*V0*J_Nbar, preserving heat subtraction.
Neither a Kelvin gain nor e0 alone fixes all these source/measure/particle/velocity
maps. The existing calibrated e0 and theta_T are preserved; neither is reassigned
as full pressure/energy or used to rematch a response row. Physical scale fields
remain null. Rational scaling controls below are algebra fixtures, not SI inputs.

Signed relativistic O(2) charge may include opposite-charge modes and is not
identical to total helium atom density. It requires an explicit lane/source and
nonrelativistic/material mapping before rho=m_atom*n is used. Normal fraction
requires transverse/current/relative-flow response, not condensate amplitude alone.

## Covariance and second-sound protocol boundary

The existing standard reference derives the full two-fluid sound quartic. Only
within an evidenced reduced/weak-mixing regime is
c2^2=(r/(1-r))*T*s_mass^2/c_p appropriate, with r=rho_s/rho. For this restricted
formula, logarithmic sensitivity of c2^2 to (r,T,s_mass,c_p) is
[1/(r*(1-r)),1/T,2/s_mass,-1/c_p]. To first order relative speed variance is
(1/4)*g^T Cov*g. This is a conditional differential formula, not an error bound,
noise assignment or guarantee of the reduced approximation. Covariance is not
silently diagonal: entropy/calorimetry and sound-derived superfluid density may
share ancestry. Near endpoints/branch mixing/large errors require other analysis.
Only a synthetic positive covariance fixture is evaluated; material covariance
and bounds remain unassigned. Printed precision and source bounds are not standard
deviations by default.

[He4 protocol](../0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md)
requires a primary state/T90-pressure path, frequency, geometry, mean flow,
complex mode/attenuation convention and uncertainty/covariance record. The
calibration and response source overlap is unresolved and compiled rows were
viewed; no independent/blind claim. Hydrodynamic locality requires collision/time/
wavelength evidence, not a natural rate automatically interpreted as physical.
The normal eta input cannot specify all thermal/bulk/mutual-friction channels.

## Locked exact controls and source scope

Use one analytic synthetic pressure p=(T^2+mu^2)/2+T*mu/4 at T=1/2,mu=1,
r=3/5 and two-component velocities in the contract. It is not a gHF/He-II EOS.
Second-order exact jets check constant-pressure path and the entropy quotient.
Check frozen-mu/SVP/Hessian-shift, chemical-versus-enthalpy, frame/entropy-current,
SI source-scale and diagonal-covariance negatives. Invalid n=0, r endpoints,
nonpositive specific heat and missing physical scales must not become admission.
No tolerance or fitting; first result/failure retained before any repair.

[Two-fluid source](https://arxiv.org/pdf/1510.01306), v1 selected section 1.2,
equations 1.1-1.9, gives the standard particle/entropy-flow and sound regime;
[Hu et al.](https://arxiv.org/pdf/1001.0772), selected sections II/III,
distinguishes response observables/probes. Full papers are not reproduced.
Frame/EOS/unit chain calculations here are conditional derivations. Existing
Core, Topic13 and material comparator evidence remains in its original scope.

Method controller remains finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
Selected/overall physical controllers and all ten method gates/J04/J05/J06 stay.
The current material requirements remain unassigned. Completing SD03 closes this
handoff only; full J00-J09, thermal state/vertex/material/external work remain open.
