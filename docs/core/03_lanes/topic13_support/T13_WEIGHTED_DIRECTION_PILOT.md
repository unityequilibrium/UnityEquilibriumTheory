# Weighted direction transport pilot

MAJOR_RESULT_CLOSURE: PARTIAL; weighted direction plumbing implemented and evaluated through the full local heat-response path.
WHAT_IS_ACTUALLY_CLOSED: Nonuniform angular weights reach susceptibility, the conserved projector, collision and heat response. Six-axis remains the default. The new rule exposes the previously absent off-diagonal shear source while preserving five invariant columns.
WHAT_REMAINS_OPEN: Angular and transition convergence, weighted transition-interpolation correspondence, degree-six moments, material/protocol matching and physical transport.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: WARN_COARSE_ANGULAR_COMPARISON_NOT_CONVERGED.
WHAT_CHANGED: Private opt-in _direction_rule in the two existing research builders; appended state metadata; tests, pilot and unmerged registry addendum. No public product API, physical parameter, historical artifact or default grid replacement.
EQUATION_OR_MAPPING: w_state=w_radial*w_direction. Axis6 uses six weights1/6; axis_cube14 uses six weights1/15 and eight weights3/40. Existing operator injection passes the selected state to the heat builder without another API change.
VERIFICATION: Eighteen tests passed across weighted moments, original BS/collision and tensor lift. F0 PASS_WITH_DISCLOSED_GAPS,369 formula rows,0 duplicate IDs. Equation-foundation and compatibility audits pass as audits while both physical gates remain BLOCKED. The two pilot rows use the same natural action and fixed numerical controls. No target or holdout dataset is an input; this is not a repository-wide holdout access certification.
CONTROLLING_BLOCKER: angular_and_transition_convergence; new-rule isotropy5.26848e-8 exceeds unchanged1e-8 criterion.
NEXT_ACTION: Separate transition interpolation/channel dependence from angular quadrature using a locked study; inspect weighted transition mapping before interpreting its small projection residual as physical improvement. Then repeat at a resolved radial reference with additional angular rules.
CLAIM_BOUNDARY: Candidate quadrature implemented, not continuum or material validation. Full Topic13, graphite calibration and global UET closure remain unchanged. Old artifacts retain historical code hashes and are not silently regenerated.

## Matched coarse comparison

Both cases use T=.22,mu=.35,Phi=.15, the natural bridge action, radial8, collision24, angular integration24, cutoff48, transition24,64 channels and interpolation40.

| Quantity | Axis6 | Axis/cube14 |
| --- | ---: | ---: |
| State count |96|224|
| Natural kappa |254.8247192440|254.8247124264|
| Entropy balance residual |2.05e-12|9.09e-13|
| Covariance residual |1.11e-16|2.27e-13|
| Isotropy residual |4.45e-11|5.27e-8|
| Shear xy source norm |0|0.0165243|
| Mapped-row projection correction |0.296445|2.04623e-9|

Heat response differs by approximately2.68e-8 relative, but this is a coarse-grid comparison, not a transport error bound. A newly representable shear source is not yet a computed viscosity. The transition projection correction changes markedly; its interpretation depends on interpolation and weighting correspondence still to be audited. Isotropy remains a visible failed gate, not excused by small heat-response change.

Evidence: artifacts/t13_weighted_direction_pilot.json and its input hashes. Registry proposal: artifacts/t13_weighted_direction_registry_addendum.json, intentionally unmerged with no physical unlock.
