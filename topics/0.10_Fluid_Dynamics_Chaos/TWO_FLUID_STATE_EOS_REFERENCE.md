# Topic 10–13: compressible two-fluid state and EOS reference

Date: 2026-09-30. Role: STANDARD_PHYSICS_REFERENCE_NOT_UET_STATE.
Overall controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Coupled input controller: two_fluid_fixed_pressure_EOS_and_UET_state_mapping_missing.

This records the standard state a He-II candidate must reproduce or explicitly
depart from. It does not equate C to density, Phi to temperature or superfluid
phase, Q to entropy flux, or the Topic 13 reference e0 to full internal energy.
The prior [single-velocity exclusion](SECOND_SOUND_MODE_ELIGIBILITY.md) remains.
No central Core equation, material coupling or physical gate is admitted.

## F0–F4: state, source, dimensions and assumptions before code

Homogeneous liquid at rest: rho=rho_n+rho_s>0, both components positive;
entropy density sigma>0; no vortices, external potential, dissipation or mean
counterflow. Work locally to linear order in a longitudinal disturbance.
This is not a nonlinear turbulent/vortex model or a zero-temperature endpoint.

Use material internal-energy density e(rho,sigma) at zero relative flow:
d e=mu_mass d rho+T d sigma; p=rho mu_mass+sigma T-e.
mu_mass is chemical potential per mass, not Core mu_C or a per-particle potential.
The local Hessian is K=[[A,B],[B,D]] with A=e_rhorho, B=e_rhosigma, D=e_sigmasigma.
Require K positive definite; rho_s is a separate superfluid response density,
not automatically the condensate fraction or the amplitude of an O(2) field.

State z=(delta rho,delta sigma,j,delta v_s). j is total mass current perturbation.
v_n=(j-rho_s delta v_s)/rho_n; w=v_n-delta v_s.
The common velocity is j/rho. Entropy is transported by v_n in this reference.
The vortex-free phase record is v_s=(hbar/m_4) grad vartheta_sf; this phase is
distinct from the UET response Phi and the calibration scale theta_T.
The chemical-potential equation below is a standard Josephson/hydrodynamic
condition; UET's microscopic origin/mapping to it is not supplied.

| Symbol | SI target |
| --- | --- |
| rho,rho_s,rho_n | kg/m^3 |
| sigma | J/(m^3 K) |
| s=sigma/rho | J/(kg K) |
| e,p | J/m^3 = Pa |
| mu_mass | J/kg |
| T | K |
| j | kg/(m^2 s) |
| v_s,v_n,w | m/s |
| A | m^5/(kg s^2) |
| B | m^3 K/kg |
| D | m s^2 K^2/kg |
| c_p,c_v,c_sat | J/(kg K) |
| alpha_p,alpha_path | 1/K |
| kappa_T | 1/Pa |
| p_path_prime | Pa/K |

The verifier uses normalized synthetic numbers, not numerical SI material inputs.

Primary standard source:
[Nikuni and Griffin](https://arxiv.org/abs/cond-mat/0009333), Section IV (86)-(88),
Appendix C (C1)-(C10). Its general Landau-Khalatnikov structure is used; its
Hartree-Fock identification of condensate and superfluid densities and dilute-gas
transport coefficients are not transferred to liquid helium.
The matrix and thermodynamic transformations below are derived here from the
explicit mass/entropy/potential equations, not copied from an extracted PDF symbol.

## Conservative longitudinal equations and work

At zero mean flow the ideal linear system is

~~~text
delta rho_t   = -partial_x j
delta sigma_t = -sigma partial_x v_n
j_t           = -partial_x delta p
delta v_s_t   = -partial_x delta mu_mass

delta mu_mass = A delta rho+B delta sigma
delta T       = B delta rho+D delta sigma
delta p       = (rho A+sigma B)delta rho+(rho B+sigma D)delta sigma

z_t = -M z_x
M =
[ 0,             0,              1,                   0 ]
[ 0,             0,       sigma/rho_n, -sigma rho_s/rho_n ]
[ rho A+sigma B, rho B+sigma D,    0,                   0 ]
[ A,             B,              0,                   0 ]
~~~

The positive quadratic *perturbation availability* is
E2=integral[delta x^T K delta x/2+
(j-rho_s delta v_s)^2/(2rho_n)+rho_s(delta v_s)^2/2] dx,
where delta x=(delta rho,delta sigma).
Its weight H is block diagonal: K and
[[1/rho_n,-rho_s/rho_n],[-rho_s/rho_n,rho_s rho/rho_n]].
H M is symmetric. Therefore e2_t+partial_x(z^T H M z/2)=0.
This quadratic result is not a full nonlinear internal-energy/entropy/FDT ledger.
Positive H symmetrizes the local ideal reference; it does not prove global
UET regularity or establish the physical EOS of He-II.

Replacing entropy current sigma v_n with sigma j/rho is an error control:
it discards relative entropy transport and breaks reciprocal work.
Reversing the superfluid chemical-potential sign must also fail work/stability.
These tests are specified before the first audit.

## Both sound branches and the reduced limit

For Fourier exp(lambda t+i k x), lambda=-i k times an eigenvalue of M.
The squared wave speeds solve

~~~text
c^4 - S c^2 + P = 0
S = rho A+2 sigma B+sigma^2 D/rho_n
P = sigma^2(rho_s/rho_n)(A D-B^2)

c_T^2 = (partial p/partial rho)_T = rho(A-B^2/D)
c_S^2 = (partial p/partial rho)_specific_entropy
      = rho A+2sigma B+sigma^2 D/rho
c_v = T/(rho D); c_p/c_v = c_S^2/c_T^2
v_entropy^2 = (rho_s/rho_n) T s^2/c_v
S = c_S^2+v_entropy^2; P = c_T^2 v_entropy^2
~~~

Finite thermal expansion mixes density and entropy modes. A zero total mass
current imposed throughout is not generally invariant: for delta rho=j=0,
j_t=-(rho B+sigma D)partial_x delta sigma. This nonzero local pressure drive
must not be hidden by a clamping operation.

At zero expansion rho B+sigma D=0, c_p=c_v and delta rho=j=0 is invariant.
The reduced counterflow pair from the previous reference is recovered, with
c2^2=(rho_s/rho_n)T s^2/c_p, provided the entropy branch is the slower one.
Away from this limit the full quartic, not that reduced equality, defines the
two modes. The usual low-speed/weak-mixing estimate needs its own error bound.

## SVP data are path derivatives, not a full local EOS

[NIST Donnelly–Barenghi review](https://srd.nist.gov/jpcrdreprint/1.556028.pdf),
Section 1 (1.2)-(1.6), Section 7 note (9),(11),(13), Section 8 note (8),(9):
density/expansion are along SVP; C_s is saturation-path heat capacity, and the
integrated entropy is obtained from C_s/T. Table 8.3 fountain-pressure entropy
and Table 8.5 heat-integrated entropy have different source roles.
The latter is derived from the calorimetry and is not independent of C_s.
None of these tables is ingested numerically in this wave.

Define c_sat=T d s/dT along p_path(T) for this entropy-based path record.
Maxwell ds=(c_p/T)dT-(alpha_p/rho)dp and
d rho/rho=-alpha_p dT+kappa_T dp give

~~~text
alpha_path = -(1/rho) d rho/dT|path
alpha_p = alpha_path+kappa_T p_path_prime
c_p = c_sat+(T alpha_p/rho)p_path_prime
c_p-c_v = T alpha_p^2/(rho kappa_T)
D = T/(rho c_v)
B = (D/rho)(alpha_p/kappa_T-sigma)
A = 1/(rho^2 kappa_T)+B^2/D
~~~

A calorimetric definition differing from T ds/dT must first be translated using
its stated heat/work protocol. Do not assign that derivative merely from a
column label. The NIST integration relation supplies the path convention here.

Two distinct positive kappa_T choices can reproduce the same rho,s,T,
alpha_path,c_sat,p_path_prime and their local SVP tangent while producing
different fixed-pressure EOS and sound poles. This is an underdetermination
witness for path-only inputs, not a claim that no independent material EOS exists.

The [material input requirements](Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json)
keep actual EOS/protocol values unassigned. Source-locked unit conversions:
g/cm^3 to kg/m^3 multiply by 1000; J/g K to J/kg K multiply by 1000;
the review's J/mol K to J/kg K multiplier is 249.837.
These conversions cannot supply missing fixed-pressure derivatives.

## Locked execution and admission boundary

[Contract](Data/03_Research/fluid_two_fluid_eos_reference_contract.json):
identity tolerance 1e-9; finite-difference thermodynamic derivative tolerance
1e-7 at steps 1e-3,1e-4,1e-5; negative-control floor 1e-8.
Wavenumbers 0.2 down to 0.003125 by halving. Periodic flux control N=32.
Base normalized rho=1,rho_s=0.6,sigma=0.8,T=1,A=9,B=-0.2,D=1.4.
Zero-expansion control changes B to -sigma D/rho without fitting.
Path witness rho=1,rho_s=0.6,s=0.8,T=1,c_sat=1.5,alpha_path=0.04,
p_path_prime=0.3,kappa_T=0.1 or 0.2; all synthetic.

A PASS establishes the declared standard reference and local path-input
underdetermination controls only. It does not implement an admitted UET
two-fluid state, physical J05/J06, material He-II prediction, attenuation,
source independence, trajectory, formal proof or Core/Topic 13 unlock.

Periodic local work controls use z=(0.1 sin x+0.04 cos 2x,
0.08 cos x+0.03 sin 3x,0.12 sin 2x+0.07 cos x,0.09 cos 2x+0.05 sin 3x).
The local Taylor internal-energy and mass-potential offsets are set to zero as
reference gauges; the positive T0 linear term is retained. No absolute material
energy/chemical potential is identified by this convention.

## Required Core-to-material thermodynamic bridge

Temperature and entropy are not two unconstrained new primitives: in this
reference T=e_sigma is an EOS conjugate. An actual Core coupling must provide
a source-locked physical Helmholtz density f_H(rho,T), or an equivalent EOS,
with explicit state transformation, SI scales and fixed-variable convention.
Then sigma=-partial f_H/partial T at fixed rho and e=f_H+T sigma define a
thermodynamic Legendre map where it is invertible. The normalized Core
Omega(C,Phi), its energy reference e0 and the He-4 alpha calibration do not
supply this map or its Hessian automatically. A superfluid phase/stiffness and
rho_s response mapping remain separate. Derived R/history traces cannot be
used as independent entropy reservoirs without a separately admitted ontology.

## Executed standard reference result

The audit passes 59 checks with warnings treated as errors; three focused
regression tests pass. No threshold or control was amended after preview.
For the normalized finite-expansion control the squared acoustic speeds are
1.2464504275 and 9.6735495725. The reduced slow estimate is 1.2591478697,
demonstrating that the reduced relation is not an exact general identity.
The pressure/entropy coupling coefficient is 0.92, so a pure entropy gradient
can drive total momentum even when j initially vanishes.

The path witnesses match rho'=-0.04, specific-entropy derivative=1.5,
T'=1 and p'=0.3. Their slow squared speeds are 0.6297999941 and
0.6245377687 with kappa_T=0.1 and 0.2. These are synthetic local witnesses,
not measurements or a claim about the size of He-II path corrections.
The [artifact](Result/artifacts/fluid_two_fluid_eos_reference_audit.json)
hashes the complete declared inputs and derivative/standard-state references.
The physical controller is unchanged; the narrower input obligation is
two_fluid_fixed_pressure_EOS_and_UET_state_mapping_missing.
