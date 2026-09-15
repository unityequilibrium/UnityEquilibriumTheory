# Research Wave: Conditional Dimensional Bridge Formula

MAJOR_RESULT_CLOSURE:
`T13_ALPHA_PHI_K_CONDITIONAL_DERIVATION` at `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED:
The local-equilibrium alpha formula, its regularity domain, and the
normalized-to-SI unit contract are implemented and machine-checked. The
formula is conditional on a temperature-dependent `a_Phi(T)`, its derivative,
an energy-density scale `e0`, and a regular equilibrium Phi branch.

WHAT_REMAINS_OPEN:
No numeric `alpha_Phi_K` is derived or independently calibrated. The four
conditional inputs are not source-locked, and the full non-circular bridge,
beta, EOS, transport, SK/KMS, entropy, and heat-flux maps remain open.

DEPENDENCY_UNLOCKED:
Conditional formula/unit integration only. No Kelvin prediction, external
validation, Gravity, transport, or Galaxy dependency is unlocked.

STATUS:
`PASS_CONDITIONAL_FORMULA_OPEN_INPUTS`

WHAT_CHANGED:
Added `docs/core/thermal_dimensional_bridge.py` with explicit conditional
formula and unit functions; added the audit artifact, gate/register sync, test
coverage, and source-wave runner integration. The current Topic 13 record now
separates formula closure from alpha calibration closure.

EQUATION_OR_MAPPING:
```text
f_th(C,Phi,T) = e0 * f_hat(C,Phi; a_Phi(T), ...)
alpha_Phi_K = -(a_Phi(T0) + 3*b_Phi*Phi0^2) / (a_Phi'(T0)*Phi0)
Delta_Tq = alpha_Phi_K * Delta_Phi
```

VERIFICATION:
`docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json` reports
`PASS_CONDITIONAL_FORMULA_OPEN_INPUTS`; focused tests pass `6`; the full Topic
13 source wave passes; Wave 1 integrity remains
`PASS_WITH_BLOCKED_LANES`; target data and Xie 2026 holdout were not used.

CONTROLLING_BLOCKER:
`dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`

NEXT_ACTION:
Source-lock or derive `a_Phi(T)`, `da_Phi/dT`, `e0`, and the equilibrium Phi
branch independently of TTG target residuals, then propagate uncertainty into
an explicitly labelled calibration record.

CLAIM_BOUNDARY:
This wave closes a conditional formula lane only. It does not close
`alpha_Phi_K`, the dimensional thermal observable map, Full Topic 13, or the
global UET theory.
