# UET Core Test Migration Report

> Organization migration report. It does not promote a physics claim.

Generated at: 2026-09-15T17:43:01+00:00
Generator: docs/scripts/audit/migrate_uet_core_tests_v3.py

## Current state

- Test files indexed: **500**
- Safe first-wave candidates: **0**
- Physically migrated: **500**
- Quarantined for unresolved path review: **0**
- Dirty sources held back: **0**
- Duplicate targets: **0**
- Existing target conflicts: **0**
- Physics status changes: **0**

## Test-specific compatibility rule

- Moved Python tests do not receive old-path wrappers, because wrappers would create duplicate pytest collection.
- The old tree is retained only for tests not yet safe to move and for its boundary README after the move wave.
- The migration manifest is the path map for moved tests; it is not evidence that the tests prove the underlying physics.
- Package marker and sandbox residue are relocated to history/review destinations and are not collected as production tests.
