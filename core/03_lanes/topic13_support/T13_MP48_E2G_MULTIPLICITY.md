# Same irrep does not identify a phonon branch

MAJOR_RESULT_CLOSURE: PARTIAL; distinct E2g eigenspaces demonstrated, full-spectrum grouping stability unresolved.

WHAT_IS_ACTUALLY_CLOSED: Within the locked MP48 harmonic source, two separated Gamma doublets match E2g characters under all 24 crystal operations. Their rigid-shear content is radically different. Symmetry name alone is insufficient for joining source lanes.

WHAT_REMAINS_OPEN: Near-zero grouping stability, experimental branch-resolved scattering weights, physical source correspondence and independent Phi response.

DEPENDENCY_UNLOCKED: Branch-aware research design only; no physical dependency.

STATUS: UNRESOLVED aggregate because grouping_stable=false. The two individual E2g character tests pass at the declared tolerance.

WHAT_CHANGED: Added all-eigenspace diagnostic, grouping sweep and three tests. Source force constants and signed near-zero frequencies remain unchanged.

EQUATION_OR_MAPPING: Existing Gamma atom-permutation/rotation representation applied separately to each frequency eigenspace; existing rigid-layer shear basis projected onto each eigenspace. No new UET equation.

VERIFICATION: Three focused tests pass. Source hashes verified. The actual audit writes its partial artifact then exits nonzero because global grouping changes over 1e-7, 1e-6 and 1e-5 THz. Only the three near-zero indices regroup; both E2g pairs stay separate throughout. No threshold was adjusted to force success.

CONTROLLING_BLOCKER: physical_branch_resolved_scattering_map_missing; global grouping sensitivity remains a separate numerical diagnostic issue.

NEXT_ACTION: Use distinct branch indices, frequencies and polarization vectors when building the scattering model. Compare which reciprocal-space observations distinguish these branches; do not import fitted source temperatures or EELS weights as independent Phi calibration.

CLAIM_BOUNDARY: Gamma harmonic source results, not measured UED branch populations, temperature, full O(2) identification or Full Topic 13 closure. No holdout input or physical unlock.

| Source indices | Frequency (cm^-1) | Mean rigid-shear projection weight |
| --- | ---: | ---: |
| 3, 4 | 29.08363524 | 0.9999999612 |
| 8, 9 | 1585.29682626 | 0.00000003879 |

Character errors are below 4e-15 for both pairs; subspace leakage is approximately
1.96e-12 and 2.95e-13. These are numerical representation checks, not uncertainty
on measured material frequencies. The existing low-frequency Raman mismatch is
not repaired by identifying the high-frequency pair.

The experimental paper's optical-phonon/EELS model uses fitted component weights
and fitted temperatures. Its UED and EELS fluences are also different; they cannot
be silently treated as the same preparation. The paper states that its EELS energy
resolution does not resolve phonon losses directly. Therefore its EELS analysis is
not a ready-made absolute population measurement or independent alpha source.
[Primary paper, Results and Figure 4](https://arxiv.org/html/2410.06810v1).

The MP48 high-frequency pair is a candidate for studying the optical channel, not
a demonstrated match to this experiment. The low-frequency interlayer lane remains
separate; both can contribute to a future multi-branch energy model if their own
observable maps and material correspondence are established.

Evidence: `artifacts/t13_mp48_e2g_multiplicity_audit.json` includes all signed
frequencies, grouping sweep, character errors and source hashes.
