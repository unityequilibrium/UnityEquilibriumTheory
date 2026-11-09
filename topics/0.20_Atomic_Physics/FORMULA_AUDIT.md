# Formula Audit: 0.20_Atomic_Physics

Review status: reviewed registry for the current hydrogen spectrum verifier, atomic engine, and secondary multi-body lanes.

The current primary verifier validates the standard Rydberg wavelength relation against a topic-local NIST hydrogen spectrum working copy and CODATA `R_H`. It does not derive the Rydberg formula from UET first principles and does not validate fine structure, Lamb shift, helium, or many-electron atoms.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `AT20-RYDBERG-WAVELENGTH` | `1/lambda = R_H (1/n_lower^2 - 1/n_upper^2)` | `Code/03_Research/Research_Rydberg_Validation.py`; `Code/01_Engine/Engine_Atomic_Hydrogen.py::transition_wavelength` | `lambda` in m or nm; `R_H` in m^-1; `n_upper`, `n_lower` dimensionless integers | CODATA `R_H` working copy; engine has an older local `R_H` constant | source-backed standard relation | primary verifier formula | Treating a standard formula check as a UET derivation would overclaim. | Add a derivation artifact if UET claims to produce `R_H` independently. |
| `AT20-RH-CODATA-CHECKPOINT` | compare fitted slope through origin with CODATA `R_H` | `Code/03_Research/Research_Rydberg_Validation.py`; `Data/03_Research/codata_2018_atomic.json` | slope in m^-1; error in ppm | CODATA 2018/2021 constants working copy | checked local benchmark | primary artifact metric | The fitted slope can be biased by rounded local wavelength rows. | Add uncertainty propagation and source-table transcription notes. |
| `AT20-SPECTRUM-RESIDUAL` | `ppm = |lambda_pred - lambda_obs| / lambda_obs * 1e6` | `Code/03_Research/Research_Rydberg_Validation.py`; `Data/03_Research/nist_hydrogen_spectrum.json` | wavelengths in nm; ppm dimensionless | NIST ASD working copy | source-backed internal benchmark | primary artifact metric | Rounded wavelengths or vacuum/air mismatch can dominate ppm-level claims. | Keep vacuum/air fields explicit and add per-line source precision. |
| `AT20-BOHR-ENERGY` | `E_n = -13.5984 eV / n^2` style level relation | `Data/03_Research/hydrogen_spectra_data.json`; `Code/02_Proof/Proof_Hydrogen_Spectrum.py` | energy eV; `n` dimensionless | local hydrogen level working copy | source-labeled diagnostic | secondary lane | It can be confused with QED/fine-structure validation. | Convert level comparison into artifact rows with source precision. |
| `AT20-ENGINE-RH-LOCAL` | `R_H = 1.09677e7 m^-1` local engine constant | `Code/01_Engine/Engine_Atomic_Hydrogen.py` | m^-1 | local rounded benchmark anchor | benchmark anchor | engine demo only | Rounded constant may inflate spectral residuals if used for ppm claims. | Load `R_H` from `codata_2018_atomic.json` in the engine or record rounding as limitation. |
| `AT20-THREEBODY-COUPLING-SMOKE` | `check = beta / beta` | `Code/03_Research/Research_Atomic_ThreeBody.py` | dimensionless | UET parameter sanity check | smoke test | excluded from primary verifier | This does not validate atomic three-body physics. | Replace with actual three-body atomic benchmark or keep as code-health check. |
| `AT20-MULTI-ELECTRON-LANE` | multi-electron comparison path | `Code/03_Research/Research_Multi_Electron.py` | unit audit incomplete | mixed local benchmark/model terms | open | excluded from primary verifier | Many-electron claims can leak into hydrogen-only evidence. | Add helium/multi-electron artifact with source-backed energies. |

## Claim Boundary

- Supported now: internal hydrogen-spectrum benchmark using NIST/CODATA working copies and explicit ppm thresholds.
- Not supported now: UET first-principles derivation of `R_H`, fine structure, Lamb shift, helium, many-electron closure, or universal atomic theory.
- Downstream use: `0.6`, `0.17`, `0.21`, `0.23`, and `0.0` may cite this topic only as a hydrogen Rydberg benchmark unless future artifacts expand the domain.

## Audit Link

- Primary artifact: `Result/artifacts/0_20_atomic_physics_verification.json`
- Core audit report: `docs/meta/core_research_hardening_audit.md`
