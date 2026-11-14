# Research Wave: Standard Graphite Transport Comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The archived Georgia Tech graphite row at `573.15 K`
supports a conditional standard comparator. The row's thermal diffusivity,
specific heat, assumed density, and reported conductivity are unit-closed and
hash-linked. The reconstructed conductivity is `74.0939625200673 W m^-1 K^-1`.

WHAT_REMAINS_OPEN: The density has no source uncertainty in this package, the
source quantity is `c_p` rather than source-locked volumetric `c_v`, and no
material-regime mapping to the TTG experiment is closed. This result does not
provide Ding `C_src`, a UET transport coefficient, a base-Phi SI anchor, or
`alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Standard-material comparator lane only. Full Topic 13,
Core curved 3+1, Gravity, and full constitutive transport remain blocked.

STATUS: `PASS_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR_CONDITIONAL`

WHAT_CHANGED: Added the machine-readable comparator audit and synchronized its
source/hash evidence into the Topic 13 gate, major-result register, dependency
gate, formula audit, current-state report, update log, and work ledger.

EQUATION_OR_MAPPING:

```text
c_p^vol = c_p^mass * rho_assumed
k = D * c_p^vol
q_F = -k grad(T)
tau_q dq/dt + q = -k grad(T)
```

VERIFICATION: Unit conversion, source row identity, raw workbook hash,
reconstructed conductivity, finite uncertainty envelopes, synthetic-control
separation, no-alpha-fit policy, and locked Xie 2026 holdout policy pass.
Source-reported `sigma_k` and first-order propagated `sigma_k` are kept as
separate envelopes because source covariance is not locked.

CONTROLLING_BLOCKER: `standard_comparator_is_not_a_UET_Phi_transport_coefficient_or_Ding_C_src`

NEXT_ACTION: Acquire a state-matched physical Kubo coefficient and an
independent base-Phi SI anchor. Keep this comparator as a standard-material
control only.

CLAIM_BOUNDARY: Conditional standard comparator; not UET constitutive transport,
not a Ding PBTE `C_src`, not `alpha_Phi_K`, not a TTG prediction, and not
external validation.
