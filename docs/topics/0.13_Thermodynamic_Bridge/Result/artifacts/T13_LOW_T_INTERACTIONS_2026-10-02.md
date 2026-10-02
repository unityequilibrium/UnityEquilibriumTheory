# Low-T phase interaction kernels and the first derived attenuation mechanism

MAJOR_RESULT_CLOSURE: `T13_LOW_T_PHASE_INTERACTION_AND_DECAY_KERNEL`, `CLOSED_FOR_LANE`. This closes candidate calculations, not Full Topic13/R1 or physical acceptance.

WHAT_IS_ACTUALLY_CLOSED: Canonical cubic/quartic vertices of the joint tree pressure, next tree dispersion and its one-phase-loop T8 thermal term, one explicitly subtracted quartic thermal-thermal contribution, and a leading T=0 Beliaev decay kernel. Direct stationary pressure, phase-space integration, independent Bose/Wick moments and a known nonrelativistic limit check the results. On-shell energy and Bose detailed balance hold without an assigned width.

WHAT_REMAINS_OPEN: Renormalized cubic-sunset pressure, mixed vacuum/thermal terms, Wilson input and real self-energy, complete finite-q vertices/residues, finite-T collisions/normal component/heat/Kubo/SK-KMS/entropy transport, independent material/source/readout/temperature scale. A small calculated quartic contribution is not an error bound for uncalculated terms.

DEPENDENCY_UNLOCKED: Calculations of matched two-loop thermodynamics and finite-T collisions only. No physical/Core/Gravity unlock; no change to the Core-owner composition or original failed conserved-C branch.

STATUS: `PASS_SCOPED_INTERACTION_KERNEL`. [Artifact](t13_low_T_interactions.json) SHA-256 `f1679543e0a644c5104d001ea7ed84adbaf1298f8d8315c9c5108cdcfb53fd0c`.

WHAT_CHANGED: Separate topic-local verifier, tests, [equation contract](../../Data/03_Research/t13_low_T_interaction_registry.json), artifact and derivation. The [preceding EFT](T13_LOW_T_PHASE_EFT_2026-10-02.md) and its artifact remain byte-identical; no old Hartree mass, pole or damping prescription is imported.

EQUATION_OR_MAPPING:

## 1. Scope, variables and units

Use the existing branch `t13.candidate.tree_matched_classical_phi_low_T_phase_EFT_v1`.
Its unchanged joint tree action defines P(X,h), X=mu^2-xi^2. This is not the
Galilean X used in the nonrelativistic comparator. Canonical phase varphi
has E, pressure E4, X/chi/s/V'' E2, and existing Phi E. The radial amplitude
is not collective C; canonical phase is not UET Pi=dot_Phi. Phi is eliminated
at tree matching, not quantized as a new field here. R_gen/R_obs remain
excluded. Natural-unit results do not fix Kelvin alpha or material identity.

For U=u-gamma^2/(2V''), W=V''-gamma^2/(2u), x=Phi-Phi_ref,

```text
Phi_X=gamma/(2 V'' U)
V''_X=6 epsilon lambda_Phi x Phi_X
Phi_XX=-Phi_X V''_X/W
V''_XX=6 epsilon lambda_Phi (Phi_X^2+x Phi_XX)
U_X=gamma^2 V''_X/(2 V''^2)
U_XX=gamma^2 [V''_XX/V''^2-2 V''_X^2/V''^3]/2
P1=s/2; P2=1/(2U)
P3=-U_X/(2U^2); P4=U_X^2/U^3-U_XX/(2U^2)
```

These are derivatives in X at fixed external h, not fitted coefficients.
Let chi=s+2mu^2/U and theta=-mu*t+varphi/sqrt(chi). Expansion of P(X,h) gives

```text
L2=(dot_varphi^2-c^2 |grad_varphi|^2)/2
L3=g_t dot_varphi^3+g_s dot_varphi |grad_varphi|^2
g_t=-(2mu P2+4mu^3 P3/3)/chi^(3/2)
g_s=2mu P2/chi^(3/2)
L4=h_t dot_varphi^4+h_m dot_varphi^2 |grad_varphi|^2+h_s |grad_varphi|^4
h_t=(P2/2+2mu^2 P3+2mu^4 P4/3)/chi^2
h_m=-(P2+2mu^2 P3)/chi^2; h_s=P2/(2chi^2)
```

g has E^-2 and h has E^-4. Independently reoptimized pressure at perturbed
time/spatial gradients checks cubic and quartic terms directly. At gamma=0,
P3=P4=0, but the O(2) phase still interacts: decoupling Phi is not a free-phonon
limit. Phi-coordinate rescaling leaves all canonical vertices/rates invariant.

## 2. The first actual attenuation mechanism

The calculated eta is positive, so at sufficiently low q this branch has
upward dispersion curvature. Energy-momentum conservation then admits a
one-to-two phonon process. At incoming k and outgoing p,r=k-p the canonical
LO cubic amplitude is

```text
M=6 g_t E_k E_p E_r
  +2 g_s [E_k (p.r)+E_p (k.r)+E_r (k.p)]
Gamma_occupation=(1/(2E_k)) (1/2!) integral dPi_p dPi_r
                  (2pi)^4 delta^3(k-p-r) delta(E_k-E_p-E_r) |M|^2
```

For convex low-q kinematics, collinear leading energies E=cq and
G=g_t+g_s/c^2 reduce the amplitude to 6G c^3 k p(k-p). Angular delta integration
and integral p^2(k-p)^2 dp=k^5/30 give

```text
Gamma_occupation=3 G^2 c^2 k^5/(80pi)+higher-order terms
gamma_pole=Gamma_occupation/2
Im omega=-gamma_pole
```

The exact-tree-dispersion phase-space check solves each angular support root
without clipping/discarding an invalid root. It uses LO vertices, so it checks
the asymptotic coefficient, not the full finite-q decay rate. Missing derivative
vertices and external-leg residues produce additional corrections.

The independent dilute nonrelativistic control g_t=0,
g_s=1/(2m sqrt(chi)), c^2=n/(m chi) gives gamma_pole/k^5=3/(640pi m n).
This is a control limit, not a helium coefficient imported into UET.
[Derezinski, Li and Napiorkowski, Eqs. 19-22](https://www.fuw.edu.pl/~derezins/damping_publ.pdf)
explicitly distinguish pole imaginary part from twice that occupation decay.

On every sampled energy root E_k=E_p+E_r, the Bose gain/loss identity
(1+n_k)n_p n_r=n_k(1+n_p)(1+n_r) holds. Energy is transferred between phonons,
not removed from the total system. This is a necessary collision-kernel check,
not a derivation of finite-T dynamics, fluctuation noise or full SK/KMS matching.

## 3. Separate dispersion and interaction terms at T8

For the preceding parent let A0=2sU, K=epsilon Z_Phi,
H=1+gamma^2 s K/V''^2 and J=-gamma^2 s K^2/V''^3.

```text
omega^2=c^2 q^2+d2 q^4+d3 q^6+...
d2=2c eta
d3=[J(1-c^2)^3-2H(1-c^2)d2]/(A0+4mu^2)
zeta=d3/(2c)-d2^2/(8c^3)
omega=cq+eta q^3+zeta q^5+...
C8_disp=4pi^6(4eta^2-c zeta)/(15c^9)
DeltaP_one_phase_loop=A4 T4+B6 T6+C8_disp T8+...
```

An independent Bose moment integral and full parent acoustic pressure/entropy
check this tree-dispersion expansion. This is still only the one-phase-loop
determinant, not the complete interacting pressure at order T8.

One quartic thermal-thermal double-bubble is computed under an explicit
vacuum/contact subtraction convention. With J_T=pi^2 T4/(30c^3), Euclidean
thermal derivative covariance is diag(-J_T,J_T/(3c^2),J_T/(3c^2),J_T/(3c^2)).
Wick contraction (including the Wick-rotated mixed-vertex sign) gives

```text
DeltaP_quartic_TT=Q8 T8
Q8=[pi^2/(30c^3)]^2 [3h_t+h_m/c^2+5h_s/(3c^4)]
```

This is a scheme-declared piece, not a computed full two-loop pressure.
Cubic exchange, mixed vacuum/thermal pieces and counterterms remain.
The real self-energy can require subtraction/matching even when its on-shell
imaginary cut is finite. Standard nonrelativistic EFT also exhibits logarithmic
dispersion corrections and sensitivity to higher derivative terms near shell;
one cannot borrow those coefficients for our relativistic X. See
[Escobedo and Manuel, Sections II-V](https://arxiv.org/html/1004.2567v2).
The small Q8 term does not bound the uncomputed diagrams or unknown Wilson input.

| mu E | zeta E^-4 | C8_disp E^-4 | Q8 E^-4 | gamma_pole/k^5 E^-4 |
| --- | --- | --- | --- | --- |
| 1.05 | -.723250120 | 324701542.490 | 45786.3360 | .0108344696 |
| 1.20 | -.077120982 | 289371.0129 | 85.7799911 | .00131422468 |

At q=.005, phase-space coefficient disagreement is 9.8701e-5/2.5070e-5;
gamma_pole/omega is 3.2123e-11/2.2553e-12 in natural units. This does not
establish an experimentally measurable linewidth. At the finest declared T,
one-loop T8 pressure/entropy errors against acoustic integrals are below
9.264e-8/2.310e-7. Q8 T8/P_T4 is about 1.20e-9/1.88e-9, **not total theory error**.

VERIFICATION: Fourteen artifact checks; focused and linked tests recorded in UPDATE_LOG. Two unchanged action states, dispersion q=.04/.02/.01, decay q=.02/.01/.005, 24/48/96 angular-root quadratures, X-derivative steps .0004/.0002/.0001, original T divisors 32/64/128 and coordinate scales .5/2. Direct stationary pressure, exact parent roots/group velocity/ledger, collinear phase-space and known-limit factor two, independent Bose moments/Wick contractions, and audited file access excluding holdout/numeric source. No physical/external/model trial claimed.

CONTROLLING_BLOCKER: `renormalized_cubic_sunset_and_vacuum_Wilson_matching_open`. Independent material/source/scale and finite-T normal/heat transport remain separate blockers.

NEXT_ACTION: Derive a Ward-consistent regulator/subtraction contract, compute the missing cubic-sunset and mixed terms together with source/entropy derivatives, then quantify a validity window or verified inconsistency. Use the derived amplitude/energy balance as input to finite-T collision research, not an assigned damping ansatz. Independently assess the preceding measurement card's material/units/readout feasibility. Preserve 7 October freeze, 11 October portfolio review and the five later reviews.

CLAIM_BOUNDARY: Candidate low-T kernels and a leading T=0 attenuation mechanism only. Not a controlled full quantum EOS/remainder, physical two-fluid heat/Kubo/SK-KMS transport, Kelvin alpha, material/TTG/He-II prediction, external validation or Full Topic13/Core. No fit, assigned width, old Hartree repair, clipping/filter/padding/threshold change or new numeric Xie access. Prior exposure stays REVIEW_REQUIRED; original conserved-C remains blocked at 1e-6 and all physical/full-Core/global promotion flags remain false.
