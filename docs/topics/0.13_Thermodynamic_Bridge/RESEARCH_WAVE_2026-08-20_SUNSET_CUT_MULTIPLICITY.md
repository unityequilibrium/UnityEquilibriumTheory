# Research Wave 2026-08-20: Sunset Cut Multiplicity (T13-119)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The action-level sunset symmetry factor and positive-energy sign multiplicity are now connected. The single `1<->3` pattern carries `1/6`; the three equal-mass `2<->2` permutations carry `3*(1/6)=1/2`. The existing representative scattering factor `0.5` matches this graph-summed weight without changing the numerical KMS/PV lane. The physical species-resolved final-state convention `1/(1+delta_cd)` is recorded separately.

WHAT_REMAINS_OPEN: The physical scattering normalization is not identified with the self-energy graph weight. Complete finite-temperature retarded/advanced/Keldysh 1PI evaluation, unique physical renormalization, physical Kubo transport, covariant entropy/heat-flux closure, dimensional `Phi` mapping, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: Action-level finite-temperature sunset cut multiplicity only. `full_core_unlock=false`; no physical coefficient, complete 1PI, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added the action-level multiplicity state, machine-readable audit artifact, focused regression, scattering-source contract clarification, full-gate projection, closure-register entry, dependency projection, and this wave record. The scattering numeric factor remains `0.5`; only its derivation and boundary were made explicit. No target data, fit, synthetic replacement, Landauer shortcut, or Xie 2026 holdout was used.

EQUATION_OR_MAPPING:

```text
S_sunset = 1/6
N_13 = 1,             w_13 = N_13*S_sunset = 1/6
N_22 = 3,             w_22 = N_22*S_sunset = 3/6 = 1/2
I_22^all = (1/2) I_22^(++-)       [equal-mass relabelled representative]
w_final(c,d) = 1/(1+delta_cd)     [separate physical scattering comparator]
```

Natural units only. `Phi` remains an effective response variable, `C` remains a collective system-behaviour coordinate, `R_gen` remains a derived history trace, and `R_obs` remains a separate observer record.

VERIFICATION: Multiplicity audit status is `PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE` with zero failed checks. `w_13=0.16666666666666666`, `w_22=0.5`, ratio `3.0`, current factor match is true, and physical final-state weights are `{0.5,1.0}` for O(2). Focused multiplicity and scattering regression: `6 passed`; full gate remains blocked and holdout access remains false.

CONTROLLING_BLOCKER: `physical_scattering_normalization_identity_and_complete_finite_temperature_1pi_missing`; full bridge still has 11 source, dimensional, alpha, EOS/transport/KMS/entropy blockers.

NEXT_ACTION: Evaluate the complete retarded/advanced/Keldysh 1PI object using the admitted graph weight, prove its regulator and physical subtraction anchor, then keep transport admission separate from this natural-unit cut result.

CLAIM_BOUNDARY: This closes action-level cut multiplicity only. It is not a physical scattering coefficient, complete finite-temperature 1PI self-energy, physical renormalization, Kubo transport, entropy-current closure, SI mapping, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.

DATA_ROLE: `ACTION_DERIVED_FINITE_T_CUT_MULTIPLICITY_NO_HOLDOUT`.

EVIDENCE_PATHS:

- `docs/core/uet_o2_finite_temperature_sunset_cut_multiplicity.py`
- `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_sunset_cut_multiplicity.py`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_sunset_cut_multiplicity_audit.json`
- `docs/core/uet_o2_finite_temperature_sunset_scattering_sk_kms.py`
- `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_sunset_scattering_sk_kms_audit.json`
