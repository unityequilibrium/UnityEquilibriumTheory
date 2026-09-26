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

## 2026-09-26 - Topic 13 bounded and aggregate closure separation

MAJOR_RESULT_CLOSURE: The bounded O(2)/He-4 thermal track remains
`CLOSED_FOR_CORE`; the aggregate Full Topic 13 matrix is `PARTIAL`, with its
canonical gate `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_IS_ACTUALLY_CLOSED: The bounded O(2)/He-4 acceptance audit passes 13/13
declared criteria. Its separate Core handoff remains eligible to start the
curved 3+1 parent work. The closure matrix now distinguishes that bounded
result from graphite/TTG aggregate readiness.

WHAT_REMAINS_OPEN: The aggregate matrix reports 21 `CLOSED_FOR_LANE`, 6
`CLOSED_AS_NO_GO`, 0 `CLOSED_FOR_CORE`, and 10 `OPEN` subresults across 7
blockers: Ding-compatible `C_src`/reproduction; graphite `alpha_Phi_K`;
normalized beta/SI correspondence; physical Kubo coefficient; dimensional
Phi-to-thermal map; material-regime mapping to TTG; and `c_v` source uncertainty.

DEPENDENCY_UNLOCKED: Bounded O(2)/He-4 Core handoff only. Curved 3+1 research
may start; Gravity/GR remains blocked until its separate parent closes. Full
constitutive transport and Galaxy remain locked.

STATUS: Bounded Core acceptance `PASS_T13_FULL_CORE_READY_ACCEPTANCE`;
aggregate Full Topic 13 `BLOCKED_OPEN_T13_FULL_BRIDGE`; claim promotion false;
Xie 2026 numeric holdout unconsumed.

WHAT_CHANGED: The aggregate matrix `status` now follows the canonical Full
Topic 13 gate. The He-4 closure is exposed as `bounded_core_track_status`,
while the legacy `full_core_unlock` flag is explicitly scoped to
`BOUNDED_O2_HE4_CORE_TRACK`. Closure register and dependency rebuilds preserve
both scopes; no physics equation, source role, threshold, or dependency decision
was changed.

EQUATION_OR_MAPPING: Measurement definitions remain
`y_TTG=Delta_Tq(t)/Delta_Tq(0)` and
`y_TTG^UET=Delta_Phi(t)/Delta_Phi(0)`. The dimensional operator remains
`Delta_Tq=alpha_Phi_K*Delta_Phi`; graphite SI calibration is still open and the
bounded He-4 calibration is not transferred to graphite.

VERIFICATION: Topic 13 closure matrix, repo-wide closure register, and
dependency gate rebuilt in sequence; bounded acceptance passed 13/13; 12
focused regression functions passed by direct invocation. `pytest` is not
installed in the bundled runtime, and the ordinary test import path requires
SciPy, which is unavailable there. No holdout payload, fit, or threshold change.

CONTROLLING_BLOCKER: `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`;
the seven aggregate blockers remain visible in the matrix and register.

NEXT_ACTION: Close an authorized source or independent base-Phi/SI calibration
package and physical transport package before reopening the aggregate
readiness decision. Do not infer graphite scale from the bounded He-4 result.

CLAIM_BOUNDARY: This is a reporting/integration repair plus verification of an
existing bounded He-4 acceptance. It does not close Full Topic 13, validate
graphite TTG externally, close curved 3+1 or Gravity, or promote global UET.

EVIDENCE_PATHS:
- `docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json` (SHA-256: `E6E84772A400273C438E0B8CA3C7B5B14C9D720DA0420FB4021B1C0E7A54FE66`)
- `docs/core/07_artifacts/topic13/t13_full_core_ready_acceptance_audit.json` (SHA-256: `CB03D1C201F4F93B3FCA6F9946C7990B9AAD2600E9F4E99AC9E40FD949E17A11`)
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json` (SHA-256: `961AEAC0383E25D1AF64B3B161C67E2F57E76DFA26B0E94BFB9BEEEFD1BB9EC1`)
- `docs/core/07_artifacts/gates/uet_major_result_closure_register.json` (SHA-256: `1C420887141F248F9637D999441039DB66B768DE3FA9582969C9754F5725E550`)
- `docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json` (SHA-256: `ECBEFDF12EE1EB6661AE8096E3F62BF1FFA7992C96CA94F1149FDBC25A8BBE6E`)
