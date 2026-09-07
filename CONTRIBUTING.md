# Contributing to Unity Equilibrium Theory

This repository contains research, theory history, book work, Thailand policy
proposals, optional services, and repository operations. Contributions must keep
each area understandable, traceable, and safe to publish.

This file is the contribution entrypoint. It does not replace the detailed
standards. The canonical research manual is
[\`docs/topics/For Work/\`](docs/topics/For%20Work/). The root
[\`AGENTS.md\`](AGENTS.md) defines the day-to-day agent workflow.

## Source of truth and workspace routing

| Area | Canonical workspace | Use it for |
| --- | --- | --- |
| Research core | \`docs/core/\`, \`docs/topics/\` | equations, methods, experiments, evidence, topic status |
| Research standards | \`docs/topics/For Work/\`, \`AGENTS.md\` | shared workflow and claim/data/formula/result rules |
| Theory history | \`uet_history/\` | historical theory notes and archive structure |
| Book writing | \`uet_history/3_publish/books/\` | canonical book identity, blueprints, reviewed public files |
| Thailand policy | \`thailand_proposals/\` | policy and project proposals |
| Services and tools | \`services_and_experiments/\` | optional KB, agents, API, GraphQL, Rust, and automation |
| Repository operations | \`.github/\`, \`WORK_LEDGER/\`, root manifests | CI, checkpoints, publishing, and hygiene |
| Raw or private work | ignored local paths | raw sources, private exports, large media, scratch work |

For path decisions, read [\`CONTEXT-MAP.md\`](CONTEXT-MAP.md). Existing
canonical paths win. Do not create a second semantic folder because an old path
is inconvenient. If a migration is needed, record the old path, replacement
path, and public boundary first.

## Read before editing

Start with:

1. [\`README.md\`](README.md)
2. [\`AGENTS.md\`](AGENTS.md)
3. [\`docs/topics/README.md\`](docs/topics/README.md)
4. [\`docs/topics/For Work/00_README.md\`](docs/topics/For%20Work/00_README.md)

Then read the narrowest relevant standard:

- governance and AI: \`01_Project_Research_Constitution.md\`,
  \`03_AI_Usage_and_Governance.md\`, \`04_Claim_and_Evidence_Rubric.md\`
- topic lifecycle and structure: \`02_Project_Workflow_and_Lifecycle.md\`,
  \`10_Topic_Architecture_5x5(+1).md\`
- code, data, references, results, formulas: standards \`11\` through \`17\`
- hardening and history: \`18_Research_Hardening_Workflow.md\`,
  \`24_TEMPLATE_UPDATE_LOG.md\`
- books: [\`uet_history/BOOK_WORKFLOW.md\`](uet_history/BOOK_WORKFLOW.md),
  [\`uet_history/3_publish/books/README.md\`](uet_history/3_publish/books/README.md),
  [\`BOOK_REGISTRY.json\`](uet_history/3_publish/books/BOOK_REGISTRY.json)

For AI work, use
[\`26_AI_AGENT_SKILL_MAP.md\`](docs/topics/For%20Work/26_AI_AGENT_SKILL_MAP.md)
and [\`27_AI_AGENT_ROUTING_MATRIX.md\`](docs/topics/For%20Work/27_AI_AGENT_ROUTING_MATRIX.md).
Skills are adapters, not sources of truth.

## Evidence and claim discipline

The repository must preserve the difference between an idea, a model, an
internal benchmark, and externally supported research.

- Do not let prose outrun the latest artifact, gate, manifest, or source record.
- Keep theory separate from benchmark behavior, fitting separate from
  prediction, and internal evidence separate from external evidence.
- Record formula origin, variable meaning, units, derivation class, and proof
  status before presenting a formula as established.
- Record source identity, DOI or URL when available, terms, preprocessing,
  units, local path, hash or version, and benchmark role for important data.
- Treat \`solved\`, \`proved\`, \`verified\`, \`exact\`, and \`production grade\` as
  restricted wording. Prefer \`hypothesis\`, \`proposal\`, \`model\`,
  \`derived relation\`, \`reproduced internally\`, or
  \`passes current internal benchmark\`.
- If documents disagree with a stable artifact or machine-readable gate, use
  the latest stable artifact or gate as controlling state and record the drift.
- A folder existing, a script running once, or a polished figure is not proof
  of a stronger readiness level.

See
[\`04_Claim_and_Evidence_Rubric.md\`](docs/topics/For%20Work/04_Claim_and_Evidence_Rubric.md)
and the [documentation style guide](docs/UET_Documentation_Details/STANDARDS/documentation_style_guide.md).

## Standard work packages

### Research topics

Use the current \`5x5(+1)\` architecture and lifecycle in \`For Work\`; do not
copy the retired 5x4 or Triple-Green rules. Required files depend on readiness
stage. A serious structured topic normally exposes the relevant set of:

- \`README.md\` with problem, scope, assumptions, method, evidence/status
  matrix, conceptual diagram, limitations, reproducibility, and readiness
- \`METHOD.md\` or an equivalent method record
- \`DATA_MANIFEST.md\` for important inputs
- \`FORMULA_AUDIT.md\` for formula origin, units, constants, proof status
- \`VERIFICATION_SPEC.md\` for metrics, thresholds, baselines, and rerun rules
- \`LIMITATIONS.md\` for boundaries and failure modes
- scripts, inputs, and traceable result artifacts
- \`UPDATE_LOG.md\` after repeated hardening or when durable reconstruction is needed

Promote only when the evidence and artifacts for the next stage exist. Demote
when provenance, reproducibility, or claim support weakens.

### Books and theory history

\`BOOK_REGISTRY.json\` controls book identity, canonical paths, public paths, and
publication state. Before creating or moving a book:

1. inspect the registry and existing folder
2. update the canonical folder, never a semantic alias
3. keep \`1_raw/\` and \`ch_drafts/\` local unless a reviewed public file is listed
4. keep Section manifests, blueprint, volume matrix, dependency map, shared
   terms, and update log aligned
5. keep W00-W18 gates distinguishable; a planned source is not a citation
6. preserve one canonical working source and record each writing wave locally

A book update is complete only when source, registry, scoped commit, and public
\`main\` path agree.

### Thailand policy and project proposals

Use \`thailand_proposals/\` for proposal narratives, source-backed assumptions,
budgets, implementation plans, and presentation inputs. Keep proposal claims
separate from research-topic readiness. Large raw media and source files remain
local and are named in a manifest when needed for provenance.

### Services, knowledge base, and platform experiments

Research must work when services are stopped. \`services_and_experiments/\` is
an optional future platform layer:

- \`uet_core\` may provide tested reusable code but does not own research status
- \`uet_kb\` is an optional derived retrieval index
- agents orchestrate work but do not decide claim or readiness status
- API, GraphQL, MCP, and other interfaces need a real use case, stable
  input/output schema, provenance, regeneration path, tests, and manageable cost

\`docs/knowledge_base/\` and vector, SQLite, LanceDB, or PostgreSQL indexes are
derived retrieval layers. They must point to canonical sources and never
control claims, status, or publication.

## The standard contribution loop

Every substantial section of work follows this loop:

1. **Classify.** Choose the area id in \`WORK_LEDGER/AREAS.md\`, workspace, and
   intended public boundary.
2. **Inspect.** Check \`git status\`, canonical sources, artifacts, gates,
   manifests, and update-log evidence.
3. **Read.** Use the narrowest governing \`For Work\` or book guide.
4. **Edit.** Change the canonical source, not a derived index, screenshot, copy,
   or public alias.
5. **Review.** Run the relevant verifier, formula audit, provenance audit,
   artifact review, manuscript gate, test, or link check.
6. **Synchronize.** Update topic/book \`UPDATE_LOG.md\` when a wave completes
   and add one factual daily \`WORK_LEDGER/YYYY/\` entry.
7. **Inspect scope.** Review \`git diff --stat\`, changed paths, ignored raw
   paths, and claim wording. Keep standards and topic changes separate unless linked.
8. **Commit.** Commit only a safe, coherent unit.
9. **Publish.** Push the branch or open/update a draft PR the same day and
   verify the remote points to the commit just made.

These records are different:

| Record | What it proves |
| --- | --- |
| \`WORK_LEDGER/\` | what work section happened and what remains |
| commit | which files changed together |
| push or PR | which change is visible remotely |
| topic/book \`UPDATE_LOG.md\` | how a local wave changed its blocker or stage |
| artifact, gate, or manifest | what was measured, checked, or sourced |

A ledger entry never replaces an artifact, manifest, or gate.

## Ledger checkpoint rule

Each completed section gets a short entry containing:

- timestamp or section label
- area id and workspace or topic
- files or artifact group changed
- verifier, audit, or review actually run
- public-safety status: \`safe\`, \`partial\`, \`private\`, or \`blocked\`
- what remains uncommitted, private, or unsafe to publish
- next commit, push, PR, or manifest action

When 10 entries accumulate for current unpushed work:

1. stop expanding scope
2. inspect status and stage only the safe coherent unit
3. commit it
4. push or open a draft PR the same day
5. record any blocker and exact next action before continuing

Do not begin an eleventh entry without making that checkpoint decision.

## Public boundary and file hygiene

Do not commit secrets, credentials, \`.env\` files, private exports, build
outputs, caches, compiled binaries, debug output, or unreviewed raw media.
The \`.gitignore\` is the default boundary, but always review the staged list.

- Raw sources belong in the appropriate ignored raw directory.
- Book \`1_raw/\` and \`ch_drafts/\` remain local by default.
- Large proposal media belongs in a manifest, not a normal documentation commit.
- Generated indexes, caches, logs, and local databases are derived outputs.
- Never use hardcoded paths such as \`C:/Users/...\`; use repo-relative paths and
  path helpers.
- When a raw input is needed to explain a public result, publish provenance and
  regeneration instructions, not the raw asset by default.

Do not rely on a broad \`git add\` when unrelated local work exists. Inspect the
exact intended file list before staging.

## Coding and reproducibility expectations

- Keep derivation-critical logic visible; do not hide claim-producing behavior
  behind vague helpers.
- Give runnable scripts clear inputs, outputs, units, assumptions, and failure
  conditions.
- Make figures and reports traceable to scripts, inputs, configuration, metrics,
  and thresholds.
- Use existing path and import conventions instead of global aliases.
- Add tests or validation at the boundary affected by the change.
- Document only commands that were actually run. Do not claim the whole repo is
  green because one script ran.

## AI-assisted contributions

AI may help with exploration, drafting, coding, auditing, summarizing, and
presentation preparation. The contributor remains responsible for checking
sources, evidence, code, and final claims.

AI-assisted work must:

- read \`AGENTS.md\` and the governing local standard before editing
- distinguish repository facts from inference
- preserve source, artifact, gate, manifest, and log boundaries
- avoid upgrading evidence or readiness because wording sounds confident
- leave a human-reviewable diff and name checks that actually ran
- use the narrowest skill instead of creating a mega-skill

See [\`03_AI_Usage_and_Governance.md\`](docs/topics/For%20Work/03_AI_Usage_and_Governance.md).

## Validation checklist

Before committing, confirm what applies:

- [ ] canonical path and governing standard identified
- [ ] no duplicate semantic path or stale alias created
- [ ] claims match artifact, gate, manifest, and source evidence
- [ ] formulas have origin, units, variable definitions, and proof status
- [ ] data provenance and preprocessing recorded
- [ ] result artifacts identify inputs, metrics, thresholds, and verifier
- [ ] relevant verifier, test, audit, or manuscript gate actually ran
- [ ] topic/book \`UPDATE_LOG.md\` updated when required
- [ ] factual \`WORK_LEDGER\` entry added
- [ ] raw, private, cache, build, binary, and secret files excluded
- [ ] \`git diff --check\` clean
- [ ] staged file list is the intended coherent unit
- [ ] commit is pushed or draft PR remote state is verified

## Branches, commits, and pull requests

The normal path is a focused \`codex/...\` or feature branch plus a PR. Keep a
PR small enough to identify source of truth, evidence boundary, validation, and
remaining blockers.

Each PR should state:

- area and canonical workspace
- reason for the change
- files or artifact groups included
- checks actually run and result
- claim or readiness impact
- raw/private files deliberately excluded
- next blocker or follow-up action

Use direct push to \`main\` only when the repository owner explicitly requests
it and the unit is coherent, validated, and safe. Verify the remote \`main\` SHA
after pushing. Otherwise use a draft PR when work or its public boundary is incomplete.

Do not mix unrelated cleanup, generated output, or speculative architecture work
into a research or book commit. If a shared standard must change to make a wave
reproducible, link that change to the pilot in the relevant update log.

## Useful entrypoints

- Research standards: [\`docs/topics/For Work/00_README.md\`](docs/topics/For%20Work/00_README.md)
- Topic index and status: [\`docs/topics/README.md\`](docs/topics/README.md)
- Repository routing: [\`CONTEXT-MAP.md\`](CONTEXT-MAP.md)
- Agent rules: [\`AGENTS.md\`](AGENTS.md)
- Book workflow: [\`uet_history/BOOK_WORKFLOW.md\`](uet_history/BOOK_WORKFLOW.md)
- Book identity and public boundary: [\`BOOK_REGISTRY.json\`](uet_history/3_publish/books/BOOK_REGISTRY.json)
- Work history: [\`WORK_LEDGER/\`](WORK_LEDGER/)
- AI skill routing: [\`27_AI_AGENT_ROUTING_MATRIX.md\`](docs/topics/For%20Work/27_AI_AGENT_ROUTING_MATRIX.md)

The goal is not to make the repository look busy. It is to make each
meaningful change understandable, reproducible within its stated boundary, and
visible in the right history.

## Branch lifecycle and CI enforcement

main is the public canonical branch. The normal path is one focused,
short-lived branch plus a PR:

    codex/research/<task>
    codex/book/<task>
    codex/history/<task>
    codex/policy/<task>
    codex/services/<task>
    codex/repo/<task>

Do not create permanent develop, staging, or topic branches. A local branch
that tracks origin/main is not the canonical main worktree. Before cleanup,
inspect every worktree, remote head, PR, and unique commit. Run
git fetch --prune origin to remove stale origin/codex/... tracking refs. Delete
a branch only after confirming it is merged or explicitly superseded and has no
unique work. Never delete a dirty worktree.

The repository ruleset should require PR checks, prevent force-push and deletion
of main, and auto-delete a merged PR head branch. No approval is required while
this is a single-maintainer repository, but every required check must pass
visibly. Direct push to main is an explicitly documented emergency only; record
the reason in WORK_LEDGER/ and verify the local, remote, and GitHub main SHA.

CI is split by responsibility:

- pr-scope.yml checks branch naming, diff whitespace, raw/private/binary/cache
  boundaries, JSON syntax, and path drift.
- pr-validation.yml runs checks only for changed areas.
- main-validation.yml runs after merge and stores validation reports.
- nightly-research-audit.yml runs deeper audits on schedule or manual dispatch;
  it never edits or pushes the repository.
- GitHub Pages has its own workflow. Railway, API, and other platform deploys
  remain paused until a real client, stable interface, provenance boundary,
  tests, and regeneration path exist.

Required checks must fail when their validation fails. Existing baseline
failures must be repaired or explicitly moved to a visible, time-bounded
non-required audit before a full suite becomes a required merge gate; they may
not be hidden with continue-on-error.

The PR template is the minimum submission contract. The work ledger, commit,
PR/push, topic update log, and artifact/gate are separate records.
