# Topic 13 Research Wave: Named Energy-Response Branch

## MAJOR_RESULT_CLOSURE:
`T13_PHI_E_TTG_BRIDGE_CONDITIONAL` is `CLOSED_FOR_LANE` only.

## WHAT_IS_ACTUALLY_CLOSED:
- The named branch defines `Phi_E := Delta_u / e0`.
- The standard energy-response mapping is recorded as `Delta_Tq = Delta_u / c_v = (e0/c_v) Phi_E`.
- `alpha_Phi_E_K = e0/c_v` and first-order independent-input uncertainty propagation are implemented and tested.
- The ontology boundary is explicit: `Phi_E` is not silently identified with base `Phi`; `c_v` is distinct from UET `C`; no new physical `R_gen` state is introduced.
- NIST SRD 69 and SCD30 graphite heat-capacity candidates are source-identified with locators and row identity, but are not consumed for calibration.

## WHAT_REMAINS_OPEN:
- The source package provides molar `Cp` and mass-specific heat candidates, not source-locked volumetric `c_v` in `J m^-3 K^-1`.
- `Cp -> c_v` and mass/molar-to-volumetric conversion, including uncertainty, are not closed.
- The NIST `+/-0.4%` value is an evaluated enthalpy deviation bound, not a stated measurement uncertainty for `c_v`.
- The dimensional energy scale `e0` is not source-locked or derived from a declared UET action.
- The mapping from base `Phi` to named `Phi_E` is not derived or independently calibrated.
- Therefore no numeric `alpha_Phi_K` or `alpha_Phi_E_K` calibration is emitted.
- Full Topic 13 EOS, transport, SK/KMS, entropy-current, and dissipative-balance closures remain open.

## DEPENDENCY_UNLOCKED:
Only the named energy-response formula/unit lane is unlocked. Full Topic 13 remains `PARTIAL`; Core curved 3+1, Gravity/GR, full constitutive transport, and Galaxy tracks remain blocked by dependency gates.

## STATUS:
`PASS_NAMED_BRANCH_OPEN_INPUTS`; Full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `claim_promotion=false`.

## WHAT_CHANGED:
- Added `docs/core/thermal_energy_response_bridge.py`.
- Added the source package `Data/03_Research/graphite_heat_capacity_source_package.json`.
- Added the audit artifact `docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json`.
- Attached the result to the Topic 13 gate and major-result register.

## EQUATION_OR_MAPPING:
```text
Phi_E = Delta_u / e0
Delta_Tq = Delta_u / c_v
Delta_Tq = (e0 / c_v) Phi_E
alpha_Phi_E_K = e0 / c_v
sigma_alpha/alpha = sqrt((sigma_e0/e0)^2 + (sigma_cv/c_v)^2)
```

## VERIFICATION:
- Named branch audit: `PASS_NAMED_BRANCH_OPEN_INPUTS`.
- Focused regression: `29 passed`.
- Wave 1 integrity: `PASS_WITH_BLOCKED_LANES`.
- Audit SHA-256: `1f4f8308b884c47a15918aa359adbe811336a1fd03dbe9986b900d84eca8060a`.
- Source package SHA-256: `9e968cdc534e2259cec91908cfa4162cd5d3bc491bcb4de6abb7ec0b4ffd1f9e`.
- Xie 2026 holdout was not accessed or consumed; no threshold, clipping, padding, or target fitting was used.

## CONTROLLING_BLOCKER:
`c_v_e0_and_base_Phi_to_Phi_E_inputs_not_source_locked`

## NEXT_ACTION:
Source-lock volumetric `c_v` with measurement uncertainty, independently derive or calibrate `e0`, and prove the base `Phi -> Phi_E` map without TTG target residuals or Xie 2026.

## CLAIM_BOUNDARY:
This wave closes a named conditional response branch only. It is not a calibration of base `alpha_Phi_K`, not an external TTG prediction, not a closure of Full Topic 13, and not global UET closure.
