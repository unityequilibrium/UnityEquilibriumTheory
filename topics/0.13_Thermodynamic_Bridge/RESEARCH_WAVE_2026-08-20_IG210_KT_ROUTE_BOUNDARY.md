# Topic 13 Research Wave: IG210 Same-State K_T Route Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY`; this is a source-availability no-go, not Full Topic 13 closure.
WHAT_IS_ACTUALLY_CLOSED: The matched-source audit now includes the source-locked Farooqui NPL IG210 package. It contains three same-grade rows at 500 C, 700 C, and 1000 C with density, C_p, diffusivity, alpha_l, conductivity, source locators, and expanded uncertainty. The package explicitly records that same-state K_T and C_v are absent.
WHAT_REMAINS_OPEN: `same_state_IG210_K_T_missing`, the C_p-to-C_v correction, Ding TTG/PBTE material mapping, Ding C_src, dimensional Phi, independent alpha_Phi_K, and full EOS/transport/KMS/entropy remain open.
DEPENDENCY_UNLOCKED: IG210 source-boundary/no-go lane only; `full_core_unlock=false`.
STATUS: `PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; claim promotion remains false.
WHAT_CHANGED: Extended `audit_topic13_graphite_alpha_v_kt_matched_source_boundary.py` and its regression to include the Farooqui package, regenerated the boundary artifact and full gate projections, and synchronized the Topic 13 records.
EQUATION_OR_MAPPING: `c_p^V-c_v^V=T*alpha_V^2*K_T`; `alpha_V=3*alpha_l` is conditional isotropic geometry only. No numeric correction is emitted.
VERIFICATION: Boundary audit passed with zero failed checks; focused regression `2 passed`; full gate remains at 10 blockers; major-result sync passed; Xie 2026 was not accessed.
CONTROLLING_BLOCKER: Same-state IG210 K_T remains unavailable. The global Topic 13 controllers remain the dimensional Phi energy anchor, independent alpha_Phi_K, Ding C_src/material mapping, and EOS/transport/KMS/entropy completion.
NEXT_ACTION: Search only for a permitted same-state IG210 K_T source with specimen identity and uncertainty. Do not infer K_T from generic graphite, elastic bulk, strength, conductivity, or diffusivity data.
CLAIM_BOUNDARY: Source-provenance/no-go lane only; not C_v, not Ding validation, not alpha_Phi_K calibration, not a TTG prediction, and not Full Topic 13 closure.

Evidence:

- Source package: `Data/03_Research/farooqui_2022_ig210_thermophysical_source_package.json`.
- Boundary audit: `docs/core/07_artifacts/topic13/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json`.
- Full gate: `Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.
- Focused regression: `docs/core/test/test_topic13_graphite_alpha_v_kt_matched_source_boundary.py`.
