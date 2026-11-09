# Formula Audit: 0.12_Vacuum_Energy_Casimir

Review status: reviewed registry for the current Casimir verifier and vacuum-energy engine surfaces.

This audit separates the source-backed Casimir benchmark from the larger vacuum-energy and dark-energy bridge. The current primary verifier can support only the sphere-plate Casimir comparison against the Mohideen working dataset.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `VAC-PP-CASIMIR` | `F/A = -pi^2 hbar c / (240 d^4)` | `Code/01_Engine/Engine_Vacuum.py::calculate_casimir_force` | `d` in nm converted to m; output is pressure/force per area in SI base units, despite the method name saying force | `hbar`, `c` are source-locked physics constants; coefficient is standard ideal parallel-plate QED result | checked local formula surface, not a UET derivation proof | diagnostic scaling reference; not the primary artifact gate | Mislabeling pressure as force can inflate claims or mix geometries. | Rename/output-document this as pressure in a later engine cleanup, or return area-normalized units explicitly. |
| `VAC-SPHERE-PFA` | `F = -pi^3 R hbar c / (360 d^3)` | `Code/01_Engine/Engine_Vacuum.py::calculate_physical_casimir_force`; `Code/03_Research/Research_Casimir.py` | `d` in nm converted to m; `R` in um converted to m; output converted to nN | `hbar`, `c` source-locked; PFA geometry formula from standard Casimir sphere-plate approximation | source-backed benchmark relation, not a new UET proof | primary verifier formula for `0_12_vacuum_energy_casimir_verification.json` | Geometry mismatch or hidden radius calibration can create artificial agreement. | Freeze radius policy against the dataset radius and add a sensitivity artifact for `R=196 um` vs `R=200 um`. |
| `VAC-FINITE-CONDUCTIVITY` | `correction = clip(1 - (16/3)(lambda_p/d)/pi, 0.8, 1.0)` | `Code/01_Engine/Engine_Vacuum.py::calculate_physical_casimir_force` | `lambda_p` and `d` in m; dimensionless correction multiplier | `lambda_p = 136 nm` is a material heuristic for gold plasma wavelength | heuristic bridge, verifier-tested only as part of the current benchmark | primary model component in the Casimir artifact | The clip floor can mask short-distance model failure. | Add unclipped comparison and material-source provenance for the gold plasma wavelength. |
| `VAC-CUTOFF` | `cutoff = 1 / (1 + (l_p/d)^4)` | `Code/01_Engine/Engine_Vacuum.py::calculate_casimir_force` | `l_p` and `d` in m; dimensionless multiplier | `l_p = 1.616e-35 m` source-locked approximate Planck length | open UET cutoff hypothesis; inactive at nm-scale Casimir distances | diagnostic only | May be mistaken for an experimentally validated Planck-scale vacuum cutoff. | Keep out of README claims until a separate high-energy or dimensional-analysis verifier exists. |
| `VAC-DARK-ENERGY-ANCHOR` | `rho_vac = 5.38e-10 * beta` | `Code/01_Engine/Engine_Vacuum.py::calculate_cosmological_constant` | `rho_vac` in J/m^3; `beta` dimensionless UET parameter | benchmark anchor near observed dark-energy density, not derived from the Casimir dataset | open heuristic anchor | excluded from the primary verifier | Returning an observed-like value can be misread as solving the cosmological-constant problem. | Replace with a derivation chain or mark as an explicit observational prior in code and docs. |
| `VAC-W-OMEGA` | `w = -1`, `Omega_total = 1` by normalized parameter ratios | `Code/01_Engine/Engine_Vacuum.py::verify_cosmological_equilibrium` | dimensionless cosmology diagnostics | algebraic engine defaults | open diagnostic, not observational fit | excluded from the primary verifier | Algebraic constants can be presented as cosmological validation. | Require cosmology dataset and baseline comparison before any README promotion. |
| `VAC-CASIMIR-SCALING` | `F(d) / F(2d) = 16` for ideal parallel plates | `Code/02_Proof/Proof_Casimir_Force.py` | dimensionless ratio using ideal `d^-4` pressure law | standard QED scaling relation | local formula sanity check | secondary proof-oriented diagnostic | Passing a scaling identity does not validate absolute force, material corrections, or dark energy. | Convert proof script into an artifact-writing secondary verifier. |

## Claim Boundary

- Supported now: the current engine can be checked against a topic-local Mohideen/Roy sphere-plate Casimir working dataset with explicit error thresholds.
- Not supported now: a proof of finite vacuum energy, a solution to the vacuum catastrophe, or a dark-energy derivation.
- Downstream use: `0.13`, `0.23`, `0.26`, and `0.0` may cite this topic only as a Casimir benchmark unless they cite a future dark-energy bridge artifact.

## Audit Link

- Primary artifact: `Result/artifacts/0_12_vacuum_energy_casimir_verification.json`
- Core audit report: `docs/meta/core_research_hardening_audit.md`
