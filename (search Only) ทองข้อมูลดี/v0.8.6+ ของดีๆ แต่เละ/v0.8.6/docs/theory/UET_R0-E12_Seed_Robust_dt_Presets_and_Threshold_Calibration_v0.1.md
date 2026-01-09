# UET R0-E12 — Seed-Robust dt Presets + Threshold Calibration v0.1
**Goal:** สร้าง dt presets ที่ “ล็อกแล้วนิ่ง” โดย
1) ต้อง PASS ทุก seed (strict)
2) ไม่ “ผ่านแบบตึง” (ใช้ run_metrics + thresholds)

---

## 1) Calibrate thresholds from run_metrics
```bash
python scripts/calibrate_metric_thresholds.py \
  --run_metrics dt_ladder_runs_seeds/run_metrics.csv \
  --use_only_pass
```
Output: `metric_thresholds.json` (quantile-based)

---

## 2) Extract strict global dt presets (model × integrator)
```bash
python scripts/extract_dt_presets_strict.py \
  --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv \
  --strict_all_seeds --require_seed_coverage \
  --metrics dt_ladder_runs_seeds/run_metrics.csv \
  --thresholds_json dt_ladder_runs_seeds/metric_thresholds.json
```
Output folder: `dt_presets_strict/` with
- `dt_presets_strict.json`
- `dt_presets_strict_selected.csv`

---

## 3) Extract strict band-aware dt presets (band × model × integrator)
ต้องมี `band_map.csv` ก่อน (จาก R0-E9/R0-E10/R0-E11)
```bash
python scripts/extract_band_dt_presets_strict.py \
  --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv \
  --band_map band_map_metrics.csv \
  --strict_all_seeds --require_seed_coverage \
  --metrics dt_ladder_runs_seeds/run_metrics.csv \
  --thresholds_json dt_ladder_runs_seeds/metric_thresholds.json
```
Output folder: `band_dt_presets_strict/` with
- `band_dt_presets_strict.json`
- `band_dt_presets_strict_selected.csv`

---

## 4) Freeze into baseline manifest (audit)
`freeze_baseline_manifest.py` รองรับ `--metric_thresholds` และ `--band_stability` แล้ว

```bash
python scripts/freeze_baseline_manifest.py \
  --out baseline/baseline_manifest.json \
  --ledger dt_ladder_runs_seeds/dt_ladder_ledger.csv \
  --band_map band_map_metrics.csv \
  --metric_thresholds dt_ladder_runs_seeds/metric_thresholds.json \
  --overwrite
```

---

## Next step (R0-E13)
- ทำ “preset stress test”: ใช้ dt presets แล้วสุ่มเคสใหม่ใน band เดิมเพื่อวัด generalization
- ทำ threshold tuning แบบ multi-objective (speed vs margin)
