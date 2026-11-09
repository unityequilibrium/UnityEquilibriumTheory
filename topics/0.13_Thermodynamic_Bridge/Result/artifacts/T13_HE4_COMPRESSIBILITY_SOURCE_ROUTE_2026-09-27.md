# Topic 13: He-II isothermal-compressibility source route

MAJOR_RESULT_CLOSURE: `PARTIAL_SOURCE_ROUTE_NO_ACCEPTED_NUMERIC_ROW`. This is source screening, not a closed empirical result.

WHAT_IS_ACTUALLY_CLOSED: Three source roles are separated. The [Donnelly-Barenghi SVP compilation](https://srd.nist.gov/jpcrdreprint/1.556028.pdf) underlies the current density/superfluid anchor but its local UET package has no independent isothermal-compressibility row. [Brooks-Donnelly 1977](https://srd.nist.gov/jpcrdreprint/1.555549.pdf), section 4.2.b and table 4, computes compressibility by differentiating a P-V-T surface and compares it with older measurements; it is not a direct independent experiment. [Elwell-Meyer 1967](https://journals.aps.org/pr/abstract/10.1103/PhysRev.164.245) is a primary dielectric-volume pressure route at 1.25-4.2 K and 0.5-28 atm, but its abstract reports *isobaric changes* in compressibility, not the absolute 1.7 K saturated-vapour-pressure row needed here.

WHAT_REMAINS_OPEN: Permitted numeric primary tables, an independent absolute baseline, state/pressure transfer to SVP, units, row-level uncertainty and shared-data covariance. The physical `Phi` clamp/relaxation contract and Noether-to-atom correspondence remain separate theory blockers.

DEPENDENCY_UNLOCKED: Source-acquisition route only. No empirical-comparison, Core or Full Topic 13 unlock.

STATUS: `PARTIAL_SOURCE_ROUTE_NO_ACCEPTED_NUMERIC_ROW`; numeric response rows accepted: zero.

WHAT_CHANGED: Added a machine-readable source-route screen and a provenance test, separate from the five bounded pre-sprint results. No digitization, fit or source value was invented.

EQUATION_OR_MAPPING: The target is `kappa_T=-(1/V)(partial V/partial P)_T` at the same material state. A density-versus-temperature curve along SVP is not this pressure derivative, and an isentropic sound measurement needs a justified conversion. Even a valid ordinary `kappa_T` cannot be substituted for the model's clamped-`Phi` response without a physical `Phi` protocol.

VERIFICATION: The screening manifest records DOI/locator/source role and no numeric response row; the local density anchor, conditional response artifact and ontology contract are hash-linked. The provenance test checks their current hashes. The external articles were inspected online on 27 September 2026; their full raw PDFs are not redistributed or represented as locally hash-locked numeric datasets.

CONTROLLING_BLOCKER: `absolute_same_state_kappa_T_row_and_Phi_response_contract_missing`.

NEXT_ACTION: Obtain permitted Elwell-Meyer tables IV/V and a justified absolute baseline, audit any shared provenance with the current density anchor, and source-lock uncertainty/pressure transfer before accepting a row. In parallel derive or declare the physical `Phi` response protocol; absent that, retain a methods/measurement-design portfolio rather than an empirical comparison.

CLAIM_BOUNDARY: This source route does not demonstrate agreement or disagreement with He-II, nor does it calibrate `alpha_Phi_K`, validate TTG, access Xie 2026 or close Full Topic 13.

Evidence: [machine-readable source screen](../../Data/03_Research/he4_isothermal_compressibility_source_route.json), [conditional response design](T13_HE4_CONDITIONAL_COMPRESSIBILITY_DESIGN_2026-09-27.md).
