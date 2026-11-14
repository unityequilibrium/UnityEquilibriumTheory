# Formula Audit: 0.2 Black Hole Physics

## Scope

This registry covers the calculation paths currently used by the black-hole topic:
the horizon/shadow benchmark path, the internal saturation-core diagnostic, GR comparator
quantities, and the CCBH cosmological-coupling analysis. It separates standard GR identities,
source-backed observational inputs, heuristic UET bridge terms, and data-blocked research
paths.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `BH-RS-GR` | `R_s = 2GM/c^2` | `Engine_BlackHole.compute_schwarzschild_radius`; `Competitor_GR_Benchmark.calculate_gr_metrics` | `G` m^3 kg^-1 s^-2; `M = Mass_Msun * M_sun` kg; `c` m/s; output m | `source_locked_physics_constant` via `docs.core.uet_parameters` | `identity` | primary EHT shadow gate and GR comparator | Unit mismatch in mass or `c` directly corrupts all radius/shadow metrics. | Keep constants tied to shared core and record source hash in artifact where practical. |
| `BH-SHADOW-DIAM` | `D_shadow = 5.2 R_s` | `Engine_BlackHole.compute_shadow_diameter`; `Research_EHT_Validation.py` | `R_s` m; output m | `source_locked_benchmark_input` / GR lensing approximation | `checked local benchmark relation` | primary EHT angular-size comparison | Treating `5.2` as UET-derived would overstate the model; it is a benchmark lensing factor. | Replace scalar factor with cited EHT/GR shadow model note and uncertainty interval. |
| `BH-ANGULAR-SIZE` | `theta_uas = (D / distance_m) * 206265 * 1e6` | `Engine_BlackHole.compute_angular_size_uas`; `Research_EHT_Validation.py` | `D` m; `distance_m` m; output microarcseconds | `source_locked_unit_conversion` | `identity` | primary EHT gate | Wrong distance unit, Mpc/kpc conversion, or arcsecond conversion changes pass/fail. | Artifact should record per-target mass, distance, observed shadow, predicted shadow, and tolerance. |
| `BH-HORIZON-TEMP` | `T_H = hbar c^3 / (8 pi G M k_B)` | `Engine_BlackHole.compute_temperature`; `Competitor_GR_Benchmark.py` | `hbar` J s; `c` m/s; `G`; `M` kg; `k_B` J/K; output K | `source_locked_physics_constant` | `identity` | diagnostic/comparator | Not part of current primary gate; using it as proof support would be claim inflation. | Add explicit temperature baseline artifact if this becomes a claim-bearing result. |
| `BH-ENTROPY-GR` | `S = 4 pi G M^2 k_B / (hbar c)` | `Engine_BlackHole.compute_entropy`; `Competitor_GR_Benchmark.py` | `M` kg; output J/K | `source_locked_physics_constant` | `identity` | diagnostic/comparator; link to 0.13 thermodynamic bridge | Hidden distinction between thermodynamic entropy and information bits can create unit confusion. | Add bit conversion `S/(k_B ln 2)` when comparing to information-density claims. |
| `BH-EVAP-TIME` | `t_evap_yr ~= 6.6e74 * (M/M_sun)^3` | `Competitor_GR_Benchmark.py` | `M/M_sun` dimensionless; output years | `checked_local_reference` | `checked local approximation` | competitor-only diagnostic | Approximation is not used by verifier; cannot support broad lifetime claims. | Replace with full SI formula and source citation if promoted. |
| `BH-UET-POTENTIAL` | `V_eff(r) = -GM/r + beta G M R_core / r^2` | `Engine_BlackHole.solve_internal_structure` | `r`, `R_core` m; `M` kg; `beta` dimensionless; output J/kg-like potential proxy | `heuristic_bridge` | `heuristic bridge` | diagnostic singularity-resolution mechanism | `R_core = 1e-4 R_s` is visualization scaling, not Planck-scale saturation. Overclaiming this as physical core size is invalid. | Replace visualization-scale core with a physically motivated saturation scale or label every plot as rescaled. |
| `BH-STABLE-RADIUS` | minimum of `V_eff(r)` over logarithmic grid | `Engine_BlackHole.solve_internal_structure` | grid radius m; output `stable_radius_m` | `topic_derived_relation` from heuristic potential | `checked local diagnostic` | diagnostic only | Minimum depends on grid bounds and rescaled `R_core`; it cannot prove singularity resolution. | Add convergence sweep over grid resolution and core-scale parameter. |
| `BH-CCBH-K` | `k = d ln M / d ln a`; engine returns `k = 3.0` | `Engine_BlackHole.solve_coupling_k`; `Research_CCBH_Analysis.fit_ccbh` | `a = 1/(1+z)` dimensionless; `M` solar masses or log solar masses; `k` dimensionless | `heuristic_bridge` plus published CCBH comparator | `data-blocked benchmark path` | secondary research path | Current CCBH script requires Shen/Kormendy files outside repo; it cannot be a primary gate until upstream data is stored under `docs/data/external/...`. | Store raw Shen/Kormendy sources in external cache, hash them, then rerun fit with explicit selection-bias limitations. |
| `BH-RECYCLING-POWER` | `dM/dt = k M H0`; `P = c^2 dM/dt` | `Research_CCBH_Analysis.analyze_entropy_recycling` | `M` kg; `H0` s^-1; output W | `heuristic_bridge` | `exploratory diagnostic` | future theory bridge only | Depends on assumed galaxy density, average BH mass, `k`, and volume; not a verified dark-energy mechanism. | Move to a dedicated cosmology/thermodynamics bridge after source-backed CCBH data exists. |

## Unit And Conversion Notes

- Mass inputs in engine-facing APIs are usually solar masses and are converted with `M_sun`.
- EHT distances use Mpc for M87* and kpc for Sgr A* before conversion to meters.
- Angular shadow outputs are reported in microarcseconds.
- The internal potential diagnostic is a scaled numerical mechanism; it should not be read as
  a physical Planck-core radius.

## Current Formula Boundary

- The EHT shadow path can support an internal benchmark statement only.
- The GR radius, Hawking temperature, and entropy formulas are standard comparator identities.
- The saturation-core and CCBH paths remain heuristic/data-blocked until their scale choices and
  upstream datasets are locked.
