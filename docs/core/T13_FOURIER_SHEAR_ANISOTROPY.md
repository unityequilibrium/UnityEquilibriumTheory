# First-Fourier model anisotropy estimate

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A published potential supplies a conditional, quantitative cubic-force comparison rather than an arbitrary anisotropy coefficient.
WHAT_REMAINS_OPEN: Higher-harmonic derivative errors, same-state displacement amplitudes, mode normalization and thermal dynamics.
DEPENDENCY_UNLOCKED: None.
STATUS: MODEL_DEPENDENT_ESTIMATE_NOT_MATERIAL_BOUND.
WHAT_CHANGED: Taylor audit, two tests and hashed artifact; no production action changed.
EQUATION_OR_MAPPING: In bond-length coordinates k=2*pi/3, U/U1=3*k^2*r^2/2-sqrt(3)*k^3*(x^3-3*x*y^2)/2+O(r^4). Leading cubic/harmonic force ratio=pi*r/sqrt(3).
VERIFICATION: Two tests PASS; numerical gradients and quadratic remainder scaling checked. At r=.005 the sampled full-potential force discrepancy is0.9123%, versus leading0.9069%.
CONTROLLING_BLOCKER: higher_spatial_harmonic_derivatives_and_same_state_amplitude.
NEXT_ACTION: Bound omitted Fourier derivatives or compare same-state anharmonic force constants; evaluate actual mode amplitude before proposing a controlled O(2) approximation.
CLAIM_BOUNDARY: No measured cubic coefficient, material tolerance guarantee, alpha or full-topic closure. Small potential-fit error does not itself bound derivatives. The1% example is illustrative, not a new acceptance gate.

Source: [Popov et al., Eq.(1), PDF page4](https://arxiv.org/pdf/1205.0777). Model transcription uses the AB reference at x=y=0. The leading1% radius is0.005513 bond lengths (about0.00783 angstrom with the source's1.42-angstrom bond). No source numeric fitting was performed here.

Evidence: artifacts/t13_fourier_shear_anisotropy_audit.json. Angular maxima are sampled over360 directions, not rigorous global bounds. Potential scale U1 cancels in the force ratio; that cancellation does not identify an absolute UET coupling.
