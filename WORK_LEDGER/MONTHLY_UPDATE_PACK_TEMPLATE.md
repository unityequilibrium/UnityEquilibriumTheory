# Monthly Update Pack Template

Use this template for one public-facing work update per month. It is a communication
layer, not a replacement for the daily work ledger, topic artifacts, proposal drafts, or
book manuscripts.

## Operating rule

- Work may happen at any time and should be recorded in the relevant ledger or source file.
- Research receives a short weekly pulse check; a public post is optional unless there is a
  meaningful artifact, finding, or blocker change.
- Review current Harness work as `R` research, `P` policy / mega project and `O`
  operations/tooling. Use the separate ledger views in [README.md](README.md).
- Legacy `S`, `T` and `B` book categories are historical appendices only after
  the 2026-11-03 relocation. Do not collect current manuscript or Superapp
  progress, recreate its workspace, or count historical book entries as research.
- If nothing materially changed, write `No material change` and retain the current stage.
- Remove completed items from the active plan if desired, but keep the pack and source record.

## Controlled process stages

`INBOX` → `FRAMING` → `BLUEPRINT` → `DRAFT / BUILD` → `REVIEW` → `READY` → `PUBLISHED` → `MAINTENANCE`

W00-W18 book gates and S00-S09 Section gates in older packs describe the former
workspace. They are not current Harness controllers. Any historical book appendix
must state its source date and link to an existing historical ledger record;
otherwise mark it `Not maintained in Harness`. Do not infer a present book stage
or fetch the separate project to complete the pack.
The stage describes where the work is in its process. It does not mean that the work is
scientifically validated or publication-ready.

## Stream mapping

| Code | Stream | Primary workspace |
| --- | --- | --- |
| `R` | Research | `docs/topics/`, `docs/meta/` |
| `P` | Policy / mega project | `thailand_proposals/` |
| `O` | Operations / tooling | `.github/`, `services_and_experiments/`, repo documentation |
| `S` | Historical Section record only | `WORK_LEDGER/BOOK_HISTORY.md`; original record date required |
| `T` | Historical core-theory book record only | `WORK_LEDGER/BOOK_HISTORY.md`; no current manuscript access |
| `B` | Historical sub-book record only | `WORK_LEDGER/BOOK_HISTORY.md`; no current manuscript access |

These presentation codes are not ledger `Stream` values. `R` maps to research;
`P` and `O` map to operations; legacy `S`/`T`/`B` refer to book-history only.

## Monthly pack

### [YYYY-MM] — UET Monthly Work Update

Period: `[YYYY-MM-01]` to `[YYYY-MM-last-day]`

Overall note: `[one sentence describing the month without inflating readiness]`

#### `R` Research

- Work item: `[topic or verifier]`
- Current stage: `[stage]`
- This month: `[one concrete change]`
- Evidence / basis: `[artifact, manifest, update log, or n/a]`
- Still open: `[one main unresolved item]`
- Next gate: `[one next controller]`
- Claim boundary: `[hypothesis / model / internal benchmark / other]`
- Tags: `#research #[stage] #work-process`

#### `P` Policy / mega project

- Work item: `[proposal or project]`
- Current stage: `[stage]`
- This month: `[one concrete change]`
- Evidence / basis: `[proposal file, map, source, or n/a]`
- Still open: `[one main unresolved item]`
- Next gate: `[one next controller]`
- Claim boundary: `[concept / blueprint / draft proposal / ready for review]`
- Tags: `#policy #[stage] #work-process`

#### `O` Operations / tooling

- Work item: `[repository, CI, service or documentation change]`
- This month: `[one completed change]`
- Evidence: `[commit, PR, test result or none]`
- Still open: `[one concrete blocker]`
- Next action: `[one exact action]`
- Boundary: `supporting work; not a research result`

### Optional Historical Appendix

Use the following legacy categories only for a dated historical explanation.
They are not active writing tasks or permission to inspect the relocated project.

#### `S` Historical Section / three-book series

- Work item: `[Section and its three volumes]`
- Current stage: `[S00-S09 stage]`
- This month: `[one concrete parent-level change]`
- Evidence / basis: `[Section Blueprint, Volume Matrix, Dependency Map, or update log]`
- Still open: `[one controlling Section issue]`
- Next gate: `[one Section gate or affected volume gate]`
- Claim boundary: `[Section concept / blueprint / reviewed architecture / publication coordination]`
- Tags: `#section #[stage] #writing-process`

#### `T` Historical core theory book

- Work item: `[chapter, section, or manuscript]`
- Current stage: `[stage]`
- This month: `[one concrete change]`
- Evidence / basis: `[chapter draft, concept map, or n/a]`
- Still open: `[one main unresolved item]`
- Next gate: `[one next controller]`
- Claim boundary: `[conceptual framework / draft manuscript / reviewed manuscript]`
- Tags: `#core-theory #[stage] #writing-process`

#### `B` Historical sub-book

- Work item: `[book and chapter]`
- Current stage: `[stage]`
- This month: `[one concrete change]`
- Evidence / basis: `[chapter draft, blueprint, source notes, or n/a]`
- Still open: `[one main unresolved item]`
- Next gate: `[one next controller]`
- Claim boundary: `[concept / blueprint / draft / publication preparation]`
- Tags: `#sub-book #[stage] #writing-process`

## Publication checklist

- [ ] Each card is based on work that actually happened in the period.
- [ ] Each card names its current process stage.
- [ ] Each card states what changed and what remains open.
- [ ] Source links or file paths are included where available.
- [ ] Book cards identify the source or review record that supports the current stage.
- [ ] Research wording stays within its evidence layer.
- [ ] No card claims completion merely because an update was posted.
- [ ] The pack is retained after publication as the monthly history.
