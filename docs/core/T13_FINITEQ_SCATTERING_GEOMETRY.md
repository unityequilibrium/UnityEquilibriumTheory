# Finite-q response gains information but remains rank deficient

MAJOR_RESULT_CLOSURE: PARTIAL; declared finite-q phase convention cross-checked and ideal geometric rank measured.

WHAT_IS_ACTUALLY_CLOSED: At six reduced wavevectors and 24 basal reciprocal vectors, the implemented geometry agrees with installed Phonopy amplitude algebra. Eight numerically visible columns have rank six on q=(s,0,0) and five on q=(s,s,0), for s=0.005,0.02,0.1.

WHAT_REMAINS_OPEN: Whether unresolved combinations change total energy; finite-q branch tracking; actual detector geometry, elastic contamination, atomic/site factors, covariance and independent Phi coupling.

DEPENDENCY_UNLOCKED: Observable-identifiability research only; no physical gate.

STATUS: REFERENCE_MATCHED_GEOMETRY_ONLY; full_core_unlock=false.

WHAT_CHANGED: Added finite-q geometric operator, candidate registry addendum, three tests and actual source artifact. All 12 mode columns are retained in the artifact. Numerical visibility is used only for normalized-rank diagnostics.

EQUATION_OR_MAPPING: S_j(Q)=|sum_s exp(2pi i G.x_s) Q.conj(e_sj(q))/sqrt(m_s)|^2. Phonopy's eigenvector convention uses the reciprocal-lattice vector G in the atomic phase; Q=G+q enters the polarization contraction. Common scattering/Debye-Waller factors and frequency/population factors are omitted.

VERIFICATION: Three tests cover Gamma limit, eigenvector phase invariance and equivalent atomic gauge transformation. Maximum relative amplitude-weight discrepancy against the installed Phonopy routine is 5.603e-16. Reference method hash/version recorded. This is an algebra/implementation cross-check, not independent validation of the force constants. F0 inventory remains 369 formula rows with no duplicates.

CONTROLLING_BLOCKER: energy_functional_identifiability_and_physical_detector_operator_missing.

NEXT_ACTION: Test whether the physical energy functional lies in the measured response row space after frequency weighting. If not, identify additional independent observables required. Retain invisible modes explicitly and do not assume equal populations to erase null directions.

CLAIM_BOUNDARY: Ideal kinematic model at declared q/G points, not measured UED rank, full population recovery, temperature, TTG validation or physical alpha. No fitting, holdout input, negative-frequency clipping or full-topic promotion.

## Rank interpretation

The column-normalized operator has two or three near-null directions among
eight numerically visible columns, respectively. Four more columns are below
the declared geometric visibility diagnostic. These are not experimentally
measured sensitivity limits. Actual noise and atomic factors can worsen useful
conditioning; detector coverage is not established by this reciprocal grid.

Each q has independent unknown populations. Stacking different q values cannot
remove ambiguity without an explicit physical relation between those unknowns.
The earlier Gamma calculation used two pair-summed columns; the present count
uses individual branches and is not a like-for-like quantitative rank increase.

Numerical diagnostics were set to 1e-12 relative column visibility and 1e-10
relative singular-value rank. They are unrelated to causal leakage thresholds.
The smallest retained normalized singular value ranges from roughly 0.0177 to
0.409 on the first path and 0.0389 to 0.225 on the second; no physical precision
or uncertainty is inferred from those values alone.

The phase convention and distinction between geometric amplitude and full
dynamic structure factor follow [Phonopy documentation](https://phonopy.github.io/phonopy/dynamic-structure-factor.html).
The cross-check sets an artificial reference frequency to one solely to divide
out its known frequency factor. Source frequencies are stored unchanged and
never replaced in a physical calculation. Common atomic factors set to one are
likewise a geometry convention, not electron-scattering calibration.

Evidence: `artifacts/t13_finiteq_scattering_geometry_audit.json`.
