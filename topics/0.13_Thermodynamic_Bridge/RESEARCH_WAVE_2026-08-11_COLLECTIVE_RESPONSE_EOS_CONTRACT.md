# Topic 13 Collective-Response EOS and Stability Contract

MAJOR_RESULT_CLOSURE: `T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT` is
`CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The named finite-temperature response lane now has
explicit derivatives, reciprocal mixed derivatives, and local Hessian
stability conditions. It is a collective-response EOS, not a physical charge
or mass EOS.

WHAT_REMAINS_OPEN: Source-backed finite-temperature coefficients, physical
Phi/e0 SI mapping, independent `alpha_Phi_K`, physical EOS observables,
covariant transport, SK/KMS, entropy production, and dissipative balance.

DEPENDENCY_UNLOCKED: A normalized EOS/stability interface for later internal
derivations only. No Core-ready, Gravity, transport, external validation, or
global dependency is unlocked.

STATUS: `PASS_NAMED_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT`

WHAT_CHANGED: `C` remains a collective system-behaviour coordinate and `Phi`
an effective response coordinate. `mu_C` and `mu_Phi` are normalized
functional derivatives, not measured chemical potentials.

EQUATION_OR_MAPPING:

```text
f_hat = a_C C^2 / 2 + b_C C^4 / 4 + a_Phi(T) Phi^2 / 2
      + b_Phi Phi^4 / 4 - g C^2 Phi / 2
mu_C = a_C C + b_C C^3 - g C Phi
mu_Phi = a_Phi(T) Phi + b_Phi Phi^3 - g C^2 / 2
H_CPhi = H_PhiC = -g C
local stability: H_CC > 0, H_PhiPhi > 0, det(H) > 0
```

VERIFICATION: Analytic first and second derivatives match a finite-difference
witness. The Hessian is reciprocal and positive definite at the declared
synthetic point. No Landauer identity, fit, source row, target, or Xie 2026
holdout was used.

CONTROLLING_BLOCKER:
`source_backed_finite_temperature_EOS_coefficient_provenance_and_physical_Phi_SI_anchor_missing`

NEXT_ACTION: Source-lock the coefficients and Phi/e0 anchor independently of
TTG fitting, then develop covariant transport, SK/KMS, entropy production,
and dissipative balance under this named lane.

CLAIM_BOUNDARY: This is a formal normalized candidate EOS, not a physical
charge-density EOS, transport law, entropy-production result, external
validation, or full Topic 13 closure.
