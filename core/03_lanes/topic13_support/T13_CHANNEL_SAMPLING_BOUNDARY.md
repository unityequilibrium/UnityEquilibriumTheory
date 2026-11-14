# Channel attribution and incoming sampling boundary

MAJOR_RESULT_CLOSURE: PARTIAL; finite-sample error attribution and a structural sampling limitation identified.
WHAT_IS_ACTUALLY_CLOSED: All 64 signed channel contributions reconstruct the two-probe matrix error. At quadrature order24 the incoming radial pair sequence repeats after21 channels; increasing channel count cannot fill the missing radial pairs.
WHAT_REMAINS_OPEN: A consistent phase-space integration measure, angular coverage, stable interpolation, projected full-operator and inverse error, and material/source/calibration closure.
DEPENDENCY_UNLOCKED: None; full_core_unlock remains false.
STATUS: INTERNAL_SAMPLER_COVERAGE_LIMITATION_IDENTIFIED.
WHAT_CHANGED: Attribution artifact and tests from the preceding computation are retained; this note records the inspected production index rule. No production rates or equations changed.
EQUATION_OR_MAPPING: j1=(2*i+3) mod21 +2; j2=(3*i+7) mod21 +2. Since gcd(2,21)=1 and gcd(3,21)=3, j1 covers21 indices but j2 only7; the ordered pair has period21.
VERIFICATION: Direct enumeration of indices0..63 yields21 unique pairs out of441 possible ordered pairs within indices2..22. The second index is restricted to3,6,9,12,15,18,21. The attribution artifact reports relative two-probe Gram error0.5517330227342936 and signed reconstruction residual8.67e-19. These are deterministic diagnostics, not statistical error bars.
CONTROLLING_BLOCKER: incoming_phase_space_coverage_and_measure_before_channel_count_convergence.
NEXT_ACTION: Design a separately named quadrature candidate with independent incoming radial nodes, incoming relative-angle integration, outgoing solid-angle weights and species bookkeeping. Validate normalization and known integral moments before replacing any collision calculation; then compare interpolation and transport under independent refinements.
CLAIM_BOUNDARY: The existing module explicitly supplies finite exact-kinematic channels, not continuum integration. This result limits its use as a continuum reference; it does not invalidate per-channel conservation or prove that the physical collision model fails.

## What the attribution establishes

Channels20,41,62 share incoming radial indices and each has about one third of the sampled rate. Almost all absolute matrix-error witness weight is inside the cutoff; outside legs contribute about1.33e-114 of that absolute weight. Do not delete or reweight channels based on this ranking. Signed error contributions can cancel and are not probabilities.

Incoming directions cycle through adjacent Cartesian axes, so their relative cosine is always zero. Outgoing polar angles take seven values0.43..1.09 radians; their azimuth changes with index. The radial repetition does NOT imply identical full channels. Neither more azimuths nor a normalization factor can supply missing incoming radial pairs or incoming relative angles.

The phase_measure in the current implementation multiplies selected radial quadrature weights; it does not implement a full independent radial-pair sum. This is consistent with a finite-channel interface, but channel-count growth alone is not a quadrature-convergence test. A replacement needs a declared integration measure, not an empirical correction chosen to improve the two probes.

Evidence: `artifacts/t13_channel_error_attribution_audit.json` (source hashes included); production rule in `uet_o2_action_derived_transition_kernel.py`. No external or holdout data were accessed for this inspection. Full Topic13 remains open.
