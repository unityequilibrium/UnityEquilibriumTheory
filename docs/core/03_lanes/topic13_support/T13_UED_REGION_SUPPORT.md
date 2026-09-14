# Source-strip extraction and remaining physical inversion

MAJOR_RESULT_CLOSURE: PARTIAL; changing finite support excluded for this specific archived strip, not for the full experiment.

WHAT_IS_ACTUALLY_CLOSED: The source-coordinate near-Bragg strip has 627 pixels in the 400 nm scan and 608 in the 800 nm scan. Every selected pixel is finite in every ON/OFF frame. Pairwise and common-support ratios coincide exactly.

WHAT_REMAINS_OPEN: Bragg/diffuse separation, branch-resolved scattering weights, inversion rank, preprocessing covariance, material equivalence and independent Phi coupling.

DEPENDENCY_UNLOCKED: Forward-scattering analysis of this region only; no physical downstream gate.

STATUS: REGION_EXTRACTED_INVERSION_OPEN; full_core_unlock=false.

WHAT_CHANGED: Added coordinate-based strip audit and three geometry tests. No image smoothing, background subtraction, fit, missing-value replacement or new core equation.

EQUATION_OR_MAPPING: Source cells 2, 7 and 8 define |kx|<0.5 inverse angstrom and |ky-L*cal|<0.1*b, where b=4*pi/(sqrt(3)*2.46 angstrom). Each scan uses its own origin, calibration and peak distance. This diagnostic sums the strip before taking ON/OFF ratios and removes the mean baseline at delay < -0.5 ps. The author figure instead retains a ky-resolved profile and uses additional smoothing.

VERIFICATION: Six linked support/geometry tests pass. Actual exported-image hashes and upstream evidence hashes checked. Both actual regions have geometric support equal to the common finite support and exactly zero difference between mask rules. A full UED regression run is recorded in the update log.

CONTROLLING_BLOCKER: bragg_diffuse_and_branch_resolved_forward_map_missing.

NEXT_ACTION: Construct a source-backed forward model that separates elastic and inelastic contributions and establishes which branch combinations are identifiable. Do not label the near-Bragg scalar signal as a shear occupation merely because both source descriptions use E2g.

CLAIM_BOUNDARY: No population, heat, temperature, lifetime, alpha or Full Topic 13 closure. No holdout input. The exclusion applies to missingness in the archived arrays within this strip; it does not validate earlier source masking or symmetry averaging.

## Scientific interpretation

The paper describes a superposition of Bragg attenuation and a near-Gamma
diffuse increase. Therefore even a complete, clean strip is not a single-mode
population meter. Its source interpretation invokes strongly coupled optical
phonons; a shared E2g label is not a branch-identity certificate for the separate
low-frequency interlayer candidate.
[Primary paper, Results and Figure 3](https://arxiv.org/html/2410.06810v1).

The pinned author notebook's cell 6 applies Gaussian sigma=1 to stacked images.
The stored delay spacing is nonuniform: approximately 0.26664-6.666 ps in one
scan and 0.26664-0.6666 ps in the other. Historical library axis semantics must
be established before claiming that the published processing smooths time; if
it does, smoothing in frame index is not a constant-width physical-time response.
Our extraction does not execute that notebook or apply its Gaussian step.

There is no numerical mask error to repair in this particular region. Repeating
that check will not resolve the remaining physical mixture. Next research should
move to the forward scattering operator, not invent a stricter mask gate.

Evidence: `artifacts/t13_ued_region_support_audit.json` includes complete strip
curves, delays, source locators and hashes. Raw images remain local-only.
