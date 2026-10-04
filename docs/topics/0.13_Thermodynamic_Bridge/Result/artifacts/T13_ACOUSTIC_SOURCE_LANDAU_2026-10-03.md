# Acoustic Landau source and conditional spectral-support bounds

MAJOR_RESULT_CLOSURE: `T13_ACOUSTIC_OFF_SHELL_LANDAU_SOURCE_AND_FLUX_BOUND`, `CLOSED_FOR_LANE`. Not Full Topic13/R1/Goal acceptance.

WHAT_IS_ACTUALLY_CLOSED: Conditional quadratic-parent energy-flux and sound lower bounds, the declared acoustic off-shell Landau Gram/source kernel, its independent on-shell optical projection, and combined pair/Landau absorption on the stated frequency grid.

WHAT_REMAINS_OPEN: Principal-value/local real and complete source/contact matching, all-mode quantum/heavy channels, complete thermal sunset/mixed pressure/source/entropy, finite-T normal/heat/Kubo/SK-KMS transport and independent material/readout/scale/uncertainty.

DEPENDENCY_UNLOCKED: Dispersive/source matching research only. No physical/Core/Gravity or owner-composition unlock.

STATUS: `PASS_SCOPED_LANDAU_SOURCE_INTERFACE`. [Artifact](t13_acoustic_source_Landau.json) SHA-256 `1d9337b1f7074fb90a6034f082017b39e07d32defbfbcd6d26520f2a126adbd2`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Acoustic_Source_Landau.py), tests and [three-entry local registry](../../Data/03_Research/t13_acoustic_source_Landau_registry.json). [Pair/source predecessor](T13_ACOUSTIC_SOURCE_PAIR_2026-10-03.md), modal and original action unchanged.

EQUATION_OR_MAPPING:

## 1. A conditional velocity bound, not a causal repair of conserved C

Use the constant rest-parent quadratic inverse for real coordinates
(sigma, pi_phase, phi). Let K=diag(1,1,epsilon Z_Phi)>0 and

```text
V0 = [[2us, 0, -gamma sqrt(s)],
      [0,   0,  0],
      [-gamma sqrt(s), 0, V_curvature]]
D(E,p) = V0 + (p^2-E^2)K + E L
L_sigma,phase=2i mu; L_phase,sigma=-2i mu
```

Assume s>0, u>0, V_curvature>0 and 2u V_curvature-gamma^2>0.
Then V0 is semidefinite with a positive radial/response block. Follow the
positive gapless acoustic branch continuously from E(0)=0, at mu>0 as in
the declared witnesses. For its polarization u_p, put
k_u=u_p^dagger K u_p, m_u=u_p^dagger V0 u_p. Differentiating the Hermitian
mode equation gives dE/dp=2p k_u/(2E k_u-u_p^dagger L u_p).
Using u_p^dagger D u_p=0 eliminates the gyroscopic term:

```text
H=(E^2+p^2) k_u + m_u >0
F=2 E p k_u
v_group=F/H
H-F=(E-p)^2 k_u + m_u >=0
```

Thus 0<=v_group<=1 conditionally. At finite p on this mu>0 acoustic branch
the radial mixing is nonzero and m_u>0, so the inequality is strict.
Integrating the slope bound gives |E(r)-E(p)|<|r-p|<=q on the Landau shell.
There is no Landau support at omega>=q for this branch. This reason is
independent of the finite thermal integration tail; unresolved numerical
support is recorded differently and never silently set to zero.

The normalized H/F quantities have spectral E^2 units, not SI energy/flux
density. A group-velocity bound is not by itself a nonlinear domain-of-
dependence proof, nor a proof for the original conserved-C thermal system.
No metric, C-as-mass or new R_gen state is introduced. pi_phase is not UET Pi.

## 2. Sound lower bound and the admitted frequency windows

For the same acoustic Schur root, define

```text
ell=p^2-E^2>=0; W=V_curvature+epsilon Z_Phi ell
A0=2s[u-gamma^2/(2 V_curvature)]>0
den=A0+ell[1+gamma^2 s epsilon Z_Phi/(V_curvature W)]>=A0
ell den=4mu^2 E^2
E^2/p^2=den/(den+4mu^2)>=A0/(A0+4mu^2)=c^2
```

Consequently E(p)>=c p. Pair support needs omega=E(p)+E(r)>=c(p+r)>=cq.
The declared omega/E(q)=.5/.9 rows satisfy omega<cq, so their pair channel
is absent by this conditional bound; omega/E(q)=1.001 lies above E(q)
and uses the already verified pair integral. The interval cq<=omega<=E(q)
is not filled in by assumption. The combined rows are the pair+Landau
absorption in these windows, not a complete spectral or retarded response.

The support endpoint construction assumes the selected monotone/convex
rest acoustic domain; the low-q curvature condition and all strict shell
roots are checked in this grid, not a global convexity theorem for all
branches/couplings or a full ultraviolet continuation.

## 3. Off-shell Landau matrix and source dressing

For omega>0, the absorption shell is E(r)=E(p)+omega with r=|p+q|.
At omega<E(q), p_min solves E(q-p_min)-E(p_min)=omega on [0,q/2].
At omega>E(q), it solves E(p_min+q)-E(p_min)=omega within the declared
momentum domain. If that bracket cannot resolve support, return unresolved.
On-shell controls have p_min=0 and do not dress the source at its tree pole.

Let T_ijk be the unchanged shifted-parent cubic tensor and u^-/u^+ the
negative-/positive-frequency acoustic polarizations with symplectic residue:

```text
V_L,i=T_ijk u^-_j(p) u^+_k(r)
R_L(omega,q)=1/(16pi q) integral dp
 p r (n_p-n_r)/(E_p E_r v_r) V_L V_L^dagger
u(q)^dagger R_L(E(q),q) u(q)=2 E(q) gamma_L
d_h=D^-1 e_Phi
Im delta_chi_hh^L=d_h^dagger R_L d_h>=0
```

The factor 1/(16pi q) includes the two Landau assignments; the modal
projection independently checks normalization against the earlier rate.
The positive Bose difference makes a Hermitian positive Gram matrix.
R_L has E^2 units; h E^3, Phi E and source chi E^-2 are the original action
lane, not a detector/heat/temperature identification. Heavy polarizations
are tree-slaved; this does not include independent quantum Phi/heavy loops.

Solve the shell by the cancellation-free same-parent c p plus curvature
rearrangement, independently cross-checking a direct angular brent root.
No clipped cosine, cone padding, modified dispersion or assigned width.
For stable accumulation, the inherited 50-digit Gram contraction uses the
same binary64 samples; it is not a 50-digit root or physical error bound.
Zero T and gamma=0 give explicit limits; nonpositive/underflowed thermal
weights are rejected rather than called absence of dynamical support.

Phi'=a Phi with h'=h/a gives chi'=a^2 chi; tests check this covariance.
It supplies no independent alpha_Phi_K. Bose detailed-balance/FDT controls
are cut-level identities, not complete open-system SK/KMS matching.

VERIFICATION: Eight artifact checks on mu=1.05/1.2, q=.04/.02, omega/E(q)=.5/.9/1.001, T=c*dispersion_scale/256 and /512, orders24/48/96 and tails32/40 fixed before the first audit. Twenty-four off-shell rows and eight on-shell controls. Max quadrature difference9.222e-13, tail difference1.436e-10, independent angular discrepancy4.873e-12, Gram difference5.704e-14, modal projection1.121e-11 and velocity finite-difference error1.262e-10. The source imaginary correction/tree ratio reaches1.484e-6; neither that ratio nor finite-tail differences establish total perturbative/truncation/physical uncertainty. Sixteen focused tests include positivity, coordinate/free/zero-T/invalid-input, artifact/protected hashes and audit-time Path read allowlist; final linked count is in UPDATE_LOG. No full repo/external validation. The read allowlist does not certify pristine historical blinding; prior context exposure remains REVIEW_REQUIRED.

CONTROLLING_BLOCKER: `local_real_source_contact_and_complete_thermal_sunset_matching_open`.

NEXT_ACTION: Derive dispersive/local/source-contact terms with the same action and matching prescription, then complete thermal pressure/source/entropy consistency. Carry independent material/readout/scale and measurement information separately; preserve 7/11 October, full Goal/R1-R5 and owner boundaries.

CLAIM_BOUNDARY: Declared acoustic absorption windows and conditional constant-quadratic-parent bounds only. No full real/source/thermal EOS, normal/Kubo/SK-KMS transport, Kelvin calibration, material prediction, original conserved-C causal repair or Full Topic13/global/Core promotion. No fit/clipping/filter/padding/threshold/ontology/owner edit or Xie numeric access; prior exposure REVIEW_REQUIRED. [Pitaevskii and Stringari](https://arxiv.org/abs/cond-mat/9708104) supply perturbative Bose Landau-damping context, not coefficients or a thermalization/physical validation claim for this parent.
