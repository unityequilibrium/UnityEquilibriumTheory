# Thermal source response has a conserving Gaussian Noether completion

MAJOR_RESULT_CLOSURE: `T13_GAUSSIAN_THERMAL_SOURCE_NOETHER_BALANCE`, `CLOSED_FOR_LANE` in the existing named acoustic thermal-insertion branch. Not Full Topic13/R1/Goal or full dissipative closure.

WHAT_IS_ACTUALLY_CLOSED: Pair-local charge continuity and first-order rotating/physical energy continuity after combining covariance response with the action-derived mean correction, seagull and stationary background shift. The fluctuation current alone is not the conserved total current.

WHAT_REMAINS_OPEN: Collisionless soft-frequency limits; full interacting/vacuum/thermal matching and approximation control; second-order source work, entropy and dissipation; physical collision/heat/Kubo/SK-KMS and independent material/source/readout/scale/uncertainty. A momentum-domain translation assumption is needed for the continuum interpretation below; this audit does not numerically integrate the current over a finite shifted cutoff.

DEPENDENCY_UNLOCKED: Collisionless-limit and actual thermal-source/readout research only. No Core/Gravity/owner-composition or physical-material admission.

STATUS: `PASS_SCOPED_GAUSSIAN_NOETHER_RESPONSE`. [Artifact](t13_thermal_noether_response.json), SHA-256 `2765fdd0b0fe83bbed54c4af2fa3fde32f40694d109ea37978b0f7b5ec268906`.

WHAT_CHANGED: Separate [Noether calculation](../../Code/03_Research/Research_T13_Thermal_Noether_Response.py), [tests](../../Code/03_Research/test_t13_thermal_noether_response.py) and [registry](../../Data/03_Research/t13_thermal_noether_response_registry.json). The [finite-q predecessor](T13_FINITE_Q_THERMAL_SOURCE_2026-10-03.md), parent action, thermal populations and source convention are unchanged.

EQUATION_OR_MAPPING:

## 1. Noether charge belongs to the declared matter lane

Write the normalized matter field as (v+sigma+i*pi_phase)/sqrt(2),
v=sqrt(s), in the rest frame with chemical parameter mu. From the
same action, for the convention dot=-iz and grad_z=iq:

```text
n=mu[(v+sigma)^2+pi_phase^2]
  +(v+sigma) dot_pi_phase-pi_phase dot_sigma
j=-(v+sigma) grad_pi_phase+pi_phase grad_sigma
n_linear=v(2mu sigma+dot_pi_phase)
j_linear=-v grad_pi_phase
```

This is an O(2) Noether charge, not a new meaning of C, mass or R_gen.
pi_phase is not UET Pi. Covariance velocities are auxiliary Gaussian
coordinates, not additions to UET ontology or an observer state.

For r_vector=p_vector+q_vector and X=delta_Cov(r,-p), the symmetrized
quadratic moments are

```text
n_cov=mu(X_sigma,sigma+X_pi,pi)
      +(X_sigma,vpi+X_vpi,sigma-X_pi,vsigma-X_vsigma,pi)/2
j_cov,z=i(p_z+r_z)(X_sigma,pi-X_pi,sigma)/2
```

Use both initial acoustic Bose covariances in the predecessor's actual
36-component two-momentum equation. No new width or relaxation input is
introduced. The position-velocity equilibrium block is antisymmetric;
its symmetric contraction with a potential perturbation vanishes.

## 2. The stationary shift is necessary, not a fitted repair

Let Cbar=(Cov_p+Cov_r)/2 and use the same cubic/quartic tensors T/Q:

```text
f_i=T_iab Cbar_ab/2
S_ij=Q_ijab Cbar_ab/2
V0_active delta_x=-f_active, delta_x_pi=0
M_ij=S_ij+T_ijk delta_x_k
d=D(z,q)^-1 e_Phi
delta_f_i=T_iab X_ab/2=-B_ij d_j
delta_d=D(z,q)^-1[-delta_f-M d]
```

The direct covariance force and separately implemented spectral bubble
agree. The contact computed from Cbar agrees independently with the
weighted average of the two predecessor modal contacts.

O(2) potential identities imply

```text
v M_pi,pi=v S_pi,pi-f_sigma
M_pi,sigma=M_pi,Phi=0
-iz n_cov+iq j_cov=v(delta_f_pi+M_pi,j d_j)
```

The source-corrected mean contribution has the opposite divergence:

```text
n_mean=v(2mu delta_d_sigma-iz delta_d_pi)
       +delta_x_sigma(2mu d_sigma-iz d_pi)
j_mean=-iq(v delta_d_pi+delta_x_sigma d_pi)
-iz(n_cov+n_mean)+iq(j_cov+j_mean)=0
```

The delta_x_sigma terms retain the change in the charge/current operator,
even though their divergence vanishes by the tree source equation.
Dropping the stationary-background part of M fails this identity in
the deliberately incorrect control. No coefficient was chosen to make
the Ward residual small.

This is a pair-local identity: the contact average contains both p and r
thermal populations. On the full translation-invariant momentum domain,
integrating their average gives the homogeneous thermal contact already
used by the source prescription. A finite cutoff cannot be translated
silently; boundary/regularization effects must be tracked. Pointwise
tests here are not a finite-cutoff integrated transport certificate or a
proof of all interacting Ward identities.

## 3. Conserved first-order energy is not dissipative heating

The gyroscopic term is absent from the rotating-frame quadratic energy.
With K=diag(1,1,epsilon*Z_Phi) and the original V0:

```text
delta_H_rot=[(V0+p_vector.dot(r_vector)K):X_xx+K:X_vv]/2
delta_F_rot,z=i[p_z K:X_vx-r_z K:X_xv]/2
```

Direct Euler evolution for an arbitrary complex cross-covariance obeys
the energy-current identity, independently of solving the source response.
The source drive has no first-order average rotating-energy work in the
stationary Gaussian covariance. The explicit potential contact f.dot(d)
is canceled by the independently computed mean contact
(V0 delta_x).dot(d)=-f.dot(d). Consequently:

```text
-iz delta_H_rot+iq delta_F_rot=0
delta_E=delta_H_rot+mu delta_n_total
delta_F=delta_F_rot+mu delta_j_total
-iz delta_E+iq delta_F=0
```

Energy here is the natural-energy Noether ledger of this action, not
experimental SI heat or a temperature observable. About stationary h0=0,
internal source power h dot(Phi) begins at second perturbative order.
For an energy definition including -h Phi, explicit source work instead
contains -dot(h) Phi. The present first-order audit does not compute
second-order absorption, thermalization, entropy production or heat
conductivity. Nonzero background h is rejected rather than silently
applying this boundary to a different energy bookkeeping convention.

## 4. Numerical and claim boundaries

The 48 declared source rows use mu1.05/1.2, T.002/.004,
(p,r,q)=(.005,.011,.008),(.02,.031,.02),(.04,.037,.02),(.02,.02,0),
and z=.02i/.05i/.03+.02i. Ward1e-9, method1e-7 and negative-control
minimum1e-3 are declared before the first audit. Original causal leakage
threshold1e-6 is unchanged and is not rerun/passed here.

Energy residuals use the sum of the absolute operator terms, not a
relative error against an analytically zero q0 energy response. This
definition was fixed before the first completed audit; no gate was
relaxed after a failure. The first audit passed. Registry status and
additional stationary-energy/contact and h0-domain checks were then
completed and the final artifact regenerated.

VERIFICATION: Eight artifact checks. Maximum fluctuation-torque residual2.261e-11, total-charge Ward1.433e-12, rotating-energy6.379e-14 and physical-energy1.433e-12. Independent force5.965e-15 and contact3.878e-16; phase-contact identity1.097e-16. Omitted-background control reaches1983.96 relative to the correct response's raw Ward-term scale; this is not a probability or physical error estimate. Tests independently check arbitrary-covariance Euler identities, stationary drive, energy-contact cancellation, coordinate rescaling, zero-T/decoupling, physical triangle/q0 and rejected real-frequency/moving/nonzero-h inputs. Artifact/hash/registry and audit-time Path allowlist retained; final linked count is recorded in UPDATE_LOG. No external/model/whole-repository or continuum-interacting validation.

CONTROLLING_BLOCKER: `collisionless_soft_limit_full_interacting_energy_and_physical_transport_open`.

NEXT_ACTION: Derive the soft-frequency/long-wavelength regime and a true heat-source/readout operator, then independent material scale. Full interacting/vacuum and second-order work/entropy/transport remain separate obligations; do not infer a collision rate from static Bose variance. Preserve7/11 October and full Goal/R1-R5 criteria.

CLAIM_BOUNDARY: Named acoustic-populated Gaussian first-order Noether completion only. Heavy tree propagation remains virtual; no heavy quantum thermal/vacuum admission, signed-C reinterpretation, R_gen backreaction, material alpha, fit, assigned rate, clipping/padding/filter, threshold/Core-owner change or numeric holdout read. Prior exposure REVIEW_REQUIRED; original conserved-C failure retained. [Baym-Kadanoff](https://journals.aps.org/pr/abstract/10.1103/PhysRev.124.287) motivates testing conservation in response approximations; [Morgan](https://arxiv.org/abs/cond-mat/0307246) distinguishes collisionless finite-temperature response with directly driven thermal fluctuations. Their public abstracts are context, not a proof of this prescription, imported transport input or novelty/experimental validation.
