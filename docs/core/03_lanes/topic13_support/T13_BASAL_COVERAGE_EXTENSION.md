# Generic wavevectors reopen the basal measurement route

MAJOR_RESULT_CLOSURE: PARTIAL; constructive same-plane target-observability route found.
WHAT_IS_ACTUALLY_CLOSED: Four tested generic reduced wavevectors identify the local second-moment target in the existing24-row basal geometry, despite unresolved out-of-plane populations. The earlier two symmetry-line controls remain ambiguous even after expanding coverage.
WHAT_REMAINS_OPEN: Actual image coverage/masks, conditioning/noise, complete spatial and BZ support, material response calibration and UET operator normalization.
DEPENDENCY_UNLOCKED: None; no physical gate. Existing-image region selection can now be investigated before requesting tilted measurements.
STATUS: GENERIC_Q_IDEAL_TARGET_IDENTIFIABLE_NOT_CALIBRATED.
WHAT_CHANGED: Six-q/two-coverage source-model audit, literature-scope reconciliation and this correction to the next measurement action. Earlier numerical witnesses remain valid at their original q points.
EQUATION_OR_MAPPING: Existing A=S/f and local c=projected relative-layer mode weight/f. Target membership in row(A), not full population recovery, controls the result.
VERIFICATION: Six existing target/geometry tests PASS; all12 cases computed, tolerances1e-9 to1e-11 recorded. Generic-q target null fractions are below1.27e-15 for24 rows. Foundation audit PASS/foundation BLOCKED.
CONTROLLING_BLOCKER: usable_generic_q_detector_regions_and_physical_response_covariance.
NEXT_ACTION: Inspect actual image masks and reciprocal calibration for generic-q regions across enough independent Brillouin zones. Compute detector-weighted target uncertainty before numerical inversion. Do not assume a new tilt experiment is necessary.
CLAIM_BOUNDARY: Ideal source-model identifiability, not measured precision, whole-zone inversion, alpha or Full Topic13 closure. No new numeric experimental dataset acquired.

## Decisive comparison

| Reduced q | Basal24 rank | Local target identifiable numerically |
| --- | --- | --- |
| (.1,0,0) | 6 | No |
| (.1,.1,0) | 5 | No |
| (.07,.113,0) | 8 | Yes |
| (.173,.097,0) | 8 | Yes |
| (.23,.19,0) | 8 | Yes |
| (.3,.12,0) | 8 | Yes |

Expanding to all source basal reciprocal vectors with magnitude at most12 inverse angstrom gives60 rows and the same conclusions at these points. It does not repair the symmetry-line controls. Changing q, rather than merely increasing row count, is decisive in this tested set. It does not follow that every generic point is well-conditioned or identifiable.

No equal-population constraint or discarded mode was needed for the target test. Rank8 is less than12, yet the local target is orthogonal to the remaining null space at these generic points. This is precisely why full-state recovery is an unnecessarily strong demand for a scalar observable. Each q remains a separate unknown population vector; no cross-q population equality was imposed.

## Literature reconciliation and data status

[Rene de Cotret et al., Section III.D](https://arxiv.org/pdf/1908.02795) use44 measured zones and eight in-plane branches, with inversion outside a stated near-Bragg region and a nonnegative population-change constraint. Their paper is not a matched dataset or reproduction of this MP48 calculation. Here the same radius gives60 ideal vectors, not44 experimentally acquired zones. The literature motivates inspecting generic-q coverage; it does not supply our missing detector covariance or UET calibration.

The targeted search returned the already-known Barantani dataset and other capability papers; no matched multi-orientation numeric package was acquired. The useful new outcome is that extra orientation is not yet necessary for the present ideal local target. Actual detector regions might offer a less costly route, but this requires mask, geometry and response checks.

## Correction to earlier interpretation

The previous local-variance audit covered only two high-symmetry paths. Its positive ambiguity witnesses are not contradicted. Any wording suggesting that all basal measurements necessarily fail, or that adding reciprocal planes is required, is too broad. Complementary planes remain one sufficient ideal design, not the only route. Generic-q identifiability also does not cure unmeasured modes elsewhere in the Brillouin zone or establish a physical chi mapping.

Evidence: `artifacts/t13_basal_coverage_extension.json`, with q magnitudes, exact grids, witnesses, tolerance sweeps and source/code hashes.
