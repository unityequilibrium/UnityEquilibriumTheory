# UET Core Data/Tooling Migration Report

> Organization migration report. It does not change physics evidence or claim status.

Generated at: 2026-09-14T06:57:12+00:00
Generator: docs/scripts/audit/migrate_uet_core_data_tooling_v3.py

## Current state

- Files indexed: **111**
- Ready for the first tooling wave: **0**
- Already migrated with shim: **25**
- Quarantined for path/provenance review: **86**
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

## Quarantine reasons

- non_code_tool_asset_requires_separate_provenance_review: 12
- path_bootstrap_requires_review: 74
