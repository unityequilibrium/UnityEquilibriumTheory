# Mass-Density Correspondence Update Log

## 2026-07-26 — Direct C-to-rho identifiability wave

- Tested the direct hypothesis `rho=f(C)` using identical two-body geometry and a common mass
  rescaling.
- The normalized geometry-only `C` remained exactly the same while the kernel-smoothed density
  amplitude doubled and the integrated mass changed from `2` to `4` code mass units.
- The density shape remained invariant, separating shape information from mass amplitude.
- Generated `mass_density_correspondence_verification.json` with structural audit status
  `PASS_WITH_BLOCKED_MAPPING` and mapping status `BLOCKED_DIRECT_C_ONLY`.
- Controlling blocker: a viable mass-density lane needs an independent matter-amplitude/source
  state and a dimensional observable map. No galaxy fit or mass claim is allowed yet.


### research-core / external 3D source-package boundary

- Area: `research-core`; workspace: C-density correspondence feeding Topic 0.1.
- Changed: registered Gaia EDR3/GCNS as a metadata-only 3D stellar-structure candidate, added source manifest, provenance audit, machine-readable gate, and regression tests.
- Verification: source-package audit `PASS_WITH_BLOCKED_EXTERNAL_SOURCE_PACKAGE`; focused tests `2/2`; no local raw numeric table, fit, or holdout consumed.
- Research finding: 3D source positions do not equal `rho_3D`; distance treatment, selection/completeness, mass realization, uncertainty propagation, and holdout are separate physical gates.
- Public-safety: `partial`; candidate source identity only, no C-to-mass derivation, galaxy validation, or dark-matter claim.
- Next controller: archive or extract a licensed source table and close selection, mass calibration, uncertainty, and holdout before external comparison.

### research-core / Gaia 3D query and holdout preregistration

- Changed: added a source-linked query manifest for `gaiadr3.gaia_source`, explicit parallax-bias and distance policies, and a HEALPix calibration/holdout split locked before data intake.
- Verification: query audit `PASS_WITH_BLOCKED_DATA_INTAKE`; source-package audit `PASS_WITH_BLOCKED_EXTERNAL_SOURCE_PACKAGE`; focused query/source tests `4/4`.
- Research finding: locking the query and holdout makes the next empirical step reproducible, but it does not turn source counts into `rho_3D`; distance, selection, mass realization, uncertainty, and dimensional `A_m` remain open.
- Public-safety: `partial`; no local numeric table, fit, calibration, or holdout row was consumed.
- Next controller: execute the locked query, archive/hash the returned table, then close schema, selection, distance, mass, uncertainty, and holdout gates.
