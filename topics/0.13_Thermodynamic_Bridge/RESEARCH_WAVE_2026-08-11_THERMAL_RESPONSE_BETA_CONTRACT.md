# Topic 13 Named Finite-Temperature beta_T13 Contract

MAJOR_RESULT_CLOSURE: `T13_THERMAL_RESPONSE_BETA_CONTRACT` is
`CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: A named finite-temperature response functional now
defines `beta_T13` as the local stiffness-temperature slope and states its
action term, units, and equilibrium entropy derivative independently of
Landauer. It is explicitly not `beta_th`, `beta_core`, or `beta_wave`.

WHAT_REMAINS_OPEN: Source-backed temperature-coefficient provenance, a
physical Phi/e0 SI anchor, correspondence to core/covariant coefficients,
independent `alpha_Phi_K`, finite-temperature EOS, transport, SK/KMS,
entropy production, and dissipative balance.

DEPENDENCY_UNLOCKED: A formula/unit interface for later bridge work only; no
Core-ready, Gravity, transport, external-validation, or global dependency.

STATUS: `PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT`

WHAT_CHANGED: `beta_T13` is a dimensionless local response-stiffness slope,
not a thermodynamic inverse temperature. The candidate functional preserves
`C` as a collective coordinate and `Phi` as a response variable; `R_gen` does
not enter or backreact.

EQUATION_OR_MAPPING:

```text
f_hat_T13 = a_Phi(T) Phi^2 / 2 + b_Phi Phi^4 / 4 - g C^2 Phi / 2
beta_T13 = T0 * (da_Phi / dT)|T0
a_Phi(T) = a_Phi(T0) + beta_T13 * (T - T0) / T0
s = -partial_T(e0 f_hat_T13) = -e0 Phi^2 beta_T13 / (2 T0)
```

VERIFICATION: The analytic entropy derivative agrees with a finite-difference
unit witness. `T0` is in K, `da_Phi/dT` is in K^-1, and `e0` is an explicit
external J m^-3 input. No Landauer term, fit, source row, target, or Xie 2026
holdout is used.

CONTROLLING_BLOCKER:
`beta_T13_source_backed_temperature_coefficient_provenance_and_physical_Phi_SI_anchor_missing`

NEXT_ACTION: Source-lock a material-relevant coefficient path and Phi/e0
anchor independently of TTG fitting, then test EOS, transport, SK/KMS,
entropy production, and dissipative balance under this named lane.

CLAIM_BOUNDARY: This is a formal candidate response-functional contract, not
a derived universal UET beta, physical entropy-production law, thermal
prediction, external validation, or full Topic 13 closure.
