# Conditional pressure-Hessian two-fluid operator and domain decision

MAJOR_RESULT_CLOSURE: `T13_CONDITIONAL_PRESSURE_HESSIAN_TWOFLUID_OPERATOR` is `PARTIAL`. The local operator identity and domain screen are derived; the direct tree-stiffness lift fails at one of the two fixed witnesses.

WHAT_IS_ACTUALLY_CLOSED: A rest pressure Hessian plus a separately supplied relative-flow stiffness determines the nondissipative linear longitudinal operator in the declared imported EFT. An analytic stiffness interval reproduces the direct mode classification. Direct insertion of Core tree stiffness is inadmissible at the existing `mu=1.05` witness.

WHAT_REMAINS_OPEN: Joint finite-T condensate stationarity, finite-T relative-flow current/Ward matching, derivation of the normal component, independent He-II state/units, source and detector coupling, dissipative response and clean Core admission.

DEPENDENCY_UNLOCKED: Conditional operator and relative-flow measurement design only. G1 physical, G2 scientific result and Full Topic 13 remain open.

STATUS: `FAIL_CONDITIONAL_OPERATOR_SCREEN`; the failure is the faster longitudinal mode at `mu=1.05`. Numerical refinement and independent linear algebra pass. This is a domain rejection of a declared constitutive lift, not a global UET no-go.

WHAT_CHANGED: Added a pressure-Hessian verifier, generated artifact, independent action-expansion tests, analytic causal interval and funding-plan controller addendum. Core equations and numeric calibration records are unchanged.

EQUATION_OR_MAPPING: `F=F0(b,y)-f_s(b,y)*(X+y^2)/2+O((X+y^2)^2)`, with `F0=p-T*s`, `b=s=p_T`, `y=mu`. Matching `f_s=-2F_X` to `Z*q/lambda` is an unproved finite-T constitutive assumption.

VERIFICATION: Eight Topic 13 tests and twelve directly related Core pressure/static-response regressions pass. A central finite-difference expansion of an independently constructed `F` includes nonconstant stiffness and a fourth-order relative-flow term; it agrees with the reduced coefficients. A first-order companion eigensolver agrees with secular roots. No measured response rows or Xie 2026 inputs are read. Artifact SHA-256: `8606303e4818030dd74061c14b243542c19c4cbb262dda29261951d4c87d6412`.

CONTROLLING_BLOCKER: `finite_T_relative_flow_current_and_normal_component_UET_match_not_derived`.

NEXT_ACTION: Derive the current response to a spatial phase gradient on one declared jointly stationary finite-T prescription, including its normal component. Check the resulting stiffness against the analytic interval before adding a physical source/detector map. At the D5 decision on 2 October, retain unresolved G1/G2 if those admissions remain absent.

CLAIM_BOUNDARY: Imported nondissipative relativistic EFT with conditional UET pressure/stiffness input. Neither natural witness is an admitted He-II state. Mode speeds are in natural units with `c=1`; they are not measured helium velocities. Passing at one point does not establish a material map, nonlinear domain of dependence, physical Kubo coefficient or full thermal closure.

## Derivation

The external parent is [Nicolis, arXiv:1108.2513](https://arxiv.org/html/1108.2513), equations (17)-(24) and (32)-(44). This note derives the reduction to rest-pressure derivatives. Normal-fluid comoving fields belong to that imported EFT; they are not added to the UET registry. Neither `C` nor `Phi` is relabeled as charge or mass. `R_gen` and `R_obs` remain outside the dynamical state.

At fixed `Phi`, write

```text
s=p_T, n=p_mu, a=p_TT, h=p_Tmu, c=p_mumu
F0_bb=-1/a, F0_by=h/a, F0_yy=c-h^2/a
K_N=T*s+mu*n-f_s*mu^2
G_N=s^2/a
K_S=mu^2*(c-h^2/a)
G_S=f_s*mu^2
M=mu*(s*h/a-n+f_s*mu)
```

The transform needs `a>0`. Derivatives of `f_s(b,y)` and the coefficient of `(X+y^2)^2` cancel in the quadratic rest-frame coefficients. Thus only the value of relative-flow curvature at the anchor is needed for these two local linear modes. This does not determine the finite-flow nonlinear response or dissipation.

Natural-unit dimensions are `p:E^4`, `T,mu:E`, `s,n:E^3`, `a,h,c,f_s:E^2`, and all five quadratic coefficients `E^4`. The phase convention can match `psi=-theta` when Core uses `theta=-mu*t`; this preserves the conditional tree current and gradient coefficient. Physical normalization and finite-T matching still need separate derivation.

The determinant gives

```text
P(z)=A*z^2-B*z+D, z=omega^2/k^2
A=K_N*K_S
B=K_N*G_S+G_N*K_S+M^2
D=G_N*G_S
```

With all four kinetic/gradient coefficients positive, both roots are strictly between zero and one iff `P(1)>0` and `2*A-B>0`. Put `x=f_s*mu^2`, `w=T*s+mu*n`, `k=K_S`, `g=G_N`, `m=mu*(s*h/a-n)`. The conditions are affine in `x`:

```text
x>0; w-x>0
P(1)=(w-g)*k-m^2+x*(-k-w-2*m+g)>0
2*A-B=2*w*k-g*k-m^2+x*(-2*k-w-2*m)>0
```

Their intersection is a necessary and sufficient interval for these strict linear-mode conditions. It is an admissibility bound, not a fitted physical value. No replacement stiffness is selected from this interval.

## Fixed-witness results

Both witnesses use `T=0.22`, `Phi=0.15`, `Z=lambda=1`, `m_eff^2=0.994`, inherited from the previous structural witness. The pressure uses a tree condensate plus thermal quasiparticles, with no vacuum or interacting self-energy corrections and no joint finite-T amplitude solve.

| mu | f_s_tree | Strict allowed f_s interval | Low/high c^2 | Decision |
| --- | --- | --- | --- | --- |
| 1.05 | 0.1085 | (0, 0.10712168) | 0.04598333 / 1.82191297 | Rejected |
| 1.20 | 0.4460 | (0, 0.44698003) | 0.13377467 / 0.65789519 | Conditionally admissible |

The last step-refinement changes in the five coefficients are `3.19e-5` and `1.20e-4`; quadrature changes are `3.22e-8` and `8.90e-8`, below the declared `1e-3` numerical tolerance. Orders are 128/192/256 and derivative steps are 4e-4/2e-4/1e-4. These are convergence diagnostics, not experimental uncertainty or continuum error bounds. The bound changes the interpretation of the direct tree lift, not the original Core action's status.

## Reproduction

```powershell
py docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Conditional_TwoFluid_Operator.py
py -m pytest -q docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_conditional_twofluid_operator.py docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_funding_rest_eos_dynamic_degeneracy.py
```

The artifact hashes the pressure, action/configuration, witness and verifier inputs. The initial test collection failed on a direct topic-module import; explicit file loading fixed collection before the eight tests passed.
