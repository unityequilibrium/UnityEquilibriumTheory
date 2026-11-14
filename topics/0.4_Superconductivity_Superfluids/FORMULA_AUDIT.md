# Formula Audit: 0.4 Superconductivity and Superfluids

## Scope

This registry covers the current superconductivity/superfluid calculation paths: McMillan
and Allen-Dynes transition-temperature formulas, UET coherence corrections, relativistic
`Z` correction, Cooper-pair gap derivation, helium lambda-point estimate, vortex circulation,
and plasma confinement scaling. It separates source-backed formula identities from calibrated
or heuristic model terms.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `SC-MCMILLAN-TC` | `Tc = (Theta_D/1.45) * exp[-1.04(1+lambda)/(lambda - mu*(1+0.62 lambda))]` | `Experiment_Superconductor_Data.mcmillan_tc` | `Theta_D` K; `lambda_ep` dimensionless; `mu_star` dimensionless; output K | `source_locked_benchmark_input`; source record `docs/data/external/condensed_matter/superconductivity/mcmillan_1968/source_record.json` | `checked local benchmark relation` | primary current verifier baseline | Current artifact records `model_gate_status=FAIL`: average error about 62.4 percent, 1/10 rows within 20 percent. | Normalize row-level material inputs; keep raw and calibrated datasets separate; rerun artifact. |
| `SC-INVERSE-MCMILLAN-LAMBDA` | solve `Tc_obs = McMillan(Theta_D, lambda_required, mu_star)` by bisection | `Experiment_Superconductor_Data.inverse_mcmillan_lambda` | `Tc_obs`, `Theta_D` in K; `mu_star` dimensionless; output `lambda_required` dimensionless | `topic_derived_diagnostic` based on McMillan relation and current working-copy rows | `diagnostic inversion` | failure-localization tool in primary artifact | Inverse-fit values can be mistaken for independently measured couplings. | Use only to prioritize source normalization; do not cite as prediction evidence. |
| `SC-ALLEN-DYNES-TC` | `Tc = (omega_log/1.2) f1 f2 exp[-1.04(1+lambda)/(lambda - mu*(1+0.62 lambda))]` | `AllenDynesEngine.compute_Tc` | `omega_log` K; `lambda`, `mu_star`, `f1`, `f2` dimensionless; output K | `source_locked_benchmark_input`; source record `docs/data/external/condensed_matter/superconductivity/allen_dynes_1975/source_record.json` plus local material package | `checked local benchmark relation` | engine benchmark candidate, not current primary gate | Hidden calibrated `lambda` or `omega_log` can turn a fit into a claimed prediction. | Add separate verifier over `comprehensive_superconductor_data.json` with per-material residuals, calibration labels, and held-out rows. |
| `SC-F1-F2` | `f1 = (1 + (lambda/Lambda1)^1.5)^(1/3)`, `Lambda1 = 2.46(1+3.8 mu*)`; `f2 = 1 + (r-1)lambda^2/(lambda^2+Lambda2^2)` | `AllenDynesEngine.compute_f1`, `compute_f2` | all dimensionless except `omega_log` unused in formula call; `r = omega2_ratio` dimensionless | `source_locked_benchmark_input` | `checked local benchmark relation` | engine diagnostic | Mislabeling `omega2_ratio` as derived will inflate claim strength. | Source-lock `omega2_ratio` or mark it per-material calibrated input. |
| `SC-UET-COHERENCE` | `coherence = log2(symmetry_order)/log2(48) * (1 - log10(mass)/3)` | `AllenDynesEngine.derive_uet_parameters` | symmetry order dimensionless; atomic mass in amu; output dimensionless | `heuristic_bridge` | `heuristic bridge` | modifies `mu_star_eff` | Formula is not a microscopic many-body derivation; it is a structured heuristic. | Test out-of-sample materials and record sensitivity to symmetry/mass choices. |
| `SC-MU-EFF` | `mu_star_eff = mu_star * (1 - beta * coherence)` | `AllenDynesEngine.compute_Tc` | `mu_star`, `beta`, `coherence` dimensionless | `heuristic_bridge` | `heuristic bridge` | engine diagnostic | Can improve fit by suppressing Coulomb term without independent validation. | Freeze beta source and compare against unmodified Allen-Dynes baseline. |
| `SC-REL-Z` | `rel_factor = 1 + alpha_group * (Z/137)^2`; `lambda_eff = lambda * rel_factor` | `AllenDynesEngine.compute_relativistic_correction` | `Z` atomic number; `alpha_group` dimensionless; output dimensionless multiplier | `heuristic_bridge` with known relativistic trend motivation | `heuristic bridge` | engine diagnostic | Group-dependent `alpha` is a tuning rule unless externally justified. | Record group table as calibrated model choice and test against held-out heavy elements. |
| `SC-COOPER-GAP` | `Delta = 2 hbar_omega exp[-1/(N0 |V_int|)]` | `Proof_Cooper_Pairing.py` | `hbar_omega` energy; `N0` density of states; `V_int` interaction energy factor; `Delta` energy | `checked_local_reference` BCS relation | `checked local symbolic relation` | proof note only | Symbolic positivity does not prove all materials enter superconducting state. | Tie symbolic proof to BCS assumptions and do not use as universal selection proof. |
| `SC-CONDENSATION-VALUE` | `E_cond = 0.5 N0 Delta^2` | `Proof_Cooper_Pairing.py` | `N0` density of states; `Delta` energy; output energy-density-like term | `checked_local_reference` | `checked local symbolic relation` | proof note only | Current prose says state selection is inevitable; that overstates a conditional BCS result. | Reword proof output/docs as conditional on attractive interaction and BCS cutoff assumptions. |
| `SF-LAMBDA-POINT` | `T_c = (2 pi hbar^2/m) * (n/2.612)^(2/3) / k_B / (1 + 1.76 beta)` | `AllenDynesEngine.compute_lambda_point` | `rho` kg/m^3; `m_He4` kg; `n` m^-3; output K | `source_locked_physics_constant` plus heuristic effective-mass correction | `heuristic bridge` | superfluid diagnostic | Beta correction changes known Bose-gas estimate without independent validation. | Compare to helium-4 lambda point with artifact and explicit density assumptions. |
| `SF-VORTEX` | `kappa_vortex = hbar * 2pi / m_He4 * 1e4` | `AllenDynesEngine.compute_quantum_vortex` | `hbar` J s; `m_He4` kg; output scaled circulation proxy | `source_locked_physics_constant` plus display scaling | `diagnostic scaling` | diagnostic only | `1e4` display scaling can be mistaken for physical unit conversion. | Separate SI circulation from visualization-scaled output. |
| `PLASMA-IPB98` | `tau_E = 0.0562 * 1.5^0.19 * P^-0.69 * B^0.15 * M^0.19 * R^1.97 * a^0.58 * n^0.41` | `AllenDynesEngine.compute_plasma_confinement`; `Research_Plasma.py` | engineering units: MW, T, m, 10^20 m^-3; output seconds | `source_locked_benchmark_input` for IPB98-style scaling | `checked local benchmark relation` | plasma diagnostic | Not superconductivity evidence unless linked to a declared fusion/plasma baseline. | Move or cross-link to plasma topic if it becomes claim-bearing. |

## Current Formula Boundary

- The current primary verifier checks a raw McMillan baseline, not a UET first-principles
  prediction.
- The verifier now hashes a source-lock manifest and external source records, but row-level
  material values remain working-copy inputs.
- The Allen-Dynes/UET engine contains useful model structure but includes heuristic and
  calibration-sensitive terms.
- High-Tc claims require a separate non-BCS benchmark path and cannot be promoted from the
  current McMillan/Allen-Dynes package alone.
