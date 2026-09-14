# Topic 13 interlayer-mode research progress (2026-09-08)

MAJOR_RESULT_CLOSURE: PARTIAL. The source-model calculation now runs reproducibly; the draft registry entry is not promoted.

WHAT_IS_ACTUALLY_CLOSED: Ten independent tests verify mass-centroid kinematics, rigid kinetic energy, rotation/permutation covariance, degenerate-pair gauge invariance and the projected spectral response identity. The MP48 source calculation selects the low pair by displacement shape, not by a target frequency.

WHAT_REMAINS_OPEN: Formal registry/source-package integration, independent review of the finite-q phase convention, material-state correspondence to Raman, strain-dependent force constants, model uncertainty and UET/Phi identification. No full physical result is closed by this progress record.

DEPENDENCY_UNLOCKED: None. This is continued diagnostic research, not an authorization for downstream physical claims.

STATUS: Eight generated numerical checks pass on the predeclared 13-point path. Overall result remains PARTIAL.

WHAT_CHANGED: Added independent tests and a runnable source-locked audit to the existing draft mass-metric module and derivation. Old phonon capacity data and whole-topic gates are not rewritten.

EQUATION_OR_MAPPING: mu=M_A*M_B/(M_A+M_B); Z_pair=B^dagger*P_pair*B/mu. The material relative-displacement reduced mass is 1.9944236595077444e-26 kg, not Phi normalization. The source-factor Gamma pair is 29.083635244 cm^-1. Its shear-projector eigenvalues are about 0.9999999612; the minimum across the short path is 0.9969846893, above the preregistered 0.98 criterion.

VERIFICATION: Ten focused pytest tests pass. Raw force-constant/structure hashes match the fixed locks. Independent Gamma assembly, eigenpairs, opposite-q frequencies and full-resolvent/spectral-sum agreement pass. No fitting, source resymmetrization, frequency clipping, cell rescaling or holdout read is performed. F0 reports 369 rows without duplicates; foundation and compatibility remain BLOCKED. The new draft is not yet a fully integrated F0-F8 equation result.

CONTROLLING_BLOCKER: material_mode_correspondence_and_independent_strain_missing. Raman source previously reports 44 +/- 1 cm^-1, unlike the MP48 harmonic pair. This comparison is contextual here, not a source-joined uncertainty test; do not infer statistical significance without model/state uncertainties.

NEXT_ACTION: Join the Raman and MP48 source records explicitly, review phase conventions independently, and diagnose the source-state frequency discrepancy before using a strained-mode response for UET matching. A derivative along momentum is not a derivative with respect to strain.

CLAIM_BOUNDARY: Material harmonic diagnostic only. No independent alpha_Phi_K, heat-flux coefficient, KMS closure, finite-cone proof, full Topic 13 unlock or global claim promotion. The separate O(2)/He-4 status is unchanged and not revalidated.

Evidence: `artifacts/t13_mp48_interlayer_mode_residue_audit.json` records the consumed source and implementation hashes. Reproduce using `python -B -m docs.scripts.audit.audit_topic13_mp48_interlayer_mode_residue` from the repository root with the permitted local MP48 sources and Phonopy installed.
