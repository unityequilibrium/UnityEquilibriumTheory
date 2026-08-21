# UET Agent Operating Guide

This file is the root entrypoint for AI agents and collaborators working in this repository.

It does not replace the project standards. It tells an agent where truth lives, how to work
without inflating claims, and how to stay useful inside the actual UET workflow.

## Purpose

Use this file to orient quickly before editing code, rewriting docs, auditing a topic, or
answering research questions.

The repository already contains the full operating standard in
[`docs/topics/For Work/`](./docs/topics/For%20Work/). This guide is the short version for
day-to-day agent work.

## Project reality

- `docs/` is the main research codebase, documentation root, and GitHub Pages source.
- `docs/topics/` contains the numbered topic workspaces and the standards workspace.
- `docs/topics/For Work/` is the canonical operating manual for topic research work.
- `docs/meta/` and `docs/topics/README.md` are the preferred source of truth for current
  topic status, readiness, and claim restraint.
- Many files under `Result/`, `_Logs/`, generated reports, and audit outputs are artifacts,
  not the first place to make narrative decisions from memory.

## Default working style

This repository is often used for:

- auditing what is still weak, unclear, overstated, missing, or not yet standardized
- answering learning-oriented questions about how the repo works
- improving credibility, structure, verification discipline, and research legibility
- conducting topic research using the standards already documented in `For Work`

If the request is ambiguous, prefer:

1. inspect local evidence first
2. identify gaps, risks, or unclear claims
3. improve structure or wording conservatively
4. avoid promoting status unless the evidence clearly supports it

When work spans repeated repair passes, prefer a visible hardening loop:

1. package or confirm the current sources
2. regenerate one stable verifier artifact
3. add or tighten one machine-readable blocker gate
4. update the local topic docs to match the new blocker boundary
5. record the pass in the topic update log
6. commit the coherent change before starting the next wave

When the user wants faster progress across many topics, prefer improving the
workflow standard and update-log discipline before trying to push every topic
forward at once:

1. tighten the operating rule in `docs/topics/For Work/` or this guide if the
   same ambiguity is slowing multiple topics
2. make the next blocker state machine-readable in the local topic package
3. use one pilot topic to prove the updated workflow before rolling it out more
   broadly

Treat this as the default acceleration path when progress feels slow across
many topics. Shared workflow clarity should compound before topic count does.

When the same blocker shape appears in several topics, treat that as a
workflow problem first and a topic problem second. Prefer this order:

1. tighten the shared rule in `AGENTS.md` or `docs/topics/For Work/`
2. name the repeated blocker class in machine-readable language
3. require active topics of that class to expose the blocker in a gate,
   manifest, or artifact field
4. prove the repaired method in one pilot topic
5. only then broaden the rollout

This prevents repeated topic work from drifting into custom one-off habits.

When progress feels slow because a topic keeps producing more prose than
closure, add structure before adding scope:

1. identify the single controlling blocker that still decides the topic state
2. require that blocker to exist in a machine-readable gate, manifest, or
   artifact field
3. require the local `UPDATE_LOG.md` to say what changed, what was rerun, and
   what still controls the topic now
4. do not start the next blocker wave until the current controller is visible
   in both artifact state and log state

This is the default anti-drift rule for repeated hardening work. The aim is to
stop a topic from feeling busy while remaining ambiguous.

When a collaborator asks for "overall progress" or "what changed lately,"
prefer reconstructing status from current artifacts, manifests, and update logs
instead of giving a prose-memory summary. The goal is to make repo-wide status
readable without guessing.

When the repository is moving across many topics at once, prefer a status-first
workflow before starting new edits:

1. inspect `docs/topics/README.md` and relevant `docs/meta/` records
2. inspect the local topic `README.md`, `LIMITATIONS.md`, and `VERIFICATION_SPEC.md`
3. inspect the current verifier artifact and any machine-readable blocker gates
4. inspect the topic `UPDATE_LOG.md` when the work spans multiple waves
5. summarize the current blocker chain before proposing promotion, publication, or rewrite

If these sources disagree, treat the latest stable verifier artifact and
machine-readable blocker gate as the controlling state for the current pass,
then repair documentation drift afterward.

If a topic package does not yet expose its current blocker chain clearly enough
to answer a status question, the next useful action is usually to add or tighten
one machine-readable gate and record the wave in `UPDATE_LOG.md` before trying
to advance the claim.

When progress reporting itself becomes difficult, treat that as a standards
defect. The next useful action is usually one of:

1. tighten the local topic `UPDATE_LOG.md`
2. tighten the blocker wording in the latest artifact or manifest
3. update `AGENTS.md` or the relevant `For Work` standard so the same
   confusion does not recur elsewhere

If several topics look stalled at the same time, do not spread effort evenly by
default. Prefer this order:

1. update the shared workflow rule that would remove repeated ambiguity
2. require status-first reconstruction and update-log discipline on active topics
3. prove the revised method on one pilot topic
4. only then expand the same pattern to adjacent topics

This keeps acceleration real instead of cosmetic.

## Start here

Open these files first when you need repository-wide context:

1. [`README.md`](./README.md)
2. [`CONTRIBUTING.md`](./CONTRIBUTING.md)
3. [`docs/topics/README.md`](./docs/topics/README.md)
4. [`docs/topics/For Work/00_README.md`](./docs/topics/For%20Work/00_README.md)
5. [`uet_history/README.md`](./uet_history/README.md)
6. [`uet_history/BOOK_WORKFLOW.md`](./uet_history/BOOK_WORKFLOW.md)

Then choose the next standard by task.

## Reading order by task

### If the task is audit, cleanup, or credibility repair

1. [`docs/topics/For Work/01_Project_Research_Constitution.md`](./docs/topics/For%20Work/01_Project_Research_Constitution.md)
2. [`docs/topics/For Work/03_AI_Usage_and_Governance.md`](./docs/topics/For%20Work/03_AI_Usage_and_Governance.md)
3. [`docs/topics/For Work/04_Claim_and_Evidence_Rubric.md`](./docs/topics/For%20Work/04_Claim_and_Evidence_Rubric.md)
4. [`docs/topics/For Work/02_Project_Workflow_and_Lifecycle.md`](./docs/topics/For%20Work/02_Project_Workflow_and_Lifecycle.md)
5. [`docs/topics/For Work/18_Research_Hardening_Workflow.md`](./docs/topics/For%20Work/18_Research_Hardening_Workflow.md)

### If the task is topic building or refactoring

1. [`docs/topics/For Work/02_Project_Workflow_and_Lifecycle.md`](./docs/topics/For%20Work/02_Project_Workflow_and_Lifecycle.md)
2. [`docs/topics/For Work/10_Topic_Architecture_5x5(+1).md`](./docs/topics/For%20Work/10_Topic_Architecture_5x5(+1).md)
3. the relevant standards in `11-18`

### If the task is book writing or history publishing

1. [`uet_history/BOOK_WORKFLOW.md`](./uet_history/BOOK_WORKFLOW.md)
2. [`uet_history/PIPELINE.md`](./uet_history/PIPELINE.md)
3. [`uet_history/3_publish/books/README.md`](./uet_history/3_publish/books/README.md)
4. [`uet_history/3_publish/books/BOOK_REGISTRY.json`](./uet_history/3_publish/books/BOOK_REGISTRY.json)
5. the existing canonical book folder and its local README, blueprint, source register,
   claim map, verification spec, and update log when present

The shared book workflow is reusable across titles. A book's local voice, chapter structure,
and citation surface remain authoritative for that book.

### If the task is multi-wave hardening or progress reconstruction

1. [`docs/topics/For Work/18_Research_Hardening_Workflow.md`](./docs/topics/For%20Work/18_Research_Hardening_Workflow.md)
2. [`docs/topics/For Work/24_TEMPLATE_UPDATE_LOG.md`](./docs/topics/For%20Work/24_TEMPLATE_UPDATE_LOG.md)
3. the local topic `README.md`, `LIMITATIONS.md`, and `VERIFICATION_SPEC.md`
4. the latest verifier artifact and any blocker manifests or gate JSON files

### If the task is mainly question answering or learning support

1. inspect the local files that already define the topic or workflow
2. answer from local evidence first, not memory
3. cite the exact file that acts as the current source of truth
4. say clearly when a conclusion is inference rather than an explicit repo statement

### If the task is repeated hardening, unblock work, or reconstruct progress

1. inspect the local topic package first
2. open [`docs/topics/For Work/18_Research_Hardening_Workflow.md`](./docs/topics/For%20Work/18_Research_Hardening_Workflow.md)
3. open [`docs/topics/For Work/24_TEMPLATE_UPDATE_LOG.md`](./docs/topics/For%20Work/24_TEMPLATE_UPDATE_LOG.md)
4. rebuild the current blocker chain from manifests, gates, and artifacts before changing prose

## Non-negotiable rules

- Do not let a topic outrun its evidence.
- Do not upgrade a fit into a prediction.
- Do not upgrade an internal rerun into external validation.
- Do not use hardcoded local paths when repository path helpers or relative structure should
  be used.
- Do not hide important physics logic or derivation-critical behavior in vague helper code.
- Do not rewrite repository status using stale counts from older prose when canonical
  metadata exists.
- Do not smooth uncertainty away just because a polished sentence sounds better.
- Do not add or promote a core equation before its ontology, standard-physics correspondence,
  units, derivation class, and observable mapping are recorded in the equation registry.
- Do not treat a normalized effective ledger as SI energy, a lane-specific mapping as a
  universal identity, or a derived trace as an independent physical substance.

## Claim discipline

Use conservative wording unless the repository clearly supports something stronger.

Preferred wording includes:

- `hypothesis`
- `proposal`
- `model`
- `derived relation`
- `reproduced internally`
- `passes current internal benchmark`
- `externally replicated`
- `peer-reviewed result`

Treat words like `solved`, `verified`, `proved`, `exact`, and `production grade` as
restricted unless the relevant local evidence explicitly justifies them.

For claim wording, defer to:

- [`docs/topics/For Work/04_Claim_and_Evidence_Rubric.md`](./docs/topics/For%20Work/04_Claim_and_Evidence_Rubric.md)
- [`docs/UET_Documentation_Details/STANDARDS/documentation_style_guide.md`](./docs/UET_Documentation_Details/STANDARDS/documentation_style_guide.md)

## When editing a topic

Before changing a topic narrative, inspect the local topic package first. Prefer this order
when files exist:

1. topic `README.md`
2. `METHOD.md`
3. `LIMITATIONS.md`
4. `VERIFICATION_SPEC.md`
5. relevant `FORMULA_AUDIT.md`
6. code, data, and result artifacts

When editing, preserve the distinction between:

- theory and benchmark behavior
- derivation and calibration
- internal evidence and external evidence
- exploratory concept work and core-credibility work

## Verification mindset

When asked to review or improve work, default to a verification-first mindset:

- look for broken structure, missing provenance, unclear baselines, weak thresholds, missing
  limitations, and inflated claims
- prefer explicit metrics and named artifacts over adjectives
- treat generated figures and logs as outputs that should be explained by scripts and inputs
- if a topic status is unclear, consult `docs/topics/README.md` and the metadata in
  `docs/meta/` before summarizing it
- if a topic has gone through many waves, prefer reconstructing the state from the update log,
  verifier artifact, and blocker gates together rather than from prose memory alone
- if a topic is moving through repeated repair passes, use the hardening workflow and keep an
  update log so later reviewers can reconstruct what changed and why
- if a topic seems stuck for a long time, first classify the blocker as source, formula,
  artifact, threshold, dependency, or claim-boundary related before deciding what to do next

## Update-log discipline

Use an `UPDATE_LOG.md` when:

- a topic is going through multiple hardening waves
- a reader would otherwise need to reconstruct progress from diffs alone
- blocker wording changes over time and needs a durable trail
- a verifier is rerun repeatedly and the result needs short historical context

The latest completed entry should make the next controlling blocker obvious to
a new reviewer without requiring diff reconstruction first.

An update log should record:

- what changed in that wave
- which verifier or audit was actually run
- which blocker narrowed or stayed controlling
- whether claim wording changed or stayed the same
- what exact next blocker remains
- what currently controls the topic-level state after that wave

An update log should not:

- replace artifact JSON as the canonical result
- replace manifests as the source of truth for provenance
- become a place for promises that were not implemented yet
- be backfilled with vague summaries that hide what really changed

For active hardening topics, treat the update log as required once any of these
become true:

- three or more distinct hardening waves have occurred
- the controlling blocker has changed wording more than once
- multiple collaborators would otherwise need git history to reconstruct state
- the topic is being used as a pilot for a workflow change

When a topic is being hardened across many short waves, prefer one concise
entry per completed wave over batching several blocker changes into one large
retroactive summary.

Recommended sequence for repeated waves:

1. change artifact, manifest, gate, or verifier logic first
2. rerun the verifier only when the evidence-producing state changed
3. sync topic docs to the new blocker boundary
4. write one concise update-log entry
5. commit the scoped wave before starting the next one

For repeated hardening, each completed log entry should make these three things
recoverable in under a minute:

1. what exact artifact or gate changed
2. what exact blocker became narrower
3. what exact blocker now controls the next wave

If an entry cannot answer those three questions, tighten the entry before
treating the wave as complete.

When a repeated ambiguity appears across several topics, prefer updating
`AGENTS.md` or the relevant `docs/topics/For Work/` standard close to the same
time so the improved method becomes reusable rather than living only in one
topic's local fixes.

For workflow-repair waves that change `AGENTS.md` or `docs/topics/For Work/`,
record the linkage explicitly in the affected pilot topic log once the pilot is
updated. That keeps standards work and topic work traceable as one method chain
instead of two unrelated edits.

For repo-wide status requests, a good reconstruction order is:

1. `docs/topics/README.md` and relevant `docs/meta/` records
2. the local topic package (`README.md`, `LIMITATIONS.md`, `VERIFICATION_SPEC.md`)
3. the latest stable verifier artifact
4. blocker manifests or gate JSON files
5. `UPDATE_LOG.md` for wave history and next-controller context

For a fast repo-wide progress snapshot, prefer reporting this compact tuple for
each active topic:

1. current tier or readiness label
2. current controlling blocker
3. latest stable verifier result
4. last completed hardening wave
5. publication status boundary

If any topic cannot be summarized in that tuple from local evidence, the topic
still needs status-hardening work before more ambitious promotion claims.

## Git workflow

Use `git` actively so work does not sit uncommitted for too long.

- check `git status` before editing so you know whether the tree is already dirty
- do not revert or overwrite unrelated user changes
- keep commits scoped to the files and task you actually touched
- prefer small, meaningful commits over one large end-of-session dump
- when a unit of work is stable, commit it instead of letting it linger
- if the repository already contains unrelated changes, stage only the intended files
- write commit messages that describe the real change plainly, especially for audits,
  standards, verification, and claim-discipline work

Suggested commit cadence:

1. finish one coherent change
2. run the relevant quick verification or review pass
3. stage only the intended files
4. commit before starting the next distinct chunk

### Repo work ledger and push checkpoints

Use the repo work ledger for every major UET workspace, not only research. The
ledger lives at `WORK_LEDGER/` because it records the operating history of the
whole repository.

Before starting a substantial section of work, classify it with
`WORK_LEDGER/AREAS.md`. Common areas include:

- `research-core` for numbered research topics under `docs/topics/`
- `research-standards` for `docs/topics/For Work/` and research operating rules
- `theory-history` for theory notes and archives under `uet_history/`
- `book-writing` for long-form book or publishable narrative work
- `thai-policy` for proposals under `thailand_proposals/`
- `services-tools` for services, experiments, MCP, GraphQL, or automation tools
- `repo-ops` for GitHub Actions, manifests, repository hygiene, and agent rules
- `raw-private` for local-only source material that may be unsafe to publish

Write one daily ledger file under `WORK_LEDGER/YYYY/`, such as
`WORK_LEDGER/2026/2026-07-04.md`. The ledger is not a replacement for topic
`UPDATE_LOG.md`; it is the repo-level trace that shows what moved that day and
what still needs a commit, push, or PR.

Add one ledger entry after each completed section of work. A section can be a
research pass, theory/book drafting pass, history migration, policy proposal
revision, service/tool change, documentation repair, result artifact review, or
any coherent batch that a future reviewer should be able to reconstruct without
reading the whole diff first.

Each entry should record:

- timestamp or short section label
- area id from `WORK_LEDGER/AREAS.md`
- workspace or topic touched
- files or artifact groups changed
- verifier, audit, or review actually run, if any
- public-safety status: `safe`, `partial`, `private`, or `blocked`
- what remains uncommitted, private, or unsafe to publish
- next commit, push, PR, or manifest action

Do not let ledger entries become another place for vague progress claims. Keep
them short, factual, and tied to actual files or artifacts.

Checkpoint rule:

- if 10 ledger entries exist for the current unpushed work, stop expanding scope
- inspect `git status` and stage only the intended files
- commit the safe coherent unit
- push the branch the same day whenever network and repository policy allow it
- if the work is not ready for `main`, open or update a draft PR instead of
  leaving the branch local-only
- if files are unsafe to publish, commit a manifest or ledger note that names the
  excluded class without publishing the raw/private content

Do not start an eleventh ledger entry until the checkpoint decision is made. If
a push is blocked, record the blocker and the exact next action in the daily
ledger before continuing.

Legacy location note: `docs/UET_Documentation_Details/WORK_LOG/` should point to
`WORK_LEDGER/` instead of becoming a second competing log location.

For multi-wave hardening, a good unit is:

1. one blocker narrowed
2. one manifest or gate added or tightened
3. one verifier rerun if the artifact schema changed
4. one short update-log entry
5. one scoped commit

When a standards or workflow change is introduced to speed up future research,
capture it in `AGENTS.md` or `docs/topics/For Work/` close to the same time so
later waves do not depend on unwritten habits.

When touching standards such as `docs/topics/For Work/` or `AGENTS.md`, prefer a
separate commit from topic-level research changes unless the standards update is
required to explain the same hardening wave.

## Book workspace path discipline

- `uet_history/3_publish/books/BOOK_REGISTRY.json` is the canonical map for book identity and paths.
- `uet_history/BOOK_WORKFLOW.md` is the shared working standard for every book; do not invent a
  separate title-specific lifecycle unless the reusable standard itself needs to change.
- Before creating or publishing a book path, inspect the registry and existing `books/` folders.
- An existing book folder is canonical. Do not create a semantic alias for the same book.
- Keep raw and draft directories local unless the registry explicitly lists a reviewed public file.
- If a book belongs to a three-book Section, inspect the parent Section Blueprint, Volume Matrix, and Dependency Map before changing the local Book Blueprint.
- Use human-readable academic-domain labels for visible Section and book folders. The parent folder shows the Section grouping, so do not add a visible `section_` prefix or Section number to the parent folder; child book folders use a numeric volume prefix for reading order; keep stable `section_id`, `book_id`, and `volume_number` values in registries and manifests.
- Treat `W00`-`W18` as separate gates. At minimum, keep research design, literature review,
  source digest/provenance, claim map/blueprint lock, Draft 1, Draft 2, integrity check,
  fact/citation audit, developmental review, line edit, copyedit, rights/ethics, proof,
  publish, and maintenance distinguishable. A planned source is not yet a verified citation.
- Start book-writing work with a planning pass, not with a request to choose or write an
  episode. For a three-book Section, first expose the Section arc, the role of all three
  books, the book-level plans, dependencies, handoffs, claim ownership, and reference tasks;
  then wait for author review before selecting a downstream writing unit.
- Treat uet_history/3_publish/books/โครงสร้างหนังสือ.md as the authoritative local writing
  pattern. It controls the structure and citation surface of a chosen unit; it does not replace
  the Section/Book planning pass or authorize the agent to invent a chapter or episode.
- A literature review is not a source list: it must synthesize positions, uncertainty,
  contrary evidence, limitations, and gaps before the blueprint is locked.
- For in-place manuscript edits, run the W09 integrity check and preserve original
  prose/structure unless the change request explicitly authorizes rewrite, deletion,
  merge, or reorder.
- Preserve one canonical working draft and use a local `UPDATE_LOG.md` to record each completed
  writing wave when the book is developed across multiple passes.
- A book update is complete only when the canonical source, registry state, scoped commit, and public `main` path agree.
- If a public copy differs from the canonical working file, stop and record the drift before publishing another copy.
## Agent behavior expectations

- Be useful for audits, critique, normalization, and learning support.
- Prefer local evidence over speculation.
- Keep summaries legible and restrained.
- If evidence is mixed, say so plainly.
- If you infer something, label it as an inference.
- If a file in `For Work` already governs the decision, follow it instead of inventing a new
  rule.
- If a topic is stuck, aim to make the blocker narrower and more machine-readable before trying
  to make the claim stronger.
- If several topics are stuck at once, prefer improving the shared workflow,
  logging, or standards first so later topic work compounds instead of
  repeating the same ambiguity.
- When asked for a repo-wide status summary, reconstruct it from standards, metadata, topic
  docs, artifacts, and update logs in that order rather than relying on memory.

## Quick routing

- Book workflow or repeatable writing gates: open [`uet_history/BOOK_WORKFLOW.md`](./uet_history/BOOK_WORKFLOW.md)
- Book identity, paths, and public/local boundary: open [`uet_history/3_publish/books/README.md`](./uet_history/3_publish/books/README.md),
  [`BOOK_REGISTRY.json`](./uet_history/3_publish/books/BOOK_REGISTRY.json), and [`PIPELINE.md`](./uet_history/PIPELINE.md)
- Book source traceability: inspect the local `REFERENCE_REGISTER`, `CLAIM_MAP`, and `VERIFICATION_SPEC` before rewriting prose
- Book research design and literature review: open `BOOK_WORKFLOW.md` and the local
  research-design/literature-review records before drafting evidence-led chapters.
- Manuscript integrity and in-place editing: inspect the W09 manifest or verification log
  before trusting line counts, chapter boundaries, or preservation claims.
- Section or three-book blueprint work: inspect the parent Section manifest and S00-S09 gate state,
  Section Blueprint, Volume Matrix, and Dependency Map before drafting or revising a child book blueprint.

- Claim sounds too strong: open
  [`04_Claim_and_Evidence_Rubric.md`](./docs/topics/For%20Work/04_Claim_and_Evidence_Rubric.md)
- AI-generated wording needs review: open
  [`03_AI_Usage_and_Governance.md`](./docs/topics/For%20Work/03_AI_Usage_and_Governance.md)
- Topic structure is messy: open
  [`10_Topic_Architecture_5x5(+1).md`](./docs/topics/For%20Work/10_Topic_Architecture_5x5(+1).md)
- Data provenance is weak: open
  [`12_Data_Standard.md`](./docs/topics/For%20Work/12_Data_Standard.md)
- Result artifacts are unclear: open
  [`14_Result_Standard.md`](./docs/topics/For%20Work/14_Result_Standard.md)
- Formula origin or units are unclear: open
  [`17_Formula_Audit_Standard.md`](./docs/topics/For%20Work/17_Formula_Audit_Standard.md)
- The topic is stuck in repeated `FAIL` or `WARN` cycles: open
  [`18_Research_Hardening_Workflow.md`](./docs/topics/For%20Work/18_Research_Hardening_Workflow.md)
- You need a durable record of what changed across waves: open
  [`24_TEMPLATE_UPDATE_LOG.md`](./docs/topics/For%20Work/24_TEMPLATE_UPDATE_LOG.md)

## One-line principle

Use the agent as a careful research assistant, auditor, and systems organizer, not as the
final authority that upgrades evidence by confidence alone.

### Repository branch and automation policy

main is the public canonical branch. Normal work enters main through a pull
request and required CI checks; do not use a second permanent integration
branch such as develop or staging.

Use one short-lived branch per coherent unit of work:

    codex/research/<task>
    codex/book/<task>
    codex/history/<task>
    codex/policy/<task>
    codex/services/<task>
    codex/repo/<task>

Before editing, confirm the current branch, worktree, and upstream. A local
branch that tracks origin/main is still a feature branch and must not be
treated as the canonical main worktree. Reconcile worktrees and stale
remote-tracking refs before deleting branches; never delete a dirty worktree
or a branch that contains unique unmerged commits.

Every normal PR must identify its area, canonical workspace, public-safety
boundary, checks actually run, and next blocker. GitHub Actions may validate,
build reports, and deploy GitHub Pages, but must not silently commit or push
source changes. Required checks must fail visibly; do not use
continue-on-error to make a required gate appear green.

The repository ruleset should prevent force-push and deletion of main, require
the scoped PR checks, and auto-delete a merged head branch. Direct push is an
emergency exception only: record the reason in WORK_LEDGER/ and verify that
local main, remote main, and the GitHub page show the same SHA.

The normal publish checkpoint is the same day as the completed section: commit
the coherent unit, push the branch, and open or update a draft PR when it is
not ready to merge. Use git fetch --prune origin during branch inventory so
stale origin/codex/... references do not look like active remote branches.
