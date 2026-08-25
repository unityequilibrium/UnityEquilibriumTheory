# Research Wave 2026-08-26: Xie 2026 Holdout Preregistration

MAJOR_RESULT_CLOSURE:
- T13_XIE_2026_HOLDOUT_COMPARISON_PREREGISTRATION is CLOSED_FOR_LANE.
- This closes an access and comparison contract only. It does not close the thermal bridge or consume the holdout.

WHAT_IS_ACTUALLY_CLOSED:
- Xie 2026 is assigned the HOLDOUT role with a fixed normalized-observable mapping and a fail-closed access policy.
- The comparison baseline lanes are fixed before any future numeric access: Fourier, Cattaneo, trace-only, and Phi response.
- The existing leakage threshold <= 1e-6 is inherited without clipping, padding, fitting, tuning, or threshold adjustment.

WHAT_REMAINS_OPEN:
- No Xie numeric payload, row, curve, or source bytes were read, archived, digitized, or used.
- The three Topic 13 root input packages remain blocked: Ding-compatible source/material uncertainty, independent base-Phi/SI/alpha/beta, and physical transport matching.
- No external holdout comparison, prediction, or validation claim exists.

DEPENDENCY_UNLOCKED:
- Future comparison protocol readiness only. Full Topic 13, Core curved 3+1, Gravity, and constitutive transport remain locked.

STATUS:
- PASS_SCOPED_XIE_2026_HOLDOUT_PREREGISTRATION_LOCKED after the focused audit.

WHAT_CHANGED:
- Added the metadata-only Xie comparison preregistration and its focused verifier.
- Added a complete generated subresult closure map for all 36 Topic 13 requirements.

EQUATION_OR_MAPPING:
- y_TTG = Delta_Tq(t) / Delta_Tq(0).
- y_TTG^UET = Delta_Phi(t) / Delta_Phi(0).
- Delta_Tq = alpha_Phi_K * Delta_Phi.
- C_src(T) = sum_mu c_mu(T).

VERIFICATION:
- The preregistration is metadata-only and has no numeric payload hash.
- xie_2026_accessed=false, numeric_payload_consumed=false, used_for_fit=false, used_for_tuning=false, used_for_calibration=false, and used_for_threshold_adjustment=false remain true.
- The full closure artifact remains BLOCKED_OPEN_T13_FULL_BRIDGE with OPEN=10 and full_core_unlock=false.

CONTROLLING_BLOCKER:
- holdout_numeric_access_requires_accepted_root_inputs_and_separate_authorization.
- For Full Topic 13 itself, the controlling physical blocker remains the missing independent Phi/SI scale and alpha_Phi_K record, together with the two other blocked root packages.

NEXT_ACTION:
- Do not read Xie numeric data. Acquire accepted non-holdout source, calibration, and transport inputs first.
- When an authorized input hash changes, rerun the input validators and full gate; only then consider a separately authorized holdout access audit.

CLAIM_BOUNDARY:
- This wave is a research-protocol result, not a thermal prediction, external validation, or Full Topic 13 closure.

EVIDENCE_PATHS:
- docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_xie_2026_holdout_comparison_preregistration.json
- docs/core/artifacts/t13_xie_2026_holdout_access_audit.json
- docs/core/artifacts/t13_xie_2026_holdout_preregistration_audit.json
- docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_SUBRESULT_CLOSURE_MAP.md
