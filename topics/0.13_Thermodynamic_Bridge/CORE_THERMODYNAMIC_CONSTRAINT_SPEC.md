# Topic 0.13 Core Thermodynamic Constraint Specification

## Purpose

This lane defines what Topic 0.13 may export into the core GR/matter-response
program.  It is a constraint contract, not a derivation of the UET bridge.

The central distinction is:

- standard thermodynamic identities may constrain a candidate theory;
- reproducing those identities does not show that UET derived its own equation
  of state, transport coefficients, entropy current, or information-energy
  bridge.

## Allowed exports

While the foundation gate remains `FOUNDATION_WARN`, only these class-C exports
are allowed:

- the Landauer lower bound `E_min = k_B T ln 2` as an imported constraint;
- Bekenstein, Unruh, and Hawking relations as standard formula constraints;
- Cattaneo as an analytical and synthetic control-system benchmark.

The current Cattaneo artifact is `SIMULATION_ONLY`; it is not external
heat-transport validation.

## Blocked derivation shortcuts

- Landauer cannot be used to derive `beta`, the charge-density equation of
  state, mobility, relaxation, or any core coupling coefficient.
- A zero engine-versus-CODATA residual shows identity consistency, not a
  non-circular UET mechanism.
- The normalized thermal-pilot `Phi` and trace `R` are not measured
  temperature, heat flux, entropy, or information matter.
- Trace remains derived and has no feedback path.
- Standard Bekenstein/Unruh/Hawking formulas do not close the core entropy
  current or dissipative Bianchi identity.

## Required gates

1. `foundation_constraint_export_gate == PASS` for the two allowed class-C
   export families;
2. `landauer_coefficient_non_derivation_gate == PASS`;
3. `cattaneo_simulation_control_gate == PASS`;
4. `trace_phi_observable_separation_gate == PASS`;
5. `row_controller_preservation_gate == PASS`;
6. `uet_bridge_derivation_gate == BLOCKED`;
7. `thermal_pilot_physical_gate == BLOCKED` while pre-arrival leakage and
   external-source readiness fail;
8. `core_eos_transport_entropy_gate == BLOCKED`;
9. `topic_promotion_gate == BLOCKED`.

## Status and controllers

Topic 0.13 remains `Draft / Tier B` with `topic_status_impact = NONE`.
`FOUNDATION_WARN` and the four Berut/Jun/Hong/Peterson row controllers remain
unchanged.

The controller for this dependency lane is:

```text
topic_0_13_constraint_only_eos_transport_entropy_bridge_missing
```

The core controller remains:

```text
noether_charge_equation_of_state_and_covariant_transport_matching_missing
```

## Required next evidence

- close the four source-row controllers with archived numeric/source surfaces,
  uncertainty, and mapping rules;
- derive a non-circular UET bridge and close the proxy-to-SI units contract;
- repair causal pre-arrival leakage under the unchanged threshold;
- attach licensed dimensional heat-transport data with preprocessing and
  uncertainty;
- derive or independently calibrate EOS/transport and construct entropy-current
  and dissipative-Bianchi closure.

## Claim boundary

Topic 0.13 may constrain the core with standard lower bounds and identities and
may provide synthetic controls.  It does not derive the UET bridge, beta, EOS,
transport, entropy current, or a dimensional `Phi/R` observable and does not
promote either Topic 0.13 or the core program.
