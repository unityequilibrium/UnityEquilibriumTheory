# UET Repo Work Ledger

This folder records Harness work. Research and historical book work have separate
reading views, while original daily records remain the single source of history.

## Choose A Work Stream

| View | Meaning | Boundary |
| --- | --- | --- |
| [Research](RESEARCH.md) | Research topics, research standards and evidence work | Not book drafting, publication administration or proof of a scientific claim |
| [Book history](BOOK_HISTORY.md) | Earlier book-writing and theory-history records | Historical only: the owner moved that workspace out on 2026-11-03 |
| [Operations](OPERATIONS.md) | Repository maintenance, tools, policy and documentation | Supporting work, not automatically a research result |
| [Mixed records](MIXED.md) | Both research and books appear as primary domains | Must not be silently counted as either single-domain result |
| [Review queue](REVIEW.md) | Missing/conflicting metadata or structural warnings | Provisional routing is explicit; original records are preserved |

**Harness agents must not inspect, edit, synchronize or publish the separate
Superapp project.** Downstream reading of Harness sources does not authorize the
reverse direction. New manuscript work is not a Harness work stream. Do not
create a replacement book workspace, copy manuscripts into this ledger, or fetch
the moved books to populate an index.

Use it to keep daily progress visible across:

- research topics and standards
- historical theory and book records (not ongoing manuscript work)
- Thailand policy proposals
- services, experiments, MCP, GraphQL, and tooling
- repository operations, GitHub Actions, manifests, and agent rules
- raw/private source handling decisions

The ledger answers one question: what work moved today, what can be published,
and what still needs a commit, push, PR, or manifest?

## Daily Files

Use one file per day under the year folder:

```text
WORK_LEDGER/2026/2026-07-04.md
```

Each completed section of work should add one short entry. If 10 entries exist
for unpushed work, stop expanding scope and make a checkpoint before continuing.

## Recording New Work

Use [TEMPLATE.md](TEMPLATE.md) and [AREAS.md](AREAS.md). Every entry identifies
`Stream`, a primary `Area`, workspace, actual changes, validation, public-safety
boundary, publication evidence and one next action. Do not mix a research wave
and a writing wave in one entry merely because both concern physics or biology.

- A paper/source review for a book belongs to book history, not research-core,
  unless a separate canonical research result was actually produced.
- `repo-ops` with research as a secondary area is still operations. A publication
  checkpoint spanning books/research records publishing work, not new results.
- Use `mixed` only when an old coherent record cannot be separated without
  rewriting history. For new work, use distinct entries and link dependencies.
- A new `book-history` entry is limited to a Harness-side archival or migration
  decision; it is not permission to work on the moved project.
- The ten-entry checkpoint counts real unpushed sections across streams, not
  rows in these indexes. Never use generated counts to infer commit/push status.

## Index And Source Discipline

Daily files stay in `YYYY/YYYY-MM-DD.md`; existing root-level daily files are
legacy sources, not deleted duplicates. All dated Markdown files inside this
ledger are indexed, including days containing both domains. Templates and monthly
communication packs are auxiliary documents, not completed-work entries.

`INDEX.json` records every source SHA-256, entry location/hash, classification
basis, flags and exact duplicates. The five Markdown views are derived from it.
They contain links, not copied ledger bodies or relocated book content. All views
are rebuilt from the local source revision; they are not a repo-wide progress or
physics-status controller. Identical records are marked, never automatically
deleted. Multiple daily files with the same date are listed for review.

Classification prefers explicit stream/primary area, then legacy area syntax,
then structured workspace or legacy research-wave metadata. Secondary areas do
not override the primary domain. A missing/contradictory record stays visible in
the review queue. Do not infer classification from unrelated narrative words.

Rare reviewed exceptions live in `CLASSIFICATION_OVERRIDES.json`, with the exact
entry id/hash and a factual reason. This is metadata review, not external or
scientific validation. A changed source invalidates the decision and returns it
to review; never change source bytes just to make an override match.
An explicitly reviewed hash variant may cover the same old text with different
line endings; it is an exact allow-list, never a wildcard for future edits.

Regenerate after adding a daily entry, changing source metadata or reviewing a
classification. Commit source, reviewed exception and derived views together:

```powershell
python docs/scripts/maintenance/build_work_ledger_index.py
python docs/scripts/maintenance/build_work_ledger_index.py --check
python -m unittest discover -s docs/scripts/maintenance -p test_work_ledger_index.py
```

Use the existing Python environment when needed. `--check` never rewrites files;
it fails on stale views, missing/new sources, or changed source hashes. CI validates
only; it must not regenerate and commit on the user's behalf.

## Relationship To Other Logs

- `WORK_LEDGER/` records repo-wide daily operating history.
- Topic `UPDATE_LOG.md` files record research-state changes for that topic.
- Manifests record what was included, excluded, private, duplicated, or too large.
- Git commits and PRs are the durable public evidence that work actually moved.

## Public Updates

Research updates draw from the Research view plus current research artifacts,
gates and topic logs. Historical book records must be labeled historical and
must not be counted as current Harness research or current Superapp progress.
Policy/tooling updates identify their own stream. Publication text still needs
the actual commit, PR or release reference; no index count proves publication.

Do not use this ledger to upgrade research claims or replace artifacts. Use it
to prevent work from disappearing into local-only branches.
