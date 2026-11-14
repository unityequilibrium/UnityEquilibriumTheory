# Formula Audit: 0.3 Cosmology and Hubble Tension

## Scope

This registry covers the current scalar Hubble-tension benchmark, the topic-specific
Hubble-frame coupling used by the engine, the redshift transition law used away from the
z=0 gate, and adjacent cosmology scripts that must not be promoted beyond diagnostic status
until they have their own source-locked verifier artifacts.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `COS-H0-GAP` | `Delta_H0_obs = H0_SH0ES - H0_PLANCK` | `Research_Hubble_Comparison.py` | `H0_SH0ES`, `H0_PLANCK`, and `Delta_H0_obs` in `km s^-1 Mpc^-1` | `source_locked_benchmark_input`; Planck 2018 source record and SH0ES 2022 source record | `checked local benchmark relation` | primary scalar benchmark comparator | A rounded scalar comparison can hide uncertainty/covariance and cannot replace a likelihood analysis. | Add uncertainty propagation and, later, full Planck/SH0ES likelihood or release-level data packages. |
| `COS-BETA-FRAME` | `beta_frame = sqrt(alpha_em)` | `Engine_Cosmology.UETCosmologyEngine.__init__`; `Research_Hubble_Comparison.py` | `alpha_em` dimensionless; `beta_frame` dimensionless | `source_locked_physics_constant` for `alpha_em`; theoretical bridge is topic-derived | `heuristic bridge / topic coupling rule` | no-fit coupling input for the primary benchmark | Treating `sqrt(alpha_em)` as a proved cosmological coupling would overstate the current derivation. | Derive why electromagnetic fine-structure coupling should control Hubble-frame separation, or demote to phenomenological bridge. |
| `COS-H0-UET-Z0` | `H0_late_uet = H0_early * (1 + beta_frame)` at `z = 0` | `Engine_Cosmology.predict_uet_h0`; `solve_hubble_tension` | `H0_early`, `H0_late_uet` in `km s^-1 Mpc^-1`; `beta_frame` dimensionless | Planck H0 benchmark plus `COS-BETA-FRAME` | `checked local benchmark relation with heuristic bridge` | primary PASS artifact: `hubble_comparison_validation.json` | A scalar z=0 match may not survive BAO, SN, CMB, growth, or high-z constraints. | Add multi-observable gate and report whether the same beta preserves non-H0 cosmological constraints. |
| `COS-REL-ERROR` | `relative_error_percent = abs(Delta_H0_uet - Delta_H0_obs) / Delta_H0_obs * 100` | `Research_Hubble_Comparison.py` | dimensionless percent; gaps in `km s^-1 Mpc^-1` cancel | `topic_derived_relation` | `identity / metric definition` | primary acceptance metric; threshold `< 20%` | Threshold can be too loose if used as evidence of full cosmological adequacy. | Define stricter paper-facing thresholds and uncertainty-aware residual metrics. |
| `COS-REDSHIFT-DRAG` | `H(z) = H_global * (1 + beta_frame * exp(-z / z_crit))` | `Engine_Cosmology.predict_uet_h0` | `z` dimensionless; `z_crit = 5.0` dimensionless; `H` in `km s^-1 Mpc^-1` | `heuristic_bridge`; `z_crit` is a model choice, not source-locked | `heuristic bridge, not source-locked` | not part of the primary z=0 verifier except at `z=0` where `exp(0)=1` | Unjustified `z_crit` can create apparent high-z behavior without observational support. | Source-lock or derive `z_crit`; validate against BAO/SN/CMB high-z data before using as theory support. |
| `COS-GENERIC-BETA-SEPARATION` | `generic_solver_beta != beta_frame`; generic beta is reported but not used as H0 coupling | `Engine_Cosmology.solve_hubble_tension`; artifact results | both betas dimensionless in artifact reporting | generic beta from central UET parameter machinery; frame beta from `sqrt(alpha_em)` | `diagnostic separation` | prevents accidental use of the wrong beta in H0 gate | Mixing generic Landauer beta into the H0 frame comparison fails the intended benchmark and confuses topic dependencies. | Keep both beta sources in artifact and dependency maps; add a regression check if generic beta is accidentally substituted. |
| `COS-LAMBDA-GAP` | dark-energy/vacuum-energy calculations in `Research_Dark_Energy.py` | `Code/03_Research/Research_Dark_Energy.py` | energy-density terms; unit audit required before promotion | mixed local constants and benchmark references | `diagnostic pending gate` | diagnostic only; explicit failure case | Collapsing H0 PASS and dark-energy FAIL into one cosmology status would hide a real model gap. | Create separate dark-energy formula audit entries and verifier artifact before any claim upgrade. |

## Current Artifact Link

- Primary command: `python docs/topics/0.3_Cosmology_Hubble_Tension/Code/03_Research/Research_Hubble_Comparison.py`
- Artifact: `Result/artifacts/hubble_comparison_validation.json`
- Latest status: `PASS`
- Relative error: about `2.085%`
- Observed gap: about `5.64 km s^-1 Mpc^-1`
- UET scalar gap: about `5.758 km s^-1 Mpc^-1`
- Claim boundary: scalar z=0 H0-gap benchmark only; not full cosmology validation.

## Current Formula Boundary

- The scalar H0-gap benchmark is source-locked and runnable.
- The `sqrt(alpha_em)` bridge is no-fit, but its cosmological derivation still needs a stronger mechanism-level proof.
- The redshift transition law and dark-energy scripts remain separate hardening targets.
- Paper-facing claims must cite the artifact, this registry, and the source-lock manifest.
