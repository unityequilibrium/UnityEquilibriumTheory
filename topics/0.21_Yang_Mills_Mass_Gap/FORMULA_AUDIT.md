# Formula Audit: 0.21 Yang-Mills Mass Gap

## Scope

This registry covers the current UET mass-gap engine, scalar glueball benchmark, alpha
sweep, unit conversion, and proof boundary. It does not claim a Clay Millennium proof.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `YM-CURVATURE-GAP` | `Delta_dim = sqrt(abs(V_curvature))`; `V_curvature = -2 alpha` for `alpha < 0`, else `alpha` | `Engine_Mass_Gap.estimate_mass_gap` | `alpha` dimensionless curvature parameter; output dimensionless | `topic_derived_relation` with swept/calibrated alpha | `heuristic bridge` | candidate model output used by primary benchmark | Positive output for selected alpha does not prove a general spectral gap. | Derive alpha from gauge-field assumptions or source-lock it to an independent observable. |
| `YM-SCALE-CONVERSION` | `mass_pred_MeV = Delta_dim * scale_GeV * 1000` | `Research_Mass_Gap.py` | `scale_GeV = 3.0 GeV`; output MeV | `benchmark_anchor` | `calibration bridge` | primary benchmark conversion | The 3 GeV scale can tune agreement unless independently justified. | Replace fixed scale with derived or source-constrained scale and sensitivity table. |
| `YM-LATTICE-CONVERSION` | `mass_MeV = (M*r0) * hbar_c / r0_fm` | `lattice_qcd_spectrum.json` working copy | `M*r0` dimensionless; `hbar_c=197.327 MeV fm`; `r0=0.5 fm`; output MeV | `checked_local_reference` from Morningstar-Peardon working copy | `checked local conversion` | benchmark input | Working copy may not include full systematic/error treatment from the paper. | Add raw table extraction or a source-normalized data package. |
| `YM-ALPHA-SWEEP` | `best_alpha = argmin_alpha abs(mass_pred(alpha)-mass_ref)` over 50 points | `Research_Mass_Gap.py` | alpha dimensionless over `[-0.5,-0.01]`; masses MeV | `benchmark_anchor` sweep grid | `calibration procedure` | primary artifact; status WARN/PASS based on residual vs uncertainty | A best-fit match is not prediction-strength evidence. | Add held-out states and report whether same alpha predicts tensor/pseudoscalar states. |
| `YM-REL-ERROR` | `relative_error_percent = abs(pred-ref)/ref * 100` | `Research_Mass_Gap.py` | dimensionless percent; masses in MeV cancel | `topic_derived_metric` | `metric definition` | primary reported metric | Relative error alone can hide whether residual is inside lattice uncertainty. | Keep uncertainty-aware status rule in artifact. |
| `YM-PROOF-SKETCH` | `m_gap = engine.estimate_mass_gap(); m_gap > 0` | `Proof_Mass_Gap.py` | dimensionless mass-gap surrogate | `topic_derived_relation` | `proof sketch / diagnostic` | not primary proof gate | Printing `m_gap > 0` can be mistaken for a Clay proof. | Convert proof script into assumptions/lemma artifact or keep diagnostic only. |
| `YM-VACUUM-ENERGY` | `Omega[C=0]` vs `Omega[C_min]` using `omega_functional_complete` | `Engine_Mass_Gap.yang_mills_vacuum_energy` | dimensionless internal functional terms | core UET functional | `diagnostic relation` | exploratory | Internal functional comparison is not a constructive Euclidean Yang-Mills proof. | Link to exact axioms, boundary conditions, and mathematical proof obligations. |

## Current Artifact Link

- Primary command: `python docs/topics/0.21_Yang_Mills_Mass_Gap/Code/03_Research/Research_Mass_Gap.py`
- Artifact: `Result/artifacts/mass_gap_validation.json`
- Current artifact status rule: `PASS` only if best-fit residual is within the selected
  lattice-row uncertainty; otherwise `WARN` unless execution fails.

## Current Formula Boundary

- Current work supports a calibration-aware scalar glueball benchmark.
- It does not prove a general positive Yang-Mills mass gap.
- Paper-facing promotion requires a source-normalized lattice package, uncertainty-aware
  multi-state prediction, and a separate theorem-target document with assumptions and gaps.
