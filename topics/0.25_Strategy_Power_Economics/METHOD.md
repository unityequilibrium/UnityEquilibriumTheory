# Method — Topic 0.25 Economics Research Program

## Status and scope

The program is U.S.-first and Claim Class C. It uses Book 1 version `book1-economics-v2-research-reset`. Global and Thailand work are separate packages; strategy/social claims remain quarantined.

## Common data flow

```text
raw provider archive
  → source/release/terms/hash lock
  → canonical panel by evidence level
  → unit, coverage, measurement, and lineage gates
  → preregistered features and baselines
  → descriptive/predictive/causal lane
  → uncertainty and robustness
  → independent replication
  → claim and publication gate
```

## Construct policy

`Y`, `W`, `Kp`, `H`, `L`, `E`, `X`, `A`, `C`, `M^j`, `Cr`, `T`, `P^{b,g}`, and `F` are the controlled symbols. Stocks, flows, shocks, indexes, physical quantities, and prices are never silently combined.

`BOOK-HEURISTIC-001 (R=N+K+I)` is retired as an identity. Existing R/N/K/I outputs are retained to document a failed legacy operationalization, not as the primary scientific model.

## Core methods by lane

- Production/resources: BEA–BLS KLEMS, BEA I-O, USEEIO, EIA, USGS, CFS; compare standard benchmarks before UET additions.
- Money value: basket/group purchasing power, FX/REER, payment use, and real asset returns are separate outputs.
- Money/credit/fiscal: identity decomposition is descriptive; causal candidates use identified shocks and pre-treatment exposure.
- Funding/lineage: sector sources-and-uses plus bounded public transactions; lineage labels are mandatory.
- Knowledge/infrastructure: R&D capital, IP, patent quality, capital services, utilization, depreciation, social NPV, fiscal NPV, and debt service remain separate.
- Wages/welfare: EPI/BLS constructions, mean/median, labor share, deflator, household basket, region, and distribution remain explicit.
- Energy/environment: heat content, throughput, energy service, efficiency, EROI, exergy, emissions, and depletion remain distinct.
- History: chronology, specialist appraisal, competing accounts, and uncertainty precede narrative use.

## Predictive contract

- rolling origins begin at the declared holdout year;
- all transformations and sign checks use training/pre-holdout data only;
- RMSE is `sqrt(mean(error^2))`;
- median absolute error is reported separately;
- candidate acceptance requires at least 10% lower RMSE than every named baseline and a 95% moving-block-bootstrap paired squared-error interval below zero;
- blocks are sampled with replacement and seed/block size/draw count are stored;
- success never upgrades a prediction into causality.

## Causal contract

A causal lane requires a DAG, identified intervention/shock, pre-treatment exposure, pre-trends, placebo and negative controls, appropriate dependence/cluster treatment, weak-instrument screening where relevant, robustness to windows/controls/weights, and two designs with materially different identifying assumptions.

## Missingness and revisions

No silent imputation is allowed in primary evidence. Global rows require every declared indicator and non-aggregate country identity. Provider vintage and as-of date must be stored; current revised data cannot be presented as a real-time forecast without a vintage audit.
