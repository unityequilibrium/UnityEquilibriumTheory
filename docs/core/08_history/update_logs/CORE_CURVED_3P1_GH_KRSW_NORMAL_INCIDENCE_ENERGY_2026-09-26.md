# Core KRSW Normal-Incidence Boundary-Form Result

## MAJOR_RESULT_CLOSURE
`CORE_CURVED_3P1_GH_KRSW_NORMAL_INCIDENCE_BOUNDARY_ENERGY_IDENTITY` is `CLOSED_FOR_LANE` for an exact flat-background, linearized-GR, normal-incidence boundary-algebra lane only.

## WHAT_IS_ACTUALLY_CLOSED
The KRSW plane-boundary hierarchy and harmonic constraints were reconstructed with rational arithmetic for both face orientations. Each one-face map has rank 4, its square has rank 1, and its cube is exactly zero. An explicitly constructed positive quadratic form satisfies the declared characteristic-form identities exactly. The two-face algebraic composition has an exact fixed amplitude in the `h_02` and `h_12` coordinates.

## WHAT_REMAINS_OPEN
The quadratic form has not been identified with the energy of the evolving Core GH discretization. The fixed amplitude is a composition of boundary maps, not a propagated slab mode. Tangential/glancing and general complex-frequency estimates, a two-face discrete slab energy estimate, corner handling, and variable-coefficient/nonlinear GH evolution remain open.

## DEPENDENCY_UNLOCKED
None. `full_core_unlock=false`, `gravity_unlock=false`, and `claim_promotion=false`. The curved 3+1 parent remains `PARTIAL`; this result does not change Topic 13 status.

## STATUS
`PASS_EXACT_ONE_FACE_NORMAL_INCIDENCE_BOUNDARY_FORM_IDENTITY`; major-result closure is lane-bounded only.

## WHAT_CHANGED
Added a deterministic exact-rational audit, a machine-readable evidence artifact, and focused regression tests. No Core physical equation, parent gate, or downstream dependency was changed.

## EQUATION_OR_MAPPING
For each outward normal sign `s`, let `a=(partial_t+s*partial_x)gamma`, `b=(partial_t-s*partial_x)gamma`, `q=-a`, and `p=-b`. The hierarchy gives `A_s a+B_s b=0` and hence `q=M_s p`. With `chi=1/4`, `r=(1-chi)/(1+chi)=3/5`, `H=W+r^-1 M^T W M+r^-2(M^2)^T W M^2`, and `W=diag(1 for diagonal, 2 for off-diagonal tensor slots)`, exact arithmetic gives `M^T H M=r(H-W)` and the declared quadratic boundary form `F=-3 p^T W p/8`.

## VERIFICATION
The audit passed all 8 exact checks; the focused regression passed 3/3 tests. Audit SHA-256: `434febb7aa4e216039093fc7b08debe5c014072a6ce988842293dd4f3b998062`; regression SHA-256: `8ee9b8732a20b871db554e49db59b74a5828ad2e054bb63e411bda45941b972c`; artifact SHA-256: `38c1d3091a2d126506e5ed1a17351caae639b8b335ae868cdd4104d1b1b215d6`. Primary comparator: [Kreiss, Reula, Sarbach, and Winicour, *Boundary conditions for coupled quasilinear wave equations with application to isolated systems*, Section IV.1, Eqs. 55-67](https://arxiv.org/html/0807.3207).

## CONTROLLING_BLOCKER
`projector_compatible_two_face_discrete_energy_estimate_for_full_GH_evolution_missing`.

## NEXT_ACTION
Derive the two-sided projector-compatible discrete energy estimate before another boundary-coefficient sweep. Then test the full GH boundary evolution, including spatial convergence and edge/corner behavior, without interpreting the algebraic fixed amplitude as an evolved mode.

## CLAIM_BOUNDARY
An exact algebraic standard-GR comparator for normal incidence only. It is not a full Kreiss estimate, slab stability proof, Core curved 3+1 closure, UET validation, Gravity compatibility, or evidence for Topic 13.
