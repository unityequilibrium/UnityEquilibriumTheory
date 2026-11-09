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

### Boundary-first interaction and observation contract

Define the system partition BEFORE identifying a state, trace or response with an
observable. The boundary is a declared modeling choice for this question, timescale
and precision, not proof that separated systems have no interaction.

| Term | Required meaning | Prohibited inference |
| --- | --- | --- |
| Subsystem | A declared set of degrees of freedom and its state | Outside the chosen boundary means physically disconnected |
| Impact | Physical coupling/state change between specified systems | Every internal impact reaches every observer |
| Effect | A receiver-relative consequence of a specified interaction/channel, including receiver behavior or a derived record | A separate force/substance, or necessarily a human interpretation |
| Detector | A physical receiving system with a state and response | The measured quantity itself is a system |
| Observable | A defined quantity/functional/operator used to obtain a predicted or recorded value | All source-state detail, or automatic source feedback |
| Backaction | Detector/receiver influence on the source through a declared physical route | Readout metadata changes source dynamics, or detection implies a large source perturbation |

Impact and effect are not exclusive species of event: one detector interaction can
have a physical impact and a receiver-side effect. An observable is not necessarily
directly read out; its measurement operator and uncertainty must be declared.
Internal source coupling, signal transport, detector coupling, receiver response and
source backaction are distinct edges. Do not force them into a universal serial
pipeline: some channels are absent, unobserved, aggregated, indirect or unresolved.
Do not infer a physical absence from an omitted graph edge.

New or revised non-FORMAL contracts declare `observation.system_partition` with
`role_mode: RELATIONAL`. A system has no permanent source/detector species: its
role follows the particular coupling or observable. One node may receive one
signal and provide another. A category is a modeling label, not physical isolation.
Include timescale, level of description and accuracy in the boundary.

- `boundary`: included/excluded systems, approximation, timescale and accuracy scope.
- `systems`: unique `id` and declared `state`; optional `categories` and `parent_id`.
  Detector and observable IDs are distinct. In RELATIONAL mode omit fixed `role`.
- Every relational system has `state_accounting` with `kind`, `state_ids`,
  `owner_ids`, `rule`. INDEPENDENT systems own nonempty, globally unique state IDs
  and have no owner_ids. AGGREGATE/VIEW systems have no new state_ids and reference
  existing INDEPENDENT owner IDs. State IDs name actual modeled degrees of freedom,
  not arbitrary aliases to evade duplicate checks. AGGREGATE containment is acyclic;
  a parent's owner set covers its children. VIEW is a derived/coarse-grained view,
  not another independently initialized state. Overlapping classifications use views
  or categories rather than copied physical states. The rule explains storage and
  interaction-energy allocation; aggregates are not additive extra energy stores.
- `accounting_component_id` references the existing system_state component, with
  derivation/implementation evidence or UNKNOWN. The checker verifies ownership
  structure, not whether different state names hide the same physical degree of
  freedom, whether all interactions were found, or whether the energy law is valid.
- `couplings`: directed `id`, `source`, `target`, `kind`, `map` and `component_id`.
  Kinds are INTERNAL, SIGNAL, DETECTION, BACKACTION, ENVIRONMENT, RECEIVER_DYNAMICS.
  A directed effective edge does not assert fundamental nonreciprocity or waive
  conservation: justify neglected reverse influence in the same component ledger.
- `observables`: `id`, `detector_id`, `target_systems`, `quantity`, `readout_map`
  and detector/processing `component_id`. Only declared target quantities are claimed
  visible; no requirement exists that every internal coordinate be recoverable.
- Each observable declares `backaction_targets` and `backaction_scope_reason`.
  Include every observed target other than the receiver itself and assess additional
  upstream/unobserved systems when their influence matters to the claim. The reason
  must justify that scope, including mediated feedback and aggregation. BACKACTION
  edges assess each receiver-to-target influence separately; they need not be active.
  Structural inclusion of observed targets does not prove the entire scope adequate.
- With no measurement claim, use an empty observable list and a scoped
  `no_detector_reason`; a formal proof must not invent a detector to fill a form.

Each coupling/readout references an EXISTING component row, not a new status registry.
MODELED requires a law/implementation; UPSTREAM_CORRECTED needs correction provenance;
BOUNDED_OMISSION needs the existing output-unit joint error budget; NOT_APPLICABLE
needs a scope-specific reason (e.g. a synthetic no-feedback definition, not an
unjustified claim of exact physical isolation); UNKNOWN needs owner/next action.
Weak feedback is not zero feedback. A significant/unknown source perturbation cannot
be dismissed because the receiver is geographically external or called an observer.
Distance, propagation delay, velocity/momentum, channel coupling and receiver
susceptibility are assessed where relevant, not compressed into a universal
distance-strength rule. Impact/effect are not large/small-response categories.

When a prior partition is changed, add `boundary_change`: `baseline_identity`
identifies the old contract through an existing identity (path, or git:commit:path),
`baseline_contract_id` and canonical `baseline_contract_sha256` bind its version;
`component_id` points to mapping evidence, `outcome` is EQUIVALENT, APPROXIMATE,
DIFFERENT or UNRESOLVED, and `explanation` states correspondence, error allowance
or the difference. The prior contract is referenced, not copied. EQUIVALENT needs
admitted mapping evidence; UNKNOWN cannot establish it. This is a scoped relation,
not a new science status. Changed scope invalidates an old review hash. The checker
binds the baseline identity but a substantive reviewer must assess equivalence.

Example: A and B interact internally, B supplies a declared channel to D, and D reads
one quantity. This does not expose all of A/B. D-to-A/B influence may be modeled,
bounded, inapplicable to the formal scope or unknown independently of that reading.
The detector itself can be part of a larger modeled system when the boundary expands.

Compatibility: absent role_mode means LEGACY_FIXED; retain the original node-role
interpretation and its per-SOURCE backaction checks. Old contracts are readable,
not silently converted or freshly certified. Relational-only fields in legacy mode
are rejected rather than ignored. The changed-contract check requires RELATIONAL
for non-FORMAL edits. FORMAL work still need not invent an observation apparatus.

The existing checker validates endpoint/component references, declared detection paths,
separate detector/observable IDs and explicit backaction assessments. UNKNOWN routes
remain diagnostic gaps, not accepted physical channels. No graph/schema can prove
exhaustive couplings, complete observability, physical isolation or valid omission bounds;
substantive review remains required. Legacy non-FORMAL contracts without this section
are reported as `system_partition:legacy_unreviewed`, not silently accepted as complete.
No historical scientific artifact is rewritten or downgraded by this metadata addition.

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
Input JSON under Data/shared source packages is an input, not a result artifact:
bind its identity without inserting output-contract fields into the original data.
The changed-path guard covers declared tabular/binary inputs and preparation code;
result JSON retains exact producer/contract lineage checks. Offline analysis of
published summaries may model the input product and processing configuration while
keeping upstream physical correspondence/corrections unknown; it need not invent
a new telescope trajectory or detector simulation. Pin distinct code versions when
unrelated dirty source work is held back, and do not call that a current rerun.

Inventory by equation IDs, verifiers, scientific entrypoints and topic verification
specs. Deduplicate shared code; never equate file count with experiment count. Start
with matter-space/observer, He-4 and nonlinear-response pilots; then published-H0,
galaxy and dynamic-frame data paths; then remaining topics by dependency and claims.

The existing inventory reports equation families, topic packages, scoped contracts
and unassigned research-surface groups as distinct, potentially overlapping units.
It discovers current numbered topics even without a verification spec and includes
formal Core contract/lane/proof/research-note documents as classification candidates.
Resolve old paths only through the explicit migration map; ambiguous aliases are
errors, never basename guesses. A linked contract or shared source file does not
certify the whole package: show resolved/missing/uncovered paths and coverage_scope.

Each discovered route has an `adoption` action, reason, priority basis and next
action. These are work-queue dispositions, NOT new scientific states. Reuse is
limited to a complete, identity-matched scoped contract; missing prerequisites wait;
stale identities or unreviewed family/package surfaces need targeted review first.
Do not infer a required rerun without evidence-producing changes, historical
inactivity from directory names, or full-topic support from a narrow formal proof.
Restrict a claim, mark history-only or supersede a result only after substantive
review records the evidence in its existing owner. Report discovery limits and
unreviewed material explicitly; hidden historical prose/private sources are not
certified by this inventory. Current discovered counts do not promote readiness
or silently replace a conflicting topic-index count.

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
