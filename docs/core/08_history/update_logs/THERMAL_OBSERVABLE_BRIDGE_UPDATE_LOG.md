# Thermal Observable Bridge Update Log

## 2026-07-27 — C-to-thermal observable bridge diagnostic

- Added an explicit normalized map `T_norm = T0 + alpha_T*C` and kept the gain
  open rather than fitting or treating it as a universal constant.
- Evaluated Fourier and Cattaneo heat-flux controls, entropy-production proxies,
  and the prior C path-cost ledger on the same synthetic periodic trajectory.
- Added a gain-rescaling identifiability test: fixed `C` with different thermal
  gains changes the thermal observable amplitude while leaving C path work fixed.
- The wave remains `SIMULATION_ONLY` and `BLOCKED_OPEN_MAPPING`; no external
  thermal source or SI measurement claim is promoted.
- Controlling blocker: derive or source-lock one dimensional observable map from
  a physical C realization to temperature/heat/entropy before calibration.


## 2026-08-08 ? Explicit Phi-to-kelvin calibration contract

- Added `ThermalPhiCalibration` and an explicit calibration-only application path.
- Open calibration records validate their missing scale/uncertainty but return no Kelvin observable; fitted independent records are rejected.
- Added `thermal_dimensional_calibration_contract.json`, its audit script, and regression tests.
- Verification: calibration audit `PASS_WITH_BLOCKED_INDEPENDENT_CALIBRATION`; combined thermal mapping tests `11/11`.
- Public-safety: `partial`; interface and anti-fitting rule are closed, but `alpha_Phi_K`, source-normalized TTG rows, heat flux, and entropy production remain blocked.
- Next controller: source-normalized TTG package plus independent calibration/derivation with uncertainty and holdout.

## 2026-08-08 - Phi-to-kelvin structural identifiability gate

- Added an algebraic scale witness to the thermal calibration verifier: `Delta_Phi -> s Delta_Phi` leaves the normalized TTG signal unchanged while `alpha_Phi_K -> alpha_Phi_K/s` leaves the dimensional response unchanged.
- Verified: normalized-signal residual `0.0`, dimensional-response residual `0.0`, fitted calibration rejection retained, focused thermal/query tests `5/5`.
- Finding: the missing `alpha_Phi_K` is not merely an absent fitted number; it is structurally non-identifiable from the current normalized Phi lane. An absolute dimensional anchor must enter through the action/energy normalization or an independent calibration.
- Claim boundary: no Phi-to-temperature, heat-flux, or entropy-production claim is promoted.
- Next controller: derive/source-lock the dimensional anchor first, then intake TTG rows with uncertainty and untouched holdout.

## 2026-08-08 - Dynamic-game physical-cost contract

- Added a separate opt-in physical-cost map for the resource-selection thermal
  bridge. It distinguishes normalized work from SI heat and requires
  independent `alpha_b`/`alpha_m` provenance.
- Verification: the contract audit passes with status
  `PASS_WITH_BLOCKED_INDEPENDENT_CALIBRATION`; open records and fitted records
  are rejected, while the numerical fixture is explicitly `TEST_ONLY`.
- Result: the algebraic mapping is now reviewable, but no external heat or
  entropy measurement is attached. This does not close the Phi-to-kelvin
  identifiability blocker.
- Next controller: source-lock one material calorimetry/heat-flux lane with
  uncertainty, detector response, and holdout.

## 2026-08-08 - Mapped cost/C control

- Passed the dynamic-game same-interaction/different-cost and same-cost/
  different-interaction controls through the `TEST_ONLY` SI cost-map fixture.
- Result: `C` residual `0.0` with mapped heat-difference magnitude `7.2 J`; `C`
  contrast `1.15` with same-cost heat residual `0.0`.
- Interpretation: the conversion contract does not merge interaction-derived
  C with declared work channels. The result remains internal contract evidence,
  not physical thermal validation.
- Next controller: source-lock a material heat/work observable and independent
  cost scales with uncertainty and holdout.
