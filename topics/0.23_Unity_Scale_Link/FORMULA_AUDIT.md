# Formula Audit: 0.23_Unity_Scale_Link

Audit status: reviewed registry, replacing the bootstrap scaffold.

Scope note: this topic is a scale-link and dependency-control topic. It is not allowed to claim grand unification from shared notation alone. Current evidence can support structural similarity, failure mapping, and scale-dependent parameter hypotheses.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T23-001` | `Omega[C] = V(C) + kappa |grad C|^2 + beta C I` | `Code/01_Engine/Engine_Derivation.py`; `Code/01_Engine/Engine_Unity_Scale.py::compute_omega` | `C` = normalized field; `grad C` = per index/dx; `kappa,beta,alpha,gamma,C0` = model coefficients; `Omega` = normalized functional value | UET master-equation structure; depends on `docs/core/uet_master_equation.py` | framework hypothesis, not proof | Primary structural common-form check | Same symbol can hide incompatible units across domains | Define per-domain dimensionalization and normalization contracts before comparing Omega magnitudes |
| `T23-002` | `V(C) = alpha (C-C0)^2 + gamma C^4` or related core potential form | `docs/core/uet_master_equation.py`; `Engine_Unity_Scale.py` | `C` normalized dimensionless field; `alpha,gamma,C0` coefficients | core UET implementation | implemented model term | Drives Omega values in cross-domain tests | Potential form may differ from derivation text `(alpha/2)C^2 + (gamma/4)C^4` | Reconcile derivation text with actual core implementation |
| `T23-003` | generated normalized fields `C_norm = (C-min(C))/(max(C)-min(C)+1e-9)` | `Engine_Unity_Scale.py::generate_field`; `compute_omega` | `C_norm` dimensionless; original units discarded | topic-local preprocessing convention | implementation convention | Makes heterogeneous domains computable by one engine | Normalization removes physical scale, so it cannot prove scale unity by itself | Record raw-unit meaning and justify each normalization per domain |
| `T23-004` | auto-kappa balance `argmin_k mean(|potential - k grad(C)^2|)` | `Code/02_Proof/Proof_Auto_Kappa.py` | `k` dimensionless sweep; `potential=(C-C0)^2`; `grad` per arbitrary `dx=0.1` | topic-local heuristic | exploratory heuristic | Tests whether shape implies a preferred kappa | Expected ranges are hand-coded and `dx` arbitrary | Convert to diagnostic only or replace with a source-backed calibration objective |
| `T23-005` | kappa running points `{Planck:0.50, Nuclear:0.57, Atomic:1.40, Human:0.10, Galaxy:0.10}` over length scale | `Code/02_Proof/Proof_Kappa_Running.py`; README scale table | `L` = m; `kappa` = model coefficient | mixed: theoretical anchors, topic calibrations, heuristic labels | open hypothesis | Visualizes scale-dependent parameter idea | Points are not a fitted beta function and cannot prove renormalization flow | Add provenance per point and fit/test a stated running model with uncertainty |
| `T23-006` | fixed-kappa falsification `B_pred = B_exp (kappa_gal/kappa_nuc)^2` | `Code/03_Research/Falsification_Analysis.py` | `B` = MeV; `kappa_gal=0.10`; `kappa_nuc=0.57`; `B_exp=2.2246 MeV` | deuteron benchmark plus topic calibration constants | useful falsification heuristic | Shows fixed parameter unity fails for nuclear binding | Scaling law is simplified and not a substitute for Topic `0.5` verifier | Link directly to `0.5` formula audit/artifact and propagate its status |
| `T23-007` | beta discontinuity factor `beta_ew / beta_gal = 1.0 / 0.05` | `Code/03_Research/Falsification_Analysis.py` | beta values dimensionless topic coefficients | topic calibration constants | falsification heuristic | Records electroweak/cosmic parameter mismatch | Values are asserted, not source-locked in this topic | Link to `0.6` verifier and define calibration source |
| `T23-008` | cross-domain Omega ordering: `Omega(seizure) < Omega(normal)` under `kappa=0.1,beta=0.05` | `Code/03_Research/Research_Cross_Domain.py` | Omega dimensionless normalized score; neural fields synthetic | synthetic generator + local engine | exploratory model-shape test | Primary verifier metric for transfer-like behavior | Synthetic neural fields make the test circular if stated as external prediction | Replace with real EEG dataset or label strictly as simulation |
| `T23-009` | economy volatility comparison using SP500 rolling windows and Omega scores | `Code/03_Research/Research_Cross_Domain.py`; `data/03_Research/economy/SP500_yahoo_real.csv`; `docs/data/external/finance/yahoo_snapshots/0_23_unity_scale_link/source_manifest.json` | price series in local CSV; log returns; rolling std; Omega dimensionless | source-referenced Yahoo-style local snapshot | exploratory local-data comparison | Secondary verifier metric | Original retrieval timestamp, query parameters, adjusted-close policy, and upstream response hash are still missing | Add reproducible downloader/query metadata and upstream response hash |
| `T23-010` | dependency bridge from `0.13`: information-energy lower-bound constraints feed beta/scale interpretation | `METHOD.md`; `README.md`; `0.13_Thermodynamic_Bridge` | depends on `E_min = k_B T ln 2` and thermodynamic bridge status | inherited from Topic `0.13` | dependency constraint | Prevents `0.23` from exceeding `0.13` evidence class | If `0.13` is WARN/source-lock open, `0.23` cannot claim paper-ready scale unification | Add dependency matrix and inherit blockers explicitly |

## Claim Guardrails

| Claim area | Maximum current claim class | Reason |
| :-- | :-- | :-- |
| Shared functional form | `C` | The same code can compute Omega across normalized fields, but unit contracts and dimensionalization are incomplete. |
| Parameter unity | `E/D` | Falsification script shows fixed `kappa` fails across nuclear/cosmic regimes. |
| Scale-dependent kappa/running | `D` | Current running curve uses hand-selected points without fitted beta function or uncertainty. |
| Cross-domain prediction | `D` | Neural/galaxy fields are synthetic; economy data is local snapshot without source lock. |
| Dependency on thermodynamic bridge | `C/D` | Inherits `0.13` WARN status and cannot outrank it. |

## Required Follow-Up

- Source-lock every kappa/beta calibration to its topic artifact (`0.5`, `0.6`, `0.13`, galaxy/cosmology topics).
- Replace synthetic neural generator tests with a real EEG/physiology dataset or keep them explicitly simulation-only.
- Replace Yahoo-style local-source metadata with reproducible finance retrieval logs, query parameters, and upstream response hashes.
- Define one explicit running-coupling model before claiming renormalization-like behavior.
- Keep `0.23` as a dependency map and structural scale-link test until data and formula dependencies are stronger.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
