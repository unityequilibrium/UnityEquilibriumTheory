# UET Core Physical Migration — Execution Map

> This is an organization execution map. Moving a file does not promote any
> equation, evidence class, or physical claim.

## Current checkpoint

The physical planner is the count authority. After the O(2) extended-family
migration on 2026-09-15 it reports **1,013** active move targets, zero target
collisions, and zero existing-destination conflicts. Counts may change only
when the planner is regenerated from the tree.

Completed structural work includes the O(2) extended Python family: **86**
implementations now live in `02_equations/o2/` and their root paths are
compatibility shims.

## Ordered completion tracks

| Order | Track | Remaining scope | Completion rule |
| :-- | :-- | --: | :-- |
| 1 | Equation and lane Python | 38 modules | One canonical family at a time; preflight blocks dirty sources, relative imports requiring rewrite, collisions, and existing targets. Import both root shim and canonical module after each family. |
| 2 | Proof and review surfaces | 2 files | Classify as proof, support, legacy, or quarantine before any move. Do not infer a physics owner from a filename. |
| 3 | Tests | 298 files | Move by test role only after path/bootstrap review; old test wrappers are forbidden because duplicate pytest collection is a failure. |
| 4 | Data and tooling | 86 files | Move only after repository-path resolver and direct-script smoke tests pass; retain a script shim or redirect where applicable. |
| 5 | Generated artifacts | 589 files | One generator family at a time. Switch generator and consumers first, compare semantic payload/hash, then move output. No hand-edited JSON. |

## Python-family order

1. Matter-space and trace family
2. Covariant family
3. Lorentz/Noether family
4. Carrier/observer family
5. Thermal, Topic 13 support, and review/support modules

The order is determined by import and ownership dependencies, not topic number.
Families with relative imports require an explicit canonical-import repair
before the physical move; the family migrator intentionally refuses to guess.

## Mandatory batch contract

Each physical batch must produce all of the following before the next batch:

1. A checked migration plan with no dirty source, duplicate target, or target conflict.
2. Canonical implementation move plus root shim/redirect where the legacy path is public.
3. Hash equality for moved source content.
4. Canonical and legacy import smoke tests; role-appropriate pytest or script smoke tests.
5. Path, import, and link audits.
6. Migration history entry, core update-log entry, work-ledger entry, and one scoped commit.

## Non-negotiable boundaries

- Generated artifacts are not bulk-renamed; their generator and consumers move
  as a unit.
- Tests are not duplicated at old and new paths.
- Dirty user files are held back unless their owner explicitly includes them.
- Quarantined assets remain outside production areas until an owner and role are
  declared.
- `AGENTS.md`, `README.md`, `CORE_FILE_INDEX.md`, and `docs/core/__init__.py`
  remain root entrypoints.
- A migration status is never a physics pass.

## Definition of complete

The migration closes only when the physical planner reports zero active move
targets or every remaining item has an explicit quarantine/deprecation record;
all active generators write canonical artifact paths; imports, links, and test
collection pass; and the registry, migration map, and planner agree on each
canonical path.
