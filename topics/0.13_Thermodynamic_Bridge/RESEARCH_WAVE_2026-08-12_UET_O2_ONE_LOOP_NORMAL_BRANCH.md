# Research Wave: Action-Derived O(2) One-Loop Normal Branch

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The thermal one-loop determinant on the homogeneous
normal background `A=0` is derived from the declared conservative O(2) action
through `m_eff(Phi)`. The response derivative, `dp/dmu=n`, `dp/dT=s`, energy
identity, positivity, and normal-domain checks pass in natural units.

WHAT_REMAINS_OPEN: Vacuum counterterm/renormalization and interacting thermal
self-energy are not included. The condensate/Goldstone/normal two-fluid sector,
physical Kubo coefficient, SK/KMS matching, SI Phi map, and `alpha_Phi_K` remain
open.

DEPENDENCY_UNLOCKED: Action-derived normal-background lane only. Full Topic 13,
physical transport, Core, and Gravity remain blocked.

STATUS: `PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE`

WHAT_CHANGED: Added the one-loop normal branch and machine-readable audit, then
synchronized it into the Topic 13 full gate, major-result register, dependency
gate, formula audit, current-state report, update log, and work ledger.

EQUATION_OR_MAPPING:

```text
E_k = sqrt(k^2 + m_eff(Phi)^2)
Omega_N^(1,T) = T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))] d^3k/(2 pi)^3
partial p_N/partial Phi = -(partial m_eff^2/partial Phi) * 1/2 integral[(n_-+n_+)/E_k] d^3k/(2 pi)^3
```

VERIFICATION: Action mass derivative, pressure derivatives, positivity,
normal-domain condition, and explicit exclusion of vacuum/condensate/two-fluid
completion pass. No physical Kubo value, SI scale, alpha, target, or holdout is
used.

CONTROLLING_BLOCKER: `vacuum_counterterm_and_renormalized_one_loop_response_not_closed`

NEXT_ACTION: Close or explicitly bound the vacuum/interaction layer, then derive
the condensate/two-fluid sector and match physical Kubo/SI Phi observables.

CLAIM_BOUNDARY: Action-derived thermal normal-background lane only. Not a
renormalized full finite-temperature UET action, not a two-fluid derivation,
not physical transport, not SI calibration, and not Full Topic 13 closure.
