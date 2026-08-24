# Topic 13 Public Phonon Route Screening

## MAJOR_RESULT_CLOSURE

`CLOSED_FOR_LANE` for `T13_PUBLIC_PHONON_ROUTE_SCREENING`. The canonical Full
Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

## WHAT_IS_ACTUALLY_CLOSED

Three public routes were screened and bounded without importing remote payloads:
Materials Project Phonon database v1.1, the LCBOPII graphitic phonon route, and
the Dryad full-scattering-matrix BTE solver. They are now machine-readable as
metadata, formula, or solver context only.

## WHAT_REMAINS_OPEN

No route supplied an accepted `C_src(T)` row package, Ding-equivalent material
state, source-grade uncertainty, independent base-Phi/SI response, or physical
UET transport coefficient. The ten Core-level Topic 13 subresults therefore
remain unchanged.

## DEPENDENCY_UNLOCKED

None. This wave narrows public-source acquisition only. It does not unlock Core
curved 3+1, Gravity/GR, full constitutive transport, or Full Topic 13.

## STATUS:

`PASS_SCOPED_PUBLIC_PHONON_ROUTE_SCREENING_NO_CORE_PAYLOAD`

## WHAT_CHANGED:

Added a source package and audit for three public routes. Materials Project is
recorded as a broad metadata-only route; LCBOPII as formula/dispersion context;
and the Dryad solver as full-scattering method context for silicon. The input
audit, closure matrix, major-result register, and dependency projection were
regenerated without changing the seven canonical blockers.

## EQUATION_OR_MAPPING:

```text
C_src(T) = sum_mu c_mu(T)
Delta_Tq = Delta_u_ph / C_src(T)
y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
```

No mapping from a public phonon record to `Phi` was asserted.

## VERIFICATION:

The route audit records source identity, route class, payload availability,
material/state boundary, and non-import status. No numeric `C_src`, `alpha_Phi_K`,
target fit, threshold change, or holdout access occurred. The canonical input
audit remains passing in its open state with zero Core-accepted packages.

## CONTROLLING_BLOCKER:

`ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, with
material/state and source-grade `c_v` uncertainty still open. Independent
`alpha_Phi_K` and physical Kubo evidence remain separate blockers.

## NEXT_ACTION:

Use the bounded route list to send the combined author/request package. If a
payload arrives, validate it through the existing fail-closed contract before
any row enters the canonical matrix. Do not treat a broad archive, a formula
paper, or a silicon solver as a Ding source.

## CLAIM_BOUNDARY:

This is a public-source screening result only. It is not numeric `C_src`, an
independent `alpha_Phi_K` calibration, physical transport validation, external
validation, prediction, or Full Topic 13 closure. `C`, `Phi`, `R_gen`, and
`R_obs` retain their declared meanings.

## SOURCE LOCATORS

- Materials Project Phonon database v1.1: https://zenodo.org/records/20196565
- LCBOPII graphitic phonon route: https://arxiv.org/abs/1010.5594
- Full-scattering-matrix BTE solver: https://datadryad.org/dataset/doi%3A10.5061/dryad.dr7sqvbdq

## EVIDENCE

- `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_public_phonon_route_screening_package.json`
- `docs/core/artifacts/t13_public_phonon_route_screening_audit.json`
- `docs/core/artifacts/t13_closure_input_package_audit.json`
- `docs/core/artifacts/t13_topic13_closure_matrix.json`
