# Topic 0.19 Core GR Program Dependency Specification

## Purpose

This lane records how the current `docs/core` GR-response research program may
be referenced by Topic 0.19 without replacing the topic's CODATA checkpoint,
physical GR benchmarks, or claim ceiling.

The core program now contains substantially more mathematical candidate
infrastructure than the Topic 0.19 primary artifact.  That is useful progress,
but it is not equivalent to physical validation of general relativity.

## Accepted core scope

The dependency gate may accept these bounded statements:

- the implemented candidate tensor evaluator has an exact response-null at
  `epsilon_nc = 0`;
- the conservative candidate parent has a local exchange-completed covariant
  identity;
- the declared flat local 1+1 constitutive kernel has exact retarded support;
- a partial response-sector reduction exists under explicit scaling;
- a fixed-scale coarse signed-charge coordinate map exists, while microscopic
  reconstruction is many-to-one.

The response-null means that implemented UET response corrections vanish.  It
does not mean the complete universe is closed, and it does not by itself derive
or solve the Einstein metric equations.

## Independent Topic 0.19 scope

The existing primary artifact remains a Claim Class C source-constant
checkpoint:

- the engine `G` value matches the local CODATA working copy;
- Planck units are standard derived definitions;
- `gravity_claim_scope_gate.controller_status` remains `WARN`;
- light bending, perihelion precession, MICROSCOPE eta, Eot-Wash, metric/EFE,
  singularity, and quantum-gravity branches remain blocked.

The dependency gate does not rerun or rewrite that artifact.  It hashes the
scientific JSON payload while excluding declared timestamp/environment fields,
so timestamp-only local reruns do not become new evidence.

## Required gates

1. `core_program_stage_gate == PASS` only while the program remains a blocked
   class-B candidate;
2. `exact_gr_response_null_gate == PASS` only with zero implemented residuals
   and `metric_pde_solved == false`;
3. `local_covariant_balance_gate == PASS` only with global theorem and curved
   derivative claims absent;
4. `causal_constitutive_scope_gate == PASS` only for the declared flat local
   1+1 lane;
5. `partial_response_reduction_gate == PASS` while full coupled reduction
   remains blocked;
6. `topic_constant_checkpoint_preservation_gate == PASS`;
7. `physical_gr_benchmark_gate == BLOCKED`;
8. `covariant_completion_gate == BLOCKED`;
9. `topic_promotion_gate == BLOCKED`.

## Status and controllers

Canonical Topic 0.19 status remains `Draft / Tier B`, with
`topic_status_impact = NONE`.  The topic's existing machine-readable physical
blockers remain unchanged.

The core controller remains:

```text
noether_charge_equation_of_state_and_covariant_transport_matching_missing
```

The Topic 0.19 dependency controller is:

```text
topic_0_19_classical_gr_tests_and_covariant_completion_missing
```

Global universe closure remains `UNRESOLVED`.  `epsilon_nc` is a dimensionless
nesting coupling, not a measured percentage of how open the universe is.

## Required next evidence

- source-backed light-bending and perihelion artifacts with uncertainty and
  competitor baselines;
- MICROSCOPE eta and Eot-Wash exclusion-curve comparisons;
- a curved 3+1 metric/response solver with convergence and well-posedness gates;
- charge-density EOS, covariant coarse graining, transport/KMS, entropy-current,
  and dissipative-Bianchi completion;
- independent holdout comparison of `epsilon_nc != 0` against the exact
  `epsilon_nc = 0` GR null.

## Claim boundary

Allowed language is limited to candidate mathematical infrastructure and an
exact implemented response-null contract.  This lane does not establish that
UET derives Einstein equations, validates GR, proves the universe open or
closed, resolves singularities, or closes quantum gravity.
