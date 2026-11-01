# UET Book Workspace

This directory is the public-facing book workspace. `BOOK_REGISTRY.json` is
the source of truth for book identity, canonical paths, public paths, and
publication state.

## Path rule

Existing book folders are canonical. Agents must inspect this directory and
the registry before creating a path. A new semantic alias for an existing book
is not allowed.

The working source and public output use the same book identity. Raw material
and chapter drafts may remain local, but they must not be silently replaced by
a renamed public copy.

## Current public tree

| Book | Public path | State |
| --- | --- | --- |
| Core UET theory | `00_uet_core_theory/` | curated scaffold |
| The Origin of Wealth | `economics_ai_energy/01_economics/` | curated blueprint |

The remaining book tracks are recorded in `BOOK_REGISTRY.json` as local-only
until their reviewed public files are promoted. The previous
`origin_of_wealth_and_economics/` path was a duplicate alias and is retired.

Three-book Sections are grouped under a human-readable academic-domain folder,
such as `history_media_power/`. The parent folder itself shows the grouping; it
does not repeat a technical `section_` prefix or a Section number. Child book
folders may carry their book number for ordering. The Section parent contains the Section Blueprint, manifest,
volume matrix, dependency map, and update log. Child book folders use concise
academic-domain labels with numeric volume prefixes such as `01_history_media/` and remain responsible for
their own book blueprint, research, drafts, and review records. Stable
`section_id`, `book_id`, and `volume_number` values remain in the registries and
manifests.

Current Section parents:
- `earth_terrain_migration/`
- `biology_psychology_economics/`
- `economics_ai_energy/`
- `history_media_power/`

## Publication workflow

1. Update the existing canonical book folder.
2. Keep `1_raw/` and `ch_drafts/` outside the public file list.
3. Update the registry state and public file list.
4. Commit the coherent book change and verify the public `main` path.

One workflow applies to every book. A book-specific change must not create a
book-specific directory convention.

## Working order

Use the same three-layer order for every Section and book:

```text
Section S00-S07 plan and lock
  -> Book W00-W05 research and Blueprint lock
    -> approved unit_id and Unit Execution Card
      -> local writing pattern
        -> W06-W10 draft, author review, integrity, and fact/citation audit
          -> W11-W18 editorial, proof, release, and maintenance
```

Do not start a new writing request by asking the author to choose an episode.
Read the Section and Book manifests first; if a plan or lock is missing, return
the planning package or handoff list. The local eight-function structure is a
Writing Unit template and does not replace the shared gates.

The shared writing lifecycle, reference workflow, review gates, and versioning rules are defined in
[uet_history/BOOK_WORKFLOW.md](../../BOOK_WORKFLOW.md). This file remains the source of truth for
book identity, paths, and publication state.

Use the shared workflow's W00-W18 gates for research, drafting, review, proof,
publication, and maintenance; this index governs the identity and path boundary.

When a book belongs to a three-book Section, the parent Section Blueprint is upstream of the local Book Blueprint. A child book may narrow its scope, but it must not silently redefine the Section role, dependency, claim ownership, or handoff.
