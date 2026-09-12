# Local second-moment observability in existing scattering designs

MAJOR_RESULT_CLOSURE: PARTIAL; target-specific ambiguity and a conditional complementary-geometry route established.
WHAT_IS_ACTUALLY_CLOSED: The local displacement second moment is tested directly, rather than inferring its identifiability from full-population rank or energy identifiability. Basal-only geometry fails for all six tested q; the existing complementary design identifies this target algebraically.
WHAT_REMAINS_OPEN: Real detector coverage, physical response scale, covariance/noise, mode coherences, BZ coverage and material-to-UET operator normalization.
DEPENDENCY_UNLOCKED: None; no physical gate or full_core_unlock.
STATUS: IDEAL_TARGET_OBSERVABILITY_NOT_EXPERIMENTAL_CALIBRATION.
WHAT_CHANGED: Reused existing null-space and scattering routines with the local variance target; three tests, six-q/two-design artifact and this note. No population fit.
EQUATION_OR_MAPPING: A=S/f_THz; c_j=||B^dagger P e_j||^2/f_THz. For fixed frequencies and diagonal occupations, delta trace per q=hbar*c.delta_n/(mu_kg*2*pi*1e12), before BZ weights. Identifiability requires c in row(A).
VERIFICATION: Three tests PASS. Positive synthetic occupation pairs produce relative model-response residuals7.17e-16 to7.09e-15 but different local targets. Basal null fractions0.04377 to0.35067; complementary null fractions below9.46e-16. Rank tolerances1e-9,1e-10,1e-11 recorded without altering physical thresholds.
CONTROLLING_BLOCKER: physical_detector_geometry_covariance_and_material_operator_matching.
NEXT_ACTION: Follow T13_BASAL_COVERAGE_EXTENSION.md: generic-q basal rows can identify this target in the same ideal model. Inspect existing image coverage there before requesting complementary planes. Do not fit the original ambiguous symmetry-line rows to a unique variance; actual detector noise/conditioning remains required.
CLAIM_BOUNDARY: Conditional harmonic single-phonon diagonal-occupation result, not a universal scattering no-go or acquired experiment. No absolute alpha, TTG holdout, thermometry or Full Topic13 closure.

## What is new relative to the energy audit

The prior energy target used frequency weights. Local displacement variance instead weights modes by projected relative-layer motion divided by frequency. Rank deficiency alone does not decide whether either scalar target is known. The present test evaluates this different target explicitly using the same declared source and geometry.

The six points are q=(s,0,0) and(s,s,0), s=.005,.02,.1. Basal geometry uses24 noncentral h,k vectors with l=0. The existing complementary design uses the same h,k set for l=-2,-1,0,1,2. This is a proposed ideal measurement set, not a claim that an archived detector acquired those rows.

All12 mode columns are retained. Constructed positive occupation pairs lie between.75 and1.25. Their target differences are about2.27% to20.17% of the unit-population reference target while their model responses coincide to floating-point precision. These are witnesses of ambiguity, not measured thermal populations, uncertainty bars, equilibrium states or realizable preparations.

The complementary response has numerical rank12 at each tested q, so its target null projection vanishes numerically. This establishes a possible geometry route, not practical precision. Missing scattering factors, elastic contamination, detector resolution and noise can obstruct real estimation. Repeating the same basal geometry does not remove its ideal null direction; independent information or a justified physical constraint is required.

## Boundary of the variance target

The result assumes fixed frequencies and incoherent diagonal mode occupations. Off-diagonal coherences or changing force constants require a larger observation model. Each q has distinct unknown populations; unrelated q cannot be stacked as repeated measurements of the same vector. Full local variance needs Brillouin-zone coverage and its quadrature weights. None of these conditions is supplied by a six-point rank calculation.

Even ideal identification of this material displacement target would not identify the UET composite chi^2 or its source coupling without an explicit operator/unit map. This result narrows the measurement design problem; it does not remove that physical matching requirement.

Evidence: `artifacts/t13_local_variance_identifiability.json`, including both complete response designs, target weights, positive witnesses, tolerance sweeps and source/code hashes.
