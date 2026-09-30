# Rest-EOS versus longitudinal sound: a bounded two-fluid EFT witness

MAJOR_RESULT_CLOSURE: `T13_REST_EOS_DYNAMICAL_RESPONSE_NONIDENTIFIABILITY_BOUNDARY` is `CLOSED_FOR_LANE` in a declared standard nondissipative two-fluid EFT class only.

WHAT_IS_ACTUALLY_CLOSED: An explicit pair has the same complete *rest* thermodynamics for every positive `b,y`, yet different low longitudinal characteristic speeds. Thus rest pressure/charge/entropy/energy calibration alone does not determine sound in this class. The distinguishing input is the coefficient of relative phase-normal flow, not another rest-EOS row.

WHAT_REMAINS_OPEN: Lifting Core's tree phase stiffness into one stationary finite-T relative-flow current, mapping it to physical He-II, source/detector coupling, dissipative attenuation, and an independent source.

DEPENDENCY_UNLOCKED: A precise measurement/derivation target, `-2 F_X` (or its independently established UET counterpart), only. Physical G1/G2 and Full Topic 13 remain locked.

STATUS: `PASS_SCOPED_STANDARD_EFT_CONSTRUCTIVE_WITNESS`; UET physical operator `NOT_ADMITTED`.

WHAT_CHANGED: Added an executable analytic example, generated [machine result](t13_funding_rest_eos_dynamic_degeneracy.json), two guard tests, and this derivation note. No Core equation, calibration, data role or holdout policy changed.

EQUATION_OR_MAPPING: In the [Nicolis finite-T superfluid EFT](https://arxiv.org/html/1108.2513), take `X=-y^2+xi^2` and, solely as an external comparator,

```text
F_zeta(b,X,y) = -3 b^(4/3)/4 + y^2 - zeta (X+y^2)/2,  zeta>0.
```

At relative rest, `xi=0`, so `F_zeta|rest=F_0` for *every* `b,y`. The rest identities are `p=y^2+b^(4/3)/4`, `epsilon=y^2+3b^(4/3)/4`, `n=2y`, `s=b`, `T=b^(1/3)` and `epsilon+p=Ts+yn`; none depends on `zeta`. But `F_X=-zeta/2`, so the quadratic longitudinal action has `G_S=-2F_X y^2=zeta y^2` and its mode roots solve

```text
(K_N c^2-G_N)(K_S c^2-G_S)-M^2 c^2 = 0.
```

At `b=y=1`: `K_N=3-zeta`, `G_N=1/3`, `K_S=2`, `G_S=zeta`, `M=zeta-2`. For `zeta=0.1` and `0.2`, the low-mode `c^2` is `0.0073682232` and `0.0152156313`; the upper mode `c^2` is `0.7799880986` and `0.7824034163`. The variables and coefficients are rescaled for a dimensionless witness; dimensional physical coefficients and an SI map are not supplied. Both examples have positive quadratic Hamiltonian coefficients and subluminal *linear longitudinal* roots at the named anchor; no global causal or material proof follows.

Core does already provide `f_s_tree=Z*q/lambda` as a formal natural-unit phase-gradient coefficient. Comparing `G_S=-2F_X y^2` with a tree gradient term `f_s_tree*(grad theta)^2/2` gives the **conditional** relation `-2F_X=f_s_tree` if `theta=psi`, phase normalization, stationary branch and units agree. The frozen normal reference has `q=-0.8715`, hence tree stiffness zero; two unadmitted tree-condensed witnesses have `f_s_tree=0.1085` and `0.446`. This is a candidate *tree coefficient* correspondence, not a finite-T current identity or physical He-II state selection.

VERIFICATION: [Verifier](../../Code/03_Research/Research_T13_Funding_RestEOS_Dynamic_Degeneracy.py) checks exact rest-state equality, quadratic energy signs, both secular residuals below `1e-12`, subluminal roots, and the formal tree-stiffness values from hashed Core/Topic13 sources. The [tests](../../Code/03_Research/test_t13_funding_rest_eos_dynamic_degeneracy.py) also check `epsilon+p=Ts+yn` at three off-anchor states, the `zeta -> 0` analytic root limit, and non-admission of the two condensed witnesses. Three focused tests pass. Artifact SHA-256: `d483a7242be63e712f234ceed21aafef95605ad730705cc99159a015eb6e47ba`. Xie 2026 was not read.

CONTROLLING_BLOCKER: The present Core static lane exposes a *formal* natural-unit condensate phase stiffness, so this pair does **not** prove that every Core static input leaves sound undetermined: changing `zeta` changes the corresponding relative-flow curvature. The remaining UET task is to lift its tree coefficient into a finite-T stationary relative-flow current and SI/material/source correspondence in one admitted scheme. A rest-EOS-only calibration cannot replace that task.

NEXT_ACTION: Derive the finite-T current and longitudinal source operator that corresponds to Core's formal tree stiffness, then obtain an independently selected condensed He-II state and material scale. If this lift fails, specify an independent relative-flow/stiffness measurement or a scoped UET-class counterexample. Do not call this standard-EFT witness G2 scientific closure.

CLAIM_BOUNDARY: This is not two UET completions, a general UET nonidentifiability theorem, a physical He-II second-sound prediction, an external comparison, or Full Topic 13 closure. The EFT introduces normal-fluid comoving coordinates for the comparator; they are not silently added to UET's ontology. `R_gen` is not a state.
