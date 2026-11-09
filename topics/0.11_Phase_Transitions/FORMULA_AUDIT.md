# Formula Audit: 0.11 Phase Transitions

## Scope

This registry covers the current phase-transition calculation paths: spectral
Cahn-Hilliard evolution, chemical potential, free-energy/order-parameter diagnostics, BEC
critical temperature, 3D Ising critical-exponent comparison, and competitor/test solvers. It
separates standard benchmark relations from UET heuristic projection claims and numerical
demonstrations.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `PT-CH-EVOLUTION` | `dC/dt = M nabla^2(delta F/delta C)` | `Engine_Phase.step` | `C` dimensionless concentration/order field; `M` mobility proxy; `dt` simulation time step; grid units normalized | `checked_local_reference` Cahn-Hilliard form | `checked local numerical relation` | engine diagnostic | Numerical stability depends on grid, `dt`, `kappa`, and noise; visual domains are not a physical proof by themselves. | Add convergence sweep over grid size, seed, `dt`, and `kappa`. |
| `PT-FREE-ENERGY` | `F[C] = int [alpha/2 C^2 + gamma/4 C^4 + kappa/2 |grad C|^2] dV` | `Engine_Phase.compute_chemical_potential` comments and implementation | `alpha`, `gamma`, `kappa` dimensionless in normalized solver; `C` dimensionless | `topic_derived_relation` / Cahn-Hilliard benchmark structure | `heuristic bridge` | diagnostic | Solver uses normalized parameters, so physical material energy units are not established. | Document nondimensionalization and map to a material dataset if making physical claims. |
| `PT-CHEM-POTENTIAL` | `mu = alpha C + gamma C^3 - kappa nabla^2 C` | `Engine_Phase.compute_chemical_potential` | `mu` normalized potential; `C` dimensionless; `nabla^2` normalized grid operator | `checked_local_reference` | `checked local numerical relation` | engine diagnostic | Sign or FFT convention errors alter phase separation. | Add unit tests comparing FFT Laplacian to finite-difference reference. |
| `PT-SPECTRAL-UPDATE` | `C_new_hat = (C_hat - dt M k^2 NL_hat + noise_hat)/(1 + dt M kappa k^4)` | `Engine_Phase.step` | Fourier amplitudes dimensionless; `k` normalized wave number | `topic_derived_relation` from semi-implicit CH update | `checked local numerical relation` | engine diagnostic | Incorrect implicit denominator can create artificial stability or growth. | Record seed, initial condition, and spectral diagnostics in artifact. |
| `PT-ORDER-PARAMETER` | `order = mean(abs(C))` | `Engine_Phase.get_extra_metrics`; `Proof_Order_Parameter.py` | dimensionless order proxy | `topic_derived_relation` | `diagnostic proxy` | proof/test diagnostic | Threshold such as `order > 0.7` is simulation-specific, not universal phase-transition proof. | Calibrate threshold against known demixing simulations or mark as internal-only. |
| `PT-DOMAIN-COUNT` | zero-crossing count over sign of `C` | `Engine_Phase._count_domains` | count dimensionless | `topic_derived_relation` | `diagnostic proxy` | visualization/diagnostic | Sensitive to noise and grid resolution; not a robust domain morphology metric. | Replace or supplement with structure factor / correlation length. |
| `PT-BEC-TC` | `Tc = (hbar omega/k_B) * (N/zeta(3))^(1/3)` | `Engine_Phase.compute_bec_tc` | `omega` rad/s; `N` count; output K | `source_locked_physics_constant` plus standard trapped-BEC relation | `checked local benchmark relation` | diagnostic only | Not used by primary phase-transition gate; cannot support broad transition claims. | Add explicit BEC verifier if this becomes claim-bearing. |
| `PT-BETA-UET` | `beta_UET ~= 1/D_eff`; current data uses `0.333` | `Research_Critical_Exponents.py`; `critical_exponents.json` | `beta` dimensionless critical exponent | `heuristic_bridge` | `heuristic bridge with internal benchmark pass` | primary verifier gate | A close beta match does not derive `gamma`, `nu`, scaling relations, or full RG universality. | Extend verifier to `gamma`, `nu`, and scaling laws; source-lock benchmark references. |
| `PT-BETA-ERROR` | `relative_error = abs(beta_UET - beta_exp)/beta_exp * 100` | `Research_Critical_Exponents.py` | percent | `topic_derived_relation` | `identity` | primary verifier metric | If only beta is tested, README must not claim full phase-transition theory closure. | Keep claim to selected 3D Ising/liquid-gas beta exponent until broader gates exist. |

## Current Formula Boundary

- The strongest current result is a selected beta-exponent internal benchmark.
- Spectral Cahn-Hilliard simulation demonstrates a normalized mechanism but is not yet mapped
  to physical material units.
- Order emergence and symmetry-breaking language must remain model/diagnostic wording unless
  backed by broader exponent, morphology, and material-data gates.
## Wave 5 Spatial-Coupling Candidate Addendum

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `PT-UET-LEGACY-INFO` | `Omega_info = beta C I`; `dC/dt += -beta I` | `docs/core/uet_master_equation.py::information_coupling`; `information_dynamics_source` | `C` normalized order field; `I` normalized information field; units remain normalized/proxy in topic 0.11 | `heuristic_bridge` | `legacy local operator` | compatibility baseline | Local source can act without requiring mass/interface structure, so it can stay spatially blind. | Keep as legacy comparator only unless a derivation requires it. |
| `PT-UET-SPATIAL-INFO-CANDIDATE` | `Omega_info = 0.5 beta C^2 I`; `dC/dt += -beta C I` | `information_coupling(..., operator_mode="spatial_coupled_v1")`; `information_dynamics_source` | `C` normalized order field; `I` normalized information field; unit closure open | `heuristic_bridge` | `candidate heuristic bridge` | diagnostic gate input | Wrong coefficient/sign can create artificial damping or noise response without physical closure. | Derive or reject the multiplicative information term before stronger claims. |
| `PT-UET-SPATIAL-GAME-CANDIDATE` | `V_game = beta_U |grad C|^2`; dynamics candidate `F_game = c_kpz V_game` | `game_theory_potential`; `game_theory_force` | `grad C` normalized grid gradient; `beta_U` strategic boost; units proxy/open | `heuristic_bridge` | `candidate diagnostic-only` | spatial operator gate | Passing interface sensitivity does not imply RG closure or universality shift. | Add unit closure and compare against accepted interface-growth/scaling references. |
| `PT-SPATIAL-SCALING-GATE` | fit `log(<|C|>) = beta log(Tc-T)+b` for baseline, legacy, and spatial lanes | `Research_Spatial_Coupling_Scaling.py`; `0_11_spatial_coupling_scaling.json` | beta dimensionless; synthetic normalized TDGL grid | `topic_derived_relation` | `diagnostic artifact` | hardening gate | Current Wave 5 result remains near mean-field: baseline `0.4912`, legacy `0.5050`, spatial `0.5081`. | Keep universality claims blocked until `universality_shift_gate` passes with documented derivation. |
| `PT-SPATIAL-COEFFICIENT-SENSITIVITY` | sweep `spatial_information_coupling` and `spatial_game_coupling`; fit beta per case | `Research_Spatial_Coupling_Sensitivity.py`; `0_11_spatial_coupling_sensitivity.json` | beta dimensionless; reduced synthetic TDGL grid | `topic_derived_relation` | `diagnostic artifact` | blocker triage | Wave 6 found no tested coefficient-only case near 3D Ising beta; best beta `0.4729`, range `0.4729` to `0.5243`. | Stop treating coefficient strength as the likely repair; revise operator form or estimator. |
| `PT-CORRELATION-LENGTH-DIAGNOSTIC` | connected autocorrelation axis crossing proxy for `xi`; fit `xi ~ (Tc-T)^(-nu_proxy)` | `Research_Correlation_Length_Diagnostics.py`; `0_11_correlation_length_diagnostics.json` | `xi` grid units; `nu_proxy` dimensionless diagnostic | `topic_derived_relation` | `diagnostic artifact` | estimator gate | Wave 7 found weak spatial correlation growth: spatial `nu_proxy ~= 0.0324`, `xi_near/xi_far ~= 1.0668`. | Add finite-size/correlation-length-aware scaling before stronger universality claims. |
| `PT-FINITE-SIZE-SCALING-DIAGNOSTIC` | sweep grid sizes and compare `xi/L`, Binder-style proxy, and lane separation | `Research_Finite_Size_Scaling_Diagnostics.py`; `0_11_finite_size_scaling_diagnostics.json` | `xi/L` dimensionless; Binder proxy dimensionless | `topic_derived_relation` | `diagnostic artifact` | finite-size gate | Wave 8 found Binder-style spread but `xi/L` too small and no spatial-vs-baseline separation. | Redesign finite-size window and operator form before stronger claims. |
| `PT-CRITICAL-WINDOW-RELAXATION-DIAGNOSTIC` | sweep closer-to-Tc temperatures and step counts; compare spatial/baseline `xi/L` | `Research_Critical_Window_Relaxation_Diagnostics.py`; `0_11_critical_window_relaxation_diagnostics.json` | `xi/L` dimensionless; steps synthetic time | `topic_derived_relation` | `diagnostic artifact` | window/relaxation gate | Wave 9 found max spatial `xi/L = 0.0737` and no gain from longer relaxation. | Stop treating runtime/window extension alone as the likely repair; revise dynamics/operator form. |
| `PT-OPERATOR-FORM-REQUIREMENT-GATE` | aggregate Waves 5-9 into blocked repair paths and v2 design requirements | `Research_Operator_Form_Requirement_Gate.py`; `0_11_operator_form_requirement_gate.json` | gate statuses and thresholds are dimensionless artifact fields | `topic_derived_relation` | `design requirement gate` | operator-revision controller | Wave 10 keeps coefficient-only, finite-size signal, and critical-window paths blocked for the current operator family. | Design a new opt-in operator with nonlocal, conserved, or scale-dependent behavior before rerunning scaling claims. |
| `PT-UET-SPATIAL-V2-CANDIDATE` | activity `= |grad C|^2 + a(nonlocal(C)-C)^2`; game force `= lambda nabla^2 V_game`; info source `~ -beta C I activity` | `uet_master_equation.py`; `Research_Spatial_Coupled_V2_Diagnostic.py`; `0_11_spatial_coupled_v2_diagnostic.json` | normalized `C`, `I`, `xi/L`; v2 coefficients are heuristic/proxy | `heuristic_bridge` | `candidate diagnostic-only` | v2 availability/safety/stability gate | Wave 11 passes core/safety/stability but blocks correlation growth and lane separation (`max_xi/L = 0.0733`). | Revise nonlocal/conserved dynamics or derive stronger operator before finite-size claims. |
| `PT-UET-SPATIAL-V2-ABLATION` | compare v2 information-only, game-only, full, short-memory, and long-memory profiles against baseline `xi/L` | `Research_Spatial_Coupled_V2_Component_Ablation.py`; `0_11_spatial_coupled_v2_component_ablation.json` | normalized `xi/L`; profile coefficients are heuristic/proxy | `topic_derived_relation` | `diagnostic ablation` | component blocker triage | Wave 12 found all tested v2 profiles below baseline; best improvement `-0.0038`. | Stop treating current v2 components as a likely repair; design a different operator structure or derivation. |
| `PT-MODEL-C-CONSERVED-ORDER-DIAGNOSTIC` | `dC/dt = M nabla^2(delta F/delta C)` via topic Cahn-Hilliard engine | `Engine_Phase.py`; `Research_Model_C_Conserved_Order_Diagnostic.py`; `0_11_model_c_conserved_order_diagnostic.json` | normalized 2D `C`, grid units, `xi` proxy; no material units | `checked_local_reference` plus topic diagnostic | `mechanism repair direction` | conserved-order mechanism gate | Wave 13 passes mass conservation, domain growth, and operator distinction gates, but remains normalized 2D mechanism evidence. | Integrate as opt-in core candidate or run finite-size/exponent gates before stronger claims. |
| `PT-CONSERVED-ORDER-CORE-CANDIDATE` | core opt-in `conserved_order_v1`: `dC/dt = -M nabla^2(force)` where `force = -delta Omega/delta C` | `uet_master_equation.py`; `Research_Conserved_Order_Core_Candidate.py`; `0_11_conserved_order_core_candidate.json` | normalized `C`, grid units, explicit finite-difference helper; no material units | `heuristic_bridge` from Model C diagnostic | `core candidate diagnostic-only` | core integration and mass-conservation gate | Wave 14 passes core exposure, legacy compatibility, and mass conservation, but blocks mechanism response (`xi` growth `0.87` vs legacy `1.47`). | Tune/integrate a spectral or semi-implicit conserved core path before finite-size claims. |
| `PT-CONSERVED-ORDER-NUMERICS-GAP` | stiffness proxy `dt * kappa * (pi / dx)^4` comparing Wave 13 spectral settings to Wave 14 explicit core settings | `Research_Conserved_Order_Numerics_Gap.py`; `0_11_conserved_order_numerics_gap.json` | dimensionless explicit-stability proxy; normalized grid units | `topic_derived_relation` | `diagnostic requirement gate` | next-operator controller | Wave 15 blocks explicit core viability: Wave 13-like stiffness proxy `32685` versus Wave 14 explicit proxy `0.097`, ratio `335544`. | Implement a spectral or semi-implicit conserved-order core candidate before coefficient tuning or finite-size claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-CORE-CANDIDATE` | core opt-in semi-implicit update `C_hat_new = (C_hat + dt M k^2 F_non_grad_hat)/(1 + dt M kappa k^4)` | `uet_master_equation.py::spectral_conserved_order_step`; `Research_Conserved_Order_Spectral_Core_Candidate.py`; `0_11_conserved_order_spectral_core_candidate.json` | normalized `C`, FFT grid units, `xi` proxy; no material units | `heuristic_bridge` from Wave 13 topic engine | `core candidate diagnostic-only` | Wave 15 repair and topic-engine bridge gate | Wave 16 passes core bridge gates with max topic-engine delta `2.89e-12` and median `xi` growth `30.49`. | Run finite-size/exponent scaling gates before stronger dynamics or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-SCALING` | finite-size sweep fits `log(<|C|>)` and `log(xi)` versus `log(Tc-T)` for `conserved_order_spectral_v1` | `Research_Conserved_Order_Spectral_Scaling.py`; `0_11_conserved_order_spectral_scaling.json` | normalized 3D lattice units; `xi/L`, Binder proxy, beta and nu proxies | `topic_derived_relation` | `diagnostic finite-size/exponent gate` | claim-boundary controller | Wave 17 passes stability/coverage but blocks correlation window (`max xi/L = 0.145`) and universality exponent (median beta `1.77`). | Improve finite-size/equilibration/scaling-window design before stronger dynamics or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-WINDOW-REPAIR` | targeted relaxation and kappa sweeps compare `xi/L` against order-signal preservation | `Research_Conserved_Order_Spectral_Window_Repair.py`; `0_11_conserved_order_spectral_window_repair.json` | normalized 3D lattice units; `xi/L`, order amplitude, kappa proxy | `topic_derived_relation` | `diagnostic repair triage` | next-window controller | Wave 18 finds relaxation-only max `xi/L = 0.113`; kappa max `xi/L = 0.377` only at order `0.000377`, below signal floor. | Design a window that preserves order signal while lifting `xi/L`, or revise the scaling estimator/operator before stronger claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-SPINODAL-WINDOW` | targeted positive spinodal-margin cases compare `xi/L` and order-signal preservation across seed replicates | `Research_Conserved_Order_Spectral_Spinodal_Window.py`; `0_11_conserved_order_spectral_spinodal_window.json` | normalized 3D lattice units; `xi/L`, order amplitude, seed replicate margin | `topic_derived_relation` | `diagnostic window candidate` | seed-margin controller | Wave 19 finds one viable order-preserving `xi/L` case (`xi/L = 0.204`, order `0.0126`) but target seed pass fraction is `0.25`. | Replicate the window across seeds and grid sizes before exponent or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-SEED-MARGIN` | target spinodal window at `T=0.900`, `kappa=0.100`, `steps=4000` compares seed replicate `xi/L` and order floors | `Research_Conserved_Order_Spectral_Seed_Margin.py`; `0_11_conserved_order_spectral_seed_margin.json` | normalized 3D `L=16` lattice units; `xi/L`, order amplitude, seed replicate pass fraction | `topic_derived_relation` | `diagnostic seed-margin repair` | finite-size replication controller | Wave 20 passes the target seed-margin gate (`4/4` seeds, min `xi/L = 0.2004`, min order `0.0505`) but remains single-grid. | Replicate over grid sizes before exponent or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-FINITE-SIZE-REPLICATION` | replicate the Wave 20 target window over `L=8,12,16` and two seed sets | `Research_Conserved_Order_Spectral_Finite_Size_Replication.py`; `0_11_conserved_order_spectral_finite_size_replication.json` | normalized 3D lattice units; `xi/L`, order amplitude, grid/seed pass fractions | `topic_derived_relation` | `diagnostic finite-size replication gate` | grid/seed replication controller | Wave 21 passes coverage but blocks replication: `L=16` fresh seeds pass only `1/3` and min `xi/L = 0.1944`. | Revise finite-size/window scaling or estimator before exponent or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-L16-RELAXATION-REPAIR` | test `L=16` fresh seeds at `4000`, `4800`, and `5600` steps for `xi/L` repair | `Research_Conserved_Order_Spectral_L16_Relaxation_Repair.py`; `0_11_conserved_order_spectral_l16_relaxation_repair.json` | normalized 3D `L=16` lattice units; `xi/L`, order amplitude, step-group pass fractions | `topic_derived_relation` | `diagnostic relaxation repair gate` | next-window/estimator controller | Wave 22 blocks relaxation-only repair: all step groups pass only `1/3` fresh seeds while order stays above floor. | Revise estimator or finite-size/window scaling before exponent or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-L16-ESTIMATOR-SENSITIVITY` | sweep axis-autocorrelation crossing thresholds for the same `L=16` fresh-seed fields | `Research_Conserved_Order_Spectral_L16_Estimator_Sensitivity.py`; `0_11_conserved_order_spectral_l16_estimator_sensitivity.json` | normalized 3D `L=16` lattice units; `xi/L`, autocorrelation threshold, crossing/saturation counts | `topic_derived_relation` | `diagnostic estimator-sensitivity gate` | estimator-design controller | Wave 23 finds the default `e^-1` threshold reproduces Wave 22, while lower thresholds make `9/9` cases pass without saturation. | Derive, calibrate, or replace the correlation estimator before exponent or universality claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-L16-STRUCTURE-FACTOR-ESTIMATOR` | threshold-free characteristic length `xi_sf = 2*pi / sqrt(sum(S(k) k^2) / sum(S(k)))` over nonzero FFT modes | `Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py`; `0_11_conserved_order_spectral_l16_structure_factor_estimator.json` | normalized 3D `L=16` lattice units; structure-factor power, RMS wave number, `xi/L` | `topic_derived_relation` | `diagnostic estimator candidate` | finite-size calibration controller | Wave 24 passes the L16 margin but warns on domain-scale risk: structure-factor max `xi/L = 0.5799`. | Calibrate over multiple grid sizes before exponent or universality claims. |
| `PT-CH-FINITE-K-ACCEPTANCE-POLICY` | strict row policy for `xi_peak = 2*pi/q_peak`: status OK, Wave 48 pass, not low-window-edge, window power >= `0.05`, low-mode power <= `0.90`, `0.10 <= xi/L < 0.75`, order >= `0.005` | `Research_Structure_Factor_CH_Finite_K_Acceptance_Policy_Gate.py`; `0_11_structure_factor_ch_finite_k_acceptance_policy_gate.json` | normalized `C`, `q`, `xi/L`, and per-row policy flags; source coefficient units remain unmapped | `topic_derived_relation` plus `heuristic_bridge` policy | `acceptance policy preflight` | claim-boundary gate | Wave 49 accepts only `6/18` rows and only `L20`; no multi-grid finite-size coverage exists. | Repair field normalization/source coefficient policy or run an accepted multi-grid candidate before exponent claims. |
| `PT-CH-FINITE-K-EXTENDED-GRID-COVERAGE` | apply the unchanged Wave 49 policy to added `L24/L28` rows and combine accepted rows with prior `L20` rows | `Research_Structure_Factor_CH_Finite_K_Extended_Grid_Coverage_Probe.py`; `0_11_structure_factor_ch_finite_k_extended_grid_coverage_probe.json` | normalized `C`, `q`, `xi/L`, grid size, and per-row policy flags; source coefficient units remain unmapped | `topic_derived_relation` plus coverage probe | `coverage probe only` | hardening gate | Wave 50 passes accepted multi-grid coverage with `L20:6`, `L24:2`, `L28:2`, but field normalization and source coefficients remain unresolved. | Resolve centered-C source equivalence and CH coefficient mapping before estimator acceptance or exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-STRUCTURE-FACTOR-MULTIGRID` | replicate `xi_sf = 2*pi / sqrt(sum(S(k) k^2) / sum(S(k)))` over `L=8,12,16` and two seed sets | `Research_Conserved_Order_Spectral_Structure_Factor_Multigrid_Calibration.py`; `0_11_conserved_order_spectral_structure_factor_multigrid_calibration.json` | normalized 3D lattice units; structure-factor `xi/L`, absolute `xi`, grid-size trend | `topic_derived_relation` | `diagnostic calibration gate` | domain-scale saturation controller | Wave 25 passes margin replication but blocks calibration: median `xi/L` is `0.997` at `L=8`, `0.717` at `L=12`, and `0.566` at `L=16`. | Add larger-grid/source-backed estimator calibration or derived acceptance rule before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-STRUCTURE-FACTOR-L20-PROBE` | rerun `xi_sf` on `L=20` and extend the median trend from Wave 25 | `Research_Conserved_Order_Spectral_Structure_Factor_L20_Probe.py`; `0_11_conserved_order_spectral_structure_factor_l20_probe.json` | normalized 3D lattice units; L20 `xi/L`, absolute `xi`, estimator ratio to axis threshold | `topic_derived_relation` | `diagnostic larger-grid probe` | acceptance-rule controller | Wave 26 passes L20 relief (`median xi/L = 0.4347`) but blocks acceptance-rule use; L20 absolute xi is below L16 (`ratio = 0.9599`) and estimator reconciliation is still missing. | Create source-backed or derived acceptance rule before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-STRUCTURE-FACTOR-ACCEPTANCE-RULE` | preflight rule excludes domain-scale grids, requires >=3 admissible grids, absolute-`xi` consistency, and estimator reconciliation | `Research_Structure_Factor_Acceptance_Rule_Gate.py`; `0_11_structure_factor_acceptance_rule_gate.json` | normalized 3D lattice units; `xi_sf/L`, absolute `xi_sf`, grid subset, estimator ratio | `topic_derived_relation` | `heuristic preflight, not physics acceptance` | claim-boundary gate | Wave 27 defines the rule but current evidence fails: `L=8` excluded, `L20/L16 = 0.9599`, and estimator ratio `2.6261` is unreconciled. | Repair absolute-length consistency or add a source-backed estimator benchmark before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-ESTIMATOR-RECONCILIATION` | compare `xi_sf / xi_axis_lower` at L16 and L20; candidate calibration factor is the observed ratio average | `Research_Structure_Factor_Estimator_Reconciliation_Gate.py`; `0_11_structure_factor_estimator_reconciliation_gate.json` | normalized grid units; estimator ratio dimensionless; calibration factor unaccepted | `topic_derived_relation` | `diagnostic reconciliation only` | estimator-calibration gate | Wave 28 finds stable ratio drift (`0.0219`) but blocks magnitude/provenance and absolute-length trend. | Source-back or derive calibration, or repair the window/dynamics before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-CALIBRATION-SOURCE-SUPPORT` | scan local refs for structure-factor/second-moment/Fourier/finite-size estimator support before accepting calibration | `Research_Structure_Factor_Calibration_Source_Support_Gate.py`; `0_11_structure_factor_calibration_source_support_gate.json` | source hashes, keyword matches, DOI/URL candidates; no physical units | `source_support_triage` | `source gap diagnostic` | source-packaging gate | Wave 29 finds zero local text-source matches for all required estimator-support classes. | Package primary estimator sources and formula boundaries before calibration or exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-SOURCE-MANIFEST` | package primary estimator-source candidates with DOI/URL, formula role, and claim boundary | `structure_factor_estimator_source_manifest.json`; `Research_Structure_Factor_Source_Manifest_Gate.py`; `0_11_structure_factor_source_manifest_gate.json` | source metadata only; no estimator units accepted | `source_support_triage` | `source manifest only` | source-review gate | Wave 30 passes metadata coverage but blocks local formula extraction and calibration acceptance. | Extract source formulas and map or reject the RMS inverse-k proxy before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-FORMULA-BOUNDARY` | source family uses `xi_2nd = sqrt(S(0)/S(k_min)-1)/(2 sin(k_min/2))`; current proxy uses all-nonzero-mode RMS inverse-k | `structure_factor_estimator_formula_boundary.json`; `Research_Structure_Factor_Formula_Boundary_Gate.py`; `0_11_structure_factor_formula_boundary_gate.json` | source formula in lattice units; current proxy remains normalized diagnostic units | `source_formula_boundary` plus `topic_derived_relation` | `source boundary extracted; current proxy mismatch` | formula-boundary gate | Wave 31 passes source formula extraction but blocks current proxy source-match and calibration acceptance. | Implement a lowest-mode second-moment estimator candidate or repair window/dynamics before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-LOWEST-MODE-CANDIDATE` | literal candidate `xi_2nd = sqrt(S(0)/S(k_min)-1)/(2 sin(k_min/2))` on L16/L20 conserved-order fields | `Research_Structure_Factor_Lowest_Mode_Candidate_Gate.py`; `0_11_structure_factor_lowest_mode_candidate_gate.json` | normalized lattice units; raw snapshot `S(0)` is not accepted susceptibility | `source_formula_candidate` | `candidate implemented; observable blocked` | replacement feasibility gate | Wave 32 passes implementation but blocks observable validity: `0/15` cases valid, all with `zero_mode_not_larger_than_lowest_mode`. | Derive an ensemble/connected susceptibility lane or repair window/dynamics before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-ENSEMBLE-SUSCEPTIBILITY-LANE` | compare `S0 = N Var_ensemble(mean(C))` against diagnostic `S0_proxy = mean(N Var_space(C))` for lowest-mode estimator use | `Research_Structure_Factor_Ensemble_Susceptibility_Lane_Gate.py`; `0_11_structure_factor_ensemble_susceptibility_lane_gate.json` | normalized lattice structure-factor units; spatial proxy not source-equivalent | `susceptibility_lane_diagnostic` | `source-closer lane blocked; proxy diagnostic-only` | S0 policy gate | Wave 33 blocks raw ensemble S0 because conserved mean gives `S0/S(k_min) < 1`; spatial proxy is numeric but not accepted. | Source-back a conserved-order susceptibility policy or finite-k/canonical estimator before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-ESTIMATOR-POLICY-SOURCE` | define required policies for conserved-order S0, finite-k/canonical replacement, and spatial-variance proxy exclusion | `structure_factor_estimator_policy_requirements.json`; `Research_Structure_Factor_Estimator_Policy_Source_Gate.py`; `0_11_structure_factor_estimator_policy_source_gate.json` | policy metadata; no estimator units accepted | `estimator_policy_source_triage` | `requirements defined; source support missing` | policy-source gate | Wave 34 passes policy requirement manifest but blocks conserved susceptibility and finite-k policy source gates. | Package policy-specific sources or choose window/dynamics repair before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-POLICY-SOURCE-CANDIDATES` | package fixed-magnetization/canonical and Cahn-Hilliard structure-factor source candidates for estimator-policy review | `structure_factor_estimator_policy_source_candidates.json`; `Research_Structure_Factor_Policy_Source_Candidate_Gate.py`; `0_11_structure_factor_policy_source_candidate_gate.json` | source metadata only; formula units not extracted | `source_candidate_packaging` | `candidates packaged; formula extraction blocked` | policy source-candidate gate | Wave 35 passes candidate manifest coverage but blocks formula extraction and policy acceptance. | Extract policy formula boundaries or choose window/dynamics repair before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-POLICY-FORMULA-BOUNDARY` | extract abstract-level fixed-magnetization/canonical and Cahn-Hilliard structure-factor boundaries for estimator-policy review | `structure_factor_estimator_policy_formula_boundary.json`; `Research_Structure_Factor_Policy_Formula_Boundary_Gate.py`; `0_11_structure_factor_policy_formula_boundary_gate.json` | abstract-level source boundaries; no accepted estimator units | `partial_formula_boundary` | `boundaries extracted; accepted formula blocked` | policy formula-boundary gate | Wave 36 passes boundary manifest and abstract boundary gates but blocks estimator acceptance and normalization mapping. | Extract full-text formulas or choose window/dynamics repair before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-FULL-TEXT-FORMULA-READINESS` | record rendered/abstract source-access readiness and extraction gaps before formula acceptance | `structure_factor_full_text_formula_extraction_readiness.json`; `Research_Structure_Factor_Full_Text_Formula_Readiness_Gate.py`; `0_11_structure_factor_full_text_formula_readiness_gate.json` | source-access metadata; no accepted estimator units | `formula_extraction_readiness` | `local math source blocked` | full-text formula readiness gate | Wave 37 passes readiness manifest but blocks local math source and accepted formula gates. | Localize TeX/PDF math sources or choose window/dynamics repair before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-SOURCE-ARCHIVE-LOCALIZATION` | verify temporary arXiv source archives and main TeX members for formula extraction | `structure_factor_source_archive_localization_manifest.json`; `Research_Structure_Factor_Source_Archive_Localization_Gate.py`; `0_11_structure_factor_source_archive_localization_gate.json` | source archive metadata; no accepted formulas | `source_archive_localization` | `archives localized; formula extraction blocked` | source archive localization gate | Wave 38 passes temporary archive and TeX member gates but blocks formula extraction and keeps repo archival policy warning-level. | Extract TeX formula fragments or define repo archival policy before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-TEX-FORMULA-FRAGMENTS` | extract exact TeX formula fragments for fixed-magnetization, canonical finite-size, and Cahn-Hilliard structure-factor policy review | `structure_factor_tex_formula_fragments.json`; `Research_Structure_Factor_Tex_Formula_Fragment_Gate.py`; `0_11_structure_factor_tex_formula_fragment_gate.json` | source TeX formulas; UET lattice units not mapped | `formula_fragment_extraction` | `fragments extracted; estimator policy blocked` | formula-source gate | Wave 43 now freshly extracts 19 fragments from 3 repo-archived source lanes and accepts no estimator policy. | Map fragments into UET normalization and finite-size admissibility, then accept/reject estimator replacement before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-SOURCE-ARCHIVE-POLICY` | record source archive policy, expected hashes, and candidate repo paths for the three formula source archives | `structure_factor_source_archive_policy.json`; `Research_Structure_Factor_Source_Archive_Policy_Gate.py`; `0_11_structure_factor_source_archive_policy_gate.json` | provenance metadata; repo archives restored | `source_archive_policy` | `policy recorded; estimator policy blocked` | source-provenance gate | Wave 45 restores repo archive availability for all `3/3` source archives; temporary cache remains non-authoritative. | Use restored archives for source-formula mapping; estimator-policy normalization still controls exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-ESTIMATOR-NORMALIZATION-MAP` | map restored source formula fragments to fixed-magnetization, canonical FSS, and Cahn-Hilliard finite-k estimator-policy lanes | `structure_factor_estimator_normalization_map.json`; `Research_Structure_Factor_Estimator_Normalization_Map_Gate.py`; `0_11_structure_factor_estimator_normalization_map_gate.json` | source formula lanes; UET lattice normalization not accepted | `estimator_policy_normalization_mapping_triage` | `candidate mapped; normalization/admissibility blocked` | policy-normalization gate | Wave 46 identifies the Cahn-Hilliard finite-k structure-factor lane as the strongest candidate family but keeps estimator acceptance blocked. | Derive UET lattice normalization, q-window admissibility, and accepted finite-k estimator implementation before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-CH-FINITE-K-PREFLIGHT` | declare CH finite-k preflight sections for centered `C`, FFT q-grid, source coefficients, `xi` extraction, and q-window admissibility | `structure_factor_ch_finite_k_normalization_preflight.json`; `Research_Structure_Factor_CH_Finite_K_Normalization_Preflight.py`; `0_11_structure_factor_ch_finite_k_normalization_preflight_gate.json` | lattice q-grid closed; field and coefficients open/proxy | `normalization_preflight_only` | `q-grid passes; estimator acceptance blocked` | unit/admissibility gate | Wave 47 passes Fourier convention only; field normalization warns and coefficient mapping, xi extraction, admissibility, and implementation remain blocked. | Implement a source-backed CH finite-k estimator candidate with explicit q-window diagnostics before exponent claims. |
| `PT-CONSERVED-ORDER-SPECTRAL-CH-FINITE-K-ESTIMATOR-CANDIDATE` | diagnostic candidate `xi_peak = 2*pi / q_peak`, where `q_peak = argmax S(q)` inside `q >= 2*q_min` finite-k window | `Research_Structure_Factor_CH_Finite_K_Estimator_Candidate.py`; `0_11_structure_factor_ch_finite_k_estimator_candidate_gate.json`; `gl_structure_factor_ch_finite_k_estimator_candidate_stats.csv` | centered UET `C` proxy; lattice q-grid closed; coefficient mapping open | `source_linked_estimator_candidate_only` | `candidate implemented; acceptance policy blocked` | implementation/q-window gate | Wave 48 passes implementation, q-window, domain-scale, and finite-size trend diagnostics, with median `xi/L = 0.5` and pass fraction `12/18`. | Resolve coefficient policy, field-normalization status, low-window-edge behavior, and acceptance thresholds before exponent claims. |

## Wave 5 Formula Boundary

The spatial-coupled operator is now available as an opt-in core candidate, but the current
scaling artifact does not support a claim that UET escapes mean-field behavior. The allowed
claim is limited to: a candidate spatial operator exists, its interface/zero-field gates pass,
and its current scaling result remains diagnostic-only.

## Wave 6 Coefficient Boundary

The coefficient sensitivity diagnostic narrows the blocker: changing the current candidate
coefficients alone did not shift the fitted beta exponent toward the 3D Ising target. The
allowed claim is limited to: coefficient-only tuning remains mean-field-like under the tested
grid, so the next hardening step needs a revised operator form, nonlocal/scale-dependent term,
or correlation-length-aware estimator.

## Wave 7 Estimator Boundary

The correlation-length diagnostic shows that the current synthetic temperature window does not
expose strong connected correlation-length growth. The allowed claim is limited to: beta-only
order-parameter fits are not enough for universality promotion, and the next hardening step
needs finite-size/correlation-length-aware scaling plus an operator form that separates from
baseline behavior.

## Wave 8 Finite-Size Boundary

The finite-size diagnostic shows that grid coverage and Binder-style proxy spread are not the
limiting issue by themselves. The current blocker is that near-critical `xi/L` remains too
small and the spatial lane does not separate from the TDGL baseline, so finite-size scaling
claims remain blocked.

## Wave 9 Relaxation Boundary

The critical-window relaxation diagnostic shows that moving closer to `Tc` and increasing
steps up to `2800` does not lift the spatial candidate out of local-correlation behavior. The
next hardening step must change the dynamics/operator form or add a better critical-growth
mechanism before rerunning finite-size claims.

## Wave 10 Operator-Form Requirement Boundary

The operator-form requirement gate aggregates the Wave 5-9 evidence chain into a design
controller. It does not validate a new equation. It records that the current `spatial_coupled_v1`
family has core-engine availability but still lacks coefficient, finite-size, critical-window,
and operator-separation support for a dynamics claim. The next hardening step must introduce a
new opt-in operator form with explicit unit/proxy boundaries, unit tests, formula-audit entries,
and fresh scaling artifacts before any claim is upgraded.

## Wave 11 Spatial-Coupled V2 Boundary

The first `spatial_coupled_v2` candidate moves beyond coefficient-only tuning by adding screened
nonlocal space-memory contrast and a conserved interface/game drive in the core engine. The
candidate passes availability, zero/uniform-field safety, conserved-force, and short-run
stability checks. It does not pass dynamics-claim gates: v2 `xi/L` remains below the baseline
lane in the first diagnostic, so the current evidence only supports continued operator-design
work.

## Wave 12 V2 Component-Ablation Boundary

The component-ablation diagnostic shows that the current v2 failure is not isolated to only one
combined lane. Information-only, game-only, full, short-memory, and long-memory profiles are all
stable and force-isolated, but none improves the correlation-length proxy over baseline. The
current v2 component family therefore remains diagnostic-only and should not be promoted by
recombining or retuning those components alone.

## Wave 13 Model C Boundary

The Model C diagnostic is the first post-v2 path that passes mechanism triage. It uses the topic
Cahn-Hilliard engine instead of a hidden standalone equation, conserves the mean order parameter,
and produces stronger domain/correlation growth than the nonconserved comparison lane. The
allowed claim is limited to: Model C is a plausible mechanism-level repair direction. It is not
yet a core UET operator replacement, 3D finite-size scaling result, material validation, or
universality-class proof.

## Wave 14 Conserved-Order Core Boundary

The `conserved_order_v1` core mode exposes a Model C-style conserved flow without changing
legacy defaults. It passes the core exposure, legacy compatibility, Wave 13 bridge, and mass
conservation gates. It does not yet pass the mechanism-response gate: the explicit finite-
difference core candidate produces weaker `xi` growth than the legacy core comparison in the
current diagnostic. The allowed claim is limited to opt-in availability and conservation, not
validated phase-transition dynamics.

## Wave 15 Numerics-Gap Boundary

The numerics-gap diagnostic does not introduce a new physics claim. It records that the Wave 14
explicit finite-difference core path is not the right next replacement path for reproducing the
Wave 13 spectral Cahn-Hilliard response: the Wave 13-like explicit stiffness proxy is far above
the declared viability threshold. The allowed claim is limited to a next-implementation
requirement: use a spectral or semi-implicit conserved-order core candidate before rerunning
finite-size, exponent, or universality gates.

## Wave 16 Spectral-Core Boundary

The `conserved_order_spectral_v1` core mode repairs the Wave 15 implementation blocker by
matching the topic spectral Cahn-Hilliard engine under normalized Wave 13-like settings while
preserving legacy defaults. The allowed claim is limited to: an opt-in core spectral bridge now
exists and passes mechanism/implementation gates. It is not yet a finite-size scaling result,
critical-exponent result, material validation, RG closure, or universal phase-transition proof.

## Wave 17 Spectral-Scaling Boundary

The spectral-scaling diagnostic is the first finite-size/exponent gate for `conserved_order_spectral_v1`.
It supports stability and coverage, but it does not support universality promotion: the near-critical
`xi/L` window remains below threshold and the fitted beta proxy is far from the 3D Ising benchmark.
The allowed claim is limited to: the next blocker is finite-size/equilibration/scaling-window design.

## Wave 18 Window-Repair Boundary

The window-repair diagnostic shows that the blocker is not fixed by simply running longer or moving
closer to `Tc`. Increasing `kappa` can raise `xi/L`, but the passing `xi/L` cases lose the order
signal below the declared floor. The allowed claim is limited to: the next repair must preserve
order amplitude while improving finite-size correlation structure, or revise the estimator/operator.

## Wave 19 Spinodal-Window Boundary

The spinodal-window diagnostic finds a narrow order-preserving `xi/L` candidate in the opt-in
`conserved_order_spectral_v1` path, but the target seed replicate margin is not robust. The allowed
claim is limited to: a candidate single-grid window exists for the next finite-size replication
pass. It is not a universality, material, RG-closure, or exponent-scaling result.

## Wave 20 Seed-Margin Boundary

The seed-margin diagnostic repairs the Wave 19 seed robustness blocker for the single-grid target
window by extending relaxation to `4000` steps. The allowed claim is limited to: the `L=16`
spinodal-window target now has enough seed-margin to justify finite-size replication. It is not
yet exponent scaling, material validation, RG closure, or universal phase-transition evidence.

## Wave 21 Finite-Size Replication Boundary

The finite-size replication diagnostic shows that the Wave 20 target is not robust across all
tested grid/seed combinations. Smaller grids pass, but `L=16` fresh seeds fall below the declared
`xi/L` threshold in two of three cases. The allowed claim is limited to: the current finite-size
window still needs redesign or estimator repair before exponent, material, RG, or universality
claims can be tested.

## Wave 22 L16 Relaxation-Repair Boundary

The `L=16` relaxation-repair diagnostic shows that longer single-grid runs are not enough to fix
the fresh-seed `xi/L` margin. Order amplitude increases with step count, but the pass fraction
stays `1/3` through `5600` steps. The allowed claim is limited to: relaxation-only repair is
blocked, so the next wave should adjust the estimator, finite-size window, or scaling design.

## Wave 23 L16 Estimator-Sensitivity Boundary

The estimator-sensitivity diagnostic shows that the Wave 22 `L=16` blocker is controlled by the
axis-autocorrelation crossing threshold. The default `e^-1` threshold exactly reproduces the
blocked result, while lower thresholds (`0.30`, `0.25`, `0.20`) make all 9 fresh-seed cases pass
without max-radius saturation. The allowed claim is limited to: the current `xi/L` gate needs
estimator derivation/calibration or replacement before any non-default threshold can support
finite-size, exponent, material, RG, or universality claims.

## Wave 24 L16 Structure-Factor Estimator Boundary

The structure-factor diagnostic adds a threshold-free characteristic-length proxy to the same
`L=16` fresh-seed fields. It confirms that the fields contain long-wavelength structure, but it
also flags finite-size/domain-scale risk: structure-factor `xi/L` ranges from `0.5549` to
`0.5799` on a single grid. The allowed claim is limited to: a candidate estimator exists for the
next multi-grid calibration wave. It is not an accepted critical correlation length, exponent
result, material validation, RG closure, or universality-class proof.

## Wave 25 Structure-Factor Multi-Grid Boundary

The multi-grid calibration diagnostic confirms that the Wave 24 structure-factor margin is
replicable, but this makes the limitation sharper rather than promoting the claim. Across
`L=8,12,16` and two seed sets, the estimator passes `18/18` cases while sitting near the domain
scale, with median `xi/L` decreasing from `0.997` to `0.566` as grid size increases. The allowed
claim is limited to: the current structure-factor RMS proxy is a reproducible long-wavelength
diagnostic that still needs larger-grid/source-backed calibration before finite-size, exponent,
material, RG, or universality claims.

## Wave 26 L20 Structure-Factor Probe Boundary

The L20 larger-grid probe narrows the Wave 25 blocker but does not clear it. The L20 cases
all pass the structure-factor margin and the median `xi/L` drops to `0.4347`, below the prior
domain-scale warning threshold. However, the absolute structure-factor length does not grow
with the grid (`L20/L16 = 0.9599`), the four-grid log slope is only `0.1110`, the prior L8
median remains domain-scale (`0.9972`), and the structure-factor/axis-lower estimator ratio
is `2.6261`. The allowed claim is limited to: the larger-grid symptom improved, but the
estimator still needs a source-backed or derived admissibility rule before finite-size,
exponent, material, RG, or universality claims.

## Wave 27 Acceptance-Rule Boundary

The acceptance-rule preflight turns the Wave 26 missing-rule blocker into explicit machine
checks. A candidate admissible subset (`L=12,16,20`) exists, but the full current chain still
fails the preflight because `L=8` is domain-scale, absolute `xi_sf` drops from `L=16` to `L=20`,
and the structure-factor/axis-lower estimator disagreement has no reconciliation rule. The
allowed claim is limited to: a conservative preflight rule exists and blocks exponent use of
the current estimator evidence. It is not an accepted critical length or universality result.

## Wave 28 Estimator-Reconciliation Boundary

The estimator-reconciliation gate shows the structure-factor/axis-lower ratio is stable enough
to study as a calibration-gap candidate (`2.6849` at L16, `2.6261` at L20; drift `0.0219`).
That does not accept the factor: the observed calibration remains source-free, the raw ratio
exceeds the unreconciled-ratio ceiling, and both estimators show declining absolute length from
L16 to L20. The allowed claim is limited to: disagreement is structured, not solved.

## Wave 29 Calibration Source-Support Boundary

The source-support gate checks whether the local reference package can justify accepting the
observed calibration factor or current RMS inverse-k proxy. It cannot: local text metadata has
zero matches for structure-factor, second-moment correlation length, Fourier estimator
definition, or finite-size admissibility. External primary candidates are recorded only as
candidates until packaged with formula roles and claim boundaries.

## Wave 30 Source-Manifest Boundary

The source-manifest gate packages three primary-source candidates with DOI/URL, formula role,
and claim boundary. This repairs metadata organization only. It keeps formula extraction,
local full-text support, and calibration acceptance blocked, so the current RMS inverse-k proxy
remains diagnostic-only.

## Wave 31 Formula-Boundary

The formula-boundary gate extracts the source-family second-moment estimator relation as a
zero-mode to lowest-nonzero-mode ratio with a lattice finite-difference denominator. The
current topic proxy instead uses all nonzero Fourier modes and a `2*pi / RMS-k` length.
Therefore the current proxy is rejected for source-backed exponent or calibration use until a
lowest-mode estimator candidate is implemented, compared, and passed through acceptance gates.

## Wave 32 Lowest-Mode Candidate Boundary

The lowest-mode candidate gate implements the source-family relation on the existing L16 and
L20 conserved-order fields. The implementation path passes, but the observable path blocks:
the raw snapshot zero mode is not larger than the lowest nonzero mode in any tested case
(`0/15` valid), so the current single-snapshot lane cannot supply the required susceptibility
observable. No surrogate `S(0)` is accepted by this wave.

## Wave 33 Ensemble Susceptibility-Lane Boundary

The susceptibility-lane gate separates two possible `S(0)` meanings. The source-closer
ensemble magnetization lane `N Var_ensemble(mean(C))` remains invalid for the comparable
L16/L20 groups because conserved mean fluctuations are too small relative to `S(k_min)`.
The spatial-variance proxy produces numeric lengths, but it aggregates nonzero modes and is
not accepted as source-equivalent zero-mode susceptibility without a separate source-backed
policy.

## Wave 34 Estimator-Policy Source Boundary

The policy-source gate makes the next requirements explicit: either package source support
for conserved-order/fixed-composition susceptibility, package source support for a finite-k or
canonical estimator policy, or choose window/dynamics repair without treating an estimator as
accepted. The current source package does not accept either replacement path, and the spatial
variance proxy remains diagnostic-only.

## Wave 35 Policy Source-Candidate Boundary

The source-candidate gate packages fixed-magnetization/canonical ensemble and Cahn-Hilliard
structure-factor source candidates. This is source packaging, not formula acceptance. The
current blocker is now formula extraction and normalization mapping: no candidate source has
been extracted into an accepted conserved-order `S(0)` policy, finite-k estimator, calibration
factor, or finite-size admissibility rule for exponent gates.

## Wave 36 Policy Formula-Boundary

The formula-boundary gate extracts only conservative source boundaries. Fixed-magnetization
and canonical finite-size sources warn that finite systems under conserved constraints cannot
silently supply a canonical zero-mode susceptibility. The Cahn-Hilliard source supports a
finite-k/domain-size review lane, but not an accepted critical `xi_2nd` replacement. Full-text
formula extraction and UET normalization mapping remain open before any exponent gate can rerun.

## Wave 37 Full-Text Formula Readiness

The readiness gate records that rendered or abstract source access is enough to preserve claim
boundaries but not enough to accept formulas. The next acceptable formula path requires local
TeX/PDF math source extraction, exact formula capture, UET lattice normalization mapping, and
finite-size admissibility rules before any estimator replacement or exponent rerun.

## Wave 38 Source-Archive Localization

The localization gate verifies that the three arXiv e-print source archives are present in a
temporary local cache and expose main TeX members (`paper-a6.tex`, `yjdeng0.tex`, and
`StructureFactor.tex`). This is not formula extraction. Raw arXiv sources are not committed,
and the next controller is exact TeX formula-fragment extraction or an explicit source-archive
policy before any UET normalization mapping.

## Wave 44 Source-Archive Policy Boundary

The source-archive policy gate records acquisition URLs, expected byte counts and hashes, and candidate repo archive paths for the three TeX source archives. After Wave 45, all `3/3` repo archives are restored and hash-verified, so fresh formula extraction is repo-reproducible. The next controller is estimator-policy and UET-normalization mapping.

## Wave 43 Formula-Fragment Boundary

The TeX formula-fragment gate preserves 19 exact formula fragments from the three localized source lanes: fixed-magnetization effective-field/free-energy, canonical finite-size corrections, and Cahn-Hilliard/interconversion structure factor. This narrows the blocker from missing formula extraction/source-cache reproducibility to policy acceptance and normalization mapping.

The extracted fragments are not yet accepted as the UET conserved-order scaling estimator. The next hardening step must choose and justify an estimator policy, map source variables into UET normalized lattice units, and define finite-size admissibility before any exponent or universality gate is rerun.

## Wave 46 Estimator Normalization-Map Boundary

The normalization-map gate turns the restored formula fragments into a source-policy map. Fixed-magnetization and canonical finite-size fragments constrain susceptibility policy boundaries, while the Cahn-Hilliard source provides the clearest finite-k `S(q,t)` candidate family. This is still not an accepted estimator: UET lattice field normalization, Fourier/q-grid convention, coefficient mapping, q-window admissibility, and non-domain-scale finite-size behavior remain open before exponent or universality gates can rerun.

## Wave 47 CH Finite-K Normalization Preflight

The CH finite-k preflight closes only the lattice q-grid convention: `q = 2*pi*fftfreq(L, d=dx)` is explicit in normalized lattice units. The rest remains claim-blocking. Centered UET `C` is still a proxy for source concentration fluctuation, source coefficients (`M`, `kappa`, interconversion terms, temperature offset, and susceptibility/curvature) are not mapped, no accepted finite-k `xi` extraction rule exists, and q-window/domain-scale admissibility remains a draft rule rather than an accepted estimator policy.

## Wave 48 CH Finite-K Estimator Candidate Boundary

The Wave 48 candidate implements a source-linked finite-k peak rule, `xi_peak = 2*pi/q_peak`, with `q_peak` chosen from the declared finite-k window after excluding `q=0` and the lowest domain-scale mode band. This is an implementation diagnostic, not formula acceptance. The candidate gives usable q-window diagnostics and a nondecreasing median absolute length across L12/L16/L20, but estimator acceptance is still blocked because centered `C` is proxy-normalized, source coefficients are unmapped, the peak hits the low-window edge in most cases, and no accepted finite-size/exponent rerun exists.


## Wave 49 CH Finite-K Acceptance Policy Boundary

Wave 49 defines the acceptance policy for the source-linked CH finite-k peak candidate. The policy permits measurement-only `S(q)` diagnostics while keeping source dynamics coefficients unmapped and centered UET `C` proxy-normalized. It excludes low-window-edge peaks from claim-bearing exponent rows. Under that strict policy, only `6/18` rows survive and all accepted rows are at `L20`, so finite-size coverage is insufficient. The accepted formula status remains preflight-only: no estimator replacement, exponent, universality, material, RG, or Tier A claim is upgraded.


## Wave 50 CH Finite-K Extended-Grid Coverage Boundary

Wave 50 applies the unchanged Wave 49 strict policy to larger grids (`L24` and `L28`) and combines those accepted rows with the prior accepted `L20` rows. This repairs the row-coverage blocker as a coverage probe: accepted counts are `L20:6`, `L24:2`, and `L28:2`. It does not accept the estimator as a claim-bearing critical length. Centered UET `C` remains proxy-normalized, source CH dynamics coefficients remain unmapped, and no exponent, universality, material, RG, or Tier A claim is upgraded.

## Wave 51 Field/Coefficient Policy Boundary

Wave 51 separates coefficient policy by claim lane. Measurement-only finite-k `q_peak` extraction may exclude source dynamics coefficients because it reads `S(q)` from existing fields, so the diagnostic measurement lane passes. Source-equivalent field normalization remains blocked: centered UET `C` is still a normalized proxy, not an accepted source concentration fluctuation for exponent use. The next controller is field-normalization derivation or replacement before estimator replacement, exponent, universality, material, RG, or Tier A claims.

## Wave 52 Field-Normalization Decision Boundary

Wave 52 audits the source field symbols and UET centered-field mapping. Source fragments expose normalized concentration/order-parameter fluctuation language for `S(q,t)`, and centered UET `C` may remain a diagnostic finite-k proxy after zero-mode removal. That does not close unit/proxy status: no source-backed amplitude or variance normalization maps UET `C` to the source fluctuation scale, and no accepted ensemble/time-averaging convention maps current snapshot rows to claim-bearing `S(q,t)`. The next controller is amplitude/variance normalization plus averaging convention, or an explicit replacement observable policy.

## Wave 53 Shape-Only Normalization Policy Boundary

Wave 53 separates peak-location diagnostics from amplitude-bearing source claims. For positive scalar amplitude normalization, `argmax_q[a S(q)] = argmax_q[S(q)]`, so finite-k `q_peak` and `xi_peak = 2*pi/q_peak` may remain diagnostic shape-only measurements. This does not accept source-equivalent `S(q)` amplitude, susceptibility, material fluctuation magnitude, ensemble/time averaging, estimator replacement, exponent, universality, material, RG, or Tier A claims. The next controller is a source averaging/uncertainty policy or replacement observable policy.

## Wave 54 Source Averaging/Uncertainty Policy Boundary

Wave 54 preserves diagnostic multi-grid seed aggregation but rejects claim-bearing uncertainty use of the current rows. The accepted rows meet the diagnostic floor (`L20:6`, `L24:2`, `L28:2`) but not the declared claim-bearing replicate floor of four accepted rows per grid. The rows are also final-snapshot diagnostics rather than accepted source time-window or ensemble averages, and no confidence interval/bootstrap/jackknife or fit-level uncertainty propagation policy is accepted. The next controller is replicate/temporal averaging data or an explicit replacement observable policy.

## Wave 55 Next-Path Decision Boundary

Wave 55 introduces no new physical formula, coefficient, or unit claim. It is a claim-boundary decision gate over the existing CH finite-k estimator path. Because none of the replacement-observable policies is source-backed and accepted, the gate selects replicate/temporal acquisition as the narrower next controller. Formula status remains unchanged: shape-only `q_peak` is diagnostic, source-equivalent amplitude and averaging are open, estimator acceptance is blocked, and exponent gates must not rerun until accepted evidence and uncertainty propagation exist.
