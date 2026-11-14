# UET Core Data/Tooling Migration Report

> Organization migration report. It does not change physics evidence or claim status.

Generated at: 2026-09-15T17:07:33+00:00
Generator: docs/scripts/audit/migrate_uet_core_data_tooling_v3.py

## Current state

- Files indexed: **99**
- Ready for the first tooling wave: **0**
- Already migrated with shim: **99**
- Quarantined for path/provenance review: **0**
- Dirty sources held back: **0**
- Duplicate targets: **0**
- Existing target conflicts: **0**
- Physics status changes: **0**

## Rules

- Python scripts move only when the first-wave path scan finds no location-sensitive bootstrap.
- Moved Python scripts retain a runpy compatibility shim at the old path.
- Markdown moves retain a redirect at the old path.
- Non-code tool assets remain pending a provenance/output classification.
- Dirty sources are never overwritten.
