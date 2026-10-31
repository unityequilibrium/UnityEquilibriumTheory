# Core KRSW Two-Face Common-Norm Result

## MAJOR_RESULT_CLOSURE
`CORE_CURVED_3P1_GH_KRSW_NO_STRICT_COMMON_TWO_FACE_CONTRACTION` is `CLOSED_FOR_LANE` for the exact normal-incidence boundary maps only.

## WHAT_IS_ACTUALLY_CLOSED
The exact composition has a nonzero fixed amplitude, with a nonzero intermediate vector. Therefore a single positive-definite quadratic form cannot make both oriented face maps strict contractions on every nonzero amplitude: the strict inequalities would decrease the norm around a cycle that returns exactly to its starting vector.

## WHAT_REMAINS_OPEN
This does not decide whether a common positive-definite form with semidefinite defects exists. It does not identify the algebraic map composition with spatial propagation or a slab mode. Full GH evolution and its discrete energy estimate remain open.

## DEPENDENCY_UNLOCKED
None. `full_core_unlock=false`, `gravity_unlock=false`, and `claim_promotion=false`.

## STATUS
`PASS_EXACT_NO_STRICT_COMMON_FACE_CONTRACTION`; the weak common-norm question remains open.

## WHAT_CHANGED
Added an exact-rational composition audit and a focused regression. No field equation, Core parent gate, or dependency decision was changed.

## EQUATION_OR_MAPPING
Let `u=M_right*v` and `M_left*u=v`, with `v` nonzero. For a common `H>0`, strict contraction would require `v^T H v > u^T H u > v^T H v`, a contradiction. If defects are only positive semidefinite, the cycle instead requires neutral directions `D_right*v=0` and `D_left*u=0`; feasibility is unresolved.

## VERIFICATION
The exact audit passed 5/5 checks and the focused regression passed 3/3 tests. Audit SHA-256: `0047bd4087499795f03109e6aa060e8c6ba98268547618f0dc34550bf3801fe4`; regression SHA-256: `871c10f2783c0e52b8a821b45d65a4158dd439628cb0885c0e71bb3a089f681a`; artifact SHA-256: `f27d0535329f3990cf02f156fd8871954727d948133ee8a5fad17059369459d4`.

## CONTROLLING_BLOCKER
`common_semidefinite_quadratic_form_feasibility_and_full_GH_two_face_energy_estimate_open`.

## NEXT_ACTION
Use the exact neutral-subspace equalities as constraints for a common semidefinite-form feasibility analysis; keep it separate from the evolved GH slab estimate.

## CLAIM_BOUNDARY
No-go only for strict common contraction of these normal-incidence face maps. It is not a no-go for nonincreasing energy, slab stability, full GH CPBC, UET, or Gravity.
