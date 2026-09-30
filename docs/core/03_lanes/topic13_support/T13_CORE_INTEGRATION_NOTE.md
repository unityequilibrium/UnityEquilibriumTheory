# Topic 13 Core Integration Note

Date: 2026-09-26 (reconciles the current acceptance artifact and closure matrix)

MAJOR_RESULT_CLOSURE: `T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY` is `CLOSED_FOR_CORE` for the bounded O(2)/He-4 lane. This does not close the legacy graphite/TTG external-validation projection.

WHAT_IS_ACTUALLY_CLOSED: A bounded O(2)/He-4 thermal bridge composes the named finite-cone causal branch and scoped no-go, independent local `alpha_Phi_K`, natural-to-physical field and temperature mappings, an SI energy-density scale, non-Landauer normalized/SI beta, finite-temperature normal EOS, formal SK/KMS/Onsager and entropy-current interfaces, dissipative balance, and one source-locked He II normal-component shear-Kubo/FDT/entropy channel. Landauer controllers are closed only as imported-constraint Core-role dispositions. The normalized-Phi-only lane has a structural scale-identifiability no-go; this does not rule out independent calibration in a separately source-matched physical lane.

WHAT_REMAINS_OPEN: The original conserved-`C` local-gradient baseline; graphite TTG external validation, including accepted numeric `C_src`, graphite-specific dimensional calibration/scale, material-state matching, and physical transport provenance; raw Landauer numeric parity; a complete physical two-fluid transport tensor; curved 3+1; Gravity; and global UET closure.

DEPENDENCY_UNLOCKED: `CORE_CURVED_3P1_OBSERVABLE_PARENT_READY` is unlocked for continued parent work. Its current gate remains `PARTIAL` with `constraint_preserving_boundaries` and `dimensional_observable_mapping` open. `GR_CLASSICAL_COMPATIBILITY_LANE` remains blocked until the curved parent itself is `CLOSED_FOR_CORE`.

STATUS: `CLOSED_FOR_CORE` for bounded O(2)/He-4; the 2026-09-26 acceptance artifact reports 13/13 criteria and the same-day closure matrix preserves the lane boundary; `claim_promotion=false`. The existing holdout audit's `xie_2026_accessed=false` records no numeric-payload use; separate article-text exposure was recorded on 2026-09-26, so future blind-holdout eligibility is `REVIEW_REQUIRED` (see PR #26).

WHAT_CHANGED: This reconciliation distinguishes the O(2)/He-4 Core-ready result from the still-open graphite/TTG external-validation projection, and distinguishes the normalized-lane alpha no-go from an independent physical-lane calibration. The 2026-09-26 holdout article-text exposure is recorded separately from numeric-payload access; it does not change equations, thresholds, or the existing Core dependency decision.

EQUATION_OR_MAPPING:

- `y_TTG = Delta_Tq(t) / Delta_Tq(0)`
- `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)`
- `Delta_Tq = alpha_Phi_K Delta_Phi_norm`
- `Delta_Phi_norm = Z_Phi Delta_Phi_natural`
- `T_K = theta_T T_natural`
- `f_SI = e0 f_natural`
- `beta_T13 = beta_natural / Z_Phi^2`
- `beta_SI = e0 beta_T13`
- `eta = -lim_(omega->0+) Im G_R^(xy,xy) / omega`
- `nabla_mu J_S^mu` contains `2 eta sigma_mu_nu sigma^mu_nu / T >= 0`
- Scale-identifiability control: `Delta_Phi -> s Delta_Phi` and `alpha_Phi_K -> alpha_Phi_K/s` preserve the normalized signal and dimensional product; normalized shape alone therefore cannot determine an absolute alpha.

VERIFICATION:

- Causal leakage: `0.0 <= 1e-6`; nonzero `C` and `Phi` arrivals; convergence, conservation, ledger, and anti-manipulation checks pass.
- `alpha_Phi_K = -1.02237987858849 K` per normalized base Phi; uncertainty bound `0.056753979576408715`.
- `beta_T13 = -0.007936042649802305`; uncertainty bound `0.0008831273413443808`.
- `beta_SI = -4071.143625305366 J m^-3` per normalized Phi squared; uncertainty bound `453.5201739147111` in the same units.
- Physical shear input: `eta = (1.29e-6 +/- 5e-8) Pa s` at 1.7 K SVP.
- Permitted Ding normalized-comparison package: 432 rows with row identity, hashes, units, uncertainty declaration, preprocessing, and license; no calibration or external-validation promotion.
- Base acceptance artifact reports all 13 criteria true for the bounded O(2)/He-4 Core lane; the separate graphite/TTG aggregate remains blocked.
- Xie 2026 article text was exposed in the 2026-09-26 research context; raw numeric rows and supplementary payload were not opened or used for fit, tuning, calibration, model selection, or threshold adjustment. Future blind-holdout eligibility requires review; see PR #26.

CONTROLLING_BLOCKER: None for the bounded Topic 13 Core handoff. The next Core controller is curved 3+1; the independent external graphite controller remains missing raw/accepted `C_src` and a graphite-specific dimensional response map.

NEXT_ACTION: Continue the Core curved 3+1 parent by closing constraint-preserving boundaries and the dimensional-observable map, preserving Topic 13 SK/KMS and entropy contracts. Keep metric/geometry separate from `Phi`, keep `C` distinct from mass, and keep `R_gen` derived. Treat graphite/TTG source and calibration work as a separate external-validation track; do not use exposed Xie article text to select models or conclusions.

CLAIM_BOUNDARY: This result is internal Core integration for the bounded O(2)/He-4 lane, not external graphite/TTG validation, not a pristine blind-holdout result, not a prediction of imported He-4 coefficients, not complete two-fluid transport, not curved 3+1 or Gravity, and not global UET closure.

Evidence hashes:

- `docs/core/07_artifacts/topic13/t13_full_core_ready_acceptance_audit.json`: `cb03d1c201f4f93b3fca6f9946c7990b9aad2600e9f4e99ac9e40fd949e17a11` (2026-09-26 scoped Core acceptance; its holdout assertion is limited to numeric-payload non-use)
- `docs/core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json`: `8cfb5389380b90315414fc80ee759de1de6577d417b5928852021ae5232875c9`
- `docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json`: `e6e84772a400273c438e0b8ca3c7b5b14c9d720da0420fb4021b1c0e7a54fe66` (2026-09-26; separates Core-ready O(2)/He-4 from the blocked graphite/TTG aggregate)
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`: `961aeac0383e25d1af64b3b161c67e2f57e76dfa26b0e94bfb9beeefd1bb9ec1`
- `docs/core/07_artifacts/topic13/t13_alpha_phi_k_identifiability_audit.json`: `ac377af3b3fa6d7b2dffb991a3085e2402c240a1a3ad4525d0b44bd2d319213d` (scale-identifiability evidence; its holdout-access field is historical and superseded by the later exposure record)
- `docs/core/07_artifacts/gates/uet_major_result_closure_register.json`: `1c420887141f248f9637d999441039db66b768de3fa9582969c9754f5725e550`
- `docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json`: `ecbefdf12ee1eb6661ae8096e3f62bf1ffa7992c96ca94f1149fdbc25a8bbe6e`
- `docs/core/07_artifacts/gates/core_curved_3p1_parent_gate.json`: `55b6fccea24ab6843eaa3ab134eee47ba653e9ebf2b87ac4e1fcdd074f443643`
- `docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json`: `7f848d3d6f6c9b5ab708587fb4190956c43ee46da50e4e5b732bc9285e9336ce` (historical numeric-payload access audit; the later article-text exposure is recorded in PR #26)
