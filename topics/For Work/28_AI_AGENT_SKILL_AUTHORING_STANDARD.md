# AI Agent Skill Authoring Standard

This file defines how to create UET-specific Codex skills without duplicating or
weakening the repository standards.

## Purpose

Use this standard when creating, updating, reviewing, or installing skills that
support UET topic work.

## Authoring principle

A UET skill is an adapter over the standards, not a new standard.

Keep skill instructions concise. Put stable governance in `For Work`; put only
triggering, reading order, workflow guardrails, and output expectations in the
skill.

## Required skill shape

Every UET skill must include:

- a lowercase hyphenated name, preferably beginning with `uet-`
- frontmatter with only `name` and `description`
- a description that states when the skill should trigger
- a short body with required reads, workflow, outputs, and stop conditions
- repo-relative paths, not hardcoded local absolute paths
- explicit reminder that `For Work` is canonical

## Required behavior

Every UET skill must:

1. read local evidence before summarizing, editing, or planning
2. use canonical metadata when present
3. keep hypothesis, model, benchmark, replication, and peer-review layers separate
4. keep diagnostic lanes separate from predictive lanes
5. preserve limitations and failure states
6. label inference separately from explicit repo statements
7. avoid readiness upgrades unless the user explicitly supplies human review

## Forbidden behavior

A UET skill must not:

- promote a topic to a higher readiness label on its own
- convert internal benchmark results into external validation
- turn a fitted result into a prediction
- treat update logs as replacements for artifacts, manifests, or gates
- treat logs, screenshots, or showcase media as benchmark-grade evidence
- hide missing formula origins, unit closure gaps, or source provenance gaps
- create a custom workflow when a `For Work` standard already covers the case

## Skill body template

```markdown
---
name: uet-example-skill
description: One-sentence capability and precise trigger contexts.
---

# UET Example Skill

This skill is an adapter over `docs/topics/For Work/`; it is not a source of
truth.

## Required reads

1. `AGENTS.md`
2. `docs/topics/For Work/00_README.md`
3. task-specific standards
4. local topic evidence files

## Workflow

1. Reconstruct local evidence.
2. Apply the relevant `For Work` checklist.
3. Separate explicit evidence from inference.
4. Produce only the requested output.

## Output

- concise audit, plan, log entry, or status tuple
- controlling blocker where relevant
- unresolved gaps and stop conditions

## Stop conditions

- If evidence is missing, report the missing evidence rather than strengthening
  the claim.
- If docs and artifacts disagree, name the controlling artifact or gate and
  mark the rest as drift.
```

## Review checklist

- [ ] skill points to the current file names in `For Work`
- [ ] skill does not duplicate long standards text
- [ ] skill has clear trigger language in frontmatter
- [ ] skill has a stop condition for missing evidence
- [ ] skill preserves the artifact/gate/log hierarchy
- [ ] skill can be validated with a realistic prompt
