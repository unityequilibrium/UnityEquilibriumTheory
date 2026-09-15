# UET Core Physical Migration Report

> Organization control-plane report. Physical migration does not promote physics evidence.

Generated at: 2026-09-15T16:40:19+00:00
Generator: docs/scripts/audit/plan_uet_core_physical_migration.py

## Current control state

- Files indexed: **1970**
- Files with a move target: **677**
- Already canonical/protected: **1293**
- Dirty sources held back: **21**
- Duplicate targets: **0**
- Existing target conflicts: **0**
- Physical move performed in this run: **False**
- Physics status changes: **0**

## Migration waves

| Wave | Files |
| :-- | --: |
| already_canonical | 1293 |
| artifacts | 589 |
| data_tooling | 86 |
| proofs | 1 |
| review | 1 |

## Safety rules

- Duplicate canonical targets and existing destinations block apply.
- Dirty user files are held back and never overwritten.
- Root entrypoints and the public facade stay in place.
- Python implementation moves create root shims; Markdown moves create redirects.
- Generated artifacts move only after generator and consumer checkpoints.
- Organization migration is not a scientific pass.
