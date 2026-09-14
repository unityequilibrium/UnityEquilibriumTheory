# UET Research Room Wave 1 Integration Note

STATUS: PASS_WITH_BLOCKED_LANES
WHAT_CHANGED: Added a shared room contract, registry entries, per-room artifact snapshots, and a non-promoting integration gate.
EQUATION_OR_MAPPING: y_TTG = Delta_Tq(t) / Delta_Tq(0); y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi. The selected causal reference is frozen-C and normalized; the full coupled candidate is separate.
VERIFICATION: Contract JSON parses; required Wave 1 registry entries and room mapping fields are checked; the selected reference branch is reported separately from the full-candidate leakage gate; Xie 2026 remains locked holdout.
CONTROLLING_BLOCKER: Full coupled pre-arrival leakage remains above the locked 1e-6 threshold; alpha_Phi_K and dimensional TTG mapping remain open; Topic 0.11 source/estimator gates remain blocked.
NEXT_ACTION: Complete independent alpha_Phi_K derivation or calibration with uncertainty, finish Topic 0.11 source and estimator gates, and rerun the owning audits before any Gravity or full constitutive-transport work.
CLAIM_BOUNDARY: Wave 1 closes coordination ambiguity only. Internal or provisional artifacts do not establish a physical proof, external validation, prediction, or closed UET theory.

Contract artifact: `docs/core/artifacts/uet_research_room_wave1_contract.json`
Gate artifact: `docs/core/artifacts/uet_research_room_wave1_integration_gate.json`
Inbox drift artifact: `docs/core/artifacts/inbox_research_alignment_drift_note.json`
