# Formula Audit: 0.15_Cluster_Dynamics

Review status: reviewed registry for the current cluster engine, virial scripts, and Bullet Cluster diagnostic verifier.

This topic currently contains two different evidence lanes: a virial/missing-mass heuristic lane and a Bullet Cluster offset diagnostic lane. The present primary artifact supports only a qualitative separation-sign diagnostic for Bullet Cluster style offsets. It does not yet calibrate the model to kpc offsets or prove a dark-matter-free cluster theory.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `CL15-VIRIAL-MASS` | `M_dyn = R v^2 / G` | `Code/01_Engine/cluster_solver.py::calculate_virial_mass_standard`; `Code/02_Proof/Proof_Virial_Mass.py` | `R` in m; `v` in m/s; `G` in SI; output kg | `G` source-locked physics constant; cluster radius/velocity are benchmark inputs | standard virial-style diagnostic, not a UET derivation | secondary comparator for missing-mass scale | Missing factor conventions and projection assumptions can shift cluster mass estimates. | Tie to `cluster_virial_1998.json` with per-cluster artifact rows and source DOI. |
| `CL15-UET-VELOCITY` | `v_uet = (v_newton^4 + G M a0)^(1/4)` where `v_newton^2 = G M / R` | `Code/01_Engine/cluster_solver.py::calculate_velocity_uet`; `Code/03_Research/Research_Cluster_Virial.py` | `M` in kg; `R` in m; `a0` in m/s^2; output m/s | `G` source-locked; `a0 = 0.8e-10 m/s^2` is a benchmark/heuristic acceleration anchor | heuristic bridge | secondary model diagnostic, not primary artifact gate | Hidden calibration of `a0` can mimic MOND-like success without independent prediction. | Record `a0` provenance and run multiple cluster rows without retuning. |
| `CL15-HALO-FISHER` | `I_halo = kappa |grad C|^2 / (C + 1e-6)` | `Code/01_Engine/Engine_Cluster_Dynamics.py::compute_halo` | `C` is normalized baryonic grid mass in model units; `grad C` per grid spacing; `I_halo` model-unit field | `kappa` is UET parameter; `1e-6` is numerical regularizer | heuristic bridge | engine diagnostic only | Grid units and normalization are not mapped to physical density units. | Add dimensional grid metadata and compare against mass/lensing profiles. |
| `CL15-EFFECTIVE-MASS` | `M_total = sum(C) + sum(I_halo)` and `V_virial = sqrt(M_total)` | `Code/01_Engine/Engine_Cluster_Dynamics.py::step` | model-unit mass and velocity; not SI-calibrated | topic-derived model state | open/heuristic | engine health metric only | Model-unit velocity can be mistaken for physical velocity dispersion. | Add explicit nondimensionalization or remove from physical claims. |
| `CL15-DRAG-TOY` | `x_gas += v_gas dt`, `x_halo += v_halo dt`, with gas velocity reduced near collision center | `Code/03_Research/Research_BulletCluster_Offset.py` | `x`, `v`, `dt` in model units; no kpc or km/s calibration | `drag_gas = 0.05`, `drag_halo = 0.0` are heuristic toy parameters | qualitative diagnostic | primary artifact formula path | Positive offset can be produced by construction if halo drag is fixed to zero. | Replace with kpc-calibrated two-component collision model or mark as qualitative only. |
| `CL15-OFFSET-SIGN-GATE` | `status = WARN if model_offset > 0 and observed_offsets_kpc > 0` | `Code/03_Research/Research_BulletCluster_Offset.py` | observed offset in kpc; model offset in dimensionless model units | observed offsets are source-labeled benchmark inputs; model offset is toy output | checked local diagnostic | primary artifact gate | Sign-only agreement cannot validate offset magnitude, lensing amplitude, or mass model. | Add kpc calibration and thresholds against 480 kpc and 120 kpc offsets. |
| `CL15-JWST-FORMATION` | early-cluster/galaxy formation comparison paths | `Code/03_Research/Research_JWST_Formation_Rate.py` | redshift, mass, formation timing; unit audit still incomplete | mixed source labels and model parameters | open | excluded from primary verifier | JWST formation claims can leak into cluster dynamics without a source-backed artifact. | Audit separately before using in README or dependency map. |

## Claim Boundary

- Supported now: a source-labeled Bullet Cluster coordinate working copy is read by the verifier, and the toy model records a qualitative separation-sign diagnostic.
- Not supported now: prediction of the 480 kpc / 120 kpc offsets, Bullet Cluster lensing-map reproduction, or a general replacement for cluster dark matter.
- Downstream use: `0.0`, `0.1`, `0.3`, `0.13`, `0.23`, and `0.26` may cite this topic only as a cluster diagnostic with unresolved dimensional calibration.

## Audit Link

- Primary artifact: `Result/artifacts/0_15_cluster_dynamics_verification.json`
- Core audit report: `docs/meta/core_research_hardening_audit.md`
