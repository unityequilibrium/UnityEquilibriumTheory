# Calculation and Observation Completeness Standard v1

Status: operating standard; extends F0-F8, never replaces a scientific gate.

## Meaning of completeness

A calculation is complete only for its declared question, system, validity domain,
observable and accuracy. This is not a claim to simulate all of reality or exclude
unknown physics. Unknown contributions remain visible. More metadata is not new
scientific evidence.

Use one versioned `CALCULATION_CONTRACT.json` per independently reviewable calculation
path, or an existing manifest's `calculation_contract` object. Multiple paths in one
workspace may use named JSON files in `calculation_contracts/`. Do not create a
contract per arithmetic operation, cell, parameter sample or repeated run.

The schema is [calculation_contract_v1.schema.json](../../meta/schemas/calculation_contract_v1.schema.json).
The checker is [audit_calculation_completeness.py](../../scripts/audit/audit_calculation_completeness.py).

## Required contract

Declare the question, output and unit, validity domain, accuracy criterion, model and
formula IDs, assumptions/approximations, initial/boundary conditions, drive and
environment. Distinguish fixed, derived, calibrated and fitted parameters and name
calibration, comparison and holdout data by source identity. Parameter counts alone
do not prove identifiability; use the applicable derivation/rank or counterexample.

Profiles:

| Profile | Required interpretation |
| --- | --- |
| FORMAL | A bounded mathematical statement, assumptions and approximation/proof domain. Instrument conditions may be inapplicable with reasons. |
| SYNTHETIC | Declared synthetic state, inputs, outputs, solver and error controls. Does not validate a material or SI interpretation. |
| PHYSICAL_COMPARISON | Physical correspondence, dimensional observable, material/protocol state, observer/instrument and upstream processing. Includes exploratory real-data comparisons. |

Using real observations in an inference requires PHYSICAL_COMPARISON even if the
result is exploratory. Synthetic controls may cite a publication as a formula source
without using its observations. Record that distinction in `data_policy`.

## Component ledger

Assess at least: system state; drive/environment; signal propagation; frame/time;
detector/observer; processing; numerical method. Each component has one disposition:

| Disposition | Evidence required |
| --- | --- |
| MODELED | Equation/method and implementation or formal derivation reference. |
| UPSTREAM_CORRECTED | Dataset identity, processing/product level, correction identity and evidence it was applied. Never reapply it silently. |
| BOUNDED_OMISSION | Effect bound in output units, supporting derivation/test, joint-group treatment and allocated error budget. |
| NOT_APPLICABLE | A reason tied to this output and domain; not a blanket exemption. |
| UNKNOWN | Missing prerequisite, accountable owner and next action; no implicit zero. |

List individual effects where their treatment differs. A group-level row must state
its scope and known subeffects. Structural validation cannot establish that the
ledger includes every relevant physical effect: record a substantive review.

## Observer and thermodynamic boundaries

Distinguish source state, generated trace, physical carrier, detector interaction,
receiver state and recorded value. R_gen is not the source's complete state, and
R_obs is a record rather than an independent substance. A dissipation-history trace
does not encode all reversible dynamics. Energy-functional descent alone does not
establish physical entropy production or a universal entropy-organizing field.

Include relevant observer trajectory, velocity, orientation, clock/time convention,
temperature, gain, resolution, memory and response time. A source-locked prescribed
trajectory is valid; solving a spacecraft orbit again is not mandatory. Specify
exposure integration and reference-frame transformations where relevant. Readout
metadata does not create physical backaction: model an actual coupling and exchange
ledger, or bound its omission. A full waveform/amplitude claim needs more detector
information than a mode-identified phase-speed comparison; assess the actual claim.

For astronomy record frame, epoch, time scale, instrument, exposure/product identity
and Doppler/aberration/timing correction history as applicable. Published H0 values
are derived summaries, not raw HST exposures. Unknown upstream details restrict
claims; do not invent a spacecraft correction or apply one to a published H0 scalar.

## Error and evidence policy

Separate numerical, approximation, measurement, systematic and omitted-effect error.
Set the acceptance rule before scoring data. Bound omissions conservatively in the
output unit; sum group bounds rather than assuming independent errors. Correlated
effects require a joint bound. Missing covariance permits justified conservative
enclosures, not invented independence or statistical confidence levels. If a bound
is unavailable, mark UNKNOWN and restrict the result to its diagnostic/formal scope.

Record source/config/code identities and exact evidence locators. Text identity uses
SHA-256 after CRLF/CR to LF normalization; binary identity uses raw bytes. Scientific
JSON payloads are not otherwise normalized. Pinned Git evidence uses a full commit
and repository-relative path; it must not be presented as the active checkout's code.
Unresolved or missing pinned objects are gaps, never a fallback to a different file.
For owner work on an unmerged local branch, explicitly mark a pinned identity
LOCAL_ONLY and keep its review INCOMPLETE/diagnostic. A fresh clone reports missing
local evidence as a gap; it cannot use that exception for COMPLETE_FOR_SCOPE or
physical acceptance. This avoids silently fetching or publishing owner work.

Source, configuration, model, measurement or scope changes require review. Unchanged
evidence may be reused. Generated scientific artifacts are changed through their
producer only. New producers attach `contract_id`, canonical contract hash and
input/config/code identities using the checker's `artifact_metadata` helper.

## Review, execution and scientific result

Review states are UNREVIEWED, INCOMPLETE, COMPLETE_FOR_SCOPE and STALE. They are
independent of execution outcome and all existing physics/claim gates. Structural
errors or changed identities cannot be hidden by a recorded COMPLETE_FOR_SCOPE.
Reviewer name and rationale are required; machine schema PASS is not physics review.
COMPLETE_FOR_SCOPE also binds `review.scope_sha256` to the canonical contract payload
excluding the review object. Scope/model/parameter/observer-policy edits invalidate
that sign-off until explicitly reviewed again. For physical acceptance record a
finite output-unit `error_budget.acceptance_limit`, sourced acceptance evidence and
an omission allocation no larger than that limit. Existing gates must independently
be in accepting states; BLOCKED/PARTIAL cannot be whitelisted as accepting.

Incomplete derivations and diagnostic comparisons may run with explicit gaps.
Physical acceptance additionally requires COMPLETE_FOR_SCOPE, no unresolved relevant
components, non-overlapping calibration/independent-validation roles, quantitative
error criteria, and the applicable existing physics gates. No automatic promotion.

## Enforcement and gradual adoption

Run `python docs/scripts/audit/audit_calculation_completeness.py --check` before
handoff. Use `--inventory --emit-report` to generate the compact coverage report and
`--changed BASE_REF --check` for a changed calculation-path check. The baseline
records pre-standard entrypoints as UNREVIEWED; it is not a scientific exemption.
Unchanged legacy paths stay in the review queue. New or changed scientific paths
need a contract or an explicit support/test disposition. New result artifacts need
producer/contract lineage. Existing consumers tolerate additive contract metadata.

Inventory by equation IDs, verifiers, scientific entrypoints and topic verification
specs. Deduplicate shared code; never equate file count with experiment count. Start
with matter-space/observer, He-4 and nonlinear-response pilots; then published-H0,
galaxy and dynamic-frame data paths; then remaining topics by dependency and claims.

Preserve old artifacts. Record whether a legacy claim can be reused within its old
scope, needs restriction, needs rerun, or awaits inputs. Rerun only changed producers
or demonstrated stale results. Superseding results retain a link to the old evidence.
Log actual changes in UPDATE_LOG and WORK_LEDGER and commit scoped units. Avoid
duplicate data, embedded historical reports and repeated no-change output growth.

## Acceptance checks

Test missing fields, unknown contributions, omission budgets and joint groups,
stale hashes, calibration reuse, duplicate corrections, unit/frame mismatches,
read-only checks, changed-path enforcement and legitimate formal exemptions.
Observer controls must cover velocity-dependent raw measurements and frame recovery,
state-dependent readout, explicit backaction, metadata-only invariance and observable
changes in a lossless system. These are synthetic controls, not new UET predictions.
