# UET R0-E13 — Preset Stress Test + Generalization Gate v0.1
**Goal:** ตรวจว่า dt presets (strict/global/band-aware) “generalize” ได้จริง  
ไม่ใช่แค่รอดกับชุด ladder/atlas ที่เราตั้งใจเลือก

> หลักคิด: ถ้า preset ใช้จริงได้ ต้อง “รอด” ภายใต้ perturbation ของพารามิเตอร์ + หลาย seed ของ init

---

## 1) Stress Spec
ใช้ `stress_spec.json` กำหนด:
- anchor cases (base_case_id, model, params)
- band label (DEMO/MID/BOUNDARY/HARD)
- perturbation distributions ของพารามิเตอร์ (top-level และ quartic coefficients)
- meta (N,L,T,seeds,integrators,n_per_case)

---

## 2) Generate stress matrix (พร้อม dt จาก presets)
```bash
python scripts/generate_stress_matrix.py \
  --spec stress_spec.json \
  --band_dt_presets dt_ladder_runs_seeds/band_dt_presets_strict/band_dt_presets_strict.json \
  --dt_presets dt_ladder_runs_seeds/dt_presets_strict/dt_presets_strict.json \
  --out stress_matrix.csv
```

Output:
- `stress_matrix.csv` (พร้อม `dt_list` แบบ single dt ต่อ integrator)
- ถ้ามี preset ขาด จะได้ `stress_missing_presets.csv`

> หมายเหตุ: matrix นี้ compatible กับ `run_dt_ladder.py`

---

## 3) Run stress test
```bash
python scripts/run_dt_ladder.py --matrix stress_matrix.csv --out stress_runs --overwrite
```

---

## 4) Summarize
```bash
python scripts/summarize_stress_test.py --ledger stress_runs/dt_ladder_ledger.csv
```
Outputs `stress_runs/stress_summary/stress_summary.csv` (pass rate + Wilson CI + fail code histogram)

---

## 5) Generalization Gate (fail-fast)
```bash
python scripts/gate_stress_results.py \
  --summary_csv stress_runs/stress_summary/stress_summary.csv \
  --min_pass_rate 0.95 \
  --min_ci_lo 0.90
```
Outputs `stress_gate_report.json` and exit code 2 on FAIL.

**Interpretation**
- ถ้า FAIL: presets/thresholds/bands ยังไม่ robust → ต้องลด dt หรือปรับ threshold (tight/collapse/btden) หรือปรับ band rule

---

## 6) Freeze evidence to baseline manifest
```bash
python scripts/freeze_baseline_manifest.py \
  --out baseline/baseline_manifest.json \
  --stress_spec stress_spec.json \
  --stress_report stress_runs/stress_summary/stress_gate_report.json \
  --overwrite
```

---

## Recommended default (เริ่มต้น)
- n_per_case: 20
- seeds: 0;1;2;3;4
- integrators: semiimplicit;stabilized
- Gate: min_pass_rate=0.95, min_ci_lo=0.90

---

## Next step (R0-E14)
- ทำ “adaptive stress”: ถ้า FAIL ให้ auto-focus ไปที่พารามิเตอร์/ย่านที่พังบ่อย แล้ว refine dt/band rule เฉพาะจุด
