# UET Core Physical Migration Report

> Organization control-plane report. Physical migration does not promote physics evidence.

Generated at: 2026-09-14T06:22:09+00:00
Generator: docs/scripts/audit/plan_uet_core_physical_migration.py

## Current control state

- Files indexed: **1699**
- Files with a move target: **1409**
- Already canonical/protected: **290**
- Dirty sources held back: **286**
- Duplicate targets: **0**
- Existing target conflicts: **0**
- Physical move performed in this run: **False**
- Physics status changes: **0**

## Migration waves

| Wave | Files |
| :-- | --: |
| already_canonical | 290 |
| artifacts | 593 |
| data_tooling | 131 |
| equation_or_lane | 181 |
| proofs | 1 |
| review | 1 |
| tests | 502 |

## Safety rules

- Duplicate canonical targets and existing destinations block apply.
- Dirty user files are held back and never overwritten.
- Root entrypoints and the public facade stay in place.
- Python implementation moves create root shims; Markdown moves create redirects.
- Generated artifacts move only after generator and consumer checkpoints.
- Organization migration is not a scientific pass.
