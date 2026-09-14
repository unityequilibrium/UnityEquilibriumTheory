# UET Core Artifact Migration Report

> Plan-only control artifact. No generated output is moved by this wave.

Generated at: 2026-09-14T08:22:48+00:00
Generator: docs/scripts/audit/plan_uet_core_artifact_migration_v3.py

## Inventory

- Generated artifacts indexed: **593** (592 JSON, 1 NPZ)
- One generator identity resolved: **57**
- Ambiguous generator identity: **0**
- Missing generator identity: **536**
- Consumer rewrite required: **593**
- Duplicate canonical targets: **0**
- Existing canonical targets: **0**
- Physical move performed: **False**
- Physics status changes: **0**

## Gate

Every artifact remains at its legacy path until its generator writes the canonical path and every active consumer is switched. The legacy directory remains a compatibility boundary; it is not a second generated-output store after a family is migrated.

## Required next action

Select one bounded artifact family, patch its generator and consumers to use core_paths.canonical_artifact_path, regenerate in check mode, compare semantic payload and hashes, then perform a scoped move with a no-duplicate audit.
