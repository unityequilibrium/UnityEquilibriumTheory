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
| observation.system_partition | Boundary; systems(id/role/state); directed couplings(id/source/target/kind/map/component_id); observables(id/detector_id/target_systems/quantity/readout_map/component_id) |
| error_budget | Numerical/approximation/measurement/systematic/omission errors, dependence, acceptance evidence, output-unit omission_limit |
| identities | Each input/config/code/evidence path, role, kind and SHA-256; pinned Git sources also need a full commit |
| entrypoints/evidence | Paths for execution or formal derivation; exact evidence locators |
| review | UNREVIEWED initially; reviewer/rationale, coverage_evidence and reviewed payload scope_sha256 for COMPLETE_FOR_SCOPE |
| claim_boundary/next_action | What this result does not decide; concrete next missing prerequisite |

## Component rows

Use the boundary-first definitions in standard 30 before filling observation prose.
Every coupling/readout references a component below; do not duplicate its disposition,
evidence or error bound in another registry. A DETECTION edge ends at a DETECTOR;
BACKACTION assessments start at that detector and separately cover each declared
SOURCE. No active feedback is required merely because detection exists. Unobserved
subsystems may remain in the graph. For a scope without measurement, observables=[]
and no_detector_reason states why. Omitted edges are not evidence of isolation.
New/revised non-FORMAL contracts need this graph; unchanged legacy contracts retain
their evidence and enter the visible unreviewed queue. Re-review payload identity after
editing it. Do not rename a physical comparison FORMAL to avoid the requirement.

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
