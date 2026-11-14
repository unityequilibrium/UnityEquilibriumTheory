# Verification Specification — Topic 0.25

## Controlling order

1. `Research_UET_Book_Topic_Alignment_Gate.py`
2. source and canonical-panel builders
3. measurement and unit gates
4. dependency producers before consumer joins
5. lane audits and baselines
6. global integrity/readiness
7. causal, external-replication, publication, and aggregate claim gates

## Required checks

- Book/Section/Topic versions and SHA-256 identities agree.
- `BOOK-HEURISTIC-001` remains retired.
- 20 WARN gates exist and no aggregate average hides them.
- Every global analysis row contains all required indicators; World Bank aggregates are excluded.
- Country counts use analysis-ready rows and consecutive common years.
- Downstream artifact counts and embedded hashes reconcile with the canonical panel.
- RMSE, median absolute error, bootstrap, holdout, and sign checks match `METHOD.md`.
- No primary imputation, Yahoo substitution, or residual velocity is hidden.
- Payer/resource links carry an evidence-level and lineage label.

## Current acceptance state

- Alignment: `PASS_WITH_BOUNDARY`.
- Literature: `WARN`.
- Global panel integrity: `BLOCKED`.
- Legacy resource candidate: false at 1/3/5 years.
- Stone/resource-coverage candidate: false at 1/3/5 years.
- Causal, external, and publication gates: blocked.

## Promotion

Evidence Grade A is evaluated by claim/lane. A causal claim requires two independent designs; every promoted claim additionally requires independent rerun and human review. Quarantined lanes do not block unrelated core diagnostics but cannot contribute evidence to them.
