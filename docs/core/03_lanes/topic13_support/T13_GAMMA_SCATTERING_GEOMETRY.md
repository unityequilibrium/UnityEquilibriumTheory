# Gamma geometry cannot separate the two E2g populations here

MAJOR_RESULT_CLOSURE: PARTIAL; numerically rank-one two-pair geometry found for the six declared basal vectors.

WHAT_IS_ACTUALLY_CLOSED: The two Gamma pair columns are proportional to numerical precision in this source model. Increasing the number of these equivalent Gamma measurements does not independently identify the two populations.

WHAT_REMAINS_OPEN: Finite-q polarization/gauge, response rank with other branches, atomic factors, Debye-Waller response, elastic contamination, detector resolution/covariance and independent Phi coupling.

DEPENDENCY_UNLOCKED: Finite-q experimental-information design only; no physical gate.

STATUS: GEOMETRY_ONLY_INVERSION_OPEN; full_core_unlock=false.

WHAT_CHANGED: Imported geometric one-phonon comparator, registry addendum, three tests and source artifact. No original source equation or force constants changed.

EQUATION_OR_MAPPING: S_pair(Q)=sum_j |sum_s exp(i Q.r_s) Q.e_sj/sqrt(m_s)|^2. Explicit atomic phases are used with Gamma atom-basis eigenvectors. Common carbon atomic scattering and equal site Debye-Waller factors are omitted, not calibrated. Pair summation corresponds to equal occupation within each degenerate pair if used for an intensity map.

VERIFICATION: Three tests check atomic destructive interference, origin/pair-basis invariance and invisible out-of-plane polarization. Actual source and upstream hashes checked. Column-normalized singular values are 1.4142135624 and 2.2548736e-16. No row or mode was clipped. F0 inventory reports 369 formula rows and no duplicate IDs before this addition; aggregate foundation remains separately controlled.

CONTROLLING_BLOCKER: finite_q_response_and_independent_information_required_for_two_pair_inversion.

NEXT_ACTION: Extend the operator to finite reduced wavevectors with a verified eigenvector phase convention, then evaluate multi-branch rank under actual detector coverage. Include elastic and uncertainty terms before attempting population inversion. A prior may select a solution but must not be described as identification by these data.

CLAIM_BOUNDARY: Conditional source-model diagnostic at six basal Gamma vectors, not a continuum no-go or a statement that UED cannot resolve modes anywhere. No physical alpha, TTG validation, holdout input or full-topic promotion.

## What this means

For (100), the two geometry weights are 0.54297562 and 0.54340356 in
angstrom^-2 per atomic mass unit. Other nonzero sampled rows scale both columns
together; (110) and (300) are near numerical extinction. Dividing each column by
its own Gamma frequency, as in a population-response coefficient, changes scale
but cannot restore rank. Common nonzero row factors also cannot restore rank.
Real site-dependent factors or finite-q physics must be evaluated, not assumed.

This gives a concrete reason not to fit two populations to the existing scalar
near-Bragg strip: even the idealized two-channel Gamma limit lacks independent
information. The full strip is not this ideal limit and mixes finite-q and Bragg
response, so its actual rank remains unmeasured.

The imported structure-factor framework distinguishes total, elastic and
one-phonon intensity and weights occupations by mode frequency and scattering
amplitude. [Primary source, equations 1-3](https://arxiv.org/pdf/1908.02795).
Our geometric comparator is only part of that framework, not its full inversion.

Evidence: `artifacts/t13_gamma_scattering_geometry_audit.json`. The upstream
near-zero frequency-grouping uncertainty is retained, not repaired by this test.
