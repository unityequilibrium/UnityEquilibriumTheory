# Topic 13 Research Wave: Continuum Relative-Flow Kubo Lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared screened contact channel is evaluated on a compactified radial domain `k in [0, infinity)`. Radial order, angular order, and compactification-scale refinements pass the unchanged `1e-2` controller, while the relative operator remains symmetric positive semidefinite and conserves the common-flow mode.

WHAT_REMAINS_OPEN: Loop-renormalized condensed vertex, complete condensed scattering channels, physical Kubo coefficient with units and uncertainty, complete two-fluid constitutive tensor, dimensional `Phi` map, independent `alpha_Phi_K`, Ding-compatible `C_src`, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: Continuum natural-unit screened contact-response lane only. No physical Kubo, SI, alpha, Core, Gravity, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_CONTINUUM_RELATIVE_FLOW_KUBO_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.

WHAT_CHANGED: Added `docs/core/uet_o2_continuum_relative_flow_kubo.py`, its machine-readable audit, focused regression, equation-registry addendum, full-gate projection, closure-register/dependency sync, and Topic 13 documentation references.

EQUATION_OR_MAPPING: `k=Lambda*u/(1-u)` with `u in (0,1)`; `D_a=(1/3) integral[d^3k/(2*pi)^3] k^2 v_a^2[-partial_E n_a]`; `sigma_ab=lambda^2/[16*pi*(s_med+m_H^2)]`; `L_rel=Gamma_rel*((1,-1),(-1,1))`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)`.

VERIFICATION: Audit has zero failed checks. Radial maximum relative change is `4.5662793172363093e-07`, angular refinement is `2.06194987822215e-06`, and scale refinement is `1.6133063996982916e-09`; focused regression is `2 passed`. No finite physical cutoff, fit, target, alpha calibration, or Xie 2026 holdout was used.

CONTROLLING_BLOCKER: `loop_renormalized_condensed_vertex_and_physical_kubo_match_missing`.

NEXT_ACTION: Derive and source-lock the loop-renormalized condensed vertex or a state-matched retarded correlator with units and uncertainty. Keep the continuum thermal response separate from physical Kubo promotion.

CLAIM_BOUNDARY: Natural-unit action-derived continuum thermal contact-response lane only; not a loop-renormalized physical Kubo coefficient, complete two-fluid transport tensor, SI `Phi` calibration, TTG prediction, external validation, or Full Topic 13 closure.

EVIDENCE_HASHES: module `70850509063f5adf4493a21ceea420c9f414e1605eea7220a00ce3549d0bca30`; audit `76b46ffe55399fa03b7ae0309352b1df5e6afb494397cecfa4b82a87e0d78813`; equation registry `7ea36995d658e1037bb03c83d0ed61cc666a78f5e66dbc85b616e2077c6c2fab`; full gate `694d8a89845d64f2007cb85c37a3fc02a0a981bec16f69de038ec98278071e7e`; closure register `fa6d58b41796c1df741be9ea0738b4fe044796b920fd679f22e00df6106299f4`; dependency `16efb0698ab5e147b0ad0e173fcb79009dc5b69ad15027f7076671f46d6d6b44`.
