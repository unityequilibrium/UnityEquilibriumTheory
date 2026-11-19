# Calculation contract template

Use the [v1 schema](../../meta/schemas/calculation_contract_v1.schema.json) and
[standard](30_Calculation_and_Observation_Completeness_Standard.md). Copy the
closest scoped pilot under a topic's `calculation_contracts/` directory, or embed
the object as `calculation_contract` in its existing manifest and register that
locator in the baseline's `embedded_contracts`. Never clone an entire dataset.

## Execution card

| Field | Complete before claiming a result |
| --- | --- |
| contract_id/profile | Stable unique path ID; FORMAL, SYNTHETIC or PHYSICAL_COMPARISON |
| question/output | One question, quantity/unit/domain/accuracy and claim intent |
| model | formula_ids; assumptions; approximation; initial_boundary; drive_environment; parameters |
| data_policy | Observations used? Calibration/comparison IDs, independence evidence, holdout policy |
| observation | Source state; trace scope; carrier; observer state; readout; backaction; frame/time; product level; corrections |
| observation.system_partition | RELATIONAL role_mode; boundary/time/accuracy; systems(id/state/state_accounting, optional parent_id/categories); accounting_component_id; couplings(id/source/target/kind/map/component_id); observables(id/detector_id/target_systems/readout_map/component_id/backaction_targets/backaction_scope_reason/quantity); boundary_change when revising an existing partition |
| error_budget | Numerical/approximation/measurement/systematic/omission errors, dependence, acceptance evidence, output-unit omission_limit |
| identities | Each input/config/code/evidence path, role, kind and SHA-256; pinned Git sources also need a full commit |
| entrypoints/evidence | Paths for execution or formal derivation; exact evidence locators |
| review | UNREVIEWED initially; reviewer/rationale, coverage_evidence and reviewed payload scope_sha256 for COMPLETE_FOR_SCOPE |
| claim_boundary/next_action | What this result does not decide; concrete next missing prerequisite |

## Component rows

Use the boundary-first definitions in standard 30 before filling observation prose.
Every coupling/readout references a component below; do not duplicate its disposition,
evidence or error bound in another registry. In RELATIONAL mode DETECTION defines
the receiving role for that relationship; the same system can supply another one.
BACKACTION assessments start at that receiver and cover its justified observable
scope, at least the observed targets other than itself. No active feedback is
required merely because detection exists. Unobserved
subsystems may remain in the graph. For a scope without measurement, observables=[]
and no_detector_reason states why. Omitted edges are not evidence of isolation.
New/revised non-FORMAL contracts need this graph; unchanged legacy contracts retain
their evidence and enter the visible unreviewed queue. Re-review payload identity after
editing it. Do not rename a physical comparison FORMAL to avoid the requirement.

State accounting: INDEPENDENT systems own unique state_ids; AGGREGATE/VIEW nodes
reference owner_ids and add no new degrees of freedom/storage. Include a rule and
existing component evidence for state and interaction-energy accounting. Use parent_id
for acyclic containment; categories cannot waive couplings. For changed boundaries,
reference the old contract identity/hash and mapping evidence with an explicit
equivalent/approximate/different/unresolved outcome. See standard 30 for exact fields.
Unchanged LEGACY_FIXED graphs remain readable under their old semantics; do not mix
fixed roles and relational fields or rewrite old scientific artifacts for compliance.

Include `system_state`, `drive_environment`, `propagation`, `frame_time`,
`detector`, `processing`, `numerics`. Add separate effects when their treatment
differs. Every row has `id`, `group`, `disposition`, `reason`, `evidence`.

- MODELED: reference its implementation or formal derivation.
- UPSTREAM_CORRECTED: list a correction with APPLIED_UPSTREAM and its product evidence.
- BOUNDED_OMISSION: add finite `bound`, output `unit` and `joint_group`; justify the combined budget.
- NOT_APPLICABLE: explain why in this exact scope.
- UNKNOWN: add `owner` and `next_action`; retain INCOMPLETE for the affected claim.

For dimensional comparisons set `comparison_unit` and `comparison_frame` in
observation. If they differ from output unit/model frame, supply
`unit_conversion_evidence`/`frame_transform_evidence`. These locators require
substantive review; the checker cannot prove that a transformation is physically valid.

New producers call `artifact_metadata(contract, root)` in the audit module and
merge the returned metadata into the generated result. Validate using `--check`;
the report generator alone never grants physical acceptance.
