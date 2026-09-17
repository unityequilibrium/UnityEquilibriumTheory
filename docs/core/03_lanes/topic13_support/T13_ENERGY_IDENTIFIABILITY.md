# Energy is not identified by this ideal response alone

MAJOR_RESULT_CLOSURE: PARTIAL; conditional numerical ambiguity of fixed-frequency energy demonstrated at all six sampled q points.

WHAT_IS_ACTUALLY_CLOSED: Rank deficiency does affect the energy functional, including when restricted to the eight geometrically visible columns. Constructed positive occupation pairs give nearly identical model responses but different energies. The test separately confirms that some rank-deficient systems can identify a sum, so this is not inferred from rank deficiency alone.

WHAT_REMAINS_OPEN: Independently energy-sensitive data, physically justified population relations, experimental response/covariance, full-zone integration, preparation/work balance and independent Phi coupling.

DEPENDENCY_UNLOCKED: Selection of complementary energy information only; no physical gate.

STATUS: NULL_SPACE_TESTED_NOT_THERMOMETRY; full_core_unlock=false.

WHAT_CHANGED: Added observable null-space audit, three tests, candidate registry and counterexample artifact. No source data, temperatures or mode frequencies were fitted.

EQUATION_OR_MAPPING: At fixed positive source frequencies, A=S/f and c=f. Population energy change is h*1e12 Hz times c^T delta_n for numerical f in THz. Identifiability requires c in row(A). The orthogonal component of c supplies a numerical near-null response direction with nonzero energy projection. Frequency changes would introduce work and are outside this test.

VERIFICATION: Three tests check identifiable sums despite unresolved populations, positive counterexamples and invisible-mode ambiguity. Six actual source response matrices and upstream hashes checked. Constructed occupations lie between 0.75 and 1.25. Relative response residuals are 4.14e-16 to 5.82e-15. Rank-tolerance sensitivity is recorded at 1e-9, 1e-10 and 1e-11; no physical threshold was changed.

CONTROLLING_BLOCKER: independent_energy_information_or_justified_population_constraint.

NEXT_ACTION: Assess an independently calibrated energy/thermometry observable or a source-backed equilibrium/kinetic constraint in the actual preparation. Evaluate its added row-space information and uncertainty before fitting. Do not impose equilibrium merely to obtain a unique answer.

CLAIM_BOUNDARY: Conditional fixed-harmonic-source numerical counterexamples, not actual observed populations, global no-go, calorimetry, heat transport, alpha calibration or Full Topic 13 closure. No holdout input. No negative mode clipping or zero-filled invisible populations.

## Actual diagnostic results

| Reduced q | Full energy null-component ratio | Visible-only energy null-component ratio |
| --- | ---: | ---: |
| (0.005,0,0) | 0.99752 | 0.99715 |
| (0.02,0,0) | 0.99058 | 0.98915 |
| (0.1,0,0) | 0.84647 | 0.82189 |
| (0.005,0.005,0) | 0.92523 | 0.91340 |
| (0.02,0.02,0) | 0.71958 | 0.66730 |
| (0.1,0.1,0) | 0.52750 | 0.42535 |

These ratios describe Euclidean projection of the energy coefficient vector.
They are not missing-energy percentages, temperature errors or confidence bounds.
The counterexamples are constructed around unit occupations, not thermal Bose
populations, actual source states or permission to substitute synthetic data.
Both absolute populations remain positive; positivity alone therefore does not
remove ambiguity within this model. Full-zone energy and actual experimental
resolution remain untested.

## Research decision

Do not require full population reconstruction automatically; first ask whether
the target observable is identifiable. That less restrictive test was performed
and still fails here. Extra analysis of the same model rows cannot uniquely
determine energy without new information. This does not block research on source
power/energy balance, independent thermometry, off-plane observables or justified
kinetics. None of those is silently assumed available or sufficient.

Evidence: `artifacts/t13_energy_identifiability_audit.json` contains full witness
populations, residuals, energy differences and tolerance sweeps. The fixed-gap
formula is consistent with the earlier work/heat distinction; it is not a claim
that all pump-induced energy change is heat.
