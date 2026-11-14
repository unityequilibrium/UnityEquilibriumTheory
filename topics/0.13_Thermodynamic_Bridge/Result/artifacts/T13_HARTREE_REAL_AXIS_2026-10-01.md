# Real-axis source response without assigned damping width

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_REAL_AXIS_RESPONSE` is `CLOSED_FOR_LANE` on the declared ten-point grid. This extends the unchanged named fixed-Phi Hartree candidate, not Full Topic13 or the full active research Goal.

WHAT_IS_ACTUALLY_CLOSED: Exact angular Cauchy/principal-value response and on-shell source cuts, independently checked by forward angular delta roots and a different radial phase-space integration. The generated [audit](t13_hartree_real_axis.json) also verifies full-domain radial subtraction, reoptimized source/current Ward, vacuum, reality and units on the declared grid.

WHAT_REMAINS_OPEN: Global collective poles and infrared/truncation control; full nonuniform covariant regulator/RG/action input; joint Phi/global state; independent material/source/detector normalization; normal component, physical heat current, collision transport and microscopic SK/KMS/entropy.

DEPENDENCY_UNLOCKED: Same-candidate global spectral/joint-state research only. No physical funding G1/G2 or Full Topic13 unlock and no change to the Core owner's recorded bounded O(2)/He-4 composition.

STATUS: `PASS_SCOPED_HARTREE_REAL_AXIS_RESPONSE`; artifact SHA-256 `a392cd0e1e45fd0b4e2b0db28136664b27e00b4338a083c7f0f9602c9fe5e148`. No claim of physical uncertainty or global stability follows from quadrature refinement.

WHAT_CHANGED: Added a separate real-axis evaluator instead of weakening the static/upper-half-plane validators of the predecessors. The trial renormalized inputs, stationary witnesses, actual current vertices, seagulls and vacuum source convention are unchanged.

EQUATION_OR_MAPPING:

## 1. Same poles, new integration coordinate

Use canonical O(2) varphi, not UET Phi, at fixed Phi. C remains collective, R_gen remains a derived history trace, and R_obs is not in the physical state. A is the predecessor's nondynamical O(2) current source, not a gauge particle or a new UET state. The internal Hartree masses a,b are not physical Goldstone masses; the preceding massless/composite IR results are retained.

The incoming momentum is k and the outgoing squared momentum is k2^2=k^2+q^2+2kq c. For each outgoing signed pole ell, inversion of the same determinant gives

```text
k2^2(ell)=ell^2-(a+b)/2+sigma*sqrt[(a-b)^2/4+4mu^2 ell^2].
sigma=+1 for low-energy poles, -1 for high-energy poles (mu>0).
dk2^2/dell=2ell*[1+sigma*2mu^2/sqrt((a-b)^2/4+4mu^2 ell^2)].
|dc/dell|=|dk2^2/dell|/(2kq).
```

For mu=0 keep the two field branches separately: k2^2=ell^2-m_field^2 and R_ell=-E_field/(2ell). This handles coincident equal masses without dividing by a vanishing quartic-pole derivative. The angular interval maps monotonically to signed-energy endpoints L,U, obtained at |k-q| and k+q. No internal gap, mass or cone is changed.

At mu>0 the residue numerators can be written `(b-a)/2+sigma*sqrtD` and `(a-b)/2+sigma*sqrtD`, with derivative `4ell*(-sigma*sqrtD-2mu^2)`. These exactly equal the original propagator residues and avoid subtracting large ell^2 terms in the UV.

## 2. Exact retarded Cauchy limit

Let p be the incoming signed pole, N(p)=sign(p)[n(|p|)+1/2], and let g include the ordered source matrix trace, N(p)-N(ell) and |dc/dell|. For a target ell_star=p+omega strictly inside (L,U), the angular integral is

```text
int_L^U g(ell)/(ell_star-ell+i0) dell
 = int_L^U [g(ell)-g(ell_star)]/(ell_star-ell) dell
   + g(ell_star)*log| (ell_star-L)/(ell_star-U) |
   - i*pi*g(ell_star).
```

Outside the interval an arbitrary constant subtraction, here the midpoint value, gives the same nonsingular integral and no imaginary jump. For upper-half-plane z evaluate the exact complex logarithm. `log1p((U-L)/(p+z-U))` equals the difference of logarithms on the retarded branch and avoids UV cancellation. The real-axis imaginary part is specified analytically as `-pi*g_star`, not obtained from a selected finite width.

In the compact artifact/formula relation, `g_star` means the on-shell value
inside the open interval and zero outside. The outside midpoint used by the
numerical Cauchy subtraction is not a spectral cut; subtracting and adding it
is exactly equivalent to the unsubtracted nonsingular integral. Exact endpoints
are excluded from this pointwise identity and handled as radial split limits.

The time-source vertex is `V0=-(2p+z)J+2i mu I`; the longitudinal one is `Vlong=-2i*(k*c+q/2)J`. The predecessor's frequency-moment polynomial contributes a nonzero time/time contact `-2 Tr(I_cov(P+Q))` after the incoming pole sum. This survives and is integrated explicitly; it is not discarded by evaluating only the pole numerator at p.

Opposite-sign incoming/outgoing poles define pair cuts; same-sign poles define scattering cuts. The latter vanish at T=0 in these stable internal propagators. Continuum absorption is not a derived collision width, relaxation time, Kubo coefficient or entropy-production law.

## 3. Independent phase-space calculation

The cross-check does not call the inverse-shell or Cauchy primitive. For each incoming pole it solves the **forward** outgoing dispersion equation `ell(k2(c))=p+omega` with a bracketed angular root. Its delta Jacobian is

```text
|dell/dc| = kq*|1 +/- 4mu^2/D_k2|/|ell|,
D_k2=sqrt[(a-b)^2+8mu^2(a+b)+16mu^4+16mu^2*k2^2].
```

The plus sign belongs to the high mode and minus to the low. At mu=0 use kq/|ell|. A central difference independently checks the derivative. Ordered original pole-residue matrices and original vertices form the delta-function cut. A second radial calculation uses a tangent momentum map and these forward roots, without a PV integral. It shares the declared propagator/action and kinematic split locations, but not the inverse-energy root or angular/PV/radial quadrature implementation.

For the joint source order (mass0,mass1,mass2,time,long), `S=diag(1,1,1,-1,1)` because the time insertion is anti-Hermitian at real frequency. The spectral density is `(B_R-S B_R^dagger S)/(2i)`, not the elementwise imaginary part of every mixed matrix. In particular the equal-mass vacuum mass bubble cut is the **real** scalar `-sign(omega)*beta/(16pi)`, where `beta=sqrt(1-4m^2/(omega^2-q^2))` above the pair threshold; its contribution to the retarded bubble is i times that density.

For the current, continue A0=i A_density with D=diag(i,1,1,1) and form `rho_phys=(D Pi D-(D Pi D)^dagger)/(2i)`. Positive `-rho_phys` is checked only on the declared positive-frequency grid, without changing eigenvalues or projecting the tensor. In the stored Euclidean-source convention, the time continuation and spatial parity combine to give `Pi(-omega,q)=Pi(omega,q)^*` in this rest frame. This is not an additional Ward projection.

## 4. Vacuum subtraction and radial domain

Keep the previously declared vacuum/thermal loop subtraction, current plus seagull subtraction, independent 4D Feynman reference and analytic spatial surface `[Tr(M)-2M0^2]/(24pi^2)`. The finite F_A^2 coefficient remains zero at Qren=1 **as a convention**, not a measured microscopic input. The real-axis reference uses split log singularities and the analytic pair jump, not a finite eta.

Angular endpoint singularities are radial **integration splits**, not removed momentum intervals. Every k from zero to infinity remains included. In compact x=k/(mapping+k), finite intervals use a sine-square map; the last interval uses

```text
x=lo+(1-lo)*(1-sqrt(1-u^2)), 0<u<1.
dx/du=(1-lo)*u/sqrt(1-u^2).
```

This makes k grow as `(1-u)^(-1/2)` and regularizes the convergent subtracted `dk/k^3` UV tail in quadrature coordinates. It is an exact change of variable, not a physical cutoff, nonlocal filter, padding or fitted subtraction. The first exploratory map amplified cancellation when order increased; that failure motivated the exact log/residue/coordinate identities, not threshold relaxation. Exact radial nodes on cut endpoints are refused; no singular value is clipped. Endpoint scanning at 512/1024 agrees on the declared grid but is not a theorem that all endpoints have been found at arbitrary parameters/asymptotic thresholds.

All quantities remain in the canonical natural-unit lane: momenta/frequencies/T/mu/A have E; a,b,s have E^2; residues have E^-1 and dc/dell has E^-1. Thus g_mass has E^-3, g_mixed E^-2 and g_current E^-1. The radial measure has E^3, giving bubble dimensionless, mixed E and current E^2. No SI calibration is supplied.

## 5. Same reoptimization, limited admission

Use the predecessor's covariance Bethe-Salpeter and mean-field equations with the newly calculated real-axis loops. In particular

```text
Gamma_field=G_int^-1+L^T J_F (I-K_H J_F)^-1 L/2.
Pi=Gamma_AA-Gamma_Aphi Gamma_field^-1 Gamma_phiA.
```

There is no projector, pseudoinverse or imposed zero mass. A singular collective inverse outside the declared grid is not repaired here. The evaluator requires q>0; the uniform Goldstone/transport limit is a separate question. Checking transversality, positive loss and loop convergence at ten points does not establish global pole absence, continuum well-posedness, a controlled Hartree remainder or physical uncertainty.

VERIFICATION: 178 linked Topic13/Core/planning tests passed, including seventeen real-axis tests. Direct forward-shell/delta roots, independent upper-half-plane angular and committed loop methods, integrated phase space, 4D vacuum below/above threshold, source/current Ward, endpoint/order refinement, reference independence, signed frequency, energy scaling, absent cold scattering and predecessor/protected hashes all passed. Maximum point-cut disagreement is 4.55e-13, integrated independent-cut disagreement <=6.94e-17, last loop refinement <=3.63e-6, Ward <=1.72e-7 and 4D vacuum-current discrepancy <=7.05e-8. These are numerical discrepancies, not physical uncertainties or certified remainder bounds. The eta sequence is verification only; production real-axis eta is exactly zero. Source reads are limited to the committed current artifact; no numeric empirical or holdout source is consumed.

CONTROLLING_BLOCKER: `global_spectral_truncation_regulator_joint_Phi_material_and_transport_matching_not_closed`.

NEXT_ACTION: Analyze global collective/IR and approximation/regulator/action limits, then joint Phi/material/source/detector and heat-current matching. Do not repeat the same grid merely to accumulate results. R1 full acceptance, portfolio dates and model recommendations are unchanged by this scoped calculation.

CLAIM_BOUNDARY: Conditional fixed-Phi rest-frame source response, not physical thermal prediction, collision damping, full Kubo/SK/KMS/entropy, repaired causal leakage, full Topic13 or global UET closure. No target fit, artificial width/mass, filter, clipping, threshold change, new numeric holdout read or Core-owner edit. Prior Xie exposure remains REVIEW_REQUIRED.

## Method Context

The source/external-action distinction follows [van Hees and Knoll](https://arxiv.org/pdf/hep-ph/0203008). Pair/scattering spectral cuts and the distinction between branch-cut response and assumed Markovian relaxation have established method context in [Boyanovsky et al., scalar QED](https://arxiv.org/pdf/hep-ph/9802370), section IV. That paper's model and HTL/transport results are not imported as UET evidence. Neither source establishes novelty or material validation for this local Hartree calculation; their Phi functional is not UET Phi.
