# Finite-T phase cuts and static thermal coherence

MAJOR_RESULT_CLOSURE: `T13_FINITE_T_PHASE_CUT_AND_STATIC_THERMAL_COHERENCE`, `CLOSED_FOR_LANE`. Not Full Topic13, R1-R5 or Goal completion.

WHAT_IS_ACTUALLY_CLOSED: Leading-cubic-vertex pair and Landau cuts using the same candidate's internal tree acoustic curvature, with independent soft Bose-moment and vacuum controls. The LO static bubble plus tadpole equals the fully tree-relaxed flow-pressure derivative; omitting the bubble demonstrably fails this identity.

WHAT_REMAINS_OPEN: Full curved vertices/residues and near-shell real response, finite local Wilson/source matching, complete two-loop thermal sunset/mixed pressure/source/entropy derivatives, finite-T normal/heat/Kubo/SK-KMS/entropy transport, independent material/readout/scale and practical measurement feasibility.

DEPENDENCY_UNLOCKED: Matched real-response and thermal-sunset research only. No physical/Core/Gravity unlock; Core-owner composition and old conserved-C failure unchanged.

STATUS: `PASS_SCOPED_THERMAL_CUT_STIFFNESS`. [Artifact](t13_thermal_cut_stiffness.json) SHA-256 `9d92eb55ab0eb4b0074d13272d71c5a32be2b6c1fcc7a1ff0f15b9383725d89d`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Thermal_Cut_Stiffness.py), focused tests and [local registry](../../Data/03_Research/t13_thermal_cut_stiffness_registry.json). [Vacuum cut/log](T13_VACUUM_CUT_LOG_2026-10-03.md), interaction, tree-EFT and Core action evidence remain byte-identical. No parameter fitted or width assigned.

EQUATION_OR_MAPPING:

## 1. Scope, units and thermal cut factors

Use the named tree-matched classical-Phi phase EFT, not old Hartree. Its
canonical phase varphi is not UET Pi; Sigma is not Phi; collective C and
derived/observer traces R_gen/R_obs are not phase fluctuation states.
Natural T, E and q have E units, Sigma E^2, g_t/g_s E^-2 and quartic h E^-4.
No conversion to Kelvin or detector observable is supplied here.

For external k, E_k and vector r=k-p, the signed cubic vertex is

```text
M = 6 g_t E_k w_p E_r
  + 2 g_s [E_k (k.p-p^2) + w_p (k^2-k.p) + E_r k.p]
```

Pair: w_p=E_p, E_r=E_k-E_p; 0<p<k. Landau: w_p=-E_p,
E_r=E_k+E_p, p>0; the physical thermal incoming vector is -p.
The energy root determines r and cos(theta), not an angle fit.
At each node |cos(theta)|<1 and v_r=dE_r/dr>0 are required.

```text
I_pair = integral_0^k dp p r M^2/(E_p E_r v_r) * (1+n_p+n_r)
I_L    = integral_0^infinity dp p r M^2/(E_p E_r v_r) * (n_p-n_r)
gamma_pair = I_pair/(64 pi E_k k)
gamma_L    = I_L/(32 pi E_k k)
Gamma_occupation = 2 gamma_pole
Im Sigma_R(E_k,k) = -2 E_k (gamma_pair+gamma_L)
```

The Landau factor includes both signed scattering cuts; the identical
pair factor is half as large. Greater/lesser weights are
(1+n_p)(1+n_r)/n_p n_r for pair and n_p(1+n_r)/(1+n_p)n_r for Landau.
On the appropriate energy shell lesser=exp(-E_k/T)*greater and
(greater+lesser)/(greater-lesser)=coth(E_k/(2T)). These are cut-level
two-point identities, not full SK/KMS, stochastic noise or kinetic closure.
At T=0 pair agrees with the predecessor and Landau vanishes.

This combines LO vertices/canonical residues with exact-tree dispersion
only to resolve the near-shell support. It is not the full finite-q
parent loop: higher-derivative vertices, momentum-dependent residues and
source/current contacts remain to be matched. The static LO calculation
below consistently uses linear internal dispersion. Do not merge these
different approximation orders into a purported complete one-loop result.

## 2. Cancellation-free same-parent root

The first audit stopped on a naive pair r/k root outside support near an
endpoint. No artifact was accepted from it. Tiny curvature was lost to
root tolerance/subtraction; grids and gates were not changed.

For t=E(q)^2/q^2, a0=2sU, k_Phi=epsilon Z_Phi and V=V_curvature,

```text
den = a0 + ell H; ell=q^2(1-t)
H=1+gamma_action^2 s k_Phi/[V(V+k_Phi ell)]
t=c^2+q^2 d
d=4mu^2(1-t)H/[(a0+ell H+4mu^2)(a0+4mu^2)]
E(q)=cq + q^3 d/(sqrt(t)+c)
```

This is an algebraic rearrangement of the original tree inverse, not a
fitted/truncated energy series. Fixed-point/root agreement is checked
against the original independent parent root and inverse. Pair solves
r=k-p+delta with delta=k p(k-p)a, retaining its positive small displacement;
Landau solves r=p+kx retaining the curvature difference separately.
No clipping, endpoint padding or nonlocal filter is used. A nonconvergent
root or unsupported angle still fails, rather than being dropped.

## 3. Soft Landau result and what dominates

Let G=g_t+g_s/c^2. In the declared convex soft regime k<<T/c,
T/(c dispersion_scale)<<1, the collinear signed vertex becomes
M_L=-6G c^3 k p^2 to leading order. The independent Bose moment is
integral x^4 n(x)[1+n(x)] dx=4pi^4/15, giving

```text
gamma_L/(k T^4) -> 3pi^3 G^2/(10c^2)
```

The dilute nonrelativistic control g_t=0, g_s=1/(2m sqrt(chi)),
c^2=n/(m chi) gives 3pi^3/(40m n c^4). This checks normalization,
not the physical input for this relativistic-X candidate.

| mu E | soft coefficient E^-4 | finest coefficient relative error | pair/Landau at finest point |
| --- | --- | --- | --- |
| 1.05 | 8556.89977298 | .000734662330 | 5.01642422e-8 |
| 1.20 | 116.440341591 | .000633814395 | 5.01591801e-8 |

Thus Landau dominates pair at these soft/low-T witnesses, not throughout
all thermal regimes or in a material experiment. Numerical radial tails
and quadrature converge; the largest 32-versus-40 tail disagreement is
5.385e-10. This bounds only that numerical tail, not omitted EFT physics.
Strictly linear loop threshold limits do not justify replacing curved
internal kinematics with just an externally shifted frequency.

## 4. Static thermal consistency, including the bubble

At fixed mu and external h, let P_j=d_X^j P_tree(X,h), chi=2P1+4mu^2P2,
c^2=2P1/chi, J4=pi^2/(30c^3). Thermal covariance is J=J4 T^4 and
<grad varphi^2>_T=J/c^2 in this LO linear-propagator subtraction.

```text
Sigma_bubble(0,q)/(q^2 T^4) = -4 g_s^2 J4/c^2
Sigma_tadpole(0,q)/(q^2 T^4) = -2 h_m J4 - (20/3)h_s J4/c^2
Sigma_total(0,q)/(q^2 T^4) = -partial_xi^2 A4_flow|xi=0 / chi
```

The static bubble's apparent angular denominator has a removable zero:
its vertex contains the same (2qp cos(theta)-q^2) factor. Cancelling it
analytically is the exact static limit, not clipping a singular on-shell
integral. An independent radial/angular integral checks bubble+tadpole.

For Q=P1+2XP2, the flow determinant and density are AD+B^2=4P1 Q,
rho=2P1, D=2P1-4xi^2P2, with X=mu^2-xi^2. Differentiating the
independent A4_flow expression at xi=0 gives

```text
partial_xi^2 A4_flow = A4_flow [11P2/P1 - (9P2+6mu^2P3)/Q]
```

Substituting the tree-derived g_s, h_m and h_s proves the displayed
fixed-order P(X,h) identity algebraically. Reoptimized pressure finite
differences and independent angular mode pressure verify it numerically.

| mu E | total static coefficient E^-4 | finest pressure derivative relative error | omission of bubble |
| --- | --- | --- | --- |
| 1.05 | -516.562984158 | 4.186e-7 | 54.09% mismatch |
| 1.20 | -15.0116574168 | 9.525e-8 | 53.04% mismatch |

This closes a specific thermal response/thermodynamic coherence question.
Static derivatives are not dynamic poles, normal density tensor, heat
current, entropy production or the complete interacting thermal pressure.

VERIFICATION: Ten artifact checks, same preregistered mu=1.05/1.2, T=c*scale/(128,256,512), cq/T=.1/.05/.025, orders24/48/96, radial tails24/32/40 and FD steps.0004/.0002/.0001. Independent angular root, original-parent inverse, soft Bose moment/NR control, vacuum and factor-two limit, analytic/finite-difference/angular flow pressure, explicit static loop integral, missing-bubble and mismatched-energy negatives, free vertices and Phi-coordinate invariance. Runtime read allowlist and evidence/protected hashes checked; counts recorded in UPDATE_LOG. Original causal threshold 1e-6 unchanged; numerical convergence is not total physical error.

CONTROLLING_BLOCKER: `matched_curvature_real_response_and_full_thermal_sunset_open`.

NEXT_ACTION: Derive full same-parent curved real response with residues/vertices/source contacts and finite local matching; compute full thermal sunset/mixed pressure with source/entropy derivatives. Assess independent material/scale/readout feasibility in parallel. Keep 7 October science freeze and 11 October review; no automatic R1-R5 admission.

CLAIM_BOUNDARY: Candidate LO finite-T cut and static-loop consistency only. No material prediction, independent alpha, full kinetic/Kubo/SK-KMS/heat/entropy or complete quantum EOS/uncertainty closure. Core-owner composition unchanged; old conserved-C failure retained. No fit, assigned width, clipping, cone padding, action/ontology/threshold change or numeric Xie access; prior exposure REVIEW_REQUIRED, physical/global/full-Core flags false.

Primary method context: [Escobedo and Manuel, Sections III-V](https://arxiv.org/html/1004.2567v2) distinguish thermal loop contributions and sensitivity to internal dispersion near shell. The candidate formulas and numerical coefficients here are derived from the local relativistic-X pressure, not imported from their nonrelativistic systems.
