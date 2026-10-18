# UET Equation Research and Physical Correspondence Standard

The scoped [Calculation and Observation Completeness Standard](30_Calculation_and_Observation_Completeness_Standard.md)
extends F0-F8 with component, observer, correction and error-budget contracts.
It introduces no additional scientific PASS and never bypasses a required F gate.

This is the canonical workflow for creating, reviewing, implementing, and promoting
UET equations. It supplements the project constitution, lifecycle, formula-audit, and
hardening standards; it does not replace them.

## Purpose

Prevent an equation from being implemented or compared with data before its symbols,
units, standard-physics correspondence, derivation status, and observable mapping are
explicit.

The unit of progress is a closed, auditable correspondence chain, not the number of
topics, equations, scripts, or figures added.

## Mandatory order

Every foundational or operator-like equation follows this order:

```text
F0 Inventory
→ F1 Ontology
→ F2 Physical correspondence
→ F3 Units
→ F4 Derivation
→ F5 Formal verification
→ F6 Numerical verification
→ F7 Observable mapping
→ F8 Data and claim gate
```

No downstream gate may be marked `PASS` while a required upstream gate is `BLOCKED`.
`WARN`, `PARTIAL`, `DIAGNOSTIC_ONLY`, and `SIMULATION_ONLY` do not satisfy a required
dependency.

Topic numbers are labels, not a research sequence. The dependency graph and the current
machine-readable gate decide what may be worked on next.

## F0 — Inventory

Before adding a new equation, inventory the relevant:

- equation text and code paths
- parameters and constants
- topic dependencies
- verifier scripts and artifacts
- sources, datasets, and unit conventions
- existing legacy or comparator implementations

Classify each item as one of:

- `foundational_equation`
- `constitutive_lane`
- `numerical_implementation`
- `observable_definition`
- `application_model`
- `legacy_or_comparator`

An initial inventory may be incomplete, but it must say so explicitly and keep the
foundation gate `BLOCKED` until the missing scope is named.

## F1 — Ontology

Before composing equations, declare the subsystem boundary and directed physical
couplings under the boundary-first section of standard 30. Distinguish internal
impact, receiver-side effect, detector state, observable/readout and source backaction.
An internal interaction does not imply an observable external signal; a received
signal does not imply significant reciprocal source disturbance. These are separate
claims requiring separate models/bounds. A missing edge is unassessed, not zero.
The same physical event may have an impact and a receiver-side effect; they are not
two invented force species. Detector is a system; observable is a defined quantity.

Every symbol must have a mathematical role and a physical interpretation status.

The current core contract is:

| Symbol | Core meaning | Prohibited shortcut |
| :-- | :-- | :-- |
| `C` | system-state coordinate; realization is lane-dependent | calling it universally mass |
| `Phi` | effective space-response variable | calling it metric, ether, particle, or information |
| `Pi` | response rate, `∂t Phi` | treating it as an independent substance |
| `R` / `I_trace` | derived causal/history observable | treating it as an energy reservoir or feedback field |
| `Omega` | functional whose physical status must be named | calling every normalized functional physical energy |
| `E` | energy ledger quantity with a declared unit lane | silently mixing effective and SI energy |

Mass, density, charge, current, and stress-energy are separate quantities unless a
lane-specific mapping defines otherwise.

## F2 — Physical correspondence

Every physical interpretation must be recorded as:

```text
UET variable or relation
↔ standard-physics counterpart
↔ measurement observable
```

Permitted examples include:

- `C ↔ rho` in a declared mass-density lane
- `C ↔ n` in the O(2) Noether-charge lane
- `C ↔ order parameter` in a phase-transition lane
- `m` or `m_eff` as a mass parameter in a field realization
- `R ↔ causal convolution of dissipation` as a derived proxy

These are distinct realizations, not a universal identity for `C`.

If no standard counterpart or measurement operator is available, the entry remains
`BLOCKED` for physical claims. It may still be used as an explicitly labelled
mathematical or exploratory model.

## F3 — Units

Every equation selects one unit lane:

- `normalized`
- `natural_units`
- `SI`
- a named topic-specific dimensional lane

The audit must record dimensions, conversions, parameter units, and whether the output
is directly measurable. A normalized equation may support internal simulation but not a
dimensional physical claim without a completed unit and observable map.

## F4 — Derivation

Every relation receives exactly one primary origin label:

- `identity`
- `derived_relation`
- `variational_derivation`
- `tree_level_derivation`
- `source_locked_physics_constant`
- `source_locked_benchmark_input`
- `constitutive_ansatz`
- `heuristic_bridge`
- `calibration_dependent_relation`
- `numerical_approximation`
- `open_derivation_target`

The record must expose the chain:

```text
assumption → derivation → approximation → fitted parameter → prediction
```

An ansatz is not a first-principles derivation. A fit is not a prediction. A numerical
implementation is not evidence that the underlying physical interpretation is correct.

## F5 — Formal verification

Before a relation is used downstream, check the applicable items:

- analytic and directional derivatives
- stationarity or equation-of-motion residuals
- conservation laws
- symmetry and covariance
- positivity and stability domain
- reciprocity and first-law relations
- closed, open, and limiting cases
- energy and entropy accounting
- parameter-domain rejection

The verifier must report the exact relation, tolerance, input configuration, and result.

## F6 — Numerical verification

Numerical work must establish:

- temporal and spatial convergence
- explicit stability preflight
- no field clipping or hidden cone padding
- no NaN or silent fallback
- reproducible configuration and seed
- causal support or declared propagation limit
- conservation drift and ledger closure
- deterministic artifact generation

Synthetic work has status `SIMULATION_ONLY`; internal reruns have status `INTERNAL`.
Neither is external validation.

## F7 — Observable mapping

Use `observation.system_partition` in the existing calculation contract to connect
each declared observable to its receiver and admitted input path. Do not require all
internal states to be observable, insert a serial trace/carrier stage unsupported by
the model, or silently add observation-derived feedback to the source. Assess detector
backaction separately even when the source and detector are treated as subsystems.
Changing a partition, readout, detector state law or omitted coupling requires scope
review; source dynamics change only through the declared physical couplings.

Before fitting or comparing data, define a measurement operator:

\[
y_{\\mathrm{pred}} = \\mathcal O[C,\\Phi,\\Pi,R].
\]

The mapping record must state:

- what the instrument or dataset measures
- preprocessing and filtering
- uncertainty and resolution
- nuisance parameters
- unit conversion
- whether the quantity is direct or a derived proxy
- which model parameters are allowed to enter the map

No observable map means no data fit and no empirical claim.

## F8 — Data and claim

The data sequence is:

```text
source lock
→ provenance and hash
→ preprocessing lock
→ parameter lock
→ calibration or fit
→ holdout test
→ external comparison
→ claim review
```

Required separations:

- fit versus prediction
- internal benchmark versus external validation
- synthetic control versus sourced observation
- mathematical consistency versus physical truth
- support versus falsification

Data can support or falsify a declared prediction; it does not prove a theory in an
absolute sense.

## Equation registry contract

Every important equation entry must include:

```text
equation_id
version
classification
relation_or_code_path
variables
mathematical_role
standard_physics_counterpart
observable_mapping
unit_lane
parameter_dimensions
source_or_origin
assumptions
symmetry_and_conservation
limiting_cases
implementation_paths
verifier_paths
evidence_class
proof_status
downstream_dependencies
claim_boundary
failure_mode
next_hardening_step
```

Missing fields are not silently filled by prose. They are recorded as `open` and can
block a dependent claim.

## Status vocabulary

Use the following status families without promotion by implication:

- `DRAFT`
- `LEGACY`
- `CANDIDATE`
- `WARN`
- `INTERNAL`
- `SIMULATION_ONLY`
- `EXTERNAL_COMPARISON`
- `PASS`
- `BLOCKED`

`PASS` applies only to the named gate, not to the whole UET framework. Human review is
required for any upward claim or readiness change.

## Wave protocol

One research wave must contain:

1. one controlling blocker
2. one registry, artifact, manifest, verifier, or doc change
3. a rerun only when evidence-producing state changed
4. synchronized claim wording
5. one update-log entry
6. one scoped commit

The next wave may not start by adding scope if the current controller is still vague.

## UET-specific foundation rule

The current matter-space chain is:

\[
(C,\\Phi,\\Pi)
\rightarrow
(\\mu_C,\\mu_\\Phi)
\rightarrow
\\text{physical dynamics}
\rightarrow
\\sigma
\rightarrow
R=I_{\\mathrm{trace}}.
\]

`R` is derived from the physical history and has no feedback edge in the new mode.
The legacy `I` field and the new `I_trace` meaning must not be merged without an
explicit migration record.

The O(2) EOS and covariant superfluid work is a lane-specific realization. It cannot
silently redefine the universal meaning of `C`, mass, energy, or space response.

## Stop conditions

Stop and mark `BLOCKED` when:

- variable meanings are ambiguous
- unit closure is missing
- a constant has no origin
- a standard-physics correspondence is absent
- an observable map is absent
- an upstream dependency is blocked
- a fit is being used as a prediction
- a causal, conservation, or ledger test fails
- public wording is stronger than the current artifact

## Required review references

- [01_Project_Research_Constitution.md](./01_Project_Research_Constitution.md)
- [02_Project_Workflow_and_Lifecycle.md](./02_Project_Workflow_and_Lifecycle.md)
- [17_Formula_Audit_Standard.md](./17_Formula_Audit_Standard.md)
- [18_Research_Hardening_Workflow.md](./18_Research_Hardening_Workflow.md)
- [24_TEMPLATE_UPDATE_LOG.md](./24_TEMPLATE_UPDATE_LOG.md)

## Impact/effect/carrier extension

The foundation program uses the following causal separation:

```text
{b_i} -> impact -> B_sys -> C -> (mu_C, mu_Phi) -> physical dynamics -> sigma -> R_gen -> carrier -> R_obs/effect
```

`impact` is a physical coupling. `carrier` is a declared propagation channel. `effect` is the receiver-side consequence of a carrier/detector interaction and is not an independent field. `information` is a state, correlation, or detector-computed payload; it is not automatically a new substance. `R_gen` and `R_obs` are distinct layers.

The model may include receiver feedback only when it is implemented as an explicit receiver-dynamics source/input with a unit lane, conservation or ledger rule, detector map, and causal propagation law. The current `matter_space_coupled_v1` operator remains trace-only: `R_gen` is derived after physical dynamics and does not feed back into `C`, `Phi`, or `Pi`.

A mass-bearing-to-carrier transition is a `CANDIDATE_TRANSITION_HYPOTHESIS`, not a universal particle identity. Photon, neutrino, positron, and gravitational-wave lanes require separate source, propagation, conservation, detector, observable, and falsification records.

Global-universe openness, a photon/neutrino identity for `I_trace`, and a closed-limit derivation of Einstein/GR are blocked until their correspondence and observable gates pass.
