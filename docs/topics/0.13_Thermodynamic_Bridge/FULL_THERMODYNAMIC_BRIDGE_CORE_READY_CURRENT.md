# Topic 0.13 Current Full-Bridge State

Machine-readable authority: `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.

MAJOR_RESULT_CLOSURE: `PARTIAL`

WHAT_IS_ACTUALLY_CLOSED: Topic 13 has lane-level causal selection, covariant
field-normalization and beta-symbol no-gos, a named finite-temperature
`beta_T13` functional, and a named collective-response EOS with explicit
derivatives, reciprocity, and local stability conditions. The results close
formula and ontology ambiguity, not physical material coefficients.

WHAT_REMAINS_OPEN: Source-backed finite-temperature coefficients, physical
Phi normalization and SI energy-density anchor, correspondence to core or
covariant coefficients, independent `alpha_Phi_K`, physical EOS observables,
covariant transport, SK/KMS, entropy production, and dissipative balance.

DEPENDENCY_UNLOCKED: A normalized response-EOS interface for later internal
derivations only. No Core-ready, Gravity/GR, transport, Galaxy, external-
validation, or global claim is unlocked.

STATUS: `BLOCKED_OPEN_T13_FULL_BRIDGE`

WHAT_CHANGED: `T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT` is
`CLOSED_FOR_LANE`. `C` remains a collective coordinate and `Phi` an effective
response; the named `mu_C` and `mu_Phi` are normalized derivatives, not
measured chemical potentials or a charge EOS.

EQUATION_OR_MAPPING:

```text
f_hat = a_C C^2 / 2 + b_C C^4 / 4 + a_Phi(T) Phi^2 / 2
      + b_Phi Phi^4 / 4 - g C^2 Phi / 2
mu_C = a_C C + b_C C^3 - g C Phi
mu_Phi = a_Phi(T) Phi + b_Phi Phi^3 - g C^2 / 2
H_CPhi = H_PhiC = -g C
local stability: H_CC > 0, H_PhiPhi > 0, det(H) > 0
```

VERIFICATION: Analytic first and second derivatives match a synthetic finite-
difference witness; the Hessian is reciprocal and positive definite at the
declared witness point. The functional does not use a Landauer identity, no
fit, source row, target, or Xie 2026 holdout.

CONTROLLING_BLOCKER: `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`. The EOS-lane controller
is `source_backed_finite_temperature_EOS_coefficient_provenance_and_physical_Phi_SI_anchor_missing`.

NEXT_ACTION: Source-lock coefficient provenance and the Phi/e0 SI observable
anchor independently of TTG target fitting. Then extend this named lane to
covariant transport, SK/KMS, entropy production, and dissipative balance.

CLAIM_BOUNDARY: UET remains a candidate effective theory. No physical charge
EOS, mass/particle/information-field identification, transport coefficient,
entropy-production law, external validation, full Topic 13 closure, or
downstream unlock is claimed.


## 2026-08-11 Causal Branch Selection Update

MAJOR_RESULT_CLOSURE: `T13_CAUSAL_THERMAL_BRANCH_SELECTION` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The original conserved-gradient baseline is a scoped high-k no-go, while the named coupled conserved-flux/C-Phi branch passes the locked compact-support, arrival, ledger, convergence, and anti-manipulation gates.

WHAT_REMAINS_OPEN: The selected causal branch is normalized; the SI `Phi` scale, source package, `alpha_Phi_K`, bridge, EOS, transport, SK/KMS, entropy, and balance requirements remain open.

DEPENDENCY_UNLOCKED: Normalized causal input only; no full Topic 13 or downstream Core dependency.

STATUS: `PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH` for branch selection; Full Topic 13 remains `PARTIAL/BLOCKED`.

WHAT_CHANGED: Linked the baseline no-go and the passing named branches as one major-result record and removed the obsolete standalone-flux note that said coupled integration was still pending.

EQUATION_OR_MAPPING: `C_t + partial_x J_C = 0`; `tau_C J_C_t + J_C = -M_C partial_x(mu_C)`; `tau_Phi Phi_tt + Phi_t + M_Phi mu_Phi = 0` in the named normalized branch.

VERIFICATION: The original baseline remains above `1e-6`; the selected coupled lane has zero measured pre-arrival leakage, nonzero arrivals, energy residual below `1e-6`, no clipping, no cone padding, no parameter fit, and no Xie 2026 access.

CONTROLLING_BLOCKER: `selected_causal_branch_is_normalized_and_dimensional_thermal_bridge_remains_open`.

NEXT_ACTION: Independently close the dimensional and thermodynamic bridge without relabeling the failed baseline.

CLAIM_BOUNDARY: No SI thermal mapping, external validation, covariant completion, or global closure follows from the named branch.
