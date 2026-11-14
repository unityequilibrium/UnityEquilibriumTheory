# Topic 13 Lowitzer P-V-T Candidate Source Boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: The Lowitzer, Winkler, and Tucker graphite P-V-T publication is screened as a relevant same-study candidate, but the accessible publisher payload is abstract-only and cannot supply a source-grade alpha_V/K_T pair.
WHAT_REMAINS_OPEN: Full P-V-T payload, machine-readable alpha_V and K_T rows, row-level uncertainty, density uncertainty, Ding TTG material/state mapping, and the independent thermal bridge remain open.
DEPENDENCY_UNLOCKED: Source-search boundary only; no Cp-to-Cv correction, Ding C_src, alpha_Phi_K, transport, Core, Gravity, or Full Topic 13 dependency unlock.
STATUS: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added an abstract-only candidate source package and extended the graphite alpha_V/K_T compatibility auditor, focused regression, full gate, closure register, and dependency metadata.
EQUATION_OR_MAPPING: c_p^V - c_v^V = T * alpha_V^2 * K_T; no numeric Cp-to-Cv correction is emitted. The abstract reports fitted bulk-modulus summary values, not an uncertainty-bearing alpha_V/K_T row pair.
VERIFICATION: Candidate package parses; payload_state=ABSTRACT_ONLY; numeric alpha_V rows, numeric K_T rows, source-grade uncertainty, Ding mapping, and correction emission are all false; focused regression 2 passed; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: same_grade_alpha_V_and_K_T_missing.
NEXT_ACTION: Obtain a permitted full Lowitzer P-V-T payload or another same-specimen/state-matched alpha_V and isothermal K_T source with units, uncertainty, and Ding-regime mapping; do not combine comparator or abstract-only values.
CLAIM_BOUNDARY: This is a source-search boundary, not a same-state thermodynamic correction, Ding validation, UET calibration, TTG prediction, external validation, or Full Topic 13 closure.
SOURCE: Publisher abstract at https://journals.aps.org/prb/abstract/10.1103/PhysRevB.73.214115; no local raw payload or source hash is claimed.
EVIDENCE_HASHES: package ef5e46d19cee679196093df802e21187ca39d5a50910b9a74727f53bf4062225; boundary audit 3391ecd38b4fd90f5936497bdcf3b327b4604d271fc317ddbddf54f932254e6c2; full gate 37e5a2bee3d05acae422dd4853236376e6eea8be7fc93ba04ad980394bd9aed2; register 397b2c83d4ef4113e0a96b4d4a3cf8bdefc875676250f035a856c884f8fac776; dependency 641dcb41c6ce1a1dec1c865dd80b1fcb79f51595fdaf8e22e2ad44fc5c202bcc.
