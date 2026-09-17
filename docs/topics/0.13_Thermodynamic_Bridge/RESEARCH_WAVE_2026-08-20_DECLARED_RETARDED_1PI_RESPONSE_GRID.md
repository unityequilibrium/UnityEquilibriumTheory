# Research Wave 2026-08-20: Declared Retarded 1PI Response Grid (T13-117)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The audited action-derived 1<->3 and labeled 2<->2 finite-temperature sunset channels are evaluated on one matched timelike invariant grid. The assembled pole-subtracted retarded response has a positive spectral grid, lower-half-plane imaginary part, grid-level KMS/FDT checks, retarded i0 consistency, and PV convergence.

WHAT_REMAINS_OPEN: This is not the complete finite-temperature retarded 1PI self-energy. All sunset cuts, a unique physical renormalization anchor, physical Kubo transport, covariant entropy/heat-flux closure, dimensional Phi mapping, independent alpha_Phi_K, Ding C_src, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: Declared retarded response-grid lane only. `full_core_unlock=false`; no physical Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added a multi-invariant state-matched retarded response builder, focused regression, machine-readable audit artifact, full-gate mapping, closure-register entry, and dependency projection. No target data, fit, synthetic replacement data, Landauer shortcut, or Xie 2026 holdout was used.

EQUATION_OR_MAPPING:

```text
Sigma_R,T^declared(s+i0) = Re Sigma_R,T^declared,sub(s) - i*pi*rho_T^declared(s)
rho_T^declared(s) = rho_>,13(s) + rho_>,22(s) - rho_<,13(s) - rho_<,22(s)
log(rho_>^declared/rho_<^declared) = sqrt(s)/T
N_T^declared = rho_T^declared*coth(sqrt(s)/(2*T))
```

VERIFICATION: Audit has zero failed checks on `s={4.75,5.0,5.5}` with three-body threshold `4.5`. Maximum KMS residual is `8.881784197001252e-16`; maximum FDT residual is `0.003942955405912313`; maximum PV inner and outer residuals are `0.0004183177470783957` and `0.00028892386785935357`; retarded i0 consistency residual is `6.776263578034403e-21`. Focused regression: `3 passed`. Wave 1 integrity remains `PASS_WITH_BLOCKED_LANES`, with no hash errors and no holdout consumption.

CONTROLLING_BLOCKER: `complete_finite_temperature_1pi_self_energy_and_all_channel_physical_renormalization_missing`; independent physical vertex/Kubo provenance, dimensional Phi anchor, alpha_Phi_K, Ding C_src, EOS/transport/KMS/entropy completion remain separate full-bridge blockers.

NEXT_ACTION: Derive the remaining finite-temperature interacting 1PI channels and a source- or microscopic-independent physical renormalization/vertex anchor. Keep this grid as a declared natural-unit lane and do not promote it to physical SI transport.

CLAIM_BOUNDARY: This is action-derived internal evidence for the declared two-channel response grid. It is not a complete interacting 1PI theory, physical Kubo coefficient, SI thermal transport, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.

DATA_ROLE: `ACTION_DERIVED_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_NO_HOLDOUT`.

EVIDENCE_HASHES:

- module `docs/core/uet_o2_finite_temperature_declared_retarded_1pi_grid.py`: `f635e131e00c295cb90bf51607a8c41b392fef4af610682d9c4d3bc99e504885`
- audit script `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_declared_retarded_1pi_grid.py`: `c2c379f776a48d0c4daad099696042e3c205ded0f51dcc7893a959ebe9d2c281`
- audit artifact `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_declared_retarded_1pi_grid_audit.json`: `f22d74b88c82e62bb0dc984bc96b1171bc2b7579d563d693fa3559ac199e3861`
- full gate `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`: `53f40cd31b9cba7d608aeb5e8a3d48d3dc204302c478c16d4bb165a96f66a9ee`
- closure register `docs/core/07_artifacts/gates/uet_major_result_closure_register.json`: `8561401dec879ebc1b3c98f438e0ea774e8a8bacaf9cbe6cacae0ab1b25b985c`
- dependency gate `docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json`: `cc3ef8f07c4e16037d9d232f40487f5de6cd841f9b12ddc8f163541bc7f820fd`
