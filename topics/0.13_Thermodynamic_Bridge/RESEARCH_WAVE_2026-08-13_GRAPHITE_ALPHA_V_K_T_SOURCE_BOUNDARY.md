# Topic 13 Graphite alpha_V/K_T Source Compatibility Boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY.

WHAT_IS_ACTUALLY_CLOSED: The current archived graphite source inventory cannot form a same-state, same-grade alpha_V/K_T pair with source-grade uncertainty for the Cp-to-Cv correction. The individual alpha_V and K_T comparator lanes remain separate.

WHAT_REMAINS_OPEN: A permitted same-specimen or explicitly state-matched alpha_V and isothermal K_T source with uncertainty, density uncertainty, Ding material-regime mapping, source-grade c_v uncertainty, and independent alpha_Phi_K remain open. Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.

DEPENDENCY_UNLOCKED: Current alpha_V/K_T source-pair inventory boundary only. No Cp-to-Cv input closure, Ding C_src, alpha_Phi_K, Full Topic 13, Core, Gravity, transport, Galaxy, or external-validation dependency is unlocked.

STATUS: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.

WHAT_CHANGED: Added a source-compatibility audit over NIST AXM-5Q1 alpha_V, Hanfland natural-graphite K_T, Bosak dynamic elastic bulk, TPG alpha_V, and Nelson-Riley alpha_V routes; integrated the lane into the full gate and major-result registry; and added focused regression coverage.

EQUATION_OR_MAPPING: c_p^V - c_v^V = T * alpha_V^2 * K_T; c_p^V = rho * c_p; c_v^V = c_p^V - T * alpha_V^2 * K_T. No numeric correction is emitted because the current inputs are not a same-state pair.

VERIFICATION: All source-compatibility checks pass. NIST does not emit K_T; Hanfland records same-state alpha_V as unavailable and natural graphite powder at 300 K; Bosak is explicitly dynamic/elastic rather than thermal K_T; TPG records different specimen/temperature; Nelson-Riley has no row-level statistical uncertainty. Focused tests pass (10 passed), full gate remains at the same 10 blockers, Wave 1 integrity is PASS_WITH_BLOCKED_LANES, and Xie 2026 remains unconsumed.

CONTROLLING_BLOCKER: same_grade_alpha_V_and_K_T_missing.

NEXT_ACTION: Acquire a permitted same-specimen or explicitly state-matched alpha_V and isothermal K_T source with uncertainty and Ding-regime mapping; do not combine current comparator values by assumption.

CLAIM_BOUNDARY: This closes a route-level source compatibility boundary, not the existence of all possible future alpha_V/K_T data. It is not a same-state thermodynamic correction, Ding validation, UET calibration, TTG prediction, external validation, or Full Topic 13 closure.

EVIDENCE_HASHES:

- boundary audit: 4a1148ba4ef81c2af07a2985b59ec18cc17d46f452b73176f3de2cb02ac3d30e
- full Topic 13 gate: 4ebeb1cde595179fcf717c2ceb46e5a84e8c6940f243c3a017403882fdf2a2dd
- closure register: 04ea35790f92edef0606bef6171c2b5b271cb0de3e9740f78188a390a2741fce
- dependency gate: 18aa1310753f611a5cc1305d257fe61df08d360fa13f15e7b9295a380eefe3f1
- Wave 1 integrity: 8d11ee5d8f154c8c69e847767f28c95c9c4d8a9dddaf4b6a5b095f8dbe1e14f8
