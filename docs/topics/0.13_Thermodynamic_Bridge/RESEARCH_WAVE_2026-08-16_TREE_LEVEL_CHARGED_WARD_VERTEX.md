# Topic 13 Research Wave: Tree-Level Charged Ward Vertex

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for `T13_UET_O2_TREE_LEVEL_CHARGED_WARD_VERTEX_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: The declared finite-density charged Euclidean propagator and bare current vertex satisfy the finite-density Ward identity on the normal branch. The zero-transfer vertex limit and charge-conjugation boundary are also explicit.
WHAT_REMAINS_OPEN: Loop-renormalized off-shell self-energy and current vertex, continuum control, physical Kubo coefficient, finite-temperature two-fluid transport, dimensional Phi-to-SI mapping, independent calibration, source closure, and external validation.
DEPENDENCY_UNLOCKED: Tree-level charged Ward interface only; no loop, continuum, physical Kubo, SI, TTG, Core, Gravity, or external-validation unlock.

STATUS: `PASS_ACTION_DERIVED_TREE_LEVEL_CHARGED_WARD_VERTEX_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; claim promotion is false.
WHAT_CHANGED: Added the tree-level charged Ward-vertex module, verifier, artifact, focused tests, full-gate lane discovery, registry addendum, and major-result sync without using target data or the locked holdout.
EQUATION_OR_MAPPING: `D_E^-1(P)=(omega_n+i*mu_eff)^2+|p|^2+m_eff(Phi)^2`; `Gamma_E^0=2*(omega_n+i*mu_eff)+nu_m`; `Gamma_E^i=2*p_i+q_i`; `nu_m*Gamma_E^0+q_i*Gamma_E^i=D_E^-1(P+Q)-D_E^-1(P)`.
VERIFICATION: Maximum Ward residual `2.5750433960628582e-15`; zero-transfer vertex residual `0.0`; charge-conjugation residual `0.0`; focused regression `6 passed`; no fitting, target, or holdout access.
CONTROLLING_BLOCKER: `loop_renormalized_off_shell_self_energy_and_current_vertex_missing`; the finite-cutoff continuum and physical Kubo gates remain open separately.
NEXT_ACTION: Derive and renormalize the finite-temperature retarded self-energy and current vertex together through the SK/KMS action, then test continuum control before physical Kubo admission.
CLAIM_BOUNDARY: This is a tree-level natural-unit normal-branch Ward identity only. It is not a loop-renormalized physical vertex, Kubo coefficient, SI observable, TTG prediction, or Full Topic 13 closure.

EVIDENCE: `docs/core/07_artifacts/topic13/t13_uet_o2_tree_level_charged_ward_vertex_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json`.
