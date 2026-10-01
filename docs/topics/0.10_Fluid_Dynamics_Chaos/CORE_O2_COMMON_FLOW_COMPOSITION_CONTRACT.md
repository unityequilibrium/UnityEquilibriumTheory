# Topic 10-13: Core O(2) common-flow composition contract

Date: 2026-09-30. Role: CURRENT_CORE_SOURCE_COMPOSITION_DIAGNOSTIC_NOT_ADMISSION.
Overall controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.

## Current source and one proposed shortcut

Core already has a fixed-Phi finite-temperature quasiparticle EOS, a static
Doppler momentum susceptibility and tree condensate phase stiffness. They are
explicitly separate natural-unit lanes. Test the proposed shortcut of combining
these as one ideal two-fluid inertia; do not assume their names prove this map.
Prior source-hashed references and Topic 13 gates are unchanged.

Primary method sources: [Son 2002 v2](https://arxiv.org/html/hep-ph/0204199v2),
equations (20),(25),(31) for zero-temperature phase/EOS/current correspondence;
[Alford et al. 2013 v3](https://arxiv.org/html/1212.0670v3),
(49),(65)-(68) for finite-temperature current/stress decomposition, and Section V
for the need to compute flow-dependent current and effective action.
The latter's low-T, weak-coupling dissipationless field theory is not a liquid
helium EOS. Neither paper identifies UET Phi with the superfluid phase.

## F0-F4: ontology, frame and units before computation

Use fixed Phi, homogeneous rest state, natural units hbar=c=k_B=1.
mu,T,m have energy units; p,e,w and momentum susceptibility have E^4;
charge/entropy densities n,s have E^3; phase stiffness f_s has E^2.
Here s denotes entropy DENSITY, distinct from the prior specific-entropy s.
Paper sigma (phase-gradient norm) is not Topic 10's entropy-density sigma.
The source metric convention differs from Core; use only consistent rest-state
scalar identities, not a copied tensor with mixed signs.

For a zero-flow ideal relativistic two-fluid state, the linear momentum is
g=(mu*n_n+T*s)*v_n+mu*n_s*v_s. A common infinitesimal boost has coefficient
w=e+p=T*s+mu*n. If f_s=n_s/mu and chi_n is the full normal momentum coefficient,
then w=mu^2*f_s+chi_n. This is a conditional constitutive correspondence target.

The Core static Doppler chi_perp_qp is NOT already admitted as chi_n.
The comparison asks whether substituting it while keeping f_s_tree is consistent.
It does not assume that a mismatch invalidates O(2), the EOS or its static lane.

At T=0, current tree pressure p0=q^2/(4*lambda), q=Z*mu^2-m_eff^2>0,
gives n0=Z*mu*q/lambda, chi_charge0=Z*(3*Z*mu^2-m_eff^2)/lambda,
f_s_tree=Z*q/lambda, w0=mu*n0=mu^2*f_s_tree.
Its long-wave Goldstone speed squared is n0/(mu*chi_charge0).
mu^2 converts stiffness to inertia units; substituting stiffness alone is invalid.

At finite T use the source pressure p(T,mu,Phi), differentiating at fixed Phi.
The signed residual grand-pressure sector is not a normal-density measurement.
Evaluate Delta=mu^2*f_s_tree+chi_perp_qp-(T*p_T+mu*p_mu).
Report Delta and numerical refinements. Do not set f_s=(w-chi)/mu^2 to force the
identity or emit that algebraic value as an action-derived coefficient.

Even satisfying this one scalar target would not derive the complete flow
master function, entrainment, longitudinal eigenmodes or dissipative transport.
A He-II map further needs a nonrelativistic limit, mass/charge normalization,
SI state and source-locked thermodynamics; natural-unit inertia is not kg/m^3.

## Locked execution design

[Machine contract](Data/03_Research/fluid_core_o2_common_flow_contract.json).
Matter: Z=1,mass_squared=1,lambda=1,response_coupling=0; epsilon_nc=0,
phi_equilibrium=0; fixed Phi=0.15. No recalibration.
Normal controls: mu=0.35 at T=0.12/0.22.
Condensed candidates: mu=1.28 at T=0.04/0.08/0.16.
Independent five-point pressure derivatives use relative steps 1e-3,3e-4,1e-4.
Quadrature orders 128/256/384 at cutoff factor 70; separately cutoff factors
45/70/100 at order 384. No changing orders and cutoff simultaneously to infer
separate convergence. Quadrature nodes/weights may be memoized exactly.
Normal identity/composition relative target 1e-5; finest-change budget 1e-6;
algebra/spectrum identity tolerance 1e-8; sensitivity floor 1e-7.
Record target PASS/FAIL separately from diagnostic execution PASS/FAIL.

The local full Core import lacks scipy. Execute only named, source-verbatim AST
functions/classes from canonical Core files in isolated namespaces, with explicit
configuration fields and source hashes. This is a source-function diagnostic,
not a full Core runtime rerun. Mathematical pressure/Doppler bodies are unchanged;
finite derivatives are this wrapper, not Core's native second-order derivative.
Do not relax a failed threshold; retain the first diagnostic.

## Controlling boundary

The candidate composition gate may reject the shortcut while the existing static
Core lane remains useful. Next derive flow-dependent finite-T current/stress/
phase stiffness from a common effective action with a stated ensemble and Ward
identities before claiming a physical normal/superfluid state. Do not use the
normal-only heat balance on the condensed branch. Keep physical J04/J05/J06,
material entropy values, Topic 13 constants and Core admission gates unchanged.
