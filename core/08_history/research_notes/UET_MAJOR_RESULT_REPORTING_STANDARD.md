# UET Major-Result Reporting Standard

This standard adds a result-level progress layer to the existing room report.
It prevents `PASS`, `WARN`, `BLOCKED`, and `SIMULATION_ONLY` from being counted
as if they were closed scientific results.

## Required result fields

Every active room must state:

```text
MAJOR_RESULT_CLOSURE:
WHAT_IS_ACTUALLY_CLOSED:
WHAT_REMAINS_OPEN:
DEPENDENCY_UNLOCKED:
```

The machine-readable record must contain `major_result_id`, `topic`,
`closure_level`, `what_is_closed`, `equation_or_mapping`, `units`,
`derivation_class`, `observable`, `data_role`, `evidence_artifacts`,
`verification_status`, `open_blockers`, `dependency_unlocked`, and
`claim_boundary`.

## Closure levels

- `OPEN`: no bounded research result is closed.
- `PARTIAL`: one or more sub-results are closed, but the major result remains incomplete.
- `CLOSED_FOR_LANE`: a named lane is internally complete within its declared scope.
- `CLOSED_FOR_CORE`: a bounded result is ready for Core inheritance; global promotion remains disabled.
- `CLOSED_FOR_EXTERNAL_CLAIM`: external evidence and review requirements are complete.

`PASS` is a verification state. It is never, by itself, a closure level.

## Topic 13 boundary

The full Topic 13 gate must keep these layers separate:

- normalized TTG/Phi operators
- the causal branch and the conserved-C structural blocker
- independent `alpha_Phi_K` calibration
- the non-circular UET bridge and `beta`
- EOS, transport, SK/KMS, entropy-current, and dissipative balance
- source provenance, uncertainty, and holdout policy

The locked Xie 2026 source is metadata-only until calibration and comparison
protocols are frozen. No calibration path may read or tune on it.

## Existing room report

After the result-level fields, retain the required room headings:

```text
STATUS:
WHAT_CHANGED:
EQUATION_OR_MAPPING:
VERIFICATION:
CONTROLLING_BLOCKER:
NEXT_ACTION:
CLAIM_BOUNDARY:
```

The standard does not promote readiness or change the meaning of `C`, `Phi`,
`R_gen`, or `R_obs`.
