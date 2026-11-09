# Core Update: Topic 13 Evidence and Scope Handoff (2026-09-24)

MAJOR_RESULT_CLOSURE: This update adds two `CLOSED_FOR_LANE` results for the normalized graphite-TTG evidence lane. It does not change Topic 13's full-bridge state. Separately, the existing O(2)/He-4 thermal branch remains `CLOSED_FOR_CORE` according to the canonical closure-progress artifact.

WHAT_IS_ACTUALLY_CLOSED:
- The archived Ding 2022 supplementary PDFs are hash-consistent with the existing review package. Their methods text documents phase/amplitude grating separation, Savitzky-Golay smoothing for acoustic oscillations, and a typical waveform-error scale near 0.01 estimated from negative-delay samples.
- The reviewed supplementary package does not provide machine-readable waveform rows, pointwise uncertainty/covariance, mode-resolved `C_src`, or located Savitzky-Golay window/order settings in the searched PDF text.
- For a nonzero constant scale, `y(t) = alpha*x(t)/(alpha*x(0)) = x(t)/x(0)`: `alpha_Phi_K` is not needed to compare normalized shape or dip time. For the same damped-mode poles, changing the initial-rate condition changes the first dip; the dispersion relation alone does not identify the measured dip time.
- A separate Fig. 1d challenger extraction removes the previously flagged large blue-mask jumps when excluding a manually inspected legend ROI. This was a post-hoc figure-pixel sensitivity check, not raw-data recovery or a preregistered physical test.

WHAT_REMAINS_OPEN:
- The graphite/Ding external-validation lane still lacks an accepted numeric `C_src` payload or accepted same-regime reproduction, a graphite-specific dimensional `Phi` map/independent scale, and source-grade material/uncertainty closure.
- The local pump-to-`(Phi, Pi)` initial-state map is not derived; no physical dip-time or propagation-speed prediction follows from the current single-mode identity.
- Full Topic 13 EOS/transport/SK-KMS/entropy and heat-flux closure remain governed by their existing open subresults.

DEPENDENCY_UNLOCKED: None by this update. The existing Core permission for the O(2)/He-4 lane is unchanged; no graphite TTG, Gravity, full constitutive-transport, or global-theory dependency is unlocked.

STATUS: `PASS_SCOPED_SOURCE_METHOD_AND_NORMALIZED_DIP_IDENTIFIABILITY`; the latest full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` and `claim_promotion=false`.

WHAT_CHANGED: Added hash-checked documentary and analytic audits for Ding 2022 processing limits and normalized dip-time identifiability. Source pixels, source PDFs, target curves, and holdout data were not modified or used for calibration.

EQUATION_OR_MAPPING:
```text
y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq = alpha_Phi_K * Delta_Phi

x(t) = exp(-gamma*t) cos(omega*t)
t_d = (pi - atan(gamma/omega)) / omega

x_0dot(t) = exp(-gamma*t) [cos(omega*t) + (gamma/omega) sin(omega*t)]
t_d,0dot = pi/omega
v_TTG = Lambda/(2*t_d)  # source-defined dip-speed diagnostic, not automatically PDE front speed
```

VERIFICATION: The SI boundary audit passed 5 checks; the source/figure-boundary focused tests passed 7 tests; normalized dip-time tests passed 3 tests. The normalized audit records `target_data_used=false`, `holdout_accessed=false`, and `claim_promotion=false`. No Xie 2026 numeric payload was read. The closure-progress artifact separately notes `future_blind_holdout_eligibility=REVIEW_REQUIRED` after incidental public-summary exposure; keep the holdout locked and review eligibility before any future blind comparison.

CONTROLLING_BLOCKER: For graphite TTG, the current gate still lists missing accepted Ding `C_src`, graphite-specific `alpha_Phi_K`/dimensional `Phi` mapping, material-state mapping, source-grade `c_v` uncertainty, physical Kubo/transport, and heat-flux/entropy linkage. These are distinct from the already closed He-4/O(2) Core lane.

NEXT_ACTION: First obtain authorized measured rows and their pointwise uncertainty, or formally keep Fig. 1d as figure-derived comparison only; separate measured markers from simulated curves and lock preprocessing. Then derive the pump-to-`(Phi, Pi)` initial-state map for a normalized-shape/dip comparison. Pursue absolute graphite temperature and full transport closure only with their own source/calibration packages.

CLAIM_BOUNDARY: The results close documentary and analytic subquestions only. They do not validate graphite TTG, calibrate `alpha_Phi_K` for graphite, identify PDE front speed from dip time, close full Topic 13, or establish global UET physics.

## Core Scope Reconciliation

The Core closure-progress artifact (`docs/core/07_artifacts/topic13/t13_full_closure_progress.json`, generated 2026-09-09) distinguishes two tracks: `o2_he4_core_ready=CLOSED_FOR_CORE`, whose independent local He-4 `alpha_Phi_K` calibration and SI normalization may be integrated into Core, and `graphite_ttg_external_validation=OPEN`. This does not transfer the He-4 calibration to graphite. The later topic gate (`docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`, generated 2026-09-16) remains blocked for the graphite/full-bridge requirement set. The older unqualified phrase “alpha remains open” should therefore be read as lane-specific, not as “no alpha calibration exists anywhere.”

## Evidence and Identity

| Evidence | Result | SHA-256 |
|:--|:--|:--|
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/ding_2022_fig1d_legend_contamination_audit.json` | `PASS_LEGEND_CONTAMINATION_DIAGNOSTIC_ONLY` | `656f3c0ad3fe55b8742da8861674578fdcb0e8a74f657806a157abe225348d3d` |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/ding_2022_ttg_preprocessing_boundary_audit.json` | `PASS_SUPPLEMENTARY_METHOD_BOUNDARY` | `3844bbbc8c232648d273fc2813e7c9881eccb6fab9726d542889f9497b00048d` |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_normalized_dip_time_identifiability.json` | `PASS_CONDITIONAL_DIP_TIME_IDENTIFIABILITY` | `4791d35583f4cefe ed5d6f3a07cec7fd6f11d783af7bc9462a49503ab0374704` |
| `docs/core/07_artifacts/topic13/t13_full_closure_progress.json` | O(2)/He-4 `CLOSED_FOR_CORE`; graphite external lane `OPEN` | `1d3614914c9d19525b0a2622c29a8845945bab172f582374ca2ee6e052807df1` |
| `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json` | `BLOCKED_OPEN_T13_FULL_BRIDGE` | `7df4ec9a05d1c858dfd3a43ac1a32bd677da6d57d30c20c502fdb27a8447ccc6` |
