# Topic 13 Research Wave: On-Shell Sunset Width

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for `T13_UET_O2_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: The neutral action-matched finite-temperature sunset lane now derives a positive on-shell width witness from the declared 1<->3 and labeled 2<->2 retarded cuts at a timelike probe.
WHAT_REMAINS_OPEN: Complete off-shell finite-temperature 1PI self-energy, unique physical renormalization, charged finite-temperature state matching, current-correlator Kubo admission, dimensional Phi-to-SI mapping, independent alpha_Phi_K calibration, Ding C_src source closure, and external validation.
DEPENDENCY_UNLOCKED: A traceable neutral natural-unit width input for the named memory/collision lane only; no physical transport, SI, alpha, TTG, Core, or Gravity unlock.

STATUS: `PASS_ACTION_MATCHED_ON_SHELL_SUNSET_COLLISION_WIDTH_LANE`; full-gate result remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; claim promotion remains false.
WHAT_CHANGED: Added the on-shell width module, verifier, artifact, focused tests, full-gate integration, and equation-registry addendum. The original finite-temperature sunset cut modules remain unchanged.
EQUATION_OR_MAPPING: `Sigma_R^cut=Sigma_R^(1<->3)+Sigma_R^(2<->2)`; `Gamma_cut(s;T)=-Im Sigma_R^cut(s;T)/sqrt(s)`; `Im Sigma_R^cut=-pi*(rho_>^cut-rho_<^cut)`.
VERIFICATION: Reference state `(T,m^2,lambda,s)=(0.35,0.5,0.8,5.0)` gives `Gamma_cut=2.5252941405998473e-05` in natural energy units and a cut-convergence bound of `1.3746648594070555e-06`; width, retarded sign, KMS, FDT, ontology, no-fit, no-target, and no-holdout checks pass. Focused sunset regression: 9 passed.
CONTROLLING_BLOCKER: `complete_off_shell_finite_temperature_1pi_self_energy_and_physical_transport_match_missing`.
NEXT_ACTION: Derive a charged finite-temperature off-shell retarded self-energy and match its current correlator through SK/KMS; retain this neutral width as a scoped witness and do not promote it to a physical Kubo coefficient.
CLAIM_BOUNDARY: This is a neutral natural-unit on-shell sunset-width lane. It is not a complete physical self-energy, conductivity/viscosity, entropy-current closure, SI thermal observable, alpha_Phi_K calibration, TTG prediction, or Full Topic 13 closure.

EVIDENCE: `docs/core/07_artifacts/topic13/t13_uet_o2_on_shell_sunset_width_audit.json`; full-gate hash integration is recorded in `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.
