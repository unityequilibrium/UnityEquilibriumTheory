# Research Wave 2026-08-11: Cp-Cv Correction Contract

MAJOR_RESULT_CLOSURE:

- `T13_CP_CV_CORRECTION_CONTRACT`
- `closure_level`: `CLOSED_FOR_LANE`
- This is a progress result for the thermodynamic formula lane, not closure of Full Topic 13.

WHAT_IS_ACTUALLY_CLOSED:

- The standard solid-state correction is explicit for both mass-specific and volumetric heat capacity:
  - `c_p^m - c_v^m = T * alpha_V^2 * K_T / rho`
  - `c_p^V - c_v^V = T * alpha_V^2 * K_T`
  - `c_v^V = rho * c_p^m - T * alpha_V^2 * K_T`
- The implementation checks units, positivity of the corrected heat capacity, mass-to-volume consistency, and independent first-order uncertainty propagation.
- The formula audit is recorded at `docs/core/07_artifacts/topic13/t13_cp_cv_correction_audit.json` with SHA-256 `73d2cb23c062ff29d8065651805842ac26a4f34a3c24f0bf9e826e6a16d797de`.
- The source contract cites NIST SP 960-11, Section 6.3.1.5, pages 69-70, Equation (21), as the standard relation. Numeric graphite correction inputs were not consumed.

WHAT_REMAINS_OPEN:

- `alpha_V` must be a source-locked volumetric thermal-expansion coefficient for the same graphite material/regime.
- `K_T` must be a source-locked isothermal bulk modulus at the same state.
- Density and all correction-input uncertainties must be source-backed; the Georgia Tech source currently supplies a mass-specific `c_p` row and 95% confidence interval, not a complete `c_v` package.
- Material-regime correspondence to the TTG source remains open.
- `e0`, the base `Phi -> Phi_E` mapping, and independent `alpha_Phi_K` remain open.
- EOS, covariant transport, SK/KMS, entropy-current, and dissipative-balance closure remain open.

DEPENDENCY_UNLOCKED:

- Only the named `c_p -> c_v` formula lane is unlocked for source intake and uncertainty review.
- No volumetric `c_v` calibration, base-`Phi` Kelvin prediction, downstream curved 3+1, Gravity, transport, or Galaxy dependency is unlocked.

STATUS:

- Full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `closure_level=PARTIAL` and `claim_promotion=false`.

WHAT_CHANGED:

- Added `docs/core/thermal_cp_cv_correction.py`.
- Added the machine-readable audit and test for the correction contract.
- Connected the contract to the Topic 13 energy branch, full gate, major-result register, and source-wave runner.
- The Georgia Tech graphite source anchor remains separate: raw workbook SHA-256 `baa7f6181fa3d5521fc594cb2c832308927bc77dbac89c43b373bc304eaa6900`; its `c_v` status remains `OPEN` and it was not used for calibration.

EQUATION_OR_MAPPING:

```text
c_p^m - c_v^m = T * alpha_V^2 * K_T / rho
c_p^V - c_v^V = T * alpha_V^2 * K_T
c_v^V = rho * c_p^m - T * alpha_V^2 * K_T
```

- `alpha_V`: volumetric expansion coefficient `[K^-1]`.
- `K_T`: isothermal bulk modulus `[Pa = J m^-3]`.
- `rho`: density `[kg m^-3]`.
- `c_v^V`: volumetric constant-volume heat capacity `[J m^-3 K^-1]`.
- This mapping does not identify `Phi_E` with base `Phi` and does not introduce a new `R_gen` state.

VERIFICATION:

- Correction audit: `PASS_FORMULA_UNIT_CONTRACT_OPEN_INPUTS` with 13 checks.
- Focused Topic 13 regression suite: `35 passed`.
- Full source-wave runner: exit code `0`.
- Wave 1 integrity: `PASS_WITH_BLOCKED_LANES`; evidence hashes match, threshold is unchanged, and Xie 2026 holdout access remains false.
- Major-result register contains 13 entries and records `T13_CP_CV_CORRECTION_CONTRACT` as `CLOSED_FOR_LANE`.

CONTROLLING_BLOCKER:

- The controlling full-bridge blocker remains `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`, with the immediate source controller `alpha_V`, `K_T`, density uncertainty, and material-regime inputs not source-locked.

NEXT_ACTION:

- Source-lock `alpha_V`, `K_T`, density uncertainty, and material-regime correspondence for the same graphite regime; then construct `c_v` with uncertainty without reading TTG target residuals or Xie 2026.
- In parallel, independently derive or calibrate `e0` and prove the base `Phi -> Phi_E` mapping before any `alpha_Phi_K` estimate is emitted.

CLAIM_BOUNDARY:

- This wave closes a standard formula contract only. It is not an independent `alpha_Phi_K` calibration, not external validation, not a proof of UET, and not a closure of Full Topic 13 or the global theory.
