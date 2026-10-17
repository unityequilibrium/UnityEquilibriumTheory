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
| error_budget | Numerical/approximation/measurement/systematic/omission errors, dependence, acceptance evidence, output-unit omission_limit |
| identities | Each input/config/code/evidence path, role, kind and SHA-256; pinned Git sources also need a full commit |
| entrypoints/evidence | Paths for execution or formal derivation; exact evidence locators |
| review | UNREVIEWED initially; reviewer/rationale, coverage_evidence and reviewed payload scope_sha256 for COMPLETE_FOR_SCOPE |
| claim_boundary/next_action | What this result does not decide; concrete next missing prerequisite |

## Component rows

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
