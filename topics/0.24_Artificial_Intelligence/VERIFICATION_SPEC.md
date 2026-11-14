# Verification Spec

## Primary command

```powershell
python docs/topics/0.24_Artificial_Intelligence/Code/03_Research/Research_AI_Scaling_Audit.py
```

## Inputs

| Input | Role |
| :-- | :-- |
| `Data/03_Research/scaling_laws.json` | reference scaling exponents and critical scales |
| `Data/GPT3_Scaling_Laws.csv` | small topic-local table for an independent log-log exponent fit |
| `Data/03_Research/deepseek_moe_data.json` | dense/MoE architecture metadata for sparsity diagnostics |

## Metrics

| Metric | Meaning | Current threshold |
| :-- | :-- | :-- |
| `csv_alpha_delta` | absolute gap between CSV-fitted `alpha_fit` and stored `alpha_N` | `<= 0.20` provisional |
| `min_moe_active_fraction < min_dense_active_fraction` | sparse active-parameter check | required |
| `alpha_kappa_relative_delta` | gap between `alpha_N` and current `kappa_macro=0.1` proxy | `<= 0.25` for PASS; otherwise WARN |

## Artifact target

`Result/artifacts/0_24_artificial_intelligence_verification.json`

The artifact must include `status`, command, environment, formula IDs, input
hashes, thresholds, metrics, per-model sparsity rows, blockers, and limitations.

## Interpretation

- `PASS`: local scaling table, sparsity check, and UET proxy check all clear the
  provisional thresholds.
- `WARN`: at least one scientific blocker remains, but the verifier ran and
  produced an inspectable artifact.
- `FAIL`: verifier cannot parse required inputs or a required check is structurally
  impossible to compute.

Current claims must remain limited to an internal scaling/sparsity benchmark. This
verifier does not prove AI alignment, ethics, consciousness, or universal
intelligence dynamics.
