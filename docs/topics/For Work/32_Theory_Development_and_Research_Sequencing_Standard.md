# Theory Development and Research Sequencing Standard v1

Status: operating method, not a scientific result or a new evidence-tier system.
Primary area: `research-standards`. Applies to theory design, reconstruction and extension.

สรุป: รู้ว่าเสนออะไร ใช้อะไรเป็นฐาน สมมติอะไรเพิ่ม ได้ผลอะไรจำเป็น และต้องผ่านอะไร
ก่อนขยายงาน ใช้หลักฐานเดิม ไม่เริ่มใหม่จากศูนย์ และไม่วัดความก้าวหน้าด้วยจำนวนไฟล์

## 1. Authority and scope

This standard orders research decisions. It supplements the [lifecycle](02_Project_Workflow_and_Lifecycle.md),
[formula audit](17_Formula_Audit_Standard.md), [hardening workflow](18_Research_Hardening_Workflow.md),
[F0-F8](EQUATION_RESEARCH_AND_PHYSICAL_CORRESPONDENCE_STANDARD.md) and
[calculation contracts](30_Calculation_and_Observation_Completeness_Standard.md).
Those remain the authorities for readiness, proof labels, physics gates and review.

TD0-TD6 below are planning stages, NOT new PASS states, topic tiers or numerical grades.
Record evidence and gaps separately per stage; never infer a completed prefix from an
advanced branch. An existing contract or gate remains the single scientific controller.
Do not copy artifacts, create a new registry, or require a file per stage.

Exploratory FORMAL/normalized models may proceed with physical correspondence explicitly
open under the existing F2 exception. They still need mathematical definitions, declared
normalization, assumptions and applicable checks. They cannot bypass physical F gates.
Purely analytic work need not acquire data or implement a numerical solver.

### Applicability and evidence types

MUST means required for the claim in its stated scope; WHEN RELEVANT means assess
applicability and record a reason if omitted; examples/templates are illustrative,
not extra gates. Use the existing contract/METHOD, not a second form.

| Profile | MUST | WHEN RELEVANT / legitimate non-applicability |
| --- | --- | --- |
| FORMAL | Definitions, assumptions, proposition, derivation/proof or counterexample, admissible domain and limitations | Numerical metrics, datasets, instruments and solver may be inapplicable; identify imported results and proof dependencies instead |
| SYNTHETIC | Explicit state/input/output, chosen laws and parameters, initial/boundary conditions, computational method and error controls | Physical apparatus/SI map not required for a normalized model; no material-validation claim follows |
| PHYSICAL_COMPARISON | Physical correspondence/units, actual data product and parameter provenance, measurement/processing model, uncertainty and scoped comparison rule | Use supported upstream correction/calibration or prescribed trajectories; do not resimulate irrelevant instrument detail or double-correct data |

A physical-data diagnostic uses PHYSICAL_COMPARISON even when incomplete. Unknown
effects remain limitations; they block only conclusions dependent on them, not
independent formal or diagnostic work. Do not relabel observed data as synthetic.
For a formal proof, a logical contradiction/counterexample can be the rejection
criterion; no fabricated numerical threshold or empirical holdout is required.

Distinguish evidence types without adding a readiness ladder:

- Mathematical verification checks a stated implication under its assumptions;
  numerical verification checks implementation/approximation in a declared domain.
  Neither alone establishes correspondence with nature.
- Physical validation/comparison evaluates declared predictions against measurements
  with uncertainty and alternatives. It supports or rejects a scope, not absolute truth.
- Calibration estimates declared parameters; fitting adjusts them to the scored data.
  A predictive test locks the model/parameter policy and rejection rule before its
  reserved comparison; prior exposure must be recorded, not relabeled as fresh holdout.
- Equivalence, a counterexample, rejection and inconclusive evidence are valid outcomes.
  Novelty is a separate question from consistency, useful application and empirical fit.
- Human/expert review must name reviewer competence, exact question, sources examined,
  disposition and unresolved objections. Required specialist judgment cannot be replaced
  by a schema PASS, AI consensus or author approval of intended meaning.

The [entrypoint ownership map](00_README.md#authority-layers-and-requirement-owners)
links the external measurement, reproducibility and integrity sources. This section
controls profile applicability for 01/04/18/20/25; it does not waive applicable
F0-F8 physical gates or require every field for every research type.

## 2. Reconstruct before redesigning

Start with the current canonical model/contract and last decision-producing results.
Then trace only the historical sources needed to explain unresolved design choices.
Identify worktree, branch, commit and dirty/local-only evidence; do not silently combine
results from different versions. A date or a file title is not an identity match.

For each consequential concept or term, record in the existing METHOD, formula audit,
claim map or research-design note:

| Field | Required distinction |
| --- | --- |
| Intended proposition | Exact claim, domain and what it does NOT claim |
| Provenance | Source locator; human statement, AI proposal, imported theory or later reconstruction |
| Author decision | Explicitly accepted, rejected, deferred or unknown; do not infer acceptance from presence in an archive |
| Translation | Mathematical object/term, derivation or ansatz, and why this choice rather than an alternative |
| Existing evidence | Exact formula/code/artifact identity and its original scope |
| Disposition | Reuse, superseded, disputed, missing, or needs author/expert review; with a reason |

Preserve rejected and superseded history without using it as an active premise. An AI
summary is not a verbatim author statement. Matching acronyms or symbols do not establish
shared authorship, units or theory identity. State coverage limits rather than claiming
to have recovered every idea from all archives/chats.

## 3. Development ladder

| Stage | Question and exit evidence | Existing authority |
| --- | --- | --- |
| TD0 Proposition | One bounded proposition, definitions, non-goals, prior work and unresolved author choices. Separate analogy from physical hypothesis. | F0-F1, claim map |
| TD1 Minimal model | State, inputs, memory, outputs, initial/boundary conditions and admissible domain. Explain each independent state and term; distinguish a derived statistic from an additional dynamical degree of freedom. | F1, F3-F4, FORMAL/SYNTHETIC contract |
| TD2 Consistency and consequences | Applicable variational identities, conservation/balance, symmetries, admissibility, stability and solution existence/uniqueness scope. Give proofs or clearly bounded numerical evidence, not an unsupported general theorem. | F4-F6 |
| TD3 Comparator and added content | Explicit comparison, transformation/reduction where possible, and what remains independently restrictive. Identify free, derived, calibrated, fitted and unidentifiable combinations. | Formula audit, F2/F4-F5, baseline |
| TD4 Physical realization | One system, dimensional map, preparation/source and observer/processing/error chain. State material regime and independent parameter origins. | F2-F3, F7, PHYSICAL_COMPARISON contract |
| TD5 Locked test | Fixed model/version, parameter policy, calibration versus reserved comparison, uncertainty-aware rejection rule and competing explanations. Record support, rejection or inconclusive only within scope. | F8 and existing claim gates |
| TD6 Generalization | Independently test transfer to another regime without silent retuning. Derive or explicitly calibrate scale changes; expose new assumptions. | Same F gates for the new scope |

TD3 may expose a contradiction that sends work back to TD1; TD4 may show that a proposed
state cannot represent the intended system. Such feedback is expected, not permission
to overwrite failed evidence. Comparator checks should start early and be revisited
when a term changes. Safe downstream diagnostics are allowed but cannot close a claim
whose required upstream evidence is missing. Independent tasks may run in parallel only
with named dependencies and fixed interfaces; topic numbers are not a work sequence.

## 4. Minimum-model and interaction rules

- Minimize unjustified independent assumptions, not the number of displayed equations.
  Many equations/tests can follow from a short generator; one equation can hide many choices.
- For a proposed information/state interaction, first ask whether the information quantity
  is a functional of existing states/history or an independently initialized state. Do not
  assume an information-mass coupling or a universal entropy identity from a word alone.
- Additional memory can be represented by an explicit state or a history operator; show
  its role and avoid counting both as independent copies of the same mechanism.
- Trace every term to a definition, imported result, derivation, constitutive ansatz,
  approximation or calibration. Plausibility and dimensional agreement do not select a
  unique coupling, establish its physical origin, or determine its numerical value.
- Prefer one declared generator for a claimed conservative sector. A dissipative sector
  requires its own declared reduction/constitutive law and ledger, not a hidden force.
- Explain what removal/decoupling of a term changes. Reuse existing ablations and exact
  limits; do not generate parameter sweeps merely to populate a checklist.
- A functional chosen to descend does not by that fact prove universal optimization,
  physical entropy production, learning, survival intent or new fundamental dynamics.
- If a model is forward-equivalent to a known comparator, retain that result. It may be
  a useful reformulation/application, but precision or more samples cannot identify its
  theory label. A new distinguishing restriction needs independent justification, not
  a term added solely to escape the comparator.

## 5. One bounded work card per decision

Put this short section in the existing research-design note, METHOD or current wave
record. Link the current calculation contract and blocker field; do not duplicate them.

```text
Question / intended claim:
System boundary / internal coupling / detector path / backaction assessment (standard 30):
Stage and scope (TD0-TD6; not an evidence status):
Current model and source/code/config identities:
Already have (evidence links and limits):
Missing or disputed (author choice / mathematical / physical / data):
Controlling dependency (existing path + field):
One next action and WHY it can change the decision:
Possible outcomes: supports within scope / rejects / equivalent / inconclusive:
Acceptance or rejection evidence required:
Stop condition and reopening prerequisite:
Reviewer needed and precise question:
Non-goals / forbidden retuning or new assumptions:
```

Choose the earliest unresolved dependency of the intended claim, not the earliest open
question anywhere in the project. A modest application need not solve fundamental unification.
Review only one controlling question per wave; keep other hypotheses in the existing backlog.
Do not activate more than three foundation lanes at once under the existing organization policy.

Every proposed new term/branch must name its parent, the observed or demonstrated gap,
why existing terms do not address it, new degrees of freedom/parameters and a finite
comparison plan. Do not expand merely because a run stopped or the user asked for progress.

## 6. Decision and efficiency rules

Useful closure includes a proved conditional relation, a counterexample, a rejected
reduction, a bounded application prediction, or a demonstrated equivalence. A clearer
input inventory can unblock work but is methodological progress, not new physical evidence.

Before/after each wave state: evidence changed; alternatives excluded; assumptions or
parameter freedoms changed; current blocker; next dependency. Report unknown counts as
unknown. No combined completion percentage, quality grade or file/test/token count is a
theory-validity score. Claim classes A-E in the existing rubric are NOT school grades.

Reuse unchanged evidence and closed negative routes. After two consecutive attempts with
no decision-relevant change, reassess the route instead of adding prose, fixtures or
search variants. A new hypothesis must be explicit and separately justified. Stop on a
proved equivalence/no-go within scope, unresolved author choice, or concrete unavailable
input; name what would reopen it. Preserve all independent authorized work that remains
useful. Never restart an exhausted research round merely to maintain activity.

## 7. Human, AI and expert responsibilities

Human authors own intent and scope decisions; agreement does not establish physics.
AI must label its additions, surface alternative formulations and seek review before
treating an unresolved author choice as settled. It must not invent a derivation, a
supporting citation, or author approval. Record errors and corrections without assigning
personal blame from outcomes. Lack of an A grade is neither evidence of failure nor a
judgment of the author. A more capable model or longer runtime is not scientific evidence.

Separate construction from adversarial review. Another AI can find defects, but it is not
independent empirical replication or a substitute for domain expertise. Request a bounded
expert review when a foundational physical identification, an unverified nonstandard proof,
or a specialist-dependent claim controls the next step. Work may remain openly provisional
while review is unavailable; expert absence must not become endless automatic reruns.

Useful review assignments:

| Reviewer competence | Concrete question |
| --- | --- |
| Mathematical physics / dynamical systems | Are the generator, state closure, admissible domain and claimed consequences consistent? |
| Statistical mechanics / thermodynamics | Is the proposed energy/entropy balance physically defined under the declared boundaries? |
| Information theory | Which functional of which state/distribution/channel is used, and what does it retain or lose? |
| Complex systems | Does persistence/coordination follow from dynamics or from chosen costs/selection rules? |
| Experimental / domain specialist | Does preparation, material regime, detector and uncertainty actually realize the proposed test? |

Prepare a small review packet: proposition, minimal equations/definitions, strongest existing
result/counterexample, one unresolved question and source links. Do not send the whole
archive. This rule does not authorize contact, email, data acquisition or paid services.

## 8. Initial adoption: Core / Topic 13

This is a routing example based on existing evidence, not a new stage promotion or a full
re-audit of every scientific artifact. Record the actual pilot wave in the existing topic
log when it is performed; do not mark the pilot complete from this standards edit.

- TD0: use the author's explicit statements and the current ontology contract to reconcile
  historical meanings; unresolved equivalences remain author-review questions.
- TD1-TD2: reuse [legacy variational closure](../../core/07_artifacts/gates/uet_legacy_variational_closure.json)
  only in its named normalized mode. Do not rerun it to settle a different information ontology.
- TD3: reuse [action discrimination](../0.13_Thermodynamic_Bridge/Result/T13_ACTION_DISCRIMINATION_2026-10-18.md).
  The demonstrated scalar/O(2) comparator equivalence limits uniqueness in that action class,
  not every possible UET model or the value of an application.
- TD4-TD5: the [Topic 13 closure gate](../0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json)
  separates O(2)/He-4 Core composition from graphite external validation. Retain its scope;
  neither its labels nor the older global closure report settle every later material/operator gap.
- Next foundational design action: reconcile ONE intended proposition with its existing
  state/term choices and comparator. First identify what is already answered and which author
  decision is genuinely missing. No automatic new equation, material substitution or source hunt.

## 9. Handoff acceptance

- Intent/proposal provenance and unresolved author decisions are distinguishable.
- A stage-specific question links to existing evidence and the governing F gate/contract.
- Mathematical consistency, comparator novelty and physical support are reported separately.
- Every next action has a reason, finite outcome rule and stop/reopening condition.
- Historical results, parent physics statuses and unrelated dirty work are preserved.
- Standards changes receive scoped link/diff review, a factual work-ledger entry and commit.
  Run scientific verifiers only for changed evidence-producing state, not for this document alone.
