# Core File Index

> Generated navigation entrypoint. Organization state is not physics evidence.

## Canonical control plane

- Organization index: [00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md](00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md)
- Physical migration manifest: [00_governance/uet_core_physical_migration_manifest.json](00_governance/uet_core_physical_migration_manifest.json)
- Physical migration report: [00_governance/UET_CORE_PHYSICAL_MIGRATION_REPORT.md](00_governance/UET_CORE_PHYSICAL_MIGRATION_REPORT.md)
- Data/tooling manifest: [00_governance/uet_core_data_tooling_migration_manifest.json](00_governance/uet_core_data_tooling_migration_manifest.json)
- Data/tooling report: [00_governance/UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md](00_governance/UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md)
- Path authority: [core_paths.py](core_paths.py)
- Compatibility loader: [core_compat.py](core_compat.py)

## Root policy

AGENTS.md, README.md, CORE_FILE_INDEX.md and __init__.py remain permanent root entrypoints. Implementations, tests, data and generated results belong in their canonical areas.

## Physical state

- Files indexed: **1717**
- Move targets: **1387**
- Already canonical or protected: **330**
- Dirty sources held back: **11**
- Duplicate targets: **0**
- Existing destination conflicts: **0**
- Physics status changes from organization migration: **0**

## Data/tooling wave

- Tooling files indexed: **111**
- Migrated with shim/redirect: **25**
- Quarantined for path/provenance review: **86**
- Tooling duplicate targets: **0**
- Tooling physics status changes: **0**

## Canonical areas

| Area | Indexed paths |
| :-- | --: |
| 00_governance | 12 |
| 01_contracts | 25 |
| 02_Proof | 2 |
| 02_equations | 1 |
| 03_lanes | 84 |
| 04_proofs | 1 |
| 05_tests | 1 |
| 06_data | 1 |
| 07_artifacts | 1 |
| 08_history | 31 |
| 99_review | 1 |
| artifacts | 594 |
| data | 132 |
| root_entrypoints | 328 |
| test | 503 |

## Migration waves

| Wave | Paths |
| :-- | --: |
| already_canonical | 330 |
| artifacts | 594 |
| data_tooling | 107 |
| equation_or_lane | 181 |
| proofs | 1 |
| review | 1 |
| tests | 503 |

## Working rule

request → owner → canonical path → compatibility check → verifier → artifact → handoff

A migrated path is easier to find; it is not thereby derived, validated or promoted. The current foundation gate remains authoritative.
