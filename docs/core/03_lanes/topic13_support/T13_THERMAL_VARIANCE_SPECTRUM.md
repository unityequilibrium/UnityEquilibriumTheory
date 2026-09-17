# Frequency attribution of the local variance discrepancy

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The mesh8-to12 covariance-trace difference is attributed to fixed frequency intervals, with total reconstruction checked against the previous artifact.
WHAT_REMAINS_OPEN: Continuum quadrature convergence, spectral branch identity, phase/observable matching and anharmonic physical response.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: INTERNAL_FREQUENCY_ATTRIBUTION_NOT_CONVERGENCE.
WHAT_CHANGED: Separate spectral runner, three tests and source-linked artifact; original covariance artifact and physical gates retained.
EQUATION_OR_MAPPING: Each interval sums the squared mass-metric overlap times the positive harmonic oscillator variance, divided by reduced mass and q-point count. Units are m^2 for trace and cm^-1 for frequency.
VERIFICATION: Three tests PASS: total reconstruction/empty intervals, degenerate-subspace invariance and invalid-frequency/mass rejection. All eight mesh/temperature totals match the earlier artifact within1.45e-15 relative difference. This numerical equality is not physical accuracy.
CONTROLLING_BLOCKER: frequency_resolved_quadrature_convergence_and_physical_mode_mapping.
NEXT_ACTION: Test shifted-mesh sensitivity and cumulative30-to300cm^-1 contributions before extending resolution or assigning branch labels. Frequencies alone cannot identify a shear or acoustic branch.
CLAIM_BOUNDARY: No measured alpha, continuum convergence, material-to-UET identity or physical unlock. Fixed bins are diagnostic partitions, not new acceptance thresholds. No holdout or external acquisition.

## Result at 300 K

The bins were fixed before running: [0,10), [10,30), [30,100), [100,300), [300,1000), [1000,infinity), in cm^-1. Both shifted meshes use the same source and phase convention as the previous local variance calculation.

| Frequency interval | Fraction of mesh12 total trace | Signed fraction of mesh8-to12 net change |
| --- | --- | --- |
| Below30 | 0.0000405% | 0.000248% |
| 30 to100 | 15.9067% | 208.6845% |
| 100 to300 | 22.1177% | -103.4263% |
| 300 to1000 | 46.2791% | 0.1287% |
| Above1000 | 15.6965% | -5.3871% |

The combined30-to300 band accounts for105.2582% of the net change, with higher-frequency decreases partly cancelling it. Signed shares above100% or below zero are valid differences, not probabilities. The30-to300 band contains38.0243% of the final trace, not all of the motion.

The earlier suggestion to investigate low frequencies was a hypothesis. The measured below30 contribution is negligible on these meshes; attributing the error simply to the softest modes would be unsupported. Opposite-signed changes across100 show why a single narrow-bin increase is not evidence that a physical branch has appeared. Different meshes sample different q points, so individual mode migration has not been tracked.

## Remaining checks

Reconstruction confirms the partition but not the shared phase convention: both calculations use the same implementation. A separate observable/phase derivation is still required for physical interpretation. Degenerate rotations wholly inside an interval preserve its sum; a numerical splitting near a bin edge may redistribute weight. Cumulative bands and alternative shifts can distinguish this boundary sensitivity from a robust total discrepancy. No eigenvalue clipping or positive-mode subset was used.

Evidence: `artifacts/t13_thermal_variance_spectrum.json`, including the hash of the prior full covariance artifact and implementation/source files.
