# TEMPLATE: AI Agent Skill Spec

Use this template before creating or revising a UET-specific Codex skill.

## Skill name

`uet-[short-action-name]`

## Purpose

What this skill helps an agent do.

## Trigger

What a user might ask that should activate the skill.

## Canonical standards

- `AGENTS.md`
- `docs/topics/For Work/00_README.md`
- `[task-specific standard]`

## Required local evidence

- `[repo-wide metadata if relevant]`
- `[topic README / LIMITATIONS / VERIFICATION_SPEC]`
- `[artifact / gate / manifest / update log]`

## Workflow

1. `[first evidence-gathering step]`
2. `[standard checklist step]`
3. `[output shaping step]`

## Allowed outputs

- `[audit finding / status tuple / log entry / wave plan]`

## Stop conditions

- `[missing evidence condition]`
- `[claim/status boundary condition]`

## Anti-overclaim rules

- Do not promote readiness status without human review.
- Do not upgrade internal benchmark evidence into external validation.
- Do not replace artifacts, manifests, gates, or canonical metadata with prose.

## Validation prompts

- `[realistic prompt 1]`
- `[realistic prompt 2]`
