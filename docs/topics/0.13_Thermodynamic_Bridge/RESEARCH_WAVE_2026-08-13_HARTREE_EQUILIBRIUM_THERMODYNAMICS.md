# Research Wave: Hartree Equilibrium Thermodynamic Consistency

## MAJOR_RESULT_CLOSURE:

`CLOSED_FOR_LANE` for `T13_UET_O2_HARTREE_EQUILIBRIUM_THERMODYNAMIC_LANE`.

## WHAT_IS_ACTUALLY_CLOSED:

The action-derived O(2) Hartree normal branch now has a stationary thermal
2PI functional. Pressure, charge density, entropy density, and energy density
are evaluated from that same equilibrium functional. The pressure derivative
identities, Maxwell relation, stationary-pressure residual, convergence, and
positive equilibrium finite-difference stability witnesses pass.

## WHAT_REMAINS_OPEN:

Vacuum renormalization and unique microscopic finite-temperature matching,
condensate/two-fluid completion, physical Kubo coefficients, microscopic
SK/KMS matching, entropy-current dissipative balance, heat-flux mapping,
dimensional `Phi` mapping, independent `alpha_Phi_K`, and Ding-compatible
numeric `C_src` remain open. Full Topic 13 remains
`BLOCKED_OPEN_T13_FULL_BRIDGE` at closure level `PARTIAL`.

## DEPENDENCY_UNLOCKED:

Only equilibrium Hartree thermodynamic consistency is unlocked. This does not
unlock full EOS/transport/KMS/entropy, Core curved 3+1, Gravity, Galaxy, SI,
alpha, TTG validation, or external validation.

## STATUS:

`PASS_ACTION_DERIVED_HARTREE_EQUILIBRIUM_THERMODYNAMICS`; full Topic 13 remains
`BLOCKED_OPEN_T13_FULL_BRIDGE`.

## WHAT_CHANGED:

Added `docs/core/uet_o2_finite_temperature_hartree_thermodynamics.py` and audit
artifact `docs/core/07_artifacts/topic13/t13_uet_o2_hartree_thermodynamic_consistency_audit.json`
(`C0845D9D7C088B6D5D16623376C215B00AAE2810B6524A1ECFE0D1564016B443`). The
lane is projected into the full gate and synchronized into the major-result
register.

## EQUATION_OR_MAPPING:

`Omega_H=Omega_1+(m_eff^2-M^2)I_T+(N+2)*lambda*I_T^2/2`

`p_H=p_1+(N+2)*lambda*I_T^2/2` at the stationary gap

`n_H=(partial p_H/partial mu)_stationary=n_1`

`s_H=(partial p_H/partial T)_stationary=s_1`

`epsilon_H=-p_H+T*s_H+mu*n_H`.

The susceptibility and heat-capacity fields in the state record are fixed-
dressed-mass excitation quantities; stationary equilibrium stability is checked
separately by finite differences. `Phi` is not temperature and no
`alpha_Phi_K` is emitted.

## VERIFICATION:

The audit reports no failed checks. Pressure-to-entropy error is
`2.9435533906163602e-09`, pressure-to-charge error is
`4.8606244897053674e-11`, and Maxwell residual is
`1.5589309357300074e-10`. Focused tests pass (`6 passed`).
No Xie 2026 numeric data, fit, tuning, calibration, or threshold adjustment was
used.

## CONTROLLING_BLOCKER:

`vacuum_counterterm_and_unique_microscopic_finite_temperature_scheme_matching_missing`
controls this lane. Full Topic 13 remains controlled by Ding `C_src`,
independent `alpha_Phi_K`, non-circular bridge/beta, physical transport/KMS,
entropy-current, dimensional-map, and source uncertainty blockers.

## NEXT_ACTION:

Close the named finite-temperature renormalization scheme, then match physical
SK/KMS/Kubo and dimensional `Phi` interfaces. Keep this equilibrium lane
separate from physical transport and alpha calibration.

## CLAIM_BOUNDARY:

This closes only equilibrium thermodynamic consistency of the declared
natural-unit O(2) Hartree normal branch. It is not a unique microscopic
finite-temperature theory, condensate/two-fluid EOS, physical transport or
SK/KMS closure, SI map, `alpha_Phi_K` calibration, TTG prediction, external
validation, Core closure, or global UET closure.
