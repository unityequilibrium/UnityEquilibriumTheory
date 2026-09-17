# Research Wave 2026-08-20: Signed-Cut Kinematic Taxonomy (T13-118)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The positive-external-energy equal-mass sunset taxonomy is now explicit for all eight internal-energy sign assignments. One `1<->3` assignment is threshold-controlled, three `2<->2` permutations are kinematically allowed, and the remaining one-plus/two-minus and all-negative assignments are excluded by future-timelike kinematics. The current scattering implementation is identified as one labeled `2<->2` pattern, leaving two permutation gaps visible.

WHAT_REMAINS_OPEN: Action-level cut multiplicity and identical-state symmetry matching remain open. Complete finite-temperature retarded 1PI self-energy, unique physical renormalization, physical Kubo transport, covariant entropy/heat-flux closure, dimensional `Phi` mapping, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: Signed-cut kinematic taxonomy only. `full_core_unlock=false`; no action-level multiplicity, physical Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added an action-compatible sign-assignment classifier, machine-readable audit artifact, focused regression, full-gate projection, closure-register entry, dependency projection, and this wave record. Corrected the prior composition state so `all_finite_temperature_sunset_channels_completed` remains false while only one labeled `2<->2` channel is present. No target data, fit, synthetic replacement, Landauer shortcut, or Xie 2026 holdout was used.

EQUATION_OR_MAPPING:

```text
P0 = sigma_1 E_1 + sigma_2 E_2 + sigma_3 E_3,  sigma_i in {+1,-1}
+ + + : P = k_1 + k_2 + k_3,          sqrt(s) >= 3 m
- + +, + - +, + + - : P + k_minus = k_plus,1 + k_plus,2
+ - -, - + -, - - + : P + k_minus,1 + k_minus,2 = k_plus  [forbidden]
- - - : P0 = -(E_1 + E_2 + E_3)       [forbidden for P0 > 0]
current labeled scattering coverage = {+ + -}; missing permutations = 2
```

Natural units only. `Phi` remains an effective response variable, `C` remains a collective system-behaviour coordinate, `R_gen` remains a derived history trace, and `R_obs` remains a separate observer record.

VERIFICATION: Audit status is `PASS_ACTION_DERIVED_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE` with zero failed checks. All 8 assignments are enumerated; allowed count is 4; `1<->3` count is 1; `2<->2` count is 3; current labeled count is 1; missing permutation count is 2. Focused regression: `3 passed`. Full sunset regression: `3 passed`. Wave 1 integrity remains `PASS_WITH_BLOCKED_LANES`, with no hash errors and no holdout consumption.

CONTROLLING_BLOCKER: `action_level_signed_cut_multiplicity_and_complete_finite_temperature_1pi_missing`; the full-bridge gate still has 11 independent blockers, led by missing independent `alpha_Phi_K` calibration and missing dimensional `Phi`/SI anchor.

NEXT_ACTION: Derive the action-level cut multiplicity and identical-state symmetry factor for the three `2<->2` permutations, then connect that result to the complete retarded/advanced/Keldysh 1PI object and physical renormalization condition. Keep the signed-cut result as a taxonomy lane and do not promote it to transport.

CLAIM_BOUNDARY: This closes only the positive-energy equal-mass signed-cut kinematic taxonomy and exposes the labeled-channel multiplicity gap. It is not a complete finite-temperature 1PI self-energy, physical Kubo coefficient, entropy-current closure, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.

DATA_ROLE: `ACTION_DERIVED_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_NO_HOLDOUT`.

EVIDENCE_PATHS:

- `docs/core/uet_o2_finite_temperature_signed_cut_coverage.py`
- `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_signed_cut_coverage.py`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_signed_cut_coverage_audit.json`
- `docs/core/uet_o2_finite_temperature_full_sunset_sk_kms.py`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_full_sunset_sk_kms_audit.json`
