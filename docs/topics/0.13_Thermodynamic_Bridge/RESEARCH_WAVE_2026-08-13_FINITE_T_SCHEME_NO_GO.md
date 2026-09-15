# Research Wave: Finite-Temperature Scheme Identifiability No-Go

## MAJOR_RESULT_CLOSURE:

`CLOSED_AS_NO_GO` for `T13_UET_O2_FINITE_T_SCHEME_IDENTIFIABILITY_NO_GO`.

## WHAT_IS_ACTUALLY_CLOSED:

The currently declared second-order reference conditions do not select a unique
finite-temperature renormalization completion. Two finite local counterterm
families share the reference value, first derivative, and second derivative,
but differ at an off-reference mass point. The named Hartree branch is therefore
recorded as an approximation branch, not as the unique microscopic theory.

## WHAT_REMAINS_OPEN:

This no-go does not supply the physical counterterm or microscopic scheme.
Interacting finite-temperature matching, condensate/two-fluid completion,
physical Kubo and SK/KMS matching, entropy-current transport, dimensional
`Phi` mapping, independent `alpha_Phi_K`, and source-compatible `C_src` remain
open. Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.

## DEPENDENCY_UNLOCKED:

Only the structural identifiability boundary is closed. No physical EOS,
transport, KMS, SI, alpha, Full Topic 13, Core, Gravity, or external-validation
dependency is unlocked.

## STATUS:

`PASS_SCOPED_NO_GO_FINITE_TEMPERATURE_SCHEME_IDENTIFIABILITY`; formal closure is
`CLOSED_AS_NO_GO` and full Topic 13 remains blocked.

## WHAT_CHANGED:

Added `docs/core/uet_o2_finite_temperature_scheme_identifiability.py`, audit
artifact `docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_scheme_identifiability_no_go.json`,
full-gate projection, major-result register sync, and focused regression test.

## EQUATION_OR_MAPPING:

`Delta V_a(x)=a*(x-x_*)^3/Lambda_*^2`

`Delta V_a(x_*)=partial_x Delta V_a(x_*)=partial_x^2 Delta V_a(x_*)=0`

while `Delta V_a(x)` and its derivatives differ for `a != 0` and `x != x_*`.
The named Hartree relation remains
`M^2=m_eff^2(Phi)+(N+2)*lambda*I_T(M^2;T,mu)`.

## VERIFICATION:

The audit reports no failed checks and an off-reference potential difference of
`0.005062500000000003` between the two witnesses. Focused tests pass (`9
passed` across the new no-go and Hartree lanes). No external source rows,
target curve, fit, calibration, or Xie 2026 numeric holdout was used.

## CONTROLLING_BLOCKER:

`source_backed_or_declared_physical_finite_temperature_renormalization_scheme_missing`
controls the no-go's next physical step. Full Topic 13 remains controlled by
Ding `C_src`, independent `alpha_Phi_K`, bridge/beta, physical transport/KMS,
entropy-current, dimensional-map, and source uncertainty blockers.

## NEXT_ACTION:

Either declare and justify a physical finite-temperature renormalization scheme
with microscopic matching, or retain Hartree as approximation-only while
closing physical Kubo/SK/KMS and SI observables without fitting alpha or reading
Xie 2026.

## CLAIM_BOUNDARY:

This is a structural no-go for uniqueness under the current reference
conditions. It is not a proof that every future microscopic finite-temperature
scheme is impossible, and it is not physical EOS/transport closure, SI mapping,
alpha calibration, TTG prediction, external validation, Core closure, or global
UET closure.
