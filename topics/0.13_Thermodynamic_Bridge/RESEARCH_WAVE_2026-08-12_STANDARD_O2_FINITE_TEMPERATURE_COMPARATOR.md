# Research Wave: Standard Finite-Temperature O(2) Comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A deterministic standard free-complex-scalar
normal-branch comparator is implemented in natural units. It evaluates
finite-temperature pressure, charge density, entropy density, energy density,
and charge susceptibility using the declared UET `m_eff(Phi)` only as an input.
Charge parity and pressure-derivative identities pass.

WHAT_REMAINS_OPEN: The finite-temperature UET effective action,
condensate/normal two-fluid sector, physical Kubo coefficients, SI Phi map,
and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Standard thermodynamic comparator lane only. Full Topic 13,
Core, Gravity, and physical constitutive transport remain blocked.

STATUS: `PASS_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR`

WHAT_CHANGED: Added the comparator module and machine-readable audit, then
synchronized it into the Topic 13 full gate, major-result register, dependency
gate, formula audit, report, update log, and work ledger.

EQUATION_OR_MAPPING:

```text
E_k = sqrt(k^2 + m_eff(Phi)^2)
p_T = T integral [L(E_k-mu) + L(E_k+mu)] d^3k/(2 pi)^3
n_T = partial p_T / partial mu
s_T = partial p_T / partial T
epsilon_T = -p_T + T*s_T + mu*n_T
```

VERIFICATION: Normal-domain positivity, finite-difference derivatives,
even/odd charge symmetry, and explicit separation from `C`, `R_gen`, `R_obs`,
`alpha_Phi_K`, Kubo, SI, target, and holdout lanes pass.

CONTROLLING_BLOCKER: `finite_temperature_UET_effective_action_and_normal_two_fluid_sector_not_derived`

NEXT_ACTION: Derive or source-lock the finite-temperature UET action and normal
sector, then match physical Kubo coefficients and the SI Phi observable map.

CLAIM_BOUNDARY: Standard QFT comparator only. Not a finite-temperature UET EOS,
not a two-fluid derivation, not physical transport, not `alpha_Phi_K`, and not
external validation.
