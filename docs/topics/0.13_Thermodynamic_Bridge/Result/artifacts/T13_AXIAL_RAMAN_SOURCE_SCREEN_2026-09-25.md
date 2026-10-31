# Topic 13 Axial-Raman Source Screen (2026-09-25)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for screening the currently identified primary-literature routes only.

WHAT_IS_ACTUALLY_CLOSED: Three candidate routes were checked against the same-state axial-strain Raman acceptance contract. None provides an independently measured graphite `epsilon_zz` paired with an `E2g` frequency row, source-grade uncertainty, and a permitted numeric payload. The source-search question is closed for these candidates; the experimental-data question remains open.

WHAT_REMAINS_OPEN: A matched-state axial-strain Raman row; graphite dimensional `Phi` anchor or independent `alpha_Phi_K`; Ding-compatible `C_src(T)` or an accepted same-regime reproduction; and the remaining graphite TTG observable/transport map.

DEPENDENCY_UNLOCKED: None. The O(2)/He-4 lane remains separately `CLOSED_FOR_CORE`; this screen does not close graphite TTG or the aggregate Topic 13 gate.

STATUS: `PASS_SCOPED_AXIAL_RAMAN_SOURCE_SCREEN_NO_ACCEPTED_ROW`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_CHANGED: Added a deterministic source-route screen, machine-readable artifact, regression tests, and read-only Topic 13/Core integration records. No equation, registry entry, or dependency gate was changed.

EQUATION_OR_MAPPING: The required missing experimental observable is `D_c/x_mode = 2*dln(nu_E2g)/d epsilon_zz` at fixed in-plane strain. No value is inferred from the screened papers.

VERIFICATION: Source-screen verifier passed; focused regression suite passed 4/4. Artifact SHA-256: `48609DEE885053CBA07509B5088534513DDCB7977D9C47C15E7FA1540814F21A`. The unchanged full-gate status is `BLOCKED_OPEN_T13_FULL_BRIDGE` (SHA-256 `20CC32438F365E3A4CEE4B22954665C41447AEC751F30A4B80CDF360744455EB`). Xie 2026 was not accessed; no target curve was used or fitted.

CONTROLLING_BLOCKER: For this Raman sublane, `same_state_independent_axial_strain_raman_row_missing`. The full graphite aggregate remains controlled by `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`; source acquisition separately remains blocked on Ding-compatible `C_src` or an accepted same-regime reproduction.

NEXT_ACTION: Stop rerunning this unchanged literature screen. A useful new input must pair independently calibrated X-ray `epsilon_zz` (preferably the full strain tensor) and Raman `E2g` data on the same graphite specimen, temperature, loading path, and time window, with row-level uncertainty/covariance. Continue Ding `C_src` and graphite `Phi`-scale work as separate controllers.

CLAIM_BOUNDARY: Source-route boundary only; no experimental Raman deformation coefficient, no `alpha_Phi_K`, no `C_src`, no graphite TTG validation, no full Topic 13 closure, no dependency unlock, and no global UET promotion.

## Candidate Routes

| Source | What it contributes | Why it does not close the missing row |
| :-- | :-- | :-- |
| [Andrada-Chacon et al. (2017)](https://doi.org/10.1016/j.carbon.2016.11.058) | HOPG under quasi-uniaxial c-axis loading; simultaneous Raman and electrical-resistance study. | The inspectable source description uses relative D/D-prime defect-band intensities, not an independently measured `epsilon_zz` paired with `E2g` frequency rows. Full numeric rows and uncertainties were not acquired. |
| [Wang et al. (2019)](https://doi.org/10.1063/1.5089291) | Direct transient c-axis strain from time-resolved X-ray diffraction; the paper reports 10.0 +/- 0.5% at 100 ps and 8.5 +/- 0.5% at 200 ps. | Above-ablation, large-strain transient regime; no paired Raman `E2g` response. Its temperature map is simulation-derived, not a matched measured thermal calibration. |
| [He et al. (2020)](https://doi.org/10.1103/PhysRevLett.124.065701) | Joint high-pressure Raman/X-ray phase observations under strong nonhydrostatic compression. | The graphite strain tensor is not reported as a paired row; indentation stress is inferred from diamond Raman and the graphite G-band changes accompany strong shear/interlayer-bonding phase transformation. |

## Acceptance Contract

A future row is eligible only if it provides the same declared specimen/preparation, independently measured `epsilon_zz` (or full strain tensor), identified `E2g` frequency, matched temperature/phase/loading/time, a preregistered elastic interval, row-level uncertainty and covariance, permitted numeric data with preprocessing and hash, and a no-fit/no-holdout access audit.

The immediate experimental design is a single-specimen, synchronized X-ray/Raman measurement with temperature and loading history recorded independently. A different paper for strain and a different paper for Raman cannot be composited into a measured derivative.
