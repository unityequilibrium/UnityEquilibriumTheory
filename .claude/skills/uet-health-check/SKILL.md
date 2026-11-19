---
name: uet-health-check
description: Monthly health check of the AI working setup for UET - stale, conflicting or duplicate rules across AGENTS.md, STANDARD.md, Claude memory and skills, plus the software signals they cause (red CI on main, branch and worktree pile-up, untracked files). Report only; the owner decides. Use when asked to audit the workflow, before a review or portfolio, or once a month.
---

# Health check (method from Kreycin, "ตรวจสุขภาพ AI ของคุณหรือยัง", 2026-11-19)

Clutter comes in three kinds: **expired**, **conflicting**, **duplicate or competing**. Fix, then measure again: it grows back.

## Read
- `AGENTS.md`, `core/AGENTS.md`, `docs/STANDARD.md` (§15 lists which `For Work` files still apply).
- Claude memory: `~/.claude/projects/C--Users-santa-Desktop-uet-harness/memory/` (index `MEMORY.md`).
- Skills: `.claude/skills/` and, while they exist, `~/.codex/skills/uet-*`.

For every rule or note ask: is it still true today (dates, PR numbers, paths, "not yet")? Does another file say the opposite? Does another file say the same thing differently?

## Measure
```
git worktree list                                  # target: 1
git branch | wc -l                                 # target: about 5
git status --short | grep -c '^??'                 # target: 0
gh run list --branch main --limit 5                # target: all green
gh pr list --state open
grep -rl "For Work/\(02\|04\|18\|26\)" ~/.codex/skills .claude/skills   # target: none
```

## Report
For each finding: kind, severity (high = breaks work or is visible to reviewers), where (file and line or command), and a proposal: keep / fix / delete.
Do not delete or edit anything yourself. Compare with the previous report if one exists and say what grew back.
Optional known-answer test: ask the same rule question three times (for example "may an agent approve its own Test Card?") and compare the answers with STANDARD.md.
