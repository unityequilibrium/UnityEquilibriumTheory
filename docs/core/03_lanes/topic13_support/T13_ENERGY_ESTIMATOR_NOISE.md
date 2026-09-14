# Energy estimator sensitivity, not an experimental error bar

MAJOR_RESULT_CLOSURE: PARTIAL; unbiased minimum-variance energy weights computed for the ideal complementary design.

WHAT_IS_ACTUALLY_CLOSED: Scalar energy weights satisfy A^T w=c and minimize variance for each declared hypothetical covariance. Full-state reconstruction is not required to form this estimator. Near-Gamma energy estimation remains sensitive despite full algebraic rank.

WHAT_REMAINS_OPEN: Actual covariance, intensity calibration, preparation/orientation consistency, exposure budget, model error, accessible reciprocal coverage and independent Phi coupling.

DEPENDENCY_UNLOCKED: Noise-aware measurement design only.

STATUS: UNBIASED_WEIGHTS_CHECKED_REAL_NOISE_OPEN; full_core_unlock=false.

WHAT_CHANGED: Added covariance-weighted estimator, registry addendum, three tests and source-model design artifact. No experimental noise was fabricated or substituted.

EQUATION_OR_MAPPING: Minimize w^T Sigma w subject to A^T w=c; E_hat=w^T y. Cholesky whitening and a minimum-norm constrained solve avoid normal equations. A and c are separately normalized by their spectral/Euclidean norms, and scales are recorded.

VERIFICATION: Three tests cover inverse-variance averaging, rank-deficient identifiable sums, rejection of unidentifiable targets, covariance scaling and larger variance from an unbiased null perturbation. Actual source/hash checks retained. F0: 369 rows, no duplicate IDs.

CONTROLLING_BLOCKER: measured_covariance_and_absolute_intensity_scale_missing.

NEXT_ACTION: Replace hypothetical covariance with actual repeat/processed-data covariance and restore physical response scale. Evaluate energy variance under a fixed acquisition budget; do not rank experiments using these normalized gains alone. Independent thermometry remains an alternative.

CLAIM_BOUNDARY: Ideal complementary design with hypothetical noise, not measured precision, population fit, temperature, physical alpha or full-topic closure. No holdout. Common gain error, parameter/model uncertainty and inaccessible rows are not corrected here.

## Normalized noise gain

| q | Independent unit noise | Correlated case rho=0.2 |
| --- | ---: | ---: |
| (0.005,0,0) | 2173.28 | 2389.92 |
| (0.02,0,0) | 532.01 | 584.68 |
| (0.1,0,0) | 78.68 | 83.54 |
| (0.005,0.005,0) | 1348.94 | 1490.02 |
| (0.02,0.02,0) | 323.80 | 357.61 |
| (0.1,0.1,0) | 54.90 | 61.13 |

Covariance is (1-rho)I+rho*11^T with unit marginal variance, solely an illustrative
design assumption. Each gain is standard deviation of normalized energy per unit
normalized input noise, not kelvin or relative energy error. Separate A/c scaling
across q means this is not an equal-exposure physical comparison. Positive common
correlation need not worsen all estimators in general; these particular cases do.

This prevents a premature inference from full rank to usable thermometry. The
implementation provides a direct energy uncertainty calculation when actual
response/covariance become available; it does not supply those missing inputs.
Evidence: `artifacts/t13_energy_estimator_noise_audit.json`.
