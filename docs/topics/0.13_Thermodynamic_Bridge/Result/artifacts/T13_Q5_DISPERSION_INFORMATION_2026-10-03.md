# Q5 Unit-Free Kinetic Information And Tree Remainder

MAJOR_RESULT_CLOSURE: T13_Q5_UNIT_FREE_KINETIC_IDENTIFIABILITY_AND_TREE_REMAINDER,
CLOSED_FOR_LANE. Not Full Topic13, physical prediction, G2-G4/R1-R5 or Goal acceptance.

WHAT_IS_ACTUALLY_CLOSED: Same-action q5 coefficient, strict positive-class
unit-free inverse and information rank. Q5 separates the predecessor's
q3 unit/kinetic family without independent U in this restricted class.
An exact rational polynomial envelope controls the tree-series error for
declared rounded-state coefficient witnesses, not material uncertainty.

WHAT_REMAINS_OPEN: Native state/current/material map, q5 measurement and
resolution/covariance, practical conditioning, interaction/finite-T/heat/
entropy/KMS and independent Phi-to-temperature scale. Gain remains separate.

DEPENDENCY_UNLOCKED: Conditional q5 measurement-information route only.
No physical/Core/Gravity, owner composition or full measurement-design unlock.

STATUS: PASS_SCOPED_Q5_INFORMATION. New internal derived evidence, no source fit.

WHAT_CHANGED: Local series/inverse/envelope calculation, tests/registry/
artifact, linked measurement supplement and canonical handoff. Predecessor
q3 proof and original work/causal FAIL remain unchanged.

EQUATION_OR_MAPPING: r=A_Q*C_Q/B_Q^2=r0-D*(I/(1+sI))^2;
tau=sqrt((r0-r)/D), I=tau/(1-s*tau). E5=cq+eta*q3+zeta*q5.

VERIFICATION: Eight preregistered scientific checks pass at mu1.05/1.2
and q.02/.01/.005: full determinant, matrix roots,50/80-digit roots,
series refinement, rational envelope, rank/inverse, prior-family separation,
coordinate covariance and uncertainty gradient. Matrix/root error<=1.776e-13;
50/80-digit discrepancy<=3.168e-50; q5 extraction refinement ratios3.996-4.000.
Finest extraction errors5.947e-5/1.597e-5 are NOT kinetic precision. A later
declared non-gating finite-q bias diagnostic reports1.477%/0.04187% kinetic
bias at q.005. No original threshold or physical gate changed.

CONTROLLING_BLOCKER: physical_q5_resolution_native_input_covariance_material_map_and_interaction_error_open.

NEXT_ACTION: Derive an explicit multi-q coefficient estimator with covariance
and the tree-envelope bias/noise tradeoff. Then identify independent material/
resolution inputs and physical validity, not another unchanged root grid.

CLAIM_BOUNDARY: All other native coefficients must be known and gamma!=0,
I>0. This does not identify full UET, gain, temperature or interactions.
Exact rational envelope applies to declared tree witnesses only, not an
exact EOS solution or physical error bar. No fit, width, quantum Phi loop,
clipping/padding, C/Pi/R_gen/R_obs relabel, owner/holdout or global promotion.
Prior Xie exposure remains REVIEW_REQUIRED; no numeric holdout read.

## Evidence

[Artifact](t13_q5_dispersion_information.json) SHA-256:
`c4b23308c1ffdc45215cdba8d1fb0e3ba8b44c861d8c2c402bec22b3055a6485`.
[Registry](../../Data/03_Research/t13_q5_dispersion_information_registry.json)
declared the original grid and gates before the first q5 audit. The
finite-q bias extension is explicitly later, before its own first audit;
its illustrative1% target is not an acceptance gate or real measurement.
[Predecessor](t13_noether_density_readout.json):
`2b6688dab3cb55c623fa5c1a43320ef28d65fe82e95b27d6ea1731f9c632ac12`.
Original q3 ambiguity remains true at its retained order, not overwritten.

## Derivation From The Existing Kernel

Use the rest h0=0 tree state. Set t=q^2, y=E^2, x=t-y,
R=2u*s, H=4mu^2, W=V_curvature, S=gamma^2*s, k=epsilon*response_kinetic.
The full three-mode determinant divided by W is

```text
delta=R-S/W >0; N=delta+H; p=k/W; A=1+pR; B=pH
F(t,y)=delta*t-N*y+A*x^2-B*x*y+p*x^3
```

Write y=a*t+b*t^2+d*t^3+..., ell=1-a. Coefficient matching, not regression,
gives

```text
a=delta/N; b=(A*ell^2-B*ell*a)/N
d=(-2A*ell*b-B*(ell-a)*b+p*ell^3)/N
c=sqrt(a); eta=b/(2c); zeta=(d-eta^2)/(2c)
I=gamma^2*k/W^2; f=1+sI
eta0=ell^2/(2cN); eta=eta0*f
zeta0=-ell^3/(c*N^2)-ell^4/(8*c^3*N^2)
K=ell^3*s*W/(2*c*N*gamma^2)>0
zeta=zeta0*f^2-K*I^2 <0
```

Units: c dimensionless, eta:E^-2, zeta:E^-4, I:E^-2, K dimensionless.
These are tree pole coefficients, not finite-T quantum transport inputs.
The predecessor establishes that this acoustic pole is density-visible,
not that its Noether charge is already physical helium atomic density.

## A New Independent-Information Route

For physical E(Q)=A_Q Q+B_Q Q^3+C_Q Q^5+... with E_unit,Q_unit unknown,
A_Q=E_unit*c/Q_unit, B_Q=E_unit*eta/Q_unit^3,
C_Q=E_unit*zeta/Q_unit^5. Hence

```text
r=A_Q*C_Q/B_Q^2=c*zeta/eta^2
r0=c*zeta0/eta0^2; D=c*K/eta0^2>0
r=r0-D*(I/(1+sI))^2
dr/dI=-2D*I/(1+sI)^3 <0
```

A_Q:Jm, B_Q:Jm3, C_Q:Jm5; r/r0 dimensionless and D:E4.
With all other native inputs fixed, the strict positive class has a unique
inverse when r0-D/s^2<r<r0: tau=sqrt((r0-r)/D), I=tau/(1-s*tau).
Then Q_unit=sqrt(A_Q*eta/(B_Q*c)), E_unit=A_Q*Q_unit/c. No U input is
needed for this restricted alternative. Outside the domain reject, do not clip.
Gamma=0 makes the response field decouple and its kinetic input unobservable.

For parameters(log E_unit,log Q_unit,I), outputs(log A_Q,log B_Q,log(-C_Q)),
k_eta=s/(1+sI), k_zeta=zeta_I/zeta:

```text
J=[[1,-1,0],[1,-3,k_eta],[1,-5,k_zeta]]
det(J)=2*(2*k_eta-k_zeta) !=0 when I>0,gamma!=0
```

All four old constructive unit-family witnesses keep A_Q/B_Q but change
r; their kinetic/scale inverses agree within9.581e-16 and2.177e-16.
Reference inverse error<=7.954e-14. Coordinate rescaling of Phi preserves
this invariant information and cannot provide an absolute Phi/Kelvin map.
Rank becomes ill-conditioned near decoupling/zero I; see the supplement.

## Exact Rational Tree-Series Envelope

With coefficients treated as declared rational witnesses, form
h=b/(2a), j=d/(2a)-b^2/(8a^2), P(t)=1+h*t+j*t^2 and y5=a*t*P(t)^2.
For 0<=y<=t, -F_y>=N-B*t. F(t,0)>0, F(t,t)<0 and
F(t,a*t)=N*b*t^2+p*ell^3*t^3>0. Thus when N-B*t>0 the unique acoustic
root satisfies a*t<=y<t. Require P>0 and0<y5<t.

The exact rational residual F(t,y5)=sum_n F_n*t^n has F_0..F_3=0 and
degree15. Mean value plus sqrt factorization gives

```text
|E-E5|/(c*q) <= sum_(n=4..15) |F_n|*t^n /
                   ((N-B*t)*a*t*(1+P(t)))
```

Rational parameters/series and numerator/denominator of the bound are
saved exactly and replay-tested without the tree solver, with no leading
coefficient clipping or floating cancellation. Its float display is not
an outward-rounded bound; the exact fraction is authoritative. High-precision
roots check the envelope; binary64 matrix agreement does not certify it.
At q.005 the two normalized rational bounds are1.276e-13/2.114e-15.
The rounded stationary-state inputs are declared polynomial witnesses;
state, EOS, physical mapping and interaction uncertainty lie outside this
certificate. Small tree truncation does not imply small inference bias.
