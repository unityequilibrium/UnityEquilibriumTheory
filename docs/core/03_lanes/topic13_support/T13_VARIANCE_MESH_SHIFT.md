# Local variance grid-shift sensitivity

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Fifteen fixed shift/resolution cases at300K establish that the sampled shift spread is much smaller than the remaining refinement difference.
WHAT_REMAINS_OPEN: Continuum convergence, directional resolution, physical phase/mode mapping and anharmonic corrections.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: INTERNAL_QUADRATURE_DIAGNOSTIC_NOT_CONVERGED.
WHAT_CHANGED: Separate shift runner, three tests and hashed artifact; original source, covariance artifacts and physical gates unchanged.
EQUATION_OR_MAPPING: Existing source harmonic covariance trace averaged on q_i=(i+s_i)/n-1/2. Units m^2; RMS converted to angstrom.
VERIFICATION: Three grid tests PASS;15 scientific cases completed without sampled nonpositive modes. Complementary quarter/three-quarter shifts agree within2.11e-15 relative trace difference. Foundation audit PASS with foundation BLOCKED.
CONTROLLING_BLOCKER: quadrature_convergence_and_material_observable_mapping.
NEXT_ACTION: Separate in-plane and out-of-plane refinement before further isotropic enlargement; verify the physical phase convention independently. Retain all tested shifts, not just the most favorable value.
CLAIM_BOUNDARY: Shift range is not a confidence interval, physical error bound or convergence proof. No alpha, holdout use, parameter fitting or readiness promotion.

## Fixed experiment and outcome

Meshes8,12,16 and shifts(.5,.5,.5),(.25,.25,.25),(.75,.75,.75),(.5,.5,.25),(.25,.25,.5) were declared before running. Shifts are fractional cell subdivisions. All modes contribute; any nonpositive eigenvalue invalidates that entire case rather than returning the positive subset.

| Mesh | RMS range, angstrom | Trace range divided by range midpoint |
| --- | --- | --- |
| 8 | 0.0747881 to0.0749445 | 0.41781% |
| 12 | 0.0778124 to0.0779931 | 0.46411% |
| 16 | 0.0797009 to0.0798630 | 0.40636% |

The half-shift trace still increases4.9131% between12 and16, compared with8.2511% between8 and12. Smaller successive changes alone do not establish convergence or an extrapolation law. The sampled shift ranges do not overlap across those resolutions. Choosing a different tested shift therefore does not remove the observed mesh drift.

Changing only the out-of-plane shift has a very small effect in these cases, while changing the in-plane shifts changes the trace more. This motivates a directional-resolution test; it does not establish physical dimensional reduction or absence of interlayer dynamics. Equivalent inversion pairs are a numerical consistency check, not independent uncertainty samples.

The same local phase convention is shared with earlier calculations. Its correctness cannot be established by agreement between these implementations. No result here authorizes replacing the all-mode local fluctuation with a coherent shear-mode amplitude or identifying it with UET Phi.

Evidence: `artifacts/t13_variance_mesh_shift.json`, including all15 rows, source/implementation hashes and runtime version.
