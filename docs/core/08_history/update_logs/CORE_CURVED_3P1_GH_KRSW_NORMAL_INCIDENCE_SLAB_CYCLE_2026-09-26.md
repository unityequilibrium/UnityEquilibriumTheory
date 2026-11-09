# Core KRSW Normal-Incidence Slab-Cycle Result

## MAJOR_RESULT_CLOSURE
`CORE_CURVED_3P1_GH_KRSW_NORMAL_INCIDENCE_SLAB_CYCLE` is `CLOSED_FOR_LANE` for the source-free, flat, linearized, normal-incidence wave system with two plane faces.

## WHAT_IS_ACTUALLY_CLOSED
The d'Alembert characteristics propagate between faces unchanged apart from travel delay. In both face orders, the exact two-face amplitude map is an idempotent rank-4 projection self-adjoint in the positive componentwise symmetric-tensor weight `W`. Consequently, a complete round-trip does not increase the declared wave-system pulse energy; the exact loss is the squared `W` norm of the projected-out component. Repeated complete cycles have no cumulative gain in this lane.

## WHAT_REMAINS_OPEN
This is not the full first-order GH SAT evolution: the lower-order `gamma2` term, tangential/glancing modes, complex-frequency uniform estimates, curvature, variable coefficients, matter, nonlinearities, and edge/corner treatment are excluded. `W` defines a mathematical componentwise wave-system energy, not Bondi/ADM energy or a detector observable.

## DEPENDENCY_UNLOCKED
None. `full_core_unlock=false`, `gravity_unlock=false`, and `claim_promotion=false`; the curved 3+1 parent remains `PARTIAL`.

## STATUS
`PASS_EXACT_NORMAL_INCIDENCE_SLAB_CYCLE_NONAMPLIFICATION`; lane closure only.

## WHAT_CHANGED
Added an exact-rational propagation/projection audit, source-hashed artifact, and focused regression. This follow-up refines the previous map-only interpretation by explicitly solving the restricted one-dimensional wave propagation; it does not close full GH slab evolution.

## EQUATION_OR_MAPPING
For `gamma(t,x)=F(t-x)+G(t+x)`, set `a_s=(partial_t+s*partial_x)gamma`, `b_s=(partial_t-s*partial_x)gamma`, `q_s=-a_s`, `p_s=-b_s`. A right-then-left cycle is `p_R(t+2L)=P p_R(t)`, `P=M_left*M_right`, with the reverse order `M_right*M_left`. For both projectors, `P^2=P`, `P^T W=W P`, and `rank(P)=4`. Thus `E[Pp]=E[p]-(1/4)*integral(((I-P)p)^T W((I-P)p)dt)<=E[p]`; physical cycle time is `2L/c`.

## VERIFICATION
The audit passed 9/9 exact checks; the focused regression passed 3/3 tests. Audit SHA-256: `4323e61c951bc5c49a47d3158ac5480a0cf675f1b9fc1f1878aa444970e82184`; regression SHA-256: `a3920aa1ecae5f75b2012e52c55dbe96814eb7c73273e14b3275e89c46f6bf6d`; artifact SHA-256: `1d0db6a5d16f82919a76ff76f566514e2192b42ab760ede29d9c4993e9ee1b74`.

## CONTROLLING_BLOCKER
`tangential_frequency_full_first_order_GH_energy_estimate_and_corner_treatment_missing`.

## NEXT_ACTION
Extend the exact cycle analysis to nonzero tangential Fourier modes and the complete constraint/physical/gauge characteristic system, then derive an SBP-SAT energy estimate for the actual full-u1 evolution.

## CLAIM_BOUNDARY
Exact normal-incidence non-amplification for the declared standard-GR wave-system lane only. It is not full GH well-posedness, physical gravitational-energy validation, Core curved 3+1 closure, UET validation, or Gravity compatibility. See [Kreiss, Reula, Sarbach, and Winicour, Section IV.1, Eqs. 55-67](https://arxiv.org/html/0807.3207).
