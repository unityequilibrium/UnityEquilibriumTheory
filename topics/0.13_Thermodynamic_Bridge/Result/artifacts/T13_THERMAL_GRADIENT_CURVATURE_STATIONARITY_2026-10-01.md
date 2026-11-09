# Thermal phase-gradient curvature and the stationary-current boundary

MAJOR_RESULT_CLOSURE: `T13_TREE_RELAXED_THERMAL_PHASE_GRADIENT_CURVATURE` is `CLOSED_FOR_LANE` in the explicitly declared tree-relaxed thermal determinant. Full Topic 13 remains open.

WHAT_IS_ACTUALLY_CLOSED: The missing static phase-gradient thermal curvature can be calculated from the action spectrum without fitting. Implicit spectral derivatives and direct moving-pressure differences agree. The nonstationary amplitude path term is isolated and quantified, so a successful local sound screen is not mistaken for stationary current closure.

WHAT_REMAINS_OPEN: Joint finite-T amplitude/Phi stationarity, microscopic Ward-consistent loop response, retarded source/detector coupling, independent material and normal-component matching, physical uncertainty and Core admission.

DEPENDENCY_UNLOCKED: Static relative-flow current design within this approximation. Physical G1, funding G2 and Full Topic 13 remain locked.

STATUS: `PASS_TREE_RELAXED_THERMAL_CURVATURE`; all nine scoped checks pass. The previous tree-only operator still records `FAIL_CONDITIONAL_OPERATOR_SCREEN`.

WHAT_CHANGED: Added moving-background spectrum/pressure, analytic thermal curvature, an independent direct derivative, amplitude-path decomposition, tests and evidence. Updated funding plans and limitations. No Core equations, frozen calibration values or old failure artifacts changed.

EQUATION_OR_MAPPING: `f_path=-d^2 p(T,mu,Phi,xi,x_tree(xi))/d xi^2`; `f_path=f_held-2Z*Omega_x/lambda`. `Omega_x>0` at the tree amplitude prevents claiming that this exact background is a jointly stationary finite-T solution.

VERIFICATION: 31 focused Topic13/Core tests pass, including five new tests. Checks cover implicit derivatives versus independent quartic roots, direct moving pressure, radial/flow/angular/cutoff refinement, a massless phonon limit, source hashes and the previous amplitude no-go. The cross-platform reproduction repair in commit `005ae47b1` passed the relevant GitHub checks. New artifact SHA-256: `324b8f52002a981929e61c6fd838f4876a87d6655b814603ef182740b3648084`.

CONTROLLING_BLOCKER: `joint_finite_T_stationary_current_response_not_derived`.

NEXT_ACTION: Derive one consistent loop/resummed amplitude and current prescription with the zero-momentum Ward identity, then its driven longitudinal response. The values below constrain the required tadpole/self-energy cancellation; they are not substitute coefficients. At D5, keep physical G1/G2 unresolved unless actual operator/material admissions exist.

CLAIM_BOUNDARY: Thermal-only Gaussian determinant on a tree-relaxed background with fixed Phi and a thermal rest frame. No interacting self-energy, vacuum renormalization, controlled truncation error, physical He-II correspondence, heat-flux/Kubo claim, fit or Xie 2026 use. This result supplies a conditional static calculation, not the remaining full thermodynamic closure.

## Action and moving spectrum

Use the existing O(2) action and `psi=-theta=mu*t+xi*z`. Here `xi` is a phase gradient, not the UET response field `Phi`. Set `x=A^2`, `q=Z*mu^2-m_eff(Phi)^2`, `r=q/Z`. The tree stationary moving amplitude is

```text
x_tree(xi)=(q-Z*xi^2)/lambda
p_tree(xi)=(q-Z*xi^2)^2/(4*lambda)
D(omega,k,xi)=(omega^2-k^2)*(omega^2-k^2-2r+2xi^2)
               -4*(mu*omega+xi*k*cos(theta))^2
```

The two positive roots define the thermal-only pressure. At zero flow this reproduces Core's existing pressure. The microscopic scalar/superflow construction is compared with [Alford et al., arXiv:1212.0670v3](https://arxiv.org/abs/1212.0670), especially equations (39)-(47) and appendix A. Its small-temperature/weak-coupling expansion is a method reference, not evidence that the current `lambda=1` witnesses have a controlled physical error bound.

For each mode, implicit differentiation gives

```text
E_xi=-D_xi/D_omega
E_xixi=-(D_xixi+2*D_omega_xi*E_xi+D_omega_omega*E_xi^2)/D_omega
delta_f_path = integral d^3k/(2*pi)^3
               [n_B(E)*E_xixi - n_B(E)*(1+n_B(E))*E_xi^2/T]
```

The isotropic mean uses `mean(cos^2(theta))=1/3`. Both the spectral-curvature and occupation terms are included. Replacing the action spectrum with a prescribed Doppler shift alone would omit the first term and the amplitude path dependence.

At fixed Cartesian background amplitude, the off-shell determinant instead has diagonal masses `a_pi=xi^2`, `a_sigma=2r+xi^2`. Its static curvature is a partial derivative of the off-shell Gaussian pressure. It is not an admitted stationary current either. Mixing it with EOS derivatives taken along the tree-amplitude path uses incompatible derivative protocols; the artifact labels that screen explicitly.

## Why the improved mode screen is not enough

Let `Omega=-p` be the off-shell tree-plus-thermal grand potential. At `xi=0`, the tree amplitude satisfies `Omega_tree,x=0`, but `Omega_G,x>0`. This agrees with Core's existing scoped Gaussian stationarity no-go. Chain rule gives

```text
x_tree''(0)=-2Z/lambda
f_path=f_held - 2Z*Omega_G,x/lambda
```

The difference is reproduced independently using Core's analytic amplitude derivative. It is substantial in these witnesses:

| mu | Tree stiffness | Tree-relaxed thermal stiffness | Held-amplitude partial curvature | Amplitude path term |
| --- | --- | --- | --- | --- |
| 1.05 | 0.10850000 | 0.09157372 | 0.11094072 | -0.01936700 |
| 1.20 | 0.44600000 | 0.43717875 | 0.45003793 | -0.01285918 |

Using the tree-relaxed thermal pressure and its curvature in the conditional EFT gives `c^2=(0.03710313,0.17181440)` and `(0.12470902,0.16964409)`. Both pass the local linear-mode screen. Neither is an admitted He-II prediction.

A formal first-order tadpole shift would be `delta_x=-2*Omega_G,x/lambda`, about -17.85% and -2.883% of `x_tree` at `lambda=1`. Applying that shift without the corresponding self-energy makes the tree transverse mass negative. The zero-momentum Ward relation requires a loop contribution `2*Omega_G,x/Z` to cancel it at that perturbative order. This is a necessary consistency requirement inferred from the tadpole/Ward relation, not an independently computed loop correlator or a solved resummation.

The tree-relaxed pressure may be a starting point for a consistently ordered perturbative effective theory. To use that interpretation, the matched current, stationary prescription, Ward response and truncation control must be derived. The present calculation neither excludes that route nor completes it.

## Formula audit

These are Topic13 diagnostic identifiers, not new Core registry equations.

| Formula ID | Units / variables | Origin and proof class | Verification role / remaining step |
| --- | --- | --- | --- |
| `t13.diagnostic.moving_tree_spectrum` | `mu,xi,k,E:E`; `q:E^2`; `Z,lambda:1` | Existing O(2) action quadratic expansion; derived in the declared background | Independent quartic roots; jointly stationary thermal spectrum remains open |
| `t13.diagnostic.thermal_gradient_curvature` | `p:E^4`; `f:E^2`; `E_xi:1`; `E_xixi:E^-1` | Thermal determinant and implicit derivative; derived in approximation | Direct pressure differences and quadrature checks; no SI conversion |
| `t13.diagnostic.amplitude_path_tadpole` | `x:E^2`; `Omega_x:E^2`; `f_path-f_held:E^2` | Chain rule plus Core Gaussian amplitude derivative; identity within prescription | Same-point independent derivative check; current admission requires stationarity |
| `t13.diagnostic.Ward_tadpole_requirement` | Transverse inverse at zero: `E^2` | Required symmetry/linearized-tadpole cancellation; loop realization open | Guides the next microscopic loop calculation; cannot replace it |

`C` is not mapped to O(2) charge or mass. `Phi` remains a fixed effective response coordinate. `R_gen` and `R_obs` are absent from the moving spectrum and have no feedback.

## Reproduction and numerical limits

The existing natural witnesses are unchanged: `T=0.22`, `Phi=0.15`, `mu=1.05/1.20`. Radial orders are 128/192/256; flow steps are 0.002/0.001/0.0005; angular orders are 8/12. Cutoff factors 50/70/90 are checked at fixed radial order; the primary config uses factor 60. The direct/implicit curvature disagreements are `1.54e-6` and `2.96e-7` relative, below the declared `1e-3` diagnostic tolerance. These are convergence checks, not experimental uncertainties.

```powershell
py docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Moving_Background_Thermal_Stiffness.py
py -m pytest -q docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_moving_background_thermal_stiffness.py
```
