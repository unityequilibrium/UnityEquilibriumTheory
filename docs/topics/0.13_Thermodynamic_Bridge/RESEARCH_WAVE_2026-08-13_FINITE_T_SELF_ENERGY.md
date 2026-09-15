# Research Wave: Finite-Temperature O(2) Self-Energy

## MAJOR_RESULT_CLOSURE:

`CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_SELF_ENERGY_HARTREE_LANE`.

## WHAT_IS_ACTUALLY_CLOSED:

The declared natural-unit O(2) action now has an explicit Hartree thermal
tadpole, self-consistent normal-branch mass gap, and implicit response
derivative. Quadrature/cutoff convergence and a weak-coupling high-temperature
limit witness are recorded in a machine-readable audit. This is an
action-derived internal lane, not an external calibration.

## WHAT_REMAINS_OPEN:

The unique microscopic finite-temperature scheme, condensate/two-fluid
completion, physical Kubo coefficient, microscopic SK/KMS matching, entropy
current and dissipative balance, dimensional `Phi` to thermal-observable map,
independent `alpha_Phi_K`, and Ding-compatible numeric `C_src` remain open.
The full Topic 13 gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with closure level
`PARTIAL`.

## DEPENDENCY_UNLOCKED:

Only the action-derived Hartree self-energy lane is unlocked. Core curved 3+1,
Gravity, full constitutive transport, Galaxy, SI, alpha, TTG validation, and
external-validation dependencies remain locked.

## STATUS:

`PASS_ACTION_DERIVED_HARTREE_THERMAL_SELF_ENERGY`; full Topic 13 remains
`BLOCKED_OPEN_T13_FULL_BRIDGE`.

## WHAT_CHANGED:

Added `docs/core/uet_o2_finite_temperature_self_energy.py` and its audit
`docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_self_energy_audit.json`
(`ACB61CB97087F66C97FC5E278F183F9CF6262FA633596C86DD910C190B545B18`). The
lane is projected into the full gate and synchronized into the major-result
register. Full-gate hash is
`0244D6F1212559D162208AA14C2ECA6C2A1E1F55E1D99DD3DD124EAC6D13FC65`; closure
register hash is
`6014AA8F5CB8224BA44D149F41B5AEE68579FAA71A5BDE492F0E14693DCCBB61`.

## EQUATION_OR_MAPPING:

`I_T(M^2;T,mu)=1/2 integral[(n_B(E-mu)+n_B(E+mu))/E] d^3k/(2*pi)^3`

`Pi_T=(N+2)*lambda*I_T`, with `N=2`

`M^2=m_eff^2(Phi)+Pi_T(M^2;T,mu)`

`dM^2/dPhi=(d m_eff^2/dPhi)/(1-dPi_T/dM^2)` and
`d m_eff^2/dPhi=-epsilon_nc*response_coupling`.

Natural units are retained. `Phi` is not temperature, `C` is not charge
density, `R_gen` remains a derived history trace, and no `alpha_Phi_K` is
emitted.

## VERIFICATION:

The audit reports no failed checks: gap residual
`-3.551898358766792e-13`, implicit-response finite-difference error
`1.1755950206360222e-09`, and weak-coupling high-temperature ratio
`0.32767865243469596` against the analytic `1/3` limit. Focused lane tests
pass (`3 passed`); adjacent Topic 13 and closure-register regressions pass
(`16 passed`); Wave 1 integrity is `PASS_WITH_BLOCKED_LANES`.
No Xie 2026 numeric data, fit, tuning, calibration, or threshold adjustment was
used.

## CONTROLLING_BLOCKER:

The immediate lane blocker is
`interacting_finite_temperature_self_energy_and_unique_microscopic_scheme_matching_missing`.
The full-topic controllers remain
`ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`,
`alpha_Phi_K_independent_calibration_missing`, and the non-circular
bridge/beta plus EOS/transport/KMS/entropy and dimensional-map blockers.

## NEXT_ACTION:

Close the microscopic finite-temperature scheme and physical SK/KMS/Kubo
interface without relabeling the Hartree lane as transport. In parallel,
continue only authorized Ding-compatible source acquisition and an independent
base-`Phi` SI anchor; do not fit `alpha_Phi_K` to TTG or access the locked Xie
2026 holdout.

## CLAIM_BOUNDARY:

This wave closes only the declared natural-unit O(2) Hartree self-energy and
implicit response derivative on the homogeneous normal branch. It is not a
unique microscopic finite-temperature theory, charge-EOS closure, physical
transport validation, SI map, `alpha_Phi_K` calibration, TTG prediction,
external validation, Core closure, or global UET closure.
