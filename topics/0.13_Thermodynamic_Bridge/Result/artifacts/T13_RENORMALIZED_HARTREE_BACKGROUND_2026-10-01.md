# Fixed-Phi finite Hartree potential and source-reoptimized background

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_FINITE_HARTREE_BACKGROUND_AND_SOURCE_BOUNDARY`, `CLOSED_FOR_LANE` for the explicitly named finite-potential candidate `t13.candidate.fixed_phi_hartree_ms_finite_potential_v1`. It is not full covariant renormalization or a replacement of the original Gaussian branch.

WHAT_IS_ACTUALLY_CLOSED: A vacuum-plus-thermal variational potential has a nonzero stationary amplitude and self-consistent internal propagator at both fixed witnesses. The source-reoptimized zero-momentum external transverse curvature vanishes and the radial curvature is positive. Entropy and canonical-charge pressure derivatives agree with the stationary envelope of this same potential.

WHAT_REMAINS_OPEN: Matching this finite prescription's counterterm tensor and running coefficients to the original action, joint Phi stationarity, global phase selection, finite-q/frequency external response/current vertices, controlled truncation/IR matching, normal component/SK/KMS/transport and independent material inputs.

DEPENDENCY_UNLOCKED: Counterterm and external-vertex completion design for this named candidate only. No full Topic13, funding or Core-composition promotion.

STATUS: `PASS_FIXED_PHI_HARTREE_SOURCE_BACKGROUND` in the [artifact](t13_renormalized_hartree_background.json). A locally stationary source candidate is not an admitted physical equilibrium state.

WHAT_CHANGED: Added the finite Hartree potential solver, seventeen independent/regression tests, this derivation and a generated artifact. The original Gaussian stationarity failure, failed tree lift and previous massless dynamic-composite result remain unchanged.

EQUATION_OR_MAPPING:

## 1. Canonical variables and declared scheme

At fixed Phi use v=sqrt(Z)*rho, s=v^2, u=lambda/Z^2 and r=mu^2-m(Phi)^2/Z. The canonical tree potential is `U(s)=-r*s/2+u*s^2/4`. C has not become mass/charge, Phi is not a metric or matter particle, and R_gen remains a derived trace. The mass variables a,b below are variational inverse-propagator coefficients, not new fundamental UET states.

Preserve T=0.22, Phi=0.15, Z=lambda=1 and mu=1.05/1.20 as the prior natural-unit witnesses. In this named approximation their numerical values are **trial renormalized coefficients at Q=1**. Bare-to-renormalized and material correspondence have not been established. They are not refitted and the original action/branch artifacts are not overwritten.

Q=1 is a renormalization convention, not an SI scale or independent temperature calibration. Changing Q while holding the coefficients fixed changes the prescription's values; this is not a physical RG-invariance test. The auxiliary subtraction mass M0 is different: changing it with Q fixed must leave the finite loop approximately unchanged and is checked explicitly.

Units: v,T,mu,Q,M0 have E; s,r,a,b and tadpoles have E^2; u,Z,lambda are dimensionless; potential/pressure have E^4; entropy and canonical charge have E^3. A renormalized tadpole can be negative after subtraction; it is not a positive noise covariance or a measured variance.

## 2. Stable Gaussian kernel and finite vacuum loops

For a,b>=0 use

```text
K(nu,k)=[[nu^2+k^2+a,-2mu*nu],[2mu*nu,nu^2+k^2+b]].
E_high^2=k^2+(a+b)/2+2mu^2+sqrt((a-b)^2+8mu^2(a+b)+16mu^4+16mu^2*k^2)/2.
E_low^2=(k^2+a)*(k^2+b)/E_high^2.
```

The product formula retains the small root without subtraction loss. No negative mass is clipped. Thermal tadpoles come from the mode residues; the thermal trace-log is `T*integral_k sum_j log(1-exp(-E_j/T))`. Direct matrix frequency sums provide an independent covariance check.

The vacuum pieces are not dropped. Let p_a=sqrt(k^2+a), p_b=sqrt(k^2+b) and W=sqrt(((p_a+p_b)/2)^2+mu^2)=(E_low+E_high)/2. The vacuum tadpole integrands are j_s=(p_a+p_b)/(4p_a W) and j_p=(p_a+p_b)/(4p_b W). Their derivatives satisfy `partial_a W=j_s/2` and `partial_b W=j_p/2`.

Physical squared masses in the subtraction are A=a+mu^2 and B=b+mu^2, not a,b alone. With E0=sqrt(k^2+M0^2) and d_s=A-M0^2, d_p=B-M0^2, define convergent residuals:

```text
R_s=j_s-1/(2E0)+d_s/(4E0^3), R_p=j_p-1/(2E0)+d_p/(4E0^3).
R_V=W-E0-(d_s+d_p)/(4E0)+(d_s^2+d_p^2)/(16E0^3).
I0=M0^2/(16pi^2)*(log(M0^2/Q^2)-1); I0'=log(M0^2/Q^2)/(16pi^2).
V0=M0^4/(64pi^2)*(log(M0^2/Q^2)-3/2).
I_s,vac=integral_k R_s+I0+d_s*I0', likewise p.
Omega_vac=integral_k R_V+2V0+(d_s+d_p)*I0/2+(d_s^2+d_p^2)*I0'/4.
```

All logarithms have dimensionless arguments. At equal physical masses below the condensation threshold, the vacuum result is independent of mu and reproduces the usual two-real-field finite terms. This check catches subtraction at shifted a,b, which would spuriously introduce chemical-potential dependence.

The numerical split K is not a physical regulator. The residual k^-5 tails are integrated analytically; split/order refinement tests the remaining k^-7 and higher contribution. Their coefficients are `[3d_s^2-2mu^2(d_s-d_p)]/16`, `[3d_p^2+2mu^2(d_s-d_p)]/16` and `[d_s^3+d_p^3-mu^2(d_s-d_p)^2]/32` for R_s,R_p,R_V. Increasing the split does not change an IR mass or filter a divergence.

Vacuum subtraction alone does not prove that the complete tensor of 2PI counterterms, source-dependent vertices or arbitrary superflow is matched. Those obligations remain explicit; the finite functional below is what is actually verified.

## 3. Variational Hartree potential and equations

Let I_s,I_p include the finite vacuum and thermal tadpoles, Omega_F their trace-log, and a0=-r+3u*s,b0=-r+u*s. Define

```text
D_H=u/4*(3I_s^2+2I_s I_p+3I_p^2).
F(s,a,b)=U(s)+Omega_F(a,b)+[(a0-a)I_s+(b0-b)I_p]/2+D_H.
partial_a Omega_F=I_s/2; partial_b Omega_F=I_p/2.
a=-r+3u*s+u*(3I_s+I_p).
b=-r+u*s+u*(I_s+3I_p).
B_field=-r+u*s+u*(3I_s+I_p)=0 for nonzero v.
```

The double-bubble coefficients follow from the connected Gaussian quartic contractions. The two gap equations cancel the mass derivatives of F; they are not coefficients selected to cancel a target residual. At field stationarity `a=2u*s` and `b=2u*(I_p-I_s)`.

The numerical solutions are approximately:

| mu | s | a | b | external radial curvature | internal low-frequency gap |
| --- | --- | --- | --- | --- | --- |
| 1.05 | 0.116732 | 0.233463 | 0.009692 | 0.204989 | 0.022052 |
| 1.20 | 0.449917 | 0.899834 | 0.012471 | 0.877155 | 0.041015 |

These are local stationary candidates at fixed Phi. The global phase minimum, finite-q stability and material identity have not been established. The finite vacuum terms change s relative to the earlier tree/thermal-only approximations; do not backfill them into the original calibration as though nothing changed.

## 4. Internal propagator is not external source response

Reoptimize a,b when varying the Cartesian mean field. The resulting potential F_bar depends on s=v_x^2+v_y^2. Thus its external transverse curvature is B_field and vanishes at the candidate. This is checked by separately solving the gaps at displaced fields and differentiating the potential, not by setting the internal b to zero.

Let J_ij=partial I_i/partial mass_j, C=[[3,1],[1,3]]. Differentiating the gap equations gives

```text
d(a,b)/ds=(1-u*C*J)^-1*u*(3,1).
dB_field/ds=u+u*(3,1)*J*d(a,b)/ds.
Gamma_external,radial=B_field+2s*dB_field/ds.
```

The implicit external radial curvatures differ from the fixed-mass internal a. Independent source-reoptimized second differences agree and the angular curvature approaches zero with field-step refinement. Forcing b=0 at the reported solution leaves nonzero gap residuals of about -0.00969/-0.01247. It is not a harmless Goldstone correction within this variational branch.

This closes neither a universal no-go nor a physical gapless finite-frequency mode. The external vertex equations at nonzero momentum/frequency are still needed. In particular, the internal gap **must not** replace the massless phase propagator in the preceding Cartesian-composite result to claim that the physical IR continuum disappeared.

## 5. Pressure, entropy and charge envelope

At simultaneous field/gap stationarity, derivatives of F_bar do not include a freely adjustable state response. The entropy `-partial_T F_bar` equals the bosonic entropy of the two internal quasiparticle modes, with the same potential and no fitted thermal coefficient. Independent re-solved and frozen-variational differences agree with it.

For canonical charge, vary mu with m(Phi)^2/Z fixed: r=mu^2-m(Phi)^2/Z changes. Holding r fixed instead is a different, incorrect thermodynamic protocol for this question. Re-solved and frozen-variational pressure derivatives agree. This canonical charge is not C, helium atom number or mass density without their missing mapping.

The energy definition epsilon=F_bar+T*S+mu*n is recorded only as a grand-canonical identity. It does not prove a dynamical energy ledger, entropy production, Onsager transport or dissipative balance.

## 6. Verification and source boundaries

The standard [Hartree renormalization reference](https://arxiv.org/pdf/1410.1337) distinguishes propagator/field counterterms and the role of symmetry-preserving regulators. [External-source reorganizations](https://arxiv.org/abs/1509.07847) motivate keeping internal and source response separate. This calculation does not implement the latter paper's symmetry-improved prescription or establish full covariant counterterm equivalence. Both references are method context, not material or TTG data.

Initial source-curvature checks failed at the unchanged 2e-5 relative criterion; rationalizing the vacuum differences and adding a finer field step fixed the numerical check. Independent vacuum reference tests then exposed a tail error at split 32. Increasing the integration split to 64 repaired those stricter tests without changing thresholds, renormalization convention, trial action coefficients or experimental inputs. The history is a numerical repair, not physical parameter tuning.

VERIFICATION: Seventeen tests cover MS finite vacuum terms and chemical-shift independence, auxiliary-reference refinement, direct frequency sums, vacuum/thermal derivative identities, quartic Wick coefficients, field/gap stationarity, variational mass derivatives, external-source Hessian, entropy/charge envelope, units, renormalization-scale dependence, no mass clipping, declared audit reads and protected baseline hashes. Related previous tests must pass before integration.

CONTROLLING_BLOCKER: `finite_potential_candidate_counterterm_and_external_dynamic_matching_not_closed`.

NEXT_ACTION: Match the counterterm projections and renormalized input to the action in this named branch; derive finite-q/frequency external/current vertex equations and their relation to the previous leading composite response. Then address joint Phi, global state/material admission and controlled transport/error. Do not call the internal propagator the physical response.

CLAIM_BOUNDARY: Fixed-Phi finite-potential stationary candidate only. Not exact UET equilibrium, full renormalization/RG matching, a physical Goldstone mass, independent helium/TTG prediction, global phase selection, microscopic SK/KMS or Full Topic13 closure. Holdout, original failures and Core-owner work remain untouched.
