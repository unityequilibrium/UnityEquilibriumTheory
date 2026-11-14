# Topic 13 Research Wave: Physical Kubo Provenance Gate

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The minimum state-matched Kubo coefficient record and
source-provenance contract is linked to the implemented Landau-frame transport
interface. Existing external records are classified as structure/readiness
sources only.

WHAT_REMAINS_OPEN: No physical coefficient record with a value, units, state
point, correlator locator, source hash, and accepted evidence status is present.
Finite-temperature normal response, curved 3+1 transport, and the base-Phi SI
anchor remain open.

DEPENDENCY_UNLOCKED: Kubo coefficient acceptance gate only. No physical
transport, Full Topic 13, Gravity, or external-validation dependency is
unlocked.

STATUS: `PASS_KUBO_PROVENANCE_GATE_OPEN_PHYSICAL_COEFFICIENT`

WHAT_CHANGED: Added the machine-readable Kubo provenance audit and linked the
existing external readiness records to the transport acceptance boundary.

EQUATION_OR_MAPPING:

```text
KuboCoefficientRecord -> constitutive coefficient
```

The mapping is allowed only when the record carries a value, declared units,
state point, correlator locator, source hash, and accepted evidence status.

VERIFICATION: The current transport verifier still reports
`physical_coefficient_evidence=BLOCKED_NOT_PROVIDED`; synthetic coefficients
remain simulation-only and no Xie 2026 or TTG target data is used.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`

NEXT_ACTION: Acquire or microscopically derive one state-matched coefficient
record, then rerun the transport verifier and its unit/state matching checks.

CLAIM_BOUNDARY: This is a provenance gate, not a physical transport result,
Kubo match, finite-temperature completion, alpha calibration, or Full Topic 13
closure.
