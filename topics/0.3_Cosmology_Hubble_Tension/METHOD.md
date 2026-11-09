# Method

- Solver component: `Code/01_Engine/Engine_Cosmology.py`
- Comparison workflow: `Code/03_Research/Research_Hubble_Comparison.py`
- Supporting analysis: CMB, dark-energy, and high-z scripts under `Code/03_Research/`

Method boundary:

- The repository currently compares published H0 values and internal engine output.
- This is a topic-specific internal benchmark workflow, not a replacement for a full
  cosmology inference pipeline.
- Core-theory evidence in this topic must use a no-fitting rule: beta or any correction term
  must be derived from prior UET definitions or independently specified physical quantities,
  not tuned to the Planck-SH0ES gap.
- The Hubble-frame comparison uses the dimensionless coupling
  `beta_frame = sqrt(alpha_em)`, with `alpha_em` imported from the central constants module.
  This is separate from the generic Landauer-derived solver beta used by other engine terms.
- The physical interpretation being tested is frame/epoch dependence: Planck/CMB probes an
  early-universe/global frame, while SH0ES probes a late-universe/local distance-ladder frame.
- The source-lock manifest binds Planck 2018, SH0ES 2022, and the fine-structure constant
  record to the primary artifact hashes.

Derivation boundary:

- The implemented benchmark covers the z=0 Planck-to-SH0ES H0 comparison.
- The `sqrt(alpha_em)` bridge is treated as the topic's current theoretical coupling rule,
  not as a fitted parameter.
- A full cosmology proof would still need to derive the redshift transition function,
  validate against BAO/SN/CMB likelihoods, and show that the same coupling does not break
  standard constraints outside the H0 benchmark.

## Next hardening steps

1. Replace scalar H0-only validation with an uncertainty-aware likelihood or release-level
   data package.
2. Derive or externally constrain the `sqrt(alpha_em)` frame-coupling bridge.
3. Source-lock and test the redshift transition scale `z_crit = 5.0`.
4. Keep dark-energy/vacuum-energy results in a separate gate so H0 PASS does not mask that
   open problem.
