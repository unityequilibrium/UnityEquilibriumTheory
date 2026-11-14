### 2026-08-14 - Calorine evidence-chain resynchronization

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE evidence chain synchronized for T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION, T13_CALORINE_ISOTOPE_MASS_SENSITIVITY, and T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION.
WHAT_IS_ACTUALLY_CLOSED: The final reproduction, acceptance, full-gate, and registry hashes now point to the same corrected provenance and sensitivity artifacts.
WHAT_REMAINS_OPEN: Full Topic 13 remains blocked by Ding-compatible C_src acceptance, material/state mapping, source-grade uncertainty, alpha_Phi_K, bridge/beta, EOS/transport/KMS/entropy, and dimensional mapping.
DEPENDENCY_UNLOCKED: No new dependency; only lane-level evidence-chain consistency.
STATUS: PASS_SCOPED_EVIDENCE_CHAIN_RESYNCHRONIZATION.
WHAT_CHANGED: Refreshed full-gate and registry projections after the final source-package and uncertainty-audit regeneration.
EQUATION_OR_MAPPING: y_TTG = Delta_Tq(t) / Delta_Tq(0); Delta_Tq = alpha_Phi_K * Delta_Phi remains open. The reported C_src envelopes are comparator diagnostics only.
VERIFICATION: Full gate remains BLOCKED_OPEN_T13_FULL_BRIDGE; claim promotion is false; no fit, holdout read, threshold change, clipping, or padding occurred.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.
NEXT_ACTION: Continue with source-locked Ding-regime material/state and uncertainty closure.
CLAIM_BOUNDARY: Hash synchronization is not physical closure, external validation, alpha calibration, or Full Topic 13 closure.
EVIDENCE_HASHES: package fdca0fe6b387ecf7a731831f808b19504b9c58ebefe2d150261de37b4334f914; reproduction audit afc8fb0d9daea81c30a09b24f0aabd824cde1a85e662ea52880fadd42863de89; candidate 5e4e0d42d6e70612eabce988b86ab10b628dea14d4270bf2364ad58f572d014b; isotope 5db4a9487f728e5275906a1d4514c154b02cee4854fadcc0ea45f3ac6d5a0221; uncertainty d1b7619f1f0040e1010eb561de5422d2063fb554055c15fd7f14186d4134e481; acceptance 880eb2cc94543f19fefae13ad8c64af820bb619d9c898cd4e1e710494519d281; full gate 8c3d550ca900d11ad5d6748e5aba4410bf5bead2f423d21d09b0b6b2db1bee33; register 8ba384957304115a936060e5b1988774c2e4455896749a610f90d6faf1def667; dependency 297a8d4cacab75c1662e7aaa2798f17ae89b572fe7bcb0a9cb1967ba90ecd73f.
