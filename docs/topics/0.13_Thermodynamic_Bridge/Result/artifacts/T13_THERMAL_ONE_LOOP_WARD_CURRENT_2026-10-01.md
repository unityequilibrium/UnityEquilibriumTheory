# Thermal one-loop Ward, condensate shift and static current

MAJOR_RESULT_CLOSURE: `T13_THERMAL_ONE_LOOP_WARD_AND_STATIC_CURRENT_MATCH` is `CLOSED_FOR_LANE` at formal one-loop thermal order with fixed `Phi`. This is not a new Full Topic13 or Core-composition admission.

WHAT_IS_ACTUALLY_CLOSED: The transverse tadpole and bubble at zero external momentum are explicitly computed from the same action determinant. They satisfy the Ward relation and cancel the one-loop condensate-shift contribution. The resulting static-current coefficient equals the previous tree-relaxed pressure curvature at this order.

WHAT_REMAINS_OPEN: Finite-frequency/momentum retarded vertices, infrared resummation, a stable renormalized background with joint `Phi` stationarity, controlled errors, physical material/normal-component/source/detector matching and independent response data.

DEPENDENCY_UNLOCKED: A consistent fixed-`Phi`, thermal one-loop static-current calculation, not a physical sound prediction. Funding G1/G2 and new diagnostic full-unlock flags remain false. Recorded bounded O(2)/He-4 Core composition is untouched.

STATUS: `PASS_THERMAL_ONE_LOOP_WARD_CURRENT`; nine artifact checks pass.

WHAT_CHANGED: Added a Topic13 loop verifier, independent matrix/Matsubara checks, nine tests and evidence. Preserved the exact thermal-Gaussian no-go and failed tree-only operator. No state-dependent counterterm, extra chemical potential or measured target was used.

EQUATION_OR_MAPPING: `Sigma_pi,T(0)=2*Omega_G,x/Z`; `delta_x=-2*Omega_G,x/lambda`; `f_1loop=f_held+Z*delta_x=f_path`. These are formal order relations, not an exact resummed solution.

VERIFICATION: 44 focused/related tests pass. Matrix log-determinant derivatives, direct Matsubara sums minus numerical vacuum integrals, pole residues, radial/cutoff refinement, energy-unit scaling, zero-temperature and coupling limits, protected artifact hashes and the infrared asymptote are checked. Artifact SHA-256: `cfd794f8d1f7ab1de4d3e3b9feb991957c76d57d40375ddd6bbab2a8a2a514aa`.

CONTROLLING_BLOCKER: `finite_momentum_retarded_Ward_current_and_IR_resummation_not_derived` for this new lane. Material admission and full finite-temperature completion remain separate physical requirements.

NEXT_ACTION: Derive the nonzero external-momentum kernel using the same vertices and subtraction prescription. Determine its static/dynamic limit and infrared treatment before admitting a driven longitudinal operator or iterating the shifted Gaussian background.

CLAIM_BOUNDARY: Only the thermal difference of a one-loop 1PI functional, evaluated about a tree-condensed background at fixed `Phi`. No vacuum/material renormalization, controlled finite-order remainder, exact finite-T state, physical Kubo coefficient, He-II prediction, fit, Xie use or global claim promotion.

## Action normalization and two actual loop terms

Retain the existing natural-unit action. Write `x=A^2`, `q=Z*mu^2-m_eff(Phi)^2`, `r=q/Z>0`, `g=lambda/Z` and `x0=q/lambda`. A transverse Cartesian perturbation is called `eta`; it is neither the response field `Phi` nor UET `C`.

The Euclidean inverse kernel divided by `Z`, at the tree background, is

```text
K = [[a,-b],[b,d]]
a=nu^2+k^2+2r; d=nu^2+k^2; b=2mu*nu
D=det K=a*d+b^2; G=K^-1
K_eta=2gA*[[0,1],[1,0]]
K_eta_eta=2g*diag(1,3); K_x=g*diag(3,1)
```

All vertices follow by differentiating the same Cartesian quartic Hessian. The chemical-potential mixing is retained. Define `Delta sum-integral` as the finite-T Matsubara sum minus the zero-T frequency integral at the same tree background. The thermal transverse 1PI correction is

```text
Sigma_pi,T(0) = (1/(2Z))*Delta integral Tr[G*K_eta_eta-G*K_eta*G*K_eta]
              = (g/Z)*(I_sigma+3I_pi) - (4g^2*x0/Z)*B
I_sigma=Delta integral G_sigma_sigma
I_pi=Delta integral G_pi_pi
B=Delta integral 1/D
```

The bubble has not been replaced with a Ward-required number. The matrix identity `Tr[G*S*G*S]=2/D`, with `S=[[0,1],[1,0]]`, reduces it analytically. Since `a-d=2g*x0`, the tadpole plus bubble equals

```text
Sigma_pi,T(0)=(g/Z)*(3I_sigma+I_pi)=2*Omega_G,x/Z
Omega_G,x=(g/2)*(3I_sigma+I_pi)
```

Both the individual terms and the equality are independently checked. Omitting the bubble fails the Ward test.

## Thermal sum and independent evaluation

Let `E_l,E_h` be the positive tree roots and `Delta=E_h^2-E_l^2`. Their squared product is `k^2*(k^2+2r)`, which supplies a numerically stable expression for `E_l^2`. With `J_a=n_B(E_a)/E_a`,

```text
I_sigma integrand = [(k^2-E_l^2)J_l+(E_h^2-k^2)J_h]/Delta
I_pi integrand = [(k^2+2r-E_l^2)J_l+(E_h^2-k^2-2r)J_h]/Delta
B integrand = (J_l-J_h)/Delta
```

The radial measure is `k^2 dk/(2*pi^2)`. A second method directly inverts the matrix at each Matsubara frequency, numerically integrates the zero-T frequency part, and subtracts before radial integration. The missing large-frequency `nu^-2` and `nu^-4` tails are derived from the kernel. At 128/256/512 terms and six fixed momentum/state checks, the maximum finest relative disagreement is `6.29e-11`, below the preregistered `1e-6` numerical-method tolerance.

No vacuum radial integral or temperature-dependent renormalization condition is selected by this thermal subtraction. Physical zero-temperature parameter matching is still required for a material interpretation.

## Stationarity and current at the same loop order

Introduce a formal loop-counting symbol `hbar_loop`, not a fitted parameter. The stationary equation through first order gives

```text
Omega_tree,x=lambda*(x-x0)/2
x=x0+hbar_loop*delta_x; delta_x=-2*Omega_G,x(x0)/lambda
Gamma_pi_pi(0)/Z=lambda*hbar_loop*delta_x/Z+hbar_loop*Sigma_pi,T(0)=0
```

This cancels the transverse inverse at zero external momentum at that order. It does not prove a finite-frequency pole or a convergent exact solution.

For the uniform phase gradient `xi`, `x0(xi)=(q-Z*xi^2)/lambda`. At zero flow `x0'=0` and `x0''=-2Z/lambda`. The previous path curvature satisfies

```text
f_path=f_held-2Z*Omega_G,x/lambda
f_1loop=Z*x0+Z*delta_x+Omega_G,xi_xi|x0=f_held+Z*delta_x=f_path
```

The amplitude-path term therefore has a consistent formal first-order interpretation as the condensate correction to the tree current. It is not an arbitrary extra stiffness chosen from target sound speeds. This upgrades the interpretation of the static calculation within this order; it does not alter the old artifact's historical exclusions.

| mu | Thermal tadpole | Thermal bubble | Sum / required loop inverse | delta_x | f_1loop |
| --- | --- | --- | --- | --- | --- |
| 1.05 | 0.02898336 | -0.00961636 | 0.01936700 | -0.01936700 | 0.09157372 |
| 1.20 | 0.02529610 | -0.01243692 | 0.01285918 | -0.01285918 | 0.43717875 |

The units of these entries are `E^2`; `Z=lambda=1`, `T=0.22`, `Phi=0.15` remain the prior fixed witnesses. The largest Ward cancellation residual is `1.04e-17`; static-current agreement is within `1.39e-17`. These residuals are numerical checks, not physical uncertainties.

## Why this still requires infrared treatment

The fractional first-order shifts are about -17.85% and -2.883%. Smallness alone is not a controlled error bound. Feeding the shifted amplitude into the undressed Gaussian kernel gives negative low roots at `k=0` (`-0.00067632`, `-0.00166221`). Only these roots are diagnosed; the unstable shifted Bose determinant is not evaluated, clipped or called equilibrium.

There is also a nonuniform expansion boundary. For the gapless branch, `c^2=r/(r+2mu^2)` and, as `k->0`,

```text
E_l~c*k; E_l,x~g*c/(2k); E_l,xx~-g^2*c/(4k^3)
k^2/(2pi^2) * [n_B*E_l,xx - n_B*(1+n_B)*E_l,x^2/T]
    ~ -g^2*T/(4pi^2*k^2)
```

Thus the bare zero-external-momentum amplitude Hessian has a nonintegrable infrared term at `T>0`. The analytic coefficient is confirmed by decreasing `k`; refining a finite radial cutoff cannot turn it into a finite continuum uncertainty. This is not a claim that a physical second-sound observable diverges, nor an impossibility theorem against consistent resummation or a finite-momentum response.

[Alford et al., arXiv:1212.0670](https://arxiv.org/abs/1212.0670), section III A, uses a low-temperature weak-coupling approximation and explicitly separates it from a self-consistent treatment. It is method context, not evidence that the present `lambda=1` witnesses have controlled errors. The Ward calculation here is derived from the repo action; it does not import a helium current or a new normal-density identity from that paper.

## Formula audit and reproduction

| Diagnostic ID | Units | Origin / status | Evidence / boundary |
| --- | --- | --- | --- |
| `t13.diagnostic.thermal_transverse_1pi_zero` | `Sigma:E^2`; `I_sigma,I_pi:E^2`; `B:1` | Actual one-loop Cartesian tadpole/bubble; thermal difference | Matrix derivatives and independent sums; finite-q continuation open |
| `t13.diagnostic.loop_order_condensate_current` | `delta_x,f:E^2`; `Omega_x:E^2` | Formal first-order stationarity plus chain rule | Current/path agreement; no exact background or remainder bound |
| `t13.diagnostic.gaussian_amplitude_hessian_IR` | radial integrand `E^-1`; integrated Hessian `1` | Bare low-momentum asymptote | Negative `k^-2` singularity; physical resummation open |

These are Topic13 diagnostic IDs, not admitted new Core equations. `C` is not charge or mass; `Phi` remains an inherited response coordinate held fixed; `R_gen` and `R_obs` are absent from the loop dynamics and have no feedback. No SI conversion is introduced.

```powershell
py docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Thermal_OneLoop_Ward_Current.py
py -m pytest -q docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_thermal_oneloop_ward_current.py
```

The first asymptotic test missed its stricter `1e-4` relative limit at `k=2.5e-4`. Decreasing momentum to `1e-4` and requiring decreasing errors verified convergence without relaxing that tolerance. The original causal leakage threshold and all physical admission gates are unchanged.
