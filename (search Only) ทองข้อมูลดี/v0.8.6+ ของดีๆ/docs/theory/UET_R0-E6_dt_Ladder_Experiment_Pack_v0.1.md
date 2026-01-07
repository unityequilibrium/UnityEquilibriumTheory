# UET R0-E6 — dt-Ladder Experiment Pack v0.1
**Goal:** เลือก dt “ใช้งานจริง” สำหรับ atlas/demos แบบ audit-friendly และเปรียบเทียบ semiimplicit vs stabilized

## Quickstart
1) Create matrix
```bash
python scripts/dt_ladder_matrix.py --out dt_ladder_matrix.csv --T 5 --N 128
```

2) Run ladder
```bash
python scripts/run_dt_ladder.py --matrix dt_ladder_matrix.csv --out dt_ladder_runs --overwrite
```

3) Summarize
```bash
python scripts/summarize_dt_ladder.py --ledger dt_ladder_runs/dt_ladder_ledger.csv
```

4) Plot
```bash
python scripts/plot_dt_ladder.py --summary_csv dt_ladder_runs/dt_ladder_summary/dt_ladder_summary.csv
```

## Recommended decision rule
- Use dt_max_pass per integrator (pass_threshold default=1.0)
- If tied, prefer lower median_backtracks and higher median_dt_min
