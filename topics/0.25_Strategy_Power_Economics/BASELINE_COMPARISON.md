# Baseline Comparison — Topic 0.25

> **Metric version:** corrected 2026-08-11
> RMSE is `sqrt(mean(error²))`; median absolute error is separate. Intervals use circular moving blocks sampled with replacement, seed `25025`.

## Legacy resource proxy

| Horizon | UET RMSE | Constant-growth RMSE | RMSE improvement | Bootstrap upper | Candidate |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.01687 | 0.01601 | -5.36% | 0.000108 | false |
| 3 | 0.03956 | 0.02987 | -32.44% | 0.001380 | false |
| 5 | 0.05916 | 0.04867 | -21.56% | 0.002373 | false |

The sign gate uses pre-holdout data only. This is a retained legacy sensitivity; `R=N+K+I` is retired as an identity.

## Stone/resource-coverage diagnostic versus inflation AR

| Horizon | UET RMSE | Inflation-AR RMSE | RMSE improvement | Bootstrap upper | Candidate |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.02376 | 0.01597 | -48.74% | 0.000514 | false |
| 3 | 0.02730 | 0.01939 | -40.85% | 0.000538 | false |
| 5 | 0.02630 | 0.02064 | -27.43% | 0.000484 | false |

The diagnostic loses to the autoregressive baseline at every declared horizon. This does not prove that money, credit, resources, or supply constraints never affect inflation; it rejects this frozen proxy candidate under this panel and metric contract.
