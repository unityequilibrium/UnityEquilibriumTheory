# UET R0-E11 — Strict Robustness + Data-Driven Bands v0.1
**Goal:** ทำให้ “ผ่านจริง” = PASS ทุก seed และ downgrade band ถ้า “ผ่านแบบตึง” ตาม metrics

## Strict dt_max per case
```bash
python scripts/strict_dt_max_pass_by_case.py \
  --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv \
  --require_seed_coverage
```

## Band map from metrics
```bash
python scripts/band_map_from_metrics.py \
  --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv \
  --run_metrics dt_ladder_runs_seeds/run_metrics.csv \
  --out band_map_metrics.csv \
  --strict_all_seeds --require_seed_coverage
```
Metric gates (defaults):
- tight_frac_max=0.2
- dt_collapse_ratio_min=0.5
- backtracks_density_max=0.5
