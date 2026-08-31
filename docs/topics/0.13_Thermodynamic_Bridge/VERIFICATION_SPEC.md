# Verification Spec

## Thermal Stationary-Background Diagnostic (2026-09-01)

Run docs.scripts.audit.audit_topic13_normal_thermal_background as a module and
docs/core/test/test_topic13_normal_thermal_background.py with pytest. Require
canonical production-potential first/second/third derivatives, independent
modified-Bessel-series thermal integrals, force/Hessian finite differences,
and stationary pressure/charge/entropy/susceptibility envelope identities.
Check zero-temperature and zero-coupling limits, signed charge conjugation,
canonical field covariance, energy dimensions and normal-gap rejection.

Declared natural-unit temperatures are 0.1, 0.25, 0.5 and 1.0 at mu=0.2.
The quadrature (order, cutoff factor) pairs are (96,48), (160,64), (256,80).
Stationarity uses residual 1e-10, thermodynamic derivative agreement 1e-4,
independent minimizer agreement 1e-3 and displacement refinement 1e-5.
These diagnostic tolerances do not alter the causal leakage threshold.

The mixed-scattering sensitivity grid uses s=4,8,16 and cos(theta)=-0.8,0,0.8.
Require the tensor-contracted shifted vertex to match the analytic exchange
formula, the zero-shift limit to recover the previous collision amplitude, and
pole inputs to raise rather than receive a regulator. Do not interpret the
pointwise comparison as a complete thermal collision or transport calculation.

Regenerate under the pre-import experimental-Data access guard; verify strict
JSON, current code hashes and the hash link to the preserved collision artifact.
The standalone registry addendum stays candidate-only and full_core_unlock
must remain false. Full thermal background/propagator/current matching is open.

## Coupled Gain/Loss Diagnostic (2026-09-01)

Run docs.scripts.audit.audit_topic13_coupled_gain_loss_operator as a module and
docs/core/test/test_topic13_coupled_gain_loss_operator.py with pytest. Require
independent mixed/contact vertices, production response fourth derivatives,
ordered-species counting, unequal-mass on-shell kinematics, Bose gain/loss
finite differences and nonlinear entropy. Include invalid-input, natural-unit
rescaling, state-mismatch, charge-conjugation and zero-coupling controls.

The initial near-null first-cell finite-difference failure is preserved in
t13_coupled_gain_loss_initial_probe_failure.json as historical evidence, not
a current source-hash snapshot. The corrected probe uses fixed non-null event
momenta and steps 1e-3, 1e-4, 1e-5; the relative acceptance remains 1e-4. The
near-null residual is still reported for every collision grid, not clipped.

Independent refinement axes are (radial, angular, azimuth, cutoff): reference
(18,8,12,10), radial (24,8,12,10), angular (18,12,12,10), azimuth (18,8,16,10),
cutoff (18,8,12,12). The diagnostic tolerance 2e-3 was set before these runs;
it is not a causal leakage threshold. Nested active bases have 3, 5, 8 and 11
functions on the same reference nodes. The largest basis also uses
(24,12,16,12) for a separate resolution check. Neither test certifies the
continuum or infinite-basis limit.

Require the response decomposition over generalized relaxation modes to
reconstruct the matrix inverse. Check that neutral sector momentum relaxes
as G^4, becomes an extra null direction at G=0, and has zero charge-current
overlap at mu=0. Never add a width or invert that unprojected decoupled null.

Run with an experimental-Data access guard installed before module import,
then verify strict JSON and all current source/evidence hashes. Retain
full_core_unlock=false, candidate-only registration and physical claim limits.
Run the equation inventory/foundation/compatibility audits in no-write mode
so this diagnostic does not overwrite shared Core artifacts.

## Named Elastic Diagnostic (2026-09-01)

Run docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering as
a module, then the matching test_topic13_action_normalized_elastic_scattering.py.
Require production quartic/cubic derivative matching, contact phase-space
normalization, charge crossing/conjugation, explicit-boost agreement,
detailed balance and reported resolution convergence. The diagnostic's
last-relative-change tolerance is 2e-3; it does not change any causal gate.

The pole region must raise an error, not receive an arbitrary width.
The standalone registry addendum remains CANDIDATE_DIAGNOSTIC_NOT_MERGED,
with no physical unlock. A passing tagged elastic rate is not a completed
collision operator, Kubo coefficient or Full Topic 13 result.

## Kinetic Canonical/Action Verification (2026-08-31)

Run docs.scripts.audit.audit_topic13_kinetic_canonical_action_match as a module
and docs/core/test/test_topic13_kinetic_canonical_normalization.py with pytest.
Require field covariance for both dilute and outgoing-Bose branches, signed-mu
species exchange, lambda_c-squared width scaling and canonical transition
consumer agreement. Polynomial-derivative checks use the production potential
and must fail when that potential is mutated.

The audit may pass the repair while action_matching_status is BLOCKED.
That mismatch is an actual open action-channel result, not an allowed physical
unlock. Keep both diluted/quantum artifacts comparator-only and preserve
full_core_unlock=false. Regenerate fixed-Phi audits when their code inventory
changes; do not treat historical source snapshots as current after edits.

## Fixed-Phi Repair Verification (2026-08-31)

Before reusing fixed-Phi results, run these modules from the repository root:

```text
python -B -m docs.scripts.audit.audit_topic13_finite_temperature_quasiparticle_eos
python -B -m docs.scripts.audit.audit_topic13_formal_transverse_response
python -B -m docs.scripts.audit.audit_topic13_fixed_phi_spectrum_repair
```

Require independent action-spectrum, small-k sound, canonical-rescaling and
normal enthalpy checks, strict JSON, and current source hashes. The focused
regression is docs/core/test/test_topic13_fixed_phi_spectrum_regression.py.
Its mutation test must reject a corrupted spectrum. Import reachability is
only a review inventory, not proof of numerical dependence.

Do not rerun the older aggregate sequence below as evidence of Full Topic 13
completion until acceptance scope and downstream freshness are repaired.
Bounded He-4 composition does not close the requested full two-fluid/SK/KMS
scope. This wave must retain full_core_unlock=false and not read source or
holdout payloads.

## Canonical Core-Ready Acceptance (2026-08-28)

Run in this order:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_landauer_core_disposition.py
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_he4_core_composition.py
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_full_bridge_gate.py
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_closure_matrix.py
.venv\Scripts\python.exe docs\scripts\audit\audit_major_result_closure.py
.venv\Scripts\python.exe docs\scripts\audit\audit_major_result_dependency_unlock.py
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_core_ready_acceptance.py
```

Acceptance requires:

- `t13_full_core_ready_acceptance_audit.json` reports `PASS_T13_FULL_CORE_READY_ACCEPTANCE` with all 13 criteria true.
- The named causal branch uses the unchanged `1e-6` threshold, has nonzero arrivals, and passes convergence, ledger, conservation, and anti-manipulation checks.
- `alpha_Phi_K` is an independent He-4 calibration with uncertainty and no target fit; `beta` does not use Landauer.
- The permitted TTG comparison package has row identity, units, uncertainty, preprocessing, license, and hashes; it remains outside calibration and external validation.
- EOS, finite-temperature normal component, SK/KMS, Onsager, entropy-current, dissipative-balance, and physical shear-Kubo records pass their declared contracts.
- Xie 2026 numeric data remain unread and global `claim_promotion` remains false.
- Matrix, register, and dependency gate agree that Topic 13 is Core-ready, curved 3+1 work is unlocked, and Gravity remains blocked.

Canonical artifacts:

- `docs/core/artifacts/t13_full_core_ready_acceptance_audit.json`
- `docs/core/artifacts/t13_he4_core_thermodynamic_bridge_composition_audit.json`
- `docs/core/artifacts/t13_topic13_closure_matrix.json`
- `Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`

- Primary command:
  - `.venv\Scripts\python.exe docs\topics\0.13_Thermodynamic_Bridge\Code\03_Research\Research_Landauer.py`
- Inputs:
  - `Data/03_Research/__init__.py`
  - `Data/03_Research/berut_2012.json`
  - `Data/03_Research/cattaneo_data.json`
  - `Data/03_Research/experimental_data.py`
  - `Data/03_Research/landauer_source_lock.json`
  - `docs/data/external/thermodynamics/landauer/berut_2012/source_record.json`
  - `docs/data/external/constants/codata/si_2019_exact_constants.json`
- Baseline:
  - Landauer exact-constant identity at 300 K.
  - Jun-style measured erasure cost must remain above the Landauer lower bound.
  - Bekenstein, Unruh, and Hawking relations are formula-consistency checks only.
  - Cattaneo synthetic heat-flux data is not part of the primary acceptance gate.
- Reported metrics:
  - `landauer_engine_vs_codata_relative_error`
  - `jun_2014_ratio_to_landauer_lower_bound`
  - `unruh_temperature_earth_g_K`
  - `hawking_temperature_solar_mass_K`
  - `bekenstein_hawking_entropy_solar_mass_planck_units`
  - input file SHA-256 identities and optional plot artifact status
- Fixed threshold:
  - `landauer_engine_vs_codata_relative_error <= 1e-12`
  - `jun_2014_ratio_to_landauer_lower_bound >= 1.0`
  - all three primary tests must return true
  - optional plot artifacts should render; plot failure downgrades artifact status to `WARN`
  - topic-derived Berut numeric rows keep this topic from claim class `A/B` until raw/supplemental table provenance is archived
- Artifact target:
  - Result/artifacts/0_13_thermodynamic_bridge_verification.json
- Interpretation:
  - Treat `PASS` as formula/lower-bound consistency only.
  - Treat `WARN` as scientifically usable for hardening but not paper-ready; the present WARN is expected while Berut numeric values remain topic-derived summaries.
  - Do not upgrade claim language to "solved", "verified UET", or "exact bridge" until source-locked external data, uncertainty propagation, and cross-topic dependency proof are complete.

## Core Thermodynamic Constraint Gate

Run:

```powershell
.venv\Scripts\python.exe docs\topics\0.13_Thermodynamic_Bridge\Code\03_Research\Research_Core_Thermodynamic_Constraint_Gate.py
```

Artifact:

- `Result/artifacts/0_13_core_thermodynamic_constraint_gate.json`

Required interpretation:

- `foundation_constraint_export_gate`: only the Landauer lower bound and standard thermodynamic/gravity identities may pass as class-C constraints.
- `landauer_coefficient_non_derivation_gate`: Landauer must remain an imported bound and must not be used to derive `beta` or core transport coefficients.
- `cattaneo_simulation_control_gate`: the Cattaneo result must remain explicitly simulation-only and non-external.
- `trace_phi_observable_separation_gate`: normalized `Phi` and `R` must not be relabeled as thermal observables or feedback without a dimensional map.
- `row_controller_preservation_gate`: the Berut, Jun, Hong, and Peterson source-row blockers must remain unchanged by this dependency packet.
- `uet_bridge_derivation_gate`: remains `BLOCKED` until a non-circular derivation and proxy-to-SI mapping exist.
- `thermal_pilot_physical_gate`: remains `BLOCKED` while pre-arrival leakage or external-source readiness fails.
- `thermal_source_observable_map_gate`: normalized quasi-temperature TTG operator must be defined while dimensional `alpha_Phi_K`, local numeric source, heat flux, and entropy-production maps remain explicitly blocked.
- `thermal_holdout_integrity_gate`: the 2026 graphite source remains a locked holdout and cannot be used for parameter selection, fitting, or gate tuning.
- `core_eos_transport_entropy_gate`: remains `BLOCKED` until charge EOS, covariant transport, entropy current, and dissipative-Bianchi completion are derived.
- `topic_promotion_gate`: remains `BLOCKED`; constraint exports and synthetic controls cannot promote the topic tier.

Current controlling blocker:

- `topic_0_13_constraint_only_eos_transport_entropy_bridge_missing`

## Ding PBTE Source-Formula Gate

Run:

```powershell
.venv\Scripts\python.exe docs\scriptsuditudit_topic13_ding_pbte_energy_temperature_mapping.py
```

Artifact:

- `docs/core/artifacts/t13_ding_pbte_energy_temperature_mapping_audit.json`

Acceptance requires the official PDF hash/size/MD5, source identity, Eq. S4/S10 locators, kelvin unit closure, source-`C`/UET-`C` separation, absent numeric calibration, material non-pooling, and Xie 2026 non-access checks to pass. `PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN` closes only the source-formula lane; it does not close numeric `C_src(T)`, base `Phi`, `e0`, `alpha_Phi_K`, or Full Topic 13.

## Ding PBTE Numeric-Input Availability Gate

Run:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_ding_pbte_numeric_input_availability.py
```

Artifact:

- `docs/core/artifacts/t13_ding_pbte_numeric_input_availability_audit.json`

Acceptance requires archived hash/size parity, OA identity/license/retraction checks, a complete non-truncated 11-object prefix, media-role classification, absence of reproduction payload candidates, the author-request statement, published computational-detail locators, an explicit missing-input list, and holdout non-access. A pass closes only the captured official-OA source route.


## Declared-Channel Retarded/Advanced/Keldysh 1PI Audit (T13-121)

Run:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi.py
```

Artifact:

- `docs/core/artifacts/t13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi_audit.json`

Acceptance requires retarded/advanced conjugacy, the declared spectral discontinuity, Keldysh component convention, Keldysh FDT residual, finite state, declared channel completion, and no-fit/no-holdout guards. The result is `CLOSED_FOR_LANE` only. Complete all-channel off-shell 1PI, physical renormalization, physical Kubo, entropy/heat-flux balance, SI `Phi` mapping, `alpha_Phi_K`, TTG validation, and Full Topic 13 remain blocked.

## T13-122 Threshold-Crossing Verification Contract
- Require a grid with at least one point below and one point above `s_th=9*m^2`.
- Require `rho_13=0` below threshold and a positive declared `rho_13` witness above threshold.
- Require a positive declared `rho_22` witness below threshold.
- Require retarded/advanced conjugacy, discontinuity, Keldysh component identity, FDT, and PV convergence without changing the existing numerical gate.
- Require no fit, no holdout access, no clipping, no cone padding, and no change to the ontology of `C`, `Phi`, `R_gen`, or `R_obs`.
- A passing lane must still project `full_core_unlock=false` while complete off-shell 1PI and physical renormalization remain open.
## T13-123 All 2-to-2 Permutation Verification Contract
- Require exactly the three allowed two-plus/one-minus signs `++-`, `+-+`, and `-++`.
- Require a unit-Jacobian relabeling map from each pattern to the reference `++-` kernel.
- Require the equal-mass aggregate graph-weight identity `3*(1/6)=1/2`.
- Require response identity, KMS/FDT, and PV convergence checks without changing the existing gate.
- Require no external data, no fit, no holdout access, and no physical Kubo or `alpha_Phi_K` emission.
- A passing permutation lane must still leave complete off-shell 1PI and physical renormalization open.
## T13-124 source comparator verification

- Source command: `.\\.venv\\Scripts\\python.exe docs/scripts/audit/audit_topic13_iaea_gr280_same_state_cp_source.py`.
- Gate command: `.\\.venv\\Scripts\\python.exe docs/scripts/audit/audit_topic13_full_bridge_gate.py`.
- Focused regression: `.\\.venv\\Scripts\\python.exe -m pytest -q docs/core/test/test_topic13_iaea_gr280_same_state_cp_source.py docs/core/test/test_topic13_bipm_specific_heat_source.py docs/core/test/test_topic13_iaea_graphite_constant_volume_source.py docs/core/test/test_topic13_iaea_cv_uncertainty_boundary.py docs/core/test/test_topic13_gatech_volumetric_cp_independence.py docs/core/test/test_topic13_mp48_temperature_volume_uncertainty_boundary.py`.
- Acceptance: raw PDF presence, exact hash, package size, source locators, 300 C row identity, Cp uncertainty interpolation, conditional volumetric conversion, no invented density standard uncertainty, no c_v/alpha emission, and no holdout access.
- Current result: source audit `PASS_SCOPED_IAEA_GR280_SAME_STATE_CP_COMPARATOR`; focused regression `10 passed`; full gate `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 blockers.
## T13-125 verification contract

- Audit command: `.\.venv\Scripts\python.exe docs/scripts/audit/audit_topic13_zenodo_hitrace_isotropic_graphite_cp_source.py`.
- Acceptance: raw size/hash match; official locator and row identity present; 27 rows and laboratory counts `10/6/11`; LNE/PTB uncertainty reconstruction passes; VINCA missing uncertainty remains explicit; no `c_v`, density, alpha, calibration, fit, or holdout output.
- Integration: `.\.venv\Scripts\python.exe docs/scripts/audit/audit_topic13_full_bridge_gate.py` followed by `.\.venv\Scripts\python.exe docs/scripts/audit/sync_topic13_major_result_lanes.py`.
- Regression: focused source/comparator suite `10 passed`.
- Expected status: comparator `PASS_SCOPED_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR`; full Topic 13 `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

## T13-131 public PBTE source-boundary verification

- Audit: `.\.venv\Scripts\python.exe docs/scripts/audit/audit_topic13_huberman_2019_public_pbte_boundary.py`.
- Focused regression: `.\.venv\Scripts\python.exe -m pytest -q docs/core/test/test_topic13_huberman_2019_public_pbte_boundary.py`.
- Integration: `.\.venv\Scripts\python.exe docs/scripts/audit/audit_topic13_full_bridge_gate.py` followed by `.\.venv\Scripts\python.exe docs/scripts/audit/sync_topic13_major_result_lanes.py`.
- Acceptance: source file, exact size/hash, 22-page inventory, no accepted machine-readable mode-resolved `C_src` or force-constant payload, no digitization, no fit, no alpha calibration, and no holdout access.
- Current result: source boundary `PASS_HUBERMAN_PUBLIC_PBTE_BOUNDARY_NO_ACCEPTED_NUMERIC_PAYLOAD`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 blockers.

## Thermal Dynamical-Regime Diagnostic

- Command: `python docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Thermal_Dynamical_Regime_Audit.py`
- Artifact: `Result/artifacts/t13_thermal_dynamical_regime_audit.json`
- Dependency: Topic 0.10 `chaos_method_validation.json` must pass first.
- Acceptance: tangent/shadow agreement, time-step resolution, perturbation-amplitude robustness,
  bounded finite states, unchanged ledger threshold, ontology separation, and no holdout access.
- Fourier and Cattaneo are analytic controls; trace-only is not a dynamical state.
- Open/KMS evaluation remains blocked until accepted common-noise transport inputs exist.
- Regression must preserve the 37-row closure matrix (`21` lane, `6` no-go, `10` open),
  `full_core_unlock=false`, blocked `alpha_Phi_K`, and the Topic 0.10 speed-comparator `FAIL`.
- A passing pilot is diagnostic `CLOSED_FOR_LANE`, not Full Topic 13 or external validation.
