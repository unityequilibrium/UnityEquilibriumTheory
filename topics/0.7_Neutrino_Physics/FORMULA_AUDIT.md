# Formula Audit: Neutrino Physics

## Scope

This registry covers the formulas and calculation paths currently used by the 0.7 verifier.
It separates source-locked benchmark values from UET-style model outputs so public wording
does not promote compatibility checks into proof claims.

## Formula Registry

| formula_id | relation | variables and units | constant_origin | proof_status | verification_role | limitation |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `NUPMNS-ANGLE-GEOM` | `theta12`, `theta23`, `theta13` from `UETNeutrinoSolver.pmns_angles_geometric()` | angles in degrees; current engine path gives `theta12 = arcsin(1/sqrt(3))`, `theta23 = pi/4`, and `theta13 = (2/3) * theta_C` | `heuristic_bridge` with Cabibbo calibration pivot | `revised benchmark-gated heuristic bridge` | primary gate against NuFIT 6.0 3sigma angle ranges | This is a real model revision, not a verifier-threshold change. Passing the gate would show benchmark compatibility only; a first-principles derivation of the tri-generation/Cabibbo-leakage bridge remains open. |
| `NUPMNS-MATRIX` | standard PMNS matrix from `theta12`, `theta23`, `theta13`, `delta_cp` | angles converted from degrees to radians; matrix entries dimensionless and complex | `checked_local_reference` | `identity` for matrix construction; inputs are not all derived | diagnostic | Matrix construction is standard, but the physical status depends on the source of the input angles and phase. |
| `NUOSC-2FLAVOR` | `P = sin^2(2 theta) * sin^2(1.27 * Delta_m^2 * L / E)` | `theta` degrees converted to radians; `Delta_m^2` in eV^2; `L` in km; `E` in GeV | `source_locked_benchmark_input` for convention; runtime values may be benchmark-fed | `checked local` | diagnostic oscillation path | The `1.27` factor is valid only under the declared eV^2/km/GeV convention. Some script examples use abstract values and should not be treated as experimental predictions. |
| `NUMASS-SPLIT` | `Delta m21^2`, `Delta m31^2` runtime parameters | eV^2; verifier reports scaled `1e5 eV^2` and `1e3 eV^2` forms | `source_locked_benchmark_input` | `benchmark anchor` | gate against NuFIT 6.0 3sigma ranges | Current mass splittings are benchmark-fed runtime parameters, not UET first-principles outputs. |
| `NUABS-SEESAW` | `m_nu = v_ew^2 / M_I`, with final `GeV -> eV` conversion | `v_ew` in GeV; `M_I` in GeV; result in eV | `heuristic_bridge` plus source-locked electroweak scale convention | `heuristic bridge` | gate against KATRIN 2025 upper limit | The current branch repairs a prior unit mismatch, but the heavy information scale remains a compact model bridge rather than an externally derived neutrino-mass theory. |
| `NUHIER-BETA` | `hierarchy = NORMAL if sign(beta) >= 0 else INVERTED` | `beta` dimensionless UET coupling; output categorical | `heuristic_bridge` | `diagnostic proxy` | diagnostic only | This is a topology proxy, not a computed Chern/winding-number proof. It must not be described as a definitive hierarchy solution. |

## Unit And Conversion Notes

- NuFIT angle checks use degrees at the reporting layer.
- PMNS matrix construction converts degrees to radians before trigonometric operations.
- Oscillation checks using the `1.27` factor require `Delta_m^2` in eV^2, `L` in km, and
  `E` in GeV.
- The absolute-mass branch keeps both `v_ew` and `M_I` in GeV, then converts the final mass
  from GeV to eV.

## Hardening Steps

- Derive the tri-generation/Cabibbo-leakage angle bridge from the UET field equations instead of treating it as a benchmark-gated heuristic.
- Replace checked transcription of the NuFIT table with a machine-parsed or independently
  double-entered source pipeline.
- Separate diagnostic oscillation demos from benchmark-gate scripts in public summaries.
- Derive or downgrade the `beta` hierarchy proxy before using it as claim support.
