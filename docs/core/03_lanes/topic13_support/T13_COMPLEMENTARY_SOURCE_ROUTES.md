# Complementary measurements: feasibility versus data readiness

MAJOR_RESULT_CLOSURE: PARTIAL; relevant experimental capabilities exist, but no matched numeric calibration package was acquired.

WHAT_IS_ACTUALLY_CLOSED: Literature supports out-of-plane graphite diffraction and an alternative late-equilibrium thermometry route. These are concrete acquisition targets, not substitutes for missing data.

WHAT_REMAINS_OPEN: Numeric rows, provenance/permission, matched preparation, forward response, covariance, timing consistency and independent Phi coupling.

DEPENDENCY_UNLOCKED: Targeted source acquisition or collaboration planning only.

STATUS: FULL_TEXT_REVIEWED_NUMERIC_PACKAGE_OPEN.

WHAT_CHANGED: Added a source-route record with explicit literature-only roles and unacquired numeric/source-hash fields. No new equation, experiment, fit or calibration.

EQUATION_OR_MAPPING: Detector channels must retain their own response models. Reflection Bragg intensity and CBED strain are not interchangeable with diffuse one-phonon matrix rows.

VERIFICATION: Read primary full text at the locators recorded in the JSON. One PMC page was inaccessible; the author's arXiv PDF supplied the second source. Review is not a numeric-source/hash audit. No figures digitized or raw rows invented.

CONTROLLING_BLOCKER: matched_numeric_energy_sensitive_observable_and_response_contract.

NEXT_ACTION: Seek same-preparation equilibrium calibration and orientation-resolved numeric records, including covariance. If unavailable, keep this route open and work on the independent Phi-source mapping rather than claiming a calibrated temperature.

CLAIM_BOUNDARY: Capability evidence only; neither cited paper establishes the proposed 124-vector design, nor supplies independent alpha for this UET lane. No full-topic promotion or holdout use.

## Two useful routes

[Pennacchio et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5491388/) demonstrate
reflection diffraction from graphite with out-of-plane peaks. This establishes
access to the direction, not access to every diffuse observation in our design.
Reflection changes the interaction geometry and needs its own response model.

[Feist et al.](https://arxiv.org/pdf/1709.02805) separate deformation-related
line shifts from intensity changes and infer temperature under a late-time
quasi-equilibrium assumption. That suggests an alternative to resolving every
mode, but not an early-time thermometer. SI 5 contains a ps/fs timing discrepancy
relative to the setup; reconcile it before importing time constants.

## Why no cross-paper merge

An observation is complementary only if it constrains the same unknown state.
Different samples, pump conditions, delays or spatial regions generally introduce
new unknowns instead. Shared material names do not establish that join. Likewise,
using an assumed equilibrium distribution to infer temperature does not independently
verify that distribution. A useful source package must make those assumptions testable.

The constructive geometry result remains valid within its declared model; this
review narrows its experimental interpretation rather than upgrading it.
Machine-readable route record: `artifacts/t13_complementary_source_routes.json`.
