# Formula Audit: 0.26_Cosmic_Dynamic_Frame

Audit status: reviewed registry, replacing the bootstrap scaffold.

Scope note: this topic is an exploratory dynamic-frame cosmology package. It currently mixes Laniakea flow visualization, SPARC-like galaxy rotation reuse, Pioneer-drag fitting, toroidal topology visualizations, and persistence arguments. These are separate evidence classes and must not be collapsed into a single cosmology claim.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T26-001` | Newtonian rotation `V_newton = sqrt(G M_disk / R)` | `Code/01_Engine/Engine_Dynamic_Universe_v1.py::calculate_Newtonian` | `G = 4.301e-6 kpc km^2 s^-2 M_sun^-1`; `M_disk` solar masses; `R` kpc; `V` km/s | astronomy unit conversion constant, inherited from galaxy-rotation practice | source-backed formula, local data dependent | Baseline term in dynamic galaxy fits | Mass model comes from Topic `0.1` loader and inherits its data assumptions | Link directly to `0.1` artifact and SPARC manifest |
| `T26-002` | fluid velocity proxy `V_fluid = sqrt(2 a0 R_m decay(R))/1000` | `Engine_Dynamic_Universe_v1.py::calculate_CosmicFluid` | `a0` m/s^2; `R_m` m; output km/s; `decay` dimensionless | Pioneer/MOND-like anchor plus topic hypothesis | heuristic bridge | Tests dynamic-frame correction shape | `a0` is treated as universal and may be double-used across domains | Source-lock `a0`, define why it applies to galaxy scales, and compare to MOND baseline |
| `T26-003` | decay factor `1/(1+(R_kpc/R_scale)^power)` | `Engine_Dynamic_Universe_v1.py::get_decay_factor` | `R_kpc`, `R_scale=1 kpc`; `power=2`; dimensionless factor | topic-tuned model parameter | open heuristic | Screens fluid term by scale | Tuned values can fit by construction | Add sensitivity/ablation artifact and freeze parameters before comparison |
| `T26-004` | combined speed `V_total = sqrt(V_newton^2 + V_fluid^2)` | `Engine_Dynamic_Universe_v1.py::solve_system` | km/s | topic model combination rule | heuristic bridge | Galaxy dynamic-frame fit | Vector-sum/energy-sum assumption needs derivation | Derive from explicit potential/force balance or label as fit rule |
| `T26-005` | mean relative velocity error `mean(abs((V_obs-V_total)/V_obs))*100` | `Engine_Dynamic_Universe_v1.py::solve_system` | percent | standard diagnostic | internal benchmark metric | Fit-quality metric | No uncertainty weighting/covariance | Add chi-square or likelihood with observed uncertainties |
| `T26-006` | Laniakea flow landmark map in supergalactic coordinates | `Code/03_Research/Research_Cosmic_Flows.py`; `Data/03_Research/Laniakea_Flows.json`; `docs/data/external/cosmology/laniakea/tully_2014/source_record.json` | SGX/SGY/SGZ Mpc; velocity km/s where present | source-referenced local working copy from Tully et al. 2014 summary | checked local visualization input | Primary verifier visualization/provenance gate | Landmarks are not raw Cosmicflows data; frame metadata incomplete | Archive raw table, frame convention, preprocessing, and residual gate |
| `T26-007` | Pioneer drag density `rho = 2 m a_obs/(Cd A v^2)` | `Code/03_Research/Research_Pioneer_Drag.py`; `docs/data/external/spacecraft/pioneer_anomaly/anderson_2002/source_record.json` | `rho` kg/m^3; `m` kg; `a` m/s^2; `A` m^2; `v` m/s | source-referenced local Pioneer working copy + assumed spacecraft constants | heuristic fit | Secondary dynamic-frame hypothesis | Thermal recoil and consensus Pioneer explanations not modeled | Add competitor baseline and source-lock telemetry/thermal model |
| `T26-008` | Stokes-like drag `F_drag = 6 pi mu R v`, `a_drag = F/m` | `Code/02_Proof/Proof_Dynamic_Viscosity.py` | SI force/acceleration terms | standard Stokes law reused as analogy | analogy/heuristic | Conceptual viscosity plot | Script language overstates equivalence to dark matter | Treat as analogy until derived for cosmological medium |
| `T26-009` | viscous-limit curve `V = sqrt(a0 r)` | `Proof_Dynamic_Viscosity.py` | `a0` m/s^2; `r` m; `V` m/s | MOND/Pioneer-like anchor | heuristic comparison | Shows scaling shape | `V ~ R^0.5` is not flat rotation and claim wording can be misleading | Compare against MOND/SPARC curves and state slope correctly |
| `T26-010` | torus parameterizations and singularity-avoidance visuals | `Engine_Dynamic_Universe_v2_Torus.py`; `Proof_Toroidal_Cycle.py`; visualizers | angles/radii mostly dimensionless or arbitrary plotting units | topology visualization convention | visualization hypothesis | Illustrates topology ideas | Visual topology is not cosmological evidence | Add observable predictions or keep as conceptual diagram |

## Claim Guardrails

| Claim area | Maximum current claim class | Reason |
| :-- | :-- | :-- |
| Laniakea flow map | `D/C` | Source-labeled landmark visualization with local working copy; raw flow data not locked. |
| Galaxy dynamic-frame fits | `C/D` | Reuses SPARC-like loader and heuristic correction; needs baseline comparison. |
| Pioneer drag | `D` | Local CSV fit with assumed constants; competitor thermal-recoil baseline absent. |
| Dark-matter replacement | `A/D` | Current formulas are heuristic bridges and analogies. |
| Toroidal cosmology | `A/D` | Visualization/topology hypothesis without observable gate. |

## Required Follow-Up

- Archive raw Laniakea/Cosmicflows tables, observer frame, velocity convention, distance calibration, and preprocessing.
- Link galaxy-fit claims to Topic `0.1` data/artifacts instead of duplicating credibility.
- Add Pioneer anomaly competitor baseline and source-locked spacecraft constants before any physical claim.
- Keep `Research_Cosmic_Flows.py` as visualization/provenance gate until numeric flow residuals are defined.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
