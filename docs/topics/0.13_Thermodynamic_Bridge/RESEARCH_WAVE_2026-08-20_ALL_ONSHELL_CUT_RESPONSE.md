# Research Wave 2026-08-20: All On-Shell Cut Response (T13-120)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The all-positive-energy equal-mass on-shell thermal cut response is now checked on the matched invariant grid `s={4.75,5.0,5.5}`. The `1<->3` channel and all three `2<->2` sign permutations are represented through the action graph weight `w_22=1/2`; the combined spectral grid has positive support, lower-half-plane retarded sign, KMS/FDT, retarded i0 consistency, and converged pole-subtracted real response.

WHAT_REMAINS_OPEN: Complete off-shell finite-temperature retarded/advanced/Keldysh 1PI evaluation, unique physical renormalization, physical scattering/Kubo normalization, covariant entropy/heat-flux closure, dimensional `Phi` mapping, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: All-positive-energy on-shell cut spectral response lane only. `full_core_unlock=false`; no off-shell 1PI, physical transport, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added an evidence-producing integration lane that combines the signed-cut taxonomy, action-level multiplicity, and state-matched retarded response grid. No holdout, target data, fit, synthetic replacement, Landauer shortcut, or threshold adjustment was used.

EQUATION_OR_MAPPING:

```text
rho_T^all_onshell = rho_T^(+++) + rho_T^(-++) + rho_T^(+-+) + rho_T^(++-)
rho_T^(2<->2,all) = (3*(1/6))*rho_T^(++-) = (1/2)*rho_T^(++-)
Sigma_R,T^all_onshell(s+i0) = Re Sigma_R,T^sub(s) - i*pi*rho_T^all_onshell(s)
N_T^all_onshell = rho_T^all_onshell*coth(sqrt(s)/(2*T))
```

Natural units only. `Phi` remains an effective response variable, `C` remains a collective system-behaviour coordinate, `R_gen` remains a derived history trace, and `R_obs` remains a separate observer record.

VERIFICATION: Audit has zero failed checks on `s={4.75,5.0,5.5}`. Maximum KMS residual `8.881784197001252e-16`; maximum FDT residual `0.003942955405912313`; maximum PV inner/outer residuals `0.0004183177470783957` / `0.00028892386785935357`; retarded i0 residual `6.776263578034403e-21`; graph weight `0.5`. Focused all-onshell regression `3 passed`; multiplicity/scattering regression `6 passed`; Wave 1 integrity remains `PASS_WITH_BLOCKED_LANES`; holdout not consumed.

CONTROLLING_BLOCKER: `complete_off_shell_finite_temperature_1pi_and_physical_renormalization_missing`; full bridge still has 11 independent source, dimensional, alpha, EOS/transport/KMS/entropy blockers.

NEXT_ACTION: Move from the complete on-shell discontinuity to the off-shell retarded/advanced/Keldysh 1PI object, prove regulator/subtraction independence under an independently declared physical anchor, and keep physical Kubo admission separate.

CLAIM_BOUNDARY: This closes only an action-derived all-positive-energy on-shell spectral response grid. It is not a complete off-shell 1PI self-energy, physical renormalization, physical Kubo coefficient, entropy-current closure, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.

DATA_ROLE: `ACTION_DERIVED_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_NO_HOLDOUT`.

EVIDENCE_PATHS:

- `docs/core/uet_o2_finite_temperature_all_onshell_cut_response.py`
- `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_all_onshell_cut_response.py`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_all_onshell_cut_response_audit.json`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_sunset_cut_multiplicity_audit.json`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_declared_retarded_1pi_grid_audit.json`
