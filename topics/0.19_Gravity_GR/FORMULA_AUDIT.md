# Formula Audit: 0.19_Gravity_GR

Review status: reviewed registry for the current gravity engine, CODATA G checkpoint, equivalence-principle proof script, and short-range gravity lane.

The present primary verifier checks that the engine constant package matches the topic-local CODATA 2018 working copy. It does not derive `G`, prove Einstein's field equations, validate light bending/perihelion precession, or solve singularities.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `GR19-CONSTANT-PACKAGE` | engine constants `G`, `c`, `hbar` | `Code/01_Engine/Engine_Gravity_GR.py::get_planck_units` | `G` in m^3 kg^-1 s^-2; `c` in m/s; `hbar` in J s | CODATA-like constants embedded in `UETParameters` fallback/defaults and checked against `codata_2018_gravity.json` | source-constant checkpoint | primary artifact input path | If defaults are mistaken for derivations, the topic overclaims. | Make `UETParameters` constant provenance explicit and load constants from manifest where possible. |
| `GR19-PLANCK-UNITS` | `l_P = sqrt(hbar G / c^3)`, `t_P = sqrt(hbar G / c^5)`, `m_P = sqrt(hbar c / G)` | `Code/01_Engine/Engine_Gravity_GR.py::get_planck_units` | length m; time s; mass kg | formula definitions based on source-locked constants | identity/standard definition | reported metric in primary artifact | Planck units are definitions from constants, not evidence for UET gravity. | Compare all Planck units to CODATA rows and record uncertainties. |
| `GR19-G-CHECKPOINT` | `error = |G_engine - G_CODATA| / G_CODATA` | `Code/03_Research/Research_G_Constant.py`; `Data/03_Research/codata_2018_gravity.json` | dimensionless percent error | source-locked CODATA working copy | checked local benchmark | primary verifier gate | Zero error can occur by copying the same constant, not by deriving it. | Add independent derivation claim only after a real derivation artifact exists. |
| `GR19-NEWTON-ACCELERATION` | `g = G M / r^2` | `Code/01_Engine/Engine_Gravity_GR.py::uet_gravitational_acceleration` | `M` kg; `r` m; output m/s^2 | standard Newtonian formula with source constant `G` | standard relation / diagnostic | engine demo only | Demo Earth/Moon/Sun values are not a GR validation. | Turn surface-gravity checks into artifact rows with source values and uncertainty. |
| `GR19-SCHWARZSCHILD-RADIUS` | `r_s = 2 G M / c^2` | `Code/01_Engine/Engine_Gravity_GR.py::schwarzschild_radius` | `M` kg; output m | standard GR Schwarzschild relation | standard relation / diagnostic | engine demo only | Can be mistaken for singularity avoidance or black-hole validation. | Link to `0.2` black-hole artifact and keep singularity claims separate. |
| `GR19-REFRACTIVE-INDEX` | `n(r) ~= 1 + 2GM/(r c^2)` | `Code/01_Engine/Engine_Gravity_GR.py::run_gravity_engine` | dimensionless refractive-index approximation | standard weak-field heuristic | heuristic diagnostic | excluded from primary verifier | Weak-field approximation may be overread as full metric derivation. | Add domain limits and compare against light-bending artifact if one exists. |
| `GR19-EQUIVALENCE-ETA` | `eta_uet = 0 * (beta/beta)` | `Code/02_Proof/Proof_Equivalence_Principle.py` | dimensionless Eotvos parameter | algebraic model assertion, not MICROSCOPE data fit | open / tautological diagnostic | excluded from primary verifier | A hardcoded zero can masquerade as experimental validation. | Compare against MICROSCOPE 2022 dataset with uncertainty and nonzero reported value. |
| `GR19-YUKAWA-SHORT-RANGE` | `V(r) = -GmM/r * (1 + alpha exp(-r/lambda))` comparator form | `Code/03_Research/Research_ShortRange_Gravity.py`; `Data/03_Research/eotwash_2007_data.json` | `lambda` m; `alpha` dimensionless | Eot-Wash/Kapner source-labeled exclusion curve | source-labeled comparator, not UET derivation | secondary lane | Short-range constraints can be cited without fitting a UET parameter. | Create a secondary artifact for allowed/excluded UET short-range parameter values. |

## Claim Boundary

- Supported now: internal CODATA constant checkpoint and Planck-unit definition reporting.
- Not supported now: derivation of `G`, Einstein field equations, light bending, perihelion precession, equivalence-principle experimental validation, or singularity avoidance.
- Downstream use: `0.0`, `0.2`, `0.3`, `0.21`, `0.23`, and `0.26` may cite this topic only as a constant/checkpoint and weak-field formula registry unless future GR artifacts are added.

## Audit Link

- Primary artifact: `Result/artifacts/0_19_gravity_gr_verification.json`
- Core audit report: `docs/meta/core_research_hardening_audit.md`
