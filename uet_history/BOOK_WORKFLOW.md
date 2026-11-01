# UET Book Writing Workflow

This is the shared workflow for long-form non-fiction and theory books. It
keeps each book's voice and structure intact while standardizing research,
review, version, and publication boundaries.

## Core rule

The book's style is local to the book. The workflow is shared.

Every active book separates:

- blueprint and intended structure
- reference planning and source digest
- manuscript draft
- review result for each wave
- public publication boundary

An elegant paragraph is not evidence that its source, claim, or publication
status has been checked.

## What this standard controls

This document standardizes the work system, not the book's voice. It controls
research design, evidence records, manuscript versions, review roles, change
traceability, and the boundary between a working draft and a public release.

There is no single ISO-style global workflow that fits every book. This standard
combines common professional distinctions from research writing, fact-checking,
editorial work, copyediting, proofreading, permissions, and publishing. Each book
may adapt the depth, but it must declare the adaptation and keep the same evidence
and handoff logic.

## Operating principles

1. Start with a research question, audience, and claim boundary.
2. Treat the first blueprint as provisional until the literature review changes or confirms it.
3. Separate a source that was planned, located, read, appraised, and actually used.
4. Map important claims to evidence before polishing the prose.
5. Keep one canonical working manuscript and make every material change traceable.
6. Never let layout, a polished tone, or an AI draft upgrade the evidence status of a claim.
7. Every gate must have an artifact, an owner, a pass condition, and a next controller.

## Unified operating model (normative)

The book workspace has three different layers. They work together, but one layer
must never be used as a substitute for another.

| Layer | What it controls | Canonical control | Normal output |
| :-- | :-- | :-- | :-- |
| **Section** | the shared promise, the three-book arc, ownership, dependencies, terminology, chronology, and handoffs | `S00-S09` | parent Section package |
| **Book** | the individual book promise, research, evidence, claims, manuscript versions, review, and release | `W00-W18` | child Book package |
| **Writing unit** | the local chapter/episode/section pattern and reader-facing rhythm | the book's approved local structure | one controlled unit draft |

The Section and Book gates are the project control system. The local writing
structure is a production template inside the Book workflow. It is not a
replacement for the Section plan, the Book Blueprint, the literature review, or
the claim map.

The normal dependency is:

```text
Section plan and lock
  -> Book plan, research, and claim/blueprint lock
    -> approved unit execution packet
      -> local unit draft and author review
        -> manuscript integrity and fact/citation audit
          -> editorial, proof, release, and maintenance gates
```

### Canonical state vocabulary

Every Section and Book manifest must use the exact gate identifiers defined in
this document. `current_gate` is a control field, not a free-form label.

Use only these gate states:

`NOT_STARTED`, `IN_PROGRESS`, `PASS`, `PASS_WITH_OPEN_ITEMS`, `BLOCKED`,
`SUPERSEDED`.

Human-friendly labels such as `BLUEPRINT_LOCKED`, `DRAFT_1_COMPLETE`, or
`MASTER_LOCK` may appear as explanatory text or an optional `phase_label`, but
they must not replace `current_gate` or `status`.

`next_controller` must name the next canonical Section or Book gate. If a human
decision is required, keep the current gate open, set the owner, and record the
decision in `open_items`; do not invent a pseudo-gate.

A child Book must always record the exact `section_blueprint_version` against
which its local Blueprint was checked. A parent Section manifest must point to
the child manifest and current Blueprint version it controls.

### Staged package rule

The minimum package is staged by gate. A new book does not need a directory full
of empty files on its first day, but its manifest must expose the state of each
required output as `NOT_STARTED`, `IN_PROGRESS`, or complete. A gate cannot pass
because a filename exists alone, and a missing future artifact must not be
hidden by a polished README.

Use an existing equivalent filename when one already exists and record the
mapping in the README or manifest. Do not create semantic aliases merely to
make a checklist look complete.

## Section and volume architecture

When a project contains a Section made of three books, use a parent-child workflow. The Section is the parent narrative and research architecture; each book is a child volume; chapters or episodes are the units inside a book.

```text
SECTION BLUEPRINT
  -> BOOK 1 BLUEPRINT
       -> chapter / episode units
  -> BOOK 2 BLUEPRINT
       -> chapter / episode units
  -> BOOK 3 BLUEPRINT
       -> chapter / episode units
```

Use the project profile THREE_BOOK_SECTION when the Section must contain exactly three books. The workflow remains reusable for another declared volume count, but the number of volumes must be explicit in the Section manifest.

The Section blueprint answers: why these books belong together, what the complete reader journey is, what role each book plays, what each book may own or defer, and how evidence, concepts, terms, chronology, and unresolved questions move between books.

The Book blueprint answers: what this individual book promises, what it must establish, which chapters or episodes deliver that promise, which claims and sources it owns, what it receives from the Section or prior books, and what it hands off to the next book.

### Section control package

For a Section with three books, maintain one parent control package using existing canonical filenames where the repository already has an equivalent:

```text
SECTION_MANIFEST.json
SECTION_BLUEPRINT.md
SECTION_RESEARCH_DESIGN.md
SECTION_LITERATURE_REVIEW.md
SECTION_CLAIM_MAP.md
VOLUME_MATRIX.md
DEPENDENCY_MAP.md
SHARED_TERMS.md
SECTION_UPDATE_LOG.md
```

The parent package is the source of truth for Section identity, volume count, shared promise, volume roles, cross-book claims, dependencies, handoffs, and Section-level status. It does not replace the local manifest, blueprint, source register, claim map, or update log of each book.

At repository level, `uet_history/3_publish/books/SECTION_REGISTRY.json` maps each Section to its canonical parent path and child volume IDs. The Section manifest and package control Section content and gate state; the Book Registry continues to control individual book identity and publication state.

Human-facing Section paths use concise academic-domain labels. The parent folder shows the grouping, so do not add a visible `section_` prefix or Section number to the parent folder. Child book folders use a numeric volume prefix for reading order, while stable `section_id`, `book_id`, and `volume_number` values remain in registries and manifests; use full English `snake_case` labels for folders.

### Volume control package

Each child book keeps its own canonical book package and records at least:

- book_id
- section_id
- volume_number
- section_blueprint_version
- book promise and reader outcomes
- entry conditions and exit conditions
- chapter or episode IDs
- claim IDs owned by the book
- inputs from the Section or earlier books
- outputs and handoffs to the Section or later books
- local sources, evidence limits, and unresolved questions

### Parent-child invariants

1. The Section promise is the parent boundary. A book may narrow it but must not silently redefine it.
2. In the THREE_BOOK_SECTION profile, the volume matrix must contain exactly Book 1, Book 2, and Book 3 with stable IDs.
3. Every major Section objective or claim has one primary owning book. Supporting books may be listed, but ownership cannot remain ambiguous.
4. Every book chapter or episode maps to a Section role, a book promise, and one or more claim or evidence tasks.
5. Every cross-book dependency has an explicit source, destination, dependency type, and resolution status.
6. Shared terms, concepts, chronology, entities, equations, and recurring examples have one controlled definition or a documented reason for variation.
7. A local book edit may not silently change another book's entry condition, exit condition, role, claim ownership, or handoff.
8. A parent blueprint is not considered locked merely because all three child outlines exist. The parent-child mappings and unresolved items must also pass review.

### Section blueprint lifecycle

Use the same gate states as the book workflow: NOT_STARTED, IN_PROGRESS, PASS, PASS_WITH_OPEN_ITEMS, BLOCKED, or SUPERSEDED.

```text
S00 SECTION_INTAKE_AND_BOUNDARY
  -> S01 SECTION_PROMISE_AND_THREE_BOOK_ARCHITECTURE
  -> S02 SECTION_RESEARCH_DESIGN
  -> S03 SECTION_LITERATURE_REVIEW_AND_CLAIM_MAP
  -> S04 VOLUME_ALLOCATION_MATRIX
  -> S05 CROSS_BOOK_DEPENDENCY_AND_CONTINUITY
  -> S06 BOOK_BLUEPRINTS_DRAFT
  -> S07 SECTION_BLUEPRINT_REVIEW_AND_LOCK
  -> S08 SECTION_INTEGRITY_AND_DRIFT_AUDIT
  -> S09 SECTION_RELEASE_AND_MAINTENANCE
```

#### S00 SECTION_INTAKE_AND_BOUNDARY

- Output: SECTION_MANIFEST.json and a Section research brief.
- Record: section_id, title, profile, volume count, intended audience, language, promise, scope, exclusions, owner, format, risk level, and claim boundary.
- Pass: a new collaborator can explain why the three books form one Section and what the Section does not attempt to cover.
- Return: narrow the Section promise or resolve the volume count before drafting any child blueprint.

#### S01 SECTION_PROMISE_AND_THREE_BOOK_ARCHITECTURE

- Output: SECTION_BLUEPRINT.md with the complete reader journey and the role of Book 1, Book 2, and Book 3.
- Record: opening problem, Section-level question, volume role, book promise, entry state, exit state, major concepts, planned conclusion, and non-overlap boundary for each volume.
- Pass: each book has a distinct job, the sequence is intelligible, and the complete Section is more than three unrelated books.
- Return: revise the Section architecture or reassign a volume role.

#### S02 SECTION_RESEARCH_DESIGN

- Output: SECTION_RESEARCH_DESIGN.md or an equivalent parent research plan.
- Record: shared research questions, book-specific questions, search locations, source hierarchy, languages, date boundaries, inclusion and exclusion rules, shared source families, and known blind spots.
- Pass: the research plan distinguishes evidence needed once for the Section from evidence that must be checked separately in each book.
- Return: repair the research design before treating a bibliography or source list as a Section review.

#### S03 SECTION_LITERATURE_REVIEW_AND_CLAIM_MAP

- Output: SECTION_LITERATURE_REVIEW.md and SECTION_CLAIM_MAP.md or canonical equivalents.
- Pass only when the review synthesizes the main positions, methods, findings, controversy, contrary evidence, limitations, gaps, and implications for the three-book architecture.
- The Section claim map records cross-book claims, claim owners, shared evidence, counter-evidence, and the strongest wording permitted by the evidence.
- Return: S02 for inadequate Section research design, S03 when sources cannot be appraised, or S01 when the literature changes the architecture.

#### S04 VOLUME_ALLOCATION_MATRIX

- Output: VOLUME_MATRIX.md.
- Record for every major objective, claim, concept, event, example, and evidence family: primary volume, supporting volume if any, first introduction, required prerequisite, resolution point, and current status.
- Pass: no major item is orphaned, duplicated without a reason, or assigned to two books as competing owners.
- Return: revise the Section blueprint or the affected Book blueprint.

#### S05 CROSS_BOOK_DEPENDENCY_AND_CONTINUITY

- Output: DEPENDENCY_MAP.md and SHARED_TERMS.md or equivalent.
- Check: terminology, chronology, prerequisites, recurring entities, equations, examples, citations, unresolved questions, and handoffs between Book 1, Book 2, and Book 3.
- Pass: every dependency has an owner, destination, status, and failure consequence.
- Return: add a dependency record, move the owning claim, or revise the handoff.

#### S06 BOOK_BLUEPRINTS_DRAFT

- Output: a draft Book Blueprint for each volume, linked to section_id and section_blueprint_version.
- Each Book Blueprint must map its chapters or episodes to the Section role, local reader outcome, claim IDs, source needs, inputs, outputs, and handoff.
- Pass: all three books can be drafted without inventing missing Section architecture.
- Return: S01-S05 when a local outline exposes a parent-level ambiguity.

#### S07 SECTION_BLUEPRINT_REVIEW_AND_LOCK

- Output: parent-child review record and locked Section Blueprint version.
- Review the Section promise, Volume Matrix, Dependency Map, Shared Terms, and all three Book Blueprints together.
- Pass: the Section architecture and child blueprints agree; every open item is assigned an owner, controller, and deadline or explicitly accepted as non-blocking.
- A Book may begin its W00-W18 workflow after S07 passes or passes with open items that do not control that Book.
- Return: S01-S06; do not repair a parent-level conflict only inside one Book folder.

#### S08 SECTION_INTEGRITY_AND_DRIFT_AUDIT

- Output: before/after Section manifest, parent-child comparison, orphan/duplicate claim report, dependency check, and drift decision.
- Run after a Book Blueprint change, a major structural review, Draft 2, Draft 3, or any change to shared evidence, terms, chronology, or handoffs.
- Pass: every difference is explained and the current Section and Book Blueprint versions agree.
- Return: the first controlling Section gate and the affected Book gate.

#### S09 SECTION_RELEASE_AND_MAINTENANCE

- Output: Section release manifest, version map, Section update log, and maintenance decision.
- Confirm that all three public or planned book paths point to the intended Section version and that excluded local material remains excluded.
- Pass: Section status, child book status, registry state, and public manifest do not contradict each other.
- Return: repair the parent package or publication boundary before promoting a child book.

### Blueprint field contract

Section Blueprint minimum fields:

- section_id, title, profile, version, status, volume_count, volume_ids
- Section promise, audience, central question, scope, exclusions, and claim boundary
- complete three-book arc and distinct role of each volume
- primary owner for each major claim, objective, concept, event, and evidence family
- shared terms, dependencies, chronology, recurring entities, and handoffs
- research domains, literature-review boundary, source hierarchy, and evidence ceiling
- unresolved questions, controlling blocker, next controller, and change history

Book Blueprint minimum fields:

- book_id, section_id, volume_number, version, status, section_blueprint_version
- book promise, audience, reader outcomes, scope, exclusions, entry state, and exit state
- chapter or episode IDs, purpose, order, dependencies, and expected handoff
- claim IDs owned by the book, evidence class, source needs, counter-evidence, and wording boundary
- inputs received from the Section or earlier books and outputs delivered to later books
- unresolved questions, controlling blocker, next controller, and change history

### Section-to-volume operating sequence

1. Run S00-S03 to establish the Section boundary, research design, literature synthesis, and parent claim map.
2. Run S04-S05 to allocate ownership and make cross-book dependencies visible.
3. Run S06 to draft the three child Book Blueprints.
4. Run S07 to review and lock the parent-child architecture.
5. Run W00-W18 separately for each book. The three book workflows may run in parallel after the parent lock, but each keeps its own evidence and review gates.
6. Run S08 after any change that may cross a book boundary and before declaring the Section coherent.
7. Run S09 only when the Section version, all three book versions, registry records, and public boundaries agree.

### Section status and handoff report

When a Section is not complete, produce a handoff report before asking another
agent to repair its books. The report is a coordination artifact, not a claim of
completion.

Use one block per Section with:

1. parent `section_id`, canonical path, manifest version, status, `current_gate`,
   controlling blocker, and `next_controller`;
2. the state of the parent package: Blueprint, research design, literature
   review, claim map, volume matrix, dependency map, shared terms, and update
   log;
3. one row for each child Book containing `book_id`, volume number, parent
   Blueprint version, local Blueprint version, `current_gate`, status, canonical
   draft path, missing or stale artifacts, and controlling blocker;
4. explicit parent-child drift, such as a version mismatch, a non-canonical gate
   name, an orphan claim, a duplicate owner, a missing handoff, or a draft count
   that disagrees with the approved Blueprint;
5. the repair order, with one next controller per item.

Use these labels in the handoff:

`COMPLETE`, `PARTIAL`, `BLOCKED`, `DRIFTED`, `NOT_STARTED`, and `NEEDS_HUMAN_DECISION`.

Do not infer completion from file count or prose volume. A parent Section is not
ready for child drafting when a parent-level blocker controls the child, and a
Book is not ready for a later gate when its required evidence or review artifact
is absent.

## Planning-first agent protocol

The first interaction for a new book-writing task is a planning pass, not a request to choose an episode. The Section and book architecture must be visible before the manuscript is drafted.

When the user asks to start, write, or continue a book and no approved execution plan has been named:

1. Inspect the Section parent package first when the book belongs to a Section. Read the Section Blueprint, research design, literature review, claim map, Volume Matrix, Dependency Map, and current gate state.
2. Inspect the canonical book folder, its Book Blueprint, research design, literature review, source register or digest, claim map, verification specification, and update log when present.
3. Read uet_history/3_publish/books/โครงสร้างหนังสือ.md as the authoritative local writing pattern. This file controls how a chosen unit is written; it does not replace the Section/Book planning pass.
4. Produce and show a planning package before drafting prose:
   - the complete Section arc and the role of all three books, when applicable;
   - the plan for each book, including promise, boundary, reader outcome, chapter or unit map, dependencies, evidence needs, and handoffs;
   - the research and reference tasks mapped to the planned claims or units;
   - the current S00-S09 and W00-W05 state, open decisions, and next controller.
5. Stop for author review and approval of the plan. Do not silently select an episode, invent a chapter, or begin manuscript prose during this planning pass.
6. After the relevant Section/Book plan and blueprint lock are approved, select an execution unit only as a downstream writing task. Apply the local structure exactly, complete the required review, and split into page or layout units only at the local structure's approved stage.

Do not open a new task with "which episode should I write?" or "write episode X" unless the parent plan and the book blueprint are already approved and the user explicitly wants execution of that unit. Use the existing S00-S09 and W00-W18 gates; this protocol changes the order of interaction, not the gate model.

### Agent dispatch rule

When a user asks to start or continue a book, the agent must read the current
manifest state and choose the next allowed work package from the state. The
agent must not ask the author to discover the workflow by choosing a random
chapter or episode.

| Current condition | Agent output | No prose drafting yet? |
| :-- | :-- | :-- |
| Section package or parent lock is missing or blocking | Section planning package and Section repair list | yes |
| Book intake, Blueprint, research design, literature review, source digest, or claim map is incomplete | Book planning/research package with source and claim tasks | yes |
| Section and Book locks pass for the relevant book | one approved unit execution packet | no, after the packet is accepted |
| Draft exists and author review or integrity/fact audit is open | the named review or audit packet | only the work allowed by that gate |
| Release or maintenance is open | the relevant release/maintenance checklist | no new structural drafting unless the gate allows it |

Every unit execution packet must name:

- `section_id`, `book_id`, `volume_number`, and `unit_id`
- the current Section and Book gate and their versions
- the unit purpose, reader outcome, and handoff
- claim IDs, source IDs or source tasks, counter-evidence, and wording limits
- the allowed edit scope and the expected artifact
- the reviewer, pass condition, open items, and next controller

If the required parent or Book artifact is missing, report that as a blocker and
create the handoff list. Do not manufacture a passing status from the presence
of a Blueprint, a bibliography, or a draft file.

### Reopen and drift rules

- If a Book change affects its role, promise, claim ownership, entry or exit condition, shared term, dependency, chronology, or handoff, reopen S04-S07 before continuing local drafting.
- If a source change affects a shared claim or the Section literature synthesis, reopen S03-S04 and the affected book gates W04, W05, or W10.
- If a change is local to wording, structure, or evidence inside one book and does not affect the parent fields above, keep it inside that Book's W00-W18 workflow and record the Section check as no-impact.
- Never update a child blueprint version without recording the Section Blueprint version it was checked against.
- A published book cannot silently become the new Section architecture. Reopen the Section workflow and create a new parent version when the architecture changes.
## Standard lifecycle

```text
W00 BOOK_INTAKE_AND_BOUNDARY
  -> W01 PROVISIONAL_BLUEPRINT
  -> W02 RESEARCH_DESIGN
  -> W03 LITERATURE_REVIEW
  -> W04 SOURCE_DIGEST_AND_PROVENANCE
  -> W05 CLAIM_MAP_AND_BLUEPRINT_LOCK
  -> W06 DRAFT_1
  -> W07 AUTHOR_REVIEW
  -> W08 DRAFT_2
  -> W09 MANUSCRIPT_INTEGRITY_CHECK
  -> W10 FACT_CITATION_AUDIT
  -> W11 DEVELOPMENTAL_REVIEW
  -> W12 DRAFT_3_EDITORIAL_REVISION
  -> W13 LINE_EDIT
  -> W14 COPYEDIT_AND_STYLE_SHEET
  -> W15 RIGHTS_LEGAL_ETHICS
  -> W16 PAGE_LAYOUT_INDEX_AND_PROOF
  -> W17 PUBLISH_AND_ARCHIVE
  -> W18 POST_PUBLICATION_MAINTENANCE
```

The lifecycle describes process state. It does not mean that every scientific,
medical, historical, or policy claim has been externally validated.

## Per-unit contract

Each book may define its own chapter, episode, section, or page structure. The
shared workflow does not replace or rename that local contract. Record the local
structure in the book's README and blueprint, then use stable chapter/episode
IDs when mapping sources and review results. This per-unit contract applies only
after the Section/Book planning pass and the relevant blueprint lock; it is not
the starting command for a new book.

For every writing unit, the normal order is:

```text
lock the local structure
  -> plan and digest sources
  -> write the unit
  -> author reviews meaning, tone, and intent
  -> revise into the next draft
  -> split into page/layout units when ready
```

Page splitting must not become a second place where unsupported claims are
introduced.

### Local structure versus workflow gates

The local structure may call a unit a chapter, episode, section, or another
book-specific name. That name is not a workflow gate. The Book Blueprint owns
the unit IDs and order; the local structure owns the writing rhythm; W00-W18
owns the evidence and review state.

For a unit-based book, use this practical loop inside the allowed Draft gate:

```text
approved unit_id
  -> source and claim task
  -> write the complete local structure
  -> author reviews meaning, tone, and intent
  -> revise the draft
  -> split into page/layout units
  -> run the required integrity and fact/citation checks
```

The eight-function pattern in `uet_history/3_publish/books/โครงสร้างหนังสือ.md`
is one local writing pattern. It is not a ninth gate, it does not define the
number of chapters in every book, and it does not authorize a new unit before
the Book Blueprint does.

## Reference workflow

Reference work has five distinct passes. They may loop, but they must not be collapsed into one bibliography step.

### 1. Research design

Before collecting a large source list, declare the review question, review mode, scope, search terms, databases or repositories, date and language boundaries, inclusion and exclusion rules, source hierarchy, cutoff date, and known blind spots.

### 2. Literature review

The literature review is a question-led synthesis of the field. It must identify established findings, major positions, methods and assumptions, agreement, controversy, contrary evidence, limitations, gaps, and the relationship to the book's own thesis or promise.

It is not a list of PDFs, an annotated bibliography, or one summary paragraph per author. Organize it by themes, positions, methods, historical periods, or concepts so relationships between sources are visible.

Minimum contents:

1. guiding question and relationship to the book promise
2. review mode, scope, cutoff date, languages, and disciplines
3. search locations, terms, dates, and screening method
4. inclusion and exclusion rules, including what was not searched
5. source and position map
6. critical appraisal of strengths, weaknesses, assumptions, and likely bias
7. consensus, disagreement, uncertainty, and contrary evidence
8. what is known, unknown, and contested
9. implications for the blueprint, claim map, and wording boundary
10. open gaps and the next research controller

### 3. Source digest and provenance

Each source receives a stable source ID and a record of what it can and cannot support.

Minimum source fields:

```text
source_id
full_citation
source_tier
source_type
source_role
claim_ids
unit_ids
exact_locator
quote_or_paraphrase
limitations_or_bias
accessed_at
snapshot_or_local_path
rights_or_permission_status
verification_status
notes
```

Use these source states when useful: `planned`, `located`, `read`, `appraised`, `extracted`, `claim_mapped`, `checked`, `used`, `superseded`, and `needs_replacement`.

Source tiers:

- `PRIMARY`  -  original study, dataset, archive, official record, firsthand interview, original document, or direct observation.
- `AUTHORITATIVE_SECONDARY`  -  systematic review, scholarly monograph, professional consensus, specialist reference, or high-quality institutional synthesis.
- `INSTITUTIONAL`  -  government, university, professional body, standards organization, or established archive.
- `TERTIARY_ORIENTATION`  -  textbook, encyclopedia, quality journalism, or overview used mainly to orient and find stronger sources.
- `LEAD_ONLY`  -  blog, social post, unsourced page, or search result used only to locate a stronger source or document a phenomenon that is itself the subject.

### 4. Reference planning and search log

After the provisional blueprint, create source tasks for every unit. A planned source is a research task, not a verified citation. Record search attempts, results screened, inclusion or exclusion decisions, and unresolved gaps.

### 5. Citation verification

After a draft exists, map every major factual, health, historical, technical, legal, or numerical claim to a checked source record. Record the exact page, section, figure, table, timestamp, archive item, DOI, PubMed record, publisher page, interview record, or stable URL when available.

Reader-facing citations may remain simple and accessible. The internal register must retain enough metadata and locators for another person to verify the claim.

```text
planned -> located -> read -> appraised -> extracted -> claim_mapped -> checked -> used
                                                            -> superseded
                                                            -> needs_replacement
```

## Claim, citation, and evidence standard

`CLAIM_MAP.md` is the bridge between the literature review and the manuscript.

For each high-impact claim record: claim ID, exact wording, unit ID, claim class, evidence class, source IDs, locator, limitations, counter-evidence, citation status, owner, and the strongest wording the evidence permits.

Claim classes should distinguish `FACT`, `INTERPRETATION`, `DERIVED_RELATION`, `HYPOTHESIS`, `ADVICE`, and `SPECULATION`.

Distinguish source roles:

- `CONSULTED`  -  read or considered during research
- `SUPPORTING`  -  selected to support a specific claim
- `CITED`  -  appears in the reader-facing citation or note
- `COUNTER_EVIDENCE`  -  qualifies or challenges the claim
- `BACKGROUND`  -  informs framing but does not support a specific assertion

Do not turn a correlation into causation, a fit into a prediction, an internal rerun into external validation, a plausible mechanism into a proved result, or an author's synthesis into an established fact.
## Minimum book package

Every active book should expose or locally maintain the following, using existing canonical filenames when they already exist:

```text
README.md
BOOK_MANIFEST.json
RESEARCH_BRIEF.md or equivalent
RESEARCH_DESIGN.md or equivalent
book blueprint or existing outline file
LITERATURE_REVIEW.md or 2_digest/LITERATURE_REVIEW.md
REFERENCE_REGISTER.md
SOURCE_DIGEST.md or 2_digest/
CLAIM_MAP.md
VERIFICATION_SPEC.md
STYLE_SHEET.md
PERMISSIONS_REGISTER.md when applicable
UPDATE_LOG.md
1_raw/       local-only source material
ch_drafts/   local-only working drafts
```

For a sectioned three-book project, the parent package additionally contains:

```text
SECTION_MANIFEST.json
SECTION_BLUEPRINT.md
SECTION_RESEARCH_DESIGN.md
SECTION_LITERATURE_REVIEW.md
SECTION_CLAIM_MAP.md
VOLUME_MATRIX.md
DEPENDENCY_MAP.md
SHARED_TERMS.md
SECTION_UPDATE_LOG.md
```

Read these package lists cumulatively, not as a requirement to create empty
documents on day one. The manifest must show future outputs as `NOT_STARTED` and
the required artifact must exist before its gate can pass. The practical minimum
for each stage is the output named by that gate plus the upstream records it
depends on.

Do not create semantic aliases merely to satisfy this list. If an existing book uses another filename or folder convention, record the mapping in its README or manifest.

An evidence-led book cannot pass W05 without a literature review, source register, and claim map. A production release cannot pass W17 without the final manifest, registry, public manifest, and update log agreeing.
## Gate model and detailed requirements

Use one of these states for every gate: `NOT_STARTED`, `IN_PROGRESS`, `PASS`, `PASS_WITH_OPEN_ITEMS`, `BLOCKED`, or `SUPERSEDED`.

Every gate record exposes `gate_id`, `status`, `owner`, `completed_at`, `artifact_paths`, `decision`, `open_items`, `controlling_blocker`, `next_controller`, and `claim_boundary`.

### W00 BOOK_INTAKE_AND_BOUNDARY

- Output: `BOOK_MANIFEST.json` and a research brief, or equivalent fields in the canonical README.
- Record: book ID, title, profile, audience, language, promise, scope, exclusions, owner, format, risk level, and claim boundary.
- For a Section child, also record section_id, volume_number, section_blueprint_version, and the parent gate state.
- Pass: a new collaborator can state the reader, deliverable, boundary, and next decision without guessing.
- Return: revise the brief before collecting sources or expanding the manuscript.

### W01 PROVISIONAL_BLUEPRINT

- Output: provisional outline with stable unit IDs, reader outcomes, throughline, open questions, and evidence needs.
- For a Section child, map every unit to its parent Section role and record the expected input and handoff.
- The blueprint is allowed to change after the literature review.
- Pass: every unit has a purpose and the book has a visible argument or reader journey.
- Return: narrow the promise, split overloaded units, or remove unsupported scope.

### W02 RESEARCH_DESIGN

- Output: `RESEARCH_DESIGN.md`, a research brief section, or equivalent review plan.
- Record: question, mode, search terms, locations, source types, dates, languages, inclusion and exclusion rules, hierarchy, cutoff date, and blind spots.
- Pass: another researcher could repeat the search logic and understand why important sources were included or excluded.
- Return: fix scope or search design before calling the source list a review.

### W03 LITERATURE_REVIEW

- Output: `LITERATURE_REVIEW.md` or equivalent section in `2_digest/`.
- Pass only when the review synthesizes positions, methods, findings, controversy, contrary evidence, limitations, gaps, and implications for the book.
- A bibliography or source digest alone is not a pass.
- Return: W02 for inadequate coverage or W04 for sources that cannot be appraised.

### W04 SOURCE_DIGEST_AND_PROVENANCE

- Output: `REFERENCE_REGISTER.md`, `SOURCE_DIGEST.md`, or the canonical equivalent.
- Every high-impact source has identity, tier, role, exact locator, key support, limitations, access date, and rights status.
- Pass: a reviewer can locate the passage, page, figure, table, timestamp, archive item, or interview record behind each major planned claim.
- Return: locate a stronger source, narrow the claim, or label it interpretation or hypothesis.

### W05 CLAIM_MAP_AND_BLUEPRINT_LOCK

- Output: `CLAIM_MAP.md` and the locked blueprint.
- Every major claim has a claim ID, exact wording, class, evidence class, source IDs, counter-evidence, limitations, locator, and status.
- Pass: no major claim is orphaned and the locked blueprint reflects what the review supports.
- For a Section child, the local lock must cite a passing or non-blocking Section Blueprint version.
- Return: revise the claim, add evidence, change structure, or reopen W03.

### W06 DRAFT_1

- Output: one canonical content-complete Draft 1 with stable unit IDs and visible citation placeholders or source links.
- Mark uncertainty and open research questions instead of silently filling gaps with confident prose.
- Pass: every unit has a reader purpose, throughline, and relationship to the claim map.
- Return: W05 for structure or W04 for support.

### W07 AUTHOR_REVIEW

- Output: author review or decision log.
- Review meaning, intent, voice, audience fit, omissions, continuity, and ethical concerns.
- Separate accept, revise, defer, reject, and needs-evidence decisions.
- Pass: author decisions are explicit and do not silently change claim strength.

### W08 DRAFT_2

- Output: canonical Draft 2 plus a change record.
- Update the claim map, source register, and unit IDs when meaning or structure changes.
- Pass: manuscript and control records agree.
- Return: reopen W07 or W05 rather than patching around discrepancies.

### W09 MANUSCRIPT_INTEGRITY_CHECK

- Output: before/after manifest, verification log, and machine-check result when available.
- Before editing, record canonical file, hash or snapshot, line and word counts, unit IDs, headings, tables, citations, links, figures, and protected passages.
- After editing, verify expected units, headings, reference sections, links, no unplanned removals, no duplicated markers, and no changes outside scope.
- Counts are diagnostics, not proof of quality.
- Pass: every difference is explained by the request or recorded as an intentional decision.
- Return: restore or reconcile the canonical draft.

### W10 FACT_CITATION_AUDIT

- Output: `VERIFICATION_SPEC.md`, claim audit, or equivalent checked matrix.
- Check wording, authority, scope, locator, date sensitivity, quote accuracy, numbers, names, units, causal language, health or financial advice, historical attribution, and limitations.
- Pass: no high-impact claim is unsupported, overgeneralized, misquoted, stale without a date boundary, or stronger than its evidence.
- Return: replace the source, narrow the wording, add a limitation, or reclassify the claim.

### W11 DEVELOPMENTAL_REVIEW

- Output: developmental review letter, chapter map, or structured issue list.
- Check reader promise, order, pacing, repetition, bridges, balance, unresolved terms, conclusion, and evidence-to-narrative relationship.
- Pass: the manuscript's structure serves its audience and claim boundary.
- Return: W05 for architecture or W12 for editorial revision.

### W12 DRAFT_3_EDITORIAL_REVISION

- Output: canonical Draft 3 or named editorial revision wave.
- Update blueprint, claim map, references, and update log when affected.
- Pass: major structural issues are closed or explicitly bounded; no new major claim bypassed W04 and W10.
- Return: W11 or W10.

### W13 LINE_EDIT

- Output: line-edited manuscript and unresolved meaning questions.
- Improve sentence clarity, rhythm, transitions, voice, and accessibility without changing evidence status.
- Pass: language serves the reader while preserving meaning and claim class.
- Return: W12 for meaning changes or W10 for evidence-strength changes.

### W14 COPYEDIT_AND_STYLE_SHEET

- Output: copyedited manuscript and `STYLE_SHEET.md`.
- Check grammar, punctuation, names, transliteration, numbers, units, terminology, headings, cross-references, citation format, tables, captions, and links.
- Pass: manuscript and style sheet agree and no copyedit silently alters a claim.
- Return: W13 for prose or W10 for factual meaning.

### W15 RIGHTS_LEGAL_ETHICS

- Output: `PERMISSIONS_REGISTER.md` when applicable, risk notes, consent records, attribution records, and professional review where needed.
- Check quotes, images, tables, screenshots, translations, archival material, interviews, living persons, private information, medical claims, financial guidance, and jurisdiction-sensitive wording.
- This is a workflow safeguard, not legal advice.
- Pass: every restricted asset or high-risk passage has a documented disposition.
- Return: obtain permission, remove or replace material, narrow wording, add disclosure, or seek qualified review.

### W16 PAGE_LAYOUT_INDEX_AND_PROOF

- Output: final layout, table of contents, index when appropriate, figure and caption list, link check, and proof report.
- Check page breaks, headings, tables, figures, captions, notes, cross-references, running heads, fonts, encoding, accessibility, and print or ebook rendering.
- Proofreading is comparison of the proof against the edited manuscript; it is not a substitute for fact-checking or developmental editing.
- Pass: proof corrections are resolved and the release proof is frozen.
- Return: W14 for text changes or rerun W16 after layout changes.

### W17 PUBLISH_AND_ARCHIVE

- Output: final release manifest, final file hashes when practical, registry update, public manifest update, release note, and archived source package.
- Confirm canonical path, public path, version, date, license, permissions, and excluded local material.
- Pass: public files, registry state, and canonical source agree.
- Return: stop publication and repair path or manifest drift.

### W18 POST_PUBLICATION_MAINTENANCE

- Output: maintenance log, correction note, replacement source record, or new-edition change log.
- Do not silently rewrite a published copy when meaning, evidence, attribution, or safety changes.
- Pass: every post-publication change has a reason, scope, date, reviewer, and version boundary.
- Return: open a correction or new-edition wave.

## Manuscript integrity and in-place edit protocol

For an existing manuscript, the default is controlled in-place enrichment: preserve original prose and structure unless the request explicitly authorizes a rewrite, deletion, merge, or reorder.

Before an edit:

- identify the canonical file and working branch
- record a hash or snapshot when practical
- record counts, unit IDs, headings, tables, reference sections, links, figures, and protected passages
- state the exact allowed scope and expected output

After an edit:

- rerun relevant structural and content checks
- compare the before/after manifest, not just the final line count
- verify no unplanned unit, paragraph, citation, link, table, or figure disappeared
- inspect changed claims for evidence and wording drift
- record the change, verifier, result, unresolved issue, and next wave in `UPDATE_LOG.md`

Line count, header count, or a passing script is an integrity signal only. It is not proof that the research, citations, argument, or language are correct.

## Editorial layers

Keep these layers separate:

- developmental editing: content, organization, argument, genre, audience, and big-picture revision
- line editing: sentence and paragraph language, rhythm, clarity, tone, and style
- copyediting: grammar, usage, punctuation, cross-references, terminology, and style-sheet consistency
- proofreading: final proof, typographical errors, formatting, and comparison against the edited manuscript
- fact-checking: deeper verification of factual assertions, especially in history and narrative non-fiction
- permissions management: copyright ownership, licenses, attribution, and approval records

A single person may perform more than one role, but the work product and gate remain distinguishable.

## Book-type profiles

- Evidence-led theory or research non-fiction: complete W02-W10, including a real literature review and claim map.
- Popular science or public knowledge: usually `NARRATIVE_CRITICAL`; retain source digest, contrary evidence, and fact audit even when reader-facing citations are light.
- History or biography: use `ARCHIVAL_SOURCE_CRITICISM`, primary-source provenance, corroboration, interview records, and higher W15 sensitivity review for living people or private information.
- Memoir or experience-led writing: use primary-source documentation for factual claims; use targeted literature review for health, psychology, history, or social claims.
- Fiction or creative non-fiction: use targeted research for technical, historical, cultural, or real-person material; real-world assertions still enter fact and rights gates.

## Human and AI roles

Humans decide research scope, source authority, claim class, uncertainty, ethical risk, permissions, final wording, and publication status.

AI may discover leads, summarize a checked source, build tables, compare drafts, identify missing citations, and run structural audits. AI output is never itself a source. AI must not invent citations, fill missing evidence, silently rewrite protected prose, or promote a gate.

## Review gates

The detailed gate requirements above are normative. A gate passes only when its named artifact and pass condition are checked.

Human review is required before publication state or claim boundary is promoted. AI may draft, map, compare, and audit; it may not promote evidence by itself.
## Wave contract

Each completed wave records:

1. what artifact changed
2. what was reviewed or rerun
3. what blocker narrowed
4. what controls the next wave
5. whether claim wording changed

The book's `UPDATE_LOG.md` is the detailed handoff. The repo `WORK_LEDGER/`
records the completed section at repository level when appropriate.

## Version rule

Use wave names and one canonical working draft rather than many large duplicate
manuscript files:

```text
W06 Draft 1
W07 author review
W08 Draft 2
W10 fact/citation audit
W12 Draft 3 editorial revision
W16 release proof
W17 publish/archive
```

Git history plus `UPDATE_LOG.md` is the normal version trail. A separate
snapshot is only needed for a meaningful milestone or external handoff.

## Applying the standard to a book

For a book inside a three-book Section, inspect the parent Section package first. The Section gates decide the allowed role, dependencies, handoffs, and claim boundary of the local book.

For a new or existing book:

1. inspect the existing canonical folder and registry entry
2. preserve the book's current voice, structure, and filenames
3. add the minimum workflow package where the book's policy allows it
4. declare the current process stage, claim boundary, and controlling blocker
5. if the Section/Book plan is not approved, produce the planning package first; do not begin by asking the author to select a chapter or episode
6. after the plan and blueprint lock, run one approved chapter or episode as a controlled execution unit before applying the workflow to the whole book
7. promote public files only after the registry and public manifest agree

For a workflow-standard audit or repair, limit the change to the shared standard,
agent instructions, templates, and the handoff report unless the user explicitly
authorizes edits to a Section or Book package. Do not rewrite manuscript prose,
move book folders, or mark a gate complete as a side effect of standardization.

The workflow is reusable across books; the source register, claim map, and local
chapter structure remain book-specific.

## External process references

This workflow adapts common distinctions used in professional non-fiction
publishing and editorial work:

- [Penguin Random House: How Can I Get Published?](https://www.penguinrandomhouse.com/articles/how-can-i-get-published/)
- [Editorial Freelancers Association: Hiring an Editor](https://www.the-efa.org/wp-content/uploads/2025/04/EFA-Hiring-an-Editor-A-Guide-for-New-Authors_REV-7-2022.pdf)
- [Authors Guild: documenting fact-finding and sources](https://authorsguild.org/app/uploads/2022/11/Chapter-8_Writers-Legal-Guide.pdf)
- [University of Toronto: what a literature review should do](https://advice.writing.utoronto.ca/types-of-writing/literature-review/)
- [Chicago Manual of Style: citation systems](https://www.chicagomanualofstyle.org/tools_citationguide.html)
- [Zotero documentation: organizing sources and notes](https://www.zotero.org/support/quick_start_guide)
