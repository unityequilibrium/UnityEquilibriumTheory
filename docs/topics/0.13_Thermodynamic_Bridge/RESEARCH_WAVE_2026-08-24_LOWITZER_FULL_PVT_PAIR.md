# Topic 13 Research Wave: Lowitzer Full P-V-T Pair

## Closure Record

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_LOWITZER_GRAPHITE_ALPHA_V_K_T_FULL_SOURCE_PAIR`.
WHAT_IS_ACTUALLY_CLOSED: A byte-preserved full-text source package now contains numeric, source-reported `alpha_V` and `K_T` rows from the same Lowitzer study, sample, and 300 K state. The package also records the source material, locators, units, uncertainty fields, raw-file hash, and a reproducible `c_p^V-c_v^V` correction-term witness.
WHAT_REMAINS_OPEN: The Lowitzer sample is synthetic graphite with grains below 20 micrometers and is not established as Ding's natural-graphite TTG material. The package does not provide Ding mode-resolved `C_src`, source-grade `c_v`, a base-`Phi` SI anchor, `alpha_Phi_K`, beta/SI correspondence, or physical transport/KMS/entropy closure.
DEPENDENCY_UNLOCKED: Only the source-state thermodynamic correction-input lane. No Ding source acceptance, dimensional calibration, Full Topic 13, Core, Gravity, constitutive-transport, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_SOURCE_LOCKED_LOWITZER_ALPHA_V_K_T_PAIR`; canonical Full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; `claim_promotion=false`.
WHAT_CHANGED: Added the archived full-text source package, a hash and uncertainty verifier, matched-source projection, closure-contract evidence, registry/dependency synchronization, and regression coverage. The old abstract-only Lowitzer candidate remains unchanged as historical screening evidence.
EQUATION_OR_MAPPING: `c_p^V-c_v^V=T*alpha_V^2*K_T`; for the HTV9 300 K row, the recorded correction witness is `11,673.6 J m^-3 K^-1` with first-order alpha/K uncertainty `1,583.27 J m^-3 K^-1`. This is a correction term, not a `c_v` value and not a `C_src` row.
VERIFICATION: `audit_topic13_lowitzer_full_source_pair.py` returned `PASS_SCOPED_SOURCE_LOCKED_LOWITZER_ALPHA_V_K_T_PAIR`; matched-source audit returned `PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_SOURCE_PAIR_LOCKED_MATERIAL_OPEN`; closure matrix reports 10 major results, 36 subresults, 192 closed lanes, 16 scoped no-go lanes, 7 open blocker groups, `full_core_unlock=false`, and `holdout_accessed=false`. Focused regression: 10 passed.
CONTROLLING_BLOCKER: `material_regime_mapping_to_TTG_not_closed` for this source route; the topic-level controller remains `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`, with Ding `C_src` and physical Kubo evidence also open.
NEXT_ACTION: Obtain a permitted Ding-compatible numeric `C_src` or accepted same-regime PBTE reproduction, a source-grade `c_v`/volume uncertainty package, and an independent paired base-`Phi`/SI record. Keep Lowitzer as a comparator and do not use it to calibrate `alpha_Phi_K`.
CLAIM_BOUNDARY: This wave closes one source-grade thermodynamic correction-input lane only. It is not a Ding-material equivalence, `C_src`, `alpha_Phi_K`, TTG prediction, physical transport result, external validation, or Full Topic 13 closure.

## Locked Source Rows

| Row | Model | T (K) | alpha_V (K^-1) | K_T (GPa) | Source locator |
|---|---|---:|---:|---:|---|
| `lowitzer_table_iv_htv9_300K` | HTV9 | 300 | `3.2e-5 +/- 0.2e-5` | `38 +/- 2` | PDF p. 6, Table IV |
| `lowitzer_table_iv_htbm9_300K` | HTBM9 | 300 | `3.2e-5 +/- 0.2e-5` | `39 +/- 1` | PDF p. 6, Table IV |
| `lowitzer_table_iv_htv14_300K` | HTV14 | 300 | `3.1e-5 +/- 0.3e-5` | `30 +/- 1` | PDF p. 6, Table IV |
| `lowitzer_table_iv_htbmag14_300K` | HTBMAG14 | 300 | `3.1e-5 +/- 0.3e-5` | `32 +/- 1` | PDF p. 6, Table IV |

Source material and scope are recorded at PDF pp. 1-2: synthetic graphite from Aldrich, grains below 20 micrometers, and approximately 20 percent disoriented layers. The source identity is therefore not silently substituted for Ding's natural graphite TTG specimen, whose grain-size and morphology contract remains separate.

## Evidence Paths

- Source package: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/lowitzer_2006_graphite_pvt_full_source_package.json`
- Local raw payload: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/lowitzer_2006_graphite_pvt.pdf` (local-only raw input; SHA-256 `401831675de0fa4ae36405f469553dcc39b12ae29cfc1799023aef8ecc658a2a`)
- Source-pair audit: `docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json`
- Matched-source boundary: `docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json`
- Canonical full gate: `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`
- Closure matrix: `docs/core/artifacts/t13_topic13_closure_matrix.json`

The raw PDF is intentionally covered by the repository local-only raw-data rule. Its path, byte count, hash, locator, and preprocessing boundary are retained in the source package and audit artifact.
