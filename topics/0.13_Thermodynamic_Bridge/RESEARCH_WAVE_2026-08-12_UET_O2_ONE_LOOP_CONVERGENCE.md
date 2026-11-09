# Research Wave: O(2) One-Loop Normal Branch Convergence

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The action-derived thermal-only one-loop normal branch
has a reproducible numerical plateau. The reference is
`cutoff_factor=70`, `quadrature_order=256`; pressure, response derivative,
scalar density, charge, entropy, energy, and susceptibility remain stable over
the declared cutoff/order sweep.

WHAT_REMAINS_OPEN: Numerical convergence does not close vacuum counterterms,
renormalization, interacting finite-temperature response, condensate/two-fluid
physics, physical Kubo transport, SK/KMS matching, SI Phi mapping, or
`alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Numerical stability of the action-derived normal branch
only. Full Topic 13, physical transport, Core, and Gravity remain blocked.

STATUS: `PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE`

WHAT_CHANGED: Added explicit cutoff and quadrature sweeps, locked a reference
baseline, and synchronized the result into the Topic 13 full gate,
major-result register, dependency gate, formula audit, report, update log, and
work ledger.

EQUATION_OR_MAPPING:

```text
cutoff = 70 * max(T, m_eff, |mu|)
quadrature_order = 256
max relative plateau drift <= 1e-8
```

VERIFICATION: Plateau max drift is below `1e-8`; cutoff-tail and order drift
are below `1e-13`. Low-order high-cutoff cases are disclosed and excluded from
the reference. No fit, target, holdout, alpha, or synthetic replacement is
used.

CONTROLLING_BLOCKER: `vacuum_counterterm_and_renormalized_one_loop_response_not_closed`

NEXT_ACTION: Close or explicitly bound the vacuum/renormalization layer, then
derive interacting finite-temperature and condensate/two-fluid sectors before
physical transport matching.

CLAIM_BOUNDARY: Numerical convergence of the declared thermal-only integral
only. Not a renormalization proof, physical transport result, SI calibration,
external validation, or Full Topic 13 closure.
