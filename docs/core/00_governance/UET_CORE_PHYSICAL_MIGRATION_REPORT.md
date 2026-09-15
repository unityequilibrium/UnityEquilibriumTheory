# UET Core Physical Migration Report

> Organization control-plane report. Physical migration does not promote physics evidence.

Generated at: 2026-09-15T18:27:17+00:00
Generator: docs/scripts/audit/plan_uet_core_physical_migration.py

## Current control state

- Files indexed: **1963**
- Files with a move target: **0**
- Already canonical/protected: **1963**
- Dirty sources held back: **845**
- Duplicate targets: **0**
- Existing target conflicts: **0**
- Physical migration complete: **True**
- Physical move performed in this run: **False**
- Physics status changes: **0**

## Migration waves

| Wave | Files |
| :-- | --: |
| already_canonical | 1963 |

## Safety rules

- Duplicate canonical targets and existing destinations block apply.
- Dirty user files are held back and never overwritten.
- Root entrypoints and the public facade stay in place.
- Python implementation moves create root shims; Markdown moves create redirects.
- Generated artifacts are canonicalized by a provenance-aware migration; generator/consumer validation remains a separate evidence gate.
- Organization migration is not a scientific pass.
