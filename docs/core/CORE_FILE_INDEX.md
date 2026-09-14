# Core File Index

> Generated navigation entrypoint. Organization state is not physics evidence.

## Canonical control plane

- Organization index: [00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md](00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md)
- Physical migration manifest: [00_governance/uet_core_physical_migration_manifest.json](00_governance/uet_core_physical_migration_manifest.json)
- Physical migration report: [00_governance/UET_CORE_PHYSICAL_MIGRATION_REPORT.md](00_governance/UET_CORE_PHYSICAL_MIGRATION_REPORT.md)
- Data/tooling manifest: [00_governance/uet_core_data_tooling_migration_manifest.json](00_governance/uet_core_data_tooling_migration_manifest.json)
- Data/tooling report: [00_governance/UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md](00_governance/UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md)
- Source-package manifest: [00_governance/uet_core_source_package_migration_manifest.json](00_governance/uet_core_source_package_migration_manifest.json)
- Source-package audit: [00_governance/uet_core_source_package_migration_audit.json](00_governance/uet_core_source_package_migration_audit.json)
- Test migration manifest: [00_governance/uet_core_test_migration_manifest.json](00_governance/uet_core_test_migration_manifest.json)
- Test migration audit: [00_governance/uet_core_test_migration_audit.json](00_governance/uet_core_test_migration_audit.json)
- Test collection audit: [00_governance/uet_core_test_collection_audit.json](00_governance/uet_core_test_collection_audit.json)
- Artifact migration manifest: [00_governance/uet_core_artifact_migration_manifest.json](00_governance/uet_core_artifact_migration_manifest.json)
- Artifact migration audit: [00_governance/uet_core_artifact_migration_audit.json](00_governance/uet_core_artifact_migration_audit.json)
- Artifact generator review queue: [07_artifacts/gates/uet_core_artifact_generator_review_queue.json](07_artifacts/gates/uet_core_artifact_generator_review_queue.json)
- Core migration enforcement audit: [00_governance/uet_core_migration_enforcement_audit.json](00_governance/uet_core_migration_enforcement_audit.json)
- Core path/import/link enforcement: **PASS**
- Path authority: [core_paths.py](core_paths.py)
- Compatibility loader: [core_compat.py](core_compat.py)

## Root policy

AGENTS.md, README.md, CORE_FILE_INDEX.md and __init__.py remain permanent root entrypoints. Implementations, tests, data and generated results belong in their canonical areas.

## Physical state

- Files indexed: **1792**
- Move targets: **1129**
- Already canonical or protected: **663**
- Dirty sources held back: **2**
- Duplicate targets: **0**
- Existing destination conflicts: **0**
- Physics status changes from organization migration: **0**

## Data/tooling wave

- Tooling files indexed: **111**
- Migrated with shim/redirect: **25**
- Quarantined for path/provenance review: **86**
- Tooling duplicate targets: **0**
- Tooling physics status changes: **0**


## Test surface wave

- Tests indexed in migration manifest: **500**
- Tests physically migrated: **205**
- Tests quarantined for path/package review: **295**
- Test migration audit: **PASS**
- Full pytest collection: **PASS** (2139 collected)
- Canonical-only collection: **PASS** (1313 collected)
- Test physics status changes: **0**

## Generated artifact control

- Artifacts indexed: **593**
- One-generator identities resolved: **77**
- Ambiguous generator identities: **6**
- Missing generator identities: **510**
- Consumer rewrites required: **535**
- Canonical artifacts migrated: **5**
- Artifact migration audit: **PASS**
- Generator review queue: **PASS_WITH_REVIEW_REQUIRED** (588 pending)
No generated output is moved until its generator and active consumers use the canonical path authority.

## Canonical areas

| Area | Indexed paths |
| :-- | --: |
| 00_governance | 29 |
| 01_contracts | 25 |
| 02_Proof | 2 |
| 02_equations | 35 |
| 03_lanes | 89 |
| 04_proofs | 1 |
| 05_tests | 222 |
| 06_data | 22 |
| 07_artifacts | 7 |
| 08_history | 31 |
| 99_review | 1 |
| artifacts | 589 |
| data | 113 |
| root_entrypoints | 328 |
| test | 298 |

## Migration waves

| Wave | Paths |
| :-- | --: |
| already_canonical | 663 |
| artifacts | 589 |
| data_tooling | 86 |
| equation_or_lane | 154 |
| proofs | 1 |
| review | 1 |
| tests | 298 |

## Working rule

request → owner → canonical path → compatibility check → verifier → artifact → handoff

A migrated path is easier to find; it is not thereby derived, validated or promoted. The current foundation gate remains authoritative.
