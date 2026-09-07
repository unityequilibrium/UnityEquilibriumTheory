# Topic 13 Legacy NEP1 State and Verifier Wave

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION`; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_IS_ACTUALLY_CLOSED:
- The public C-CX model remains byte-identity locked and is evaluated through the pinned Calorine 1.0 legacy backend record.
- The archived 4x4x2 force-constant state and the 8x8x4 / 10x10x5 RTA mesh runs remain internally consistent for `fc2` and `fc3`.
- The current `POSCAR` is accepted by semantic atom-count and primitive-volume checks rather than rejected for a formatting-only hash difference.
- Candidate rows remain finite, positive, source-identified volumetric `C_src` values in `J m^-3 K^-1`.

WHAT_REMAINS_OPEN:
- The candidate is not Ding-equivalent and has no source-grade material/model uncertainty.
- No independent base-`Phi` SI anchor, `alpha_Phi_K`, beta/SI correspondence, physical UET Kubo coefficient, or physical SK/KMS/entropy map is present.
- The authorized Ding numeric PBTE/TTG payload or an accepted same-regime independent reproduction is still absent.

DEPENDENCY_UNLOCKED: Candidate PBTE reproduction and state/hash verification lane only. No Ding source acceptance, dimensional bridge, Full Topic 13, Core, Gravity, constitutive transport, or Galaxy dependency is unlocked.

STATUS: `PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION`; `claim_promotion=false`; `holdout_accessed=false`.

WHAT_CHANGED: The legacy reproduction verifier now separates semantic force-constant state from temporary POSCAR formatting. It checks the current atom count and primitive volume, compares `fc2`/`fc3` hashes across mesh runs, regenerates the candidate source package and audit, and refreshes the Calorine NEP1/public-model compatibility preflights.

EQUATION_OR_MAPPING: `C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]`; latest candidate rows are `993760.2797173061 J m^-3 K^-1` at `200 K` and `1689859.0705455516 J m^-3 K^-1` at `300 K`. The adjacent-mesh maximum relative change is `0.0022937348623178356` and is only a numerical candidate preflight. `Delta_Tq = alpha_Phi_K * Delta_Phi` remains uninstantiated.

VERIFICATION: Legacy reproduction audit `PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION`; focused regression `9 passed`; full gate `BLOCKED_OPEN_T13_FULL_BRIDGE`; closure-input audit `3 packages / 0 accepted_for_core`; closure matrix `10 major results / 36 subresults / 21 lane / 5 no-go / 10 open`; `xie_2026_accessed=false`.

CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, with `material_regime_mapping_to_TTG_not_closed`, `c_v_source_uncertainty_not_closed`, and the independent dimensional/alpha and physical-transport packages still open.

NEXT_ACTION: Obtain an authorized Ding-compatible numeric package or accepted same-regime PBTE reproduction, then validate it through the existing fail-closed contract. Do not rerun this comparator as a substitute for the missing source package, and do not use it to calibrate `alpha_Phi_K` or read the locked holdout.

CLAIM_BOUNDARY: This is a source-locked candidate reproduction and verifier-repair result. It is not Ding `C_src` acceptance, a `Phi`-to-temperature prediction, an independent `alpha_Phi_K` calibration, physical UET transport, external validation, Full Topic 13 closure, or global UET closure.

EVIDENCE_PATHS:
- `docs/core/artifacts/t13_calorine_legacy_nep2_pbte_reproduction_audit.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/calorine_legacy_nep2_pbte_reproduction_source_package.json`
- `docs/core/artifacts/t13_calorine_nep1_backend_compatibility_audit.json`
- `docs/core/artifacts/t13_calorine_public_model_variant_boundary_audit.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`
