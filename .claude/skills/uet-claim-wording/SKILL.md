---
name: uet-claim-wording
description: Check README, papers, topic docs or any public UET text for overclaims, restricted words, missing claim ids and numbers that drift from claims.json, then propose evidence-matched wording. Use before publishing, before a portfolio or review, or when asked whether a statement is supported.
---

# Claim wording (AGENTS.md §4, STANDARD §2)

## Rules to check
- Every scientific statement in public text points to a claim id with its level. Without one it counts as L0.
- Restricted words: `solved`, `proved`, `verified`, `exact`, `production grade`. `predicts` only for a `BLIND_PREDICTION` card. A `CONSTRAINT` result "bounds", "excludes" or "is consistent with".
- Preferred words: hypothesis, model, derived relation, internally consistent (L1), confronted with data (L2), externally replicated (L3).
- Do not upgrade a fit into a prediction, an internal rerun into external validation, a normalized quantity into SI, or a lane mapping into a universal identity (C is not universally mass).
- Say when a result is not UET-distinct (standard physics passes too). Do not call reuse of known theory a weakness: UET is a synthesis theory; judge correct use of each source and the composition.
- FAILED results stay visible. Never drop them from a results table.

## Procedure
1. List each claim-like sentence with its location.
2. Match it to `claims.json` and the result file. Mark: supported / overstated / unsupported / stale number.
3. Check the counts: README badge and registry line, `README.th.md`, `core/CORE_MAP.md` against the levels in `claims.json`.
4. Propose replacement wording. Edit only if the owner asked for edits; English and Thai READMEs change together.
