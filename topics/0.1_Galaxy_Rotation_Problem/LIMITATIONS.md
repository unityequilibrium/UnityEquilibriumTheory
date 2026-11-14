# Limitations

- The checked-in verifier input is a summary-row working copy, not a full upstream
  SPARC radial-curve archive.
- The current benchmark uses one recorded radius and one recorded observed
  velocity per processed galaxy row, so it cannot by itself establish whole-curve
  agreement.
- The engine contains heuristic bridge terms and hidden scaling anchors that still
  need explicit derivation, dependency mapping, and sensitivity analysis.
- The meaning of `R_disk_kpc` in the working copy needs tighter source-locking so
  the enclosed-mass relation is not applied against an ambiguous radius
  convention.
- Internal pass rates do not establish out-of-sample performance, nor do they
  replace comparator baseline evaluation against MOND or dark-matter models.
- The artifact-level `WARN` means the verifier ran; it does not mean the model passed. The current `galaxy_model_gate` must keep dark-matter replacement and galaxy-closure claims blocked while the summary-row residual gate fails.
- The artifact-level `galaxy_claim_scope_gate` is the export controller for integration topics; it must remain blocking while full-curve SPARC source-lock, competitor baselines, uncertainty handling, and out-of-sample checks are open.
- No fresh external replication package is documented in this hardening pass.

## History-dependent trace lane

The history-dependent comparison is a separate candidate lane, not a
replacement for the current rotation verifier. It requires full radial
curves, pointwise uncertainty, a galaxy-history or controlled proxy, named
competitor baselines, locked parameters, and holdout evaluation.

The current readiness artifact is
docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_history_comparison.json
and remains BLOCKED. Dark-matter replacement wording remains blocked.

## Current Claim Boundary

| Claim area | Allowed wording now | Blocker to stronger wording |
| :-- | :-- | :-- |
| Run contract | internal summary-row verifier ran | does not imply model acceptance |
| Summary-row model | residual blocker over repository working copy | average error must pass threshold and pass rate must be nonzero under a declared metric |
| SPARC replication | not supported | source-locked full curve arrays, row semantics, and preprocessing manifest |
| Dark-matter replacement | not supported | comparator baselines, lensing/rotation evidence, uncertainty, and out-of-sample tests |
