# Even finite-pair work explains the old amplitude failure, not physical heating

MAJOR_RESULT_CLOSURE: `T13_FINITE_PAIR_CYCLIC_WORK_PARITY_AND_REMAINDER`, `CLOSED_FOR_LANE`. The declared two-block Gaussian control now has derived even coefficients and a conditional conservative remainder formula. Original source-work FAIL stays FAIL; no Full Topic13/Goal/R1 acceptance.

WHAT_IS_ACTUALLY_CLOSED: Sign symmetry excludes odd work orders exactly in this control. Direct coefficient evolution through order six independently reproduces the old finite-flow work grid. The large quartic contribution explains why halving amplitude produced approximately 1/16 rather than the leading 1/4 ratio; it is not a coefficient fit.

WHAT_REMAINS_OPEN: The derived bound is too loose to certify the old amplitude grid usefully. Its floating-point evaluation is not interval certified. Nonlinear parent-action completion, physical energy/heat/readout/scale, collision and SK/KMS/entropy remain open.

DEPENDENCY_UNLOCKED: Source/readout identifiability and controlled parent-remainder research only, not Core/Gravity/physical or funding acceptance.

STATUS: `PASS_SCOPED_GAUSSIAN_WORK_REMAINDER`. [Artifact](t13_gaussian_work_remainder.json), SHA-256 `0bff6697f0c94f749cbaf2134c3e78ae36de40c66783a7303e8c5f5aadf307b1`, is the numerical controller. [Predecessor](t13_gaussian_source_work.json) remains byte-identical at SHA-256 `959441d2940f0aa209d72b8f8671d440807dd14ae9a80aff4357606f3bce4c62`.

WHAT_CHANGED: Separate [coefficient calculation](../../Code/03_Research/Research_T13_Gaussian_Work_Remainder.py), [tests](../../Code/03_Research/test_t13_gaussian_work_remainder.py) and [local registry](../../Data/03_Research/t13_gaussian_work_remainder_registry.json). No old pulse/amplitude/gate/action or Core-owner edit. The pending protocol was locked before the first audit; the residual normalization was corrected before that audit, not after a failed physical result.

EQUATION_OR_MAPPING:

## 1. A declared finite quadratic control, not the full parent

Use the predecessor's real blocks y=(y_p,y_r), y_p=(x_p,xdot_p), with
the same source, state, thermal insertion, and momenta. Let

```text
A(epsilon,t)=A0+epsilon*A1(t)
A0=diag(A_p,A_r), A1=[[0,delta_A],[delta_A,0]]
H0=diag(V_p,K,V_r,K), C0=diag(C_p0,C_r0)
P=diag(I6,-I6)
```

At all times P A(epsilon) P=A(-epsilon), P C0 P=C0 and P H0 P=H0.
Uniqueness of finite ODE flow gives S(-epsilon)=P S(epsilon) P.
Since the source potential vanishes at both endpoints,
W(epsilon)=.5 Tr(H0[S C0 S^T-C0]) and therefore W(-epsilon)=W(epsilon).
This statement applies to this off-diagonal two-block control only:
it does not exclude odd nonlinear work in a different parent/source model.
q0 duplicated blocks remain orientation controls, not added material modes.

## 2. Coefficients come from derivatives of the ODE, not observed work

Expand C(epsilon,t)=sum_n epsilon^n C_n(t), with C_n(0)=0 for n>0.
The exact covariance equation gives

```text
dot_Cn=A0 Cn+Cn A0^T+A1 C(n-1)+C(n-1) A1^T
W(epsilon)=epsilon^2 W2+epsilon^4 W4+epsilon^6 W6+R6
```

Odd C_n have off-diagonal X_n=(r,p); even ones have diagonal P_n,R_n.
The explicit block recurrences and work identity are

```text
dot_Xn=A_r Xn+Xn A_p^T+delta_A P(n-1)+R(n-1) delta_A^T
dot_Pn=A_p Pn+Pn A_p^T+delta_A X(n-1)+X(n-1)^T delta_A^T
dot_Rn=A_r Rn+Rn A_r^T+delta_A X(n-1)^T+X(n-1) delta_A^T
W(2k)=int Vdot1:X(2k-1)_xx
     =.5 Tr(H_p P(2k)+H_r R(2k)) at the final endpoint
```

The n=1 recurrence uses the original stationary C_p0,C_r0. Both real
orientations give the work contraction above, not an extra factor 1/2.
No factorial is inserted because C_n denotes Taylor coefficients rather
than raw derivatives. W4/W6 use two new, preregistered solver levels.
The cancellation-prone binary64 W2 is reported but not relabelled;
predictions use the predecessor's independently resolved leading W2.

| mu | p,r,q | W4 | W6 |
| --- | --- | --- | --- |
| 1.05 | .02,.031,.02 | 3.246916e-4 | 2.652832e-6 |
| 1.05 | .04,.037,.02 | 7.395746e-5 | 6.042969e-7 |
| 1.05 | .02,.02,0 | 5.043354e-4 | 4.134111e-6 |
| 1.20 | .02,.031,.02 | 4.432071e-4 | 2.305308e-5 |
| 1.20 | .04,.037,.02 | 5.901890e-5 | 3.002818e-6 |
| 1.20 | .02,.02,0 | 7.361024e-4 | 3.838084e-5 |

Across the original18 case/amplitude points, epsilon^4 W4 divided by
epsilon^2 W2 ranges3.323e3 to2.839e7. Thus the frozen grid is not a
leading-quadratic-work regime even when its amplitude looks small.
This ratio uses independently derived coefficients, not a regression
or a proposal to change the old amplitudes/thresholds.

Coefficients and W are E per internal pair; epsilon and eta are
dimensionless. A justified momentum measure would be needed for an E^4
density. This is rotating Gaussian energy, not the physical Noether
E=Hrot+mu N, SI heat or Kelvin temperature. Natural Phi has dimension E
and h E^3 here; neither is normalized Phi nor a material thermometer.

## 3. Conditional conservative tail bound

Assume the exact finite H0 is positive, C0 is positive semidefinite,
A0^T H0+H0 A0=0, the pulse is integrable, and its endpoints vanish.
Set R=chol(H0)^T and whiten the state. The free generator is antisymmetric,
so its flow U0 is orthogonal. In the interaction picture,
B(t)=U0^T R A1(t) R^-1 U0 has the same spectral norm as R A1 R^-1.
The exact finite tones give an all-time triangle bound, not a sample proof:

```text
eta = int ||B(t)||_2 dt <= L sum_nu ||R A1_nu R^-1||_2
E0 = .5 Tr(R C0 R^T)
```

The Peano-Baker iterated integrals obey ||U_n||<=eta^n/n!.
For D0=R C0 R^T positive semidefinite, each covariance term satisfies
|.5 Tr(U_j D0 U_(n-j)^T)|<=E0 ||U_j|| ||U_(n-j)||.
Summing j gives |W_n|<=E0 (2eta)^n/n!. Parity removes every odd
coefficient, so the conditional exact bound is

```text
|R_2N| <= E0 sum_(k>N) (2|epsilon|eta)^(2k)/(2k)!
```

The [Peano-Baker review](https://www.math.uni-bielefeld.de/baake/ps/peano-baker.pdf),
Section 2/Theorem 1, supplies the standard factorial norm-majorant method.
The energy/parity specialization here is a derivation for this control,
not a novelty claim or a physical coefficient imported from that paper.

For x=2|epsilon|eta<=1, the tail after W2 is at most
E0*cosh(1)*x^4/24. Consequently a sufficient conditional domain for
relative error tol in epsilon^2 W2, assuming exact W2>0, is

```text
|epsilon| <= min(1/(2eta),sqrt(24*tol*W2/(E0*cosh(1)*(2eta)^4)))
```

Evaluations give eta=247.686 to567.285 and sufficient amplitude bounds
5.900e-13 to2.362e-11 for tol=.01. These are deliberately conservative,
not pulse amplitudes selected from the old curve. None of .02/.01/.005
is certified by this domain. At .02, the order-six tail bound ranges
20.27 to1.006e7 in pair-energy units and is plainly unusable as an error bar.
An analytic inequality is not a certified interval evaluation of the
floating-point norm/coefficient inputs. Accurate numeric prediction at
three amplitudes is not a proof of a useful remainder bound there.

## 4. Known control and independent checks

A0=0,A1=sigma_x,C0=I2,H0=I2 gives E0=1 and
W=cosh(2epsilon*eta)-1. Its even tail saturates the formula and exposes a
missing factor two. This is a known mathematical diagnostic, not data,
calibration, an admitted UET state, or a heat-production example.
Negative epsilon with the unchanged original finite flow checks parity.
Sampled tone norms only check implementation; the all-time bound uses
the analytic finite-tone triangle argument.

VERIFICATION: Eight new scientific checks PASS at six frozen cases. Order-four/six refinement error, scaled to their common coefficient norm, is at most6.591e-14; endpoint work/energy error at most1.002e-14. Through-six predictions match the predecessor's independent finite-flow grid within4.302e-9 relative; negative-amplitude sign difference is zero at recorded precision. Final26-file linked suite522 passed in596.26 seconds, including44 new tests and31 funding-contract tests, with audit-time Path read allowlist and current/protected hash checks. Focused runs are subsets, not additional coverage counts. This does not repair the six original FAIL gates, certify binary64 W2, or bound missing parent-action physics. No external or whole-repository validation/model trial.

CONTROLLING_BLOCKER: `physical_source_readout_scale_and_parent_interaction_remainder_open`. A useful original-grid bound and an interval-certified evaluation remain separate obligations, not absorbed into the new PASS.

NEXT_ACTION: Link the resolved finite-pair coefficient content to one source-to-state-to-detector/independent-scale measurement card, and determine the missing nonlinear parent terms before physical energy/entropy claims. Do not rerun unchanged amplitude work or tune the pulse. Preserve7/11 October and the existing full scientific acceptance rules.

CLAIM_BOUNDARY: Finite quadratic Gaussian rotating-energy work only. No full interacting/quantum/collision/Kubo/SK/KMS/SI/entropy/temperature or Full Topic13/Core/global claim. R_gen/R_obs/C/UET Pi are excluded from covariance states. No fit, assigned rate/width, vacuum fill, clipping, cone padding, threshold/ontology/owner change or numeric Xie read. Prior context exposure remains REVIEW_REQUIRED, not pristine blindness. Original conserved-C FAIL remains unchanged.
