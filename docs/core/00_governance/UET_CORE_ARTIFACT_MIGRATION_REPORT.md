# UET Core Artifact Migration Report

> Organization control artifact. Each physical move is recorded per bounded wave; no physics claim is promoted.

Generated at: 2026-09-14T13:47:08+00:00
Generator: docs/scripts/audit/plan_uet_core_artifact_migration_v3.py

## Inventory

- Generated artifacts indexed: **593** (592 JSON, 1 NPZ)
- Active legacy outputs: **591**
- Canonical outputs migrated: **2**
- One generator identity resolved: **57**
- Ambiguous generator identity: **0**
- Missing generator identity: **536**
- Consumer rewrite required: **539**
- Duplicate canonical targets: **0**
- Existing canonical targets: **0**
- Physical move recorded: **True**
- Physics status changes: **0**

## Gate

Active artifacts remain at their legacy path until their generator and consumers are ready. Migrated artifacts are represented by one canonical output plus history metadata; the legacy directory is not a second generated-output store.

## Required next action

Select one bounded artifact family, patch its generator and consumers to use core_paths.canonical_artifact_path, regenerate in check mode, compare semantic payload and hashes, then perform a scoped move with a no-duplicate audit.
