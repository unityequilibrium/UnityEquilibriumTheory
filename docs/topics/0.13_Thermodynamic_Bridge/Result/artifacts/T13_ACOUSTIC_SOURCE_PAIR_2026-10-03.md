# Off-shell acoustic pair and action-source response

MAJOR_RESULT_CLOSURE: `T13_ACOUSTIC_OFF_SHELL_PAIR_SOURCE_INTERFACE`, `CLOSED_FOR_LANE`. Not Full Topic13/R1/Goal completion.

WHAT_IS_ACTUALLY_CLOSED: Tree h-to-Phi susceptibility from the original parent, its static derivative and acoustic pole residue, and a positive off-shell two-acoustic pair spectral matrix dressed by that source. Its pole projection reproduces the previously derived acoustic attenuation.

WHAT_REMAINS_OPEN: Off-shell Landau and complete source/contact matching, principal-value and finite local real matching, heavy/all-mode quantum channels, complete thermal sunset/mixed pressure/source/entropy, physical material/readout/normalization/uncertainty and transport.

DEPENDENCY_UNLOCKED: Further source/real matching research only. No physical/Core/Gravity or owner-composition change.

STATUS: `PASS_SCOPED_PAIR_SOURCE_INTERFACE`. [Artifact](t13_acoustic_source_pair.json) SHA-256 `c151cc3d2b8342f3ab0b6569a68f40a58ce2d604d99a419e934556e605b4f025`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Acoustic_Source_Pair.py), tests and [local registry](../../Data/03_Research/t13_acoustic_source_pair_registry.json). [Modal predecessor](T13_ACOUSTIC_MODAL_CUTS_2026-10-03.md) and action unchanged. [First failure](t13_acoustic_source_pair_first_failure.json), SHA-256 `6b53e39b96e500ef0ef63c7afc9b75e5e5928a6f2ced04a9c0c7959290ff1843`, is retained as a historical numerical diagnostic; its original pre-repair source hash is not the current verifier hash and is not a current rerun certificate.

EQUATION_OR_MAPPING:

## 1. Source is declared in the action, not supplied by a detector fit

The original action contains +h Phi, with h an external nondynamical source.
For real fluctuation coordinates (sigma, pi_phase, phi), use the unchanged
tree inverse D from the modal predecessor. Set

```text
ell=q^2-omega^2
W=V_curvature+epsilon Z_Phi ell
den=ell+2us-gamma_action^2 s/W
chi_hh=e_Phi^T D^-1 e_Phi
      =1/W+gamma_action^2 s ell/[W^2(ell den-4mu^2 omega^2)]
```

This follows by eliminating sigma and phase, not by projecting the h source
onto a phase mode and dropping the other tree terms. Direct 3x3 inversion
independently checks the Schur expression away from poles. The source
normalization is the original +h Phi; h is not heat input or a detector field.

In natural units h has E^3, Phi E and chi_hh E^-2. Sigma/self-energy is not
Phi; pi_phase is not UET Pi. C/R_gen/R_obs are excluded. Heavy polarizations
are tree slaved, not new independent quantum Phi intermediate states.

For static omega=0 followed by q->0,

```text
dPhi/dh at fixed mu = [V_curvature-gamma_action^2/(2u)]^-1
```

This is also obtained by differentiating the same stationary source equation
and is checked by independently recomputing h+/-step states. It is not a
Kelvin calibration or a claim that static and dynamic limits commute.

At the acoustic pole the Phi-Phi residue is Z_pi B^2. A symmetric matrix
pole limit checks this separately from the phase-phase residue. The source
coupling is therefore fixed at tree level by the declared action, not an
extra arbitrary multiplier selected from the attenuation curve.

## 2. Off-shell pair matrix and its relation to the earlier on-shell result

Let T_ijk be the full shifted-parent cubic tensor and u(p),u(r) its normalized
positive-frequency acoustic modes. Define

```text
V_i(p,r)=T_ijk u_j(p) u_k(r)
R_pair(omega,q)=1/(32pi q) integral dp
 p r (1+n_p+n_r)/(E_p E_r v_r) V V^dagger
```

Here E_r=omega-E_p and r obeys strict momentum-triangle support. This
calculation admits omega>E(q) only for its off-shell grid. Convex/monotone
support at these witnesses gives p_min from E(p_min)+E(q+p_min)=omega,
and p_max=q+p_min. Nodes lie strictly inside; no clipped cosine or artificial
support extension is used. The separate on-shell control uses the earlier
cancellation-free same-parent pair root.

R_pair is Hermitian positive semidefinite as a weighted Gram matrix.
With the predecessor incoming-frequency convention,

```text
u(q)^dagger V = M_aaa^*
u(q)^dagger R_pair(E(q),q) u(q) = 2 E(q) gamma_pair
```

Thus the source matrix is tied to the already checked modal damping, not
a different normalization or assigned width. R_pair has E^2 units.

## 3. Dress the declared source and keep the real part open

With retarded forcing convention D(omega+i0), tree chi has positive absorptive
spectral weight. The cut adds the absorptive inverse contribution -i R_pair.
Away from the tree poles the leading pair contribution is

```text
d_h=D^-1 e_Phi
Im delta_chi_hh = d_h^dagger R_pair d_h >= 0
```

It is not the complete susceptibility. The dispersive principal-value part,
finite local/source/contact terms, Landau contribution and consistent
thermal pressure remain uncomputed. The pole is not dressed with an
assigned linewidth; source rows avoid it. No extrapolation of this acoustic
grid into a full ultraviolet loop or material spectrum is admitted.

Under Phi'=a Phi and h'=h/a, chi'_hh=a^2 chi_hh; the source spectral response
has the same covariance. Tests verify this, rather than wrongly requiring
coordinate-dependent susceptibility to be numerically invariant. A physical
readout coefficient would have to transform consistently and be admitted
independently; this result supplies no alpha_Phi_K.

## 4. Numerical failure and repair without changing acceptance

The first audit failed only the Gram-source agreement: contracting a rounded
binary64 matrix after summing cancels large terms, producing up to
1.80454e-8 relative error. Quadrature was already below 1.1e-11. Raising
quadrature order or loosening the 1e-9 identity threshold would not address
that cause. This Windows runtime's longdouble has binary64 precision.

The repair accumulates the same complex Gram matrix from the same binary64
samples with 50 decimal digits, then contracts it with the same source
vector. The independent per-node source-square integral agrees to
5.965e-14. The double-matrix error remains reported, not hidden. This is
precision for accumulation/contraction only, not a 50-digit root/vertex,
physical uncertainty bound or change of grid/threshold.

VERIFICATION: Six artifact checks; mu=1.05/1.2, q=.04/.02, omega/E(q)=1.1/1.5, T=0 and c*dispersion_scale/256, orders24/48/96, source steps1e-4/5e-5/2.5e-5 and pole offsets.01/.001/.0001 fixed before first audit. Max static derivative error4.003e-6; source residue1.505e-10; modal optical projection3.791e-13; quadrature1.015e-11. Direct matrix/Schur, stationary source derivative, Gram positivity/hermiticity, pole projection, complex orientation, coordinate covariance, decoupled source, support/energy/Bose and invalid-input tests, protected hashes and runtime file allowlist. Test counts in UPDATE_LOG; not full repo or external validation.

CONTROLLING_BLOCKER: `off_shell_Landau_local_real_source_contact_and_complete_thermal_sunset_open`.

NEXT_ACTION: Compute off-shell Landau/source/contact interface and the same-prescription dispersive/local matching, then complete thermal pressure/source/entropy. Independent material/readout/scale work remains separate; preserve 7/11 October and full Goal/R1-R5 acceptance.

CLAIM_BOUNDARY: Declared pair-source grid and tree h response only. No full source/real/thermal transport/KMS/EOS, detector/Kelvin mapping, physical prediction or global/Core promotion. No fitting, clipping/padding/filter, threshold/ontology/Core-owner change or Xie numeric access; prior exposure REVIEW_REQUIRED and old conserved-C failure unchanged. Imported quasiparticle method context is [Derezinski, Li and Napiorkowski](https://www.fuw.edu.pl/~derezins/damping_publ.pdf); their material coefficients are not inputs to this parent-derived source response.
