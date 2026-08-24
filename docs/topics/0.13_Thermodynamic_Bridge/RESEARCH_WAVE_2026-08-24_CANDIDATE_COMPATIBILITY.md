# Topic 13 Candidate Compatibility Wave

## Major Result Closure

`PARTIAL`; the canonical Full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

## What Is Actually Closed

- Five existing source packages are compared field-by-field with the three non-derivable Core input contracts.
- Ten candidate route records are machine-readable: four thermal-source routes, five base-Phi inventory routes, and one transport route.
- Candidate rows, standard-physics comparators, UET mappings, and missing acceptance fields are kept separate.
- No candidate route is accepted for Core, and no new Core subresult is closed.

## What Remains Open

The current canonical matrix has 10 major result areas and 36 required subresults:

- `CLOSED_FOR_LANE`: 21 subresults.
- `CLOSED_AS_NO_GO`: 5 subresults.
- `CLOSED_FOR_CORE`: 0 subresults.
- `OPEN`: 10 subresults.

Full Topic 13 requires the open Core-level subresults below to be accepted, while preserving `claim_promotion=false` and the locked Xie 2026 holdout.

| Open subresult | Evidence required to close for Core | Current controller |
| --- | --- | --- |
| `base_phi_si_anchor` | Dimensionful action/free-energy origin or paired base-Phi/SI response with `e0`, units, state, uncertainty, and hash | `dimensional_phi_to_thermal_observable_map_missing` |
| `independent_alpha_record` | Independent `Delta_Phi` plus `Delta_Tq` or `Delta_u_ph` record; `alpha_Phi_K` in `K per normalized Phi`, uncertainty, provenance, and clean holdout path | `alpha_Phi_K_independent_calibration_missing` |
| `normalized_beta_si_map` | Non-Landauer beta derivation plus SI scale correspondence, limiting cases, units, and uncertainty | `normalized_beta_and_SI_scale_correspondence_missing` |
| `physical_source_backed_eos` | State-matched physical `C_src`, Phi scale, charge-density EOS, stability/reciprocity, and uncertainty propagation | `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` |
| `physical_uet_kubo_record` | UET physical Kubo coefficient with SI units, state, correlator/source hash, evidence status, and uncertainty | `physical_Kubo_coefficient_record_missing` |
| `physical_sk_transport_match` | Same-state finite-temperature normal/condensed response, SK/KMS/FDT residuals, and microscopic or source match | `physical_Kubo_coefficient_record_missing` |
| `physical_entropy_production_mapping` | Entropy current, positivity/Onsager condition, dissipative balance, and source-linked uncertainty | `physical_Kubo_coefficient_record_missing` |
| `accepted_numeric_csrc` | Mode-resolved or accepted independent `C_src(T)` rows, material/TTG state, convergence, locator, preprocessing, row identity, hash, and source-grade uncertainty | `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` |
| `material_and_uncertainty_closure` | Ding-regime material mapping plus same-grade `c_v`/volume or `alpha_V`/`K_T` correction and propagated uncertainty | `material_regime_mapping_to_TTG_not_closed`; `c_v_source_uncertainty_not_closed` |
| `physical_heat_flux_entropy_map` | One-state SI map from `C_src` and `Delta_Phi` to heat flux and entropy production, including coefficient and uncertainty chain | `physical_Kubo_coefficient_record_missing`; `dimensional_phi_to_thermal_observable_map_missing` |

## Required Input Packages

Full Topic 13 cannot be closed by rerunning the existing comparators alone. Three grouped packages must pass the fail-closed contract:

1. `T13_INPUT_DING_TTG_SOURCE`: row-complete numeric `C_src(T)` or accepted same-regime reproduction, material/response state, convergence, provenance, and source-grade uncertainty.
2. `T13_INPUT_BASE_PHI_SI_ALPHA_BETA`: independent base-Phi/SI anchor or dimensionful derivation, independent alpha record, and beta derivation not inferred from Landauer.
3. `T13_INPUT_PHYSICAL_TRANSPORT_MATCH`: state-matched physical Kubo coefficient, SK/KMS/FDT match, normal-component completion, entropy/heat-flux propagation, and uncertainty.

## Candidate Route Boundary

| Candidate | Maximum admissible contribution now | Why it does not close Core |
| --- | --- | --- |
| Calorine/Zenodo NEP PBTE | Numeric candidate `C_src` and mesh-convergence lane | C-CX/NEP state is not Ding-equivalent; source-grade uncertainty and accepted mode payload are open |
| Materials Project MP48 | Independent harmonic graphite `c_v` comparator | No Ding PBTE/TTG response, no UET `e0`, and no source-grade statistical uncertainty |
| Materials Cloud QH-15 | Source-locked macroscopic volumetric `SpecificC` comparator | No mode-resolved `C_src`, Ding-state equivalence, or source-grade uncertainty |
| Georgia Tech Gen3 CSP | One independent `c_p` row with 95% interval | `c_p` to volumetric `c_v` and density uncertainty are not closed |
| Kim 2018 Green-Kubo | Standard-physics directional conductivity comparator | No UET Phi state, base-Phi anchor, retarded SK/KMS match, or entropy map |

## Status

`PASS_SCOPED_T13_CANDIDATE_COMPATIBILITY_AUDIT_OPEN`; the compatibility artifact reports five source packages and ten route records, with zero Core-accepted routes.

## What Changed

Added `docs/core/artifacts/t13_candidate_core_compatibility_audit.json`, its deterministic generator and regression, and linked the artifact into the three-package input audit. The register projection was repaired to preserve the matrix counts `10` and `36`.

## Equation Or Mapping

`y_TTG = Delta_Tq(t) / Delta_Tq(0)`; `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)`; `Delta_Tq = alpha_Phi_K * Delta_Phi`; `C_src(T) = sum_mu c_mu(T)`; physical transport is admitted only after a state-matched Kubo/SK/KMS/entropy record.

## Verification

The input audit reports three packages inspected and zero accepted for Core. The matrix reports `21/5/0/10` across `CLOSED_FOR_LANE/CLOSED_AS_NO_GO/CLOSED_FOR_CORE/OPEN`, totaling 36. Focused regression: `11 passed`. Xie 2026 remains unread and no target or holdout fit was performed.

## Controlling Blocker

No admissible Core input package has arrived. Existing comparator routes are exhausted for this closure contract unless a new source payload or declared derivation is supplied.

## Next Action

Obtain one authorized Ding-compatible `C_src` package, one independent base-Phi/SI alpha-beta package, and one state-matched physical Kubo/SK/KMS/entropy package. Validate each through the existing fail-closed contract before changing any closure level.

## Claim Boundary

This is a compatibility and evidence-acquisition result only. It is not Full Topic 13 closure, external validation, prediction, physical UET transport proof, Core curved 3+1 readiness, Gravity unlock, or global UET closure.

## Evidence Paths

- `docs/core/artifacts/t13_candidate_core_compatibility_audit.json`
- `docs/core/artifacts/t13_closure_input_package_audit.json`
- `docs/core/artifacts/t13_topic13_closure_matrix.json`
- `docs/core/artifacts/uet_major_result_closure_register.json`
- `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`
