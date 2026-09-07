# Topic 0.13 Full Thermodynamic Bridge Core-Ready Decision

This note is the human-readable companion to the current scoped acceptance
records. The legacy aggregate gate remains available for backward-compatible
graphite/TTG tracking, but it is not the controlling status for the bounded
O(2)/He-4 Core handoff.

MAJOR_RESULT_CLOSURE: `T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY` is
`CLOSED_FOR_CORE` with `13/13` acceptance criteria passing.

WHAT_IS_ACTUALLY_CLOSED: The bounded O(2)/He-4 lane closes the named causal
branch, scoped conserved-gradient no-go, independent He-4 response scale,
field normalization, SI energy scale, non-Landauer beta mapping,
finite-temperature normal thermodynamics, formal SK/KMS/Onsager interface,
entropy and dissipative balance, one source-locked He-II shear transport
channel, Landauer Core-role disposition, and holdout isolation.

WHAT_REMAINS_OPEN: Graphite TTG external validation, raw-author Ding `C_src`,
graphite-specific `alpha_Phi_K`, raw Landauer row parity, the original
conserved-`C` local-gradient baseline, complete two-fluid external validation,
curved 3+1, Gravity, and global UET closure.

DEPENDENCY_UNLOCKED: The Topic 13 thermal bridge may be integrated into Core.
`CORE_CURVED_3P1_OBSERVABLE_PARENT_READY` is the next major result. Gravity
remains blocked by that separate Core result, not by the closed Topic 13 Core
handoff.

STATUS: `PASS_T13_FULL_CORE_READY_ACCEPTANCE`; `full_core_unlock=true`;
`claim_promotion=false`; `holdout_accessed=false`.

WHAT_CHANGED: Reporting now separates the accepted O(2)/He-4 Core track from
the legacy graphite/TTG aggregate. The aggregate JSON may still report
`BLOCKED_OPEN_T13_FULL_BRIDGE` because its `status` field preserves the older
external-validation scope. Use `core_result_status`,
`closure_tracks.o2_he4_core_ready`, and the final acceptance audit for Core
decisions.

EQUATION_OR_MAPPING:

```text
y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq = alpha_Phi_K * Delta_Phi_norm
Delta_Phi_norm = Z_Phi * Delta_Phi_natural
f_SI = e0 * f_natural
beta_T13 = beta_natural / Z_Phi^2
beta_SI = e0 * beta_T13
```

VERIFICATION: The final acceptance audit passes all `13/13` requirements. The
named causal branch has zero measured pre-arrival leakage against the unchanged
`1e-6` threshold. The accepted He-4 lane records independent dimensional and
transport inputs, while Xie 2026 remains unread by calibration and tuning
paths. Focused Core-ready regressions pass.

CONTROLLING_BLOCKER: None for the bounded Topic 13 Core handoff. The external
graphite track is controlled by missing accepted Ding-equivalent `C_src`, a
graphite-specific independent response scale, and its dimensional observable
map.

NEXT_ACTION: Continue `CORE_CURVED_3P1_OBSERVABLE_PARENT_READY`. Keep graphite
TTG and raw Landauer acquisition as non-blocking external research tracks with
their own stop rules.

CLAIM_BOUNDARY: `CLOSED_FOR_CORE` means internally composed and suitable for a
bounded Core handoff. It is not graphite validation, a prediction of imported
He-4 coefficients, complete physical transport validation, Gravity closure,
or global UET closure.

Canonical evidence:

- `docs/core/artifacts/t13_full_core_ready_acceptance_audit.json`
- `docs/core/artifacts/t13_he4_core_thermodynamic_bridge_composition_audit.json`
- `docs/core/artifacts/t13_topic13_closure_matrix.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`
