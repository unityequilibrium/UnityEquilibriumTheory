# Research Wave T13-130: Covariant Action Symbolic SI Conversion Contract

MAJOR_RESULT_CLOSURE:
`CLOSED_FOR_LANE` for the symbolic natural-unit to SI conversion contract only.

WHAT_IS_ACTUALLY_CLOSED:
The covariant action/response lane now exposes an auditable symbolic conversion map. Given an independently sourced energy reference `E_ref`, exact SI constants convert natural-unit energy density, heat-capacity density, thermal-energy differences, and response slopes without inventing a numeric calibration.

WHAT_REMAINS_OPEN:
`E_ref`, the covariant field normalization `Phi_scale`, the base `Phi -> Phi_E` map, `e0`, temperature-dependent response coefficients, and independent `alpha_Phi_K` calibration remain open. This lane does not close the full thermal bridge.

DEPENDENCY_UNLOCKED:
Only the symbolic unit-contract lane is available to Core integration. No Core-ready, Gravity, external-validation, or global-closure dependency is unlocked.

STATUS:
`PASS_SCOPED_SYMBOLIC_ACTION_SI_CONVERSION_CONTRACT`; the Topic 13 full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `closure_level=PARTIAL`.

WHAT_CHANGED:
Added the reusable conversion module, a machine-readable audit artifact, regression tests, full-gate lane registration, and major-result/dependency synchronization.

EQUATION_OR_MAPPING:
```text
u_SI = u_nat * E_ref^4 / (hbar*c)^3
C_SI = C_nat * k_B*E_ref^3 / (hbar*c)^3
Delta_Tq = (E_ref/k_B) * Delta_theta
alpha_Phi_K = (E_ref/k_B) * alpha_Phi_theta
Phi_normalized = Phi_covariant / Phi_scale
```

VERIFICATION:
The scoped audit passes with no failed checks; the dedicated regression suite passes 4 tests; the full Topic 13 gate was rerun; research-room integrity remains `PASS_WITH_BLOCKED_LANES`; Xie 2026 remains unread by calibration paths.

CONTROLLING_BLOCKER:
`energy_reference_and_base_Phi_normalization_provenance_missing`.

NEXT_ACTION:
Find or derive an independent provenance record for `E_ref` and the covariant-to-base-`Phi` normalization. Only after that can a numeric `Phi -> thermal observable` anchor be evaluated.

CLAIM_BOUNDARY:
This is symbolic dimensional bookkeeping conditional on declared inputs, not a measured SI calibration, not a prediction, and not proof of the UET action or thermal transport.
