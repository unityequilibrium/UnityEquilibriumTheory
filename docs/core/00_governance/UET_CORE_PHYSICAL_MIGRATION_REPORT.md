# UET Core Physical Migration Report

> Organization control-plane report. Physical migration does not promote physics evidence.

Generated at: 2026-09-16T18:37:27+00:00
Generator: docs/scripts/audit/plan_uet_core_physical_migration.py

## Current control state

- Files indexed: **1973**
- Files with a move target: **0**
- Already canonical/protected: **1973**
- Dirty sources held back: **23**
- Duplicate targets: **0**
- Existing target conflicts: **0**
- Physical migration complete: **True**
- Move targets pending: **0**
- Physical move performed in this run: **False**
- Last physical consolidation: **PASS** (426 compatibility assets archived)
- Physics status changes: **0**

## Migration waves

| Wave | Files |
| :-- | --: |
| already_canonical | 1973 |

## Safety rules

- Duplicate canonical targets and existing destinations block apply.
- Dirty user files are held back and never overwritten.
- Root entrypoints and the public facade stay in place.
- Python implementations live at numeric canonical paths; old imports use one lazy alias registry, and old Markdown paths use redirects.
- Generated artifacts are canonicalized by a provenance-aware migration; generator/consumer validation remains a separate evidence gate.
- Organization migration is not a scientific pass.
