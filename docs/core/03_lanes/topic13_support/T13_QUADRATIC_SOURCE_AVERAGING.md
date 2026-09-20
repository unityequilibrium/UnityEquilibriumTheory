# Spatial averaging of the existing quadratic source

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the finite positive-weight algebraic source identity.
WHAT_IS_ACTUALLY_CLOSED: Spatially averaging the existing quadratic matter source is not equivalent to applying it to spatially averaged matter. The missing term is the within-footprint second central moment.
WHAT_REMAINS_OPEN: Material displacement-to-chi operator and normalization, physical measurement weights, dynamic susceptibility, calibration provenance and quantum/reference treatment.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: SOURCE_AVERAGING_IDENTITY_NOT_CALIBRATION.
WHAT_CHANGED: Production-residual diagnostic, four tests and hashed artifact; no new source or effective dynamics introduced.
EQUATION_OR_MAPPING: For nonnegative w_i summing to1, sum_i w_i J(chi_i)-J(chi_bar)=epsilon*h*sum_i w_i |chi_i-chi_bar|^2/2, with chi_bar=sum_i w_i chi_i and J=epsilon*h*|chi|^2/2.
VERIFICATION: Four tests PASS, four diagnostic rows; largest identity error6.94e-18. First test attempt used an inadmissible negative epsilon; corrected to test the existing nonnegative domain and explicitly assert rejection of negative epsilon. Production validation unchanged. Foundation audit PASS with foundation BLOCKED.
CONTROLLING_BLOCKER: physical_local_second_moment_and_UET_operator_normalization.
NEXT_ACTION: Match an independently measured local second-moment response and its normalization to the existing operator; a coherent spatial mean alone does not identify it. Keep the material and UET variables distinct until that map is established.
CLAIM_BOUNDARY: Classical finite-field identity, not a new closure model, on-shell drive, quantum composite renormalization, physical alpha or Full Topic13 closure. No holdout or source acquisition.

## Why this changes the measurement question

With two equally weighted points chi=(1,0) and(-1,0), chi_bar=0 but average|chi|^2=1. In the declared synthetic epsilon=.5,h=.8 example, the production source average is0.2 while the source of the mean is0. The number is in the existing natural-unit diagnostic lane, not an experimental force or temperature.

The identity follows by expanding chi_i=chi_bar+delta_i and using sum_i w_i delta_i=0. It holds realization by realization and requires no Gaussian assumption. It does not predict the unresolved variance. Turning that variance into an independent dynamical variable would need a new closure and registry treatment, which this pass does not introduce.

For homogeneous zero-mean thermal matter, ensemble expectation of the local square can remain nonzero even when the coherent mean vanishes. Spatial averaging of that local square and squaring a spatial average probe different correlation combinations. A window can suppress coherent fluctuations without removing the mean local quadratic source. Therefore simply replacing the earlier all-mode local RMS by a whole-layer averaged amplitude is not a justified calibration shortcut.

## Boundaries that remain essential

- A material centroid displacement s is not yet chi. Even a validated measurement of average|s|^2 does not supply average|chi|^2 without operator and unit normalization.
- A temperature-modulated source derivative is not independent alpha calibration if the temperature target itself defines the normalization.
- The finite positive-weight averaging identity does not make a signed or complex TTG Fourier amplitude a nonnegative variance. Fourier-transform the local composite operator with its actual weights; do not square the Fourier amplitude and call it the same observable.
- A renormalized quantum composite or vacuum subtraction needs the existing action/reference convention; finite classical algebra does not fix it.
- The residual source is not the measured Phi or heat response; propagation and input-energy accounting remain required.

Evidence: `artifacts/t13_quadratic_source_averaging.json`. This closes a measurement-design ambiguity while retaining all material calibration blockers.
