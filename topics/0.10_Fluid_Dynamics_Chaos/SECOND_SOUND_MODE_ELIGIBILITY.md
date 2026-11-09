# Topic 10: hydrodynamic second-sound mode eligibility

Date: 2026-09-30. Scope: conditional linearized reference boundary, not physical
He-II prediction, full nonlinear no-go or Core admission.
Overall controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Coupled branch question: can the current isothermal single-velocity candidate
supply the hydrodynamic counterflow acoustic pair required by J02/J06?

## State/source/units record before code

Use the existing [vector contract](VECTOR_STATE_RESEARCH_CONTRACT.md) and its
[registered candidate](../../core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_vector_state_addendum.json).
C,Phi,Q,u retain their meanings. The [conditional action](VECTOR_VARIATIONAL_ORIGIN.md)
does not assign Phi to temperature or Q to entropy flux. No new UET operator or
material parameter is introduced here.

The canonical scalar source and parent normalized controls supply all candidate
coefficients. The mean C0=0.7 is a synthetic conserved-state control.
Phi0 solves mu_Phi(C0,Phi0)=0; mu_C may be constant nonzero because C is conserved.
The homogeneous state is at rest, with no sources, vortices or boundary forcing.
For the scoped stable branch require D>0, A D-B^2>0, finite positive mobility,
tau and rho0, and constant nonnegative eta. Do not apply the conclusion to an
unregistered massless, undamped, critical or singular coefficient limit.

The Fourier symbol concerns the local continuum or a family of increasing domain
lengths, allowing k to approach zero. It is not a grid/time trajectory or a claim
that arbitrarily small k exists on the fixed [0,2*pi) control box.

Method source:
[Nikuni and Griffin, Section IV equations (86)-(88), Appendix C equations (C1)-(C10)](https://arxiv.org/abs/cond-mat/0009333).
Their general Landau-Khalatnikov mode/entropy structure is used; dilute-gas
coefficients and trap assumptions are not assigned to liquid He-II.
The liquid-He-II data/protocol remains
[Topic 13 J02](../0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md).
No recommended speed row, alpha, Z, theta_T, e0 or measured eta is used in this
mode-eligibility calculation.

Candidate matrices and numerical two-fluid controls are normalized. The
reference state delta T,w is a separate standard-physics state, not a
reinterpretation of C,Phi,Q,u. Its SI dimension targets are:
rho_s,rho_n in kg/m^3; s and c_p per mass in J/(kg K); T in K;
w=v_n-v_s in m/s; a in K; b in m^2/(s^2 K);
c2^2=a b in m^2/s^2; diffusion constants in m^2/s.
All numerical values for this reference are explicitly synthetic, not He-4 data.

## Linearization of the current candidate

Let c,phi,q be small perturbations and lambda the growth rate in
exp(lambda t+i k x). Define

~~~text
A = a_C + 3 b_C C0^2 - g Phi0
B = -g C0
D = a_Phi + 3 b_Phi Phi0^2
A_k = A+kappa_C k^2; D_k = D+kappa_Phi k^2
d = M_C k^2; alpha = M_Phi/tau; gamma = 1/tau
L_scalar =
[ -d A_k,       -d B,          0 ]
[      0,           0,          1 ]
[ -alpha B, -alpha D_k,    -gamma ]
P(lambda,k) = (lambda+d A_k)(lambda^2+gamma lambda+alpha D_k)
              -d alpha B^2
~~~

The first-order scalar force is mu_C0 grad c+mu_Phi0 grad phi,
an exact gradient. Pressure projection removes it for incompressible flow.
The transverse velocity therefore decouples with lambda_shear=-eta k^2/rho0.
There is no longitudinal common velocity for k !=0 under div u=0.
This does not exclude longitudinal relative counterflow in a *different*
two-fluid state with zero net mass current.

At k=0 the scalar roots are 0 and the roots of
lambda^2+gamma lambda+alpha D=0. Since alpha D>0, the zero scalar root
is simple. The implicit-function expansion in z=k^2 gives

~~~text
lambda_slow = -M_C (A-B^2/D) k^2 + O(k^4)
~~~

The other scalar roots stay away from zero; transverse modes are diffusive.
Thus this rest-frame stable candidate has no pair
lambda_plus/minus=+/-i c2 |k|+O(k^2), c2>0, approaching zero.
This is a conditional algebraic exclusion of the hydrodynamic second-sound
branch, not evidence against every UET extension, every finite-frequency
resonance, or nonlinear pattern propagation.

Matrix parity alone is not a proof: a massless undamped scalar with a nilpotent
zero-frequency block can have +/-i c |k| even when matrix entries use k^2.
The argument above uses the simple scalar zero root, finite gap and decoupled
shear block. A massless-undamped wave is retained as an out-of-contract positive
control to prevent a blanket no-go inference.

A uniform mean flow Doppler shifts lambda by -i U k. A diffusive mode can then
have apparent phase speed U. Removing the rest-frame shift must restore the
nonacoustic result; bulk advection is not the counterpropagating second-sound pair.
Finite nonsingular unit conversions and local state changes preserve the
eigenvalues up to finite rate/wavenumber scales; they cannot create an absent
hydrodynamic pole pair.

## Separate counterflow reference and quadratic work

For the low-expansion, constant-pressure, vortex-free ideal two-fluid limit,
use w=v_n-v_s and zero net mass current:
v_n=(rho_s/rho)w, v_s=-(rho_n/rho)w.
With specific entropy s, delta s=(c_p/T)delta T:

~~~text
partial_t delta T = -a partial_x w; a=(rho_s/rho) T s/c_p
partial_t w       = -b partial_x delta T; b=(rho/rho_n) s
c2^2 = a b = (rho_s/rho_n) T s^2/c_p
lambda_plus/minus = +/-i c2 |k|
~~~

These equations are a reduced *standard-physics reference*, not a complete
two-fluid UET model or an exact source-matched He-II eigenmode.
Thermal expansion, compressible first/second-sound mixing, vortices, finite
mean counterflow, frequency-dependent transport and measurement boundaries
require separate admission/protocol records.

The positive quadratic wave-availability weights are
H_T=rho c_p/T and H_w=rho_s rho_n/rho. They satisfy
H_T a=H_w b=rho_s s. For periodic ideal reference fields,

~~~text
E_wave = integral [H_T (delta T)^2/2+H_w w^2/2] dx
J_wave = rho_s s delta T w
partial_t e_wave+partial_x J_wave=0
~~~

This is a perturbation-availability/work balance, not the full SI internal-energy
or entropy ledger. Optional synthetic diagonal diffusion gives
dE_wave/dt=-integral[H_T D_T |grad delta T|^2+H_w D_w |grad w|^2] dx,
with acoustic damping O(k^2). D_w is a reference diffusion coefficient, not
the measured normal shear viscosity or an admitted physical two-fluid tensor.
The microscopic entropy production/FDT coefficients remain open.

## Locked verification and required disposition

The [contract](Data/03_Research/fluid_second_sound_mode_eligibility_contract.json)
locks wavenumbers 0.2 down to 0.003125 by halving, polynomial/eigen residual
tolerance 1e-9, Hessian finite-derivative tolerance 1e-7, small-k slope tolerance
1e-3 on the finest point, and control sensitivity floor 1e-8 before code.

Tests must compare canonical Hessian derivatives, matrix characteristic roots,
slow diffusive slope/gapped roots, transverse projection, ideal/damped two-fluid
acoustic branches and positive wave-work symmetrizer. Doppler advection,
clamped relative motion and massless-undamped scalar controls distinguish the
excluded branch from apparent or out-of-scope waves. No PDE solution is evolved.

On an exclusion result, keep the single-velocity proposal as a bounded
isothermal/scalar-fluid reference. Do not fit its oscillator frequency to the
20.33 m/s table or label it second sound. Before J02/J05/J06 physical execution,
register a separate entropy/temperature/relative-velocity (and superfluid
phase/chemical-potential) dynamics with material EOS, transport and observables.
Existing Topic 13 natural-unit relative-flow contact response is not a complete
He-II hydrodynamic eigenmode or source-independent SI transport tensor.

No Core/Topic 13 status promotion or dependency unlock follows from this audit.

## Verifier integrity repair

The first preview printed nominal PASS on 123 checks but emitted a ComplexWarning:
its imported real-only RMS used mean(a**2) on complex work matrices. That metric
cannot establish the complex symmetrizer result. The complete preview is retained
as [invalid diagnostic](Result/artifacts/fluid_second_sound_mode_initial_metric_diagnostic.json),
with its original payload/hash; it is not accepted evidence.

The corrected verifier uses sqrt(mean(abs(a)**2)) locally, without changing the
older source-hashed vector/action helpers. Pure-imaginary matrix defects and a
wrong reciprocal counterflow sign are explicit sensitivity controls; the latter
must violate wave work and create a real unstable branch. These controls were
added after preview as a harness repair, not blind preregistration. All original
numerical controls and tolerances remain unchanged. A failed audit reports
UNRESOLVED_AUDIT_FAILED rather than a candidate exclusion.

## Executed reference result

The repaired audit passes 139/139 controls with warnings treated as errors.
For the synthetic C0=0.7, Phi0=0.0610227648 branch, the predicted slow coefficient
is 0.4244576512; at k=0.003125 the measured -lambda_slow/k^2 is 0.4244675851.
The k=0 fast roots are -0.5 +/-0.8724513359 i and remain gapped.
These normalized numbers have no assigned He-II units.

The separate two-fluid positive control has c2=sqrt(1.5)=1.2247448714 normalized,
with synthetic attenuation coefficient 0.09. Correct ideal/damped work matrices
pass the complex magnitude norm, while reversed reciprocal sign is detected.
[Current artifact](Result/artifacts/fluid_second_sound_mode_eligibility_audit.json)
is source hashed; three regression tests rerun it and retain the invalid preview.
The narrower coupled controller is
isothermal_single_velocity_candidate_counterflow_acoustic_mode_missing.
Physical admission and independent primary response inputs remain blocked.
