# Cross Sweep Summary (seed10)

**Generated:** 2024-12-19

---

## Completed Sweeps

| Sweep | Grid Size | Seeds | Total Runs | Status |
|-------|-----------|-------|------------|--------|
| β × k_ratio | 5×5 | 10 | 250 | ✅ Complete |
| β × δ | 5×6 | 10 | 300 | ✅ Complete |
| s × δ | 5×6 | 10 | 300 | ✅ Complete |

---

## Key Observations

### 1. Seed-Locked Voting
- All sweeps use **fixed seeds 0-9** for reproducibility
- `grade_bias` (SYM/BIAS_C/BIAS_I) is deterministic per seed
- Statistical aggregation over seeds gives robust phase boundaries

### 2. β × k_ratio Structure
- High β + low k_ratio → stronger bias (BIAS_C dominant)
- k_ratio ≈ 1 → more symmetric outcomes

### 3. β × δ Structure  
- Delta (Λ) controls potential depth
- High delta → faster relaxation, cleaner separation
- Low delta → transient effects more visible

### 4. s × δ Structure (Most Informative)
- **s_tilt** directly controls asymmetry direction
- `s > 0` → BIAS_C, `s < 0` → BIAS_I, `s = 0` → SYM
- `common_mode = (mean_C + mean_I)/2` shows clear structure
- Omega varies systematically with delta

---

## Transient Metrics

| Metric | Description | Flag |
|--------|-------------|------|
| `t_relax` | Time to 5% of equilibrium | `NOT_INFORMATIVE` if ≤ dt |
| `slope_init` | Initial Omega decay slope | Always computed |
| `AUC_E_norm` | Area under normalized decay | Always computed |

> Note: Most runs show `t_relax_flag = NOT_INFORMATIVE` due to fast equilibration.

---

## Files

```
reports/cross_sweeps/seed10/
├── beta_k_ratio/
│   └── UET_final_summary_v2.csv
├── beta_delta/
│   └── UET_final_summary_v2.csv
├── s_delta/
│   └── UET_final_summary_v2.csv
└── ledger.csv
```

---

## Reproduce

```powershell
# Install deps
py -m pip install -r requirements.txt

# Re-run aggregation + plots
powershell -ExecutionPolicy Bypass -File .\run_all_cross_sweep.ps1 -Mode aggregate_only

# Export to reports/
powershell -ExecutionPolicy Bypass -File .\setup_reports.ps1
```
