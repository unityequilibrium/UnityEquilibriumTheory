# UET R0-E10 — Band Stability + Richer Run Metrics v0.1
**Goal:** ทำให้ band/presets “นิ่ง” ภายใต้หลาย seed และวัดความ “ตึง/ใกล้ fail” จาก run artifacts

## 1) Expand dt ladder to multiple seeds
```bash
python scripts/expand_dt_ladder_matrix_seeds.py \
  --matrix_in dt_ladder_matrix.csv \
  --matrix_out dt_ladder_matrix_seeds.csv \
  --seeds 0;1;2;3;4
```

## 2) Run ladder
```bash
python scripts/run_dt_ladder.py --matrix dt_ladder_matrix_seeds.csv --out dt_ladder_runs_seeds --overwrite
```

## 3) Compute metrics from timeseries/summary
```bash
python scripts/compute_run_metrics.py --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv
```
Outputs `dt_ladder_runs_seeds/run_metrics.csv` with:
- `dOmega_max, dOmega_median`
- `tight_frac` (fraction of accepted steps with dΩ > -eps)
- `dt_collapse_ratio = dt_min/dt`
- `backtracks_density = dt_backtracks_total/steps_accepted`

## 4) Band stability check (per seed → mode)
```bash
python scripts/band_stability_check.py \
  --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv \
  --write_band_map
```
Outputs:
- `band_by_seed.csv`
- `band_stability_by_case.csv`
- `band_map_mode.csv`
