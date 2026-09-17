# Directional resolution of local thermal variance

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The tested refinement drift is localized predominantly to reciprocal in-plane resolution, not out-of-plane resolution at fixed16x16 sampling.
WHAT_REMAINS_OPEN: Continuum accuracy, coupled directional refinement, physical phase/observable mapping and anharmonic material response.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: INTERNAL_DIRECTIONAL_DIAGNOSTIC_NOT_CONVERGED.
WHAT_CHANGED: Six-case directional runner, three tests, hashed artifact and this interpretation; earlier artifacts retained.
EQUATION_OR_MAPPING: Existing source harmonic covariance trace with separate reciprocal-axis mesh sizes, in m^2; local relative-layer RMS in angstrom.
VERIFICATION: Three tests PASS; all six scientific cases completed without sampled nonpositive eigenvalues. Isotropic grid exactly reproduces the existing grid generator. Foundation audit PASS with foundation BLOCKED.
CONTROLLING_BLOCKER: directional_convergence_and_independent_phase_mapping.
NEXT_ACTION: Independently audit the intracell phase and displacement observable before using further numerical refinement to claim a physical amplitude. Further mesh work should prioritize in-plane resolution and recheck the out-of-plane direction at finer in-plane sampling.
CLAIM_BOUNDARY: No physical dimensional reduction, converged amplitude, UET alpha or Full Topic13 closure. No clipping, fit, holdout acquisition or threshold change.

## Measured sequence at300K

| Grid | Relative-layer RMS, angstrom |
| --- | --- |
| 8x8x8 | 0.0747881 |
| 16x16x8 | 0.0797009 |
| 32x32x8 | 0.0829739 |
| 48x48x8 | 0.0839382 |
| 16x16x16 | 0.0797009 |
| 16x16x32 | 0.0797009 |

At fixed third-axis size8, the trace changes13.5696%,8.3817%,2.3378% along the8-to16-to32-to48 in-plane sequence. These are unequal refinement ratios, so they do not by themselves give a convergence order or justified extrapolation. The final value is not a calibrated physical amplitude.

At fixed16x16 in-plane sampling, third-axis8-to16 and16-to32 trace changes are approximately-8.40e-10 and-3.32e-11 relative. This supports allocating the next quadrature effort in-plane, but does not prove the third direction is negligible for arbitrarily fine meshes, other observables or physical dynamics.

## Correction to the scope of the earlier spectral result

The earlier below30cm^-1 contribution was negligible on meshes8 and12. On48x48x8 it is1.8553% of the total trace. Thus that earlier measured fact must not be generalized to the continuum. The frequency attribution itself changes with resolution; a frequency interval is not a tracked physical branch.

All calculations share the same phase convention and local centroid coordinate. Agreement between implementations cannot independently validate that convention. This shared assumption now deserves direct verification rather than accumulating further similar mesh artifacts. Nothing here makes the local all-mode RMS interchangeable with a coherent Gamma shear amplitude, Popov slip coordinate or UET Phi.

Evidence: `artifacts/t13_variance_directional_grid.json` with fixed grids, bins, source/implementation hashes and runtime version. No statistical uncertainty has been inferred from this deterministic sequence.
