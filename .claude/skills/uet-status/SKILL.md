---
name: uet-status
description: Report where UET research stands from the machine-checked records - claim counts by level, what each layer or topic has at which level, open Test Cards, open PRs and the next step. Read-only. Use for "where are we", "what is the state of X", or numbers for a README, a report or a portfolio.
---

# Status from records, not from memory (STANDARD §1, §2)

Status belongs to claims, not to topics or folders. Anything without a claim id is L0.

## Sources, in this order
1. `docs/standard/claims.json`: level per claim. Count with
   `.venv/Scripts/python.exe -c "import json,collections;d=json.load(open('docs/standard/claims.json',encoding='utf-8'));c=d['claims'] if isinstance(d,dict) else d;print(collections.Counter(x['level'] for x in c))"`
2. `docs/standard/results/*.json`: outcome, numbers, producer commit, approval.
3. `docs/standard/tests/*.json`: card status (DRAFT / APPROVED / CLOSED).
4. `core/CORE_MAP.md` and `README.md` for the human summary; check their counts against step 1 and report any drift.
5. `gh pr list --state open` and `git log origin/main` for what is merged versus waiting.
6. Topic `UPDATE_LOG.md` for the latest wave and its "next" line.

Legacy gates, verifier artifacts and old status words (`PASS_*`, `CLOSED_FOR_CORE`, tiers A–D) are `LEGACY_UNREVIEWED`: map them with STANDARD §13 and never report them as evidence levels.

## Output
- A short table: claim id, level, one-line meaning, evidence (result id or test card).
- What is merged on `main` versus only on a branch or PR.
- What is not UET-distinct, and what failed (FAILED is a result, list it).
- The next step from the latest log entry.
Do not edit files. If counts drift, say where and offer `uet-claim-wording` to fix them.
