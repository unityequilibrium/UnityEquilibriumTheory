# Topic 13 Core Integration Note

Date: 2026-08-28

MAJOR_RESULT_CLOSURE: `T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY` is `CLOSED_FOR_CORE` with final acceptance `PASS_T13_FULL_CORE_READY_ACCEPTANCE`.

WHAT_IS_ACTUALLY_CLOSED: A bounded O(2)/He-4 thermal bridge now composes the named finite-cone causal branch and scoped no-go, independent local `alpha_Phi_K`, natural-to-physical field and temperature mappings, an SI energy-density scale, non-Landauer normalized/SI beta, finite-temperature normal EOS, formal SK/KMS/Onsager and entropy-current interfaces, dissipative balance, and one source-locked He II normal-component shear-Kubo/FDT/entropy channel. Landauer controllers are closed only as imported-constraint Core-role dispositions. Xie 2026 remains unread.

WHAT_REMAINS_OPEN: The original conserved-`C` local-gradient baseline, graphite TTG external validation, raw-author Ding `C_src`, raw Landauer numeric parity, a complete physical two-fluid transport tensor, curved 3+1, Gravity, and global UET closure.

DEPENDENCY_UNLOCKED: Research on `CORE_CURVED_3P1_OBSERVABLE_PARENT_READY` may start. `GR_CLASSICAL_COMPATIBILITY_LANE` remains blocked until the curved parent itself is `CLOSED_FOR_CORE`.

STATUS: `CLOSED_FOR_CORE`; final acceptance `13/13`; `claim_promotion=false`; `holdout_accessed=false`.

WHAT_CHANGED: Core now consumes the exact Topic 13 result ID rather than the legacy graphite/TTG aggregate. Closure-matrix v3 marks the 10 historical graphite requirements as a backward-compatible external-validation projection while the O(2)/He-4 track controls Core readiness.

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

VERIFICATION:

- Causal leakage: `0.0 <= 1e-6`; nonzero `C` and `Phi` arrivals; convergence, conservation, ledger, and anti-manipulation checks pass.
- `alpha_Phi_K = -1.02237987858849 K` per normalized base Phi; uncertainty bound `0.056753979576408715`.
- `beta_T13 = -0.007936042649802305`; uncertainty bound `0.0008831273413443808`.
- `beta_SI = -4071.143625305366 J m^-3` per normalized Phi squared; uncertainty bound `453.5201739147111` in the same units.
- Physical shear input: `eta = (1.29e-6 +/- 5e-8) Pa s` at 1.7 K SVP.
- Permitted Ding normalized-comparison package: 432 rows with row identity, hashes, units, uncertainty declaration, preprocessing, and license; no calibration or external-validation promotion.
- Final acceptance artifact reports all 13 criteria true.

CONTROLLING_BLOCKER: None for the bounded Topic 13 Core handoff. The next Core controller is curved 3+1; the independent external graphite controller remains missing raw/accepted `C_src` and a graphite-specific dimensional response map.

NEXT_ACTION: Build the curved 3+1 parent, constraint evolution, well-posedness, observable/unit mapping, and uncertainty interface while preserving Topic 13 SK/KMS and entropy contracts. Keep metric/geometry separate from `Phi`, keep `C` distinct from mass, and keep `R_gen` derived.

CLAIM_BOUNDARY: This result is internal Core integration, not external replication, not a prediction of imported He-4 coefficients, not complete two-fluid transport, not curved 3+1 or Gravity, and not global UET closure.

Evidence hashes:

- `docs/core/artifacts/t13_full_core_ready_acceptance_audit.json`: `846d2bfbc819c1b6f700f109645a451b5d3647a570527af5dc0e21240dacae41`
- `docs/core/artifacts/t13_he4_core_thermodynamic_bridge_composition_audit.json`: `13f444f3bf14edca27e8a7af8ff957d2447c5dc0d0dc24a4d8cb77e2cfa82418`
- `docs/core/artifacts/t13_topic13_closure_matrix.json`: `ba42d8a9c1745398ec0ee04300a792d18416fccae9205bc376a96f68d423036d`
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`: `77c4fa3cfafb1fa6ee4e1e3df65f953ea3011bd33500f6786e92eca6869390c9`
- `docs/core/artifacts/uet_major_result_closure_register.json`: `94a9356f24e2dae0d396bd96931d068919e4f1773e95fd255f2cf4470bac1e55`
- `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`: `800cf61860945108ea3cb4a1604da32765d8ca0e4ddc55118ccf8702bee4d6fc`
- `docs/core/artifacts/t13_xie_2026_holdout_access_audit.json`: `c3185da0a233894d7f338138bbe6acee287194e1852a80e40b0b5f6f2134e21b`
