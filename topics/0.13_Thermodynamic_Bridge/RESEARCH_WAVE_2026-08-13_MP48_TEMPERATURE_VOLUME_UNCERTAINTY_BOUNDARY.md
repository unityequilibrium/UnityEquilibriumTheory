# Topic 13 MP48 Temperature-Volume Uncertainty Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY`.

WHAT_IS_ACTUALLY_CLOSED: The current MP48 route is closed as a scoped boundary. Its room-temperature volume anchor and non-statistical display envelope cannot be promoted to a source-grade, temperature-resolved volumetric `c_v` uncertainty contract.

WHAT_REMAINS_OPEN: A permitted temperature-resolved graphite volume source with uncertainty, source-grade statistical `c_v` uncertainty, Ding material-regime mapping, Ding-compatible mode-resolved `C_src`, and independent `alpha_Phi_K` remain open. Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.

DEPENDENCY_UNLOCKED: MP48 comparator-boundary reporting only. No Ding `C_src`, `alpha_Phi_K`, full Topic 13, Core curved 3+1, Gravity, transport, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_CHANGED: Added the source-contract boundary audit `docs/core/07_artifacts/topic13/t13_mp48_temperature_volume_uncertainty_boundary_audit.json`, integrated the lane into the full Topic 13 gate and major-result registry, and added a focused regression test. The MP48 source package remains an independent harmonic comparator.

EQUATION_OR_MAPPING: `C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell(T)`; the current comparator uses the declared room-temperature volume anchor as `V_mol,cell(T)`, so the fixed-volume step is an explicit approximation. `Delta_Tq = Delta_u / C_v^vol(T)` remains a standard comparator mapping only.

VERIFICATION: All boundary checks pass. The package declares `temperature_resolved_volume_status=OPEN`, `source_statistical_uncertainty=NOT_REPORTED_BY_DEPOSIT`, and `combined_envelope_status=NON_STATISTICAL_DISPLAY_ONLY`. MP48 source audit, adjacent source-boundary regressions, and focused tests pass (`8 passed`). Full gate and Wave 1 integrity remain consistent; Xie 2026 was not accessed or consumed.

CONTROLLING_BLOCKER: `temperature_resolved_graphite_volume_and_source_grade_c_v_uncertainty_missing` controls this lane. Full-topic controllers still include `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, `alpha_Phi_K_independent_calibration_missing`, bridge/beta, EOS/transport/KMS/entropy, dimensional mapping, and source uncertainty.

NEXT_ACTION: Obtain a permitted same-state temperature-resolved graphite volume source with uncertainty, or record a source-backed equivalent, then rerun the volumetric `c_v` contract. Keep MP48 comparator-only and independently resolve `alpha_Phi_K` without reading the locked Xie 2026 holdout.

CLAIM_BOUNDARY: This wave closes a route-level source/uncertainty boundary only. It is not Ding PBTE `C_src`, an UET energy anchor, an `alpha_Phi_K` calibration, a TTG prediction, physical transport validation, external validation, Core closure, or global UET closure.

EVIDENCE_HASHES:

- boundary audit: `9736291b43cc2723d2e6cdd73af007c9d606bf8322394ab5c2fcf1194e151f69`
- MP48 source package: `86f5d5015b5bd0172bc2bfae64271955c56470650bdb6b8459bb1280e5dbc3cf`
- MP48 source audit: `56493e6d4883f3f78d24f630f5cdc6718eec350ce264152146979e3bb0ee39a9`
- full Topic 13 gate: `bb5094dcc9683e8d8641b4648bac7d653d701ad96881e9a94e7cfc4df914b637`
- closure register: `326f7efd7bbe2822753012973d49565b29f3f97a96d69056be8baba836637e35`
- dependency gate: `e48de2a90d0919f485880797cc0b21a612c7691fb36f7da00d3725254d754506`
- Wave 1 integrity: `8d11ee5d8f154c8c69e847767f28c95c9c4d8a9dddaf4b6a5b095f8dbe1e14f8`
